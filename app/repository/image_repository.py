from app.repository.text_repository import TextRepository
import weavite 
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeVar, Union
from app.core.config import configs 
from app.repository.base_repository import BaseRepository

class ImageRepository(BaseRepository):
    """
    Image Repository for Weaviate.
    This class handles the interaction with Weaviate for image data.
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[weavite.Client]]) -> None:
        """Initialize the repository with a Weaviate client."""
        self.session_factory = session_factory
        super().__init__(session_factory)