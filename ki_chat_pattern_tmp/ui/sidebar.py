import flet as ft
from core.llm_manager import LLMManager
from core.user_config import UserConfig

class Sidebar(ft.Container):
    def __init__(self, llm_manager: LLMManager, on_model_change,  on_new_chat=None, on_load_chat=None):
        super().__init__()
        self.llm_manager = llm_manager
        self.on_model_change = on_model_change
        self.on_new_chat = on_new_chat
        self.on_load_chat = on_load_chat
        
        self.width = 280
        self.bgcolor = "surfaceVariant"
        self.padding = 20
        self.history_list_view = None
        self.content = self.build_content()

    def build_content(self):
        self.model_dropdown = ft.Dropdown(
            label="Select Model",
            options=[],
            text_size=14,
            border_color=ft.Colors.OUTLINE,
            width=240,
        )
        self.model_dropdown.on_change = self.handle_model_change
        
        # History ListView
        self.history_list_view = ft.ListView(
            controls=[ft.Text("No chats yet", size=13, italic=True, color=ft.Colors.OUTLINE)],
            spacing=5,
        )

        self.status_container = ft.Column(visible=False)

        return ft.Column(
            controls=[
                ft.Text("KI Chat", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=ft.Colors.OUTLINE_VARIANT),
                
                ft.Row([
                    ft.Text("Model Configuration", size=12, color=ft.Colors.OUTLINE),
                    ft.IconButton(
                        ft.Icons.REFRESH, 
                        icon_size=14, 
                        icon_color=ft.Colors.OUTLINE,
                        tooltip="Refresh APIs",
                        on_click=lambda e: self.page.run_task(self.load_models)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                self.model_dropdown,
                self.status_container,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                
                # Chat History Section
                ft.Row([
                    ft.Text("Chat History", size=12, color=ft.Colors.OUTLINE),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_size=16,
                        tooltip="New Chat",
                        on_click=self.handle_new_chat
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # History List (scrollable)
                ft.Container(
                    content=self.history_list_view,
                    expand=True,
                    padding=ft.padding.only(top=5)
                ),
                
                ft.Divider(height=20, color=ft.Colors.OUTLINE_VARIANT),
                ft.ElevatedButton(
                    "Settings", 
                    icon=ft.Icons.SETTINGS, 
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                )
            ]
        )
    
    def handle_new_chat(self, e):
        """Handler für New Chat Button"""
        if self.on_new_chat:
            self.on_new_chat()
    
    def handle_load_chat(self, conversation_id):
        """Handler für Chat-Load aus History"""
        if self.on_load_chat:
            self.on_load_chat(conversation_id)
    
    def update_history_list(self, conversations):
        """Update die History-Liste mit Konversationen"""
        self.history_list_view.controls.clear()
        
        if not conversations:
            self.history_list_view.controls.append(
                ft.Text("No chats yet", size=13, italic=True, color=ft.Colors.OUTLINE)
            )
        else:
            for conv in conversations:
                # Chat-Item als anklickbare Container
                self.history_list_view.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                conv["title"], 
                                size=13, 
                                weight=ft.FontWeight.W_500,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(
                                conv["updated_at"][:10],  # Nur Datum
                                size=11,
                                color=ft.Colors.OUTLINE
                            ),
                        ], spacing=2),
                        padding=8,
                        border_radius=5,
                       bgcolor=ft.Colors.SURFACE,
                        on_click=lambda e, cid=conv["id"]: self.handle_load_chat(cid),
                        ink=True,
                    )
                )
        
        self.history_list_view.update()

    def handle_model_change(self, e):
        # Parse value "provider_id|model_id"
        if not self.model_dropdown.value:
            return
        
        try:
            pid, mid = self.model_dropdown.value.split("|", 1)
            print(f"DEBUG: Switching to Provider='{pid}', Model='{mid}'")
            self.llm_manager.active_provider_id = pid
            self.llm_manager.active_model_id = mid
            
            # Persist selection
            UserConfig.save("last_model", self.model_dropdown.value)
            
            if self.on_model_change:
                self.on_model_change(f"Switched to {mid}")
        except ValueError:
            pass

    async def load_models(self):
        models = await self.llm_manager.get_all_models()
        options = []
        for m in models:
            # key format: provider_id|model_id
            # m.provider_id is injected by LLMManager
            pid = getattr(m, 'provider_id', 'mock')
            key = f"{pid}|{m.id}" 
            text = f"{m.name} ({m.provider})"
            options.append(ft.dropdown.Option(key=key, text=text))
        
        self.model_dropdown.options = options
        print(f"DEBUG: Sidebar updated with {len(options)} options.")
        self.model_dropdown.update() # Explicitly update the dropdown too
        
        # Check for provider errors
        if self.status_container: 
             self.status_container.controls.clear()
             
        has_errors = False
        for pid, provider in self.llm_manager.providers.items():
            if provider.config.init_error:
                has_errors = True
                self.status_container.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.AMBER, size=16),
                            ft.Text(f"{provider.config.name}: {provider.config.init_error}", color=ft.Colors.RED, size=10, width=200, no_wrap=False)
                        ], wrap=True),
                        padding=5
                    )
                )
        
        if has_errors:
            self.status_container.visible = True
        else:
            self.status_container.visible = False
            
        self.status_container.update()
        
        # Smart default selection priority:
        # 1. Saved config
        # 2. Prefer Real Providers
        # 3. Fallback to First Option
        
        saved_model = UserConfig.get("last_model")
        current_selection = f"{self.llm_manager.active_provider_id}|{self.llm_manager.active_model_id}"
        
        target_value = None
        
        # 1. Saved config (Highest Priority)
        if saved_model and any(o.key == saved_model for o in options):
            target_value = saved_model
            
        # 2. Prefer Real Providers (Auto-Switch away from Mock Default)
        # Only respect 'current_selection' if it is NOT a mock (unless it was saved, handled above)
        elif current_selection and "mock" not in current_selection.lower() and any(o.key == current_selection for o in options):
             target_value = current_selection
             
        # 3. Fallback / First Launch (Find best real provider)
        elif options:
            real_models = [o for o in options if "mock" not in o.key.lower()]
            if real_models:
                target_value = real_models[0].key
            else:
                target_value = options[0].key  # Fallback to Mock if nothing else exists
        
        if target_value:
            self.model_dropdown.value = target_value
            # Trigger update to sync Manager
            self.handle_model_change(None)

        self.update()
