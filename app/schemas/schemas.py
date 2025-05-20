from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi import UploadFile

TextRequest = str

ImageRequest = UploadFile  # Base64 encoded image

class RankedTextResult(BaseModel):
    text: str
    similarity: float
    rank: int
    metadata: Optional[Dict[str, Any]] = None
    
class RankedImageResult(BaseModel):
    image_path: str
    image_url: Optional[str] = None
    similarity: float
    rank: int

class TextSearchResponse(BaseModel):
    text: List[str] 
    ranked_results: Optional[List[RankedTextResult]] = None
    image_name: Optional[str] = None

class ImageSearchResponse(BaseModel):
    image_urls: List[str]
    ranked_results: Optional[List[RankedImageResult]] = None
    query: Optional[str] = None
    
class UploadResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str