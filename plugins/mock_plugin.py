"""
Mock Provider Plugin
A simple mock provider for testing without real API calls
"""
import asyncio
from typing import AsyncIterator
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo


class MockProvider(BaseLLMProvider):
    """Mock provider for testing"""
    
    async def initialize(self):
        """Mock initialization (always succeeds)"""
        print("✓ Mock Provider initialized")
    
    async def get_available_models(self) -> list[ModelInfo]:
        """Get list of mock models"""
        return [
            ModelInfo(
                id="mock-gpt-4",
                name="Mock GPT-4",
                provider="Mock",
                context_length=8000,
                supports_streaming=True
            ),
            ModelInfo(
                id="mock-claude",
                name="Mock Claude",
                provider="Mock",
                context_length=100000,
                supports_streaming=True
            ),
        ]
    
    async def stream_chat(
        self,
        messages: list[Message],
        model_id: str = "mock-gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Simulate streaming response"""
        response = f"This is a mock response from {model_id}. Your message was: '{messages[-1].content}'"
        
        # Simulate streaming by yielding word by word
        words = response.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.05)  # Simulate network delay
