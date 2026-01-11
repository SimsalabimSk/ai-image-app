from __future__ import annotations

import logging

from packages.common.logging import configure_json_logging

from .executor import execute_run_sync
from .main import celery_app

configure_json_logging()
logger = logging.getLogger("worker.tasks")


@celery_app.task(name="execute_run")
def execute_run(run_id: str) -> dict:
    """T13 end-to-end: DB status + mock adapter + MinIO store + assets + events."""
    logger.info("execute_run called", extra={"run_id": run_id})
    result = execute_run_sync(run_id)
    logger.info("execute_run finished", extra={"run_id": run_id, "result": result})
    return result
