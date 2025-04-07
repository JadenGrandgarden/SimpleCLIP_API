from typing import Any, Protocol


class Repository(Protocol):
    """
    Repository Protocol for Weaviate.
    This defines the methods that any repository should implement.
    """
    
    def read_by_vector(self, search_vector: list[float], type_filter: str, limit: int) -> list[dict[str, Any]]:
        """Read data by vector."""
        pass
    
    def read_by_id(self, id: str) -> dict[str, Any]:
        """Read an entity by its ID."""
        pass
    
    def read_all(self) -> list[dict[str, Any]]:
        """Read all entities."""
        pass
    
    def delete_by_id(self, id: str) -> None:
        """Delete an entity by its ID."""
        pass
    
    def update_image_data(self, image_data: list[dict[str, Any]]) -> None:
        """Update image data for an entity."""
        pass

    def update_text_data(self, text_data: list[dict[str, Any]]) -> None:
        """Update text data for an entity."""
        pass
    
    def close_scoped_session(self) -> None:
        """Close the scoped session."""
        pass
    
class BaseService:
    """
    Base Service for Weaviate.
    This class handles the interaction with Weaviate for both text and image data.
    """
    def __init__(self, repository: Repository) -> None:
        """Initialize the service with a repository."""
        self.repository = repository
        
    def read_by_id(self, id: str) -> dict[str, Any]:
        """Read an entity by its ID."""
        return self.repository.read_by_id(id)
    
    def read_all(self) -> list[dict[str, Any]]:
        """Read all entities."""
        return self.repository.read_all()
    
    def delete_by_id(self, id: str) -> None:
        """Delete an entity by its ID."""
        self.repository.delete_by_id(id)
    
    def close_scoped_session(self):
        self.repository.close_scoped_session()
        
    