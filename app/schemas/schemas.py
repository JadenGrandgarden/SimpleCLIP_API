from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile

TextRequest = str

ImageRequest = UploadFile  # Base64 encoded image
    
class TextSearchResponse(BaseModel):
    text: List[str] 

    
class UploadResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str

    



# class TextVectorResponse(BaseModel):
#     text: str
#     vector: List[float]
#     dim: int

# class ImageVectorResponse(BaseModel):
#     vector: List[float]
#     dim: int