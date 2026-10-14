from fastapi import APIRouter

from neurogenesis_api.schemas import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()
