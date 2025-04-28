from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import List, Optional
import io
from PIL import Image
import base64
from app.schemas.schemas import TextSearchResponse, ImageRequest, TextRequest
from fastapi.responses import FileResponse
from app.core.container import Container
from app.core.middleware import inject
from app.services.image_services import ImageService
from app.services.text_services import TextService

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.get("/text")
@inject
def search_by_text(
    query: TextRequest,
    limit: int = Query(5, ge=1, le=100),
    service: TextService = Depends(Provide[Container.text_service]),
):
    """
    Search for images using a text query
    
    Args:
        query: Text to search with
        limit: Maximum number of results to return
        
    Returns:
        List of matching image results
    """
    image_paths = service.search_by_text(text=query, limit=limit)
    
    # Create FileResponse objects here if you need to return the actual files
    response_files = []
    for path in image_paths:
        response_files.append(FileResponse(path, media_type="image/jpeg"))
    print(response_files)
    # Otherwise return list of paths that can be requested individually
    return {"response_files": response_files}


@router.post("/image", response_model=TextSearchResponse)
@inject
async def search_by_image(
    file: ImageRequest = File(...),
    limit: int = Query(5, ge=1, le=100),
    service: ImageService = Depends(Provide[Container.image_service]),
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
    
    results = service.search_by_image(image=image, limit=limit)
    
    
    text_results = []
    for obj in results.objects:
        if obj.properties.get("text"):
            text_results.append(obj.properties["text"])
    return TextSearchResponse(text=text_results)

