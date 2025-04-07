import weaviate 
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeVar, Union
from app.core.config import configs 
from app.repository.base_repository import BaseRepository

class TextRepository(BaseRepository):
    """
    Text Repository for Weaviate.
    This class handles the interaction with Weaviate for text data.
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[weaviate.Client]]) -> None:
        """Initialize the repository with a Weaviate client."""
        self.session_factory = session_factory
        super().__init__(session_factory)
