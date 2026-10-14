"""Transactional persistence operations with append-only audit events."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neurogenesis_api import models
from neurogenesis_api.schemas import (
    ProjectCreate,
    ProjectResponse,
    ResearchRunRequest,
    ResearchRunResponse,
    ResearchTask,
    plan_research_run,
)


async def create_project(session: AsyncSession, request: ProjectCreate) -> ProjectResponse:
    project = models.Project(
        name=request.name,
        disease_area=request.disease_area,
        description=request.description,
    )
    session.add(project)
    await session.flush()
    session.add(
        models.AuditEvent(
            action="project.created",
            entity_type="project",
            entity_id=project.id,
            actor_type="user",
            event_data={"status": project.status},
        )
    )
    await session.commit()
    await session.refresh(project)
    return _project_response(project)


async def list_projects(session: AsyncSession) -> tuple[ProjectResponse, ...]:
    result = await session.scalars(
        select(models.Project).order_by(models.Project.created_at.desc())
    )
    return tuple(_project_response(project) for project in result)


async def get_project(session: AsyncSession, project_id: UUID) -> ProjectResponse | None:
    project = await session.get(models.Project, project_id)
    return _project_response(project) if project else None


async def create_research_run(
    session: AsyncSession, request: ResearchRunRequest
) -> ResearchRunResponse | None:
    project = await session.get(models.Project, request.project_id)
    if project is None:
        return None

    plan = plan_research_run(request)
    run = models.ResearchRun(
        id=plan.id,
        project_id=request.project_id,
        question=plan.question,
        level=plan.level,
        status=plan.status,
        scope=request.scope.model_dump(mode="json"),
        outputs=list(request.outputs),
        tasks=[task.model_dump(mode="json") for task in plan.tasks],
        disclaimer=plan.disclaimer,
    )
    session.add(run)
    session.add(
        models.AuditEvent(
            action="research_run.planned",
            entity_type="research_run",
            entity_id=run.id,
            actor_type="user",
            event_data={"project_id": str(project.id), "task_count": len(plan.tasks)},
        )
    )
    await session.commit()
    await session.refresh(run)
    return _research_run_response(run)


async def get_research_run(
    session: AsyncSession, research_run_id: UUID
) -> ResearchRunResponse | None:
    run = await session.get(models.ResearchRun, research_run_id)
    return _research_run_response(run) if run else None


def _project_response(project: models.Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        disease_area=project.disease_area,
        description=project.description,
        status="active",
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _research_run_response(run: models.ResearchRun) -> ResearchRunResponse:
    return ResearchRunResponse(
        id=run.id,
        project_id=run.project_id,
        question=run.question,
        level=run.level,  # type: ignore[arg-type]
        status="planned",
        created_at=run.created_at,
        tasks=tuple(ResearchTask.model_validate(task) for task in run.tasks),
        disclaimer=run.disclaimer,
    )
