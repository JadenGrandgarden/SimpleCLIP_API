from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import base64
import io
from PIL import Image
import os

from simple_clip.clip import CLIP
from simple_clip.encoders import ImageEncoder, TextEncoder
from simple_clip.utils import get_image_encoder, get_text_encoder
from transformers import AutoTokenizer

app = Flask(__name__)
CORS(app)

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
        
        # # Print model summary
        # print(model)
        
        # Load model weights if the file exists
        if os.path.exists(model_path):
            print(f"Loading model from: {model_path}")
            state_dict = torch.load(model_path, map_location=device)
            load_info = model.load_state_dict(state_dict, strict=False)
            # print(f"Model loaded successfully: {load_info}")
            # print(f"Missing keys: {load_info.missing_keys}")
            # print(f"Unexpected keys: {load_info.unexpected_keys}")
        elif os.path.exists('models/clip_model.pth'):
            print(f"Loading model from: models/clip_model.pth")
            state_dict = torch.load('models/clip_model.pth', map_location=device)
            load_info = model.load_state_dict(state_dict, strict=False)
            # print(f"Model loaded successfully: {load_info}")
            # print(f"Missing keys: {load_info.missing_keys}")
            # print(f"Unexpected keys: {load_info.unexpected_keys}")
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

@app.route("/vectorize/text", methods=["POST"])
def vectorize_text():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400
    
    text = data["text"]
    
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
    
    return jsonify({
        "text": text,
        "vector": vector,
        "dim": len(vector)
    })

@app.route("/vectorize/image", methods=["POST"])
def vectorize_image():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    if "image" not in data:
        return jsonify({"error": "No image provided"}), 400
    
    # Decode base64 image
    try:
        image_data = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
    except Exception as e:
        return jsonify({"error": f"Invalid image data: {str(e)}"}), 400
    
    # Transform and encode image
    img_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        image_features = model.extract_image_features(img_tensor)
        image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
    
    # Convert to list and return
    vector = image_features[0].cpu().numpy().tolist()
    
    return jsonify({
        "vector": vector,
        "dim": len(vector)
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

@app.route("/ui", methods=["GET"])
def serve_ui():
    return send_from_directory('static', 'index.html')

@app.route("/test", methods=["GET"])
def serve_test():
    return send_from_directory('static', 'test.html')


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "name": "SimpleCLIP API",
        "status": "running",
        "endpoints": [
            {"path": "/health", "method": "GET", "description": "Health check endpoint"},
            {"path": "/vectorize/text", "method": "POST", "description": "Text vectorization endpoint"},
            {"path": "/vectorize/image", "method": "POST", "description": "Image vectorization endpoint"}
        ]
    })

if __name__ == "__main__":
    initialize()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))