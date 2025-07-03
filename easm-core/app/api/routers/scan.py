from fastapi import APIRouter, Depends, HTTPException, status
from celery import Celery
from typing import Dict

from app.services.scan_service import ScanService
from app.schemas.scan import (
    ScanRequest, ScanResponse, ScanStatus,
    NmapScanRequest, MasscanScanRequest, NucleiScanRequest, ScannerType
)
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
    Create a new scan request (generic endpoint that supports all scanner types)
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
            options=request.options.dict() if hasattr(request.options, "dict") else request.options
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

@router.post("/scan/nmap", response_model=ScanResponse, summary="Create Nmap Scan", 
             description="Create a new network scan using Nmap with specific options")
async def create_nmap_scan(
    request: NmapScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """
    Create a new Nmap scan with specific options.
    
    - **ports**: Port range to scan (e.g. '1-1000', '22,80,443')
    - **scan_type**: Scan type (SYN, TCP, UDP, etc.)
    - **timing**: Timing template (0-5, higher is faster)
    - **os_detection**: Enable OS detection
    - **service_detection**: Enable service version detection
    - **script_scan**: Enable default script scan
    - **timeout**: Scan timeout in seconds
    """
    try:
        logger.info(
            "Creating Nmap scan request",
            target=request.target
        )
        
        # Use service layer for business logic
        result = await scan_service.create_scan(
            target=request.target,
            scanner=ScannerType.NMAP,
            options=request.options.dict()
        )
        
        # Queue the scan task
        celery_app.send_task(
            "app.tasks.scan_asset",
            args=[result["scan_id"], request.model_dump()],
            queue="celery"
        )
        
        return ScanResponse(**result)
        
    except Exception as e:
        logger.error("Failed to create Nmap scan", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Nmap scan"
        )
        
@router.post("/scan/masscan", response_model=ScanResponse, summary="Create Masscan Scan",
             description="Create a new fast network scan using Masscan with specific options")
async def create_masscan_scan(
    request: MasscanScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """
    Create a new Masscan scan with specific options.
    
    - **ports**: Port range to scan (e.g. '1-10000', '22,80,443')
    - **rate**: Packets per second to send
    - **timeout**: Scan timeout in seconds
    """
    try:
        logger.info(
            "Creating Masscan scan request",
            target=request.target
        )
        
        # Use service layer for business logic
        result = await scan_service.create_scan(
            target=request.target,
            scanner=ScannerType.MASSCAN,
            options=request.options.dict()
        )
        
        # Queue the scan task
        celery_app.send_task(
            "app.tasks.scan_asset",
            args=[result["scan_id"], request.model_dump()],
            queue="celery"
        )
        
        return ScanResponse(**result)
        
    except Exception as e:
        logger.error("Failed to create Masscan scan", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Masscan scan"
        )
        
@router.post("/scan/nuclei", response_model=ScanResponse, summary="Create Nuclei Vulnerability Scan",
             description="Create a new vulnerability scan using Nuclei with specific options")
async def create_nuclei_scan(
    request: NucleiScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """
    Create a new Nuclei vulnerability scan with specific options.
    
    Nuclei is a fast and customizable vulnerability scanner focused on finding security issues
    through predefined templates. It can detect a wide variety of security vulnerabilities.
    
    For available template types and severity levels, see the API endpoints:
    - `/api/v1/scan/nuclei/templates`
    - `/api/v1/scan/nuclei/severity-levels`
    
    **Supported Options:**
    - **templates**: Template directories to use (cves, dns, file, http, network, ssl, etc.)
    - **severity**: Severity levels to include (critical, high, medium, low, info)
    - **timeout**: Scan timeout in seconds
    - **rate**: Rate limiting in requests per second
    - **concurrency**: Number of concurrent requests
    - **exclude_templates**: Templates to exclude (e.g. 'cves/2020/...')
    - **retries**: Number of times to retry failed requests
    - **verbose**: Enable verbose output for more detailed results
    - **follow_redirects**: Follow HTTP redirects during scanning
    - **max_host_error**: Maximum number of errors allowed before skipping host
    """
    try:
        logger.info(
            "Creating Nuclei scan request",
            target=request.target
        )
        
        # Convert enum values to strings for the options
        options_dict = request.options.dict()
        if "templates" in options_dict and options_dict["templates"]:
            options_dict["templates"] = ",".join([t.value for t in options_dict["templates"]])
        if "severity" in options_dict and options_dict["severity"]:
            options_dict["severity"] = ",".join([s.value for s in options_dict["severity"]])
        
        # Use service layer for business logic
        result = await scan_service.create_scan(
            target=request.target,
            scanner=ScannerType.NUCLEI,
            options=options_dict
        )
        
        # Queue the scan task
        celery_app.send_task(
            "app.tasks.scan_asset",
            args=[result["scan_id"], request.model_dump()],
            queue="celery"
        )
        
        return ScanResponse(**result)
        
    except Exception as e:
        logger.error("Failed to create Nuclei scan", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Nuclei scan"
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

@router.get("/scan/options", summary="Get Scanner Options", 
         description="Get available options for all scanner types")
async def get_scanner_options():
    """Get available options for all scanner types"""
    from app.schemas.scan_options import NmapScanOptions, MasscanOptions, NucleiOptions
    
    return {
        "nmap": NmapScanOptions.schema(),
        "masscan": MasscanOptions.schema(),
        "nuclei": NucleiOptions.schema()
    }

@router.get("/scan/options/{scanner_type}", summary="Get Scanner Type Options",
         description="Get available options for a specific scanner type")
async def get_scanner_type_options(scanner_type: ScannerType):
    """Get available options for a specific scanner type"""
    from app.schemas.scan_options import NmapScanOptions, MasscanOptions, NucleiOptions
    
    options_map = {
        ScannerType.NMAP: NmapScanOptions.schema(),
        ScannerType.MASSCAN: MasscanOptions.schema(),
        ScannerType.NUCLEI: NucleiOptions.schema(),
        ScannerType.HTTPX: {"message": "HTTPX options not yet documented"}
    }
    
    if scanner_type not in options_map:
        raise HTTPException(status_code=404, detail=f"Scanner type {scanner_type} not found")
        
    return options_map[scanner_type]

@router.get("/scan/nuclei/templates", summary="List Available Nuclei Templates",
         description="Get a list of available template directories for Nuclei scanner")
async def list_nuclei_templates():
    """Get a list of available Nuclei template directories"""
    # This could be enhanced to actually check the filesystem for available templates
    from app.schemas.scan_options import NucleiTemplateEnum
    
    return {
        "available_templates": [t.value for t in NucleiTemplateEnum],
        "description": "These are the standard template directories available in Nuclei"
    }
