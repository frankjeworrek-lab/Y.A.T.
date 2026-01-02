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
        
    def show(self, initial_tab='providers'):
        """Show the unified settings dialog"""
        if self.llm_manager:
            self.pending_active_provider = self.llm_manager.active_provider_id
            
        with ui.dialog() as self.dialog, ui.card().classes('w-full max-w-4xl h-[85vh] p-0 flex flex-col overflow-hidden').style(
            'background-color: var(--bg-secondary); border: 1px solid var(--border-color);'
        ):
            # 1. FIXED HEADER
            with ui.column().classes('w-full p-6 pb-0 shrink-0 gap-0'):
                # Title & Close
                with ui.row().classes('w-full items-center justify-between mb-2'):
                    ui.label('Preferences').classes('text-2xl font-bold text-white')
                    ui.button(icon='close', on_click=self.dialog.close).props('flat round').classes('text-gray-400')
                
                # Helper for Theme Application
                def apply_theme(theme_vars):
                    js = ""
                    for k, v in theme_vars.items():
                        js += f"document.documentElement.style.setProperty('{k}', '{v}');"
                    ui.run_javascript(js)
                
                # Tabs
                with ui.tabs().classes('w-full text-gray-400') as tabs:
                    provider_tab = ui.tab('AI Providers', icon='smart_toy')
                    appearance_tab = ui.tab('Appearance', icon='palette')
                    
                # Set initial tab
                if initial_tab == 'appearance':
                    tabs.set_value(appearance_tab)
                else:
                    tabs.set_value(provider_tab)
                
                ui.separator().classes('bg-gray-700 mt-0')
            
            # 2. SCROLLABLE CONTENT (Flex-1)
            with ui.tab_panels(tabs, value=provider_tab if initial_tab != 'appearance' else appearance_tab, animated=False).classes(
                'w-full flex-1 overflow-y-auto min-h-0 bg-transparent p-6'
            ):
                
                # --- TAB 1: PROVIDERS ---
                with ui.tab_panel(provider_tab).classes('p-0'):
                    ui.label('Configure AI providers & API keys').classes('text-sm text-gray-400 mb-4')
                    self.provider_list_container = ui.column().classes('w-full')
                    self._render_provider_list()
                    # Spacer logic is handled by footer padding

                # --- TAB 2: APPEARANCE ---
                with ui.tab_panel(appearance_tab).classes('p-0'):
                    # 1. UI Scaling
                    ui.label('Interface Scale').classes('text-lg font-bold text-white mt-2')
                    with ui.row().classes('w-full items-center gap-4 mb-6'):
                        ui.icon('text_fields', size='sm').classes('text-gray-400')
                        ui.slider(min=12, max=20, step=1, value=16, 
                            on_change=lambda e: ui.run_javascript(f'document.documentElement.style.fontSize = "{e.value}px"')
                        ).props('label-always color=blue').classes('flex-1')
                        ui.icon('text_fields', size='lg').classes('text-gray-400')

                    ui.separator().classes('bg-gray-700 mb-4')

                    # 2. Themes Grid
                    ui.label('Theme Collection').classes('text-lg font-bold text-white mb-4')
                    themes = {
                        'Midnight Pro': {'--bg-primary': '#000000', '--bg-secondary': '#0a0a0a', '--bg-accent': '#141414', '--border-color': '#333333', '--text-primary': '#ffffff', '--text-secondary': '#888888', '--accent-color': '#e0e0e0'},
                        'Nordic Frost': {'--bg-primary': '#242933', '--bg-secondary': '#2e3440', '--bg-accent': '#3b4252', '--border-color': '#4c566a', '--text-primary': '#eceff4', '--text-secondary': '#d8dee9', '--accent-color': '#88c0d0'},
                        'Cyberpunk Neon': {'--bg-primary': '#0d0221', '--bg-secondary': '#1a0b2e', '--bg-accent': '#261447', '--border-color': '#ff00ff', '--text-primary': '#00fff5', '--text-secondary': '#b8b8b8', '--accent-color': '#ff00ff'},
                        'Retro Terminal': {'--bg-primary': '#0d1117', '--bg-secondary': '#161b22', '--bg-accent': '#21262d', '--border-color': '#30363d', '--text-primary': '#39d353', '--text-secondary': '#8b949e', '--accent-color': '#238636'},
                        'Dracula': {'--bg-primary': '#282a36', '--bg-secondary': '#44475a', '--bg-accent': '#6272a4', '--border-color': '#bd93f9', '--text-primary': '#f8f8f2', '--text-secondary': '#6272a4', '--accent-color': '#ff79c6'}
                    }
                    with ui.grid(columns=2).classes('w-full gap-4'):
                        for name, colors in themes.items():
                            with ui.card().classes('cursor-pointer hover:scale-105 transition-transform').style(
                                f'background-color: {colors["--bg-secondary"]}; border: 1px solid {colors["--border-color"]};'
                            ).on('click', lambda c=colors: apply_theme(c)):
                                with ui.row().classes('items-center gap-2'):
                                    ui.element('div').style(f'width: 20px; height: 20px; border-radius: 50%; background-color: {colors["--accent-color"]}')
                                    ui.label(name).style(f'color: {colors["--text-primary"]}')
            
            # 3. FIXED FOOTER (Only for Providers)
            with ui.row().classes('w-full p-6 pt-4 shrink-0 bg-transparent justify-end gap-3') as footer_row:
                ui.separator().classes('bg-gray-700 mb-4 w-full')
                ui.button('Cancel', on_click=self.dialog.close).props('outline').classes('text-gray-300')
                ui.button('Save Changes', icon='save', on_click=self._save_settings).style(
                    'background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);'
                )
            
            # Debug Info in Footer
            from core.paths import USER_DATA_DIR
            with ui.row().classes('w-full justify-center pb-2'):
                 ui.label(f'Data: {USER_DATA_DIR}').classes('text-[10px] text-gray-600 font-mono')
            
            # Logic to show footer only on Provider tab
            def update_footer(e):
                # e.value is the selected tab object
                footer_row.visible = (e.value == provider_tab)
            
            tabs.on_value_change(update_footer)
            # Set initial state
            footer_row.visible = (tabs.value == provider_tab)
        
        self.dialog.open()
        
        # Auto-scroll to active provider
        if self.llm_manager and self.llm_manager.active_provider_id:
            active_id = self.llm_manager.active_provider_id
            # Small delay to ensure dialog DOM is rendered
            ui.timer(0.1, lambda: ui.run_javascript(
                f'document.getElementById("provider-{active_id}")?.scrollIntoView({{behavior: "smooth", block: "center"}})'
            ), once=True)
    
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
        
        # Status logic
        # 1. Check for Config Errors (Missing Keys)
        if provider.status == 'error':
            status_text = "NO KEY"
            status_color = "orange" 
            status_icon = "warning"
        elif provider.config.get('init_error'):
            # Runtime error during init (e.g. invalid key)
            status_text = "ERROR"
            status_color = "red"
            status_icon = "error"
        # 2. If healthy, check if Active
        elif is_active:
            status_text = "ACTIVE"
            status_color = "green"
            status_icon = "check_circle"
        # 3. Healthy but inactive
        else:
            status_text = "READY"
            status_color = "grey"
            status_icon = "radio_button_unchecked"
        
        with ui.card().props(f'id=provider-{provider.id}').classes('w-full mb-4 p-4').style(
            'background-color: var(--bg-accent); border: 1px solid var(--border-color);'
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
            
            # Settings (always show, user can configure keys even if not active)
            with ui.column().classes('w-full gap-3 mt-3 pt-3 border-t border-gray-700'):
                for setting in provider.settings:
                    self._build_setting_input(provider, setting)
    
    def _build_setting_input(self, provider, setting):
        """Build an input field for a provider setting"""
        # Create unique key first
        input_key = f"{provider.id}_{setting['key']}"
        
        # Determine value logic:
        # 1. Check temporary state (if we just refreshed UI while user was typing)
        if hasattr(self, 'temp_input_values') and input_key in self.temp_input_values:
            current_value = self.temp_input_values[input_key]
        else:
            # 2. Check saved config/env
            current_value = self.config_manager.get_provider_setting_value(
                provider.id, 
                setting['key']
            ) or setting.get('default', '')
        
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
        # 1. PRESERVE STATE: Capture all current input values before destroying them
        if not hasattr(self, 'temp_input_values'):
            self.temp_input_values = {}
        
        for key, widget in self.provider_inputs.items():
            # For booleans/switches, value is boolean. For inputs, it's string.
            val = widget.value
            if isinstance(val, bool):
                 val = 'true' if val else 'false'
            self.temp_input_values[key] = val
            
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
            if setting_def.get('env_var'):
                print(f"DEBUG: Saving {setting_def['env_var']} = '{value}' (Length: {len(value)})")
                if value:
                    os.environ[setting_def['env_var']] = value
                    self._update_env_file(setting_def['env_var'], value)
                else:
                    # Explicitly remove if empty!
                    if setting_def['env_var'] in os.environ:
                        del os.environ[setting_def['env_var']]
                    self._update_env_file(setting_def['env_var'], "")
            
            # Update provider config ONLY for non-API-key settings
            # API keys should NEVER be in provider_config.json
            if setting_key != 'api_key':
                self.config_manager.update_provider_config(
                    provider_id,
                    {setting_key: value}
                )
        
        # Apply pending provider activation immediately so re-init knows what's active
        if self.pending_active_provider and self.llm_manager:
            from core.user_config import UserConfig
            self.llm_manager.active_provider_id = self.pending_active_provider
            
            # 1. PERSIST ACTIVATION IMMEDIATELY
            UserConfig.save('active_provider_id', self.pending_active_provider)

        # Re-initialize all providers to pick up new/removed API keys
        if self.llm_manager:
            import asyncio
            async def reinit_sequence():
                # 1. Re-initialize ACTIVE provider first
                active_pid = self.llm_manager.active_provider_id
                if active_pid and active_pid in self.llm_manager.providers:
                    try:
                        await self.llm_manager.providers[active_pid].initialize()
                        print(f"✓ Re-initialized (ACTIVE): {active_pid}")
                    except Exception as e:
                        print(f"✗ Re-init failed (ACTIVE): {active_pid}: {e}")

                # 2. If we just switched provider, load its models and select default
                if self.pending_active_provider:
                     provider_instance = self.llm_manager.providers.get(self.pending_active_provider)
                     if provider_instance:
                        try:
                            models = await provider_instance.get_available_models()
                            if not models:
                                raise ValueError("No models returned by provider. Please check API Key/Settings.")
                            
                            # ONLY auto-select first model if we actually CHANGED the provider
                            # If we just updated settings for the SAME provider, keep the current model!
                            current_model_is_valid = False
                            if self.llm_manager.active_model_id:
                                if any(m.id == self.llm_manager.active_model_id for m in models):
                                    current_model_is_valid = True
                            
                            if not current_model_is_valid:
                                self.llm_manager.active_model_id = models[0].id
                                print(f'✓ Activated model: {models[0].name}')
                            else:
                                print(f'✓ Kept active model: {self.llm_manager.active_model_id}')
                            # Clear any previous error if success
                            provider_instance.config.init_error = None
                        except Exception as e:
                             print(f'✗ Error loading models for new provider: {e}')
                             # Propagate error to provider config so Sidebar shows it
                             err_msg = f"Model Fetch Error: {str(e)}"
                             provider_instance.config.init_error = err_msg
                             print(f"Provider Error: {err_msg}")
                             # ui.notify intentionally removed to avoid 'slot stack empty' error in background task
                             # The Sidebar status update below will show the error visually anyway.

                # 3. Refresh Sidebar UI (CRITICAL: Do this after model selection)
                if self.sidebar:
                    # Pass explicit True to force update even if value seems same
                    await self.sidebar.load_models()

                # 4. Re-initialize other providers in background -> REMOVED per user request ("Highlander Principle")
                # We only care about the active provider. Others will be initialized when they become active.
                pass
            
            asyncio.create_task(reinit_sequence())
        
        ui.notify('Settings saved & Provider updated!', type='positive')
        self.dialog.close()
    
    def _update_env_file(self, key: str, value: str):
        """Update .env file with new value - Safe for bundled app"""
        try:
            from core.paths import get_data_path
            # Use user data directory for persistent env storage
            env_path = Path(get_data_path('.env'))
            
            # Read existing .env content (handle if file doesn't exist)
            env_content = {}
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                k, v = line.split('=', 1)
                                env_content[k.strip()] = v.strip()
                except Exception:
                    pass # Ignore read errors
            
            # Update value
            if value:
                env_content[key] = value
            elif key in env_content:
                del env_content[key]
            
            # Write back
            with open(env_path, 'w') as f:
                for k, v in env_content.items():
                    f.write(f'{k}={v}\n')
                    
        except Exception as e:
            print(f"⚠️ Warning: Could not save .env file (ok in bundled app): {e}")
