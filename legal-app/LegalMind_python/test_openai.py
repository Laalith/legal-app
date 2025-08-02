# test_openai_gpt35.py - Test script using GPT-3.5-turbo

import openai
import os
from dotenv import load_dotenv

def test_openai_connection():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Set the API key
    openai.api_key = api_key
    
    try:
        # Test API call with GPT-3.5-turbo
        print("🔄 Testing OpenAI API connection with GPT-3.5-turbo...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Changed to GPT-3.5-turbo
            messages=[
                {"role": "user", "content": "Say 'Hello, API is working with GPT-3.5!'"}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ SUCCESS: {result}")
        
        # Test legal analysis capability
        print("\n🔄 Testing legal analysis capability...")
        legal_test = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Explain this legal clause in simple terms: 'The party shall indemnify and hold harmless the other party from any claims.'"}
            ],
            max_tokens=100
        )
        
        legal_result = legal_test.choices[0].message.content.strip()
        print(f"✅ LEGAL ANALYSIS TEST: {legal_result[:100]}...")
        
        return True
        
    except openai.error.AuthenticationError:
        print("❌ ERROR: Invalid API key")
        print("Please check your OpenAI API key in the .env file")
        return False
        
    except openai.error.RateLimitError:
        print("❌ ERROR: Rate limit exceeded or insufficient credits")
        print("Please check your OpenAI account balance")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing OpenAI API Connection with GPT-3.5-turbo")
    print("=" * 50)
    success = test_openai_connection()
    
    if success:
        print("\n🎉 Your setup is ready!")
        print("You can now run your Legal Document Analyzer")
    else:
        print("\n❌ Please fix the issues above before proceeding")
        print("\nTo get GPT-4 access:")
        print("1. Add credits to your OpenAI account")
        print("2. Make some API calls with GPT-3.5 first")
        print("3. Wait for GPT-4 access to be granted")