import pytest
from fastapi.testclient import TestClient
import json
from unittest import mock

from app.main import app
from app.schemas.scan_options import NucleiTemplateEnum, SeverityEnum
from app.api.routers.nuclei_templates import TEMPLATE_INFO

client = TestClient(app)

def test_list_nuclei_templates():
    """Test that the nuclei templates endpoint returns the expected templates"""
    response = client.get("/api/v1/scan/nuclei/templates")
    
    assert response.status_code == 200
    
    templates = response.json()
    assert isinstance(templates, list)
    assert len(templates) == len(TEMPLATE_INFO)
    
    # Verify that template data matches what's defined in the API
    for template in templates:
        assert "id" in template
        assert "name" in template
        assert "description" in template
        assert "count" in template
        
        # Make sure the template is in our Enum
        assert template["id"] in [t.value for t in NucleiTemplateEnum]
        
        # Verify count is a non-negative number
        assert isinstance(template["count"], int)
        assert template["count"] >= 0

def test_list_nuclei_severity_levels():
    """Test that the nuclei severity levels endpoint returns the expected levels"""
    response = client.get("/api/v1/scan/nuclei/severity-levels")
    
    assert response.status_code == 200
    
    levels = response.json()
    assert isinstance(levels, list)
    assert len(levels) == 5  # critical, high, medium, low, info
    
    # Verify that each severity level is in our Enum
    for level in levels:
        assert "id" in level
        assert "name" in level
        assert "description" in level
        assert level["id"] in [s.value for s in SeverityEnum]

@mock.patch("app.services.scan_service.ScanService.create_scan")
@mock.patch("app.api.routers.scan.celery_app.send_task")
def test_create_nuclei_scan(mock_send_task, mock_create_scan):
    """Test that the nuclei scan endpoint correctly handles requests"""
    # Setup mock to return a successful scan response
    scan_id = "test-scan-id"
    mock_create_scan.return_value = {
        "scan_id": scan_id,
        "status": "queued",
        "message": "Scan queued"
    }
    
    # Test with minimal options
    request_data = {
        "target": "example.com",
        "scanner": "nuclei"
    }
    
    response = client.post("/api/v1/scan/nuclei", json=request_data)
    
    assert response.status_code == 200
    assert response.json()["scan_id"] == scan_id
    
    # Verify that the task was queued
    mock_send_task.assert_called_once()
    
    # Test with all options
    request_data = {
        "target": "example.com",
        "scanner": "nuclei",
        "options": {
            "templates": ["cves", "http"],
            "severity": ["critical", "high"],
            "timeout": 300,
            "rate": 100,
            "concurrency": 20,
            "exclude_templates": ["cves/2020/CVE-2020-1234"],
            "retries": 2,
            "verbose": True,
            "follow_redirects": True,
            "max_host_error": 15
        }
    }
    
    # Reset mocks
    mock_send_task.reset_mock()
    
    response = client.post("/api/v1/scan/nuclei", json=request_data)
    
    assert response.status_code == 200
    
    # Verify that the options were correctly processed
    mock_create_scan.assert_called_with(
        target="example.com",
        scanner="nuclei",
        options={
            "templates": "cves,http",
            "severity": "critical,high",
            "timeout": 300,
            "rate": 100,
            "concurrency": 20,
            "exclude_templates": ["cves/2020/CVE-2020-1234"],
            "retries": 2,
            "verbose": True,
            "follow_redirects": True,
            "max_host_error": 15
        }
    )
    
    # Verify that the task was queued
    mock_send_task.assert_called_once()

@mock.patch("app.services.scan_service.ScanService.create_scan")
def test_nuclei_scan_invalid_options(mock_create_scan):
    """Test that the nuclei scan endpoint correctly validates options"""
    # Invalid template
    request_data = {
        "target": "example.com",
        "scanner": "nuclei",
        "options": {
            "templates": ["invalid_template_name"],
        }
    }
    
    response = client.post("/api/v1/scan/nuclei", json=request_data)
    
    # Should fail validation
    assert response.status_code == 422
    
    # Invalid severity
    request_data = {
        "target": "example.com",
        "scanner": "nuclei",
        "options": {
            "severity": ["invalid_severity_name"],
        }
    }
    
    response = client.post("/api/v1/scan/nuclei", json=request_data)
    
    # Should fail validation
    assert response.status_code == 422

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
