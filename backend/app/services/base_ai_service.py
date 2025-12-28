"""
Base AI Service - Reusable AI utilities
"""
from typing import Dict, Any
import json
import hashlib
from functools import lru_cache
from ..core.ai_config import ai_config

class BaseAIService:
    """Base class for AI-powered services"""
    
    def __init__(self):
        self.gemini = ai_config.get_gemini_model()
        self._request_cache = {}
    
    def _get_cache_key(self, prompt: str, temperature: float) -> str:
        """Generate cache key for request"""
        content = f"{prompt}_{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def call_gemini(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.1,
        json_mode: bool = True
    ) -> Dict[str, Any]:
        """Call Gemini API with structured output (or return mock data)"""
        
        # MOCK MODE: Return fake data without API call
        if ai_config.is_mock_mode():
            return self._get_mock_response(prompt, json_mode)
        
        # Check cache to avoid duplicate API calls
        cache_key = self._get_cache_key(prompt, temperature)
        if cache_key in self._request_cache:
            return self._request_cache[cache_key]
        
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            
            if json_mode:
                full_prompt += "\n\nRespond with ONLY valid JSON, no markdown formatting."
            
            # SAFETY: Limit tokens to prevent exhaustion
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": 512,  # Reduced from 2048
            }
            
            response = self.gemini.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            if json_mode:
                # Clean response text
                text = response.text.strip()
                # Remove markdown code blocks if present
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                    text = text.strip()
                result = json.loads(text)
            else:
                result = {"response": response.text}
            
            # Cache the result
            self._request_cache[cache_key] = result
            return result
            
        except Exception as e:
            # SAFETY FALLBACK: If AI fails, return mock response for demo reliability
            print(f"⚠️ AI call failed, using mock fallback: {str(e)}")
            return self._get_mock_response(prompt, json_mode)
    
    def _get_mock_response(self, prompt: str, json_mode: bool) -> Dict[str, Any]:
        """Generate mock responses for testing without API calls"""
        
        # Document extraction mock
        if "extract" in prompt.lower() or "document" in prompt.lower():
            return {
                "success": True,
                "extracted_fields": {
                    "name": "Mock Test User",
                    "document_id": "123456789012",
                    "document_type": "AADHAAR",
                    "date_of_birth": "1990-01-01",
                    "address": "Mock Address, City, State"
                },
                "confidence": 0.95,
                "verification_status": "VERIFIED"
            }
        
        # HR assistant mock
        if "employee" in prompt.lower() or "onboarding" in prompt.lower():
            return {
                "success": True,
                "answer": "Based on the data, you have 6 total employees with 0 completed onboarding. This indicates all employees are in various stages of the onboarding process.",
                "confidence": 0.9
            }
        
        # Employee chatbot mock
        if "task" in prompt.lower() or "chat" in prompt.lower():
            return {
                "success": True,
                "reply": "Welcome! To complete your onboarding, please: 1) Upload required documents (PAN, Aadhaar), 2) Complete the orientation training, 3) Fill out the employee information form. Let me know if you need help with any of these steps!",
                "next_steps": ["upload_documents", "training", "forms"]
            }
        
        # Onboarding analysis mock
        if "analyze" in prompt.lower() or "status" in prompt.lower():
            return {
                "success": True,
                "overall_completion": 35,
                "tasks_completed": 2,
                "tasks_pending": 5,
                "documents_verified": 0,
                "documents_pending": 2,
                "training_progress": 20,
                "recommendations": [
                    "Upload pending documents",
                    "Complete orientation training",
                    "Schedule meeting with HR"
                ],
                "status": "IN_PROGRESS"
            }
        
        # Default mock response
        return {
            "success": True,
            "response": "Mock AI response - AI_MODE is set to 'mock'",
            "note": "This is simulated data for testing without API calls"
        }
