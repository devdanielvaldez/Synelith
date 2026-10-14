import httpx
import pytest
from neurogenesis_connectors.pubmed import (
    PubMedClient,
    PubMedClientSettings,
    PubMedUpstreamError,
)


async def no_sleep(_: float) -> None:
    return None


@pytest.mark.asyncio
async def test_search_normalizes_metadata_and_records_provenance() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("esearch.fcgi"):
            return httpx.Response(
                200,
                json={"esearchresult": {"count": "1", "idlist": ["12345"]}},
            )
        return httpx.Response(
            200,
            json={
                "result": {
                    "uids": ["12345"],
                    "12345": {
                        "title": "A source-grounded Alzheimer study",
                        "authors": [{"name": "Researcher A"}],
                        "fulljournalname": "Example Journal",
                        "pubdate": "2025",
                        "articleids": [{"idtype": "doi", "value": "10.0000/example"}],
                    },
                }
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
    ) as http_client:
        client = PubMedClient(
            http_client,
            PubMedClientSettings(max_requests_per_second=10, api_key="fixture-key"),
            sleep=no_sleep,
            jitter=lambda: 0,
        )
        result = await client.search("APOE microglia", limit=5)

    assert result.total == 1
    assert result.returned == 1
    assert result.articles[0].pmid == "12345"
    assert result.articles[0].doi == "10.0000/example"
    assert result.articles[0].source_access == "metadata_only"
    assert result.provenance.complete is True
    assert result.provenance.source_hash.startswith("sha256:")


@pytest.mark.asyncio
async def test_search_retries_rate_limit_then_succeeds() -> None:
    calls = 0
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"retry-after": "1"})
        return httpx.Response(200, json={"esearchresult": {"count": "0", "idlist": []}})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
    ) as http_client:
        client = PubMedClient(
            http_client,
            PubMedClientSettings(max_requests_per_second=10, api_key="fixture-key"),
            sleep=record_sleep,
            jitter=lambda: 0,
        )
        result = await client.search("tau")

    assert result.returned == 0
    assert calls == 2
    assert 1.0 in delays


@pytest.mark.asyncio
async def test_search_rejects_malformed_payload() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"esearchresult": {"count": "unknown", "idlist": []}})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
    ) as http_client:
        client = PubMedClient(
            http_client,
            PubMedClientSettings(max_requests_per_second=10, api_key="fixture-key"),
            sleep=no_sleep,
        )
        with pytest.raises(PubMedUpstreamError):
            await client.search("amyloid")
