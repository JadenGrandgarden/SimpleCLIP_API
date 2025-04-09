import weaviate 
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeVar, Union
from app.core.config import configs 
from weaviate.classes.query import Filter
from tqdm import tqdm
import uuid

class BaseRepository(Protocol):
    """
    Protocol for Base Repository.
    This defines the methods that any repository should implement.
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[weaviate.Client]]) -> None:
        """Initialize the repository with a Weaviate client."""
        self.session_factory = session_factory
        
    def update_image_data(self, image_data: List[Dict[str, Any]]) -> None:
        """Update image data for an entity."""
        """
        Import only image data into collection.
        
        image_data should be a list of dictionaries with:
        - id: string (optional unique identifier to link with captions later)
        - image_path: string 
        - vector: list of floats
        - image_base64: base64 encoded image (optional)
        - metadata: dict (optional)
        
        Returns a list of UUIDs for the imported objects.
        """
        
        # Generate UUIDs for each image from image file name


        with self.session_factory() as client:
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            with collection.batch.dynamic() as batch:
                for item in tqdm(image_data, desc="Uploading images"):
                    print(item['image_path'])
                    properties = {
                        "image_path": item["image_path"],
                        # "image_base64": item.get("image_base64", None),  # Optional base64 image
                        "Type": "Image",
                        "metadata": item.get("metadata", {}),
                    }
                    batch.add_object(
                        properties=properties,
                        vector=item["vector"],
                        uuid=item.get("id", str(uuid.uuid5(uuid.NAMESPACE_DNS, item["image_path"].split("/")[-1]))),  # Optional UUID
                    )
    
    def update_text_data(self, text_data: List[Dict[str, Any]]) -> None:
        """Update text data for an entity."""
        """
        Import only text data into collection.
        
        text_data should be a list of dictionaries with:
        - id: string (optional unique identifier to link with images later)
        - text: string 
        - vector: list of floats
        - metadata: dict (optional)
        
        Returns a list of UUIDs for the imported objects.
        """
        
        with self.session_factory() as client:
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            with collection.batch.dynamic() as batch:
                for item in tqdm(text_data, desc="Uploading texts"):
                    properties = {
                        "text": item["text"],
                        "Type": "Text",
                        "metadata": item.get("metadata", {}),
                    }
                    batch.add_object(
                        properties=properties,
                        vector=item["vector"],
                        uuid=item.get("id", str(uuid.uuid5(uuid.NAMESPACE_DNS, item["text"]))),  # Optional UUID
                    )
    def read_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Read an entity by its ID."""
        with self.session_factory() as client:
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            entity = collection.query.fetch_object_by_id(id)
            print(entity.properties)
            return entity.properties if entity else None
        
    def read_all(self) -> List[Dict[str, Any]]:
        """Read all entities."""
        entities = []
        with self.session_factory() as client:
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            print("Fetching all entities...")
            results = collection.query.fetch_objects(limit=1000).objects
            print(f"Fetched {len(results)} entities.")
            for item in results:
                entities.append(item.properties)
            return entities if entities else []
        
    def read_by_vector(self, search_vector: List[float], type_filter: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Read entities by vector."""
        with self.session_factory() as client:
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            entities = collection.query.near_vector(
            near_vector=search_vector,
            filters = Filter.by_property("type").equal(type_filter),
            limit=limit
            )
            return entities if entities else []
        
    def delete_by_id(self, id: str) -> None:
        """Delete an entity by its ID."""
        with self.session_factory() as client:
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            collection.data.delete(id).do()
            print(f"Deleted entity with ID: {id}")
            
    def close_scoped_session(self):
        with self.session_factory() as client:
            return client.close() 
        

        