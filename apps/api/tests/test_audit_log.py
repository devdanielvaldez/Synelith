import httpx
import pytest
from conftest import make_settings
from neurogenesis_api.database import Database
from neurogenesis_api.main import create_app


@pytest.mark.asyncio
async def test_audit_events_are_listed_newest_first_and_can_be_filtered(
    database: Database,
) -> None:
    app = create_app(make_settings(), database=database)

    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
    ):
        first_project = await client.post(
            "/v1/projects",
            json={"name": "First project", "disease_area": "Alzheimer's disease"},
        )
        second_project = await client.post(
            "/v1/projects",
            json={"name": "Second project", "disease_area": "Alzheimer's disease"},
        )
        run = await client.post(
            "/v1/research-runs",
            json={
                "project_id": second_project.json()["id"],
                "question": "Which evidence should this research plan retrieve first?",
            },
        )
        all_events = await client.get("/v1/audit/events", params={"limit": 2})
        project_events = await client.get("/v1/audit/events", params={"entity_type": "project"})
        run_events = await client.get("/v1/audit/events", params={"action": "research_run.planned"})

    assert first_project.status_code == 201
    assert run.status_code == 201
    assert all_events.status_code == 200
    assert len(all_events.json()) == 2
    assert all_events.json()[0]["entity_id"] == run.json()["id"]
    assert [event["action"] for event in project_events.json()] == [
        "project.created",
        "project.created",
    ]
    assert len(run_events.json()) == 1
    assert run_events.json()[0]["event_data"]["task_count"] == 3


@pytest.mark.asyncio
async def test_audit_event_query_limits_are_validated(database: Database) -> None:
    app = create_app(make_settings(), database=database)

    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
    ):
        response = await client.get("/v1/audit/events", params={"limit": 101})

    assert response.status_code == 422
