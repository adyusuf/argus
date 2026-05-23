from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "argus",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.autodiscover_tasks(["app.workers"])

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "scan-active-cameras": {
            "task": "app.workers.tasks.scan_all_cameras",
            "schedule": settings.frame_interval_seconds,
        },
    },
)
