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
        
        if not self.api_key:
            self.config.init_error = "API key not found. Set ANTHROPIC_API_KEY environment variable."
            return
        
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.api_key)
            print(f"✓ Anthropic Provider initialized")
        except Exception as e:
            self.config.init_error = f"Failed to initialize: {str(e)}"
            print(f"✗ Anthropic initialization failed: {e}")
    
    async def get_available_models(self) -> list[ModelInfo]:
        """Get list of available Anthropic models"""
        return [
            ModelInfo(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                provider="Anthropic",
                context_length=200000,
                supports_streaming=True
            ),
            ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider="Anthropic",
                context_length=200000,
                supports_streaming=True
            ),
        ]
    
    async def stream_chat(
        self,
        messages: list[Message],
        model_id: str = "claude-3-5-sonnet-20241022",
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
