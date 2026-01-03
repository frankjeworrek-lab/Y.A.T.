"""
Y.A.T. (Yet Another Talk) - NiceGUI Application
Unified launcher supporting both Desktop (native window) and Web (browser) modes.

Usage:
    python main.py          # Desktop mode (default, native window via PyWebView)
    python main.py --web    # Web mode (opens in browser)
"""
import asyncio
import argparse
import sys
import os
from dotenv import load_dotenv
from nicegui import ui, app
from core.llm_manager import LLMManager
from core.providers.types import ProviderConfig
from ui_nicegui.app_layout import AppLayout

def resolve_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load secrets from resolved path
# Load secrets from resolved path (bundled defaults)
load_dotenv(resolve_path('.env'))

# Load secrets from user data directory (user overrides)
from core.paths import get_data_path
load_dotenv(get_data_path('.env'), override=True)

# Ensure data directory exists
from core.paths import ensure_data_dir
ensure_data_dir()

# DEBUG: Write version marker to prove this code is running
from core.paths import get_data_path
import datetime
try:
    with open(get_data_path('init_marker.txt'), 'w') as f:
        f.write(f"Version: v0.2.1-marker\nTimestamp: {datetime.datetime.now()}\nPlatform: {sys.platform}\n")
except Exception as e:
    print(f"Failed to write marker: {e}")

# Global LLM Manager (initialized on startup)
llm_manager = None

# Serve logo directory from resolved path
app.add_static_files('/logo', resolve_path('logo'))


async def initialize_providers():
    """Initialize all providers via plugin auto-discovery"""
    global llm_manager
    
    if llm_manager is not None:
        return  # Already initialized
    
    from core.plugin_loader import PluginLoader
    from core.provider_config_manager import ProviderConfigManager
    
    llm_manager = LLMManager()
    
    # Load provider configurations
    config_manager = ProviderConfigManager()
    
    # Auto-discover and load plugins
    plugin_loader = PluginLoader(plugins_dir=resolve_path("plugins"))
    plugins = plugin_loader.load_all_plugins()
    
    print(f"\n[PLUGIN] Loaded {len(plugins)} plugin(s)")
    
    # Register each loaded plugin
    for plugin_name, provider_class in plugins.items():
        # Get configuration for this provider
        provider_id = plugin_name.replace('_plugin', '')
        provider_config = config_manager.get_provider(provider_id)
        
        # SKIP if provider is disabled in config
        if provider_config and not provider_config.enabled:
            print(f"  [-] Skipped: {provider_id} (disabled in config)")
            continue
        
        if not provider_config:
            # Use default config if not in provider_config.json
            provider_config_obj = ProviderConfig(name=plugin_name)
        else:
            # Transfer config details from Manager (Dataclass) to Plugin (Pydantic)
            provider_config_obj = ProviderConfig(
                name=provider_config.name,
                status=provider_config.status,
                base_url=provider_config.config.get('base_url'),
                api_key=os.getenv(provider_config.config.get('api_key_env', '')) if provider_config.type == 'cloud' else None
            )
        
        # Create and initialize provider instance
        try:
            provider_instance = provider_class(provider_config_obj)
            await provider_instance.initialize()
            
            # Register with LLMManager
            llm_manager.register_provider(provider_id, provider_instance)
            
            print(f"  [+] Registered: {provider_id}")
        except Exception as e:
            print(f"  [X] Failed to register {plugin_name}: {e}")
    
    # Set intelligent defaults
    # Set intelligent defaults
    from core.user_config import UserConfig
    enabled_providers = config_manager.get_enabled_providers()
    
    # Strict Config Adherence Logic
    # ------------------------------------------------------------------
    # 1. Load explicit ACTIVE PROVIDER from UserConfig
    active_provider_id = None
    saved_active_provider = UserConfig.get('active_provider_id')
    
    if saved_active_provider and saved_active_provider in llm_manager.providers:
         # CASE A: We have a saved choice. WE OBEY IT.
         # No checks for enabled status. No checks for successful init.
         # You save what you get.
         active_provider_id = saved_active_provider
         print(f"[OK] Config: Leaning on saved provider '{active_provider_id}'")
    
    elif enabled_providers:
        # CASE B: First run / No config. 
        # USER REQUEST: No fallbacks. The user sees the truth (nothing selected).
        # active_provider_id = enabled_providers[0].id
        print(f"[OK] Config: No saved provider. Starting with NONE.")
        active_provider_id = None
        
    # 2. Set the Active Provider in Manager
    if active_provider_id:
        llm_manager.active_provider_id = active_provider_id
        
        # 3. Try to restore last model (UI sugar only)
        # We try to make the UI nice, but we don't change the provider based on this.
        provider_instance = llm_manager.providers.get(active_provider_id)
        if provider_instance:
            last_model = UserConfig.get('last_model')
            target_model_id = None
            
            # extract model id if it matches our provider
            if last_model and last_model.startswith(active_provider_id + '|'):
                 try:
                     _, mid = last_model.split('|', 1)
                     target_model_id = mid
                 except ValueError:
                     pass
            
            # Try to fetch models to validate target_model_id
            try:
                models = await provider_instance.get_available_models()
                if not models:
                    raise ValueError("No models available (check credentials)")
                    
                if target_model_id and any(m.id == target_model_id for m in models):
                    llm_manager.active_model_id = target_model_id
                else:
                    llm_manager.active_model_id = models[0].id
                print(f"[OK] Active Model: {llm_manager.active_model_id}")
                
                # Clear error if success AND Upgrade status to active (Verified)
                provider_instance.config.init_error = None
                provider_instance.config.status = "active"
            except Exception as e:
                # If fetching models fails (e.g. invalid key), we still stay on this provider!
                # We just can't set a model ID yet. The UI will show the error.
                error_msg = f"Error code: {str(e)}" # Simplified error
                if "401" in str(e):
                    error_msg = "Invalid API Key (401)"
                
                print(f"  Confirming active provider '{active_provider_id}' despite model fetch error: {e}")
                provider_instance.config.init_error = error_msg
                # Status remains "configured" (or "error" if we wanted to be strict, but init_error handles the UI red flag)
    
    print("[OK] Plugin-based providers initialized successfully\n")


@ui.page('/', title='Y.A.T.')
async def main_page():
    """Main application page"""
    # Remove default padding/gap to prevent scrollbars
    ui.context.client.content.classes('p-0 gap-0')
    
    # FORCE NO SCROLLBARS on the main window
    ui.add_head_html('<style>body { overflow: hidden !important; }</style>')
    
    # THEME ENGINE: Default CSS Variables
    ui.add_head_html('''
    <style>
    :root {
        --bg-primary: #0f1117;
        --bg-secondary: #1f2937;
        --bg-accent: #111827;
        --border-color: #374151;
        --text-primary: #e5e7eb;
        --text-secondary: #9ca3af;
        --accent-color: #4299e1;
        --success-color: #4ade80;
        --error-color: #f87171;
    }
    </style>
    ''')

    # Ensure providers are initialized
    await initialize_providers()
    
    # Create and build layout
    app_layout = AppLayout(llm_manager)
    app_layout.build()
    
    # Initialize async components
    await app_layout.initialize_async()


def start_web_mode():
    """Start in Web/Browser mode"""
    print("[*] Starting Y.A.T. (Web Mode)...")
    ui.run(
        title='Y.A.T.',
        dark=True,
        reload=False,
        show=True,  # Auto-open browser
        port=8080,
        binding_refresh_interval=0.1,
    )


def start_desktop_mode():
    """Start in Desktop mode with native window"""
    import webview
    import threading
    import time
    
    print("[*] Starting Y.A.T. (Desktop Mode)...")
    print("   Architect: Frank Jeworrek")
    
    def start_nicegui_server():
        """Start NiceGUI server in background thread"""
        ui.run(
            title='Y.A.T.',
            favicon=resolve_path('logo/dock.png'),
            dark=True,
            reload=False,
            show=False,  # Don't open browser - PyWebView will handle display
            port=8080,
            binding_refresh_interval=0.1,
        )
    
    # Start NiceGUI server in separate thread
    server_thread = threading.Thread(target=start_nicegui_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Create native desktop window with PyWebView
    print("[*] Creating desktop window...")
    webview.create_window(
        title='Y.A.T.',
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
    
    print("[*] Desktop app closed")


if __name__ in {"__main__", "__mp_main__"}:
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Y.A.T. - AI Chat Application'
    )
    parser.add_argument(
        '--web',
        action='store_true',
        help='Run in web mode (browser) instead of desktop mode (default)'
    )
    
    args = parser.parse_args()
    
    # Launch appropriate mode
    if args.web:
        start_web_mode()
    else:
        start_desktop_mode()
