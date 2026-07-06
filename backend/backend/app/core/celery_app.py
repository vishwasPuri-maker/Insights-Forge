from celery import Celery
from app.core.config import settings
import app.db.base  # noqa: F401 -- registers all ORM models/mappers


celery_app = Celery(
    "insightsforge_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.ingestion"],
)
celery_app.set_default()




# Celery app configuration settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max execution time
    broker_connection_timeout=4,  # fail fast if Redis unavailable
    broker_connection_retry_on_startup=False,
    # Eager mode: run tasks synchronously in the calling process (no worker /
    # Redis needed). Default True so ingestion works on Render's free tier.
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,
)

# Auto-discover tasks registered in app.tasks modules
celery_app.autodiscover_tasks(["app"])
