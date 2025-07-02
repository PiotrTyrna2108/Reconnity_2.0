import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.scan_service import ScanService
from app.api.errors import ScanNotFoundException

@pytest.fixture
def scan_service():
    """Fixture providing scan service instance"""
    return ScanService()

@pytest.mark.asyncio
async def test_create_scan_success(scan_service):
    """Test successful scan creation"""
    result = await scan_service.create_scan(
        target="192.168.1.1",
        scanner="nmap",
        options={"ports": "80,443"}
    )
    
    assert "scan_id" in result
    assert result["status"] == "queued"
    assert "192.168.1.1" in result["message"]

@pytest.mark.asyncio
async def test_get_scan_status_not_found(scan_service):
    """Test getting status of non-existent scan"""
    result = await scan_service.get_scan_status("non-existent-id")
    assert result is None

@pytest.mark.asyncio
async def test_complete_scan_success(scan_service):
    """Test successful scan completion"""
    # Create scan first
    create_result = await scan_service.create_scan("192.168.1.1", "nmap")
    scan_id = create_result["scan_id"]
    
    # Complete the scan
    results = {
        "open_ports": [22, 80, 443],
        "services": {"80": {"name": "http"}}
    }
    
    success = await scan_service.complete_scan(scan_id, results)
    assert success is True
    
    # Check scan status
    status = await scan_service.get_scan_status(scan_id)
    assert status["status"] == "completed"
    assert status["results"] == results
    assert "findings" in status
    assert "risk_score" in status

@pytest.mark.asyncio
async def test_fail_scan_success(scan_service):
    """Test scan failure handling"""
    # Create scan first
    create_result = await scan_service.create_scan("192.168.1.1", "nmap")
    scan_id = create_result["scan_id"]
    
    # Fail the scan
    error_msg = "Network timeout"
    success = await scan_service.fail_scan(scan_id, error_msg)
    assert success is True
    
    # Check scan status
    status = await scan_service.get_scan_status(scan_id)
    assert status["status"] == "failed"
    assert status["error"] == error_msg

def test_classify_port_severity(scan_service):
    """Test port severity classification"""
    # High risk ports
    assert scan_service._classify_port_severity(22) == "medium"  # SSH
    assert scan_service._classify_port_severity(3389) == "high"  # RDP
    assert scan_service._classify_port_severity(1433) == "high"  # SQL Server
    
    # Low risk ports
    assert scan_service._classify_port_severity(8080) == "low"

def test_classify_service_severity(scan_service):
    """Test service severity classification"""
    assert scan_service._classify_service_severity("telnet") == "critical"
    assert scan_service._classify_service_severity("mysql") == "high"
    assert scan_service._classify_service_severity("ssh") == "medium"
    assert scan_service._classify_service_severity("unknown") == "low"
