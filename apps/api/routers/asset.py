from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from packages.common.storage import presign_get_url

from ..deps import get_db_session
from ..services.asset_service import assert_not_expired, get_asset_or_404

router = APIRouter(prefix="/asset", tags=["asset"])


@router.get("/{asset_id}")
def get_asset(asset_id: str, request: Request, session: Session = Depends(get_db_session)):
    asset = get_asset_or_404(session, asset_id)
    try:
        assert_not_expired(asset)
    except Exception as e:
        # Map to error model
        # FastAPI will handle HTTPException by default; we want consistent body.
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            request_id = request.headers.get("x-request-id", "req_local")
            code = e.detail
            status = e.status_code
            return JSONResponse(status_code=status, content={"error": {"code": code, "message": code, "request_id": request_id}})
        raise

    url = presign_get_url(bucket=asset.storage_bucket, key=asset.storage_key, expires_seconds=300)
    # Redirect (client downloads directly)
    return RedirectResponse(url=url, status_code=302)
