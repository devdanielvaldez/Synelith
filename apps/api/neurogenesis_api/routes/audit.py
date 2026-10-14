from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from neurogenesis_api.audit_log import list_audit_events
from neurogenesis_api.database import get_session
from neurogenesis_api.schemas import AuditEventResponse

router = APIRouter(prefix="/v1/audit", tags=["audit"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("/events", response_model=tuple[AuditEventResponse, ...])
async def list_audit_events_endpoint(
    session: Session,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    action: Annotated[Optional[str], Query(min_length=1, max_length=100)] = None,  # noqa: UP045
    entity_type: Annotated[Optional[str], Query(min_length=1, max_length=80)] = None,  # noqa: UP045
) -> tuple[AuditEventResponse, ...]:
    return await list_audit_events(
        session,
        limit=limit,
        action=action,
        entity_type=entity_type,
    )
