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
    """
    Nmap scan request for network discovery and port scanning
    
    Nmap is the most popular network scanning tool for:
    - Port scanning (TCP/UDP)
    - Service detection and version identification
    - OS fingerprinting
    - Script scanning for vulnerabilities
    
    Example: {"target": "scanme.nmap.org", "scanner": "nmap", "options": {"ports": "1-1000", "scan_type": "SYN", "service_detection": true}}
    """
    scanner: Literal[ScannerType.NMAP] = Field(
        default=ScannerType.NMAP,
        description="Nmap scanner type"
    )
    options: Optional[NmapScanOptions] = Field(
        default_factory=NmapScanOptions,
        description="Nmap-specific scanning options"
    )

class MasscanScanRequest(BaseScanRequest):
    """
    Masscan scan request for fast port scanning
    
    Masscan is the fastest port scanner for:
    - High-speed TCP port scanning
    - Large network range scanning
    - Internet-wide scanning capabilities
    
    Example: {"target": "192.168.1.0/24", "scanner": "masscan", "options": {"ports": "80,443,22", "rate": "1000"}}
    """
    scanner: Literal[ScannerType.MASSCAN] = Field(
        default=ScannerType.MASSCAN,
        description="Masscan scanner type"
    )
    options: Optional[MasscanOptions] = Field(
        default_factory=MasscanOptions,
        description="Masscan-specific scanning options"
    )

class NucleiScanRequest(BaseScanRequest):
    """
    Nuclei scan request for vulnerability detection
    
    Nuclei is a template-based vulnerability scanner for:
    - Web application vulnerability scanning
    - Misconfiguration detection
    - CVE detection with community templates
    - Custom vulnerability template execution
    
    Example: {"target": "https://example.com", "scanner": "nuclei", "options": {"templates": ["tech-detect", "cves"], "severity": ["critical", "high"]}}
    """
    scanner: Literal[ScannerType.NUCLEI] = Field(
        default=ScannerType.NUCLEI,
        description="Nuclei scanner type"
    )
    options: Optional[NucleiOptions] = Field(
        default_factory=NucleiOptions,
        description="Nuclei-specific scanning options"
    )

class GenericScanRequest(BaseScanRequest):
    """
    Generic scan request that supports all scanner types
    
    Use this schema when you want to specify the scanner type and custom options.
    Examples:
    - For Nmap: {"target": "scanme.nmap.org", "scanner": "nmap", "options": {"ports": "80,443", "scan_type": "SYN"}}
    - For Masscan: {"target": "192.168.1.0/24", "scanner": "masscan", "options": {"ports": "1-1000", "rate": "1000"}}
    - For Nuclei: {"target": "https://example.com", "scanner": "nuclei", "options": {"templates": ["tech-detect"], "severity": ["high"]}}
    """
    scanner: ScannerType = Field(
        default=ScannerType.NMAP, 
        description="Type of scanner to use",
        example="nmap"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Scanner-specific options",
        example={
            "ports": "80,443,22",
            "scan_type": "SYN",
            "timing": 4
        }
    )

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
