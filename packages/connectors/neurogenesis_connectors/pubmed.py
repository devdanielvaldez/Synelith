"""Resilient, metadata-only PubMed connector backed by NCBI E-utilities."""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

Sleep = Callable[[float], Awaitable[None]]


class PubMedClientSettings(BaseModel):
    """Runtime settings aligned with the NCBI E-utilities usage policy."""

    model_config = ConfigDict(frozen=True)

    base_url: HttpUrl = HttpUrl("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/")
    tool: str = "neurogenesis_ai"
    email: str = "developers@neurogenesis.ai"
    api_key: str | None = None
    timeout_seconds: float = Field(default=10.0, gt=0, le=60)
    max_retries: int = Field(default=3, ge=0, le=5)
    max_requests_per_second: float | None = Field(default=None, gt=0, le=10)

    @property
    def effective_rate(self) -> float:
        policy_limit = 10.0 if self.api_key else 3.0
        return min(self.max_requests_per_second or policy_limit, policy_limit)


class PubMedArticle(BaseModel):
    model_config = ConfigDict(frozen=True)

    pmid: str
    title: str
    authors: tuple[str, ...] = ()
    journal: str | None = None
    publication_date: str | None = None
    doi: str | None = None
    source_access: Literal["metadata_only"] = "metadata_only"


class RetrievalProvenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: Literal["NCBI PubMed"] = "NCBI PubMed"
    database: Literal["pubmed"] = "pubmed"
    query: str
    retrieved_at: datetime
    provider_url: str
    schema_version: Literal["pubmed-search/v1"] = "pubmed-search/v1"
    source_hash: str
    complete: bool
    content_trust: Literal["untrusted_source_metadata"] = "untrusted_source_metadata"


class PubMedSearchResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    total: int
    returned: int
    offset: int
    articles: tuple[PubMedArticle, ...]
    provenance: RetrievalProvenance


class PubMedUpstreamError(RuntimeError):
    """Raised when NCBI cannot provide a complete, valid response."""


class _RateLimiter:
    def __init__(self, requests_per_second: float, sleep: Sleep) -> None:
        self._minimum_interval = 1 / requests_per_second
        self._sleep = sleep
        self._lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            delay = self._minimum_interval - (now - self._last_request_at)
            if delay > 0:
                await self._sleep(delay)
            self._last_request_at = time.monotonic()


class PubMedClient:
    """Search PubMed and normalize ESearch/ESummary responses."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        settings: PubMedClientSettings,
        *,
        sleep: Sleep = asyncio.sleep,
        jitter: Callable[[], float] = random.random,
    ) -> None:
        self._http = http_client
        self._settings = settings
        self._sleep = sleep
        self._jitter = jitter
        self._limiter = _RateLimiter(settings.effective_rate, sleep)

    async def search(self, query: str, *, limit: int = 10, offset: int = 0) -> PubMedSearchResult:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must not be empty")
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        if offset < 0:
            raise ValueError("offset must be non-negative")

        search_payload = await self._request_json(
            "esearch.fcgi",
            {
                "db": "pubmed",
                "term": normalized_query,
                "retmode": "json",
                "retmax": str(limit),
                "retstart": str(offset),
                "sort": "pub date",
            },
        )
        search_result = _mapping(search_payload.get("esearchresult"), "esearchresult")
        ids = _string_list(search_result.get("idlist"), "esearchresult.idlist")
        total = _integer(search_result.get("count"), "esearchresult.count")

        summary_payload: dict[str, Any] = {"result": {"uids": []}}
        if ids:
            summary_payload = await self._request_json(
                "esummary.fcgi",
                {
                    "db": "pubmed",
                    "id": ",".join(ids),
                    "retmode": "json",
                    "version": "2.0",
                },
            )

        articles = _parse_summaries(summary_payload, ids)
        raw_hash = hashlib.sha256(
            json.dumps(
                {"search": search_payload, "summary": summary_payload},
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()

        return PubMedSearchResult(
            total=total,
            returned=len(articles),
            offset=offset,
            articles=tuple(articles),
            provenance=RetrievalProvenance(
                query=normalized_query,
                retrieved_at=datetime.now(timezone.utc),  # noqa: UP017 - local Python 3.9 validation
                provider_url=str(self._settings.base_url),
                source_hash=f"sha256:{raw_hash}",
                complete=len(articles) == len(ids),
            ),
        )

    async def _request_json(self, endpoint: str, parameters: dict[str, str]) -> dict[str, Any]:
        params = {
            **parameters,
            "tool": self._settings.tool,
            "email": self._settings.email,
        }
        if self._settings.api_key:
            params["api_key"] = self._settings.api_key

        for attempt in range(self._settings.max_retries + 1):
            await self._limiter.wait()
            try:
                response = await self._http.get(
                    endpoint,
                    params=params,
                    timeout=self._settings.timeout_seconds,
                )
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt == self._settings.max_retries:
                    raise PubMedUpstreamError("NCBI request failed after retry exhaustion") from exc
                await self._backoff(attempt, None)
                continue

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == self._settings.max_retries:
                    raise PubMedUpstreamError(
                        f"NCBI returned retryable status {response.status_code} after retry exhaustion"
                    )
                await self._backoff(attempt, response.headers.get("retry-after"))
                continue

            try:
                response.raise_for_status()
                payload = response.json()
            except (httpx.HTTPStatusError, ValueError) as exc:
                raise PubMedUpstreamError(
                    "NCBI returned an invalid or unsuccessful response"
                ) from exc
            if not isinstance(payload, dict):
                raise PubMedUpstreamError("NCBI returned a non-object JSON payload")
            return payload

        raise AssertionError("retry loop ended unexpectedly")

    async def _backoff(self, attempt: int, retry_after: str | None) -> None:
        if retry_after:
            try:
                delay = min(float(retry_after), 30.0)
            except ValueError:
                delay = 0.0
        else:
            delay = 0.0
        if delay <= 0:
            delay = min((2**attempt) + self._jitter(), 30.0)
        await self._sleep(delay)


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PubMedUpstreamError(f"NCBI payload field {field} is not an object")
    return value


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise PubMedUpstreamError(f"NCBI payload field {field} is not a string list")
    return value


def _integer(value: object, field: str) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError) as exc:
        raise PubMedUpstreamError(f"NCBI payload field {field} is not an integer") from exc


def _parse_summaries(payload: dict[str, Any], expected_ids: list[str]) -> list[PubMedArticle]:
    result = _mapping(payload.get("result"), "result")
    articles: list[PubMedArticle] = []
    for pmid in expected_ids:
        raw = _mapping(result.get(pmid), f"result.{pmid}")
        raw_authors = raw.get("authors", [])
        if not isinstance(raw_authors, list):
            raise PubMedUpstreamError(f"NCBI payload field result.{pmid}.authors is not a list")
        authors = tuple(
            str(author.get("name", "")).strip()
            for author in raw_authors
            if isinstance(author, dict) and str(author.get("name", "")).strip()
        )
        article_ids = raw.get("articleids", [])
        if not isinstance(article_ids, list):
            raise PubMedUpstreamError(f"NCBI payload field result.{pmid}.articleids is not a list")
        doi = next(
            (
                str(identifier.get("value"))
                for identifier in article_ids
                if isinstance(identifier, dict)
                and identifier.get("idtype") == "doi"
                and identifier.get("value")
            ),
            None,
        )
        title = str(raw.get("title", "")).strip()
        if not title:
            raise PubMedUpstreamError(f"NCBI payload field result.{pmid}.title is empty")
        articles.append(
            PubMedArticle(
                pmid=pmid,
                title=title,
                authors=authors,
                journal=_optional_string(raw.get("fulljournalname") or raw.get("source")),
                publication_date=_optional_string(raw.get("pubdate")),
                doi=doi,
            )
        )
    return articles


def _optional_string(value: object) -> str | None:
    normalized = str(value).strip() if value is not None else ""
    return normalized or None
