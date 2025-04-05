import os
import torch
import torchvision.transforms as transforms
from transformers import AutoTokenizer
from simple_clip.clip import CLIP
from simple_clip.utils import get_image_encoder, get_text_encoder
from app.core.config import configs

# Define a class to hold our resources
class SimpleClipResources:
    def __init__(self):
        self._initialized = False
        """Initialize all resources"""
        if self._initialized:
            return
            
        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Get environment variables
        model_path = os.environ.get("MODEL_PATH", configs.MODEL_PATH)
        image_encoder_name = os.environ.get("IMAGE_ENCODER", configs.IMAGE_ENCODER)
        text_encoder_name = os.environ.get("TEXT_ENCODER", configs.TEXT_ENCODER)
        
        try:
            # Load encoders
            image_encoder = get_image_encoder(image_encoder_name)
            text_encoder = get_text_encoder(text_encoder_name)
            
            # Create CLIP model
            self.model = CLIP(
                image_encoder=image_encoder,
                text_encoder=text_encoder,
                image_mlp_dim=576,
                text_mlp_dim=768,
                proj_dim=256
            )
            
            # Load model weights
            if os.path.exists(model_path):
                print(f"Loading model from: {model_path}")
                state_dict = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(state_dict, strict=False)
            else:
                print(f"Warning: Model file not found at {model_path}, using untrained model")
            
            self.model.to(self.device)
            self.model.eval()
            
            # Initialize tokenizer
            try:
                print(f"Loading tokenizer for vinai/phobert-base")
                self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", local_files_only=False)
                
                # Verify tokenizer
                test_result = self.tokenizer("Test sentence", return_tensors="pt")
                if test_result is not None and 'input_ids' in test_result:
                    print(f"Tokenizer verified successfully")
                else:
                    raise ValueError("Tokenizer verification failed")
                    
            except Exception as e:
                print(f"Error initializing tokenizer: {e}")
                raise RuntimeError(f"Failed to initialize tokenizer: {e}")
            
            # Define image transform
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            self._initialized = True
            print("Model initialization complete!")
        except Exception as e:
            print(f"Error initializing model: {str(e)}")
            raise e
    
    def encode_image(self, image: str):
        """
        Encode an image using the model.
        """
        # Apply transformations
        image = self.transform(image).unsqueeze(0).to(self.device)
        
        # Extract image features
        with torch.no_grad():
            image_features = self.model.extract_image_features(image)
            image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
        
        return {
            "vector": image_features[0].cpu().numpy().tolist(),
            "dim": image_features.shape[1]  
        } 
    
    def encode_text(self, text: str):
        """
        Encode text using the model.
        """
        # Tokenize and encode text
        encoded_texts = self.tokenizer(
            [text],
            padding=True,
            truncation=True,
            max_length=100,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = encoded_texts['input_ids'].to(self.device)
        attention_mask = encoded_texts['attention_mask'].to(self.device)
        
        # Extract text features
        with torch.no_grad():
            text_features = self.model.extract_text_features(input_ids, attention_mask)
            text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)
        
        return {
            "vector": text_features[0].cpu().numpy().tolist(),
            "dim": text_features.shape[1]  
        }
    

# Create a singleton instance
resources = SimpleClipResources()

# # Export the initialize function and resources
# def initialize():
#     resources.initialize()

# def get_resources():
#     if not resources._initialized:
#         resources.initialize()
#     return resources