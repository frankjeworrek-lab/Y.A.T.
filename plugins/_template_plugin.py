"""
CUSTOM PROVIDER PLUGIN TEMPLATE
Copy this file to create your own LLM provider plugin!

Instructions:
1. Copy this file to plugins/your_provider_plugin.py
2. Rename the class from TemplateProvider to YourProviderName
3. Implement the three required methods
4. Add your provider to provider_config.json
5. Restart the app - your provider will be auto-discovered!

Example providers in plugins/:
- openai_plugin.py
- anthropic_plugin.py
- mock_plugin.py
"""
import os
from typing import AsyncIterator
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo


class TemplateProvider(BaseLLMProvider):
    """
    Template for creating custom LLM providers
    
    Replace this docstring with your provider description.
    Example: "Cohere AI Provider for Command-R models"
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # Add custom instance variables here
        self.client = None
        self.api_key = None
    
    async def initialize(self):
        """
        Initialize your provider
        
        This is called once on app startup. Use it to:
        - Load API keys from environment
        - Create API client instances
        - CRITICAL: Perform a real API call (e.g. list_models or ping) to verify the key!
        - Set self.config.init_error if something fails
        """
        # Example: Load API key
        self.api_key = os.getenv('YOUR_PROVIDER_API_KEY')
        
        try:
            # TODO: Initialize your client here
            # self.client = MyClient(api_key=self.api_key)
            
            # TODO: Add a real Health Check here!
            # await self.client.models.list()  # <--- This forces the API to validate the key immediately
            
            print(f"✓ {self.config.name} initialized")
        except Exception as e:
            self.config.init_error = f"Failed to initialize: {str(e)}"
            print(f"✗ Your Provider initialization failed: {e}")
    
    async def get_available_models(self) -> list[ModelInfo]:
        """
        Return list of models your provider supports
        
        Returns:
            List of ModelInfo objects describing each model
        """
        return [
            ModelInfo(
                id="your-model-id",           # Internal model identifier
                name="Your Model Name",        # Display name in UI
                provider="Your Provider",      # Provider name
                context_length=4096,          # Max tokens in context
                supports_streaming=True        # Whether streaming is supported
            ),
            # Add more models here...
        ]
    
    async def stream_chat(
        self,
        messages: list[Message],
        model_id: str = "your-default-model",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """
        Stream chat completion from your provider
        
        Args:
            messages: Conversation history (list of Message objects)
            model_id: Which model to use
            temperature: Randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Text chunks as they arrive from the API
            
        Raises:
            RuntimeError: If provider not initialized
        """
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        # Example implementation:
        # 1. Convert messages to your provider's format
        # provider_messages = [
        #     {"role": msg.role.value, "content": msg.content}
        #     for msg in messages
        # ]
        
        # 2. Call your provider's streaming API
        # stream = await self.client.chat.stream(
        #     model=model_id,
        #     messages=provider_messages,
        #     temperature=temperature,
        #     max_tokens=max_tokens
        # )
        
        # 3. Yield text chunks as they arrive
        # async for chunk in stream:
        #     if chunk.text:
        #         yield chunk.text
        
        # Placeholder implementation (remove this):
        yield "Replace this with actual API call to your provider"


# That's it! Your provider is now ready to be auto-discovered.
# Add it to provider_config.json and restart the app.
