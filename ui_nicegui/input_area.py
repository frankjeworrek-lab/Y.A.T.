"""
InputArea component for NiceGUI
Text input with send button, auto-focus, and modern design
"""
from nicegui import ui
import asyncio


class InputArea:
    def __init__(self, on_submit):
        self.on_submit = on_submit
        self.text_input = None
        self.send_button = None
        
    def build(self):
        """Build the input area UI with professional styling"""
        with ui.card().classes('w-full m-4 p-3 shadow-xl').style(
            'background-color: #1f2937; border: 1px solid #374151; border-radius: 20px;'
        ):
            with ui.row().classes('w-full gap-3 items-center'):
                self.text_input = ui.input(
                    placeholder='Type your message...'
                ).classes('flex-1').props('outlined dense dark standout').style(
                    'background-color: #111827;'
                    'border-radius: 12px;'
                    'color: #e5e7eb;'
                    'font-size: 14px;'
                    'padding: 12px;'
                )
                
                # Bind Enter key with proper on_keydown syntax
                self.text_input.on('keydown.enter', lambda: self._handle_submit_wrapper())
                
                # Send button with gradient
                self.send_button = ui.button(
                    icon='send',
                    on_click=lambda: self._handle_submit_wrapper()
                ).props('round').classes('shadow-lg').style(
                    'background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);'
                    'width: 48px; height: 48px;'
                )
    
    def _handle_submit_wrapper(self):
        """Wrapper to handle sync-to-async conversion"""
        import asyncio
        asyncio.create_task(self._handle_submit())

    
    async def _handle_keydown(self, e):
        """Handle keyboard events"""
        if e.args.get('keycode') == 13 and not e.args.get('shiftKey'):
            await self._handle_submit()
    
    async def _handle_submit(self, e=None):
        """Handle message submission"""
        text = self.text_input.value.strip()
        if text and self.on_submit:
            self.text_input.value = ''
            self.text_input.update()
            await self.on_submit(text)
            # Re-focus input
            try:
                await asyncio.sleep(0.1)
                self.text_input.run_method('focus')
            except Exception as err:
                print(f"Focus error: {err}")
    
    def disable(self):
        """Disable input during processing"""
        if self.send_button:
            self.send_button.disable()
        if self.text_input:
            self.text_input.disable()
    
    def enable(self):
        """Enable input after processing"""
        if self.send_button:
            self.send_button.enable()
        if self.text_input:
            self.text_input.enable()
            try:
                self.text_input.run_method('focus')
            except:
                pass
