from typing import List, Optional
from pathlib import Path
from app.repository.text_repository import TextRepository
from app.services.weavite__service import BaseService
from app.utils.vectorize import resources
from typing import Dict, Any
from datetime import datetime

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
        
        for item in metadata:
            # Add created_at timestamp to each metadata item
            item['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        """
        # Get text vector embedding
        text_vector = resources.encode_text(text)["vector"]
        
        # Get raw results from repository
        raw_results = self.text_repository.read_by_vector(
            search_vector=text_vector,
            type_filter="Image",
            limit=limit
        )
        
        image_paths = []
        for result in raw_results.objects:
            if result.properties.get("image_path"):
                image_path = Path(result.properties["image_path"])
                if image_path.exists():
                    image_paths.append(str(image_path))
                else:
                    print(f"Warning: Image file not found: {image_path}")

        return image_paths
            