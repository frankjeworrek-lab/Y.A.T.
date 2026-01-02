import flet as ft
import asyncio
from dotenv import load_dotenv
from core.llm_manager import LLMManager
from core.providers.mock_provider import MockProvider
from core.providers.types import ProviderConfig
from ui.app_layout import AppLayout

load_dotenv(override=True)

async def main(page: ft.Page):
    page.title = "KI Chat Pattern"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_min_width = 800
    page.window_min_height = 600
    
    # Initialize Core Logic
    llm_manager = LLMManager()
    
    # Register Mock Provider (add real ones later via config)
    mock_config = ProviderConfig(name="Mock Provider")
    llm_manager.register_provider("mock", MockProvider(mock_config))
    
    from core.providers.openai_provider import OpenAIProvider
    openai_config = ProviderConfig(name="OpenAI")
    openai_provider = OpenAIProvider(openai_config)
    await openai_provider.initialize()
    llm_manager.register_provider("openai", openai_provider)
    
    from core.providers.anthropic_provider import AnthropicProvider
    anthropic_config = ProviderConfig(name="Anthropic")
    anthropic_provider = AnthropicProvider(anthropic_config)
    await anthropic_provider.initialize()
    llm_manager.register_provider("anthropic", anthropic_provider)
    
    # Set init defaults
    llm_manager.active_provider_id = "mock"
    llm_manager.active_model_id = "mock-gpt-4"

    # Create Main Layout
    layout = AppLayout(page, llm_manager)
    
    page.add(layout)
    
    # Initial load of models
    await layout.initialize_async()

if __name__ == "__main__":
    ft.app(target=main)
