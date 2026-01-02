"""
Provider Configuration Manager
Handles loading, saving, and managing provider configurations
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ProviderSetting:
    """Single provider setting definition"""
    key: str
    label: str
    type: str  # 'text', 'password', 'number', 'boolean'
    required: bool = False
    default: Optional[str] = None
    env_var: Optional[str] = None


@dataclass
class ProviderConfig:
    """Provider configuration"""
    id: str
    name: str
    type: str  # 'cloud' or 'local'
    icon: str
    color: str
    enabled: bool
    config: Dict
    settings: List[Dict]
    status: str = "unknown"  # 'active', 'disabled', 'error', 'offline'
    error_message: Optional[str] = None


from .paths import get_data_path

class ProviderConfigManager:
    """Manages provider configurations"""
    
    def __init__(self, config_file: Optional[str] = None):
        path_str = config_file or get_data_path("provider_config.json")
        self.config_file = Path(path_str)
        self.providers: Dict[str, ProviderConfig] = {}
        self.load_config()
    
    def load_config(self):
        """Load provider configurations from JSON file"""
        if not self.config_file.exists():
            # Create default config
            self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            # Corrupt file, recreate defaults
            self._create_default_config()
            with open(self.config_file, 'r') as f:
                data = json.load(f)
        
        existing_ids = {p.get('id') for p in data.get('providers', [])}
        
        # SELF-HEALING: If standard providers are missing, add them!
        defaults = self._get_default_providers_data()
        modified = False
        
        # Ensure 'providers' list exists
        if 'providers' not in data:
            data['providers'] = []
            
        for default_provider in defaults['providers']:
            if default_provider['id'] not in existing_ids:
                print(f"[FIX] Auto-Repair: Adding missing provider '{default_provider['id']}'")
                data['providers'].append(default_provider)
                modified = True
        
        if modified:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        for provider_data in data.get('providers', []):
            provider = ProviderConfig(**provider_data)
            # Update status based on environment
            provider.status = self._check_provider_status(provider)
            self.providers[provider.id] = provider

    def save_config(self):
        """Save provider configurations to JSON file"""
        data = {
            'providers': [
                {
                    'id': p.id,
                    'name': p.name,
                    'type': p.type,
                    'icon': p.icon,
                    'color': p.color,
                    'enabled': p.enabled,
                    'config': p.config,
                    'settings': p.settings
                }
                for p in self.providers.values()
            ]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _check_provider_status(self, provider: ProviderConfig) -> str:
        """Check provider status based on configuration"""
        if not provider.enabled:
            return "disabled"
        
        # Check if API key is set (for cloud providers)
        if provider.type == "cloud":
            api_key_env = provider.config.get('api_key_env')
            if api_key_env and not os.getenv(api_key_env):
                return "error"
        
        return "active"

    def _get_default_providers_data(self):
        """Return the dictionary of standard default providers"""
        return {
            'providers': [
                {
                    "id": "google",
                    "name": "Google Gemini",
                    "type": "cloud",
                    "icon": "google",
                    "color": "#4285F4",
                    "enabled": True,
                    "config": {
                        "api_key_env": "GOOGLE_API_KEY"
                    },
                    "settings": [
                        {
                            "key": "api_key_env",
                            "label": "API Key Environment Variable",
                            "type": "text",
                            "default": "GOOGLE_API_KEY",
                            "env_var": "GOOGLE_API_KEY"
                        }
                    ]
                },
                {
                    "id": "anthropic",
                    "name": "Anthropic Claude",
                    "type": "cloud",
                    "icon": "smart_toy",
                    "color": "#D97757",
                    "enabled": True,
                    "config": {
                        "api_key_env": "ANTHROPIC_API_KEY"
                    },
                    "settings": [
                        {
                            "key": "api_key_env",
                            "label": "API Key Environment Variable",
                            "type": "text",
                            "default": "ANTHROPIC_API_KEY",
                            "env_var": "ANTHROPIC_API_KEY"
                        }
                    ]
                },
                {
                    "id": "openai",
                    "name": "OpenAI GPT",
                    "type": "cloud",
                    "icon": "bolt",
                    "color": "#10A37F",
                    "enabled": True,
                    "config": {
                        "api_key_env": "OPENAI_API_KEY"
                    },
                    "settings": [
                        {
                            "key": "api_key_env",
                            "label": "API Key Environment Variable",
                            "type": "text",
                            "default": "OPENAI_API_KEY",
                            "env_var": "OPENAI_API_KEY"
                        }
                    ]
                },
                {
                    "id": "ollama",
                    "name": "Ollama (Local)",
                    "type": "local",
                    "icon": "laptop_mac",
                    "color": "#000000",
                    "enabled": True,
                    "config": {
                        "base_url": "http://localhost:11434"
                    },
                    "settings": [
                        {
                            "key": "base_url",
                            "label": "Base URL",
                            "type": "text",
                            "default": "http://localhost:11434",
                        }
                    ]
                },
                {
                    "id": "groq",
                    "name": "Groq",
                    "type": "cloud",
                    "icon": "speed",
                    "color": "#f55036",
                    "enabled": True,
                    "config": {
                        "api_key_env": "GROQ_API_KEY"
                    },
                    "settings": [
                        {
                            "key": "api_key_env",
                            "label": "API Key Environment Variable",
                            "type": "text",
                            "default": "GROQ_API_KEY",
                            "env_var": "GROQ_API_KEY"
                        }
                    ]
                },
                {
                    "id": "mistral",
                    "name": "Mistral AI",
                    "type": "cloud",
                    "icon": "wind_power",
                    "color": "#fd6f00",
                    "enabled": True,
                    "config": {
                        "api_key_env": "MISTRAL_API_KEY"
                    },
                    "settings": [
                        {
                            "key": "api_key_env",
                            "label": "API Key Environment Variable",
                            "type": "text",
                            "default": "MISTRAL_API_KEY",
                            "env_var": "MISTRAL_API_KEY"
                        }
                    ]
                },
                {
                    "id": "deepseek",
                    "name": "DeepSeek",
                    "type": "cloud",
                    "icon": "search",
                    "color": "#4d6bfe",
                    "enabled": True,
                    "config": {
                        "api_key_env": "DEEPSEEK_API_KEY"
                    },
                    "settings": [
                        {
                            "key": "api_key_env",
                            "label": "API Key Environment Variable",
                            "type": "text",
                            "default": "DEEPSEEK_API_KEY",
                            "env_var": "DEEPSEEK_API_KEY"
                        }
                    ]
                }
            ]
        }
    
    def _create_default_config(self):
        """Create default provider config file with standard providers"""
        default_data = self._get_default_providers_data()
        # Ensure directory exists (just in case)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(default_data, f, indent=2)
    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider configuration by ID"""
        return self.providers.get(provider_id)
    
    def get_all_providers(self) -> List[ProviderConfig]:
        """Get all provider configurations"""
        return list(self.providers.values())
    
    def get_enabled_providers(self) -> List[ProviderConfig]:
        """Get only enabled providers"""
        return [p for p in self.providers.values() if p.enabled]
    
    def enable_provider(self, provider_id: str):
        """Enable a provider"""
        if provider_id in self.providers:
            self.providers[provider_id].enabled = True
            self.providers[provider_id].status = self._check_provider_status(self.providers[provider_id])
            self.save_config()
    
    def disable_provider(self, provider_id: str):
        """Disable a provider"""
        if provider_id in self.providers:
            self.providers[provider_id].enabled = False
            self.providers[provider_id].status = "disabled"
            self.save_config()
    
    def update_provider_config(self, provider_id: str, config_updates: Dict):
        """Update provider configuration"""
        if provider_id in self.providers:
            self.providers[provider_id].config.update(config_updates)
            self.providers[provider_id].status = self._check_provider_status(self.providers[provider_id])
            self.save_config()
    
    def get_provider_setting_value(self, provider_id: str, setting_key: str) -> Optional[str]:
        """Get a specific setting value for a provider"""
        provider = self.get_provider(provider_id)
        if not provider:
            return None
        
        # Check config first
        if setting_key in provider.config:
            return provider.config[setting_key]
        
        # Check environment variable
        for setting in provider.settings:
            if setting['key'] == setting_key and 'env_var' in setting:
                return os.getenv(setting['env_var'])
        
        return None
