import time
import logging
import httpx
import json
import os
from typing import Dict, Any
import asyncio
from .queue import redis_settings

logger = logging.getLogger(__name__)

CORE_URL = os.getenv("CORE_URL", "http://core:8001")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

async def scan_asset(ctx: dict, scan_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main scan orchestration task
    Routes scan requests to appropriate scanner services
    """
    logger.info(f"[SCAN_TASK] Received task with scan_id={scan_id} and payload={payload}")
    logger.info(f"[SCAN_TASK] Context: {ctx}")
    
    if not isinstance(payload, dict):
        logger.error(f"[SCAN_TASK] Received invalid payload type: {type(payload)}")
        await report_scan_failure(scan_id, f"Invalid payload type: {type(payload)}")
        raise ValueError(f"Invalid payload type: {type(payload)}")
    
    if "target" not in payload:
        logger.error(f"[SCAN_TASK] Missing 'target' in payload: {payload}")
        await report_scan_failure(scan_id, "Missing 'target' in payload")
        raise ValueError("Missing 'target' in payload")
        
    if "scanner" not in payload:
        logger.error(f"[SCAN_TASK] Missing 'scanner' in payload: {payload}")
        await report_scan_failure(scan_id, "Missing 'scanner' in payload")
        raise ValueError("Missing 'scanner' in payload")
    
    target = payload["target"]
    scanner = payload["scanner"]
    options = payload.get("options", {})
    
    logger.info(f"[SCAN_TASK] Starting scan {scan_id} for target={target} scanner={scanner}")
    
    try:
        # Route to appropriate scanner service
        if scanner == "nmap":
            # Send task to nmap scanner service
            await ctx['redis'].enqueue_job(
                'run_nmap_scan', 
                scan_id, target, options,
                _queue_name='scanner-nmap'
            )
            logger.info(f"[SCAN_TASK] Delegated nmap scan {scan_id} to scanner service")
            
        elif scanner == "masscan":
            # Send task to masscan scanner service
            await ctx['redis'].enqueue_job(
                'run_masscan_scan', 
                scan_id, target, options,
                _queue_name='scanner-masscan'
            )
            logger.info(f"[SCAN_TASK] Delegated masscan scan {scan_id} to scanner service")
            
        elif scanner == "nuclei":
            # Send task to nuclei scanner service
            await ctx['redis'].enqueue_job(
                'run_nuclei_scan', 
                scan_id, target, options,
                _queue_name='scanner-nuclei'
            )
            logger.info(f"[SCAN_TASK] Delegated nuclei scan {scan_id} to scanner service")
            
        else:
            raise ValueError(f"Unknown scanner: {scanner}")
        
        # Don't report completion here - scanner will report back directly to core service
        logger.info(f"[SCAN_TASK] Scan {scan_id} delegated successfully")
        return {"status": "delegated", "scan_id": scan_id}
        
    except Exception as e:
        logger.error(f"[SCAN_TASK] Failed to delegate scan {scan_id}: {str(e)}")
        await report_scan_failure(scan_id, str(e))
        raise

async def report_scan_completion(scan_id: str, results: Dict[str, Any]):
    """Report successful scan completion to core service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CORE_URL}/api/v1/scan/{scan_id}/complete",
                json=results,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"[REPORT] Scan completion reported: {scan_id}")
    except Exception as e:
        logger.error(f"[REPORT] Failed to report completion: {e}")
        logger.error(f"[REPORT] Response status: {getattr(e, 'response', None) and getattr(e.response, 'status_code', 'N/A')}")


async def report_scan_failure(scan_id: str, error_message: str):
    """Report scan failure to core service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CORE_URL}/api/v1/scan/{scan_id}/fail",
                json={"error": error_message},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"[REPORT] Scan failure reported: {scan_id}")
    except Exception as e:
        logger.error(f"[REPORT] Failed to report failure: {e}")


# Helper function to update scan status in database
async def update_scan_status(scan_id: str, status: str):
    """Update scan status in database via API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{CORE_URL}/api/v1/scan/{scan_id}/status",
                json={"status": status},
                timeout=5
            )
            response.raise_for_status()
    except Exception as e:
        logger.error(f"[UPDATE] Failed to update scan status: {e}")


# Define ARQ worker settings
class WorkerSettings:
    """ARQ Worker configuration"""
    redis_settings = redis_settings
    functions = [scan_asset]
    queue_name = 'core'
    job_timeout = 300  # 5 minutes timeout for jobs
