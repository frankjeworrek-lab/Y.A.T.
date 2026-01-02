from typing import Dict, List, Optional
from .providers.base_provider import BaseLLMProvider
from .providers.types import ProviderConfig, ModelInfo, Message

class LLMManager:
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.active_provider_id: Optional[str] = None
        self.active_model_id: Optional[str] = None
    
    def register_provider(self, provider_id: str, provider: BaseLLMProvider):
        self.providers[provider_id] = provider
        # Auto-select first provider if none selected
        if not self.active_provider_id:
            self.active_provider_id = provider_id

    async def get_all_models(self) -> List[ModelInfo]:
        all_models = []
        for provider_id, provider in self.providers.items():
            if provider.config.enabled:
                try:
                    models = await provider.get_models()
                    for m in models:
                        m.provider_id = provider_id # Inject the ID so UI knows which provider to call
                    all_models.extend(models)
                except Exception as e:
                    print(f"Error fetching models from {provider.config.name}: {e}")
        return all_models

    async def get_available_models(self) -> List[ModelInfo]:
        """Fetch models only from the currently active provider"""
        if not self.active_provider_id or self.active_provider_id not in self.providers:
            return []
            
        provider = self.providers[self.active_provider_id]
        try:
            models = await provider.get_models()
            for m in models:
                m.provider_id = self.active_provider_id
            return models
        except Exception as e:
            # Let the UI handle the empty list/error state
            print(f"Error fetching models from active provider {provider.config.name}: {e}")
            return []

    async def stream_chat(self, message_history: List[Message], provider_id: str = None, model_id: str = None):
        pid = provider_id or self.active_provider_id
        mid = model_id or self.active_model_id
        print(f"DEBUG: stream_chat using Provider='{pid}', Model='{mid}'")
        
        if not pid or pid not in self.providers:
            yield "Error: No active provider selected."
            return

        provider = self.providers[pid]
        try:
            async for chunk in provider.stream_chat(mid, message_history):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"
