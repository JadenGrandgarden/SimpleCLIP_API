import requests
import base64
import json
import os
from PIL import Image
from io import BytesIO
from pprint import pprint

# API base URL
BASE_URL = "http://localhost:5000"


def test_health():
    """Test the health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("Health Check:")
        pprint(response.json())
        print("\n")
    except Exception as e:
        print(f"Health check failed: {e}")
        print("\n")


def test_search_by_text():
    """Test the search by text endpoint."""
    try:
        query = "con mèo"
        response = requests.get(
            f"{BASE_URL}/search/text", params={"query": query, "limit": 5}
        )
        print("Search by Text:")
        results = response.json()
        print(f"Query: '{query}'")
        print(results)
        print(f"Found {len(results['response_files'])} results")
        print("\n")
        for i, image_path in enumerate(results["response_files"]):
            print(f"Result {i + 1}: {image_path}")
        print("\n")
    except Exception as e:
        print(f"Search by text failed: {e}")
        print("\n")


def test_search_by_image():
    """Test the search by image endpoint."""
    try:
        image_path = "app/asset/cat-1.jpg"

        with open(image_path, "rb") as img_file:
            files = {"file": img_file}
            response = requests.post(
                f"{BASE_URL}/search/image", files=files, params={"limit": 3}
            )

        print("Search by Image:")
        results = response.json()
        print(results)
        print(f"Image: '{image_path}'")
        print(f"Found {len(results['text'])} results")
    except Exception as e:
        print(f"Search by image failed: {e}")
        print("\n")


def test_upload_text():
    """Test the upload text endpoint."""
    try:
        texts = ["Mèo đen tuyền", "Nhó nham nhó"]
        metadata = [
            {"source": "test", "language": "en"},
            {"source": "test", "language": "en"},
        ]

        response = requests.post(
            f"{BASE_URL}/upload/text", json={"texts": texts, "metadata": metadata}
        )

        print("Upload Text:")
        result = response.json()
        pprint(result)
        print("\n")
    except Exception as e:
        print(f"Upload text failed: {e}")
        print("\n")


def test_upload_image():
    """Test the upload image endpoint."""
    try:
        image_path = "app/asset/cat-1.jpg"
        metadata = json.dumps(
            [{"description": "A test cat image", "category": "animals"}]
        )

        print(f"1. Opening image file: {image_path}")
        with open(image_path, "rb") as img_file:
            # Try with the "files" parameter name
            files = {"file": img_file}

            print("2. Sending request to server")
            response = requests.post(
                url=f"{BASE_URL}/upload/image",
                files=files,
                data={"metadata_json": metadata},
            )
            print(f"3. Response status: {response.status_code}")
            print(f"4. Response: {response.text}")

    except Exception as e:
        print(f"Upload image failed: {e}")


def test_get_all_images():
    """Test getting all images."""
    try:
        response = requests.get(f"{BASE_URL}/image/all")

        print("Get All Images:")
        result = response.json()
        print(f"Retrieved {len(result)} images")
        print("\n")
    except Exception as e:
        print(f"Get all images failed: {e}")
        print("\n")


def test_get_image_by_id():
    """Test getting a specific image by ID."""
    try:
        # First get all images to get an ID
        image_path = "cat-1.jpg"
        import uuid

        image_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, image_path))
        response = requests.get(f"{BASE_URL}/image/{image_id}")

        print("Get Image by ID:")
        result = response.json()
        print(f"Image ID: {image_id}")
        print(f"Image: {result}")

    except Exception as e:
        print(f"Get image by ID failed: {e}")
        print("\n")


if __name__ == "__main__":
    print("===== TESTING SIMPLECLIP API =====\n")

    # Basic functionality
    # test_health()

    # # Search functionality
    # test_search_by_text()
    # test_search_by_image()

    # Upload functionality
    test_upload_image()
    # test_upload_text()

    # # # Image retrieval
    # test_get_all_images()
    # test_get_image_by_id()

    print("===== API TESTS COMPLETED =====")
