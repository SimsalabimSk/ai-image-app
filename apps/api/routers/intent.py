from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db_session
from ..schemas.intent import IntentCreateRequest, IntentCreateResponse
from ..services.intent_service import create_intent

router = APIRouter(prefix="/intent", tags=["intent"])


@router.post("", response_model=IntentCreateResponse, status_code=201)
def post_intent(req: IntentCreateRequest, session: Session = Depends(get_db_session)) -> IntentCreateResponse:
    intent_id, spec = create_intent(session, req)
    session.commit()
    return IntentCreateResponse(intent_id=intent_id, intent_spec=spec)
