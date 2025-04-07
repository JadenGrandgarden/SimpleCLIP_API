from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import configs
from app.core.container import Container
from app.utils.class_object import singleton
from app.api.routes import api_router
from app.core.middleware import request_debug_middleware


@singleton
class AppCreator:
    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            version="0.0.1"
        )
        
        self.app.middleware("http")(request_debug_middleware)

        # set db and container
        self.container = Container()
        self.db = self.container.db()
        self.db.create_schema()

        # set cors
        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # set routes
        @self.app.get("/")
        def root():
            return "service is working"
        
        print("main.py: api_router created")

        self.app.include_router(api_router)


app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
container = app_creator.container