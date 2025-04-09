from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List, Dict, Any, Optional
import json
from PIL import Image
import io
from app.schemas.schemas import UploadResponse, TextRequest, ImageRequest
from app.core.container import Container
from app.core.middleware import inject
from app.services.image_services import ImageService
from app.services.text_services import TextService
from fastapi import HTTPException


router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)


@router.post("/text", response_model=UploadResponse)
@inject
def upload_text(
    request_data: Dict[str, Any],
    service: TextService = Depends(Provide[Container.text_service])
):
    """Upload text data to the vector database"""
    metadata = request_data.get("metadata", None)
    texts = request_data.get("texts", None)
    
    print(f"Received metadata: {metadata}")
    print(f"Received texts: {texts}")
    return service.upload_text(texts, metadata)


@router.post("/image")
@inject
async def upload_image(
    metadata_json: str = Form(None),
    file: UploadFile = File(...),
    service: ImageService = Depends(Provide[Container.image_service])
):
    """Upload image files to the vector database"""
    
    try:
        
        # Process single uploaded image
        content = await file.read()
        # Parse metadata
        metadata = json.loads(metadata_json) if metadata_json else None
        img = Image.open(io.BytesIO(content)).convert('RGB')
        images = [img]  # Create a list with the single image
        images_filename = [file.filename]
        
        print(f"Processed image: {file.filename}, size: {img.size}")
        
        # Call service with single image in a list
        response = service.upload_image(images,images_filename, metadata)
        if not isinstance(response, dict):
            return {"message": "Image uploaded successfully"}
        return response
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")