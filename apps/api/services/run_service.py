from __future__ import annotations

import datetime as dt
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.common.models import IntentSpec, OrchestrationPlan
from packages.common.orm_models import Intent, Run

from .orchestrator import build_orchestration_plan


def _load_intent_or_404(session: Session, intent_id: str) -> tuple[Intent, IntentSpec]:
    row = session.execute(select(Intent).where(Intent.intent_id == intent_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="INTENT_NOT_FOUND")
    spec = IntentSpec.model_validate(row.intent_spec_json)
    return row, spec


def create_run(
    session: Session,
    *,
    intent_id: str,
    mode: str,
    policy_profile: str,
) -> tuple[str, OrchestrationPlan]:
    intent_row, intent_spec = _load_intent_or_404(session, intent_id)

    plan = build_orchestration_plan(intent=intent_spec, mode=mode, policy_profile=policy_profile)

    run_id = f"run_{uuid.uuid4().hex[:10]}"
    run = Run(
        run_id=run_id,
        project_id=intent_row.project_id,
        intent_id=intent_row.intent_id,
        status="queued",
        mode=mode,
        policy_profile=policy_profile,
        orchestration_plan_json=plan.model_dump(),
        latest_temp_asset_id=None,
        error_code=None,
        error_message=None,
        created_at=dt.datetime.utcnow(),
        updated_at=dt.datetime.utcnow(),
    )
    session.add(run)
    return run_id, plan
