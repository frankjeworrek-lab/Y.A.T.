"""
Groq Provider Plugin
"""
import os
from typing import AsyncIterator
from openai import AsyncOpenAI

from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo, Role

class GroqProvider(BaseLLMProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None

    async def initialize(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            self.config.init_error = "GROQ_API_KEY not found"
            return

        try:
            self.client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
            print(f"[OK] Groq initialized")
        except Exception as e:
            self.config.init_error = str(e)

    async def check_health(self) -> bool:
        return self.client is not None

    async def get_models(self) -> list[ModelInfo]:
        if not self.client: return []
        try:
            # Groq model list requires auth
            response = await self.client.models.list()
            models = []
            for m in response.data:
                models.append(ModelInfo(
                    id=m.id,
                    name=m.id,
                    provider="Groq",
                    context_length=8192,
                    supports_streaming=True
                ))
            return models
        except Exception as e:
            print(f"  [ERR] Groq fetch failed: {e}")
            raise e

    async def stream_chat(self, model_id: str, messages: list[Message], temperature=0.7, max_tokens=2000) -> AsyncIterator[str]:
        if not self.client: raise RuntimeError("Groq not initialized")
        
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
