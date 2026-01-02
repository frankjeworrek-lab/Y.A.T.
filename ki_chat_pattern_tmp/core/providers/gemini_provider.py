import os
from typing import AsyncGenerator, List
from .base_provider import BaseLLMProvider
from .types import Message, ModelInfo, ProviderConfig, ModelCapability

class GeminiProvider(BaseLLMProvider):
    """
    Example: Generic provider for Google Gemini.
    Requires: pip install google-generativeai
    """
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        
    async def initialize(self) -> None:
        try:
            import google.generativeai as genai
            api_key = self.config.api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("Warning: Gemini API Key not found.")
                return
            genai.configure(api_key=api_key)
            self.client = genai
        except ImportError:
            print("Warning: google-generativeai not installed.")

    async def get_models(self) -> List[ModelInfo]:
        if not self.client:
            return []
        
        # Gemini models (hardcoded common ones for simplicity)
        return [
            ModelInfo(id="gemini-pro", name="Gemini Pro", provider="Google Gemini"),
            ModelInfo(id="gemini-2.0-flash-exp", name="Gemini 2.0 Flash", provider="Google Gemini"),
        ]

    async def stream_chat(
        self, 
        model_id: str, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "Error: Gemini client not initialized"
            return

        try:
            model = self.client.GenerativeModel(model_id)
            
            # Convert message history
            history = []
            for m in messages[:-1]:  # All but last
                role = "user" if m.role.value == "user" else "model"
                history.append({"role": role, "parts": [m.content]})
            
            chat = model.start_chat(history=history)
            response = await chat.send_message_async(
                messages[-1].content,
                stream=True
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {e}"

    async def check_health(self) -> bool:
        return self.client is not None
