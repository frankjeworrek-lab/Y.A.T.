import os
from typing import AsyncGenerator, List
from openai import AsyncOpenAI
from .base_provider import BaseLLMProvider
from .types import Message, ModelInfo, ProviderConfig, ModelCapability

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        
    async def initialize(self) -> None:
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.config.init_error = "No Key found (Check .env / Docs)"
            print(f"Warning: {self.config.name} API Key not found.")
            return
            
        self.client = AsyncOpenAI(api_key=api_key, base_url=self.config.base_url)

    async def get_models(self) -> List[ModelInfo]:
        if not self.client:
            return []
            
        try:
            # For efficiency we might hardcode common models or fetch them
            # Fetching is better for "professional" robust app
            models_list = await self.client.models.list()
            
            # Filter relevant models (cleaner list, chat only)
            def is_relevant(mid):
                exclusions = ["vision", "audio", "realtime", "transcribe", "diarize", "-03", "-06", "-01", "instruct"]
                return ("gpt-4" in mid or "gpt-3.5-turbo" in mid) and not any(x in mid for x in exclusions)
            
            gpt_models = [m for m in models_list.data if is_relevant(m.id)]
            # Sort: GPT-4 first
            gpt_models.sort(key=lambda x: x.id, reverse=True)
            
            return [
                ModelInfo(
                    id=m.id,
                    name=m.id,
                    provider="OpenAI",
                    capabilities=[ModelCapability.CHAT]
                ) for m in gpt_models
            ]
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                sanitized_key = f"{self.client.api_key[:7]}..." if self.client and self.client.api_key else "None"
                print(f"DEBUG: 401 Error. Using Key: {sanitized_key}")
                self.config.init_error = "Invalid API Key (401)"
            elif "429" in error_msg:
                self.config.init_error = "Rate Limit / Quota Exceeded (429)"
            else:
                self.config.init_error = f"Connection Error: {error_msg[:30]}..."
            
            print(f"Error fetching OpenAI models: {e}")
            return []

    async def stream_chat(
        self, 
        model_id: str, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "Display Error: OpenAI client not initialized (Missing API Key?)"
            return

        # Convert internal Message format to OpenAI format
        openai_messages = [
            {"role": m.role.value, "content": m.content} 
            for m in messages
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=model_id,
                messages=openai_messages,
                stream=True
            )

            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            yield f"Error: {e}"

    async def check_health(self) -> bool:
        return self.client is not None
