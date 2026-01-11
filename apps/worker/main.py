from __future__ import annotations

import logging

from celery import Celery

from packages.common.logging import configure_json_logging
from packages.common.settings import settings

configure_json_logging()
logger = logging.getLogger("worker")

celery_app = Celery(
    "ai_image_app_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Task autodiscovery placeholder — real tasks added later.
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Register tasks
from . import tasks  # noqa: E402,F401
