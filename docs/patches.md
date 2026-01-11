# Patch Log (App-level)

Append-only.

## P-APP-001 — Static Stability Audit (no-docker)
- Date: 2026-01-10
- Motivation: Docker is not available in some environments; we still want a minimal stability signal.
- Change: Add `scripts/static_audit.py` (compileall + import key modules + contract lock verify).
- Expected outcome: Early detection of import/packaging regressions without running infra.
