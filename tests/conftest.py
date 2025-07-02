import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'easm-core'))

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
    os.environ.setdefault("CELERY_BROKER_URL", "memory://")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")

@pytest.fixture
def mock_scan_results():
    """Mock scan results for testing"""
    return {
        "scanner": "nmap",
        "target": "192.168.1.1",
        "scan_duration": 5.2,
        "timestamp": 1656747600.0,
        "open_ports": [22, 80, 443],
        "services": {
            "22": {"name": "ssh", "product": "OpenSSH", "version": "8.9"},
            "80": {"name": "http", "product": "Apache", "version": "2.4"},
            "443": {"name": "https", "product": "Apache", "version": "2.4"}
        },
        "os_info": {
            "name": "Linux 5.4",
            "accuracy": "85"
        }
    }
