from fastapi.testclient import TestClient
from neurogenesis_api.main import create_app
from neurogenesis_api.settings import Settings


def test_health_and_research_plan_are_explicit_about_status() -> None:
    app = create_app(
        Settings(
            environment="test",
            cors_origins=("http://localhost:3001",),
            ncbi_api_key=None,
            ncbi_email="test@example.org",
        )
    )

    with TestClient(app) as client:
        health_response = client.get("/health")
        run_response = client.post(
            "/v1/research-runs",
            json={
                "project_id": "project-demo",
                "question": "How do APOE-associated lipid states relate to microglial activation?",
                "outputs": ["evidence_matrix", "knowledge_graph", "hypotheses"],
            },
        )

    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"
    assert run_response.status_code == 201
    payload = run_response.json()
    assert payload["status"] == "planned"
    assert all(task["status"] == "pending" for task in payload["tasks"])
    assert "not a clinical assessment" in payload["disclaimer"]
