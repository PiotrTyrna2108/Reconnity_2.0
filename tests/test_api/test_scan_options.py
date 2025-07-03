import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.scan import ScannerType

client = TestClient(app)

def test_get_all_scanner_options():
    """Test that we can get options for all scanners"""
    response = client.get("/api/v1/scan/options")
    
    assert response.status_code == 200
    
    options = response.json()
    assert isinstance(options, list)
    
    # Check that we have options for all scanner types
    scanner_types = [option["scanner"] for option in options]
    assert ScannerType.NMAP.value in scanner_types
    assert ScannerType.MASSCAN.value in scanner_types
    assert ScannerType.NUCLEI.value in scanner_types
    
    # Check that options have the expected structure
    for option in options:
        assert "scanner" in option
        assert "description" in option
        assert "options" in option
        assert isinstance(option["options"], dict)

def test_get_specific_scanner_options():
    """Test that we can get options for a specific scanner"""
    for scanner_type in [ScannerType.NMAP.value, ScannerType.MASSCAN.value, ScannerType.NUCLEI.value]:
        response = client.get(f"/api/v1/scan/options/{scanner_type}")
        
        assert response.status_code == 200
        
        option = response.json()
        assert option["scanner"] == scanner_type
        assert "description" in option
        assert "options" in option
        assert isinstance(option["options"], dict)
        
        if scanner_type == ScannerType.NUCLEI.value:
            # Check that Nuclei options include our new options
            assert "templates" in option["options"]
            assert "severity" in option["options"]
            assert "timeout" in option["options"]
            assert "rate" in option["options"]
            assert "retries" in option["options"]
            assert "follow_redirects" in option["options"]

def test_invalid_scanner_type():
    """Test that we get a 404 for an invalid scanner type"""
    response = client.get("/api/v1/scan/options/invalid")
    
    assert response.status_code == 422  # Validation error due to enum

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
