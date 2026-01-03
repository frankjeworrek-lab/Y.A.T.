"""
Factory Reset Utility
Provides safe, user-initiated reset to factory defaults.
"""
import shutil
import sys
import os
import asyncio
from pathlib import Path
from .paths import get_data_path


def execute_factory_reset() -> bool:
    """
    Permanently delete all user data.
    
    Returns:
        bool: True if successful, False if failed
    """
    try:
        data_dir = Path(get_data_path('.'))
        
        if data_dir.exists():
            # Nuclear option: Remove entire user data directory
            shutil.rmtree(data_dir)
            print(f"[FACTORY RESET] Deleted: {data_dir}")
            return True
        else:
            print(f"[FACTORY RESET] No data directory found at: {data_dir}")
            return True  # Nothing to delete = success
            
    except Exception as e:
        print(f"[FACTORY RESET ERROR] {e}")
        return False


async def _delayed_restart():
    """Internal: Restart with delay to allow event handler to complete"""
    await asyncio.sleep(0.5)  # Give event loop time to finish
    try:
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        print(f"[RESTART ERROR] {e}")
        print("[RESTART] Falling back to exit. Please restart manually.")
        os._exit(0)  # Hard exit without exception


async def _delayed_close():
    """Internal: Close with delay to allow event handler to complete"""
    await asyncio.sleep(0.5)  # Give event loop time to finish
    
    # Try to close PyWebView window if running in desktop mode
    try:
        import webview
        # Get all windows and destroy them
        for window in webview.windows:
            window.destroy()
        await asyncio.sleep(0.2)  # Give window time to close
    except Exception as e:
        print(f"[DEBUG] PyWebView close attempt: {e}")
    
    # Try graceful NiceGUI shutdown
    try:
        from nicegui import app
        app.shutdown()
        await asyncio.sleep(0.2)  # Give shutdown time to process
    except Exception:
        pass
    
    # Hard exit without raising SystemExit exception
    os._exit(0)


def restart_app():
    """
    Attempt to restart the application.
    Schedule restart in background to avoid event loop issues.
    """
    asyncio.create_task(_delayed_restart())


def close_app():
    """
    Gracefully close the application.
    Schedule close in background to avoid event loop issues.
    """
    asyncio.create_task(_delayed_close())
