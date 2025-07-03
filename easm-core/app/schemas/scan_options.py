from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class SeverityEnum(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"
    
class NucleiTemplateEnum(str, Enum):
    """Enum representing available Nuclei template categories"""
    cves = "cves"  # Common Vulnerabilities and Exposures templates
    dns = "dns"  # DNS-related vulnerability templates
    file = "file"  # File-related vulnerability templates
    headless = "headless"  # Templates requiring browser interaction
    http = "http"  # HTTP-related vulnerability templates
    network = "network"  # Network-related vulnerability templates
    ssl = "ssl"  # SSL/TLS vulnerability templates
    workflows = "workflows"  # Complex multi-step vulnerability checks

class NmapScanOptions(BaseModel):
    """Options specific to nmap scanner"""
    ports: Optional[str] = Field(
        default="1-1000", 
        description="Port range to scan (e.g. '1-1000', '22,80,443')"
    )
    scan_type: Optional[str] = Field(
        default="SYN", 
        description="Scan type (SYN, TCP, UDP, etc.)"
    )
    timing: Optional[int] = Field(
        default=4, 
        ge=0, le=5, 
        description="Timing template (0-5, higher is faster)"
    )
    os_detection: Optional[bool] = Field(
        default=False, 
        description="Enable OS detection"
    )
    service_detection: Optional[bool] = Field(
        default=True, 
        description="Enable service version detection"
    )
    script_scan: Optional[bool] = Field(
        default=False, 
        description="Enable default script scan"
    )
    timeout: Optional[int] = Field(
        default=300, 
        description="Scan timeout in seconds"
    )

class MasscanOptions(BaseModel):
    """Options specific to masscan scanner"""
    ports: Optional[str] = Field(
        default="1-10000", 
        description="Port range to scan (e.g. '1-10000', '22,80,443')"
    )
    rate: Optional[int] = Field(
        default=1000, 
        description="Packets per second to send"
    )
    timeout: Optional[int] = Field(
        default=120, 
        description="Scan timeout in seconds"
    )

class NucleiOptions(BaseModel):
    """Options specific to nuclei scanner"""
    templates: Optional[List[NucleiTemplateEnum]] = Field(
        default=["cves"], 
        description="Template directories to use for scanning. See /api/v1/scan/nuclei/templates for available options."
    )
    severity: Optional[List[SeverityEnum]] = Field(
        default=["critical", "high", "medium"], 
        description="Severity levels to include. See /api/v1/scan/nuclei/severity-levels for details."
    )
    timeout: Optional[int] = Field(
        default=600, 
        description="Scan timeout in seconds. Increase for larger scans."
    )
    rate: Optional[int] = Field(
        default=150, 
        description="Rate limiting in requests per second. Lower to avoid overwhelming the target."
    )
    concurrency: Optional[int] = Field(
        default=25, 
        description="Number of concurrent requests. Lower for sensitive targets."
    )
    exclude_templates: Optional[List[str]] = Field(
        default=None, 
        description="Templates to exclude (e.g. 'cves/2020/...'). Format: 'directory/subdirectory/template-id'"
    )
    retries: Optional[int] = Field(
        default=1,
        description="Number of times to retry a failed request"
    )
    verbose: Optional[bool] = Field(
        default=False,
        description="Enable verbose output for more detailed results"
    )
    follow_redirects: Optional[bool] = Field(
        default=True,
        description="Follow HTTP redirects during scanning"
    )
    max_host_error: Optional[int] = Field(
        default=30,
        description="Maximum number of errors allowed for a host before skipping"
    )
