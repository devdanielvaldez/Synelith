from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from neurogenesis_api.database import get_session
from neurogenesis_api.persistence import create_research_run, get_research_run
from neurogenesis_api.schemas import ResearchRunRequest, ResearchRunResponse

router = APIRouter(prefix="/v1/research-runs", tags=["research-runs"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=ResearchRunResponse, status_code=status.HTTP_201_CREATED)
async def create_research_run_endpoint(
    request: ResearchRunRequest, session: Session
) -> ResearchRunResponse:
    run = await create_research_run(session, request)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return run


@router.get("/{research_run_id}", response_model=ResearchRunResponse)
async def get_research_run_endpoint(research_run_id: UUID, session: Session) -> ResearchRunResponse:
    run = await get_research_run(session, research_run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research run not found")
    return run
