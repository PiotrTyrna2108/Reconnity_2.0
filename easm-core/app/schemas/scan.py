from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union, Literal
from datetime import datetime
from enum import Enum

from app.schemas.asset import AssetBase
from app.schemas.scan_options import NmapScanOptions, MasscanOptions, NucleiOptions

class ScannerType(str, Enum):
    NMAP = "nmap"
    MASSCAN = "masscan"
    NUCLEI = "nuclei"
    HTTPX = "httpx"

class BaseScanRequest(AssetBase):
    """Base schema for all scan requests"""
    pass

class NmapScanRequest(BaseScanRequest):
    """Schema for Nmap scan request"""
    scanner: Literal[ScannerType.NMAP] = ScannerType.NMAP
    options: Optional[NmapScanOptions] = Field(default_factory=NmapScanOptions)

class MasscanScanRequest(BaseScanRequest):
    """Schema for Masscan scan request"""
    scanner: Literal[ScannerType.MASSCAN] = ScannerType.MASSCAN
    options: Optional[MasscanOptions] = Field(default_factory=MasscanOptions)

class NucleiScanRequest(BaseScanRequest):
    """Schema for Nuclei scan request"""
    scanner: Literal[ScannerType.NUCLEI] = ScannerType.NUCLEI
    options: Optional[NucleiOptions] = Field(default_factory=NucleiOptions)

class GenericScanRequest(BaseScanRequest):
    """Compatibility schema for generic scan requests"""
    scanner: ScannerType = Field(default=ScannerType.NMAP, description="Scanner type")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Scanner options")

# Union of all scan request types
ScanRequest = Union[NmapScanRequest, MasscanScanRequest, NucleiScanRequest, GenericScanRequest]

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
