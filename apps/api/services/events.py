from __future__ import annotations

import datetime as dt
import uuid
from typing import Any, Optional

from sqlalchemy.orm import Session

from packages.common.orm_models import Event


def emit_event(
    session: Session,
    *,
    run_id: str,
    event_type: str,
    run_mode: str,
    novelty_tier: str,
    feasibility_status: str,
    frontier_target: Optional[str] = None,
    payload: Optional[dict[str, Any]] = None,
) -> str:
    event_id = str(uuid.uuid4())
    ev = Event(
        event_id=event_id,
        run_id=run_id,
        ts=dt.datetime.utcnow(),
        event_type=event_type,
        run_mode=run_mode,
        novelty_tier=novelty_tier,
        feasibility_status=feasibility_status,
        frontier_target=frontier_target,
        payload_json=payload,
    )
    session.add(ev)
    return event_id
