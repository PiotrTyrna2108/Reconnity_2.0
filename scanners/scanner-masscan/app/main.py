import subprocess
import json
import os
import time
import logging
import httpx
import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ARQ Redis settings from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CORE_URL = os.getenv("CORE_URL", "http://core:8001")

# Parse Redis URL
def parse_redis_url(url: str):
    """Parse Redis URL into components for ARQ RedisSettings"""
    if url.startswith("redis://"):
        url = url[len("redis://"):]
    
    host_port, *rest = url.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 6379
        
    db = int(rest[0]) if rest else 0
    
    return RedisSettings(
        host=host,
        port=port,
        database=db
    )

async def run_masscan_scan(ctx: Dict, scan_id: str, target: str, options: Dict[str, Any] = None):
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
            await report_scan_failure(scan_id, error_msg)
            return
            
        # Build masscan command
        masscan_args = build_masscan_command(target, options)
        logger.info(f"[MASSCAN] Running command: {' '.join(masscan_args)}")
        
        # Execute masscan scan
        start_time = time.time()
        process = subprocess.run(
            masscan_args,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout for masscan (faster than nmap)
        )
        scan_duration = time.time() - start_time
        
        if process.returncode == 0:
            # Parse masscan output
            scan_results = parse_masscan_output(process.stdout, target, scan_id, scan_duration)
            
            logger.info(f"[MASSCAN] Scan completed successfully: {scan_id}")
            
            # Report results to core service via Redis messaging
            await report_scan_completion(ctx, scan_id, scan_results)
            
        else:
            error_msg = f"Masscan scan failed with return code {process.returncode}: {process.stderr}"
            logger.error(f"[MASSCAN] {error_msg}")
            await report_scan_failure(ctx, scan_id, error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Masscan scan timed out after 2 minutes"
        logger.error(f"[MASSCAN] {error_msg}")
        await report_scan_failure(ctx, scan_id, error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during masscan scan: {str(e)}"
        logger.error(f"[MASSCAN] {error_msg}")
        await report_scan_failure(ctx, scan_id, error_msg)


def build_masscan_command(target: str, options: Dict[str, Any]) -> list:
    """Build masscan command with appropriate flags"""
    cmd = ["masscan"]
    
    # Add target
    cmd.append(target)
    
    # Add ports
    if "ports" in options:
        cmd.extend(["-p", options["ports"]])
    else:
        cmd.extend(["-p", "1-10000"])  # Default port range
    
    # Add rate limiting
    if "rate" in options:
        cmd.extend(["--rate", str(options["rate"])])
    else:
        cmd.extend(["--rate", "1000"])  # Default rate
    
    # Add json output
    cmd.extend(["--output-format", "json", "--output-filename", "-"])
    
    # Exclude reserved addresses
    cmd.append("--exclude-file=/etc/masscan/exclude.conf")
    
    return cmd


def parse_masscan_output(json_output: str, target: str, scan_id: str, duration: float) -> Dict[str, Any]:
    """Parse masscan JSON output and extract relevant information"""
    try:
        # Handle the case when masscan doesn't produce any output
        if not json_output.strip():
            logger.warning(f"[MASSCAN] No output for {target}")
            return {
                "scanner": "masscan",
                "target": target,
                "scan_id": scan_id,
                "scan_duration": duration,
                "timestamp": time.time(),
                "open_ports": [],
                "services": {}
            }
        
        # Parse the JSON output (masscan outputs one JSON object per line)
        results = {
            "scanner": "masscan",
            "target": target,
            "scan_id": scan_id,
            "scan_duration": duration,
            "timestamp": time.time(),
            "open_ports": [],
            "services": {}
        }
        
        for line in json_output.splitlines():
            line = line.strip()
            if not line:
                continue
            
            try:
                finding = json.loads(line)
                if "ports" in finding and finding["ports"]:
                    port = finding["ports"][0]
                    if port["status"] == "open":
                        port_number = port["port"]
                        results["open_ports"].append(port_number)
                        
                        # Basic service identification
                        service_name = identify_service_by_port(port_number)
                        results["services"][str(port_number)] = {
                            "name": service_name,
                            "protocol": port["proto"],
                            "state": "open"
                        }
            except json.JSONDecodeError:
                logger.warning(f"[MASSCAN] Failed to parse line: {line}")
                continue
        
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
    common_ports = {
        21: "ftp",
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "dns",
        80: "http",
        110: "pop3",
        143: "imap",
        443: "https",
        465: "smtps",
        587: "smtp",
        993: "imaps",
        995: "pop3s",
        3306: "mysql",
        3389: "rdp",
        5432: "postgresql",
        8080: "http-proxy",
        8443: "https-alt"
    }
    
    return common_ports.get(port, "unknown")


async def report_scan_completion(ctx: Dict, scan_id: str, results: Dict[str, Any]):
    """Report scan completion via Redis message to core service"""
    try:
        # Send scan result message to core queue
        redis_pool = ctx.get('redis') or await create_pool(parse_redis_url(REDIS_URL))
        await redis_pool.enqueue_job(
            'process_scan_result',
            scan_id=scan_id,
            status='completed',
            results=results,
            scanner='masscan',
            _queue_name='core'
        )
        logger.info(f"[MASSCAN] Scan completion message sent: {scan_id}")
    except Exception as e:
        logger.error(f"[MASSCAN] Failed to send completion message: {e}")


async def report_scan_failure(ctx: Dict, scan_id: str, error: str):
    """Report scan failure via Redis message to core service"""
    try:
        # Send scan failure message to core queue
        redis_pool = ctx.get('redis') or await create_pool(parse_redis_url(REDIS_URL))
        await redis_pool.enqueue_job(
            'process_scan_result',
            scan_id=scan_id,
            status='failed',
            error=error,
            scanner='masscan',
            _queue_name='core'
        )
        logger.info(f"[MASSCAN] Scan failure message sent: {scan_id}")
    except Exception as e:
        logger.error(f"[MASSCAN] Failed to send failure message: {e}")


class WorkerSettings:
    """ARQ Worker settings"""
    functions = [run_masscan_scan]
    redis_settings = parse_redis_url(REDIS_URL)
    queue_name = 'scanner-masscan'


if __name__ == "__main__":
    logger.info("[MASSCAN] Starting Masscan scanner service with ARQ...")
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        import asyncio
        from arq.worker import Worker
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                Worker(WorkerSettings).run()
            )
        except KeyboardInterrupt:
            pass