from fastapi import APIRouter
from loguru import logger
from app.schemas.schemas import HealthResponse

router = APIRouter(
    tags=["health"]
)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    logger.info("Health check endpoint called")
    return HealthResponse(status="ok")