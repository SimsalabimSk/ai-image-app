from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel

from .run import RunLinks


class ErrorBody(BaseModel):
    code: str
    message: str


class AssetRef(BaseModel):
    asset_id: str
    type: Literal["image"] = "image"
    url: str


class RunGetResponse(BaseModel):
    run_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    latest_temp_asset_id: Optional[str] = None
    assets: list[AssetRef] = []
    error: Optional[ErrorBody] = None
    links: RunLinks


class AuditEvent(BaseModel):
    event: str
    ts: str
    run_id: str
    run_mode: Literal["fast", "boost", "deep"]
    novelty_tier: Literal["N_LOW", "N_MED", "N_HIGH"]
    feasibility_status: Literal["proceed", "proceed_with_guards", "revise", "blocked"]
    frontier_target: Optional[str] = None
    payload: Optional[dict[str, Any]] = None


class RunEventsResponse(BaseModel):
    run_id: str
    events: list[AuditEvent]


class RunExplainResponse(BaseModel):
    run_id: str
    summary: str
    constraints: list[str]
    policy: dict
