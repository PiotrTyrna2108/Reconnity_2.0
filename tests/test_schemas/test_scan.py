import pytest
from app.schemas.scan import ScanRequest, ScanResponse, Finding, RiskScore
from pydantic import ValidationError

def test_scan_request_valid_ip():
    """Test scan request with valid IP address"""
    request = ScanRequest(
        target="192.168.1.1",
        scanner="nmap",
        options={"ports": "80,443"}
    )
    assert request.target == "192.168.1.1"
    assert request.scanner == "nmap"
    assert request.options["ports"] == "80,443"

def test_scan_request_valid_domain():
    """Test scan request with valid domain"""
    request = ScanRequest(
        target="example.com",
        scanner="nmap"
    )
    assert request.target == "example.com"

def test_scan_request_valid_cidr():
    """Test scan request with valid CIDR"""
    request = ScanRequest(
        target="192.168.1.0/24",
        scanner="nmap"
    )
    assert request.target == "192.168.1.0/24"

def test_scan_request_invalid_target():
    """Test scan request with invalid target"""
    with pytest.raises(ValidationError) as exc_info:
        ScanRequest(
            target="invalid-target!@#$",
            scanner="nmap"
        )
    
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert "target" in str(errors[0])

def test_scan_request_invalid_scanner():
    """Test scan request with invalid scanner"""
    with pytest.raises(ValidationError) as exc_info:
        ScanRequest(
            target="192.168.1.1",
            scanner="invalid_scanner"
        )
    
    errors = exc_info.value.errors()
    assert any("scanner" in str(error) for error in errors)

def test_finding_model():
    """Test Finding model validation"""
    finding = Finding(
        id="test-id",
        scan_id="scan-123",
        target="192.168.1.1",
        finding_type="open_port",
        severity="high",
        title="Open port 22",
        port=22,
        service="ssh",
        created_at="2025-07-02T10:00:00Z"
    )
    
    assert finding.port == 22
    assert finding.severity == "high"
    assert finding.finding_type == "open_port"

def test_finding_invalid_port():
    """Test Finding with invalid port number"""
    with pytest.raises(ValidationError):
        Finding(
            id="test-id",
            scan_id="scan-123",
            target="192.168.1.1",
            finding_type="open_port",
            severity="high",
            title="Invalid port",
            port=99999,  # Invalid port number
            created_at="2025-07-02T10:00:00Z"
        )

def test_risk_score_model():
    """Test RiskScore model"""
    risk_score = RiskScore(
        score=85,
        level="high",
        factors={
            "open_ports": 30.0,
            "services": 25.0,
            "vulnerabilities": 30.0
        },
        calculated_at="2025-07-02T10:00:00Z"
    )
    
    assert risk_score.score == 85
    assert risk_score.level == "high"
    assert len(risk_score.factors) == 3
