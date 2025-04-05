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

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)


@router.post("/text", response_model=UploadResponse)
@inject
def upload_text(
    texts: TextRequest,
    metadata: Optional[List[Dict[str, Any]]] = None,
    service: TextService = Depends(Provide[Container.upload_service])
):
    """Upload text data to the vector database"""
    return service.upload_text(texts, metadata)


@router.post("/image", response_model=UploadResponse)
@inject
async def upload_image(
    files: ImageRequest = File(...),
    metadata_json: str = Form(None),
    service: ImageService = Depends(Provide[Container.upload_service])
):
    """Upload image files to the vector database"""
    metadata = json.loads(metadata_json) if metadata_json else None
    
    # Process uploaded images
    images = []
    for file in files:
        content = await file.read()
        img = Image.open(io.BytesIO(content)).convert('RGB')
        images.append(img)
    
    return service.upload_image(images, metadata)