from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from typing import List, Optional
import io
from PIL import Image
import os
import base64
from app.schemas.schemas import TextSearchResponse, ImageRequest, TextRequest
from fastapi.responses import FileResponse
from app.core.container import Container
from app.core.middleware import inject
from app.services.image_services import ImageService
from app.services.text_services import TextService
from app.core.config import configs as CFG

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
    image_urls = []
    for path in image_paths:
        filename = os.path.basename(path)
        # Create a URL using the /assets/ endpoint
        image_url = f"/asset/{filename}"
        image_urls.append(image_url)

    return {"image_urls": image_urls}


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
    try:
        # Read the uploaded image
        content = await file.read()

        # Process the image
        image = Image.open(io.BytesIO(content)).convert("RGB")

        # Create a temporary file with proper extension
        temp_file_path = os.path.join(
            CFG.TEMP_DIR, f"temp_image_{os.urandom(8).hex()}.jpg"
        )

        # Save the processed image to temporary location
        os.makedirs(CFG.TEMP_DIR, exist_ok=True)
        image.save(temp_file_path)

        # Call service to perform the search
        results = service.search_by_image(image_filename=temp_file_path, limit=limit)

        # Extract text results
        text_results = []
        for obj in results.objects:
            if obj.properties.get("text"):
                text_results.append(obj.properties["text"])

        return TextSearchResponse(text=text_results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    finally:
        # Ensure temporary file is removed even if an error occurs
        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Failed to remove temporary file: {str(e)}")
