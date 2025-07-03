from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from enum import Enum
from pydantic import BaseModel

from app.schemas.scan import ScannerType
from app.schemas.scan_options import NmapScanOptions, MasscanOptions, NucleiOptions
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

class ScannerOptions(BaseModel):
    """Schema for available scanner options"""
    scanner: str
    description: str
    options: Dict[str, Any]
    
@router.get("/scan/options", summary="Get All Scanner Options", 
            description="Returns options for all available scanners")
async def get_scanner_options():
    """
    Get configuration options for all available scanners
    
    Returns a list of all scanner types with their available options and default values.
    This helps API users understand what options are available for each scanner type.
    """
    try:
        # Build options dictionary for each scanner
        scanners = [
            {
                "scanner": ScannerType.NMAP.value,
                "description": "Network port scanner with service detection capabilities",
                "options": NmapScanOptions().dict(exclude_none=True)
            },
            {
                "scanner": ScannerType.MASSCAN.value,
                "description": "Fast mass IP port scanner",
                "options": MasscanOptions().dict(exclude_none=True)
            },
            {
                "scanner": ScannerType.NUCLEI.value, 
                "description": "Vulnerability scanner with template-based detection",
                "options": NucleiOptions().dict(exclude_none=True)
            },
            # Additional scanners can be added here
        ]
        
        return scanners
    except Exception as e:
        logger.error(f"Failed to get scanner options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scanner options"
        )

@router.get("/scan/options/{scanner_type}", summary="Get Scanner Type Options",
            description="Returns options for a specific scanner type")
async def get_scanner_type_options(scanner_type: ScannerType):
    """
    Get configuration options for a specific scanner type
    
    Parameters:
    - **scanner_type**: Type of scanner (nmap, masscan, nuclei)
    
    Returns details about available options, their default values, and descriptions
    for the specified scanner type.
    """
    try:
        if scanner_type == ScannerType.NMAP:
            return {
                "scanner": ScannerType.NMAP.value,
                "description": "Network port scanner with service detection capabilities",
                "options": NmapScanOptions().dict(exclude_none=True)
            }
        elif scanner_type == ScannerType.MASSCAN:
            return {
                "scanner": ScannerType.MASSCAN.value,
                "description": "Fast mass IP port scanner",
                "options": MasscanOptions().dict(exclude_none=True)
            }
        elif scanner_type == ScannerType.NUCLEI:
            return {
                "scanner": ScannerType.NUCLEI.value,
                "description": "Vulnerability scanner with template-based detection",
                "options": NucleiOptions().dict(exclude_none=True)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scanner type {scanner_type} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scanner options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scanner options"
        )
