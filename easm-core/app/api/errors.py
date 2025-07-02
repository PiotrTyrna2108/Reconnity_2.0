from fastapi import HTTPException, status
from typing import Dict, Any

class EASMException(Exception):
    """Base exception for EASM application"""
    pass

class ScanNotFoundException(EASMException):
    """Raised when scan is not found"""
    pass

class ScannerNotSupportedException(EASMException):
    """Raised when scanner is not supported"""
    pass

class TargetValidationException(EASMException):
    """Raised when target validation fails"""
    pass

def scan_not_found_handler(request, exc: ScanNotFoundException):
    """Handle scan not found exception"""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Scan not found"
    )

def scanner_not_supported_handler(request, exc: ScannerNotSupportedException):
    """Handle unsupported scanner exception"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Scanner not supported: {str(exc)}"
    )

def target_validation_handler(request, exc: TargetValidationException):
    """Handle target validation exception"""
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Invalid target: {str(exc)}"
    )
