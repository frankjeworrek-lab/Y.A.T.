"""
Ollama Provider Plugin (Local)
"""
import os
from typing import AsyncIterator
from openai import AsyncOpenAI

from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo, Role

class OllamaProvider(BaseLLMProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        self.base_url = "http://localhost:11434/v1"

    async def initialize(self):
        # Override Base URL from config if set
        if self.config.config.get('base_url'):
            self.base_url = self.config.config.get('base_url') + "/v1" # Ensure /v1
            # Strip double /v1 if user added it
            if self.base_url.endswith("/v1/v1"):
                self.base_url = self.base_url[:-3]

        try:
            self.client = AsyncOpenAI(
                base_url=self.base_url,
                api_key="ollama" # not required but needed by client
            )
            print(f"[OK] Ollama initialized at {self.base_url}")
        except Exception as e:
            self.config.init_error = str(e)

    async def check_health(self) -> bool:
        return self.client is not None

    async def get_models(self) -> list[ModelInfo]:
        if not self.client: return []
        try:
            print(f"  [WAIT] Fetching Ollama models from {self.base_url}...")
            response = await self.client.models.list()
            models = []
            for m in response.data:
                models.append(ModelInfo(
                    id=m.id,
                    name=m.id.title(),
                    provider="Ollama",
                    context_length=4096, # Default guess
                    supports_streaming=True
                ))
            return models
        except Exception as e:
            print(f"  [ERR] Ollama fetch failed: {e}")
            raise e

    async def stream_chat(self, model_id: str, messages: list[Message], temperature=0.7, max_tokens=2000) -> AsyncIterator[str]:
        if not self.client: raise RuntimeError("Ollama not initialized")
        
        system_msg = None
        formatted_msgs = []
        for m in messages:
            if m.role == Role.SYSTEM:
                system_msg = m.content # Some models prefer system via API, but messages works too
                formatted_msgs.append({"role": "system", "content": m.content})
            else:
                 formatted_msgs.append({"role": m.role.value, "content": m.content})

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
