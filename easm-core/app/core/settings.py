from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "EASM Core Service"
    version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://easm:easm@db:5432/easm")
    
    # Redis (for ARQ)
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Services
    core_url: str = os.getenv("CORE_URL", "http://core:8001")
    api_url: str = os.getenv("API_URL", "http://api:8000")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-change-in-production")
    
    # Monitoring
    prometheus_url: str = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Scanner Configuration
    nmap_timeout: int = int(os.getenv("NMAP_TIMEOUT", "300"))
    scan_queue_ttl: int = int(os.getenv("SCAN_QUEUE_TTL", "3600"))
    
    # Risk Engine
    risk_score_ttl: int = int(os.getenv("RISK_SCORE_TTL", "86400"))
    
    class Config:
        env_file = ".env"

settings = Settings()
