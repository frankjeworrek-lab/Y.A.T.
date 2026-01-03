"""
Connection Status Monitor (Wächter)
Passively monitors internet connectivity every 30 seconds.
Provides visual feedback about the global connection state.
"""
from nicegui import ui
import httpx
import asyncio

class ConnectionMonitor:
    def __init__(self):
        self.status = True # Optimistic start
        self.icon = None
        self.label = None
        
    def build(self):
        """Build the UI component (Footer style)"""
        with ui.row().classes('w-full items-center justify-center gap-2 mt-auto pt-4 pb-2 opacity-50 hover:opacity-100 transition-opacity cursor-help'):
            self.icon = ui.icon('wifi', size='xs', color='green')
            self.label = ui.label('System Online').classes('text-[10px] text-gray-500 font-mono')
            
            # Use a timer to check periodically
            ui.timer(30.0, self._check_connection)
            
            # Initial check shortly after startup
            ui.timer(2.0, self._check_connection, once=True)

    async def _check_connection(self):
        try:
            # Check a reliable high-availability endpoint
            async with httpx.AsyncClient(timeout=3.0) as client:
                # Use 1.1.1.1 (Cloudflare) or Google
                await client.get('https://www.google.com', timeout=3.0)
            
            # If we are here, we are online
            if not self.status: # Only update if state changed
                self.status = True
                self.icon.props('icon=wifi color=green')
                self.label.text = 'System Online'
                
        except Exception:
            # If request fails, assume offline
            if self.status:
                self.status = False
                self.icon.props('icon=wifi_off color=red')
                self.label.text = 'Network Error'
