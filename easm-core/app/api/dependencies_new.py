from fastapi import Depends
from sqlalchemy.orm import Session
from ..services.scan_service import ScanService
from ..core.settings import settings
from ..database import get_db

def get_scan_service(db: Session = Depends(get_db)) -> ScanService:
    """Dependency to get scan service instance with database session"""
    return ScanService(db=db)

def get_settings():
    """Dependency to get application settings"""
    return settings
