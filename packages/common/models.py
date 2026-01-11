from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


TaskType = Literal["generate"]
RunMode = Literal["fast", "boost", "deep"]
PolicyProfile = Literal["production", "growth", "frontier"]


class Constraints(BaseModel):
    aspect_ratio: str
    resolution: str


class SafetySpec(BaseModel):
    policy_level: Literal["standard", "strict"] = "standard"


class IntentSpec(BaseModel):
    task_type: TaskType = "generate"
    intent_text: str = Field(min_length=1, max_length=4000)
    constraints: Constraints
    safety: SafetySpec = SafetySpec()
    seed: Optional[int] = None


class ModuleDecision(BaseModel):
    name: str
    action: Literal["ACTIVATE", "BYPASS"]
    reason: Optional[str] = None


class OrchestrationPlan(BaseModel):
    policy_profile: PolicyProfile = "production"
    modules: list[ModuleDecision]
    time_budget_ms: int = 30000
    qi_profile: Optional[Literal["lite", "standard", "frontier"]] = None
