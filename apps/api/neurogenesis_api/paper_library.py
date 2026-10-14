"""Transactional ingestion and reads for the bibliographic paper library."""

from __future__ import annotations

import hashlib
import json
from uuid import UUID

from neurogenesis_connectors.pubmed import PubMedArticle, PubMedSearchResult
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from neurogenesis_api import models
from neurogenesis_api.schemas import PaperResponse, PubMedImportResponse


async def import_pubmed_result(
    session: AsyncSession, result: PubMedSearchResult
) -> PubMedImportResponse:
    """Persist one complete PubMed result without mutating prior source snapshots."""
    if not result.provenance.complete:
        raise ValueError("incomplete PubMed results cannot be imported")

    papers: list[PaperResponse] = []
    created = 0
    for article in result.articles:
        normalized_doi = _normalize_doi(article.doi)
        conditions = [models.Paper.pmid == article.pmid]
        if normalized_doi:
            conditions.append(models.Paper.doi == normalized_doi)
        existing_row = (
            await session.execute(
                select(models.Paper, models.Source)
                .join(models.Source, models.Source.id == models.Paper.source_id)
                .where(or_(*conditions))
            )
        ).first()
        if existing_row:
            papers.append(_paper_response(*existing_row))
            continue

        source = models.Source(
            provider="NCBI PubMed",
            external_id=article.pmid,
            source_type="bibliographic_metadata",
            url=f"https://pubmed.ncbi.nlm.nih.gov/{article.pmid}/",
            license="NCBI terms; linked article rights may vary",
            access_level="metadata_only",
            source_hash=_article_hash(article),
            retrieved_at=result.provenance.retrieved_at,
            source_metadata={
                "query": result.provenance.query,
                "schema_version": result.provenance.schema_version,
                "content_trust": result.provenance.content_trust,
                "authors": list(article.authors),
                "journal": article.journal,
            },
        )
        session.add(source)
        await session.flush()
        paper = models.Paper(
            source_id=source.id,
            title=article.title,
            doi=normalized_doi,
            pmid=article.pmid,
            publication_date=article.publication_date,
            review_status="unreviewed",
        )
        session.add(paper)
        await session.flush()
        session.add(
            models.AuditEvent(
                action="paper.imported",
                entity_type="paper",
                entity_id=paper.id,
                actor_type="user",
                event_data={
                    "provider": source.provider,
                    "pmid": article.pmid,
                    "source_hash": source.source_hash,
                    "source_access": source.access_level,
                },
            )
        )
        papers.append(_paper_response(paper, source))
        created += 1

    library_total = await session.scalar(select(func.count()).select_from(models.Paper))
    await session.commit()
    return PubMedImportResponse(
        query=result.provenance.query,
        retrieved=result.returned,
        created=created,
        existing=len(papers) - created,
        library_total=library_total or 0,
        papers=tuple(papers),
    )


async def list_papers(session: AsyncSession) -> tuple[PaperResponse, ...]:
    rows = await session.execute(
        select(models.Paper, models.Source)
        .join(models.Source, models.Source.id == models.Paper.source_id)
        .order_by(models.Paper.created_at.desc())
    )
    return tuple(_paper_response(paper, source) for paper, source in rows)


async def get_paper(session: AsyncSession, paper_id: UUID) -> PaperResponse | None:
    row = (
        await session.execute(
            select(models.Paper, models.Source)
            .join(models.Source, models.Source.id == models.Paper.source_id)
            .where(models.Paper.id == paper_id)
        )
    ).first()
    return _paper_response(*row) if row else None


def _normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    normalized = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if normalized.startswith(prefix):
            normalized = normalized.removeprefix(prefix).strip()
    return normalized or None


def _article_hash(article: PubMedArticle) -> str:
    serialized = json.dumps(
        article.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    ).encode()
    return f"sha256:{hashlib.sha256(serialized).hexdigest()}"


def _paper_response(paper: models.Paper, source: models.Source) -> PaperResponse:
    return PaperResponse(
        id=paper.id,
        title=paper.title,
        doi=paper.doi,
        pmid=paper.pmid,
        publication_date=paper.publication_date,
        review_status="unreviewed",
        source_id=source.id,
        source_access="metadata_only",
        source_hash=source.source_hash,
        created_at=paper.created_at,
    )
