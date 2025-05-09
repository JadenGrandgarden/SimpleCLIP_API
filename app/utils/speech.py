
from pydub import AudioSegment
from transformers import pipeline
import torch
import os
from app.core.config import configs

def save_audio_file(file_path, audio_data):
    """
    Save the audio data to a file.
    """
    with open(file_path, 'wb') as f:
        f.write(audio_data)
    print(f"Audio file saved to {file_path}")
    return file_path

def convert_audio_to_wav(input_file_path, output_file_path):
    """
    Convert an audio file to WAV format using pydub.
    """
    audio = AudioSegment.from_file(input_file_path)
    audio.export(output_file_path, format="wav")
    print(f"Converted {input_file_path} to {output_file_path}")
    return output_file_path

def speech_to_text(file_path):
    """
    Convert speech to text using a speech recognition library.
    """
    # Placeholder for actual speech-to-text conversion
    # This should be replaced with the actual implementation
    print(f"Converting speech to text from {file_path}")
    transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-medium", device=configs.DEVICE)
    result = transcriber(file_path)
    text = result['text']
    print(f"Transcribed text: {text}")
    return text