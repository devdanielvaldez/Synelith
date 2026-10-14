from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from neurogenesis_connectors.pubmed import PubMedClient, PubMedUpstreamError
from sqlalchemy.ext.asyncio import AsyncSession

from neurogenesis_api.database import get_session
from neurogenesis_api.paper_library import get_paper, import_pubmed_result, list_papers
from neurogenesis_api.schemas import PaperResponse, PubMedImportRequest, PubMedImportResponse

router = APIRouter(prefix="/v1/papers", tags=["papers"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post("/import/pubmed", response_model=PubMedImportResponse)
async def import_pubmed_endpoint(
    payload: PubMedImportRequest, request: Request, session: Session
) -> PubMedImportResponse:
    pubmed = cast(PubMedClient, request.app.state.pubmed)
    try:
        result = await pubmed.search(payload.query, limit=payload.limit)
    except PubMedUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "pubmed_upstream_error",
                "message": "PubMed could not provide a complete, valid response.",
            },
        ) from exc
    if not result.provenance.complete:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "pubmed_incomplete_result",
                "message": "Incomplete PubMed results were not imported.",
            },
        )
    return await import_pubmed_result(session, result)


@router.get("", response_model=tuple[PaperResponse, ...])
async def list_papers_endpoint(session: Session) -> tuple[PaperResponse, ...]:
    return await list_papers(session)


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper_endpoint(paper_id: UUID, session: Session) -> PaperResponse:
    paper = await get_paper(session, paper_id)
    if paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    return paper
