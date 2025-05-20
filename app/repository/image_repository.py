import weaviate 
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeVar, Union
from app.core.config import configs 
from app.repository.base_repository import BaseRepository

class ImageRepository(BaseRepository):
    """
    Image Repository for Weaviate.
    This class handles the interaction with Weaviate for image data.
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[weaviate.Client]]) -> None:
        """Initialize the repository with a Weaviate client."""
        self.session_factory = session_factory
        super().__init__(session_factory)
        
    def read_all_image(self):
        """Read all image data from Weaviate."""
        try:
            with self.session_factory() as client:
                collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
                results = collection.query.fetch_objects(
                    limit=10000,
                    filters=weaviate.classes.query.Filter.by_property("type").equal("Image")
                ).objects
                
                print(f"Found {len(results)} image objects")
                
                images = []
                for obj in results:
                    if obj.properties:
                        images.append(obj.properties)
                
                return images
        except Exception as e:
            print(f"Error retrieving all images: {e}")
            return []