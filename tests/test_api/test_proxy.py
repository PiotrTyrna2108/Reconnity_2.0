import pytest
from fastapi.testclient import TestClient
import httpx
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

class MockResponse:
    def __init__(self, status_code, json_data, content=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.content = content or str(json_data).encode()
        self.headers = headers or {"content-type": "application/json"}
        
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "Error response", request=None, response=self
            )

@pytest.mark.asyncio
@patch("httpx.AsyncClient.request")
async def test_proxy_get_request(mock_request):
    """Test that GET requests are correctly proxied to core API"""
    # Mock the response from core API
    mock_response = MockResponse(200, {"key": "value"})
    mock_request.return_value = mock_response
    
    # Make request to proxy
    response = client.get("/api/v1/scan/options")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == {"key": "value"}
    
    # Verify that request was forwarded correctly
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert kwargs["url"] == "http://core:8001/api/v1/scan/options"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.request")
async def test_proxy_post_request(mock_request):
    """Test that POST requests are correctly proxied to core API"""
    # Mock the response from core API
    mock_response = MockResponse(201, {"scan_id": "12345"})
    mock_request.return_value = mock_response
    
    # Make request to proxy
    response = client.post("/api/v1/scan", json={"target": "example.com"})
    
    # Verify response
    assert response.status_code == 201
    assert response.json() == {"scan_id": "12345"}
    
    # Verify that request was forwarded correctly
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert kwargs["url"] == "http://core:8001/api/v1/scan"
    assert "content" in kwargs  # Body should be forwarded

@pytest.mark.asyncio
@patch("httpx.AsyncClient.request")
async def test_proxy_error_handling(mock_request):
    """Test that errors from core API are correctly handled"""
    # Mock an error response from core API
    error_response = MockResponse(404, {"detail": "Resource not found"})
    mock_request.return_value = error_response
    
    # Make request to proxy
    response = client.get("/api/v1/scan/nonexistent")
    
    # Verify that error is passed through
    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found"}

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
