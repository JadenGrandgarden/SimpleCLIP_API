from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List, Dict, Any, Optional

from app.core.container import Container
from app.core.middleware import inject
from app.services.image_services import ImageService
import os

router = APIRouter(
    prefix="/image",
    tags=["image"],
)


@router.get("/all")
@inject
def read_all_images(
    image: ImageService = Depends(Provide[Container.image_service]),
):
    """
    Retrieve all images from the database
    
    Args:
        limit: Maximum number of results to return
        
    Returns:
        List of images
    """
    print("Fetching all images")
    images = image.read_all_image()
    for img in images:
        if "image_path" in img:
            filename = os.path.basename(img["image_path"])
            img["image_url"] = f"/asset/{filename}"
    return images


@router.get("/{image_id}")
@inject
def read_image_by_id(
    image_id: str = Path(..., description="The ID of the image to retrieve"),
    image: ImageService = Depends(Provide[Container.image_service]),
):
    """
    Retrieve an image by its ID
    
    Args:
        image_id: The ID of the image to retrieve
        
    Returns:
        Image data if found
    """
    print(f"Fetching image with ID: {image_id}")
    image = image.read_by_id(image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.delete("/{image_id}")
@inject
def delete_image_by_id(
    image_id: str = Path(..., description="The ID of the image to delete"),
    image: ImageService = Depends(Provide[Container.image_service]),
):
    """
    Delete an image by its ID
    
    Args:
        image_id: The ID of the image to delete
        
    Returns:
        Confirmation message
    """
    # Check if image exists first
    img = image.read_by_id(image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete the image
    image.delete_by_id(image_id)
    return {"message": f"Image with ID {image_id} deleted successfully"}