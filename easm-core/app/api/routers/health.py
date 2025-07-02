from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from app.services.scan_service import ScanService
from app.schemas.health import HealthCheck
from app.core.settings import settings
from app.api.dependencies import get_settings

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint with detailed information"""
    return HealthCheck(
        status="healthy",
        service="easm-core",
        version=settings.version
    )
