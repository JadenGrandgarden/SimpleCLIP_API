import os
from typing import List
from torch import cuda
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
    # Device
    DEVICE: str = "cuda" if cuda.is_available() else "cpu"
    # Image path 
    IMAGE_SAVE_DIR: str = "./app/asset/"
    # date 
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"
    # UUID code 
    UUID_CODE: str = "00000000-0000-0000-0000-000000000000"
    # Model path
    MODEL_PATH: str = "C:/Users/Admin/Capstone/SimpleCLIP/app/utils/simple_clip/models/clip_model.pth"
    # Temperature 
    TEMPERATURE: float = 1.0
    # Image encoder name
    IMAGE_ENCODER: str = "mobilenetv3_large_150d.ra4_e3600_r256_in1k"
    # Image encoder dimension
    IMAGE_EMBEDDING_DIM: int = 1280
    # Image size
    IMAGE_SIZE: int = 224
    # Text encoder name
    TEXT_ENCODER: str = "vinai/phobert-base-v2"
    # Text encoder dimension
    TEXT_EMBEDDING_DIM: int = 768
    # Max length of text
    MAX_TEXT_LENGTH: int = 200
    # Projection head dimension
    PROJECTION_DIM: int = 256
    # Number of projection layers
    NUM_PROJECTION_LAYERS: int = 1
    # Weavite URL 
    WEAVIATE_URL: str = "http://localhost:8080"
    # Weaviate class name
    WEAVIATE_COLLECTION_NAME: str = "MultimodalData"

configs = Configs()

    
    