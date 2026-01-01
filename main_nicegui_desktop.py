"""
KI Chat Pattern - NiceGUI Desktop App (Native Window)
Uses PyWebView for true desktop window experience
"""
import asyncio
from dotenv import load_dotenv
from nicegui import ui, app
import webview
import threading
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
        # Get models from the provider instance
        provider_instance = llm_manager.providers.get(default_provider.id)
        if provider_instance:
            models = await provider_instance.get_available_models()
            if models:
                llm_manager.active_model_id = models[0].id
                print(f"\n✓ Default: {default_provider.name} / {models[0].name}")
    
    print("✓ Plugin-based providers initialized successfully\n")


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


def start_nicegui_server():
    """Start NiceGUI server in background thread"""
    ui.run(
        title='KI Chat Pattern',
        dark=True,
        reload=False,
        show=False,  # Don't open browser - PyWebView will handle display
        port=8080,
        binding_refresh_interval=0.1,
    )


if __name__ in {"__main__", "__mp_main__"}:
    print("🚀 Starting KI Chat Pattern (Desktop Mode)...")
    
    # Start NiceGUI server in separate thread
    server_thread = threading.Thread(target=start_nicegui_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be ready
    import time
    time.sleep(2)
    
    # Create native desktop window with PyWebView
    print("🪟 Creating desktop window...")
    webview.create_window(
        title='KI Chat Pattern',
        url='http://localhost:8080',
        width=1200,
        height=800,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        background_color='#1E1E1E',
        text_select=True,
    )
    
    # Start PyWebView (blocks until window is closed)
    webview.start(debug=False)
    
    print("👋 Desktop app closed")
