"""
Sidebar component for NiceGUI
Model selection, chat history, and controls
"""
from nicegui import ui
from core.llm_manager import LLMManager
from core.user_config import UserConfig


class Sidebar:
    def __init__(self, llm_manager: LLMManager, on_model_change, on_new_chat=None, on_load_chat=None):
        self.llm_manager = llm_manager
        self.on_model_change = on_model_change
        self.on_new_chat = on_new_chat
        self.on_load_chat = on_load_chat
        
        self.model_select = None
        self.history_container = None
        self.status_container = None
        
    def build(self):
        """Build the sidebar UI with professional dark theme"""
        with ui.column().classes('w-72 h-screen p-5 gap-4').style(
            'background-color: var(--bg-secondary); border-right: 1px solid var(--border-color);'
        ):
            # Header with gradient
            # Header Banner
            ui.image('/logo/Gemini_Generated_Image_ki82s1ki82s1ki82.png').classes('w-full rounded-xl shadow-md mb-2')
            
            ui.separator().classes('bg-gray-700')
            
            # Model Configuration Section
            with ui.column().classes('w-full gap-2 mt-2'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Model').classes('text-sm font-semibold text-gray-300')
                    ui.button(icon='refresh', on_click=self._refresh_models).props(
                        'flat dense size=sm'
                    ).classes('text-gray-400 hover:text-blue-400')
                
                # Active Provider Status Badge
                with ui.row().classes('w-full items-center gap-2 mb-2 px-3 py-2').style(
                    'background-color: var(--bg-accent); border-radius: 6px; border: 1px solid var(--border-color);'
                ):
                    self.provider_status_icon = ui.icon('circle', size='xs').classes('text-green-400')
                    self.provider_status_label = ui.label('Active: Loading...').classes('text-xs text-gray-300')
                
                # Model Dropdown with custom styling
                self.model_select = ui.select(
                    options={},
                    label='Select Model',
                    on_change=self._handle_model_change
                ).classes('w-full').props('outlined dense dark bg-color="grey-9" label-color="grey-4"').style(
                    'background-color: var(--bg-accent); border-color: var(--border-color);'
                )
            
            # Status Container (for errors)
            with ui.column().classes('w-full') as status_col:
                self.status_container = status_col
                self.status_container.visible = False
            
            # Chat History Section with margin instead of flex spacer
            with ui.column().classes('w-full flex-1 min-h-0 mt-6'):
                with ui.row().classes('w-full justify-between items-center mb-2'):
                    ui.label('History').classes('text-sm font-semibold text-gray-300')
                    ui.button(
                        icon='add',
                        on_click=self._handle_new_chat
                    ).props('flat dense size=sm color=blue-4')
                
                # History List (native vertical scroll, centered items via padding)
                with ui.column().classes('w-full flex-1 overflow-y-auto overflow-x-hidden justify-start p-2 gap-2') as history_col:
                    self.history_container = history_col
                    ui.label('No chats yet').classes('text-sm italic text-gray-500 p-2')
        
            ui.separator().classes('bg-gray-700 mt-2')
            
            # Footer Actions
            with ui.row().classes('w-full gap-2 items-center mb-2'):
                # Preferences (Main Action)
                ui.button(
                    'Preferences',
                    icon='tune',
                    on_click=lambda: self._open_settings(tab='providers')
                ).props('outline').classes('flex-1 text-gray-300').style(
                    'border-color: var(--border-color); color: var(--text-primary);'
                )
                
                # Help / Docs (Secondary Action)
                ui.button(
                    icon='help_outline',
                    on_click=self._open_docs
                ).props('outline').classes('text-gray-400 w-12').style(
                    'border-color: var(--border-color); color: var(--text-secondary);'
                ).tooltip('Knowledge Base')
            
 
    
    def _open_settings(self, tab='providers'):
        """Open settings dialog with specific tab"""
        from .provider_settings_dialog import ProviderSettingsDialog
        # Pass self (Sidebar) as callback/parent logic provider if needed, or remove param if not used
        # Note: Previous code had 'sidebar=self', checking if dialog accepts it.
        # Assuming dialog accepts (llm_manager, on_theme_change_callback) or similar.
        # Let's inspect dialog constructor.
        # Step 446 says: __init__(self, llm_manager, on_theme_change=None):
        # But previous code used: dialog = ProviderSettingsDialog(llm_manager=self.llm_manager, sidebar=self) (IN FILE VIEW above)
        # Wait, file view line 91 says: ProviderSettingsDialog(llm_manager=self.llm_manager, sidebar=self)
        # So I must keep that call signature!
        dialog = ProviderSettingsDialog(llm_manager=self.llm_manager, sidebar=self)
        dialog.show(initial_tab=tab)

    def _open_docs(self):
        """Open documentation dialog"""
        from .docs_dialog import DocsDialog
        DocsDialog().show()
    


    
    async def _refresh_models(self):
        """Refresh models from all providers"""
        await self.load_models()
    
    def _handle_new_chat(self):
        """Handle new chat button"""
        if self.on_new_chat:
            self.on_new_chat()
    
    def _handle_load_chat(self, conversation_id):
        """Handle chat load from history"""
        if self.on_load_chat:
            self.on_load_chat(conversation_id)
    
    def _handle_model_change(self, e):
        """Handle model selection change"""
        value = self.model_select.value
        if not value:
            return
        
        try:
            pid, mid = value.split('|', 1)
            self.llm_manager.active_provider_id = pid
            self.llm_manager.active_model_id = mid
            
            # Persist selection
            UserConfig.save('last_model', value)
            
            if self.on_model_change:
                self.on_model_change(f'Switched to {mid}')
        except (ValueError, AttributeError) as err:
            print(f"Model change error: {err}")
    
    async def load_models(self):
        """Load and populate model dropdown"""
        # FIX: Only load models for the ACTIVE provider.
        # This prevents the dropdown from implicitly switching providers 
        # just because the active one has no models (error state).
        models = await self.llm_manager.get_available_models()
        
        options = {}
        for m in models:
            pid = getattr(m, 'provider_id', 'mock')
            key = f"{pid}|{m.id}"
            text = f"{m.name} ({m.provider})"
            options[key] = text
        
        self.model_select.options = options
        self.model_select.update()
        
        # Update Active Provider Status Badge
        active_provider = self.llm_manager.providers.get(self.llm_manager.active_provider_id)
        if active_provider:
            provider_name = active_provider.config.name
            has_error = bool(active_provider.config.init_error)
            
            self.provider_status_label.text = f'Active: {provider_name}'
            print(f"DEBUG Sidebar: Active={provider_name}, Error={active_provider.config.init_error}")
            
            if has_error:
                self.provider_status_icon.name = 'warning'
                self.provider_status_icon.props('color=red')
                self.provider_status_icon.classes('text-red-500', remove='text-green-400')
                self.provider_status_label.classes('text-red-400', remove='text-gray-300')
            else:
                self.provider_status_icon.name = 'circle'
                self.provider_status_icon.props(remove='color=red') # FIX: Clear color prop so Tailwind class works
                self.provider_status_icon.classes('text-green-400', remove='text-red-500')
                self.provider_status_label.classes('text-gray-300', remove='text-red-400')
        else:
            # No provider selected (Truth)
            self.provider_status_label.text = 'Active: None'
            self.provider_status_icon.name = 'help_outline'
            self.provider_status_icon.props('color=grey')
            self.provider_status_icon.classes('text-gray-500', remove='text-green-400 text-red-500')
            self.provider_status_label.classes('text-gray-500', remove='text-red-400')
        
        # Check for provider errors (only show for ACTIVE provider)
        self.status_container.clear()
        has_errors = False
        
        active_provider = self.llm_manager.providers.get(self.llm_manager.active_provider_id)
        if active_provider and active_provider.config.init_error:
            print(f"DEBUG: Showing error for {active_provider.config.name}: {active_provider.config.init_error}")
            has_errors = True
            with self.status_container:
                with ui.card().classes('w-full p-2 bg-red-900 bg-opacity-20 border border-red-700'):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('warning', color='amber', size='sm')
                        ui.label(f"{active_provider.config.name}: {active_provider.config.init_error}").classes(
                            'text-xs text-red-300'
                        )
        
        self.status_container.visible = has_errors
        
        # Smart default selection
        # Respect the managers active provider (which was set by main.py from config)
        saved_model = UserConfig.get('last_model')
        current_manager_provider = self.llm_manager.active_provider_id
        
        target_value = None
        
        # 1. Try saved model ONLY if it matches active provider
        if saved_model and saved_model in options and saved_model.startswith(current_manager_provider + '|'):
             target_value = saved_model
        
        # 2. Else use current selection from Manager (which main.py set up)
        elif f"{current_manager_provider}|{self.llm_manager.active_model_id}" in options:
             target_value = f"{current_manager_provider}|{self.llm_manager.active_model_id}"
             
        # 3. Fallback: First model of active provider
        if not target_value:
             provider_options = [k for k in options.keys() if k.startswith(current_manager_provider + '|')]
             if provider_options:
                 target_value = provider_options[0]
        
        # 4. Ultimate Fallback
        if not target_value and options:
            target_value = list(options.keys())[0]

        if target_value:
            self.model_select.value = target_value
            # Do NOT trigger on_change if we are just restoring state to avoid loops
            # self._handle_model_change(None) 
            # We just set the UI to match the internal state
            pass
    
    def update_history_list(self, conversations):
        """Update chat history list with modern card design"""
        self.history_container.clear()
        
        if not conversations:
            with self.history_container:
                ui.label('No chats yet').classes('text-sm italic text-gray-500 p-2')
        else:
            with self.history_container:
                for conv in conversations:
                    conv_id = conv['id']
                    with ui.card().classes('w-full p-3 cursor-pointer transition-all').style(
                        'background-color: var(--bg-secondary); border: 1px solid var(--border-color);'
                        'transition: all 0.2s ease;'
                    ).on('click', lambda cid=conv_id: self._handle_load_chat(cid)):
                        # Add hover effect via inline style
                        ui.add_head_html("""
                        <style>
                        .nicegui-content .q-card:hover {
                            background-color: var(--bg-accent) !important;
                            border-color: var(--accent-color) !important;
                        }
                        </style>
                        """)
                        ui.label(conv['title']).classes('text-sm font-medium text-gray-200 truncate')
                        ui.label(conv['updated_at'][:10]).classes('text-xs text-gray-500 mt-1')
