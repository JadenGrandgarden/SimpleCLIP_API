from app.repository.text_repository import TextRepository
from app.repository.image_repository import ImageRepository
from app.utils.vectorize import resources
from app.utils.save_image import save_image
from app.core.config import configs
from typing import Dict, List, Any, Optional
from PIL import Image
import base64
import io


class UploadService:
    """
    Upload Service for Weaviate.
    This class handles the upload functionality for text and image data.
    """
    def __init__(self, text_repository: TextRepository, image_repository: ImageRepository) -> None:
        """Initialize the service with repositories."""
        self.text_repository = text_repository
        self.image_repository = image_repository
    
    def upload_text(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> Dict[str, str]:
        """
        Upload text data to the vector database.
        
        Args:
            texts: List of text strings to upload
            metadata: Optional list of metadata dictionaries for each text
            
        Returns:
            Dictionary with upload status message
        """
        if metadata is None:
            metadata = [{} for _ in texts]
        
        if len(texts) != len(metadata):
            raise ValueError("Length of texts and metadata must match")
        
        # Process and prepare text data
        text_data = []
        for i, text in enumerate(texts):
            # Get text vector embedding
            embedding = resources.encode_text(text)
            
            # Create text data entry
            text_item = {
                "text": text,
                "vector": embedding["vector"],
                "metadata": metadata[i]
            }
            text_data.append(text_item)
        
        # Upload to repository
        self.text_repository.update_text_data(text_data)
        
        return {"message": f"Successfully uploaded {len(texts)} text items"}
    
    def upload_image(self, images: List[Image.Image], 
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
        image_paths = save_image(images, metadata)
        # Turn images into base64 strings
        image_base64_list = []
        for image in images:
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            image_base64_list.append(image_base64)
        images = image_base64_list
        if metadata is None:
            metadata = [{} for _ in images]
        
        if len(images) != len(image_paths) or len(images) != len(metadata):
            raise ValueError("Length of images, image_paths, and metadata must match")
        
        # Process and prepare image data
        image_data = []
        for i, image in enumerate(images):
            # Get image vector embedding
            embedding = resources.encode_image(image)
            
            # Convert image to base64 for storage (optional)
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Create image data entry
            image_item = {
                "image_path": image_paths[i],
                "image_base64": image_base64,
                "vector": embedding["vector"],
                "metadata": metadata[i]
            }
            image_data.append(image_item)
        
        # Upload to repository
        self.image_repository.update_image_data(image_data)
        
        return {"message": f"Successfully uploaded {len(images)} image items"}