import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "easm-core"
    assert "timestamp" in data

@patch('app.main.celery_app.send_task')
def test_create_scan_success(mock_send_task):
    """Test successful scan creation"""
    mock_send_task.return_value = None
    
    scan_data = {
        "target": "192.168.1.1",
        "scanner": "nmap",
        "options": {"ports": "80,443"}
    }
    
    response = client.post("/internal/scan", json=scan_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "scan_id" in data
    assert data["status"] == "queued"
    assert "192.168.1.1" in data["message"]
    
    # Verify Celery task was called
    mock_send_task.assert_called_once()

def test_create_scan_invalid_target():
    """Test scan creation with invalid target"""
    scan_data = {
        "target": "invalid-target!@#",
        "scanner": "nmap"
    }
    
    response = client.post("/internal/scan", json=scan_data)
    assert response.status_code == 422  # Validation error

def test_create_scan_unsupported_scanner():
    """Test scan creation with unsupported scanner"""
    scan_data = {
        "target": "192.168.1.1",
        "scanner": "unsupported_scanner"
    }
    
    response = client.post("/internal/scan", json=scan_data)
    assert response.status_code == 422  # Validation error

def test_get_scan_status_not_found():
    """Test getting status of non-existent scan"""
    response = client.get("/internal/scan/non-existent-id")
    assert response.status_code == 404
    
    data = response.json()
    assert "not found" in data["detail"].lower()
