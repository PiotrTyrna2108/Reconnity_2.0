import os
from arq import create_pool
from arq.connections import RedisSettings
from typing import Dict, Any
from ..core.logging import get_logger
from .metrics import create_metrics_middleware

logger = get_logger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

def parse_redis_url(url: str) -> Dict[str, Any]:
    """Parse Redis URL into components for ARQ RedisSettings"""
    if url.startswith("redis://"):
        url = url[len("redis://"):]
    
    host_port, *rest = url.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 6379
        
    db = int(rest[0]) if rest else 0
    
    return {
        "host": host,
        "port": port,
        "database": db
    }

redis_settings = RedisSettings(**parse_redis_url(REDIS_URL))

async def get_redis_pool():
    """Get a Redis connection pool for ARQ"""
    return await create_pool(redis_settings)

class WorkerSettings:
    """ARQ worker settings for easm-core service"""
    redis_settings = redis_settings
    queue_name = "core"
    
    # Import here to avoid circular imports
    from .scan_tasks import scan_asset, report_scan_result, report_scan_failure
    
    functions = [
        ("scan_asset", scan_asset),
        ("report_scan_result", report_scan_result),
        ("report_scan_failure", report_scan_failure)
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
