from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy.orm import Session

from packages.common.models import Constraints, IntentSpec, SafetySpec
from packages.common.orm_models import Intent

from ..schemas.intent import IntentCreateRequest


def create_intent(session: Session, req: IntentCreateRequest) -> tuple[str, IntentSpec]:
    # IM-1 minimal: normalize into IntentSpec
    spec = IntentSpec(
        task_type=req.task_type,
        intent_text=req.intent_text.strip(),
        constraints=Constraints(aspect_ratio=req.aspect_ratio, resolution=req.resolution),
        safety=SafetySpec(policy_level=req.policy_level),
        seed=req.seed,
    )

    intent_id = f"in_{uuid.uuid4().hex[:10]}"
    row = Intent(
        intent_id=intent_id,
        project_id=req.project_id,
        task_type=req.task_type,
        intent_text=req.intent_text.strip(),
        intent_spec_json=spec.model_dump(),
        created_at=dt.datetime.utcnow(),
    )
    session.add(row)
    return intent_id, spec
