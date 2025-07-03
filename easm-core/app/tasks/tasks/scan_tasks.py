import time
import logging
import httpx
import json
import os
from typing import Dict, Any
import asyncio
from ..config.redis_config import redis_settings
from ..config.retry_helpers import with_redis_retry
from ...core.logging import get_logger

logger = get_logger(__name__)

CORE_URL = os.getenv("CORE_URL", "http://core:8001")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

@with_redis_retry(max_retries=3, retry_delay=1.0, operation_name="enqueue_job")
async def enqueue_job_with_retry(redis_client, function_name, *args, _queue_name=None, queue_display=None, **kwargs):
    """Enqueue a job with retry logic"""
    return await redis_client.enqueue_job(
        function_name,
        *args,
        _queue_name=_queue_name,
        **kwargs
    )

async def scan_asset(ctx: dict, scan_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main scan orchestration task
    Routes scan requests to appropriate scanner services
    """
    logger.info(f"[SCAN_TASK] Received task with scan_id={scan_id} and payload={payload}")
    logger.info(f"[SCAN_TASK] Context: {ctx}")
    
    if not isinstance(payload, dict):
        logger.error(f"[SCAN_TASK] Received invalid payload type: {type(payload)}")
        await report_scan_error(ctx, scan_id, f"Invalid payload type: {type(payload)}")
        raise ValueError(f"Invalid payload type: {type(payload)}")
    
    if "target" not in payload:
        logger.error(f"[SCAN_TASK] Missing 'target' in payload: {payload}")
        await report_scan_error(ctx, scan_id, "Missing 'target' in payload")
        raise ValueError("Missing 'target' in payload")
        
    if "scanner" not in payload:
        logger.error(f"[SCAN_TASK] Missing 'scanner' in payload: {payload}")
        await report_scan_error(ctx, scan_id, "Missing 'scanner' in payload")
        raise ValueError("Missing 'scanner' in payload")
    
    target = payload["target"]
    scanner = payload["scanner"]
    options = payload.get("options", {})
    
    logger.info(f"[SCAN_TASK] Starting scan {scan_id} for target={target} scanner={scanner}")
    
    try:
        # Route to appropriate scanner service
        if scanner == "nmap":
            # Send task to nmap scanner service with retry logic
            await enqueue_job_with_retry(
                ctx['redis'],
                'run_nmap_scan', 
                scan_id, target, options,
                _queue_name='scanner-nmap',
                queue_display="scanner-nmap"
            )
            logger.info(f"[SCAN_TASK] Delegated nmap scan {scan_id} to scanner service")
            
        elif scanner == "masscan":
            # Send task to masscan scanner service with retry logic
            await enqueue_job_with_retry(
                ctx['redis'],
                'run_masscan_scan', 
                scan_id, target, options,
                _queue_name='scanner-masscan',
                queue_display="scanner-masscan"
            )
            logger.info(f"[SCAN_TASK] Delegated masscan scan {scan_id} to scanner service")
            
        elif scanner == "nuclei":
            # Send task to nuclei scanner service with retry logic
            await enqueue_job_with_retry(
                ctx['redis'],
                'run_nuclei_scan', 
                scan_id, target, options,
                _queue_name='scanner-nuclei',
                queue_display="scanner-nuclei"
            )
            logger.info(f"[SCAN_TASK] Delegated nuclei scan {scan_id} to scanner service")
            
        else:
            raise ValueError(f"Unknown scanner: {scanner}")
        
        # Don't report completion here - scanner will report back directly to core service
        logger.info(f"[SCAN_TASK] Scan {scan_id} delegated successfully")
        return {"status": "delegated", "scan_id": scan_id}
        
    except Exception as e:
        logger.error(f"[SCAN_TASK] Failed to delegate scan {scan_id}: {str(e)}")
        await report_scan_error(ctx, scan_id, str(e))
        raise

async def process_scan_result(ctx: dict, scan_id: str, status: str, **kwargs) -> Dict[str, Any]:
    """
    Process scan results coming from scanners via Redis message queue
    This is the preferred way for scanners to report results (instead of HTTP callbacks)
    """
    logger.info(f"[PROCESS] Received scan result for {scan_id} with status {status}")
    
    # Create database session
    db = None
    
    try:
        # Import here to avoid circular imports
        from ..services.scan_service import ScanService
        from ..database import SessionLocal
        
        # Create database session
        db = SessionLocal()
        scan_service = ScanService(db)
        
        if status == "completed":
            results = kwargs.get("results", {})
            scanner = kwargs.get("scanner", "unknown")
            
            # Use ScanService directly to update the database
            success = await scan_service.complete_scan(scan_id, results)
            
            if success:
                logger.info(f"[PROCESS] Scan completion processed: {scan_id} (scanner: {scanner})")
                return {
                    "status": "success", 
                    "scan_id": scan_id, 
                    "message": "Scan results processed successfully"
                }
            else:
                logger.error(f"[PROCESS] Failed to process scan completion: Scan not found")
                return {
                    "status": "error",
                    "scan_id": scan_id,
                    "message": "Scan not found"
                }
            
        elif status == "failed":
            error = kwargs.get("error", "Unknown error")
            scanner = kwargs.get("scanner", "unknown")
            
            # Use ScanService directly to update the database
            success = await scan_service.fail_scan(scan_id, error)
            
            if success:
                logger.info(f"[PROCESS] Scan failure processed: {scan_id} (scanner: {scanner})")
                return {
                    "status": "failed", 
                    "scan_id": scan_id, 
                    "message": f"Scan failure processed: {error}"
                }
            else:
                logger.error(f"[PROCESS] Failed to process scan failure: Scan not found")
                return {
                    "status": "error",
                    "scan_id": scan_id,
                    "message": "Scan not found"
                }
            
        else:
            error_msg = f"Unknown scan status: {status}"
            logger.error(f"[PROCESS] {error_msg}")
            return {"status": "error", "message": error_msg}
            
    except Exception as e:
        logger.error(f"[PROCESS] Failed to process scan result: {e}")
        return {"status": "error", "message": f"Failed to process scan result: {str(e)}"}
    finally:
        # Close database session if it was created
        if db:
            db.close()

async def report_scan_error(ctx: dict, scan_id: str, error_message: str):
    """
    Report scan error using Redis message queue
    This is a helper function used internally by scan_asset
    """
    logger.error(f"[SCAN_ERROR] {error_message} for scan {scan_id}")
    
    try:
        # Process the error directly through process_scan_result function
        await process_scan_result(
            ctx,
            scan_id=scan_id,
            status='failed',
            error=error_message,
            scanner='core'
        )
    except Exception as e:
        logger.error(f"[SCAN_ERROR] Failed to report error via Redis: {str(e)}")

# Note: Legacy HTTP callback methods have been removed as part of ARQ migration
# All communication now happens via Redis message queue


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
    functions = [scan_asset, process_scan_result]
    queue_name = 'core'
    job_timeout = 300  # 5 minutes timeout for jobs
