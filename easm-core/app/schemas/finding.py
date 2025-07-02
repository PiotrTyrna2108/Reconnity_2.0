from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, str
from datetime import datetime

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
