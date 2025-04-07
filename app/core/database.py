from contextlib import contextmanager
from typing import Any, Generator
from app.core.config import configs
import weaviate

class WeaviateDatabase:
    def __init__(self) -> None:
        # Khởi tạo client kết nối đến Weaviate với URL được cung cấp
        self._client = weaviate.connect_to_local()
    
    def create_schema(self) -> None:
        """
        Tạo hoặc cập nhật schema cho một class trong Weaviate.
        Ví dụ, bạn có thể định nghĩa schema cho một entity như 'User'
        """
        # Lưu ý: Bạn nên kiểm tra nếu class đã tồn tại để tránh lỗi
        if self._client.collections.exists(configs.WEAVIATE_COLLECTION_NAME):
            print(f"Schema for {configs.WEAVIATE_COLLECTION_NAME} already exists")
            return
        self._client.collections.create(configs.WEAVIATE_COLLECTION_NAME)
        print(f"Schema for {configs.WEAVIATE_COLLECTION_NAME} created")
    
    @contextmanager
    def session(self) -> Generator[Any, None, None]:
        """
        Cung cấp một context manager để lấy client Weaviate.
        Vì Weaviate hoạt động theo giao thức HTTP, không có khái niệm session hay giao dịch 
        nên chúng ta chỉ trả về client để thực hiện các thao tác CRUD.
        """
        try:
            yield self._client
        except Exception as e:
            # Không có rollback cho Weaviate vì các thao tác đều được gửi qua HTTP
            raise e
        finally:
            # Không cần đóng kết nối vì weaviate-client sử dụng HTTP, nên không có thao tác clean-up đặc biệt
            self._client.close()
