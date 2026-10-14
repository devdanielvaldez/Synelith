from fastapi import APIRouter, status

from neurogenesis_api.schemas import (
    ResearchRunRequest,
    ResearchRunResponse,
    plan_research_run,
)

router = APIRouter(prefix="/v1/research-runs", tags=["research-runs"])


@router.post("", response_model=ResearchRunResponse, status_code=status.HTTP_201_CREATED)
async def create_research_run(request: ResearchRunRequest) -> ResearchRunResponse:
    return plan_research_run(request)
