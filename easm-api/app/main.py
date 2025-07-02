from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
import httpx
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_PREFIX = "/api/v1"
CORE_URL = os.getenv("CORE_URL", "http://core:8001")

class AssetRequest(BaseModel):
    target: str
    scanner: str = "nmap"
    options: Optional[dict] = None

class ScanResponse(BaseModel):
    scan_id: str
    status: str = "queued"
    message: str

app = FastAPI(
    title="EASM API Gateway",
    description="External Attack Surface Management API Gateway",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "easm-api"}

@app.post(f"{API_PREFIX}/scan", response_model=ScanResponse)
async def create_scan(req: AssetRequest):
    """
    Create a new scan request
    
    - **target**: IP address, domain, or CIDR to scan
    - **scanner**: Type of scanner to use (nmap, masscan, etc.)
    - **options**: Additional scanner-specific options
    """
    try:
        logger.info(f"Creating scan for target: {req.target} with scanner: {req.scanner}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{CORE_URL}/api/v1/scan", 
                json=req.model_dump()
            )
            response.raise_for_status()
            result = response.json()
            
        logger.info(f"Scan created successfully: {result}")
        return ScanResponse(**result)
        
    except httpx.TimeoutException:
        logger.error("Timeout while communicating with core service")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Core service timeout"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from core service: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Core service error"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get(f"{API_PREFIX}/scan/{{scan_id}}")
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{CORE_URL}/api/v1/scan/{scan_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Core service error"
        )
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )