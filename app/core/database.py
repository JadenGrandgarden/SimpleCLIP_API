from contextlib import contextmanager
from typing import Any, Generator
from app.core.config import configs
import weaviate

class WeaviateDatabase:
    def __init__(self) -> None:
        # Khởi tạo client kết nối đến Weaviate với URL được cung cấp
        self._client = None
        self._connect()
    
    def _connect(self) -> None:
        """
        Kết nối đến Weaviate với URL được cung cấp trong configs.
        Nếu không thể kết nối, sẽ in ra thông báo lỗi.
        """
        try:
            self._client = weaviate.connect_to_local()
            print(f"Connected to Weaviate at {configs.WEAVIATE_URL}")
        except Exception as e:
            print(f"Failed to connect to Weaviate: {e}")
    
    def create_schema(self) -> None:
        """
        Tạo hoặc cập nhật schema cho một class trong Weaviate.
        Ví dụ, bạn có thể định nghĩa schema cho một entity như 'User'
        """
        # Lưu ý: Bạn nên kiểm tra nếu class đã tồn tại để tránh lỗi
        try:
            if self._client is None:
                self._connect()
        
            if self._client.collections.exists(configs.WEAVIATE_COLLECTION_NAME):
                print(f"Schema for {configs.WEAVIATE_COLLECTION_NAME} already exists")
                return
            self._client.collections.create(configs.WEAVIATE_COLLECTION_NAME)
            print(f"Schema for {configs.WEAVIATE_COLLECTION_NAME} created")
        except Exception as e:
            print(f"Failed to create schema: {e}")
    
    @contextmanager
    def session(self) -> Generator[Any, None, None]:
        """
        Cung cấp một context manager để lấy client Weaviate.
        Vì Weaviate hoạt động theo giao thức HTTP, không có khái niệm session hay giao dịch 
        nên chúng ta chỉ trả về client để thực hiện các thao tác CRUD.
        """
        client = None
        try:
            if self._client is None or (hasattr(self._client, 'is_connected') and not self._client.is_connected()):
                print("Connecting to Weaviate...")
                self._connect()
            client = self._client
            yield client
        except Exception as e:
            # Không có rollback cho Weaviate vì các thao tác đều được gửi qua HTTP
            raise e
        finally:
            # Không cần đóng kết nối vì weaviate-client sử dụng HTTP, nên không có thao tác clean-up đặc biệt
            # self._client.close()
            pass
    def close(self):
        """Explicitly close the database connection"""
        if self._client is not None and hasattr(self._client, 'close'):
            try:
                print("Closing Weaviate connection...")
                self._client.close()
            except Exception as e:
                print(f"Error closing Weaviate connection: {e}")
            finally:
                self._client = None