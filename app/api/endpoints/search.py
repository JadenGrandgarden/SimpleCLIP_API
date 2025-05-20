from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from typing import List, Optional, Dict, Any
import io
from PIL import Image
import os
import base64
from app.schemas.schemas import TextSearchResponse, ImageRequest, TextRequest
from fastapi.responses import FileResponse
from app.core.container import Container
from app.core.middleware import inject
from app.services.image_services import ImageService
from app.services.text_services import TextService
from app.core.config import configs as CFG
import py_vncorenlp
from app.utils.speech import save_audio_file, convert_audio_to_wav, speech_to_text

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.get("/text")
@inject
def search_by_text(
    query: Optional[TextRequest] = Query(None),
    limit: int = Query(10, ge=10, le=100),
    service: TextService = Depends(Provide[Container.text_service])
):
    """
    Search for images using a text query
    
    Args:
        query: Text to search with
        limit: Maximum number of results to return
        
    Returns:
        List of matching image results with similarity scores
    """
    # Preprocess the query text
    query = query.strip().lower()
    
    # Save the query database
    query = [query]
    metadata = [{
        "source": "search",
        "language": "vi"
    }] * len(query)
    service.upload_text(query, metadata)
    print(f"Successfully uploaded text: {query}")
    
    # Perform the search
    print(f"Searching for: {query}")
    search_results = service.search_by_text(text=query[0], limit=limit)
    
    # Convert image paths to URLs
    image_urls = []
    for path in search_results["response_files"]:
        filename = os.path.basename(path)
        # Create a URL using the /assets/ endpoint
        image_url = f"/asset/{filename}"
        image_urls.append(image_url)
    
    # Add URLs to the ranked results
    ranked_results = search_results["ranked_results"]
    for item in ranked_results:
        item["image_url"] = f"/asset/{os.path.basename(item['image_path'])}"
    
    return {
        "image_urls": image_urls,
        "ranked_results": ranked_results,
        "query": query[0]
    }


@router.post("/audio")
@inject
async def search_by_audio(
    file: UploadFile = File(...),
    limit: int = Query(10, ge=10, le=100),
    service: TextService = Depends(Provide[Container.text_service])
):
    """
    Search for text using an audio query
    
    Args:
        file: Audio file to search with
        limit: Maximum number of results to return
        
    Returns:
        List of matching text results with similarity scores
    """
    # Read the uploaded audio file
    content = await file.read()
    # Save the audio file to a temporary location
    audio_file_path = os.path.join(
        CFG.AUDIO_PATH, f"temp_audio_{os.urandom(8).hex()}.wav"
    )
    print(f"Audio file path: {audio_file_path}")
    os.makedirs(CFG.AUDIO_PATH, exist_ok=True)
    save_audio_file(audio_file_path, content)
    # Convert the audio file to WAV format
    wav_file_path = os.path.join(
        CFG.AUDIO_PATH, f"temp_audio_{os.urandom(8).hex()}.wav"
    )
    convert_audio_to_wav(audio_file_path, wav_file_path)
    # Perform speech-to-text conversion
    query = speech_to_text(wav_file_path)
    # Remove the temporary audio file
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
        
    # Preprocess the query text
    query = query.strip().lower()
    
    # Save the query database
    query = [query]
    metadata = [{
        "source": "search",
        "language": "vi"
    }] * len(query)
    service.upload_text(query, metadata)
    print(f"Successfully uploaded text: {query}")
    
    # Perform the search
    print(f"Searching for: {query}")
    search_results = service.search_by_text(text=query[0], limit=limit)
    
    # Convert image paths to URLs
    image_urls = []
    for path in search_results["response_files"]:
        filename = os.path.basename(path)
        # Create a URL using the /assets/ endpoint
        image_url = f"/asset/{filename}"
        image_urls.append(image_url)
    
    # Add URLs to the ranked results
    ranked_results = search_results["ranked_results"]
    for item in ranked_results:
        item["image_url"] = f"/asset/{os.path.basename(item['image_path'])}"

    return {
        "query": query[0],
        "image_urls": image_urls,
        "ranked_results": ranked_results
    }


@router.post("/image")
@inject
async def search_by_image(
    file: UploadFile = File(...),
    limit: int = Query(5, ge=1, le=100),
    service: ImageService = Depends(Provide[Container.image_service]),
):
    """
    Search for text using an image query
    
    Args:
        file: Image file to search with
        limit: Maximum number of results to return
        
    Returns:
        List of matching text results with similarity scores
    """
    try:
        # Read the uploaded image
        content = await file.read()

        # Process the image
        image = Image.open(io.BytesIO(content)).convert("RGB")

        # Create a temporary file with proper extension
        temp_file_path = os.path.join(
            CFG.TEMP_DIR, f"temp_image_{os.urandom(8).hex()}.jpg"
        )

        # Save the processed image to temporary location
        os.makedirs(CFG.TEMP_DIR, exist_ok=True)
        image.save(temp_file_path)

        # Call service to perform the search
        results = service.search_by_image(image_filename=temp_file_path, limit=limit)

        return {
            "text": results["text"],
            "ranked_results": results["ranked_results"],
            "image_name": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    finally:
        # Ensure temporary file is removed even if an error occurs
        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Failed to remove temporary file: {str(e)}")
