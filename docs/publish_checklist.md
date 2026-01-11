# Publish checklist — MVP v0.1.0

## Repo hygiene
- [ ] CI green (test + smoke)
- [ ] Contract lock passes (`scripts/verify_contract_lock.py`)
- [ ] VERSION files set to 0.1.0
- [ ] CHANGELOG updated

## Local validation
- [ ] `make dev` succeeds end-to-end
- [ ] `scripts/smoke_e2e.py` produces `out/<asset_id>.png`
- [ ] `GET /run/{id}/events` shows RUN_CREATED → ORCHESTRATION_DECIDED → RUN_QUEUED → RUN_STARTED → ASSET_STORED → RUN_SUCCEEDED

## Release
- [ ] Create git tag: `v0.1.0`
- [ ] Create GitHub Release notes using CHANGELOG v0.1.0
- [ ] Archive artifacts if needed (OpenAPI + lock + alembic)

## Next (v0.1.1+)
- [ ] Real adapter interface (swap mock for real model providers)
- [ ] Auth (API keys) + per-project quotas
- [ ] Persistent asset promotion (temp → permanent)
