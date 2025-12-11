from contextlib import contextmanager
from typing import Any, Generator
from loguru import logger
from app.core.config import configs
import weaviate

class WeaviateDatabase:
    def __init__(self) -> None:
        self._client = weaviate.connect_to_local()

    def create_schema(self) -> None:
        """
        Create or update schema for a class in Weaviate.
        """
        if self._client.collections.exists(configs.WEAVIATE_COLLECTION_NAME):
            logger.info(f"Schema for {configs.WEAVIATE_COLLECTION_NAME} already exists")
            return
        self._client.collections.create(configs.WEAVIATE_COLLECTION_NAME)
        logger.info(f"Schema for {configs.WEAVIATE_COLLECTION_NAME} created")

    @contextmanager
    def session(self) -> Generator[Any, None, None]:
        """
        Provide a context manager to get Weaviate client.
        Since Weaviate operates via HTTP protocol, there is no concept of session or transaction,
        so we just return the client to perform CRUD operations.
        """
        try:
            if hasattr(self._client, 'is_connected') and not self._client.is_connected():
                logger.info("Connecting to Weaviate...")
                self._client.connect()
            yield self._client
        except Exception as e:
            raise e
        finally:
            pass