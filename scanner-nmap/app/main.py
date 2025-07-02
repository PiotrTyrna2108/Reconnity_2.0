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
celery_app = Celery("scanner_nmap", broker=broker_url)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

CORE_URL = os.getenv("CORE_URL", "http://core:8001")

@celery_app.task(name="scanner-nmap.run", bind=True)
def run_nmap_scan(self, scan_id: str, target: str, options: Dict[str, Any] = None):
    """
    Execute nmap scan for given target
    """
    logger.info(f"[NMAP] Starting scan for {target} (id={scan_id})")
    
    if options is None:
        options = {}
    
    try:
        # Build nmap command
        nmap_args = build_nmap_command(target, options)
        logger.info(f"[NMAP] Running command: {' '.join(nmap_args)}")
        
        # Execute nmap scan
        start_time = time.time()
        result = subprocess.run(
            nmap_args,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        scan_duration = time.time() - start_time
        
        if result.returncode == 0:
            # Parse nmap output
            scan_results = parse_nmap_output(result.stdout, target, scan_id, scan_duration)
            logger.info(f"[NMAP] Scan completed successfully: {scan_id}")
            
            # Report results to core service
            report_scan_completion(scan_id, scan_results)
            
        else:
            error_msg = f"Nmap scan failed with return code {result.returncode}: {result.stderr}"
            logger.error(f"[NMAP] {error_msg}")
            report_scan_failure(scan_id, error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Nmap scan timed out after 5 minutes"
        logger.error(f"[NMAP] {error_msg}")
        report_scan_failure(scan_id, error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during nmap scan: {str(e)}"
        logger.error(f"[NMAP] {error_msg}")
        report_scan_failure(scan_id, error_msg)

def build_nmap_command(target: str, options: Dict[str, Any]) -> list:
    """Build nmap command with appropriate flags"""
    cmd = ["nmap"]
    
    # Default options for security scanning
    cmd.extend([
        "-sS",  # TCP SYN scan
        "-O",   # OS detection
        "-sV",  # Service version detection
        "-sC",  # Default scripts
        "--open",  # Only show open ports
        "-oX", "-",  # XML output to stdout
    ])
    
    # Add custom options if provided
    if "ports" in options:
        cmd.extend(["-p", options["ports"]])
    else:
        cmd.extend(["-p", "1-10000"])  # Default port range
    
    if options.get("aggressive", False):
        cmd.append("-A")
    
    if options.get("timing"):
        cmd.extend(["-T", str(options["timing"])])
    else:
        cmd.extend(["-T", "4"])  # Default aggressive timing
    
    # Add target
    cmd.append(target)
    
    return cmd

def parse_nmap_output(xml_output: str, target: str, scan_id: str, duration: float) -> Dict[str, Any]:
    """Parse nmap XML output and extract relevant information"""
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_output)
        
        results = {
            "scanner": "nmap",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "open_ports": [],
            "services": {},
            "os_info": {},
            "vulnerabilities": []
        }
        
        # Parse host information
        for host in root.findall("host"):
            # Get host status
            status = host.find("status")
            if status is not None and status.get("state") == "up":
                
                # Parse ports
                ports_elem = host.find("ports")
                if ports_elem is not None:
                    for port in ports_elem.findall("port"):
                        port_id = port.get("portid")
                        protocol = port.get("protocol")
                        
                        state = port.find("state")
                        if state is not None and state.get("state") == "open":
                            results["open_ports"].append(int(port_id))
                            
                            # Get service information
                            service = port.find("service")
                            if service is not None:
                                service_info = {
                                    "name": service.get("name", "unknown"),
                                    "product": service.get("product", ""),
                                    "version": service.get("version", ""),
                                    "protocol": protocol
                                }
                                results["services"][port_id] = service_info
                
                # Parse OS information
                os_elem = host.find("os")
                if os_elem is not None:
                    for osmatch in os_elem.findall("osmatch"):
                        if osmatch.get("accuracy", "0") >= "80":
                            results["os_info"] = {
                                "name": osmatch.get("name"),
                                "accuracy": osmatch.get("accuracy")
                            }
                            break
        
        return results
        
    except Exception as e:
        logger.error(f"[NMAP] Failed to parse XML output: {e}")
        # Return basic results if parsing fails
        return {
            "scanner": "nmap",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "raw_output": xml_output,
            "parse_error": str(e)
        }

def report_scan_completion(scan_id: str, results: Dict[str, Any]):
    """Report successful scan completion to core service"""
    try:
        response = requests.post(
            f"{CORE_URL}/api/v1/scan/{scan_id}/complete",
            json=results,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"[NMAP] Scan completion reported: {scan_id}")
    except Exception as e:
        logger.error(f"[NMAP] Failed to report completion: {e}")

def report_scan_failure(scan_id: str, error: str):
    """Report scan failure to core service"""
    try:
        response = requests.post(
            f"{CORE_URL}/api/v1/scan/{scan_id}/fail",
            json={"error": error},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"[NMAP] Scan failure reported: {scan_id}")
    except Exception as e:
        logger.error(f"[NMAP] Failed to report failure: {e}")

if __name__ == "__main__":
    logger.info("[NMAP] Starting Nmap scanner service...")
    celery_app.start()