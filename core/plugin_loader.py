"""
Dynamic Plugin Loader for LLM Providers
Automatically discovers and loads provider plugins from the plugins directory
"""
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import ProviderConfig


class PluginLoader:
    """Dynamically loads provider plugins from the plugins directory"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.loaded_plugins: Dict[str, Type[BaseLLMProvider]] = {}
        self.plugin_errors: Dict[str, str] = {}
        
    def discover_plugins(self) -> List[str]:
        """Discover all Python files in the plugins directory"""
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created plugins directory: {self.plugins_dir}")
            return []
        
        plugin_files = []
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # Skip __init__.py and private files
            plugin_files.append(file_path.stem)
        
        return plugin_files
    
    def load_plugin(self, plugin_name: str) -> Optional[Type[BaseLLMProvider]]:
        """Load a single plugin by name"""
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
        
        plugin_path = self.plugins_dir / f"{plugin_name}.py"
        
        if not plugin_path.exists():
            self.plugin_errors[plugin_name] = f"Plugin file not found: {plugin_path}"
            return None
        
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                self.plugin_errors[plugin_name] = "Failed to create module spec"
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # Find the provider class in the module
            provider_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseLLMProvider) and 
                    obj is not BaseLLMProvider):
                    provider_class = obj
                    break
            
            if provider_class is None:
                self.plugin_errors[plugin_name] = "No BaseLLMProvider subclass found"
                return None
            
            self.loaded_plugins[plugin_name] = provider_class
            print(f"✓ Loaded plugin: {plugin_name} ({provider_class.__name__})")
            return provider_class
            
        except Exception as e:
            self.plugin_errors[plugin_name] = f"Error loading plugin: {str(e)}"
            print(f"✗ Failed to load plugin '{plugin_name}': {e}")
            return None
    
    def load_all_plugins(self) -> Dict[str, Type[BaseLLMProvider]]:
        """Discover and load all plugins"""
        plugin_names = self.discover_plugins()
        
        print(f"\n🔌 Discovering plugins in: {self.plugins_dir}")
        print(f"Found {len(plugin_names)} plugin(s): {', '.join(plugin_names) if plugin_names else 'none'}")
        
        for plugin_name in plugin_names:
            self.load_plugin(plugin_name)
        
        if self.plugin_errors:
            print(f"\n⚠️  {len(self.plugin_errors)} plugin(s) failed to load")
            for name, error in self.plugin_errors.items():
                print(f"  - {name}: {error}")
        
        return self.loaded_plugins
    
    def get_plugin_info(self, plugin_name: str) -> Optional[dict]:
        """Get metadata about a loaded plugin"""
        if plugin_name not in self.loaded_plugins:
            return None
        
        provider_class = self.loaded_plugins[plugin_name]
        return {
            'name': plugin_name,
            'class_name': provider_class.__name__,
            'module': provider_class.__module__,
            'doc': provider_class.__doc__ or "No description available"
        }
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin (for hot-reload)"""
        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]
        
        if plugin_name in self.plugin_errors:
            del self.plugin_errors[plugin_name]
        
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]
        
        result = self.load_plugin(plugin_name)
        return result is not None
