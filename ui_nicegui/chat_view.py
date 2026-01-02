"""
ChatView component for NiceGUI
Displays chat messages with markdown support and modern bubble design
"""
from nicegui import ui
from core.providers.types import Message, Role


class ChatView:
    def __init__(self):
        self.messages_container = None
        self.message_rows = []
        
    def build(self):
        """Build the chat view UI with professional dark theme"""
        # Main container with scroll area
        with ui.scroll_area().classes('flex-1 p-6').style(
            'background-color: var(--bg-primary);'
        ) as scroll:
            self.scroll_area = scroll
            
            with ui.column().classes('w-full gap-4') as container:
                self.messages_container = container
                
                # Welcome message
                with ui.column().classes('items-center justify-center mt-20 mb-10'):
                    ui.icon('chat_bubble', size='xl').classes('text-blue-400 mb-4')
                    ui.label('Start a conversation').classes('text-2xl font-bold text-gray-200')
                    ui.label('Choose a model and send your first message').classes('text-sm text-gray-500')
        
        return self.messages_container
    
    def add_message(self, message: Message):
        """Add a new message with modern bubble design"""
        is_user = message.role == Role.USER
        
        # Clear welcome message on first message
        if len(self.message_rows) == 0:
            self.messages_container.clear()
        
        with self.messages_container:
            with ui.row().classes('w-full items-start gap-3' + (' justify-end' if is_user else ' justify-start')):
                if not is_user:
                    # AI Avatar (left side) with gradient
                    with ui.avatar().style(
                        'background-color: var(--bg-secondary); border: 1px solid var(--border-color);'
                    ):
                        ui.icon('auto_awesome', size='sm', color='white')
                
                # Message bubble with modern design
                bubble_bg = (
                    'background-color: var(--accent-color);'
                    if is_user else
                    'background-color: var(--bg-secondary); border: 1px solid var(--border-color);'
                )
                
                with ui.card().classes('max-w-2xl p-4 shadow-lg').style(
                    bubble_bg + 'border-radius: 16px;'
                ):
                    msg_element = ui.markdown(message.content).classes(
                        'prose prose-invert max-w-none'
                    ).style(
                        'color: white;' if is_user else 'color: var(--text-primary);'
                    )
                    self.message_rows.append({
                        'element': msg_element,
                        'is_user': is_user
                    })
                
                if is_user:
                    # User Avatar (right side)
                    with ui.avatar().style('background-color: var(--accent-color);'):
                        ui.icon('person', size='sm', color='white')
        
        # Auto-scroll to bottom
        self._scroll_to_bottom()
    
    def _scroll_to_bottom(self):
        """Scroll chat to bottom"""
        if self.scroll_area:
            # Use NiceGUI's scroll_to method
            self.scroll_area.scroll_to(percent=1.0)
    
    def update_last_message(self, content: str):
        """Update the content of the last message (for streaming)"""
        if self.message_rows:
            last_msg = self.message_rows[-1]
            last_msg['element'].set_content(content)
            # Auto-scroll während Streaming
            self._scroll_to_bottom()
    
    def clear(self):
        """Clear all messages and show welcome screen"""
        self.messages_container.clear()
        self.message_rows.clear()
        
        # Re-add welcome message
        with self.messages_container:
            with ui.column().classes('items-center justify-center mt-20 mb-10'):
                ui.icon('chat_bubble', size='xl').classes('text-blue-400 mb-4')
                ui.label('Start a conversation').classes('text-2xl font-bold text-gray-200')
                ui.label('Choose a model and send your first message').classes('text-sm text-gray-500')
