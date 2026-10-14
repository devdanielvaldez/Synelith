"""Versioned public API schemas."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["neurogenesis-api"] = "neurogenesis-api"
    version: Literal["0.1.0"] = "0.1.0"


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=160)
    disease_area: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=4_000)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    disease_area: str
    description: str | None
    status: Literal["active"] = "active"
    created_at: datetime
    updated_at: datetime


class ResearchScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    species: tuple[str, ...] = ("human",)
    publication_cutoff: str | None = None


class ResearchRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: UUID
    question: str = Field(min_length=10, max_length=2_000)
    level: Literal["basic", "intermediate", "advanced", "scientific"] = "scientific"
    scope: ResearchScope = Field(default_factory=ResearchScope)
    outputs: tuple[Literal["evidence_matrix", "knowledge_graph", "hypotheses"], ...] = (
        "evidence_matrix",
    )

    @field_validator("question")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        return " ".join(value.split())


class ResearchTask(BaseModel):
    order: int
    agent: str
    objective: str
    status: Literal["pending"] = "pending"


class ResearchRunResponse(BaseModel):
    id: UUID
    project_id: UUID
    question: str
    level: Literal["basic", "intermediate", "advanced", "scientific"]
    status: Literal["planned"] = "planned"
    created_at: datetime
    tasks: tuple[ResearchTask, ...]
    disclaimer: str


class PubMedImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        return " ".join(value.split())


class PaperResponse(BaseModel):
    id: UUID
    title: str
    doi: str | None
    pmid: str | None
    publication_date: str | None
    review_status: Literal["unreviewed"] = "unreviewed"
    source_id: UUID
    source_access: Literal["metadata_only"] = "metadata_only"
    source_hash: str
    created_at: datetime


class PubMedImportResponse(BaseModel):
    query: str
    retrieved: int
    created: int
    existing: int
    library_total: int
    complete: Literal[True] = True
    papers: tuple[PaperResponse, ...]
    disclaimer: str = "Imported records contain bibliographic metadata only and have not been reviewed as evidence."


def plan_research_run(request: ResearchRunRequest) -> ResearchRunResponse:
    tasks = [
        ResearchTask(
            order=1,
            agent="literature-scout",
            objective="Retrieve and deduplicate eligible literature within the declared scope.",
        ),
        ResearchTask(
            order=2,
            agent="paper-analyst",
            objective="Extract source-grounded claims and methodological limitations.",
        ),
        ResearchTask(
            order=3,
            agent="adversarial-reviewer",
            objective="Search for counter-evidence, confounders, and rival explanations.",
        ),
    ]
    if "knowledge_graph" in request.outputs:
        tasks.append(
            ResearchTask(
                order=len(tasks) + 1,
                agent="graph-curator",
                objective="Normalize entities and prepare provenance-backed relationships.",
            )
        )
    if "hypotheses" in request.outputs:
        tasks.append(
            ResearchTask(
                order=len(tasks) + 1,
                agent="hypothesis-generator",
                objective="Draft falsifiable hypotheses without promoting them to findings.",
            )
        )
    return ResearchRunResponse(
        id=uuid4(),
        project_id=request.project_id,
        question=request.question,
        level=request.level,
        created_at=datetime.now(timezone.utc),  # noqa: UP017 - local Python 3.9 validation
        tasks=tuple(tasks),
        disclaimer=(
            "Planned computational research only. This run is not a clinical assessment or a "
            "validated scientific discovery."
        ),
    )
