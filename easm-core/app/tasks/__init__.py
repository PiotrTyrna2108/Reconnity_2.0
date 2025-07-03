# Import from reorganized structure

# Import from tasks directory
from .tasks import scan_asset, process_scan_result

# Import from config directory
from .config import get_redis_pool
from .config import redis_settings, with_redis_retry, RedisRetryClient, WorkerSettings

# Import from monitoring directory
from .monitoring import (
    ARQ_TASK_RECEIVED, 
    ARQ_TASK_STARTED,
    ARQ_TASK_COMPLETED,
    ARQ_TASK_FAILED,
    ARQ_TASK_DURATION,
    ARQ_QUEUE_SIZE,
    ARQ_COMMUNICATION_ERRORS,
    ARQ_RETRY_COUNT,
    monitor_queue_metrics,
    create_metrics_middleware
)

# For backward compatibility - keep old imports functional
# Removed imports from .scan_tasks, .queue, .retry, .metrics as these modules do not exist or are misplaced.
