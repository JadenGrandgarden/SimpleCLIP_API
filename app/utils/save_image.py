import os
from PIL import Image
import numpy as np
import torch
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.config import configs

def save_image(images: List[Image.Image], images_filename: List[str],
               metadata: Optional[List[Dict[str, Any]]] = None) -> List[str]:
    """
    Save image data to the local file system.
    
    Args:
        images: List of PIL Image objects to save
        metadata: Optional list of metadata dictionaries for each image
        
    Returns:
        Dictionary with upload status message
    """
    
    print("Saving images...")
    if metadata is None:
        metadata = [{} for _ in images]
    
    if len(images) != len(metadata):
        raise ValueError("Length of images and metadata must match")
    
    # Create a directory for saving images if it doesn't exist
    os.makedirs(configs.IMAGE_SAVE_DIR, exist_ok=True)
    
    # Process and save images
    saved_images = []
    for i, image in enumerate(images):
        print(f"Processing image {i+1}/{len(images)}")
        # Generate a unique filename based on current timestamp and index
        filename = images_filename[i]
        
        # Save the image to the specified directory
        image_path = os.path.join(configs.IMAGE_SAVE_DIR, filename)
        image.save(image_path)
        
        # Append saved image info to the list
        saved_images.append(image_path)
    
    return saved_images