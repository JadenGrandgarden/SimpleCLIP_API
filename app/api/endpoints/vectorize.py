from fastapi import APIRouter, HTTPException
from app.models.schemas import TextRequest, ImageRequest, TextVectorResponse, ImageVectorResponse
from app.core.initialization import get_resources
import torch
import base64
import io
from PIL import Image

router = APIRouter()

@router.post("/text", response_model=TextVectorResponse)
async def vectorize_text(request: TextRequest):
    # Get initialized resources
    resources = get_resources()
    
    text = request.text
    print(f"Received text: {text}")
    print(f"Using device: {resources.device}")
    
    if resources.tokenizer is None:
        raise HTTPException(status_code=500, detail="Tokenizer not initialized")
    
    # Encode text
    encoded_texts = resources.tokenizer(
        [text],
        padding=True,
        truncation=True,
        max_length=100,
        return_tensors='pt'
    )
    
    # Move to device
    input_ids = encoded_texts['input_ids'].to(resources.device)
    attention_mask = encoded_texts['attention_mask'].to(resources.device)
    
    # Extract text features
    with torch.no_grad():
        text_features = resources.model.extract_text_features(input_ids, attention_mask)
        text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)
    
    # Convert to list and return
    vector = text_features[0].cpu().numpy().tolist()
    
    return TextVectorResponse(
        text=text,
        vector=vector,
        dim=len(vector)
    )

@router.post("/image", response_model=ImageVectorResponse)
async def vectorize_image(request: ImageRequest):
    # Get initialized resources
    resources = get_resources()
    
    # Decode base64 image
    try:
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
    
    # Transform and encode image
    img_tensor = resources.transform(image).unsqueeze(0).to(resources.device)
    
    with torch.no_grad():
        image_features = resources.model.extract_image_features(img_tensor)
        image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
    
    # Convert to list and return
    vector = image_features[0].cpu().numpy().tolist()
    
    return ImageVectorResponse(
        vector=vector,
        dim=len(vector)
    )