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

async def run_nmap_scan(ctx: Dict, scan_id: str, target: str, options: Dict[str, Any] = None):
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
        
        # Execute nmap scan (using subprocess since nmap doesn't support async)
        start_time = time.time()
        process = subprocess.run(
            nmap_args,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        scan_duration = time.time() - start_time
        
        if process.returncode == 0:
            # Parse nmap output
            scan_results = parse_nmap_output(process.stdout, target, scan_id, scan_duration)
            
            logger.info(f"[NMAP] Scan completed successfully: {scan_id}")
            
            # Report results to core service
            await report_scan_completion(ctx, scan_id, scan_results)
            
        else:
            error_msg = f"Nmap scan failed with return code {process.returncode}: {process.stderr}"
            logger.error(f"[NMAP] {error_msg}")
            await report_scan_failure(ctx, scan_id, error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Nmap scan timed out after 5 minutes"
        logger.error(f"[NMAP] {error_msg}")
        await report_scan_failure(ctx, scan_id, error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during nmap scan: {str(e)}"
        logger.error(f"[NMAP] {error_msg}")
        await report_scan_failure(ctx, scan_id, error_msg)


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
            scanner='nmap',
            _queue_name='core'
        )
        logger.info(f"[NMAP] Scan completion message sent: {scan_id}")
    except Exception as e:
        logger.error(f"[NMAP] Failed to send completion message: {e}")


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
            scanner='nmap',
            _queue_name='core'
        )
        logger.info(f"[NMAP] Scan failure message sent: {scan_id}")
    except Exception as e:
        logger.error(f"[NMAP] Failed to send failure message: {e}")


class WorkerSettings:
    """ARQ Worker settings"""
    functions = [run_nmap_scan]
    redis_settings = parse_redis_url(REDIS_URL)
    queue_name = 'scanner-nmap'


if __name__ == "__main__":
    logger.info("[NMAP] Starting Nmap scanner service with ARQ...")
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