from typing import Annotated, cast

from fastapi import APIRouter, HTTPException, Query, Request, status
from neurogenesis_connectors.pubmed import PubMedClient, PubMedSearchResult, PubMedUpstreamError

router = APIRouter(prefix="/v1/literature", tags=["literature"])


@router.get("/search", response_model=PubMedSearchResult)
async def search_literature(
    request: Request,
    q: Annotated[str, Query(min_length=2, max_length=500)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PubMedSearchResult:
    pubmed = cast(PubMedClient, request.app.state.pubmed)
    try:
        return await pubmed.search(q, limit=limit, offset=offset)
    except PubMedUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "pubmed_upstream_error",
                "message": "PubMed could not provide a complete, valid response.",
            },
        ) from exc
