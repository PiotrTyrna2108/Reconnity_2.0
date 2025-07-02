from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Boolean
from sqlalchemy.sql import func

from app.models.base import Base

class Finding(Base):
    """Finding model for storing scan findings"""
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True)
    scan_id = Column(String, nullable=False, index=True)
    target = Column(String, nullable=False, index=True)
    finding_type = Column(String, nullable=False)  # open_port, service, vulnerability, etc.
    severity = Column(String, default="info")  # critical, high, medium, low, info
    title = Column(String, nullable=False)
    description = Column(Text)
    port = Column(Integer)
    service = Column(String)
    created_at = Column(DateTime, default=func.now())
    verified = Column(Boolean, default=False)
    finding_metadata = Column(JSON)

class RiskScore(Base):
    """Risk scoring model for assets"""
    __tablename__ = "risk_scores"
    
    id = Column(String, primary_key=True)
    target = Column(String, nullable=False, index=True)
    score = Column(Integer, nullable=False)  # 0-100
    factors = Column(JSON)  # JSON object with risk factors
    calculated_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
