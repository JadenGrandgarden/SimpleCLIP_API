from pydantic import BaseModel
from typing import List

class TextRequest(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image: str  # Base64 encoded image

class TextVectorResponse(BaseModel):
    text: str
    vector: List[float]
    dim: int

class ImageVectorResponse(BaseModel):
    vector: List[float]
    dim: int

class HealthResponse(BaseModel):
    status: str