"""
Anthropic Provider Plugin
Provides integration with Anthropic's Claude API
"""
import os
from typing import AsyncIterator
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo, Role


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API Provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        self.api_key = None
    
    async def initialize(self):
        """Initialize Anthropic client"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.api_key)
            print(f"✓ Anthropic Provider initialized")
        except Exception as e:
            self.config.init_error = f"Failed to initialize: {str(e)}"
            print(f"✗ Anthropic initialization failed: {e}")
    
    async def check_health(self) -> bool:
        """Check if provider is healthy"""
        return self.client is not None and self.api_key is not None
    
    async def get_models(self) -> list[ModelInfo]:
        """Get available models (required by base class)"""
        return await self.get_available_models()
    
    async def get_available_models(self) -> list[ModelInfo]:
        """Get list of available Anthropic models via API (Honesty Check)"""
        if self.config.init_error or not self.client:
            return []
            
        try:
            print("  ↻ Fetching Anthropic models from API...")
            # Real API call to prove key validity
            response = await self.client.models.list()
            
            models = []
            for m in response.data:
                # Filter useful models if necessary, or take all
                if m.type == 'model':
                    models.append(ModelInfo(
                        id=m.id,
                        name=m.display_name,
                        provider="Anthropic",
                        context_length=200000, # Anthropic usually doesn't return context length in list, default large
                        supports_streaming=True
                    ))
            
            # Use fallback cache if API returns empty but no error (rare)
            if not models:
                 raise ValueError("API returned no models")
                 
            print(f"  ✓ Fetched {len(models)} Anthropic models")
            return models
            
        except Exception as e:
            print(f"  ✗ Anthropic model fetch failed: {e}")
            raise e  # Fail loud -> Red Light
    
    async def stream_chat(
        self,
        model_id: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream chat completion from Anthropic"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        # Separate system messages
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        # Create streaming request
        kwargs = {
            "model": model_id,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        if system_message:
            kwargs["system"] = system_message
        
        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
