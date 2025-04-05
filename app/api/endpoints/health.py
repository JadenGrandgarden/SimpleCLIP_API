from fastapi import APIRouter
from app.schemas.schemas import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")