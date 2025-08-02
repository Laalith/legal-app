# test_imports.py - Test if all imports work

try:
    from backend.analyzer import analyze_uploaded_file
    print("✅ analyzer.py imported successfully")
except ImportError as e:
    print(f"❌ analyzer.py import failed: {e}")

try:
    from backend.logic.summarizer import summarize_text
    print("✅ summarizer.py imported successfully")
except ImportError as e:
    print(f"❌ summarizer.py import failed: {e}")

try:
    from backend.logic.grantie import analyze_warranties_and_guarantees, check_warranty_compliance
    print("✅ grantie.py imported successfully")
except ImportError as e:
    print(f"❌ grantie.py import failed: {e}")

try:
    from backend.logic.tts import text_to_speech
    print("✅ tts.py imported successfully")
except ImportError as e:
    print(f"❌ tts.py import failed: {e}")

print("\n--- Environment Check ---")
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ OpenAI API Key found: {api_key[:10]}...")
else:
    print("❌ OpenAI API Key not found in .env file")

print("\n--- Test Complete ---")