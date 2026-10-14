import httpx
import pytest
from conftest import make_settings
from neurogenesis_api.database import Database
from neurogenesis_api.main import create_app
from neurogenesis_api.models import AuditEvent
from sqlalchemy import func, select


@pytest.mark.asyncio
async def test_project_and_research_run_are_persisted_with_audit_events(
    database: Database,
) -> None:
    app = create_app(make_settings(), database=database)

    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
    ):
        health_response = await client.get("/health")
        project_response = await client.post(
            "/v1/projects",
            json={
                "name": "APOE and microglia",
                "disease_area": "Alzheimer's disease",
                "description": "Evidence synthesis for lipid-associated microglial states.",
            },
        )
        project = project_response.json()
        list_response = await client.get("/v1/projects")
        run_response = await client.post(
            "/v1/research-runs",
            json={
                "project_id": project["id"],
                "question": "How do APOE-associated lipid states relate to microglial activation?",
                "outputs": ["evidence_matrix", "knowledge_graph", "hypotheses"],
            },
        )
        run = run_response.json()
        persisted_run_response = await client.get(f"/v1/research-runs/{run['id']}")

    assert health_response.status_code == 200
    assert project_response.status_code == 201
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [project["id"]]
    assert run_response.status_code == 201
    assert run["status"] == "planned"
    assert all(task["status"] == "pending" for task in run["tasks"])
    assert "not a clinical assessment" in run["disclaimer"]
    assert persisted_run_response.status_code == 200
    assert persisted_run_response.json() == run

    async with database.sessions() as session:
        audit_count = await session.scalar(select(func.count()).select_from(AuditEvent))
    assert audit_count == 2


@pytest.mark.asyncio
async def test_research_run_requires_an_existing_project(database: Database) -> None:
    app = create_app(make_settings(), database=database)

    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
    ):
        response = await client.post(
            "/v1/research-runs",
            json={
                "project_id": "00000000-0000-0000-0000-000000000001",
                "question": "Does this project exist before planning the research run?",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
