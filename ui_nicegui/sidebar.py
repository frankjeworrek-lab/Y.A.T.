"""
Sidebar component for NiceGUI
Model selection, chat history, and controls
"""
from nicegui import ui
from core.llm_manager import LLMManager
from core.user_config import UserConfig
from .components.connection_status import ConnectionMonitor


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
            ui.image('/logo/logo.png').classes('w-full rounded-xl shadow-md mb-2').tooltip('Y.A.T. v2.1')
            
            # Signature
            ui.label('ARCHITECT • FRANK JEWORREK').classes(
                'w-full text-center text-[10px] text-gray-500 font-bold tracking-[0.2em] mb-3 opacity-80'
            )
            
            ui.separator().classes('bg-gray-700')
            
            # Model Configuration Section
            with ui.column().classes('w-full gap-2 mt-2'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Model').classes('text-sm font-semibold text-gray-300')
                    ui.button(icon='refresh', on_click=self._refresh_models).props(
                        'flat dense size=sm'
                    ).classes('text-gray-400 hover:text-blue-400')
                
                # Active Provider Status Badge
                # Interactive: Click to retry connection or open settings
                with ui.row().classes('w-full items-center gap-2 mb-2 px-3 py-2 cursor-pointer hover:bg-opacity-50 transition-colors').style(
                    'background-color: var(--bg-accent); border-radius: 6px; border: 1px solid var(--border-color);'
                ).on('click', self._handle_status_click):
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
            
            # Global Connection Monitor (Footer)
            ConnectionMonitor().build()
            

            
 
    
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

    async def _handle_status_click(self):
        """
        Smart Status Click Handler:
        - If active: Do nothing (or open connection info)
        - If error/warning: Try to REPAIR connection (Soft Retry)
        - If no provider: Open settings
        """
        if not self.llm_manager.active_provider_id:
            self._open_settings()
            return

        provider = self.llm_manager.providers.get(self.llm_manager.active_provider_id)
        if not provider:
            return

        # Don't interrupt working connection
        if provider.config.status == 'active' and not provider.config.init_error:
            ui.notify("Connection is healthy", type='info')
            return
            
        # REPAIR SEQUENCE
        # 1. Visual Feedback
        self.set_optimistic_state(provider.config.name)
        
        # 2. Logic Reset (Allow retry)
        provider.config.init_error = None
        
        # 3. Execution
        try:
             # Wait a tiny bit to let the UI render the spinner
             import asyncio
             await asyncio.sleep(0.1)
             
             # Force Re-Init and Load
             await provider.initialize()
             await self.load_models()
             
             if provider.config.status == 'active':
                 ui.notify(f"Successfully reconnected to {provider.config.name}", type='positive')
             
        except Exception as e:
            # Error handling is done by load_models, but notify here too
             ui.notify(f"Retry failed: {str(e)}", type='negative')
    
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
        # This prevents the dropdown from implicitly switching providers 
        # just because the active one has no models (error state).
        models = await self.llm_manager.get_available_models()
        
        # Mirror Logic from main.py: If we got models, the provider is ACTIVE.
        active_p = self.llm_manager.providers.get(self.llm_manager.active_provider_id)
        if active_p and models:
            active_p.config.status = 'active'
            active_p.config.init_error = None
        
        options = {}
        for m in models:
            pid = getattr(m, 'provider_id', 'mock')
            key = f"{pid}|{m.id}"
            text = f"{m.name} ({m.provider})"
            options[key] = text
        
        self.model_select.options = options
        self.model_select.update()
        
        
        # Update Active Provider Status Badge
        
        # CRITICAL: Check if NO plugins loaded (system broken)
        if len(self.llm_manager.providers) == 0:
            from core.paths import get_data_path
            self.provider_status_label.text = 'SYSTEM ERROR: No Plugins'
            self.provider_status_icon.name = 'error'
            self.provider_status_icon.props('color=yellow')
            self.provider_status_icon.classes('text-yellow-400 animate-pulse', remove='text-green-400 text-orange-400 text-red-500 text-gray-500')
            self.provider_status_label.classes('text-yellow-400 font-bold', remove='text-gray-300 text-orange-400 text-red-400')
            
            debug_log = get_data_path('plugin_debug.log')
            print(f"\n{'='*60}")
            print(f"CRITICAL: No provider plugins loaded!")
            print(f"Debug log: {debug_log}")
            print(f"{'='*60}\n")
            return
        
        active_provider = self.llm_manager.providers.get(self.llm_manager.active_provider_id)
        if active_provider:
            provider_name = active_provider.config.name
            has_error = bool(active_provider.config.init_error)
            
            self.provider_status_label.text = f'Active: {provider_name}'
            api_status = active_provider.config.status
            print(f">>> DEBUG Sidebar REFRESH: Provider='{provider_name}', Status='{api_status}', InitError='{active_provider.config.init_error}'")
            
            if has_error:
                self.provider_status_icon.name = 'error'
                self.provider_status_icon.props('color=red')
                self.provider_status_icon.classes('text-red-500', remove='text-green-400 text-orange-400 text-gray-400')
                self.provider_status_label.classes('text-red-400', remove='text-gray-300 text-orange-400')
            
            elif api_status == 'active': # Verified Runtime Success
                self.provider_status_icon.name = 'circle'
                self.provider_status_icon.props(remove='color=red color=orange color=grey') 
                self.provider_status_icon.classes('text-green-400', remove='text-red-500 text-orange-400 text-gray-500')
                self.provider_status_label.classes('text-gray-300', remove='text-red-400 text-orange-400')
            
            elif api_status == 'error': # Missing Key (Manager check)
                self.provider_status_icon.name = 'warning'
                self.provider_status_icon.props('color=orange')
                self.provider_status_icon.classes('text-orange-400', remove='text-green-400 text-red-500 text-gray-500')
                self.provider_status_label.text = f'{provider_name} (Setup needed)'
                self.provider_status_label.classes('text-orange-400', remove='text-gray-300')
            
            else: # 'configured' or unknown -> RED (Strict policy: If not active -> Error)
                self.provider_status_icon.name = 'error_outline'
                self.provider_status_icon.props('color=red')
                self.provider_status_icon.classes('text-red-400', remove='text-green-400 text-orange-400 text-gray-500')
                self.provider_status_label.text = 'No Active Provider'
                self.provider_status_label.classes('text-red-400', remove='text-gray-300 text-orange-400')
        else:
            # No provider selected -> Warn the user!
            self.provider_status_label.text = 'No Active Provider'
            self.provider_status_icon.name = 'warning'
            self.provider_status_icon.props('color=orange')
            self.provider_status_icon.classes('text-orange-400', remove='text-green-400 text-red-500 text-gray-500')
            self.provider_status_label.classes('text-orange-400', remove='text-gray-300 text-red-400')
        
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

    def set_optimistic_state(self, provider_id: str):
        """
        OPTIMISTIC UI: Immediately set visual state to 'Connecting...'
        Called by Settings Dialog BEFORE the async initialization finishes.
        This provides instant feedback on slow systems (Windows).
        """
        # Set Badge to Connecting (Spinner)
        self.provider_status_icon.name = 'sync'
        self.provider_status_icon.props('color=yellow')
        self.provider_status_icon.classes('text-yellow-400 animate-spin', remove='text-green-400 text-red-500 text-orange-400 animate-pulse text-gray-500')
        
        self.provider_status_label.text = f'Connecting: {provider_id}...'
        self.provider_status_label.classes('text-yellow-400', remove='text-gray-300 text-red-400 text-orange-400')
        self.provider_status_label.update()
        self.provider_status_icon.update()
