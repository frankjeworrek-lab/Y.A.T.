import json
import os
from typing import Any, Dict

SETTINGS_FILE = "user_settings.json"

class UserConfig:
    @staticmethod
    def load() -> Dict[str, Any]:
        if not os.path.exists(SETTINGS_FILE):
            return {}
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    @staticmethod
    def save(key: str, value: Any) -> None:
        settings = UserConfig.load()
        settings[key] = value
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        settings = UserConfig.load()
        return settings.get(key, default)
