import shutil
from pathlib import Path
import sys
import os

def reset():
    # Detect Home Directory correctly on all OS
    data_dir = Path.home() / ".yat"
    
    print(f"\n[RESET TOOL]")
    print(f"Target Directory: {data_dir}")
    
    if not data_dir.exists():
        print("[INFO] Directory does not exist. Clean state confirmed.")
        return

    # Safety Check
    print(f"[WARN] This will delete all Settings, Keys, and Chat History!")
    response = input(f"Are you sure you want to delete {data_dir}? [y/N] ")
    
    if response.lower() == 'y':
        try:
            shutil.rmtree(data_dir)
            print(f"[OK] Successfully deleted {data_dir}")
        except Exception as e:
            print(f"[ERR] Failed to delete: {e}")
            print("Tip: Close the application before running this script.")
    else:
        print("[INFO] Aborted.")

if __name__ == "__main__":
    reset()
