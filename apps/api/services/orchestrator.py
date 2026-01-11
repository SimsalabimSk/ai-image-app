from __future__ import annotations

from packages.common.models import ModuleDecision, OrchestrationPlan, PolicyProfile, RunMode
from packages.common.models import IntentSpec


def build_orchestration_plan(
    *,
    intent: IntentSpec,
    mode: RunMode = "boost",
    policy_profile: PolicyProfile = "production",
) -> OrchestrationPlan:
    """MF-7 v0.2 + PMR-001 (minimal stub).

    Deterministic defaults for MVP U1:
    - MF-6 (novelty budget) is ACTIVE with implicit N_LOW
    - FG-1 (feasibility gate) is ACTIVE -> proceed
    - FM-1 (frontier map / known safe) is ACTIVE
    - RA-016 (scenario selector mandatory) is ACTIVE (implicit scenario=U1)
    - QI-01 is BYPASS by default (N_LOW + known_safe)
    """
    modules: list[ModuleDecision] = [
        ModuleDecision(name="MF-6", action="ACTIVATE"),
        ModuleDecision(name="FG-1", action="ACTIVATE"),
        ModuleDecision(name="FM-1", action="ACTIVATE"),
        ModuleDecision(name="RA-016", action="ACTIVATE"),
        ModuleDecision(name="QI-01", action="BYPASS", reason="N_LOW + known_safe (MVP default)"),
    ]

    # time budget heuristic (MVP): allow 30s
    return OrchestrationPlan(
        policy_profile=policy_profile,
        modules=modules,
        time_budget_ms=30000,
        qi_profile=None,
    )
