import os
from arq import create_pool
from typing import Dict, Any
from ..core.logging import get_logger
from .metrics import create_metrics_middleware
from .redis_config import redis_settings

logger = get_logger(__name__)

async def get_redis_pool():
    """Get a Redis connection pool for ARQ"""
    return await create_pool(redis_settings)

class WorkerSettings:
    """ARQ worker settings for easm-core service"""
    redis_settings = redis_settings
    queue_name = "core"
    
    # Import from package level to avoid circular imports
    from . import scan_asset, report_scan_completion, report_scan_failure
    
    functions = [
        scan_asset,
        report_scan_completion, 
        report_scan_failure
    ]
    
    # Add metrics middleware
    middlewares = [create_metrics_middleware(queue_name)]
    
    async def startup(ctx):
        """Worker startup initialization"""
        logger.info(f"ARQ Worker starting with queue: {WorkerSettings.queue_name}")
        ctx["redis"] = await get_redis_pool()
        
    async def shutdown(ctx):
        """Worker shutdown cleanup"""
        logger.info("ARQ Worker shutting down")
