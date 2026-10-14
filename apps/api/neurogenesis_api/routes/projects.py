from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from neurogenesis_api.database import get_session
from neurogenesis_api.persistence import create_project, get_project, list_projects
from neurogenesis_api.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/v1/projects", tags=["projects"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(request: ProjectCreate, session: Session) -> ProjectResponse:
    return await create_project(session, request)


@router.get("", response_model=tuple[ProjectResponse, ...])
async def list_projects_endpoint(session: Session) -> tuple[ProjectResponse, ...]:
    return await list_projects(session)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_endpoint(project_id: UUID, session: Session) -> ProjectResponse:
    project = await get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
