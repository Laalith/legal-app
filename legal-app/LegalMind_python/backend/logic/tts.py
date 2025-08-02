# backend/logic/tts.py

import os
import requests
from dotenv import load_dotenv
from backend.config import ELEVENLABS_API_KEY, DEFAULT_TTS_VOICE

# Load ElevenLabs API key
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Default voice ID (you can change it to another voice if desired)
DEFAULT_VOICE_ID = "Rachel"

def text_to_speech(text, output_file="output.mp3"):
    """
    Convert text to speech using ElevenLabs API.
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("Missing ELEVENLABS_API_KEY in .env")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{DEFAULT_VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return output_file
    else:
        raise Exception(f"TTS failed: {response.status_code} - {response.text}")
# Test script
if __name__ == "__main__":
    sample = "This clause explains that either party may terminate the agreement with 30 days' notice."
    audio_path = text_to_speech(sample)
    print(f"Audio saved at: {audio_path}")
