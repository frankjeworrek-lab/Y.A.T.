
from nicegui import ui
from core.docs_manager import DocsManager

class DocsDialog:
    def __init__(self):
        self.manager = DocsManager()
        self.dialog = None
        self.content_markdown = None
        self.nav_column = None
        
    def show(self):
        """Show the documentation dialog"""
        with ui.dialog() as self.dialog, ui.card().classes('w-full max-w-7xl h-[85vh] p-0 overflow-hidden').style(
            'background-color: var(--bg-secondary); border: 1px solid var(--border-color);'
        ):
            # Header
            with ui.row().classes('w-full items-center p-4 border-b border-gray-700 justify-between shrink-0').style(
                'background-color: var(--bg-secondary);'
            ):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('menu_book', size='sm').classes('text-blue-400')
                    ui.label('Y.A.T. Knowledge Base').classes('text-lg font-bold text-white')
                
                with ui.row().classes('items-center gap-2'):
                    ui.input(placeholder='Search docs...', on_change=self._handle_search).props(
                        'dense outlined rounded debounce=300'
                    ).classes('w-64').style('background-color: var(--bg-primary);')
                    
                    ui.button(icon='close', on_click=self.dialog.close).props('flat round dense text-color=grey')

            # Body (Splitter)
            with ui.splitter(value=25).classes('w-full flex-1 min-h-0') as splitter:
                # LEFT: Navigation
                with splitter.before:
                    with ui.column().classes('w-full h-full p-2 overflow-y-auto gap-1') as self.nav_column:
                        self._render_file_list()
                
                # RIGHT: Content
                with splitter.after:
                    with ui.column().classes('w-full h-full p-8 overflow-y-auto').style('background-color: var(--bg-primary);'):
                        self.content_markdown = ui.markdown().classes('w-full prose prose-invert prose-blue max-w-none')
            
        self.dialog.open()
        # Load README by default
        self._load_doc('README.md')

    def _render_file_list(self):
        """Render the list of all documents"""
        self.nav_column.clear()
        docs = self.manager.get_all_docs()
        
        with self.nav_column:
            ui.label('Documents').classes('text-xs font-bold text-gray-500 uppercase px-3 py-2')
            for doc in docs:
                ui.button(doc['title'], on_click=lambda f=doc['filename']: self._load_doc(f)).props(
                    'flat align=left no-caps'
                ).classes('w-full text-left text-gray-300 hover:bg-gray-800 rounded-md px-3 py-2 text-sm')

    def _handle_search(self, e):
        """Handle search input"""
        query = e.value
        self.nav_column.clear()
        
        if not query:
            self._render_file_list()
            return
            
        results = self.manager.search(query)
        
        with self.nav_column:
            if not results:
                ui.label('No results found.').classes('text-gray-500 italic p-4 text-sm')
                return
            
            ui.label(f'{len(results)} Matches').classes('text-xs font-bold text-blue-400 uppercase px-3 py-2')
            
            for res in results:
                with ui.column().classes('w-full mb-2'):
                    # Document Title Link
                    ui.button(res['title'], on_click=lambda f=res['filename']: self._load_doc(f)).props(
                        'flat align=left no-caps'
                    ).classes('w-full text-left font-bold text-white hover:bg-gray-800 rounded-md px-3 py-1 dense text-sm')
                    
                    # Context Snippets
                    if res['matches']:
                         with ui.column().classes('pl-4 gap-0'):
                             for m in res['matches']:
                                 ui.label(f"...{m['content']}...").classes('text-xs text-gray-500 truncate w-full')

    def _load_doc(self, filename):
        """Load content into markdown area"""
        content = self.manager.get_doc_content(filename)
        if content:
            self.content_markdown.set_content(content)
