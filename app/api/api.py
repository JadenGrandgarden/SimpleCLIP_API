from fastapi import APIRouter
from app.api.endpoints import vectorize, health, ui

# Create main API router
api_router = APIRouter()

# Include the vectorize endpoints
api_router.include_router(
    vectorize.router,
    prefix="/vectorize",
    tags=["vectorize"]
)

# Include the health check endpoints
api_router.include_router(
    health.router,
    tags=["health"]
)

# Include the UI endpoints
api_router.include_router(
    ui.router,
    tags=["ui"]
)