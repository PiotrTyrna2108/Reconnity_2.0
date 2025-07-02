from celery import Celery
import os

# Initialize Celery app
celery_app = Celery("core")
celery_app.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks to register them
from .scan_tasks import scan_asset  # noqa