from app.repository.text_repository import TextRepository
from app.repository.image_repository import ImageRepository
from app.utils.vectorize import resources
from app.core.config import configs


class SearchService:
    """
    Search Service for Weaviate.
    This class handles the search functionality for text and image data.
    """
    def __init__(self, text_repository: TextRepository, image_repository: ImageRepository) -> None:
        """Initialize the service with repositories."""
        self.text_repository = text_repository
        self.image_repository = image_repository
    
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
        print(f"Text vector: {text_vector}")
        
        # Search in image repository using the text vector
        return self.image_repository.read_by_vector(
            search_vector=text_vector,
            type_filter="Image",
            limit=limit
        )
    
    def search_by_image(self, image, limit: int = 5):
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
        return self.text_repository.read_by_vector(
            search_vector=image_vector,
            type_filter="Text",
            limit=limit
        )