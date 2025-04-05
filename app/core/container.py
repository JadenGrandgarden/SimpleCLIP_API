from dependency_injector import containers, providers
from app.core.config import configs
from app.core.database import WeaviateDatabase
from app.repository import *
from app.services import *


class Container(containers.DeclarativeContainer):
    # Cấu hình wiring để tự động inject các dependency vào các module chỉ định
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.upload",
            "app.api.endpoints.search",
            "app.api.endpoints.image",
            "app.api.endpoints.health",
        ]
    )

    # Khởi tạo Database là một Singleton, đảm bảo chỉ có một instance trong toàn ứng dụng
    db = providers.Singleton(WeaviateDatabase)

    # # Định nghĩa các repository sử dụng Factory, mỗi lần gọi sẽ tạo instance mới
    # # session_factory được truyền từ db.provided.session là một phương thức được cung cấp bởi đối tượng Database
    image_repository = providers.Factory(
        ImageRepository, session_factory=db.provided.session
    )
    text_repository = providers.Factory(
        TextRepository, session_factory=db.provided.session
    )
    

    # # Định nghĩa các service sử dụng Factory, các service này phụ thuộc vào repository tương ứng
    image_service = providers.Factory(ImageService, image_repository=image_repository)
    text_service = providers.Factory(TextService, text_repository=text_repository)
