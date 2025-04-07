import os
import logging
from typing import List, Optional
from PIL import Image
from pathlib import Path
from app.core.config import configs
from app.repository.text_repository import TextRepository
from app.services.weavite__service import BaseService
from app.utils.vectorize import resources
from app.utils.save_image import save_image
from typing import Dict, Any
import base64
import io

class TextService(BaseService):
    """Service for handling text operations in the repository."""
    
    def __init__(self, text_repository: TextRepository) -> None:
        """Initialize the service with the text repository."""
        self.text_repository = text_repository
        super().__init__(text_repository)
    
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
    
    def search_by_text(self, text: str, limit: int = 5):
        """
        Search for images using text query.
        
        Args:
            text: The text query to search with
            limit: Maximum number of results to return
            
        Returns:
            List of search results
        """
        # Get text vector embedding
        text_vector = resources.encode_text(text)["vector"]
        
        # Search in image repository using the text vector
        return self.text_repository.read_by_vector(
            search_vector=text_vector,
            type_filter="Image",
            limit=limit
        )