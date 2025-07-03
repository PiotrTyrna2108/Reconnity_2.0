# filepath: /Users/piotrtyrna/Desktop/Reconnity/easm-microservices/easm-api/app/main.py
from fastapi import FastAPI, HTTPException, status, Request, Response
import httpx
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_PREFIX = "/api/v1"
CORE_URL = os.getenv("CORE_URL", "http://core:8001")

app = FastAPI(
    title="EASM API Gateway",
    description="External Attack Surface Management API Gateway",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "easm-api"}

@app.api_route(f"{API_PREFIX}/{{path:path}}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_endpoint(path: str, request: Request):
    """
    Universal proxy endpoint that forwards all requests to core API
    
    This endpoint acts as a simple proxy, passing all requests to the core API
    and returning the responses. It preserves headers, query parameters, and 
    request bodies.
    """
    try:
        # Get request body if it exists
        body = await request.body() if request.method in ["POST", "PUT"] else None
        
        # Get query parameters
        params = dict(request.query_params)
        
        # Log request details
        logger.info(
            f"Proxying {request.method} request to {path}",
            extra={"target": path, "method": request.method}
        )
        
        # Forward request to core API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=f"{CORE_URL}/api/v1/{path}",
                params=params,
                headers={k: v for k, v in request.headers.items() 
                         if k.lower() not in ["host", "content-length"]},
                content=body
            )
            
            # Handle HTTP errors
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Pass error code and details from core API
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "detail" in error_json:
                        error_detail = error_json["detail"]
                except:
                    pass
                
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
            
            # Return response from core API
            content_type = response.headers.get("content-type", "application/json")
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type
            )
            
    except httpx.TimeoutException:
        logger.error(f"Timeout while communicating with core service: {path}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Core service timeout"
        )
    except HTTPException:
        # Pass through HTTPException (already properly formatted)
        raise
    except Exception as e:
        logger.error(f"Proxy error for {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
