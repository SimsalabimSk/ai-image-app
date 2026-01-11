from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .orm_base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String, ForeignKey("users.user_id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="projects")
    intents: Mapped[list["Intent"]] = relationship(back_populates="project")
    runs: Mapped[list["Run"]] = relationship(back_populates="project")


class Intent(Base):
    __tablename__ = "intents"

    intent_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String, ForeignKey("projects.project_id"))
    task_type: Mapped[str] = mapped_column(String, nullable=False)
    intent_text: Mapped[str] = mapped_column(Text, nullable=False)
    intent_spec_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped[Project | None] = relationship(back_populates="intents")
    runs: Mapped[list["Run"]] = relationship(back_populates="intent")


class Run(Base):
    __tablename__ = "runs"

    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String, ForeignKey("projects.project_id"))
    intent_id: Mapped[str | None] = mapped_column(String, ForeignKey("intents.intent_id"))

    status: Mapped[str] = mapped_column(String, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    policy_profile: Mapped[str] = mapped_column(String, nullable=False)
    orchestration_plan_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    latest_temp_asset_id: Mapped[str | None] = mapped_column(String, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped[Project | None] = relationship(back_populates="runs")
    intent: Mapped[Intent | None] = relationship(back_populates="runs")
    assets: Mapped[list["Asset"]] = relationship(back_populates="run")
    events: Mapped[list["Event"]] = relationship(back_populates="run")


class Asset(Base):
    __tablename__ = "assets"

    asset_id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str | None] = mapped_column(String, ForeignKey("runs.run_id"))

    type: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    storage_provider: Mapped[str] = mapped_column(String, nullable=False)
    storage_bucket: Mapped[str] = mapped_column(String, nullable=False)
    storage_key: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    is_temp: Mapped[bool] = mapped_column(Boolean, nullable=False)
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())

    run: Mapped[Run | None] = relationship(back_populates="assets")


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str | None] = mapped_column(String, ForeignKey("runs.run_id"))

    ts: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())
    event_type: Mapped[str] = mapped_column(String, nullable=False)

    # P-SW1 header fields
    run_mode: Mapped[str] = mapped_column(String, nullable=False)
    novelty_tier: Mapped[str] = mapped_column(String, nullable=False)
    feasibility_status: Mapped[str] = mapped_column(String, nullable=False)
    frontier_target: Mapped[str | None] = mapped_column(String, nullable=True)

    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    run: Mapped[Run | None] = relationship(back_populates="events")
