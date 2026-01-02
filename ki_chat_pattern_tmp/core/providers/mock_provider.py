import asyncio
from typing import AsyncGenerator, List
from .base_provider import BaseLLMProvider
from .types import Message, ModelInfo, ProviderConfig, ModelCapability

class MockProvider(BaseLLMProvider):
    async def initialize(self) -> None:
        pass

    async def get_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                id="mock-gpt-4", 
                name="Mock GPT-4", 
                provider="MockProvider", 
                context_window=100000,
                capabilities=[ModelCapability.CHAT]
            ),
            ModelInfo(
                id="mock-claude", 
                name="Mock Claude", 
                provider="MockProvider",
                context_window=200000,
                capabilities=[ModelCapability.CHAT]
            )
        ]

    async def stream_chat(
        self, 
        model_id: str, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        response_text = f"This is a mocked response from {model_id}. I received your message: '{messages[-1].content}'. Here is some streaming data..."
        
        # Simulate thinking
        await asyncio.sleep(0.5)
        
        words = response_text.split(" ")
        for word in words:
            yield word + " "
            await asyncio.sleep(0.05) # Simulate token generation delay

    async def check_health(self) -> bool:
        return True
