from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from packages.common.models import OrchestrationPlan


class RunCreateRequest(BaseModel):
    intent_id: str
    mode: Literal["fast", "boost", "deep"] = "boost"
    policy_profile: Literal["production", "growth", "frontier"] = "production"


class RunLinks(BaseModel):
    events: str
    explain: str


class RunCreateResponse(BaseModel):
    run_id: str
    status: Literal["queued"]
    orchestration_plan: OrchestrationPlan
    links: RunLinks
