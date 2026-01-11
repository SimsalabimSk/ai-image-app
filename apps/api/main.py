from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from packages.common.db import db
from packages.common.logging import configure_json_logging

from .routers import health, intent, run, run_read, asset

logger = logging.getLogger("api")


def create_app() -> FastAPI:
    configure_json_logging()

    app = FastAPI(title="AI Image App API", version="0.1.0")

    @app.on_event("startup")
    def _startup() -> None:
        # Minimal DB connectivity check (fail fast in dev)
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get("x-request-id", "req_local")
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error")
        request_id = request.headers.get("x-request-id", "req_local")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL", "message": "Internal error", "request_id": request_id}},
        )

    app.include_router(health.router, tags=["health"])
    app.include_router(intent.router)
    app.include_router(run.router)
    app.include_router(run_read.router)
    app.include_router(asset.router)
    return app


app = create_app()
