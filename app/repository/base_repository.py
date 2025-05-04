import weaviate 
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeVar, Union
from app.core.config import configs 
from weaviate.classes.query import Filter
from tqdm import tqdm
import uuid
import time
import grpc
class BaseRepository(Protocol):
    """
    Protocol for Base Repository.
    This defines the methods that any repository should implement.
    """
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    BACKOFF_FACTOR = 2  # exponential backoff factor
    def __init__(self, session_factory: Callable[..., AbstractContextManager[weaviate.Client]]) -> None:
        """Initialize the repository with a Weaviate client."""
        self.session_factory = session_factory
        self._current_client = None
    def _execute_with_retry(self, operation_func):
        """Execute an operation with retry logic."""
        retries = 0
        last_exception = None
        current_delay = self.RETRY_DELAY
        
        while retries < self.MAX_RETRIES:
            try:
                with self.session_factory() as client:
                    self._current_client = client
                    result = operation_func(client)
                    return result
            except weaviate.exceptions.WeaviateClosedClientError as e:
                retries += 1
                last_exception = e
                print(f"Connection error, retrying {retries}/{self.MAX_RETRIES}...")
                time.sleep(self.RETRY_DELAY)
                current_delay *= self.BACKOFF_FACTOR
            except weaviate.exceptions.WeaviateQueryError as e:
                if "Channel closed" in str(e):
                    retries += 1
                    last_exception = e
                    print(f"gRPC channel closed error, retrying {retries}/{self.MAX_RETRIES}...")
                    time.sleep(current_delay)
                    current_delay *= self.BACKOFF_FACTOR
                else:
                    print(f"Weaviate query error: {e}")
                    raise
                    
            except grpc.RpcError as e:
                retries += 1
                last_exception = e
                print(f"gRPC error: {e.details() if hasattr(e, 'details') else str(e)}, retrying {retries}/{self.MAX_RETRIES}...")
                time.sleep(current_delay)
                current_delay *= self.BACKOFF_FACTOR
                
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise
            finally:
                self._close_client()
        
        print(f"Failed after {self.MAX_RETRIES} retries: {last_exception}")
        raise last_exception
    
    def _close_client(self) -> None:
        """Close the Weaviate client connection."""
        if self._current_client:
            try:
                if hasattr(self._current_client, 'close'):
                    self._current_client.close()
            except Exception as e:
                print(f"Error closing client: {e}")
            finally:
                self._current_client = None
        
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
                    print("File UUID: ", item.get("id", str(uuid.uuid5(uuid.NAMESPACE_DNS, item["image_path"].split("/")[-1]))))
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
        def operation(client):
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            entity = collection.query.fetch_object_by_id(id)
            # print(entity.properties)
            return entity.properties if entity else None
        return self._execute_with_retry(operation)
        
    def read_all(self) -> List[Dict[str, Any]]:
        """Read all entities."""
        def operation(client):
            entities = []
            collection = client.collections.get(configs.WEAVIATE_COLLECTION_NAME)
            print("Fetching all entities...")
            results = collection.query.fetch_objects(limit=1000).objects
            print(f"Fetched {len(results)} entities.")
            for item in results:
                entities.append(item.properties)
            return entities if entities else []
        return self._execute_with_retry(operation)
        
    def read_by_vector(self, search_vector: List[float], type_filter: str, limit: int = 10) -> List[Dict[str, Any]]:
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
            collection.data.delete_by_id(id)
            print(f"Deleted entity with ID: {id}")
            
    def close_scoped_session(self) -> None:
        """Properly close the Weaviate client connection."""
        self._close_client()
        

        