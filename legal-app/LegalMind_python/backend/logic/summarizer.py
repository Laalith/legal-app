# backend/logic/summarizer.py - Fixed to use GPT-3.5-turbo

import openai
from dotenv import load_dotenv
import os
from backend.config import OPENAI_API_KEY

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text(text: str) -> str:
    """
    Use OpenAI GPT-3.5-turbo to summarize legal text in simple language.
    """
    prompt = f"""Summarize the following legal text in clear, simple terms:

{text}

Please provide a concise summary that explains:
1. The main purpose of this document
2. Key obligations and rights
3. Important terms to be aware of
4. Any potential risks or benefits

Keep the summary accessible to non-lawyers.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Changed from gpt-4 to gpt-3.5-turbo
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=400  # Increased for better summaries
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"