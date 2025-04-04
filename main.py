from fastapi import FastAPI, HTTPException, File, UploadFile, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import base64
import io
from PIL import Image
import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from simple_clip.clip import CLIP
from simple_clip.encoders import ImageEncoder, TextEncoder
from simple_clip.utils import get_image_encoder, get_text_encoder
from transformers import AutoTokenizer

# Pydantic models for request/response
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

class EndpointInfo(BaseModel):
    path: str
    method: str
    description: str

class IndexResponse(BaseModel):
    name: str
    status: str
    endpoints: List[EndpointInfo]

# Create FastAPI app
app = FastAPI(title="SimpleCLIP API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
tokenizer = None
device = None
transform = None

def initialize():
    """Initialize the model and tokenizer"""
    global model, tokenizer, device, transform
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Get environment variables
    model_path = os.environ.get("MODEL_PATH", "/app/models/clip_model.pth")
    image_encoder_name = os.environ.get("IMAGE_ENCODER", "mobile_net_v3_small")
    text_encoder_name = os.environ.get("TEXT_ENCODER", "phobert-base")
    
    try:
        # Load encoders
        image_encoder = get_image_encoder(image_encoder_name)
        text_encoder = get_text_encoder(text_encoder_name)
        
        # Create CLIP model
        model = CLIP(
            image_encoder=image_encoder,
            text_encoder=text_encoder,
            image_mlp_dim=576, # Explicitly set for MobileNetV3Small
            text_mlp_dim=768, # Standard dimension for BERT-based models
            proj_dim=256
        )
        
        # Load model weights if the file exists
        if os.path.exists(model_path):
            print(f"Loading model from: {model_path}")
            state_dict = torch.load(model_path, map_location=device)
            load_info = model.load_state_dict(state_dict, strict=False)
        elif os.path.exists('models/clip_model.pth'):
            print(f"Loading model from: models/clip_model.pth")
            state_dict = torch.load('models/clip_model.pth', map_location=device)
            load_info = model.load_state_dict(state_dict, strict=False)
        else:
            print(f"Warning: Model file not found at {model_path}, using untrained model")
        
        model.to(device)
        model.eval()
        
        # Get tokenizer
        tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
        
        # Define image transform
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print("Model initialization complete!")
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
        raise e

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    initialize()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/vectorize/text", response_model=TextVectorResponse)
async def vectorize_text(request: TextRequest):
    text = request.text
    
    # Encode text
    encoded_texts = tokenizer(
        [text],
        padding=True,
        truncation=True,
        max_length=100,
        return_tensors='pt'
    )
    
    # Move to device
    input_ids = encoded_texts['input_ids'].to(device)
    attention_mask = encoded_texts['attention_mask'].to(device)
    
    # Extract text features
    with torch.no_grad():
        text_features = model.extract_text_features(input_ids, attention_mask)
        text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)
    
    # Convert to list and return
    vector = text_features[0].cpu().numpy().tolist()
    
    return TextVectorResponse(
        text=text,
        vector=vector,
        dim=len(vector)
    )

@app.post("/vectorize/image", response_model=ImageVectorResponse)
async def vectorize_image(request: ImageRequest):
    # Decode base64 image
    try:
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
    
    # Transform and encode image
    img_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        image_features = model.extract_image_features(img_tensor)
        image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
    
    # Convert to list and return
    vector = image_features[0].cpu().numpy().tolist()
    
    return ImageVectorResponse(
        vector=vector,
        dim=len(vector)
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")

@app.get("/ui")
async def serve_ui():
    return FileResponse('static/index.html')

@app.get("/test")
async def serve_test():
    return FileResponse('static/test.html')

@app.get("/", response_model=IndexResponse)
async def index():
    return IndexResponse(
        name="SimpleCLIP API",
        status="running",
        endpoints=[
            EndpointInfo(path="/health", method="GET", description="Health check endpoint"),
            EndpointInfo(path="/vectorize/text", method="POST", description="Text vectorization endpoint"),
            EndpointInfo(path="/vectorize/image", method="POST", description="Image vectorization endpoint")
        ]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8081)), reload=True)