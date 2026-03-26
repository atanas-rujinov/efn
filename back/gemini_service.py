import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_ai_advice(disability: str, request_description: str, request_type: str = "drive") -> str:
    """
    Get AI advice from Google Gemini based on the disability and request description.
    
    Args:
        disability: The disability of the person making the request
        request_description: Description of the request (what they need help with)
        request_type: Type of request ("drive" for drive requests, "shop" for shop requests)
    
    Returns:
        AI-generated advice for the helper/driver
    """
    try:
        if not GEMINI_API_KEY:
            return "API key not configured"
        
        model = genai.GenerativeModel("gemini-flash-latest")
        
        # Create a detailed system prompt
        request_type_text = "drive request" if request_type == "drive" else "shopping request"
        
        prompt = f"""You are an AI assistant helping drivers and helpers provide better support to people with disabilities.

A person with the following disability needs assistance:
Disability: {disability}

Request Type: {request_type_text}
Request Description: {request_description}

Please provide specific, practical advice for the helper/driver on:
1. How to best assist this person with their {request_type_text}
2. Important considerations related to their disability
3. Specific accommodations or techniques they should use
4. Any safety or comfort considerations
5. Communication tips

Keep the advice concise, actionable, and respectful."""

        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return f"Unable to generate advice: {str(e)}"
