"""
Mistral AI Provider Plugin
"""
import os
from typing import AsyncIterator
from openai import AsyncOpenAI

from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo, Role

class MistralProvider(BaseLLMProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None

    async def initialize(self):
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            self.config.init_error = "MISTRAL_API_KEY not found"
            return

        try:
            self.client = AsyncOpenAI(
                base_url="https://api.mistral.ai/v1",
                api_key=api_key
            )
            print(f"[OK] Mistral initialized")
        except Exception as e:
            self.config.init_error = str(e)

    async def check_health(self) -> bool:
        return self.client is not None

    async def get_models(self) -> list[ModelInfo]:
        if not self.client: return []
        try:
            response = await self.client.models.list()
            models = []
            for m in response.data:
                # Include standard models
                if "mistral" in m.id or "mixtral" in m.id:
                    models.append(ModelInfo(
                        id=m.id,
                        name=m.id,
                        provider="Mistral",
                        context_length=32000,
                        supports_streaming=True
                    ))
            return models
        except Exception as e:
            print(f"  [ERR] Mistral fetch failed: {e}")
            raise e

    async def stream_chat(self, model_id: str, messages: list[Message], temperature=0.7, max_tokens=2000) -> AsyncIterator[str]:
        if not self.client: raise RuntimeError("Mistral not initialized")
        
        formatted_msgs = [{"role": "system" if m.role == Role.SYSTEM else m.role.value, "content": m.content} for m in messages]

        stream = await self.client.chat.completions.create(
            model=model_id,
            messages=formatted_msgs,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
