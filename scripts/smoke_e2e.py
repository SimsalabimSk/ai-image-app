from __future__ import annotations

import os
import time
import json
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
PROJECT_ID = os.getenv("PROJECT_ID", "proj_demo")
REQUEST_ID = os.getenv("REQUEST_ID", "req_smoke_001")


def _h():
    return {"x-request-id": REQUEST_ID, "content-type": "application/json"}


def main() -> None:
    print("BASE_URL:", BASE_URL)

    # 1) Create intent
    intent_req = {
        "project_id": PROJECT_ID,
        "task_type": "generate",
        "intent_text": "A minimal demo image of a cat astronaut, simple style.",
        "style_tags": ["demo"],
        "aspect_ratio": "1:1",
        "resolution": "512x512",
        "seed": 123,
        "policy_level": "standard",
    }
    r = requests.post(f"{BASE_URL}/intent", headers=_h(), data=json.dumps(intent_req), timeout=30)
    r.raise_for_status()
    intent = r.json()
    intent_id = intent["intent_id"]
    print("intent_id:", intent_id)

    # 2) Create run
    run_req = {"intent_id": intent_id, "mode": "boost", "policy_profile": "production"}
    r = requests.post(f"{BASE_URL}/run", headers=_h(), data=json.dumps(run_req), timeout=30)
    r.raise_for_status()
    run = r.json()
    run_id = run["run_id"]
    print("run_id:", run_id)

    # 3) Poll run
    status = None
    for i in range(60):
        rr = requests.get(f"{BASE_URL}/run/{run_id}", headers={"x-request-id": REQUEST_ID}, timeout=30)
        rr.raise_for_status()
        data = rr.json()
        status = data["status"]
        if status in ("succeeded", "failed"):
            print("final status:", status)
            if status == "failed":
                print("error:", data.get("error"))
            break
        if i % 5 == 0:
            print("status:", status)
        time.sleep(1.0)

    if status != "succeeded":
        raise SystemExit(f"Run did not succeed (status={status})")

    latest_asset_id = data["latest_temp_asset_id"]
    print("latest_temp_asset_id:", latest_asset_id)

    # 4) Fetch events
    er = requests.get(f"{BASE_URL}/run/{run_id}/events?limit=200", headers={"x-request-id": REQUEST_ID}, timeout=30)
    er.raise_for_status()
    events = er.json()["events"]
    print("events:", [e["event"] for e in events])

    # 5) Download asset (follows redirect to presign)
    ar = requests.get(f"{BASE_URL}/asset/{latest_asset_id}", headers={"x-request-id": REQUEST_ID}, timeout=30, allow_redirects=True)
    ar.raise_for_status()
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{latest_asset_id}.png")
    with open(out_path, "wb") as f:
        f.write(ar.content)
    print("saved:", out_path, "bytes:", len(ar.content))


if __name__ == "__main__":
    main()
