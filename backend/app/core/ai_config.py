"""
AI Configuration and Initialization
"""
import os
from typing import Optional
import google.generativeai as genai

class AIConfig:
    """Centralized AI configuration"""
    
    _gemini_model: Optional[genai.GenerativeModel] = None
    _mock_mode: bool = None
    
    @classmethod
    def is_mock_mode(cls) -> bool:
        """Check if running in mock mode (no API calls)"""
        if cls._mock_mode is None:
            cls._mock_mode = os.getenv("AI_MODE", "live").lower() == "mock"
        return cls._mock_mode
    
    @classmethod
    def get_gemini_model(cls):
        """Get or initialize Gemini model"""
        # In mock mode, don't initialize model
        if cls.is_mock_mode():
            return None
            
        if cls._gemini_model is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            
            genai.configure(api_key=api_key)
            # Use gemini-1.5-flash-latest for v1beta API
            cls._gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        return cls._gemini_model

# Singleton instance
ai_config = AIConfig()
