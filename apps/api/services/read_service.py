from __future__ import annotations

import datetime as dt

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.common.orm_models import Asset, Event, Run


def get_run_or_404(session: Session, run_id: str) -> Run:
    row = session.execute(select(Run).where(Run.run_id == run_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="RUN_NOT_FOUND")
    return row


def list_assets(session: Session, run_id: str) -> list[Asset]:
    return list(session.execute(select(Asset).where(Asset.run_id == run_id)).scalars().all())


def list_events(session: Session, run_id: str, since_ts: dt.datetime | None, limit: int) -> list[Event]:
    q = select(Event).where(Event.run_id == run_id)
    if since_ts is not None:
        q = q.where(Event.ts >= since_ts)
    q = q.order_by(Event.ts.asc()).limit(limit)
    return list(session.execute(q).scalars().all())
