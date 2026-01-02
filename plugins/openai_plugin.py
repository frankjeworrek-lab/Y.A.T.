"""
OpenAI Provider Plugin
Provides integration with OpenAI's API (GPT-4, GPT-3.5, etc.)
Authentic behavior: Dynamic models and standard parameters.
"""
import os
from typing import AsyncIterator
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider with Dynamic Model Loading"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        self.api_key = None
        # Cache models to avoid fetching on every click
        self._model_cache = []
    
    async def initialize(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            self.config.init_error = "API key not found. Set OPENAI_API_KEY environment variable."
            return
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
            print(f"✓ OpenAI Provider initialized")
        except Exception as e:
            self.config.init_error = f"Failed to initialize: {str(e)}"
            print(f"✗ OpenAI initialization failed: {e}")
    
    async def check_health(self) -> bool:
        """Check if provider is healthy"""
        return self.client is not None and self.api_key is not None
    
    async def get_models(self) -> list[ModelInfo]:
        """Alias for get_available_models (required by base class)"""
        return await self.get_available_models()
    
    async def get_available_models(self) -> list[ModelInfo]:
        """Fetch real list of available OpenAI models dynamically"""
        if not self.client:
            return []
            
        # Return cached models if available (performance)
        if self._model_cache:
            return self._model_cache
            
        try:
            print("  ↻ Fetching OpenAI models from API...")
            response = await self.client.models.list()
            
            # Filter and process models
            models = []
            
            # Models we definitely want to ignore
            ignored_keywords = [
                "audio", "whisper", "tts", "dall-e", "davinci", "babbage", "curie", 
                "embedding", "moderation", "realtime", "instruct"
            ]
            
            for m in response.data:
                mid = m.id
                
                # Filter out non-chat models
                if any(keyword in mid for keyword in ignored_keywords):
                    continue
                
                # Filter for known chat prefixes or specific recently added models
                if not (mid.startswith("gpt-") or mid.startswith("o1-") or "chat" in mid or "ft:" in mid):
                     continue

                # Create ModelInfo
                info = ModelInfo(
                    id=mid,
                    name=mid, # Map specific IDs to nicer names if needed
                    provider="OpenAI",
                    # Context length is hard to guess from API, defaulting conservatively or checking ID
                    context_length=128000 if "gpt-4" in mid or "o1-" in mid else 16385,
                    supports_streaming=True
                )
                models.append(info)
            
            # Sort: GPT-4o first, then GPT-4, then the rest
            models.sort(key=lambda x: (
                not x.id.startswith("gpt-4o"), 
                not x.id.startswith("gpt-4"),
                x.id
            ))
            
            self._model_cache = models
            print(f"  ✓ Fetched {len(models)} OpenAI models")
            return models
            
        except Exception as e:
            print(f"  ✗ Failed to fetch models: {e}")
            # Fallback to defaults if API fails
            return [
                ModelInfo(id="gpt-4o", name="GPT-4o (Fallback)", provider="OpenAI", context_length=128000),
                ModelInfo(id="gpt-3.5-turbo", name="GPT-3.5 Turbo (Fallback)", provider="OpenAI", context_length=16385),
            ]
    
    async def stream_chat(
        self,
        model_id: str,
        messages: list[Message],
        temperature: float = None,  # Optional!
        max_tokens: int = None      # Optional!
    ) -> AsyncIterator[str]:
        """Stream chat completion from OpenAI"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        # Prepare System Context (Time, Date, OS)
        import datetime
        import platform
        
        now = datetime.datetime.now()
        system_context = (
            f"Current Date: {now.strftime('%A, %B %d, %Y')}\n"
            f"Current Time: {now.strftime('%H:%M:%S')}\n"
            f"Operating System: {platform.system()} {platform.release()}\n"
            f"User Environment: Desktop App (NiceGUI)\n"
            "You are a helpful, professional AI assistant."
        )
        
        # Convert messages to OpenAI format and prepend System Context
        openai_messages = [
            {"role": "system", "content": system_context}
        ]
        
        for msg in messages:
            # Check if there is already a system message, if so append to context
            if msg.role.value == "system":
                openai_messages[0]["content"] += f"\n\n{msg.content}"
            else:
                openai_messages.append({"role": msg.role.value, "content": msg.content})
        
        # Prepare request arguments - authentic behavior
        # Only pass parameters if explicitly provided, else use OpenAI defaults
        kwargs = {
            "model": model_id,
            "messages": openai_messages,
            "stream": True
        }
        
        # O1 and reasoning models do not support temperature
        is_reasoning_model = any(x in model_id for x in ["o1-", "search-", "reasoning"])
        
        if temperature is not None and not is_reasoning_model:
            kwargs["temperature"] = temperature
            
        if max_tokens is not None:
             kwargs["max_tokens"] = max_tokens
        
        try:
            stream = await self.client.chat.completions.create(**kwargs)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {e}"
