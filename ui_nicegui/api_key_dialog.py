"""
API Key Configuration Dialog for NiceGUI
Allows users to configure API keys directly from the GUI
"""
from nicegui import ui
import os
from pathlib import Path


class APIKeyDialog:
    def __init__(self):
        self.dialog = None
        self.openai_input = None
        self.anthropic_input = None
        self.gemini_input = None
        
    def show(self):
        """Show the API key configuration dialog"""
        with ui.dialog() as self.dialog, ui.card().classes('w-full max-w-2xl p-6').style(
            'background-color: #1f2937; border: 1px solid #374151;'
        ):
            # Header
            with ui.row().classes('w-full items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-3'):
                    ui.icon('key', size='lg').classes('text-blue-400')
                    ui.label('API Keys Configuration').classes('text-2xl font-bold text-white')
                ui.button(icon='close', on_click=self.dialog.close).props('flat round').classes('text-gray-400')
            
            ui.separator().classes('bg-gray-700 mb-4')
            
            # Info text
            ui.label('Configure your API keys to use AI providers').classes('text-sm text-gray-400 mb-4')
            
            # Load current values
            current_openai = os.getenv('OPENAI_API_KEY', '')
            current_anthropic = os.getenv('ANTHROPIC_API_KEY', '')
            current_gemini = os.getenv('GOOGLE_API_KEY', '')
            
            # OpenAI Section
            with ui.column().classes('w-full gap-2 mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('api', size='sm').classes('text-green-400')
                    ui.label('OpenAI API Key').classes('text-md font-semibold text-gray-200')
                    if current_openai:
                        ui.badge('✓', color='green').classes('text-xs')
                
                self.openai_input = ui.input(
                    placeholder='sk-...',
                    value=current_openai,
                    password=True,
                    password_toggle_button=True
                ).classes('w-full').props('outlined dense dark').style(
                    'background-color: #111827;'
                )
                ui.label('Get your key at: platform.openai.com/api-keys').classes('text-xs text-gray-500')
            
            # Anthropic Section
            with ui.column().classes('w-full gap-2 mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('api', size='sm').classes('text-purple-400')
                    ui.label('Anthropic API Key').classes('text-md font-semibold text-gray-200')
                    if current_anthropic:
                        ui.badge('✓', color='green').classes('text-xs')
                
                self.anthropic_input = ui.input(
                    placeholder='sk-ant-...',
                    value=current_anthropic,
                    password=True,
                    password_toggle_button=True
                ).classes('w-full').props('outlined dense dark').style(
                    'background-color: #111827;'
                )
                ui.label('Get your key at: console.anthropic.com').classes('text-xs text-gray-500')
            
            # Google Gemini Section
            with ui.column().classes('w-full gap-2 mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('api', size='sm').classes('text-blue-400')
                    ui.label('Google Gemini API Key').classes('text-md font-semibold text-gray-200')
                    if current_gemini:
                        ui.badge('✓', color='green').classes('text-xs')
                
                self.gemini_input = ui.input(
                    placeholder='AIza...',
                    value=current_gemini,
                    password=True,
                    password_toggle_button=True
                ).classes('w-full').props('outlined dense dark').style(
                    'background-color: #111827;'
                )
                ui.label('Get your key at: makersuite.google.com/app/apikey').classes('text-xs text-gray-500')
            
            ui.separator().classes('bg-gray-700 my-4')
            
            # Buttons
            with ui.row().classes('w-full justify-end gap-3'):
                ui.button('Cancel', on_click=self.dialog.close).props('outline').classes('text-gray-300')
                ui.button('Save Keys', icon='save', on_click=self._save_keys).props('').style(
                    'background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);'
                )
        
        self.dialog.open()
    
    def _save_keys(self):
        """Save API keys to .env file"""
        env_path = Path('.env')
        
        # Read existing .env content
        env_content = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()
        
        # Update with new values
        if self.openai_input.value:
            env_content['OPENAI_API_KEY'] = self.openai_input.value
        elif 'OPENAI_API_KEY' in env_content:
            del env_content['OPENAI_API_KEY']
        
        if self.anthropic_input.value:
            env_content['ANTHROPIC_API_KEY'] = self.anthropic_input.value
        elif 'ANTHROPIC_API_KEY' in env_content:
            del env_content['ANTHROPIC_API_KEY']
        
        if self.gemini_input.value:
            env_content['GOOGLE_API_KEY'] = self.gemini_input.value
        elif 'GOOGLE_API_KEY' in env_content:
            del env_content['GOOGLE_API_KEY']
        
        # Write back to .env
        with open(env_path, 'w') as f:
            for key, value in env_content.items():
                f.write(f'{key}={value}\n')
        
        # Update environment variables
        if self.openai_input.value:
            os.environ['OPENAI_API_KEY'] = self.openai_input.value
        if self.anthropic_input.value:
            os.environ['ANTHROPIC_API_KEY'] = self.anthropic_input.value
        if self.gemini_input.value:
            os.environ['GOOGLE_API_KEY'] = self.gemini_input.value
        
        ui.notify('API Keys saved successfully! Restart app to apply changes.', type='positive')
        self.dialog.close()
