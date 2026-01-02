import flet as ft
from core.providers.types import Message, Role

class ChatView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20
        
        self.messages_list = ft.ListView(
            expand=True,
            spacing=20,
            auto_scroll=True,
        )
        
        self.content = self.messages_list

    def add_message(self, message: Message):
        is_user = message.role == Role.USER
        
        # Avatar
        avatar = ft.CircleAvatar(
            content=ft.Icon(ft.Icons.PERSON if is_user else ft.Icons.AUTO_AWESOME),
            bgcolor=ft.Colors.BLUE_GREY_700 if is_user else ft.Colors.TEAL_700,
            radius=16,
        )
        
        # Message Bubble
        bubble = ft.Container(
            content=ft.Markdown(
                message.content,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme="atom-one-dark",
            ),
            bgcolor=ft.Colors.PRIMARY_CONTAINER if is_user else "surfaceVariant",
            padding=15,
            border_radius=ft.border_radius.only(
                top_left=15, top_right=15, 
                bottom_left=5 if is_user else 15,
                bottom_right=15 if is_user else 5
            ),
            width=600, # Max width constraint? Better to use flexible 
        )
        
        # Flexible layout for bubble to prevent full width
        # Row with alignment
        row = ft.Row(
            controls=[
                avatar if not is_user else ft.Container(),
                bubble,
                avatar if is_user else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        
        self.messages_list.controls.append(row)
        self.update()

    def update_last_message(self, content: str):
        if not self.messages_list.controls:
            return
        
        last_row = self.messages_list.controls[-1]
        # Structure is Row -> [Avatar, Bubble, Avatar]
        # Bubble is index 1
        bubble = last_row.controls[1]
        # Markdown is bubble content
        bubble.content.value = content
        bubble.content.update() # Just update the markdown control for performance
        # self.update() # Avoid full redraw if possible, but auto_scroll might need it
        # self.messages_list.scroll_to(offset=-1, duration=100) # manual scroll if needed

    def clear(self):
        self.messages_list.controls.clear()
        self.update()
