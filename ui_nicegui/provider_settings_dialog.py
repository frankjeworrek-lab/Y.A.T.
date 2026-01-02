"""
Provider Settings Dialog for NiceGUI
Comprehensive provider management interface
"""
from nicegui import ui
import os
from pathlib import Path
from core.provider_config_manager import ProviderConfigManager


class ProviderSettingsDialog:
    def __init__(self, llm_manager=None, sidebar=None):
        self.dialog = None
        self.config_manager = ProviderConfigManager()
        self.llm_manager = llm_manager
        self.sidebar = sidebar
        self.provider_inputs = {}
        self.pending_active_provider = None  # Staged change until Save
        
    def show(self):
        """Show the provider settings dialog"""
        with ui.dialog() as self.dialog, ui.card().classes('w-full max-w-4xl p-6').style(
            'background-color: #1f2937; border: 1px solid #374151; max-height: 80vh; overflow-y: auto;'
        ):
            # Header
            with ui.row().classes('w-full items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-3'):
                    ui.icon('settings', size='lg').classes('text-blue-400')
                    ui.label('Provider Management').classes('text-2xl font-bold text-white')
                ui.button(icon='close', on_click=self.dialog.close).props('flat round').classes('text-gray-400')
            
            ui.separator().classes('bg-gray-700 mb-4')
            
            # Info text
            ui.label('Configure and manage AI providers').classes('text-sm text-gray-400 mb-4')
            
            # Provider List Container (refreshable)
            self.provider_list_container = ui.column().classes('w-full')
            self._render_provider_list()
            
            ui.separator().classes('bg-gray-700 my-4')
            
            # Buttons
            with ui.row().classes('w-full justify-end gap-3'):
                ui.button('Cancel', on_click=self.dialog.close).props('outline').classes('text-gray-300')
                ui.button('Save & Apply', icon='save', on_click=self._save_settings).style(
                    'background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);'
                )
        
        self.dialog.open()
    
    def _render_provider_list(self):
        """Render provider cards (can be called to refresh)"""
        self.provider_list_container.clear()
        
        with self.provider_list_container:
            if self.llm_manager:
                loaded_provider_ids = list(self.llm_manager.providers.keys())
                for provider in self.config_manager.get_all_providers():
                    if provider.id in loaded_provider_ids:
                        self._build_provider_card(provider)
            else:
                for provider in self.config_manager.get_all_providers():
                    self._build_provider_card(provider)
    
    def _build_provider_card(self, provider):
        """Build a card for a single provider"""
        # Determine intelligent status (check pending selection first)
        is_active = (provider.id == self.pending_active_provider) if self.pending_active_provider else (self.llm_manager and provider.id == self.llm_manager.active_provider_id)
        
        # Check if API key exists
        api_key_setting = next((s for s in provider.settings if s['key'] == 'api_key'), None)
        has_key = False
        if api_key_setting and api_key_setting.get('env_var'):
            has_key = bool(os.getenv(api_key_setting['env_var']))
        
        # Status logic
        if is_active:
            status_text = "ACTIVE"
            status_color = "green"
            status_icon = "check_circle"
        elif has_key:
            status_text = "READY"
            status_color = "blue"
            status_icon = "verified"
        else:
            status_text = "NO KEY"
            status_color = "orange"
            status_icon = "key_off"
        
        with ui.card().classes('w-full mb-4 p-4').style(
            'background-color: #111827; border: 1px solid #374151;'
        ):
            # Header row
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center gap-3'):
                    # Radio button for activation (always clickable - validation on click)
                    if is_active:
                        ui.icon('radio_button_checked', size='sm').classes('text-green-400')
                    else:
                        ui.button(
                            icon='radio_button_unchecked',
                            on_click=lambda pid=provider.id: self._activate_provider(pid)
                        ).props('flat dense round').classes('text-gray-500 hover:text-blue-400')
                    
                    # Icon
                    ui.icon(provider.icon, size='md').classes(f'text-{provider.color}-400')
                    
                    # Name and type
                    with ui.column().classes('gap-1'):
                        ui.label(provider.name).classes('text-lg font-bold text-white')
                        ui.label(f'{provider.type.capitalize()} Provider').classes('text-xs text-gray-500')
                
                # Status badge and icon
                with ui.row().classes('items-center gap-2'):
                    ui.icon(status_icon, size='sm').classes(f'text-{status_color}-400')
                    ui.badge(status_text, color=status_color).classes('text-xs font-bold')
            
            # Info text
            if is_active:
                ui.label('🟢 Currently in use for chat').classes('text-xs text-green-400 mb-2')
            elif has_key:
                ui.label('💡 Ready to use. Select a model from sidebar to activate.').classes('text-xs text-blue-400 mb-2')
            else:
                ui.label('⚠️ API key required. Enter below to enable this provider.').classes('text-xs text-orange-400 mb-2')
            
            # Settings (always show, user can configure keys even if not active)
            with ui.column().classes('w-full gap-3 mt-3 pt-3 border-t border-gray-700'):
                for setting in provider.settings:
                    self._build_setting_input(provider, setting)
    
    def _build_setting_input(self, provider, setting):
        """Build an input field for a provider setting"""
        # Get current value
        current_value = self.config_manager.get_provider_setting_value(
            provider.id, 
            setting['key']
        ) or setting.get('default', '')
        
        # Create appropriate input type
        input_key = f"{provider.id}_{setting['key']}"
        
        with ui.row().classes('w-full items-center gap-3'):
            ui.label(setting['label']).classes('text-sm text-gray-300 w-32')
            
            if setting['type'] == 'password':
                self.provider_inputs[input_key] = ui.input(
                    placeholder=f"Enter {setting['label']}",
                    value=current_value,
                    password=True,
                    password_toggle_button=True
                ).classes('flex-1').props('outlined dense dark').style(
                    'background-color: #1f2937;'
                )
            elif setting['type'] == 'boolean':
                self.provider_inputs[input_key] = ui.switch(
                    value=current_value == 'true'
                ).classes('flex-1')
            else:  # text, number
                self.provider_inputs[input_key] = ui.input(
                    placeholder=f"Enter {setting['label']}",
                    value=current_value
                ).classes('flex-1').props('outlined dense dark').style(
                    'background-color: #1f2937;'
                )
            
            if setting.get('required'):
                ui.label('*').classes('text-red-400 text-sm')
    
    def _activate_provider(self, provider_id: str):
        """Stage provider activation (applied on Save)"""
        self.pending_active_provider = provider_id
        # Refresh UI to show checked radio button
        self._render_provider_list()
    
    def _toggle_provider(self, provider_id: str, enabled: bool):
        """Toggle provider enabled/disabled"""
        if enabled:
            self.config_manager.enable_provider(provider_id)
        else:
            self.config_manager.disable_provider(provider_id)
        
        # Refresh dialog
        self.dialog.close()
        self.show()
    
    def _save_settings(self):
        """Save all provider settings"""
        # Update environment variables and configs
        for input_key, input_widget in self.provider_inputs.items():
            provider_id, setting_key = input_key.split('_', 1)
            
            provider = self.config_manager.get_provider(provider_id)
            if not provider:
                continue
            
            # Find the setting definition
            setting_def = next(
                (s for s in provider.settings if s['key'] == setting_key),
                None
            )
            if not setting_def:
                continue
            
            # Get value
            if setting_def['type'] == 'boolean':
                value = 'true' if input_widget.value else 'false'
            else:
                value = input_widget.value
            
            # Save to environment if has env_var (API keys)
            if setting_def.get('env_var') and value:
                os.environ[setting_def['env_var']] = value
                
                # Also save to .env file (ONLY here, NOT in provider_config.json!)
                self._update_env_file(setting_def['env_var'], value)
            
            # Update provider config ONLY for non-API-key settings
            # API keys should NEVER be in provider_config.json
            if setting_key != 'api_key':
                self.config_manager.update_provider_config(
                    provider_id,
                    {setting_key: value}
                )
        
        # Re-initialize all providers to pick up new/removed API keys
        if self.llm_manager:
            import asyncio
            async def reinit_providers():
                # Determine active provider  ID
                active_pid = self.pending_active_provider or self.llm_manager.active_provider_id
                
                # 1. ACTIVE provider FIRST (critical errors show immediately!)
                if active_pid and active_pid in self.llm_manager.providers:
                    try:
                        await self.llm_manager.providers[active_pid].initialize()
                        print(f"✓ Re-initialized (ACTIVE): {active_pid}")
                    except Exception as e:
                        print(f"✗ Re-init failed (ACTIVE): {active_pid}: {e}")
                    
                    # Refresh Sidebar immediately after active provider init
                    # This updates the "Active: ..." badge and error status
                    if self.sidebar:
                        await self.sidebar.load_models()
                
                # 2. Other providers (background)
                for pid, provider in self.llm_manager.providers.items():
                    if pid != active_pid:
                        try:
                            await provider.initialize()
                            print(f"✓ Re-initialized: {pid}")
                        except Exception as e:
                            print(f"✗ Re-init failed: {pid}: {e}")
            
            asyncio.create_task(reinit_providers())
        
        # Apply pending provider activation (if any)
        if self.pending_active_provider and self.llm_manager:
            provider_instance = self.llm_manager.providers.get(self.pending_active_provider)
            if provider_instance:
                self.llm_manager.active_provider_id = self.pending_active_provider
                
                # Select first model from this provider
                import asyncio
                async def set_model():
                    try:
                        models = await provider_instance.get_available_models()
                        if models:
                            self.llm_manager.active_model_id = models[0].id
                            print(f'✓ Activated: {self.pending_active_provider} / {models[0].name}')
                    except Exception as e:
                        print(f'✗ Error loading models: {e}')
                
                asyncio.create_task(set_model())
        
        ui.notify('Settings saved! Providers reloaded.', type='positive')
        self.dialog.close()
    
    def _update_env_file(self, key: str, value: str):
        """Update .env file with new value"""
        env_path = Path('.env')
        
        # Read existing .env content
        env_content = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env_content[k.strip()] = v.strip()
        
        # Update value
        if value:
            env_content[key] = value
        elif key in env_content:
            del env_content[key]
        
        # Write back
        with open(env_path, 'w') as f:
            for k, v in env_content.items():
                f.write(f'{k}={v}\n')
