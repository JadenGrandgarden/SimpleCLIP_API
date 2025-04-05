from fastapi import APIRouter
from app.api.endpoints.health import router as health_router
from app.api.endpoints.search import router as search_router
from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.image import router as image_router

# Create main API router
api_router = APIRouter()

router_list = [
    health_router,
    search_router,
    upload_router,
    image_router
]

for router in router_list:
    api_router.include_router(router)