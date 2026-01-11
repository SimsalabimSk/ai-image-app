# Changelog

## v0.1.0 — MVP baseline
- Intent-first flow: `/intent` → `/run` → `/run/{id}` + `/events` + `/asset`
- Orchestration stub (deterministic plan for U1)
- Worker executes run end-to-end with mock PNG generator
- MinIO-backed temp asset storage with TTL + presigned download
- Append-only audit events feed
- CI: lint/type/test + OpenAPI sanity + compose smoke
- Contract freeze: OpenAPI v0.1.2 + DB schema v0.1.0 (lock + CI enforcement)
