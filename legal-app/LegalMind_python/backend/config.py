# backend/config.py

import os
from dotenv import load_dotenv

# Load .env variables once here
load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ElevenLabs API
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Default TTS voice (optional customization)
DEFAULT_TTS_VOICE = os.getenv("DEFAULT_TTS_VOICE", "Rachel")  # fallback to "Rachel"
