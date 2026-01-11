from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import settings


@dataclass(frozen=True)
class Db:
    engine: Engine
    session_factory: sessionmaker


def build_db() -> Db:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return Db(engine=engine, session_factory=session_factory)


db = build_db()


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency generator."""
    session: Session = db.session_factory()
    try:
        yield session
    finally:
        session.close()
