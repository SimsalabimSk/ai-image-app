from __future__ import annotations

import datetime as dt

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.common.orm_models import Asset


def get_asset_or_404(session: Session, asset_id: str) -> Asset:
    row = session.execute(select(Asset).where(Asset.asset_id == asset_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="ASSET_NOT_FOUND")
    return row


def assert_not_expired(asset: Asset) -> None:
    if asset.is_temp and asset.expires_at is not None:
        # expires_at stored as naive utc in our worker
        now = dt.datetime.utcnow()
        if asset.expires_at <= now:
            raise HTTPException(status_code=410, detail="ASSET_EXPIRED")
