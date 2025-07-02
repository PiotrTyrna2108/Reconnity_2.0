from celery import Celery
import subprocess
import json
import os
import time
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("scanner_masscan", broker=broker_url)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

CORE_URL = os.getenv("CORE_URL", "http://core:8001")

@celery_app.task(name="scanner-masscan.run", bind=True)
def run_masscan_scan(self, scan_id: str, target: str, options: Dict[str, Any] = None):
    """
    Execute masscan scan for given target
    """
    logger.info(f"[MASSCAN] Starting scan for {target} (id={scan_id})")
    
    if options is None:
        options = {}
    
    try:
        # Resolve domain name to IP if needed (masscan only works with IPs)
        import socket
        try:
            # Check if target is not already an IP address
            if not any(c.isdigit() for c in target.replace('.', '')):
                logger.info(f"[MASSCAN] Resolving domain name: {target}")
                target_ip = socket.gethostbyname(target)
                logger.info(f"[MASSCAN] Resolved {target} to {target_ip}")
                target = target_ip
        except socket.gaierror as e:
            error_msg = f"Failed to resolve hostname {target}: {e}"
            logger.error(f"[MASSCAN] {error_msg}")
            report_scan_failure(scan_id, error_msg)
            return
            
        # Build masscan command
        masscan_args = build_masscan_command(target, options)
        logger.info(f"[MASSCAN] Running command: {' '.join(masscan_args)}")
        
        # Execute masscan scan
        start_time = time.time()
        result = subprocess.run(
            masscan_args,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout for masscan (faster than nmap)
        )
        scan_duration = time.time() - start_time
        
        if result.returncode == 0:
            # Parse masscan output
            scan_results = parse_masscan_output(result.stdout, target, scan_id, scan_duration)
            logger.info(f"[MASSCAN] Scan completed successfully: {scan_id}")
            
            # Report results to core service
            report_scan_completion(scan_id, scan_results)
            
        else:
            error_msg = f"Masscan scan failed with return code {result.returncode}: {result.stderr}"
            logger.error(f"[MASSCAN] {error_msg}")
            report_scan_failure(scan_id, error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Masscan scan timed out after 2 minutes"
        logger.error(f"[MASSCAN] {error_msg}")
        report_scan_failure(scan_id, error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during masscan scan: {str(e)}"
        logger.error(f"[MASSCAN] {error_msg}")
        report_scan_failure(scan_id, error_msg)

def build_masscan_command(target: str, options: Dict[str, Any]) -> list:
    """Build masscan command with appropriate flags"""
    cmd = ["masscan"]
    
    # Add ports (required for masscan)
    if "ports" in options:
        cmd.extend(["-p", options["ports"]])
    else:
        cmd.extend(["-p", "1-10000"])  # Default port range
    
    # Add rate limiting (masscan can be very aggressive)
    rate = options.get("rate", "1000")  # packets per second
    cmd.extend(["--rate", str(rate)])
    
    # Output format
    cmd.extend(["-oJ", "-"])  # JSON output to stdout
    
    # Add target
    cmd.append(target)
    
    return cmd

def parse_masscan_output(json_output: str, target: str, scan_id: str, duration: float) -> Dict[str, Any]:
    """Parse masscan JSON output and extract relevant information"""
    try:
        results = {
            "scanner": "masscan",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "open_ports": [],
            "services": {},
            "scan_stats": {}
        }
        
        # Parse JSON lines (masscan outputs one JSON object per line)
        for line in json_output.strip().split('\n'):
            if not line.strip():
                continue
                
            try:
                data = json.loads(line)
                
                if data.get("ip") and data.get("ports"):
                    for port_info in data["ports"]:
                        port_num = port_info.get("port")
                        protocol = port_info.get("proto", "tcp")
                        status = port_info.get("status", "open")
                        
                        if status == "open" and port_num:
                            results["open_ports"].append(port_num)
                            
                            # Basic service identification (masscan doesn't do deep service detection)
                            service_name = identify_service_by_port(port_num)
                            if service_name:
                                results["services"][str(port_num)] = {
                                    "name": service_name,
                                    "protocol": protocol,
                                    "state": status,
                                    "method": "port-based-identification"
                                }
                            
            except json.JSONDecodeError as e:
                logger.warning(f"[MASSCAN] Failed to parse JSON line: {line} - {e}")
                continue
        
        # Sort ports for consistent output
        results["open_ports"].sort()
        
        return results
        
    except Exception as e:
        logger.error(f"[MASSCAN] Failed to parse output: {e}")
        # Return basic results if parsing fails
        return {
            "scanner": "masscan",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "raw_output": json_output,
            "parse_error": str(e)
        }

def identify_service_by_port(port: int) -> str:
    """Basic service identification by well-known ports"""
    port_services = {
        21: "ftp",
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "dns",
        80: "http",
        110: "pop3",
        143: "imap",
        443: "https",
        993: "imaps",
        995: "pop3s",
        1433: "mssql",
        3306: "mysql",
        3389: "rdp",
        5432: "postgresql",
        6379: "redis",
        9200: "elasticsearch",
        27017: "mongodb"
    }
    
    return port_services.get(port, "unknown")

def report_scan_completion(scan_id: str, results: Dict[str, Any]):
    """Report successful scan completion to core service"""
    try:
        response = requests.post(
            f"{CORE_URL}/api/v1/scan/{scan_id}/complete",
            json=results,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"[MASSCAN] Scan completion reported: {scan_id}")
    except Exception as e:
        logger.error(f"[MASSCAN] Failed to report completion: {e}")

def report_scan_failure(scan_id: str, error: str):
    """Report scan failure to core service"""
    try:
        response = requests.post(
            f"{CORE_URL}/api/v1/scan/{scan_id}/fail",
            json={"error": error},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"[MASSCAN] Scan failure reported: {scan_id}")
    except Exception as e:
        logger.error(f"[MASSCAN] Failed to report failure: {e}")

if __name__ == "__main__":
    logger.info("[MASSCAN] Starting Masscan scanner service...")
    celery_app.start()
