from fastapi import APIRouter, Depends, HTTPException, status
from celery import Celery
from typing import Dict

from app.services.scan_service import ScanService
from app.schemas.scan import ScanRequest, ScanResponse, ScanStatus
from app.api.dependencies import get_scan_service
from app.api.errors import ScanNotFoundException
from app.core.settings import settings
from app.core.logging import get_logger

# Configure celery
celery_app = Celery("core", broker=settings.celery_broker_url)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure logging
logger = get_logger(__name__)

router = APIRouter()

@router.post("/scan", response_model=ScanResponse)
async def create_scan(
    request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """
    Create a new scan request (Clean Architecture pattern)
    """
    try:
        logger.info(
            "Creating scan request",
            target=request.target,
            scanner=request.scanner
        )
        
        # Use service layer for business logic
        result = await scan_service.create_scan(
            target=request.target,
            scanner=request.scanner,
            options=request.options
        )
        
        # Queue the scan task
        celery_app.send_task(
            "app.tasks.scan_asset",
            args=[result["scan_id"], request.model_dump()],
            queue="celery"
        )
        
        return ScanResponse(**result)
        
    except Exception as e:
        logger.error("Failed to create scan", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scan"
        )

@router.get("/scan/{scan_id}", response_model=ScanStatus)
async def get_scan_status(
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service)
):
    """Get scan status and results"""
    scan_data = await scan_service.get_scan_status(scan_id)
    
    if not scan_data:
        raise ScanNotFoundException(f"Scan {scan_id} not found")
    
    return ScanStatus(**scan_data)

@router.post("/scan/{scan_id}/complete")
async def complete_scan(
    scan_id: str,
    results: dict,
    scan_service: ScanService = Depends(get_scan_service)
):
    """Mark scan as completed with results"""
    success = await scan_service.complete_scan(scan_id, results)
    
    if not success:
        raise ScanNotFoundException(f"Scan {scan_id} not found")
    
    return {"message": "Scan marked as completed"}

@router.post("/scan/{scan_id}/fail")
async def fail_scan(
    scan_id: str,
    error_data: dict,
    scan_service: ScanService = Depends(get_scan_service)
):
    """Mark scan as failed"""
    error_message = error_data.get("error", "Unknown error")
    success = await scan_service.fail_scan(scan_id, error_message)
    
    if not success:
        raise ScanNotFoundException(f"Scan {scan_id} not found")
    
    return {"message": "Scan marked as failed"}
