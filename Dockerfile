FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy simple_clip package
COPY simple_clip /app/simple_clip/

# Copy static files
COPY static /app/static/

# Copy application code
COPY main.py .

# Environment variables
ENV MODEL_PATH=/app/models/clip_model.pth
ENV IMAGE_ENCODER=mobile_net_v3_small
ENV TEXT_ENCODER=phobert-base
ENV PORT=8081

# Expose port
EXPOSE 8081

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]