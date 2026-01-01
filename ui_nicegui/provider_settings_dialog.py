"""
Provider Settings Dialog for NiceGUI
Comprehensive provider management interface
"""
from nicegui import ui
import os
from pathlib import Path
from core.provider_config_manager import ProviderConfigManager


class ProviderSettingsDialog:
    def __init__(self):
        self.dialog = None
        self.config_manager = ProviderConfigManager()
        self.provider_inputs = {}
        
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
            
            # Provider List
            for provider in self.config_manager.get_all_providers():
                self._build_provider_card(provider)
            
            ui.separator().classes('bg-gray-700 my-4')
            
            # Buttons
            with ui.row().classes('w-full justify-end gap-3'):
                ui.button('Cancel', on_click=self.dialog.close).props('outline').classes('text-gray-300')
                ui.button('Save & Apply', icon='save', on_click=self._save_settings).style(
                    'background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);'
                )
        
        self.dialog.open()
    
    def _build_provider_card(self, provider):
        """Build a card for a single provider"""
        # Status badge color
        status_colors = {
            'active': 'green',
            'disabled': 'gray',
            'error': 'red',
            'offline': 'orange'
        }
        status_color = status_colors.get(provider.status, 'gray')
        
        with ui.card().classes('w-full mb-4 p-4').style(
            'background-color: #111827; border: 1px solid #374151;'
        ):
            # Header row
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center gap-3'):
                    # Icon
                    ui.icon(provider.icon, size='md').classes(f'text-{provider.color}-400')
                    
                    # Name and type
                    with ui.column().classes('gap-1'):
                        ui.label(provider.name).classes('text-lg font-bold text-white')
                        ui.label(f'{provider.type.capitalize()} Provider').classes('text-xs text-gray-500')
                
                # Status and enable toggle
                with ui.row().classes('items-center gap-3'):
                    ui.badge(provider.status.capitalize(), color=status_color).classes('text-xs')
                    
                    toggle = ui.switch(
                        value=provider.enabled,
                        on_change=lambda e, pid=provider.id: self._toggle_provider(pid, e.value)
                    ).classes('ml-2')
                    ui.label('Enabled').classes('text-sm text-gray-400')
            
            # Settings (only show if enabled)
            if provider.enabled:
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
            
            # Save to environment if has env_var
            if setting_def.get('env_var') and value:
                os.environ[setting_def['env_var']] = value
                
                # Also save to .env file
                self._update_env_file(setting_def['env_var'], value)
            
            # Update provider config
            self.config_manager.update_provider_config(
                provider_id,
                {setting_key: value}
            )
        
        ui.notify('Provider settings saved! Restart app to apply changes.', type='positive')
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
