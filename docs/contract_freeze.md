# Contract Freeze (MVP baseline)

## What is frozen
- **OpenAPI:** `openapi/openapi.v0.1.2.yaml`
- **DB schema:** Alembic head tracked in `contracts/lock.m0.1.json`

## Rule
No breaking changes **without**:
1) New append-only RA-003 entry (`docs/ra003_decisions.md`)
2) Updating `contracts/lock.m0.1.json` (and bumping versions as needed)
3) Passing CI (default forbids contract drift)

## CI enforcement
CI runs:
- `python scripts/verify_contract_lock.py`

It fails if OpenAPI or Alembic head differs from lock.
