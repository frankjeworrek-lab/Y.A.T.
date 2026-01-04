"""
Sidebar component for NiceGUI
Model selection, chat history, and controls
"""
from nicegui import ui
from core.llm_manager import LLMManager
from core.user_config import UserConfig
from .components.connection_status import ConnectionMonitor
import asyncio


class Sidebar:
    def __init__(self, llm_manager: LLMManager, on_model_change, on_new_chat=None, on_load_chat=None):
        self.llm_manager = llm_manager
        self.on_model_change = on_model_change
        self.on_new_chat = on_new_chat
        self.on_load_chat = on_load_chat
        
        self.model_select = None
        self.history_container = None
        self.status_container = None
        
        self.status_badge_row = None
        self.provider_status_icon = None
        self.provider_status_label = None
        self.status_action_icon = None
        self.status_icon_container = None # New container for the isolated icon
        
        self.refresh_btn = None
        
    def build(self):
        """Build the sidebar UI with professional dark theme"""
        with ui.column().classes('w-72 h-screen p-5 gap-4').style(
            'background-color: var(--bg-secondary); border-right: 1px solid var(--border-color);'
        ):
            # Header
            ui.image('/logo/logo.png').classes('w-full rounded-xl shadow-md mb-2').tooltip('Y.A.T. v2.1')
            
            ui.label('ARCHITECT • FRANK JEWORREK').classes(
                'w-full text-center text-[10px] text-gray-500 font-bold tracking-[0.2em] mb-1 opacity-80'
            )
            
            ui.separator().classes('bg-gray-700 mt-1')
            
            # Model Configuration
            with ui.column().classes('w-full gap-2 mt-2'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Model').classes('text-sm font-semibold text-gray-300')
                    # Animated Refresh Button
                    self.refresh_btn = ui.button(icon='refresh', on_click=self._refresh_models).props(
                        'flat dense size=sm'
                    ).classes('text-gray-400 hover:text-blue-400 hover:rotate-180 transition-transform duration-500')
                
                # --- STATUS BADGE (Fixed Single Line) ---
                # Using explicit inline styles to defeat any framework wrapping defaults
                with ui.row().classes('w-full mb-2 px-2 py-1.5 cursor-pointer transition-colors border rounded-md bg-[#0F1115]').style(
                    'display: flex; flex-direction: row; flex-wrap: nowrap; align-items: center; white-space: nowrap; border-color: rgba(255,255,255,0.05); min-height: 28px;'
                ).on('click', self._handle_status_click) as row:
                    self.status_badge_row = row
                    
                    # Icon
                    self.provider_status_icon = ui.icon('circle', size='10px').classes('mr-2 flex-shrink-0')
                    
                    # Text
                    self.provider_status_label = ui.label('INITIALIZING...').classes('text-[10px] font-bold tracking-widest uppercase flex-1 truncate text-gray-500 leading-none')
                    
                    # Hit Icon
                    self.status_action_icon = ui.label('').classes('text-[10px] font-bold flex-shrink-0 leading-none')

                # Dropdown
                self.model_select = ui.select(
                    options={},
                    label='Select Model',
                    on_change=self._handle_model_change
                ).classes('w-full').props('outlined dense dark bg-color="grey-9" label-color="grey-4"').style(
                    'background-color: var(--bg-accent); border-color: var(--border-color);'
                )
            
            # Status Details
            with ui.column().classes('w-full') as status_col:
                self.status_container = status_col
                self.status_container.visible = False
            
            # Chat History
            with ui.column().classes('w-full flex-1 min-h-0 mt-6'):
                with ui.row().classes('w-full justify-between items-center mb-2'):
                    ui.label('History').classes('text-sm font-semibold text-gray-300')
                    ui.button(
                        icon='add',
                        on_click=self._handle_new_chat
                    ).props('flat dense size=sm color=blue-4').classes('hover:scale-125 transition-transform duration-200')
                
                with ui.column().classes('w-full flex-1 overflow-y-auto overflow-x-hidden justify-start p-2 gap-2') as history_col:
                    self.history_container = history_col
                    ui.label('No chats yet').classes('text-sm italic text-gray-500 p-2')
        
            ui.separator().classes('bg-gray-700 mt-2')
            
            # Footer
            with ui.row().classes('w-full gap-2 items-center mb-2'):
                ui.button(
                    'Preferences',
                    icon='tune',
                    on_click=lambda: self._open_settings(tab='providers')
                ).props('outline').classes('flex-1 text-gray-300 transition-colors hover:text-white').style(
                    'border-color: var(--border-color); color: var(--text-primary);'
                )
                ui.button(
                    icon='help_outline',
                    on_click=self._open_docs
                ).props('outline').classes('text-gray-400 w-12 transition-colors hover:text-white').style(
                    'border-color: var(--border-color); color: var(--text-secondary);'
                )
            
            ConnectionMonitor().build()
    
    def _open_settings(self, tab='providers'):
        from .provider_settings_dialog import ProviderSettingsDialog
        dialog = ProviderSettingsDialog(llm_manager=self.llm_manager, sidebar=self)
        dialog.show(initial_tab=tab)

    def _open_docs(self):
        from .docs_dialog import DocsDialog
        DocsDialog().show()
    
    async def _refresh_models(self):
        """Refresh models with Scenario-Driven Animation"""
        self.refresh_btn.classes(add='animate-spin', remove='hover:rotate-180')
        try:
             await self.load_models()
        finally:
             await asyncio.sleep(0.5)
             self.refresh_btn.classes(remove='animate-spin', add='hover:rotate-180')

    def _update_status_badge(self, state_group, text, icon_name, animate=False, action_hint=""):
        """
        Tech-Chip Logic (Single Line Enforced)
        Container stays dark. Content glows.
        """
        # Note: We rely on the inline .style() for flex-behavior. Classes just handle colors/spacing.
        # Removed 'gap-2' here because we use 'mr-2' on the icon for precision.
        base_outer = 'w-full mb-2 px-2 py-1.5 cursor-pointer transition-colors border rounded-md bg-[#0F1115]'
        
        if state_group == 'green':
            icon_color = 'text-green-500'
            text_color = 'text-green-500'
            border_color = 'border-green-900/40' 
            hover = 'hover:border-green-800 hover:bg-[#151a15]'
        elif state_group == 'blue':
            icon_color = 'text-blue-400'
            text_color = 'text-blue-400'
            border_color = 'border-blue-900/40'
            hover = 'hover:border-blue-800 hover:bg-[#15191f]'
        elif state_group == 'orange':
            icon_color = 'text-orange-400'
            text_color = 'text-orange-400'
            border_color = 'border-orange-900/40'
            hover = 'hover:border-orange-800 hover:bg-[#1f1a15]'
        elif state_group == 'red':
            icon_color = 'text-red-500'
            text_color = 'text-red-500'
            border_color = 'border-red-900/40'
            hover = 'hover:border-red-800 hover:bg-[#1f1515]'
        elif state_group == 'critical':
            icon_color = 'text-red-600'
            text_color = 'text-red-600'
            border_color = 'border-red-600'
            hover = 'hover:bg-red-950/50'
        else:
            icon_color = 'text-gray-600'
            text_color = 'text-gray-600'
            border_color = 'border-white/5'
            hover = 'hover:bg-gray-800'

        # Apply Container
        self.status_badge_row.classes(replace=f"{base_outer} {border_color} {hover}")
        
        # Icon
        self.provider_status_icon.name = icon_name
        self.provider_status_icon._props['color'] = None 
        
        current_anim = ''
        if animate == 'spin': current_anim = 'animate-spin'
        elif animate == 'pulse': current_anim = 'animate-pulse'
        
        # Apply Icon Style (Restore explicit classes)
        self.provider_status_icon.classes(replace=f"mr-2 flex-shrink-0 {icon_color} {current_anim}")
        
        # Text (Uppercase enforcement + Leading None)
        self.provider_status_label.text = text.upper()
        self.provider_status_label.classes(replace=f"text-[10px] font-bold tracking-widest uppercase flex-1 truncate leading-none {text_color}")
        
        # Action Hint
        self.status_action_icon.text = action_hint
        self.status_action_icon.classes(replace=f"text-[10px] font-bold flex-shrink-0 leading-none {text_color}")


    async def _handle_status_click(self):
        """Active User Assistance Handler"""
        if not self.llm_manager.active_provider_id:
            self._open_settings()
            return
        
        provider = self.llm_manager.providers.get(self.llm_manager.active_provider_id)
        if not provider: return

        self._update_status_badge('blue', 'Verifying...', 'search', animate='spin')
        self.status_action_icon.text = "" 
        await asyncio.sleep(0.5) 
        try:
             await provider.initialize()
             await self.load_models()
             if provider.config.status == 'active' and not provider.config.init_error:
                 self._update_status_badge('green', 'Verified', 'check_circle', animate=False)
                 await asyncio.sleep(1.5)
                 await self.load_models() # Restore normal text
        except Exception:
             self._update_status_badge('red', 'Crash', 'bug_report')

    
    def _handle_new_chat(self):
        if self.on_new_chat: self.on_new_chat()
    
    def _handle_load_chat(self, conversation_id):
        if self.on_load_chat: self.on_load_chat(conversation_id)
    
    def _handle_model_change(self, e):
        value = self.model_select.value
        if not value: return
        try:
            pid, mid = value.split('|', 1)
            self.llm_manager.active_provider_id = pid
            self.llm_manager.active_model_id = mid
            UserConfig.save('last_model', value)
            if self.on_model_change: self.on_model_change(f'Switched to {mid}')
        except Exception: pass
    
    async def load_models(self):
        """Load models and Map to Status Matrix v2"""
        # (Logic unchanged, reused for brevity in this replace call, ensures consistency)
        models = await self.llm_manager.get_available_models()
        active_id = self.llm_manager.active_provider_id
        active_provider = self.llm_manager.providers.get(active_id) if active_id else None
        
        if len(self.llm_manager.providers) == 0:
            self._update_status_badge('critical', 'Critical Failure', 'dangerous', animate='pulse', action_hint='➜')
        elif not active_provider:
            self._update_status_badge('orange', 'No Provider', 'touch_app', animate='pulse', action_hint='➜')
        else:
            p_name = active_provider.config.name
            init_error = active_provider.config.init_error
            status = active_provider.config.status
            if init_error:
                err_text = str(init_error).lower()
                if '401' in err_text or 'key' in err_text:
                    self._update_status_badge('red', f'{p_name}: Auth Failed', 'lock', animate='pulse', action_hint='🛠️')
                elif '429' in err_text or 'quota' in err_text:
                    self._update_status_badge('red', f'{p_name}: Quota Exceeded', 'payments', animate=False, action_hint='➜')
                elif 'connect' in err_text:
                    self._update_status_badge('red', f'{p_name}: No Connection', 'wifi_off', animate='pulse', action_hint='↻')
                else:
                    self._update_status_badge('red', f'{p_name}: Error', 'bug_report', animate='pulse', action_hint='↻')
            
            elif status == 'setup_needed':
                 self._update_status_badge('orange', f'{p_name}: Configure', 'settings', animate='pulse', action_hint='⚙️')
            
            elif status == 'active':
                if not models:
                    self._update_status_badge('orange', f'{p_name}: No Models', 'folder_off', animate=False, action_hint='↻')
                else:
                    self._update_status_badge('green', f'Active: {p_name}', 'circle', animate=False)
            else:
                self._update_status_badge('red', f'{p_name}: Unknown', 'help', action_hint='?')
        
        options = {}
        if models:
            for m in models:
                pid = getattr(m, 'provider_id', 'mock')
                key = f"{pid}|{m.id}"
                options[key] = f"{m.name} ({m.provider})"
        self.model_select.options = options
        self.model_select.update()
        
        display_val = None
        saved = UserConfig.get('last_model')
        if saved and saved in options: display_val = saved
        elif active_id and f"{active_id}|{self.llm_manager.active_model_id}" in options:
             display_val = f"{active_id}|{self.llm_manager.active_model_id}"
        elif options: display_val = list(options.keys())[0]
        if display_val: self.model_select.value = display_val

    def update_history_list(self, conversations):
        self.history_container.clear()
        if not conversations:
            with self.history_container: ui.label('No chats yet').classes('text-sm italic text-gray-500 p-2')
        else:
            with self.history_container:
                for conv in conversations:
                    conv_id = conv['id']
                    with ui.card().classes('w-full p-3 cursor-pointer transition-all').style(
                        'background-color: var(--bg-secondary); border: 1px solid var(--border-color);'
                        'transition: all 0.2s ease;'
                    ).on('click', lambda cid=conv_id: self._handle_load_chat(cid)):
                        ui.add_head_html(".nicegui-content .q-card:hover { background-color: var(--bg-accent) !important; border-color: var(--accent-color) !important; }")
                        ui.label(conv['title']).classes('text-sm font-medium text-gray-200 truncate')
                        ui.label(conv['updated_at'][:10]).classes('text-xs text-gray-500 mt-1')

    def set_optimistic_state(self, provider_id: str):
        self._update_status_badge('blue', 'Connecting...', 'sync', animate='spin')
