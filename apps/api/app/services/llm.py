import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash') # Using flash for speed
        else:
            self.model = None
            print("⚠️ WARNING: GEMINI_API_KEY not found in environment.")

    async def generate_json(self, prompt: str):
        if not self.model:
            return None
        
        # Enforce JSON output
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        return response.text

llm_service = LLMService()
