import os
import logging
from typing import List, Optional
from PIL import Image
from pathlib import Path
from app.core.config import configs
from app.repository.image_repository import ImageRepository
from app.services.weavite__service import BaseService
from app.utils.vectorize import resources
from app.utils.save_image import save_image
from typing import Dict, Any
import base64
import io
from datetime import datetime

class ImageService(BaseService):
    """Service for handling image operations in the repository."""
    
    def __init__(self, image_repository: ImageRepository) -> None:
        """Initialize the service with the image repository."""
        self.image_repository = image_repository
        super().__init__(image_repository)
        
    def read_all_image(self) -> List[Dict[str, Any]]:
        """Read all image data from the repository."""
        all_images = self.image_repository.read_all_image()
        return all_images
    
    def upload_image(self, images: List[Image.Image], images_filename: List[str],
                    metadata: Optional[List[Dict[str, Any]]] = None) -> Dict[str, str]:
        """
        Upload image data to the vector database.
        
        Args:
            images: List of PIL Image objects to upload
            metadata: Optional list of metadata dictionaries for each image
        Returns:
            Dictionary with upload status message
        """
        # Save images to local storage
        image_paths = save_image(images, images_filename, metadata)
        
        if metadata is None:
            metadata = [{} for _ in images]
        for item in metadata:
            # Add created_at timestamp to each metadata item
            item['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        if len(images) != len(image_paths) or len(images) != len(metadata):
            raise ValueError("Length of images, image_paths, and metadata must match")
        
        image_data = []
        
        for i, image in enumerate(images):
            # Get image vector embedding
            embedding = resources.encode_image(image)
            # Create image data entry
            image_item = {
                "image_path": image_paths[i],
                "vector": embedding["vector"],
                "metadata": metadata[i]
            }
            image_data.append(image_item)
        
        self.image_repository.update_image_data(image_data)
        return {"message": f"Successfully uploaded {len(images)} image items"}
    
    def search_by_image(self, image: Image.Image, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for text using image query.
        
        Args:
            image: The image to search with (PIL Image)
            limit: Maximum number of results to return
            
        Returns:
            List of search results
        """
        # Get image vector embedding
        image_vector = resources.encode_image(image)["vector"]
        
        # Search in text repository using the image vector
        return self.image_repository.read_by_vector(
            search_vector=image_vector,
            type_filter="Text",
            limit=limit
        )