from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.sql import func

from app.models.base import Base

class Scan(Base):
    """Scan model for tracking scan requests and results"""
    __tablename__ = "scans"
    
    id = Column(String, primary_key=True)
    target = Column(String, nullable=False, index=True)
    scanner = Column(String, nullable=False)
    status = Column(String, default="queued")  # queued, running, completed, failed
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    options = Column(JSON)
    results = Column(JSON)
    error_message = Column(Text)
