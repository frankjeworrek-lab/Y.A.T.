"""
OpenAI Provider Plugin
Provides integration with OpenAI's API (GPT-4, GPT-3.5, etc.)
"""
import os
from typing import AsyncIterator
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        self.api_key = None
    
    async def initialize(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            self.config.init_error = "API key not found. Set OPENAI_API_KEY environment variable."
            return
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
            print(f"✓ OpenAI Provider initialized")
        except Exception as e:
            self.config.init_error = f"Failed to initialize: {str(e)}"
            print(f"✗ OpenAI initialization failed: {e}")
    
    async def get_available_models(self) -> list[ModelInfo]:
        """Get list of available OpenAI models"""
        return [
            ModelInfo(
                id="gpt-4o-search-preview",
                name="GPT-4o",
                provider="OpenAI",
                context_length=128000,
                supports_streaming=True
            ),
            ModelInfo(
                id="gpt-4-turbo-preview",
                name="GPT-4 Turbo",
                provider="OpenAI",
                context_length=128000,
                supports_streaming=True
            ),
            ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider="OpenAI",
                context_length=16385,
                supports_streaming=True
            ),
        ]
    
    async def stream_chat(
        self,
        messages: list[Message],
        model_id: str = "gpt-4o-search-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream chat completion from OpenAI"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
        
        stream = await self.client.chat.completions.create(
            model=model_id,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
