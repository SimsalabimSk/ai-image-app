from __future__ import annotations

from celery import Celery

from packages.common.settings import settings

celery_client = Celery(
    "ai_image_app_api_client",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
