"""
Main App Layout for NiceGUI
Orchestrates sidebar, chat view, and input area
"""
from nicegui import ui
import asyncio
import uuid
from core.llm_manager import LLMManager
from core.providers.types import Message, Role
from storage.chat_db import ChatDatabase
from .sidebar import Sidebar
from .chat_view import ChatView
from .input_area import InputArea


class AppLayout:
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        
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
        
    def build(self):
        """Build the main application layout with dark theme"""
        with ui.row().classes('w-full h-screen').style('background-color: #0f1117; margin: 0; padding: 0;'):
            # Sidebar
            self.sidebar.build()
            
            # Main Content
            with ui.column().classes('flex-1 h-screen').style('padding: 0; margin: 0;'):
                # Chat View
                self.chat_view.build()
                
                # Input Area
                self.input_area.build()
        
        # Start queue worker
        asyncio.create_task(self._queue_worker())
    
    async def initialize_async(self):
        """Initialize async components"""
        await self.sidebar.load_models()
        self.refresh_history_list()
    
    async def _queue_worker(self):
        """Sequential message processor"""
        while True:
            prompt = await self.message_queue.get()
            try:
                await self.run_chat_flow(prompt)
            except Exception as e:
                print(f"Queue error: {e}")
                # Cannot use ui.notify in background task - just log
            finally:
                self.message_queue.task_done()
    
    def refresh_history_list(self):
        """Refresh chat history sidebar"""
        conversations = self.db.get_conversations()
        self.sidebar.update_history_list(conversations)
    
    def handle_new_chat(self):
        """Start a new chat"""
        self.current_conversation_id = None
        self.message_history = []
        self.chat_view.clear()
        print('New chat started')
    
    def handle_load_chat(self, conversation_id):
        """Load existing chat from history"""
        if self.current_conversation_id == conversation_id:
            return
        
        self.current_conversation_id = conversation_id
        self.message_history = self.db.load_messages(conversation_id)
        
        self.chat_view.clear()
        for msg in self.message_history:
            self.chat_view.add_message(msg)
        
        print('Chat loaded')
    
    def handle_model_change(self, status_text):
        """Handle model selection change"""
        print(f"Model changed: {status_text}")
    
    async def handle_input_submit(self, text):
        """Queue message for processing"""
        await self.message_queue.put(text)
    
    async def run_chat_flow(self, text):
        """Process chat message with streaming"""
        if not text:
            return
        
        self.input_area.disable()
        
        # Ensure Conversation ID
        if not self.current_conversation_id:
            self.current_conversation_id = str(uuid.uuid4())
            title = text[:30] + '...' if len(text) > 30 else text
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
        assistant_msg = Message(role=Role.ASSISTANT, content='')
        self.chat_view.add_message(assistant_msg)
        self.message_history.append(assistant_msg)
        
        # 3. Stream Response
        current_content = ''
        
        try:
            async for chunk in self.llm_manager.stream_chat(self.message_history[:-1]):
                current_content += chunk
                self.chat_view.update_last_message(current_content)
        except Exception as e:
            current_content += f'\n\n[Error: {str(e)}]'
            self.chat_view.update_last_message(current_content)
            print(f'Chat error: {str(e)}')
        
        # Update final content
        assistant_msg.content = current_content
        self.db.save_message(self.current_conversation_id, assistant_msg)
        
        # Refresh history list (for timestamp update)
        self.refresh_history_list()
        
        self.input_area.enable()
