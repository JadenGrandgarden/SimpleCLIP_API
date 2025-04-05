from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile

class TextRequest(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image: List[UploadFile]  # Base64 encoded image
    
class TextSearchResponse(BaseModel):
    text: List[str] 

class ImageSearchResponse(BaseModel):
    image: List[str]  # List of image URLs or identifiers 
    
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