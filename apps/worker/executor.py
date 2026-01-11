from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from packages.common.db import get_session
from packages.common.orm_models import Asset, Event, Intent, Run
from packages.common.storage import put_bytes
from packages.common.storage_paths import temp_asset_key
from packages.common.settings import settings

from .adapters.mock_image import generate_deterministic_png


def _emit_event(
    session: Session,
    *,
    run_id: str,
    event_type: str,
    run_mode: str,
    novelty_tier: str,
    feasibility_status: str,
    frontier_target: str | None,
    payload: dict | None,
) -> None:
    ev = Event(
        event_id=str(uuid.uuid4()),
        run_id=run_id,
        ts=dt.datetime.utcnow(),
        event_type=event_type,
        run_mode=run_mode,
        novelty_tier=novelty_tier,
        feasibility_status=feasibility_status,
        frontier_target=frontier_target,
        payload_json=payload,
    )
    session.add(ev)


def execute_run_sync(run_id: str) -> dict:
    # Note: using session generator from packages/common/db.py
    session_gen = get_session()
    session: Session = next(session_gen)
    try:
        run = session.execute(select(Run).where(Run.run_id == run_id)).scalar_one_or_none()
        if run is None:
            return {"run_id": run_id, "status": "not_found"}

        # Load intent spec for generation
        intent = session.execute(select(Intent).where(Intent.intent_id == run.intent_id)).scalar_one()
        intent_spec = intent.intent_spec_json

        # Mark running
        run.status = "running"
        run.updated_at = dt.datetime.utcnow()
        _emit_event(
            session,
            run_id=run_id,
            event_type="RUN_STARTED",
            run_mode=run.mode,
            novelty_tier="N_LOW",
            feasibility_status="proceed",
            frontier_target="known_safe",
            payload=None,
        )
        session.commit()

        # Generate deterministic mock PNG
        res = generate_deterministic_png(
            intent_text=intent_spec["intent_text"],
            resolution=intent_spec["constraints"]["resolution"],
            seed=intent_spec.get("seed"),
        )

        asset_id = f"as_{uuid.uuid4().hex[:10]}"
        key = temp_asset_key(project_id=run.project_id or "proj_unknown", run_id=run_id, asset_id=asset_id)

        put = put_bytes(
            bucket=settings.s3_bucket,
            key=key,
            data=res.bytes,
            content_type=res.mime_type,
        )

        expires_at = dt.datetime.utcnow() + dt.timedelta(hours=settings.temp_ttl_hours)

        asset = Asset(
            asset_id=asset_id,
            run_id=run_id,
            type="image",
            mime_type=res.mime_type,
            storage_provider="minio",
            storage_bucket=put.bucket,
            storage_key=put.key,
            sha256=put.sha256,
            size_bytes=put.size_bytes,
            is_temp=True,
            expires_at=expires_at,
            created_at=dt.datetime.utcnow(),
        )
        session.add(asset)

        _emit_event(
            session,
            run_id=run_id,
            event_type="ASSET_STORED",
            run_mode=run.mode,
            novelty_tier="N_LOW",
            feasibility_status="proceed",
            frontier_target="known_safe",
            payload={"asset_id": asset_id, "bucket": put.bucket, "key": put.key, "sha256": put.sha256},
        )

        # Mark succeeded
        run.status = "succeeded"
        run.latest_temp_asset_id = asset_id
        run.updated_at = dt.datetime.utcnow()

        _emit_event(
            session,
            run_id=run_id,
            event_type="RUN_SUCCEEDED",
            run_mode=run.mode,
            novelty_tier="N_LOW",
            feasibility_status="proceed",
            frontier_target="known_safe",
            payload={"latest_temp_asset_id": asset_id},
        )

        session.commit()
        return {"run_id": run_id, "status": "succeeded", "latest_temp_asset_id": asset_id}
    except Exception as e:
        # best-effort fail record
        try:
            run = session.execute(select(Run).where(Run.run_id == run_id)).scalar_one_or_none()
            if run is not None:
                run.status = "failed"
                run.error_code = "WORKER_ERROR"
                run.error_message = str(e)
                run.updated_at = dt.datetime.utcnow()
                _emit_event(
                    session,
                    run_id=run_id,
                    event_type="RUN_FAILED",
                    run_mode=run.mode if run is not None else "boost",
                    novelty_tier="N_LOW",
                    feasibility_status="proceed",
                    frontier_target="known_safe",
                    payload={"error": str(e)},
                )
                session.commit()
        finally:
            pass
        return {"run_id": run_id, "status": "failed", "error": str(e)}
    finally:
        try:
            session_gen.close()
        except Exception:
            pass
        session.close()
