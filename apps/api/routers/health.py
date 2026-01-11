from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..deps import get_db_session

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
def health_db(session: Session = Depends(get_db_session)) -> dict:
    session.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}
