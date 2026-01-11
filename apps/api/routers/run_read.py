from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..deps import get_db_session
from ..schemas.read import (
    AuditEvent,
    ErrorBody,
    RunEventsResponse,
    RunExplainResponse,
    RunGetResponse,
    AssetRef,
)
from ..schemas.run import RunLinks
from ..services.read_service import get_run_or_404, list_assets, list_events

router = APIRouter(prefix="/run", tags=["run-read"])


@router.get("/{run_id}", response_model=RunGetResponse)
def get_run(run_id: str, session: Session = Depends(get_db_session)) -> RunGetResponse:
    run = get_run_or_404(session, run_id)
    assets = list_assets(session, run_id)

    asset_refs: list[AssetRef] = []
    for a in assets:
        asset_refs.append(AssetRef(asset_id=a.asset_id, url=f"/asset/{a.asset_id}"))

    error = None
    if run.status == "failed":
        error = ErrorBody(code=run.error_code or "UNKNOWN", message=run.error_message or "failed")

    links = RunLinks(events=f"/run/{run_id}/events", explain=f"/run/{run_id}/explain")
    return RunGetResponse(
        run_id=run_id,
        status=run.status,
        latest_temp_asset_id=run.latest_temp_asset_id,
        assets=asset_refs,
        error=error,
        links=links,
    )


@router.get("/{run_id}/events", response_model=RunEventsResponse)
def get_run_events(
    run_id: str,
    since_ts: Optional[str] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    session: Session = Depends(get_db_session),
) -> RunEventsResponse:
    # validate run exists
    _ = get_run_or_404(session, run_id)

    since_dt: dt.datetime | None = None
    if since_ts is not None:
        since_dt = dt.datetime.fromisoformat(since_ts.replace("Z", "+00:00"))

    events = list_events(session, run_id, since_dt, limit)

    out: list[AuditEvent] = []
    for e in events:
        out.append(
            AuditEvent(
                event=e.event_type,
                ts=e.ts.replace(tzinfo=dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                run_id=run_id,
                run_mode=e.run_mode,
                novelty_tier=e.novelty_tier,
                feasibility_status=e.feasibility_status,
                frontier_target=e.frontier_target,
                payload=e.payload_json,
            )
        )

    return RunEventsResponse(run_id=run_id, events=out)


@router.get("/{run_id}/explain", response_model=RunExplainResponse)
def get_run_explain(run_id: str, session: Session = Depends(get_db_session)) -> RunExplainResponse:
    run = get_run_or_404(session, run_id)

    # MVP explain is audit-safe + minimal
    summary = (
        f"Run {run_id} status={run.status}. "
        f"Mode={run.mode}, policy_profile={run.policy_profile}. "
        f"latest_temp_asset_id={run.latest_temp_asset_id}."
    )
    constraints = [
        "Append-only audit events (/run/{run_id}/events)",
        "Temp assets have TTL and may expire",
        "No vendor lock-in in infra (Postgres/Redis/MinIO)",
    ]
    policy = {"policy_profile": run.policy_profile}

    return RunExplainResponse(run_id=run_id, summary=summary, constraints=constraints, policy=policy)
