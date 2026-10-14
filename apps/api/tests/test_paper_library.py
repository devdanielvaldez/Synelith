from datetime import datetime, timezone

import httpx
import pytest
from conftest import make_settings
from neurogenesis_api.database import Database
from neurogenesis_api.main import create_app
from neurogenesis_api.models import AuditEvent, Paper, Source
from neurogenesis_connectors.pubmed import (
    PubMedArticle,
    PubMedSearchResult,
    RetrievalProvenance,
)
from sqlalchemy import func, select


def pubmed_result(*, complete: bool = True) -> PubMedSearchResult:
    return PubMedSearchResult(
        total=1,
        returned=1,
        offset=0,
        articles=(
            PubMedArticle(
                pmid="39700001",
                title="APOE lipid states in human microglia",
                authors=("Ada Researcher", "Lin Scientist"),
                journal="Example Neuroscience",
                publication_date="2026 Oct",
                doi="HTTPS://DOI.ORG/10.1000/Example",
            ),
        ),
        provenance=RetrievalProvenance(
            query="APOE microglia",
            retrieved_at=datetime.now(timezone.utc),  # noqa: UP017 - Python 3.9 test runner
            provider_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            source_hash="sha256:retrieval",
            complete=complete,
        ),
    )


class FakePubMedClient:
    def __init__(self, result: PubMedSearchResult) -> None:
        self.result = result
        self.calls: list[tuple[str, int, int]] = []

    async def search(self, query: str, *, limit: int = 10, offset: int = 0) -> PubMedSearchResult:
        self.calls.append((query, limit, offset))
        return self.result


@pytest.mark.asyncio
async def test_pubmed_import_is_persistent_audited_and_idempotent(database: Database) -> None:
    app = create_app(make_settings(), database=database)
    fake = FakePubMedClient(pubmed_result())

    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
    ):
        app.state.pubmed = fake
        first = await client.post(
            "/v1/papers/import/pubmed", json={"query": "  APOE   microglia ", "limit": 6}
        )
        second = await client.post(
            "/v1/papers/import/pubmed", json={"query": "APOE microglia", "limit": 6}
        )
        library = await client.get("/v1/papers")
        paper = await client.get(f"/v1/papers/{first.json()['papers'][0]['id']}")

    assert first.status_code == 200
    assert first.json()["created"] == 1
    assert first.json()["existing"] == 0
    assert first.json()["library_total"] == 1
    assert first.json()["papers"][0]["doi"] == "10.1000/example"
    assert second.json()["created"] == 0
    assert second.json()["existing"] == 1
    assert len(library.json()) == 1
    assert paper.json() == library.json()[0]
    assert fake.calls == [("APOE microglia", 6, 0), ("APOE microglia", 6, 0)]

    async with database.sessions() as session:
        paper_count = await session.scalar(select(func.count()).select_from(Paper))
        source_count = await session.scalar(select(func.count()).select_from(Source))
        audit_count = await session.scalar(select(func.count()).select_from(AuditEvent))
    assert (paper_count, source_count, audit_count) == (1, 1, 1)


@pytest.mark.asyncio
async def test_incomplete_pubmed_result_is_not_imported(database: Database) -> None:
    app = create_app(make_settings(), database=database)

    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client,
    ):
        app.state.pubmed = FakePubMedClient(pubmed_result(complete=False))
        response = await client.post("/v1/papers/import/pubmed", json={"query": "APOE microglia"})

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "pubmed_incomplete_result"
    async with database.sessions() as session:
        paper_count = await session.scalar(select(func.count()).select_from(Paper))
    assert paper_count == 0
