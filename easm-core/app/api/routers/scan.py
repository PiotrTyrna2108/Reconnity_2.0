from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Dict, Any, Optional
import json

from ...services.scan_service import ScanService
from ...schemas.scan import (
    ScanRequest, ScanResponse, ScanStatus,
    NmapScanRequest, MasscanScanRequest, NucleiScanRequest, ScannerType
)
from ..dependencies import get_scan_service
from ..errors import ScanNotFoundException
from ...core.settings import settings
from ...core.logging import get_logger
from ...tasks import get_redis_pool

# Configure logging
logger = get_logger(__name__)

router = APIRouter()

@router.post("/scan", 
            response_model=ScanResponse,
            summary="Create New Scan", 
            description="""
Create a new security scan for a target using specified scanner.

**Supported Scanners:**
- **nmap**: Network discovery and port scanning (most comprehensive)
- **masscan**: Fast port scanning for large networks
- **nuclei**: Web vulnerability scanning with templates

**Target Formats:**
- Single IP: `192.168.1.1`
- Network range: `192.168.1.0/24` 
- Domain: `example.com`
- URL: `https://httpbin.org`

**Examples:**

*Nmap scan:*
```json
{
  "target": "scanme.nmap.org",
  "scanner": "nmap",
  "options": {
    "ports": "80,443,22",
    "scan_type": "SYN",
    "service_detection": true
  }
}
```

*Masscan scan:*
```json
{
  "target": "192.168.1.0/24", 
  "scanner": "masscan",
  "options": {
    "ports": "1-1000",
    "rate": "1000"
  }
}
```

*Nuclei scan:*
```json
{
  "target": "https://httpbin.org",
  "scanner": "nuclei", 
  "options": {
    "templates": ["tech-detect", "cves"],
    "severity": ["high", "critical"]
  }
}
```
            """,
            tags=["Scanning"])
async def create_scan(
    request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """
    Create a new scan request (supports all scanner types)
    
    Returns a scan_id that can be used to track the scan progress and retrieve results.
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

@router.get("/scan/{scan_id}", 
           response_model=ScanStatus,
           summary="Get Scan Results",
           description="""
Get comprehensive scan status and results by scan ID.

**Response includes:**
- Scan status (`queued`, `running`, `completed`, `failed`)
- Target information and scanner used  
- Complete scan results with discovered services
- Security findings with risk assessments
- Overall risk score and factors

**Scan Status Values:**
- `queued`: Scan is waiting to be processed
- `running`: Scan is currently executing  
- `completed`: Scan finished successfully
- `failed`: Scan encountered an error

Use the scan_id returned from the POST /scan endpoint to track your scan progress.
           """,
           tags=["Scanning"])
async def get_scan_status(
    scan_id: str = Path(..., description="Unique scan identifier returned from scan creation", example="12345678-1234-5678-9abc-123456789abc"), 
    scan_service: ScanService = Depends(get_scan_service)
):
    """Get detailed scan status, progress, and results by scan_id"""
    result = await scan_service.get_scan_status(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanStatus(**result)

@router.post("/scan/quick",
            response_model=ScanResponse,
            summary="Quick Scan (with URL parameters)",
            description="""
Alternative endpoint for creating scans using URL parameters instead of JSON body.
Useful for quick testing and simple integrations.

**Examples:**
- `POST /api/v1/scan/quick?target=scanme.nmap.org&scanner=nmap&ports=80,443`
- `POST /api/v1/scan/quick?target=httpbin.org&scanner=nuclei&templates=tech-detect`
            """,
            tags=["Scanning"])
async def create_quick_scan(
    target: str = Query(..., description="Target to scan", example="scanme.nmap.org"),
    scanner: ScannerType = Query(default="nmap", description="Scanner type to use"),
    ports: Optional[str] = Query(default=None, description="Ports to scan (e.g., '80,443,22' or '1-1000')", example="80,443,22"),
    scan_type: Optional[str] = Query(default="SYN", description="Scan type for nmap", example="SYN"),
    rate: Optional[int] = Query(default=None, description="Scan rate for masscan", example=1000),
    templates: Optional[str] = Query(default=None, description="Nuclei templates (comma-separated)", example="tech-detect,cves"),
    severity: Optional[str] = Query(default=None, description="Nuclei severity levels (comma-separated)", example="high,critical"),
    scan_service: ScanService = Depends(get_scan_service)
):
    """
    Create a new scan using query parameters instead of JSON body
    
    This endpoint provides a simpler way to create scans for testing and basic integrations.
    """
    try:
        # Build options based on scanner type and provided parameters
        options = {}
        
        if scanner == "nmap":
            if ports:
                options["ports"] = ports
            if scan_type:
                options["scan_type"] = scan_type
                
        elif scanner == "masscan":
            if ports:
                options["ports"] = ports
            if rate:
                options["rate"] = rate
                
        elif scanner == "nuclei":
            if templates:
                options["templates"] = templates.split(",")
            if severity:
                options["severity"] = severity.split(",")
        
        logger.info(f"Creating quick scan - target: {target}, scanner: {scanner}, options: {options}")
        
        # Use service layer for business logic
        result = await scan_service.create_scan(
            target=target,
            scanner=scanner,
            options=options
        )
        
        # Create Redis connection and enqueue job
        redis = await get_redis_pool()
        payload = {
            "target": target,
            "scanner": scanner,
            "options": options
        }
        
        job = await redis.enqueue_job(
            'scan_asset',
            result["scan_id"],
            payload,
            _queue_name='core'
        )
        
        logger.info(f"Quick scan job queued with ID: {job.job_id}", extra={"scan_id": result["scan_id"], "job_id": job.job_id})
        
        return ScanResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to create quick scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scan: {str(e)}"
        )

# Note: HTTP callback endpoints have been removed as part of ARQ migration
# All scanner communication now happens via Redis message queue through process_scan_result function
