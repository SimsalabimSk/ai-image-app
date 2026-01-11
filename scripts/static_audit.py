from __future__ import annotations

import importlib
import sys
import compileall


MODULES = [
    "apps.api.main",
    "apps.api.routers.intent",
    "apps.api.routers.run",
    "apps.api.routers.run_read",
    "apps.api.routers.asset",
    "apps.worker.main",
    "apps.worker.tasks",
    "apps.worker.executor",
    "packages.common.storage",
    "packages.common.storage_paths",
]


def main() -> None:
    ok = compileall.compile_dir(".", quiet=1)
    if not ok:
        raise SystemExit("compileall failed")

    for m in MODULES:
        importlib.import_module(m)

    # Contract lock check
    from scripts.verify_contract_lock import main as verify_lock  # type: ignore
    verify_lock()

    print("Static audit OK.")


if __name__ == "__main__":
    main()
