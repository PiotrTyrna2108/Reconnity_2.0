from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel

from app.schemas.scan_options import NucleiTemplateEnum, SeverityEnum
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

class TemplateInfo(BaseModel):
    """Information about a nuclei template category"""
    id: str
    name: str
    description: str
    count: int = 0  # Estimated count of templates in this category

# Template information with descriptions
TEMPLATE_INFO = {
    "cves": {
        "name": "CVEs",
        "description": "Common Vulnerabilities and Exposures templates",
        "count": 5000  # Approximate count
    },
    "dns": {
        "name": "DNS",
        "description": "DNS-related vulnerability templates",
        "count": 100
    },
    "file": {
        "name": "File",
        "description": "File-related vulnerability templates",
        "count": 150
    },
    "headless": {
        "name": "Headless",
        "description": "Templates requiring browser interaction",
        "count": 200
    },
    "http": {
        "name": "HTTP",
        "description": "HTTP-related vulnerability templates",
        "count": 800
    },
    "network": {
        "name": "Network",
        "description": "Network-related vulnerability templates",
        "count": 250
    },
    "ssl": {
        "name": "SSL",
        "description": "SSL/TLS vulnerability templates",
        "count": 120
    },
    "workflows": {
        "name": "Workflows",
        "description": "Complex multi-step vulnerability checks",
        "count": 50
    }
}

@router.get("/scan/nuclei/templates", response_model=List[TemplateInfo],
            summary="List Nuclei Templates",
            description="Returns a list of available Nuclei template categories with descriptions")
async def list_nuclei_templates():
    """
    Get a list of available Nuclei template categories
    
    Returns information about each template category including:
    - id: Template category ID
    - name: Human-readable name
    - description: Brief description of what this template category covers
    - count: Approximate number of templates in this category
    """
    try:
        templates = []
        for template_id, info in TEMPLATE_INFO.items():
            templates.append(TemplateInfo(
                id=template_id,
                name=info["name"],
                description=info["description"],
                count=info["count"]
            ))
        
        return templates
    except Exception as e:
        logger.error(f"Failed to list Nuclei templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list Nuclei templates"
        )

@router.get("/scan/nuclei/severity-levels", response_model=List[Dict[str, str]],
            summary="List Nuclei Severity Levels",
            description="Returns a list of supported severity levels for Nuclei templates")
async def list_nuclei_severity_levels():
    """
    Get a list of supported severity levels for Nuclei templates
    
    Returns information about each severity level including:
    - id: Severity level ID
    - name: Human-readable name
    - description: Brief description of this severity level
    """
    try:
        return [
            {
                "id": "critical",
                "name": "Critical",
                "description": "Severe vulnerabilities that require immediate attention"
            },
            {
                "id": "high",
                "name": "High",
                "description": "Important vulnerabilities that should be addressed soon"
            },
            {
                "id": "medium",
                "name": "Medium",
                "description": "Moderate risk vulnerabilities"
            },
            {
                "id": "low",
                "name": "Low",
                "description": "Low risk vulnerabilities"
            },
            {
                "id": "info",
                "name": "Info",
                "description": "Informational findings that don't pose a security risk"
            }
        ]
    except Exception as e:
        logger.error(f"Failed to list Nuclei severity levels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list Nuclei severity levels"
        )
