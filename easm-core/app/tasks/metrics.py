import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram

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
