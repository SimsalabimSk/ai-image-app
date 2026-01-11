from __future__ import annotations

import json
import os
import sys
import hashlib
import glob
import re


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_alembic_head(versions_glob: str) -> tuple[str | None, str | None]:
    paths = glob.glob(versions_glob)
    if not paths:
        return None, None
    # Choose most recently modified as "head" for MVP baseline lock.
    path = max(paths, key=lambda p: os.path.getmtime(p))
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"revision\s*=\s*['\"]([^'\"]+)['\"]", txt)
    rev = m.group(1) if m else os.path.basename(path)
    return rev, path


def main() -> None:
    allow = os.getenv("ALLOW_CONTRACT_CHANGE", "0") == "1"

    with open("contracts/lock.m0.1.json", "r", encoding="utf-8") as f:
        lock = json.load(f)

    openapi = lock["contract"]["openapi"]
    expected_openapi_sha = openapi["sha256"]
    actual_openapi_sha = sha256_file(openapi["path"])

    expected_rev = lock["contract"]["db_schema"]["alembic_head_revision"]
    actual_rev, actual_path = find_alembic_head("infra/alembic/versions/*.py")

    problems: list[str] = []
    if actual_openapi_sha != expected_openapi_sha:
        problems.append("OpenAPI hash differs from lock (contract changed).")
    if expected_rev != actual_rev:
        problems.append("Alembic head revision differs from lock (schema changed).")

    if problems and not allow:
        print("CONTRACT FREEZE VIOLATION:")
        for p in problems:
            print("-", p)
        print("\nTo change contracts intentionally:")
        print("1) Add RA-003 decision entry (docs/ra003_decisions.md)")
        print("2) Update contracts/lock.m0.1.json (and bump OpenAPI/DB version if needed)")
        print("3) Re-run CI with ALLOW_CONTRACT_CHANGE=1 only for that PR (then remove).")
        sys.exit(1)

    print("Contract lock OK." if not problems else "Contract changed but ALLOW_CONTRACT_CHANGE=1 set.")
    if problems:
        for p in problems:
            print("-", p)
        print("Detected head:", actual_rev, "file:", actual_path)


if __name__ == "__main__":
    main()
