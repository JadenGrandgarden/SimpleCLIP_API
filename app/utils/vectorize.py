import os
import torch
import torchvision.transforms as transforms
from transformers import AutoTokenizer
import numpy as np
import cv2
import albumentations as A
from app.utils.CLIP import CLIPModel
from app.core.config import configs as CFG
from app.utils.modules import ImageEncoder, TextEncoder

def get_transforms():
    return A.Compose([
        A.Resize(CFG.IMAGE_SIZE, CFG.IMAGE_SIZE, always_apply=True),
        A.Normalize(max_pixel_value=255.0, always_apply=True),
    ])

def get_tensor_from_path(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = get_transforms()(image=image)['image']
    res = torch.tensor(image).permute(2, 0, 1).float()
    # print(res)
    return res


# Define a class to hold our resources
class SimpleClipResources:
    def __init__(self):
        self._initialized = False
        """Initialize all resources"""
        if self._initialized:
            return
            
        # Set device
        self.device = CFG.DEVICE
        print(f"Using device: {self.device}")
        
        # Get environment variables
        # model_path = os.environ.get("MODEL_PATH", configs.MODEL_PATH)
        # image_encoder_name = os.environ.get("IMAGE_ENCODER", configs.IMAGE_ENCODER)
        # text_encoder_name = os.environ.get("TEXT_ENCODER", configs.TEXT_ENCODER)

        model_path = CFG.MODEL_PATH

        try:        
            # Create CLIP model
            self.model = CLIPModel()
            
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
                self.tokenizer = AutoTokenizer.from_pretrained(CFG.TEXT_ENCODER)
                
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
            self.transform = get_transforms()
            
            self._initialized = True
            print("Model initialization complete!")
        except Exception as e:
            print(f"Error initializing model: {str(e)}")
            raise e
    
    def encode_image(self, image_path: str):
        """
        Encode an image using the model.
        """
        # Apply transformations
        image = get_tensor_from_path(image_path)
        
        # Extract image features
        with torch.no_grad():
            image_features = self.model.image_encoder(image.unsqueeze(0).to(self.device))
            image_features = self.model.image_projection(image_features)
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
            text_features = self.model.text_encoder(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            text_features = self.model.text_projection(text_features)
            text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)
        
        return {
            "vector": text_features[0].cpu().numpy().tolist(),
            "dim": text_features.shape[1]  
        }

# Create a singleton instance
# if __name__ == "__main__":
#     resources = SimpleClipResources()
#     image_path = 'app/asset/cat-1.jpg'
#     print(resources.encode_image(image_path))
#     text = "A cat sitting on a chair"
#     print(text)
#     print(resources.encode_text(text))
resources = SimpleClipResources()



# # Export the initialize function and resources
# def initialize():
#     resources.initialize()

# def get_resources():
#     if not resources._initialized:
#         resources.initialize()
#     return resources