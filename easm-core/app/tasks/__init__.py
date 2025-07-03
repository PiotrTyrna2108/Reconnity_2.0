from arq import create_pool
from .redis_config import redis_settings

# Function to create ARQ Redis pool
async def get_redis_pool():
    return await create_pool(redis_settings)

# Make functions available at package level
from .scan_tasks import scan_asset, process_scan_result

# Import WorkerSettings after defining redis_settings
from .queue import WorkerSettings
