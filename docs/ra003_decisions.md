# RA-003 Decision Record (App-level)

**Rule:** Append-only. Never rewrite old entries.  
**Contract Freeze (MVP baseline):** OpenAPI **v0.1.2** + DB schema **v0.1.0** locked via `contracts/lock.m0.1.json`.

---

## DR-APP-0001 — Contract Freeze MVP baseline
- Date: 2026-01-10
- Decision: Freeze OpenAPI v0.1.2 and DB schema v0.1.0 as MVP baseline.
- Enforcement: CI runs `scripts/verify_contract_lock.py` (fails on contract drift).
- Breaking changes: forbidden without a new decision entry + explicit lock update.
