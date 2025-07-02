from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.schemas.asset import AssetBase

class ScanRequest(AssetBase):
    """Schema for scan request"""
    scanner: str = Field(default="nmap", description="Scanner type")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Scanner options")
    
    @validator('scanner')
    def validate_scanner(cls, v):
        """Validate scanner type"""
        supported_scanners = {'nmap', 'masscan', 'nuclei', 'httpx'}
        if v not in supported_scanners:
            raise ValueError(f'Unsupported scanner. Supported: {supported_scanners}')
        return v

class ScanResponse(BaseModel):
    """Schema for scan response"""
    scan_id: str
    status: str
    message: str

class ScanStatus(BaseModel):
    """Schema for scan status"""
    scan_id: str
    target: str
    scanner: str
    status: str
    progress: int = Field(ge=0, le=100)
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    findings: Optional[List[Dict[str, Any]]] = None
    risk_score: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class Finding(BaseModel):
    """Schema for scan finding"""
    id: str
    scan_id: str
    target: str
    finding_type: str = Field(..., description="Type of finding (open_port, service, vulnerability)")
    severity: str = Field(..., description="Severity level (critical, high, medium, low, info)")
    title: str
    description: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    service: Optional[str] = None
    created_at: str
    verified: bool = False
    metadata: Optional[Dict[str, Any]] = None

class RiskScore(BaseModel):
    """Schema for risk score"""
    score: int = Field(ge=0, le=100)
    level: str = Field(..., description="Risk level (critical, high, medium, low, info)")
    factors: Dict[str, float]
    calculated_at: str

class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str
    service: str
    version: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
