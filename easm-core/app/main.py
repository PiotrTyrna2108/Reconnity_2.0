from fastapi import FastAPI, Depends, HTTPException, status
import os
from celery import Celery

# Import our modules
from .core.settings import settings
from .core.logging import configure_logging, get_logger
from .api.dependencies import get_scan_service, get_settings
from .api.errors import (
    EASMException, ScanNotFoundException, ScannerNotSupportedException,
    scan_not_found_handler, scanner_not_supported_handler
)
from .schemas.scan import ScanRequest, ScanResponse, ScanStatus
from .services.scan_service import ScanService
from .api.routers import health, scan, nuclei_templates, scan_options

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
        from .database import init_db
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Add exception handlers
app.add_exception_handler(ScanNotFoundException, scan_not_found_handler)
app.add_exception_handler(ScannerNotSupportedException, scanner_not_supported_handler)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(scan.router, prefix="/api/v1", tags=["scan"])
app.include_router(nuclei_templates.router, prefix="/api/v1", tags=["nuclei"])
app.include_router(scan_options.router, prefix="/api/v1", tags=["scan"])