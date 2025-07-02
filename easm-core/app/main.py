from fastapi import FastAPI, HTTPException, status, Depends
from celery import Celery
import os

# Import our modules
from .core.settings import settings
from .core.logging import configure_logging, get_logger
from .api.dependencies import get_scan_service, get_settings
from .api.errors import (
    EASMException, ScanNotFoundException, ScannerNotSupportedException,
    scan_not_found_handler, scanner_not_supported_handler
)
from .schemas.scan import ScanRequest, ScanResponse, ScanStatus, HealthCheck
from .services.scan_service import ScanService
from .database import init_db

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Core business logic for EASM with Clean Architecture",
    version=settings.version,
    debug=settings.debug
)

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Add exception handlers
app.add_exception_handler(ScanNotFoundException, scan_not_found_handler)
app.add_exception_handler(ScannerNotSupportedException, scanner_not_supported_handler)

# Celery configuration
celery_app = Celery("core", broker=settings.celery_broker_url)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint with detailed information"""
    return HealthCheck(
        status="healthy",
        service="easm-core",
        version=settings.version
    )

@app.post("/internal/scan", response_model=ScanResponse)
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

@app.get("/internal/scan/{scan_id}", response_model=ScanStatus)
async def get_scan_status(
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service)
):
    """Get scan status and results"""
    scan_data = await scan_service.get_scan_status(scan_id)
    
    if not scan_data:
        raise ScanNotFoundException(f"Scan {scan_id} not found")
    
    return ScanStatus(**scan_data)

@app.post("/internal/scan/{scan_id}/complete")
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

@app.post("/internal/scan/{scan_id}/fail")
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