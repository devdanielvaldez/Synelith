"""Read-only access to the append-only audit ledger."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neurogenesis_api import models
from neurogenesis_api.schemas import AuditEventResponse


async def list_audit_events(
    session: AsyncSession,
    *,
    limit: int,
    action: str | None = None,
    entity_type: str | None = None,
) -> tuple[AuditEventResponse, ...]:
    statement = select(models.AuditEvent)
    if action:
        statement = statement.where(models.AuditEvent.action == action)
    if entity_type:
        statement = statement.where(models.AuditEvent.entity_type == entity_type)
    events = await session.scalars(
        statement.order_by(models.AuditEvent.created_at.desc(), models.AuditEvent.id.desc()).limit(
            limit
        )
    )
    return tuple(
        AuditEventResponse(
            id=event.id,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            actor_type=event.actor_type,
            event_data=event.event_data,
            created_at=event.created_at,
        )
        for event in events
    )
