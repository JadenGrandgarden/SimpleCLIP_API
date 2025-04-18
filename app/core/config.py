import os
from typing import List

# from dotenv import load_dotenv
from pydantic_settings import BaseSettings

class Configs(BaseSettings):
    """
    Configuration settings for the application.
    """
    # base
    # ENV: str = os.getenv("ENV", "dev")
    API: str = "/api"
    PROJECT_NAME: str = "Simple CLIP"
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    # Image path 
    IMAGE_SAVE_DIR: str = "./app/asset/"
    # date 
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"
    # UUID code 
    UUID_CODE: str = "00000000-0000-0000-0000-000000000000"
    # Model path
    MODEL_PATH: str = "C:/Users/Admin/Capstone/SimpleCLIP/app/utils/simple_clip/models/clip_model.pth"
    # Image encoder name
    IMAGE_ENCODER: str = "mobile_net_v3_small"
    # Text encoder name
    TEXT_ENCODER: str = "phobert-base"
    # Weavite URL 
    WEAVIATE_URL: str = "http://localhost:8080"
    # Weaviate class name
    WEAVIATE_COLLECTION_NAME: str = "MultimodalData"

configs = Configs()

    
    