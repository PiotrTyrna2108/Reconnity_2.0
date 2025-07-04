from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import ipaddress
import re

class AssetBase(BaseModel):
    """Base schema for asset data with comprehensive target validation"""
    target: str = Field(
        ..., 
        description="Target to scan - supports multiple formats",
        example="scanme.nmap.org",
        examples=[
            "192.168.1.1",           # Single IP address
            "192.168.1.0/24",        # CIDR network range
            "scanme.nmap.org",       # Domain name
            "example.com",           # Website domain
            "https://httpbin.org",   # Full URL (for web scanners)
        ]
    )
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target format"""
        v = v.strip()
        
        # Check if it's an IP address
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        
        # Check if it's a CIDR
        try:
            ipaddress.ip_network(v, strict=False)
            return v
        except ValueError:
            pass
        
        # Check if it's a domain name
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(domain_pattern, v):
            return v
        
        raise ValueError('Invalid target format. Must be IP, CIDR, or domain name')
