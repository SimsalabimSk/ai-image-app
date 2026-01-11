from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..deps import get_db_session
from ..schemas.run import RunCreateRequest, RunCreateResponse, RunLinks
from ..services.events import emit_event
from ..services.queue import celery_client
from ..services.run_service import create_run

router = APIRouter(prefix="/run", tags=["run"])


@router.post("", response_model=RunCreateResponse, status_code=201)
def post_run(
    req: RunCreateRequest,
    request: Request,
    session: Session = Depends(get_db_session),
) -> RunCreateResponse:
    run_id, plan = create_run(
        session,
        intent_id=req.intent_id,
        mode=req.mode,
        policy_profile=req.policy_profile,
    )

    # Append-only events (RA-003 feed). MVP defaults: N_LOW + proceed + known_safe
    emit_event(
        session,
        run_id=run_id,
        event_type="RUN_CREATED",
        # P-SW1 header fields:
        run_mode=req.mode,
        novelty_tier="N_LOW",
        feasibility_status="proceed",
        frontier_target="known_safe",
        payload={"intent_id": req.intent_id, "policy_profile": req.policy_profile},
    )
    emit_event(
        session,
        run_id=run_id,
        event_type="ORCHESTRATION_DECIDED",
        run_mode=req.mode,
        novelty_tier="N_LOW",
        feasibility_status="proceed",
        frontier_target="known_safe",
        payload={"orchestration_plan": plan.model_dump()},
    )
    emit_event(
        session,
        run_id=run_id,
        event_type="RUN_QUEUED",
        run_mode=req.mode,
        novelty_tier="N_LOW",
        feasibility_status="proceed",
        frontier_target="known_safe",
        payload={"queue": "celery", "task": "execute_run"},
    )

    session.commit()

    # Enqueue celery task (implemented in later ticket T13).
    # This will be a no-op until the worker task exists.
    celery_client.send_task("execute_run", args=[run_id])

    links = RunLinks(
        events=f"/run/{run_id}/events",
        explain=f"/run/{run_id}/explain",
    )
    return RunCreateResponse(run_id=run_id, status="queued", orchestration_plan=plan, links=links)
