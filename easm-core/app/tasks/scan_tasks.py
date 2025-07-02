from . import celery_app
import time
import logging
import httpx
import requests
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

CORE_URL = os.getenv("CORE_URL", "http://core:8001")

@celery_app.task(name="app.tasks.scan_asset", bind=True)
def scan_asset(self, scan_id: str, payload: Dict[str, Any]):
    """
    Main scan orchestration task
    Routes scan requests to appropriate scanner services
    """
    target = payload["target"]
    scanner = payload["scanner"]
    options = payload.get("options", {})
    
    logger.info(f"[SCAN_TASK] Starting scan {scan_id} for target={target} scanner={scanner}")
    
    try:
        # Route to appropriate scanner service
        if scanner == "nmap":
            # Send task to nmap scanner service
            celery_app.send_task(
                "scanner-nmap.run",
                args=[scan_id, target, options],
                queue="scanner-nmap"
            )
            logger.info(f"[SCAN_TASK] Delegated nmap scan {scan_id} to scanner service")
            
        elif scanner == "masscan":
            # Send task to masscan scanner service
            celery_app.send_task(
                "scanner-masscan.run",
                args=[scan_id, target, options],
                queue="scanner-masscan"
            )
            logger.info(f"[SCAN_TASK] Delegated masscan scan {scan_id} to scanner service")
            
        else:
            raise ValueError(f"Unknown scanner: {scanner}")
        
        # Don't report completion here - scanner will report back directly to core service
        logger.info(f"[SCAN_TASK] Scan {scan_id} delegated successfully")
        
    except Exception as e:
        logger.error(f"[SCAN_TASK] Failed to delegate scan {scan_id}: {str(e)}")
        report_scan_failure(scan_id, str(e))
        raise

def report_scan_completion(scan_id: str, results: Dict[str, Any]):
    """Report successful scan completion to core service"""
    try:
        import requests
        response = requests.post(
            f"{CORE_URL}/internal/scan/{scan_id}/complete",
            json=results,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"[REPORT] Scan completion reported: {scan_id}")
    except Exception as e:
        logger.error(f"[REPORT] Failed to report completion: {e}")

def report_scan_failure(scan_id: str, error: str):
    """Report scan failure to core service"""
    try:
        import requests
        response = requests.post(
            f"{CORE_URL}/internal/scan/{scan_id}/fail",
            json={"error": error},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"[REPORT] Scan failure reported: {scan_id}")
    except Exception as e:
        logger.error(f"[REPORT] Failed to report failure: {e}")