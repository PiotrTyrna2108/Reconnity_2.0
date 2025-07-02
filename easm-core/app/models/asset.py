from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from datetime import datetime

from app.models.base import Base

class Asset(Base):
    """Asset model for storing discovered assets"""
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)
    target = Column(String, nullable=False, index=True)
    asset_type = Column(String, nullable=False)  # ip, domain, url, etc.
    status = Column(String, default="active")  # active, inactive, unknown
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    asset_metadata = Column(JSON)
