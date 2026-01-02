import os
from typing import AsyncGenerator, List
from anthropic import AsyncAnthropic
from .base_provider import BaseLLMProvider
from .types import Message, ModelInfo, ProviderConfig, ModelCapability

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        
    async def initialize(self) -> None:
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            # Silent fallback: Just don't enable provider, don't show error
            print("Warning: Anthropic API Key not found.")
            return
            
        self.client = AsyncAnthropic(api_key=api_key, base_url=self.config.base_url)

    async def get_models(self) -> List[ModelInfo]:
        if not self.client:
            return []
        
        # Anthropic doesn't have a public models list API endpoint that is standard like OpenAI's
        # robust implementation usually hardcodes these or fetches from a config
        return [
            ModelInfo(id="claude-3-opus-20240229", name="Claude 3 Opus", provider="Anthropic"),
            ModelInfo(id="claude-3-sonnet-20240229", name="Claude 3 Sonnet", provider="Anthropic"),
            ModelInfo(id="claude-3-haiku-20240307", name="Claude 3 Haiku", provider="Anthropic"),
        ]

    async def stream_chat(
        self, 
        model_id: str, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "Display Error: Anthropic client not initialized"
            return

        # Anthropic format: system message is separate
        system_prompt = ""
        filtered_messages = []
        
        for m in messages:
            if m.role.value == "system":
                system_prompt += m.content + "\n"
            else:
                filtered_messages.append({"role": m.role.value, "content": m.content})

        try:
            stream = await self.client.messages.create(
                model=model_id,
                messages=filtered_messages,
                system=system_prompt,
                max_tokens=4096,
                stream=True
            )

            async for event in stream:
                if event.type == "content_block_delta":
                    yield event.delta.text
        except Exception as e:
            yield f"Error: {e}"

    async def check_health(self) -> bool:
        return self.client is not None
