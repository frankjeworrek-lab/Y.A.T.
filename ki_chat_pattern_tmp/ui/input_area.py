import asyncio
import flet as ft

class InputArea(ft.Container):
    def __init__(self, on_submit):
        super().__init__()
        self.on_submit = on_submit
        self.padding = 20
        self.bgcolor = ft.Colors.SURFACE
        
        self.text_field = ft.TextField(
            hint_text="Ask anything...",
            min_lines=1,
            max_lines=5,
            filled=True,
            border_radius=25,
            shift_enter=True,
            on_submit=self.handle_submit,
            expand=True,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor="surfaceVariant",
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=20, vertical=15)
        )
        
        self.send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=ft.Colors.PRIMARY,
            on_click=self.handle_click_submit,
            tooltip="Send message"
        )
        
        self.content = ft.Row(
            controls=[
                self.text_field, 
                self.send_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    async def handle_submit(self, e):
        text = self.text_field.value.strip()
        if text:
            self.text_field.value = ""
            self.update()
            
            # Always submit - AppLayout handles queuing
            import inspect
            if inspect.iscoroutinefunction(self.on_submit):
                await self.on_submit(text)
            else:
                self.on_submit(text)

    async def handle_click_submit(self, e):
        await self.handle_submit(e)

    def disable(self):
        self.send_button.disabled = True
        self.update()

    async def enable(self):
        self.send_button.disabled = False
        self.update()
