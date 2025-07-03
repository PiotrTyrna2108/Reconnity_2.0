"""
Retry mechanism for Redis operations
Provides decorators and utilities for adding retry logic to Redis operations
"""

import asyncio
import functools
import logging
from typing import Callable, Any, TypeVar, cast, Optional
import redis.exceptions

from ...core.logging import get_logger
from ..monitoring.task_metrics import ARQ_COMMUNICATION_ERRORS, ARQ_RETRY_COUNT

logger = get_logger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

def with_redis_retry(
    max_retries: int = 3,
    retry_delay: float = 0.5,
    backoff_factor: float = 2.0,
    queue_name: str = "unknown",
    operation_name: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorator for adding retry logic to async Redis operations
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay between retries
        queue_name: Name of the queue for metrics
        operation_name: Name of the operation for logging and metrics
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            retries = 0
            current_delay = retry_delay
            
            while True:
                try:
                    return await func(*args, **kwargs)
                    
                except (redis.exceptions.RedisError, ConnectionError, OSError) as e:
                    retries += 1
                    # Record error in metrics
                    ARQ_COMMUNICATION_ERRORS.labels(queue=queue_name, operation=op_name).inc()
                    
                    if retries > max_retries:
                        logger.error(f"Redis operation '{op_name}' failed after {max_retries} retries: {e}")
                        raise
                        
                    # Record retry attempt in metrics
                    ARQ_RETRY_COUNT.labels(queue=queue_name, operation=op_name).inc()
                    
                    logger.warning(
                        f"Redis operation '{op_name}' failed (attempt {retries}/{max_retries}): {e}. "
                        f"Retrying in {current_delay:.2f}s"
                    )
                    
                    # Wait before retrying with exponential backoff
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
        
        return cast(F, wrapper)
    return decorator


class RedisRetryClient:
    """
    Wrapper for Redis client with retry logic
    Provides common Redis operations with built-in retry mechanism
    """
    
    def __init__(
        self, 
        redis_client, 
        queue_name: str = "unknown",
        max_retries: int = 3, 
        retry_delay: float = 0.5,
        backoff_factor: float = 2.0
    ):
        self.redis = redis_client
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
    
    @with_redis_retry(operation_name="enqueue_job")
    async def enqueue_job(self, function_name: str, *args: Any, **kwargs: Any) -> str:
        """Enqueue a job with retry mechanism"""
        return await self.redis.enqueue_job(function_name, *args, **kwargs)
    
    @with_redis_retry(operation_name="get_job_result")
    async def get_job_result(self, job_id: str) -> Any:
        """Get job result with retry mechanism"""
        return await self.redis.get_job_result(job_id)
