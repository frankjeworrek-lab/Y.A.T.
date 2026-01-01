"""
KI Chat Pattern - NiceGUI Desktop Version
Main entry point for the NiceGUI implementation
"""
import asyncio
from dotenv import load_dotenv
from nicegui import ui, app
from core.llm_manager import LLMManager
from core.providers.mock_provider import MockProvider
from core.providers.types import ProviderConfig
from ui_nicegui.app_layout import AppLayout

load_dotenv(override=True)

# Global LLM Manager (initialized on startup)
llm_manager = None


async def initialize_providers():
    """Initialize all providers via plugin auto-discovery"""
    global llm_manager
    
    if llm_manager is not None:
        return  # Already initialized
    
    from core.plugin_loader import PluginLoader
    from core.provider_config_manager import ProviderConfigManager
    from core.providers.types import ProviderConfig
    
    llm_manager = LLMManager()
    
    # Load provider configurations
    config_manager = ProviderConfigManager()
    
    # Auto-discover and load plugins
    plugin_loader = PluginLoader(plugins_dir="plugins")
    plugins = plugin_loader.load_all_plugins()
    
    print(f"\n🔌 Plugin System: Loaded {len(plugins)} plugin(s)")
    
    # Register each loaded plugin
    for plugin_name, provider_class in plugins.items():
        # Get configuration for this provider
        provider_id = plugin_name.replace('_plugin', '')
        provider_config = config_manager.get_provider(provider_id)
        
        # SKIP if provider is disabled in config
        if provider_config and not provider_config.enabled:
            print(f"  ⊘ Skipped: {provider_id} (disabled in config)")
            continue
        
        if not provider_config:
            # Use default config if not in provider_config.json
            provider_config_obj = ProviderConfig(name=plugin_name)
        else:
            provider_config_obj = ProviderConfig(name=provider_config.name)
        
        # Create and initialize provider instance
        try:
            provider_instance = provider_class(provider_config_obj)
            await provider_instance.initialize()
            
            # Register with LLMManager
            llm_manager.register_provider(provider_id, provider_instance)
            
            print(f"  ✓ Registered: {provider_id}")
        except Exception as e:
            print(f"  ✗ Failed to register {plugin_name}: {e}")
    
    # Set intelligent defaults
    enabled_providers = config_manager.get_enabled_providers()
    if enabled_providers:
        default_provider = enabled_providers[0]
        llm_manager.active_provider_id = default_provider.id
        provider_instance = llm_manager.providers.get(default_provider.id)
        if provider_instance:
            models = await provider_instance.get_available_models()
            if models:
                llm_manager.active_model_id = models[0].id
                print(f"\n✓ Default: {default_provider.name} / {models[0].name}")


@ui.page('/')
async def main_page():
    """Main application page"""
    # Ensure providers are initialized
    await initialize_providers()
    
    # Create and build layout
    app_layout = AppLayout(llm_manager)
    app_layout.build()
    
    # Initialize async components
    await app_layout.initialize_async()


if __name__ in {"__main__", "__mp_main__"}:
    # NiceGUI Desktop Mode Options:
    # 
    # Option 1: Browser-based (current, easiest)
    # - Opens in default browser automatically
    # - Full NiceGUI features
    # - Easy to develop and debug
    
    # Option 2: Native window with PyWebView
    # - Install: pip install nicegui[native]
    # - Uncomment below section
    # - Comment out ui.run() section
    
    # from nicegui import native
    # native.start_server_and_native_window(
    #     main_page,
    #     window_title='KI Chat Pattern',
    #     width=1200,
    #     height=800,
    # )
    
    # Current: Browser-based (auto-opens in browser)
    ui.run(
        title='KI Chat Pattern',
        dark=True,
        reload=False,
        show=True,  # Auto-open browser
        port=8080,
        binding_refresh_interval=0.1,
    )
