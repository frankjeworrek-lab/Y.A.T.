from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Any
from .types import Message, ModelInfo, ProviderConfig

class BaseLLMProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider (e.g. validate clients)."""
        pass

    @abstractmethod
    async def get_models(self) -> List[ModelInfo]:
        """Fetch available models from the provider."""
        pass

    @abstractmethod
    async def stream_chat(
        self, 
        model_id: str, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from the provider."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the provider is reachable and configured correctly."""
        pass
