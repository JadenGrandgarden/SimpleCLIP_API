from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import List, Optional
import io
from PIL import Image
import base64
from app.schemas.schemas import ImageSearchResponse, TextSearchResponse, ImageRequest, TextRequest

from app.core.container import Container
from app.core.middleware import inject
from app.services.image_services import ImageService
from app.services.text_services import TextService

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.get("/text", response_model=TextSearchResponse)
@inject
def search_by_text(
    query: TextRequest,
    limit: int = Query(5, ge=1, le=100),
    service: TextService = Depends(Provide[Container.search_service]),
):
    """
    Search for images using a text query
    
    Args:
        query: Text to search with
        limit: Maximum number of results to return
        
    Returns:
        List of matching image results
    """
    return service.search_by_text(text=query, limit=limit)


@router.post("/image", response_model=ImageSearchResponse)
@inject
async def search_by_image(
    file: ImageRequest = File(...),
    limit: int = Query(5, ge=1, le=100),
    service: ImageService = Depends(Provide[Container.search_service]),
):
    """
    Search for text using an image query
    
    Args:
        file: Image file to search with
        limit: Maximum number of results to return
        
    Returns:
        List of matching text results
    """
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert('RGB')
    
    return service.search_by_image(image=image, limit=limit)