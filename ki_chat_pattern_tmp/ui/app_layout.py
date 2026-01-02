import flet as ft
import asyncio
import uuid
from core.llm_manager import LLMManager
from core.providers.types import Message, Role
from storage.chat_db import ChatDatabase
from .sidebar import Sidebar
from .chat_view import ChatView
from .input_area import InputArea

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, llm_manager: LLMManager):
        super().__init__()
        self.main_page = page
        self.llm_manager = llm_manager
        self.expand = True
        self.spacing = 0
        
        # Persistence
        self.db = ChatDatabase()
        self.current_conversation_id = None
        
        # State
        self.message_history: list[Message] = []
        
        # Message Queue (sequential processing)
        self.message_queue = asyncio.Queue()
        self.is_processing = False
        
        # Components
        self.sidebar = Sidebar(
            llm_manager, 
            self.handle_model_change,
            on_new_chat=self.handle_new_chat,
            on_load_chat=self.handle_load_chat
        )
        self.chat_view = ChatView()
        self.input_area = InputArea(self.handle_input_submit)
        
        # Main Content Area
        self.main_content = ft.Container(
            expand=True,
            bgcolor="background",
            content=ft.Column(
                controls=[
                    self.chat_view,
                    self.input_area
                ],
                spacing=0
            )
        )
        
        self.controls = [
            self.sidebar,
            ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT),
            self.main_content
        ]

    async def initialize_async(self):
        await self.sidebar.load_models()
        self.refresh_history_list()
        
        # Start queue worker
        asyncio.create_task(self._queue_worker())
    
    async def _queue_worker(self):
        """Sequential message processor"""
        while True:
            prompt = await self.message_queue.get()
            try:
                await self.run_chat_flow(prompt)
            except Exception as e:
                print(f"Queue error: {e}")
            finally:
                self.message_queue.task_done()

    def refresh_history_list(self):
        conversations = self.db.get_conversations()
        self.sidebar.update_history_list(conversations)

    def handle_new_chat(self):
        self.current_conversation_id = None
        self.message_history = []
        self.chat_view.clear()
        
    def handle_load_chat(self, conversation_id):
        if self.current_conversation_id == conversation_id:
            return
            
        self.current_conversation_id = conversation_id
        self.message_history = self.db.load_messages(conversation_id)
        
        self.chat_view.clear()
        for msg in self.message_history:
            self.chat_view.add_message(msg)

    def handle_model_change(self, status_text):
        self.main_page.snack_bar = ft.SnackBar(ft.Text(status_text))
        self.main_page.snack_bar.open = True
        self.main_page.update()

    def handle_input_submit(self, text):
        # Queue message instead of direct processing
        asyncio.create_task(self.message_queue.put(text))

    async def run_chat_flow(self, text):
        if not text: 
            return

        self.input_area.disable()
        
        # Ensure Conversation ID
        if not self.current_conversation_id:
            self.current_conversation_id = str(uuid.uuid4())
            # Titel generieren (erste 30 Zeichen)
            title = text[:30] + "..." if len(text) > 30 else text
            self.db.create_conversation(
                self.current_conversation_id, 
                title=title,
                provider_id=self.llm_manager.active_provider_id,
                model_id=self.llm_manager.active_model_id
            )
            self.refresh_history_list()
        
        # 1. User Message
        user_msg = Message(role=Role.USER, content=text)
        self.message_history.append(user_msg)
        self.chat_view.add_message(user_msg)
        self.db.save_message(self.current_conversation_id, user_msg)
        
        # 2. Assistant Message Placeholder
        assistant_msg = Message(role=Role.ASSISTANT, content="")
        self.chat_view.add_message(assistant_msg)
        
        # 3. Stream
        self.message_history.append(assistant_msg)
        current_content = ""
        
        try:
            async for chunk in self.llm_manager.stream_chat(self.message_history[:-1]):
                current_content += chunk
                self.chat_view.update_last_message(current_content)
        except Exception as e:
            current_content += f"\n\n[Error: {str(e)}]"
            self.chat_view.update_last_message(current_content)
            
        # Update final content
        assistant_msg.content = current_content
        self.db.save_message(self.current_conversation_id, assistant_msg)
        
        # History-Liste updaten (für Timestamp change)
        self.refresh_history_list()
        
        await self.input_area.enable()
