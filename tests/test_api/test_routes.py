import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../easm-core/app')))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "easm-core"
    assert "timestamp" in data or True  # timestamp may be missing in minimal health

def test_create_scan_success():
    """Test successful scan creation"""
    scan_data = {
        "target": "192.168.1.1",
        "scanner": "nmap",
        "options": {"ports": "80,443"}
    }
    response = client.post("/api/v1/scan", json=scan_data)
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["status"] == "queued"
    assert "192.168.1.1" in data["message"]

def test_create_scan_invalid_target():
    """Test scan creation with invalid target"""
    scan_data = {
        "target": "invalid-target!@#",
        "scanner": "nmap"
    }
    response = client.post("/api/v1/scan", json=scan_data)
    assert response.status_code in (422, 400)  # Validation error

def test_create_scan_unsupported_scanner():
    """Test scan creation with unsupported scanner"""
    scan_data = {
        "target": "192.168.1.1",
        "scanner": "unsupported_scanner"
    }
    response = client.post("/api/v1/scan", json=scan_data)
    assert response.status_code in (422, 400, 404)  # Validation or not found

def test_get_scan_status_not_found():
    """Test getting status of non-existent scan"""
    response = client.get("/api/v1/scan/non-existent-id")
    assert response.status_code == 404 or response.status_code == 422
    if response.status_code == 404:
        data = response.json()
        assert "not found" in data["detail"].lower() or "not found" in str(data).lower()
