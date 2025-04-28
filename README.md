# SimpleCLIP

SimpleCLIP is a lightweight and accessible implementation of the Contrastive Language-Image Pre-training (CLIP) model. This project is designed to help researchers and developers understand and utilize CLIP for multimodal learning tasks.

## Key Features

- **Simplified CLIP Architecture**: A streamlined version of the original CLIP model for ease of use and understanding.
- **Multimodal Retrieval**: Supports both text-to-image and image-to-text retrieval tasks.
- **Pre-trained Models**: Leverage pre-trained weights for quick experimentation.
- **User-Friendly API**: Intuitive API for seamless integration into your projects.

## Installation

To install SimpleCLIP, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/SimpleCLIP.git
    ```
2. Navigate to the project directory:
    ```bash
    cd SimpleCLIP
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run weaviate vector database:
    ```bash
    docker conmpose up --build
    ```
5. Run the app:
    ```bash
    uvicorn app.main:app --host 127.0.0.1 --port 8081
    ```

## Usage

SimpleCLIP can be used for tasks such as multimodal retrieval, feature extraction, and more. Refer to the [documentation](#) for detailed examples and tutorials.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
