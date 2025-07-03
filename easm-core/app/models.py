# =====================================================================
# DEPRECATED: Ten plik jest przestarzały i nie powinien być używany.
# Wszystkie modele są teraz zdefiniowane w katalogu app/models/
# Używaj importów z app.models zamiast z tego pliku.
# Pozostawiono jako odniesienie do poprzedniej wersji systemu.
# =====================================================================

from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

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
