"""Persistence models for the auditable research domain."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)  # noqa: UP017 - local Python 3.9 validation


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    disease_area: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)  # noqa: UP045
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class Source(TimestampMixin, Base):
    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("provider", "external_id", name="uq_source_provider_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(Text)  # noqa: UP045
    license: Mapped[Optional[str]] = mapped_column(String(255))  # noqa: UP045
    access_level: Mapped[str] = mapped_column(String(50), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class Paper(TimestampMixin, Base):
    __tablename__ = "papers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    doi: Mapped[Optional[str]] = mapped_column(String(255), unique=True)  # noqa: UP045
    pmid: Mapped[Optional[str]] = mapped_column(String(32), unique=True)  # noqa: UP045
    publication_date: Mapped[Optional[str]] = mapped_column(String(64))  # noqa: UP045
    review_status: Mapped[str] = mapped_column(String(32), default="unreviewed", nullable=False)


class Claim(TimestampMixin, Base):
    __tablename__ = "claims"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    paper_id: Mapped[UUID] = mapped_column(ForeignKey("papers.id"), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    locator: Mapped[str] = mapped_column(String(255), nullable=False)
    interpretation: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), default="unreviewed", nullable=False)
    source_access: Mapped[str] = mapped_column(String(50), nullable=False)


class ResearchRun(TimestampMixin, Base):
    __tablename__ = "research_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="planned", nullable=False)
    scope: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    outputs: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    tasks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(50), default="system", nullable=False)
    event_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now(), nullable=False
    )
