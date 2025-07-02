from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str
    service: str
    version: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
