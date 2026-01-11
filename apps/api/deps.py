from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from packages.common.db import get_session as _get_session


def get_db_session() -> Generator[Session, None, None]:
    yield from _get_session()
