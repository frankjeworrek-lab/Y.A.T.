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
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        
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
    
    def _create_default_config(self):
        """Create default provider config file with empty structure"""
        default_data = {
            'providers': []
        }
        # Ensure directory exists (just in case)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(default_data, f, indent=2)
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
