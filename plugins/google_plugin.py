"""
Google Gemini Provider Plugin
Provides integration with Google's Gemini API
"""
import os
import logging
from typing import AsyncIterator
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo, Role

class GoogleProvider(BaseLLMProvider):
    """Google Gemini API Provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = None
    
    async def initialize(self):
        """Initialize Google GenAI client"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        
        try:
            genai.configure(api_key=self.api_key)
            print(f"✓ Google Provider initialized")
        except Exception as e:
            self.config.init_error = f"Failed to initialize: {str(e)}"
            print(f"✗ Google initialization failed: {e}")
    
    async def check_health(self) -> bool:
        """Check if provider is healthy"""
        return self.api_key is not None
    
    async def get_models(self) -> list[ModelInfo]:
        """Get available models (required by base class)"""
        return await self.get_available_models()

    async def get_available_models(self) -> list[ModelInfo]:
        """Get list of available Google models via API (Honesty Check)"""
        if self.config.init_error or not self.api_key:
            return []
            
        try:
            print("  ↻ Fetching Google models from API...")
            models = []
            # genai.list_models() returns an iterator
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Clean up model name (remove 'models/' prefix)
                    mid = m.name.replace('models/', '')
                    
                    models.append(ModelInfo(
                        id=mid,
                        name=m.display_name or mid,
                        provider="Google",
                        context_length=m.input_token_limit,
                        supports_streaming=True
                    ))
            
            print(f"  ✓ Fetched {len(models)} Google models")
            return models
            
        except Exception as e:
            print(f"  ✗ Google model fetch failed: {e}")
            raise e  # Propagate error to make status RED
    
    async def stream_chat(
        self,
        model_id: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream chat completion from Google Gemini"""
        if not self.api_key:
            raise RuntimeError("Provider not initialized")
        
        # Configure model
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Safety settings (block few)
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        
        # Extract system instruction if present
        system_instruction = None
        gemini_messages = []
        
        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_instruction = msg.content
            else:
                role = "user" if msg.role == Role.USER else "model"
                gemini_messages.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })
        
        # Initialize model
        model = genai.GenerativeModel(
            model_name=model_id,
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=system_instruction
        )
        
        # Generate stream
        response = await model.generate_content_async(
            gemini_messages,
            stream=True
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
