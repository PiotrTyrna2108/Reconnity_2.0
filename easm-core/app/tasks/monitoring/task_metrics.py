import time
import logging
import asyncio
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Define ARQ task metrics
ARQ_TASK_RECEIVED = Counter(
    'arq_task_received_total',
    'Number of ARQ tasks received',
    ['queue', 'task_name']
)

ARQ_TASK_STARTED = Counter(
    'arq_task_started_total',
    'Number of ARQ tasks started',
    ['queue', 'task_name']
)

ARQ_TASK_COMPLETED = Counter(
    'arq_task_completed_total',
    'Number of ARQ tasks completed successfully',
    ['queue', 'task_name']
)

ARQ_TASK_FAILED = Counter(
    'arq_task_failed_total',
    'Number of ARQ tasks that failed',
    ['queue', 'task_name']
)

ARQ_TASK_DURATION = Histogram(
    'arq_task_duration_seconds',
    'Time taken to execute ARQ tasks',
    ['queue', 'task_name'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float('inf'))
)

# Queue monitoring metrics
ARQ_QUEUE_SIZE = Gauge(
    'arq_queue_size',
    'Current number of tasks in the ARQ queue',
    ['queue']
)

ARQ_QUEUE_LATENCY = Gauge(
    'arq_queue_latency_seconds',
    'Time between oldest job enqueued and now',
    ['queue']
)

ARQ_WORKER_COUNT = Gauge(
    'arq_worker_count',
    'Number of active ARQ workers',
    ['queue']
)

# Communication monitoring
ARQ_COMMUNICATION_ERRORS = Counter(
    'arq_communication_errors_total',
    'Number of Redis communication errors',
    ['queue', 'operation']
)

ARQ_RETRY_COUNT = Counter(
    'arq_retry_count_total',
    'Number of retry attempts for Redis operations',
    ['queue', 'operation']
)

class TaskMetrics:
    """Metrics collector for ARQ tasks"""
    
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.task_timers: Dict[str, float] = {}
    
    def task_received(self, task_name: str) -> None:
        """Record task received"""
        ARQ_TASK_RECEIVED.labels(queue=self.queue_name, task_name=task_name).inc()
    
    def task_started(self, task_name: str, job_id: str) -> None:
        """Record task started"""
        ARQ_TASK_STARTED.labels(queue=self.queue_name, task_name=task_name).inc()
        self.task_timers[job_id] = time.time()
    
    def task_completed(self, task_name: str, job_id: str) -> None:
        """Record task completed"""
        ARQ_TASK_COMPLETED.labels(queue=self.queue_name, task_name=task_name).inc()
        
        if job_id in self.task_timers:
            duration = time.time() - self.task_timers[job_id]
            ARQ_TASK_DURATION.labels(queue=self.queue_name, task_name=task_name).observe(duration)
            del self.task_timers[job_id]
    
    def task_failed(self, task_name: str, job_id: str) -> None:
        """Record task failed"""
        ARQ_TASK_FAILED.labels(queue=self.queue_name, task_name=task_name).inc()
        
        if job_id in self.task_timers:
            duration = time.time() - self.task_timers[job_id]
            ARQ_TASK_DURATION.labels(queue=self.queue_name, task_name=task_name).observe(duration)
            del self.task_timers[job_id]
    
    def record_communication_error(self, operation: str) -> None:
        """Record Redis communication error"""
        ARQ_COMMUNICATION_ERRORS.labels(queue=self.queue_name, operation=operation).inc()
    
    def record_retry_attempt(self, operation: str) -> None:
        """Record Redis retry attempt"""
        ARQ_RETRY_COUNT.labels(queue=self.queue_name, operation=operation).inc()

def create_metrics_middleware(queue_name: str):
    """Create ARQ middleware for metrics collection"""
    metrics = TaskMetrics(queue_name)
    
    async def metrics_middleware(ctx: Dict[str, Any], job: Dict[str, Any], job_name: str,
                            job_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ARQ middleware for collecting metrics"""
        job_id = job.get('job_id', 'unknown')
        metrics.task_received(job_name)
        metrics.task_started(job_name, job_id)
        
        # Store job_id and job_name in context for use in post-processing
        ctx['job_id'] = job_id
        ctx['job_name'] = job_name
        
        try:
            result = await job['coro']
            metrics.task_completed(job_name, job_id)
            return result
        except Exception as e:
            metrics.task_failed(job_name, job_id)
            raise
    
    return metrics_middleware

async def monitor_queue_metrics(redis, queue_names=None):
    """Background task to monitor ARQ queue metrics"""
    if queue_names is None:
        queue_names = ['core', 'scanner-nmap', 'scanner-masscan', 'scanner-nuclei']
    
    while True:
        try:
            for queue_name in queue_names:
                # Get queue size
                queue_size = await redis.llen(f'arq:queue:{queue_name}')
                ARQ_QUEUE_SIZE.labels(queue=queue_name).set(queue_size)
                
                # Get queue latency if queue not empty
                if queue_size > 0:
                    try:
                        # Get oldest job's timestamp
                        oldest_job = await redis.lindex(f'arq:queue:{queue_name}', -1)
                        if oldest_job:
                            job_details = await redis.hgetall(f'arq:job:{oldest_job.decode()}')
                            if b'enqueue_time' in job_details:
                                enqueue_time = float(job_details[b'enqueue_time'])
                                latency = time.time() - enqueue_time
                                ARQ_QUEUE_LATENCY.labels(queue=queue_name).set(latency)
                    except Exception as e:
                        logger.warning(f"Failed to get queue latency for {queue_name}: {e}")
                
                # Count active workers
                try:
                    workers = await redis.smembers(f'arq:workers:{queue_name}')
                    ARQ_WORKER_COUNT.labels(queue=queue_name).set(len(workers))
                except Exception as e:
                    logger.warning(f"Failed to count workers for {queue_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to update queue metrics: {e}")
        
        # Update every 15 seconds
        await asyncio.sleep(15)
