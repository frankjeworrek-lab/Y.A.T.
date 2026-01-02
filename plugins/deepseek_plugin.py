"""
DeepSeek Provider Plugin
"""
import os
from typing import AsyncIterator
from openai import AsyncOpenAI

from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo, Role

class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None

    async def initialize(self):
        # Reset state
        self.config.init_error = None
        
        # Close old client
        if self.client:
           try: await self.client.close()
           except: pass

        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            self.config.init_error = "DEEPSEEK_API_KEY not found"
            return
        
        api_key = api_key.strip()

        try:
            self.client = AsyncOpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=api_key
            )
            print(f"[OK] DeepSeek initialized")
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
                # Filter for DeepSeek models specifically or list all
                models.append(ModelInfo(
                    id=m.id,
                    name=m.id,
                    provider="DeepSeek",
                    context_length=32000,
                    supports_streaming=True
                ))
            return models
        except Exception as e:
            print(f"  [ERR] DeepSeek fetch failed: {e}")
            raise e

    async def stream_chat(self, model_id: str, messages: list[Message], temperature=0.7, max_tokens=2000) -> AsyncIterator[str]:
        if not self.client: raise RuntimeError("DeepSeek not initialized")
        
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
