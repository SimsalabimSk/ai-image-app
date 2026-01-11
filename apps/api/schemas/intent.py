from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from packages.common.models import Constraints, IntentSpec, SafetySpec


class IntentCreateRequest(BaseModel):
    project_id: str
    task_type: Literal["generate"] = "generate"
    intent_text: str = Field(min_length=1, max_length=4000)
    style_tags: list[str] = []
    aspect_ratio: Literal["1:1", "4:3", "3:4", "16:9", "9:16"]
    resolution: Literal["512x512", "768x768", "1024x1024", "1024x576", "576x1024"]
    seed: Optional[int] = None
    policy_level: Literal["standard", "strict"] = "standard"


class IntentCreateResponse(BaseModel):
    intent_id: str
    intent_spec: IntentSpec
