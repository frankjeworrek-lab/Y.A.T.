
import os
from pathlib import Path
import sys

# Define the user data directory
# This will be ~/.yat on macOS/Linux
USER_DATA_DIR = Path.home() / ".yat"

def get_data_path(filename: str) -> str:
    """Get absolute path for a file in the user data directory."""
    return str(USER_DATA_DIR / filename)

def ensure_data_dir():
    """Ensure the user data directory exists."""
    if not USER_DATA_DIR.exists():
        try:
            USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created user data directory: {USER_DATA_DIR}")
        except Exception as e:
            print(f"[ERR] Failed to create data directory {USER_DATA_DIR}: {e}")

def resolve_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a read-only resource (code, assets).
    Works for dev environment and PyInstaller bundle (_MEIPASS).
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # In dev mode, use the project root (assuming this file is in core/)
        # core/paths.py -> parent -> project root
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)
