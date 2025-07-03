# filepath: /Users/piotrtyrna/Desktop/Reconnity/easm-microservices/easm-core/app/api/routers/scan.py.new
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import json

from app.services.scan_service import ScanService
from app.schemas.scan import (
    ScanRequest, ScanResponse, ScanStatus,
    NmapScanRequest, MasscanScanRequest, NucleiScanRequest, ScannerType
)
from app.api.dependencies import get_scan_service
from app.api.errors import ScanNotFoundException
from app.core.settings import settings
from app.core.logging import get_logger
from app.tasks import get_redis_pool

# Configure logging
logger = get_logger(__name__)

router = APIRouter()

@router.post("/scan", response_model=ScanResponse)
async def create_scan(
    request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """
    Create a new scan request (generic endpoint that supports all scanner types)
    """
    try:
        logger.info(
            "Creating scan request",
            extra={"target": request.target, "scanner": request.scanner}
        )
        
        # Use service layer for business logic
        result = await scan_service.create_scan(
            target=request.target,
            scanner=request.scanner,
            options=request.options.dict() if hasattr(request.options, "dict") else request.options
        )
        
        # Create Redis connection and enqueue job
        redis = await get_redis_pool()
        payload = {
            "target": request.target,
            "scanner": request.scanner,
            "options": request.options.dict() if hasattr(request.options, "dict") else request.options
        }
        logger.info(f"Enqueueing job scan_asset with scan_id={result['scan_id']}, payload={payload}")
        job = await redis.enqueue_job(
            'scan_asset',
            result["scan_id"],
            payload,
            _queue_name='core'  # Upewnij się, że zadanie trafia do kolejki 'core'
        )
        
        logger.info(
            f"Scan job queued with ID: {job.job_id}",
            extra={"scan_id": result["scan_id"], "job_id": job.job_id}
        )
        
        return ScanResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to create scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scan: {str(e)}"
        )
