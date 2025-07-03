import os
import asyncio
from arq import create_pool
from typing import Dict, Any
from ...core.logging import get_logger
from ..monitoring.task_metrics import create_metrics_middleware, monitor_queue_metrics
from .redis_config import redis_settings

logger = get_logger(__name__)

async def get_redis_pool():
    """Get a Redis connection pool for ARQ"""
    return await create_pool(redis_settings)

class WorkerSettings:
    """ARQ worker settings for easm-core service"""
    redis_settings = redis_settings
    queue_name = "core"
    
    # Import functions directly to avoid circular imports
    from .scan_tasks import scan_asset, process_scan_result
    
    functions = [
        scan_asset,
        process_scan_result
    ]
    
    # Add metrics middleware
    try:
        middlewares = [create_metrics_middleware(queue_name)]
    except Exception as e:
        logger.warning(f"Failed to initialize metrics middleware: {e}")
        middlewares = []
    
    async def startup(ctx):
        """Worker startup initialization"""
        logger.info(f"ARQ Worker starting with queue: {WorkerSettings.queue_name}")
        ctx["redis"] = await get_redis_pool()
        
        # Start queue metrics monitoring task if this is the core worker
        if WorkerSettings.queue_name == "core":
            # Start queue metrics monitoring in background
            ctx['metrics_task'] = asyncio.create_task(
                monitor_queue_metrics(ctx["redis"])
            )
            logger.info("Queue metrics monitoring started")
        
    async def shutdown(ctx):
        """Worker shutdown cleanup"""
        logger.info("ARQ Worker shutting down")
        
        # Cancel metrics monitoring task if it exists
        if 'metrics_task' in ctx:
            ctx['metrics_task'].cancel()
            try:
                await ctx['metrics_task']
            except asyncio.CancelledError:
                pass
            logger.info("Queue metrics monitoring stopped")
