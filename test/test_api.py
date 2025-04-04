import requests
import base64
from pprint import pprint

# API base URL
BASE_URL = "http://localhost:8081"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:")
    pprint(response.json())
    print("\n")

def test_text_vectorization():
    text = "Chú mèo đi ăn đêm"
    response = requests.post(
        f"{BASE_URL}/vectorize/text",
        json={"text": text}
    )
    print("Text Vectorization:")
    result = response.json()
    print(f"Input text: {result['text']}")
    print(f"Vector dimension: {result['dim']}")
    print(f"First 5 elements: {result['vector'][:5]}...")
    print("\n")

def test_image_vectorization():
    # Replace with path to your image
    image_path = "test/asset/cat.jpg"
    
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    response = requests.post(
        f"{BASE_URL}/vectorize/image",
        json={"image": img_data}
    )
    print("Image Vectorization:")
    result = response.json()
    print(f"Vector dimension: {result['dim']}")
    print(f"First 5 elements: {result['vector'][:5]}...")

if __name__ == "__main__":
    test_health()
    test_text_vectorization()
    test_image_vectorization()