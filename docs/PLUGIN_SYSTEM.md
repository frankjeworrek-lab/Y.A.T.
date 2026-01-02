# Plugin System Documentation

## 🔌 **True Plugin Architecture**

The Y.A.T. now features a **true plugin system** where providers are automatically discovered and loaded from the `plugins/` directory.

---

## 🎯 **How It Works**

### **Auto-Discovery Flow:**

```
App Start
    ↓
PluginLoader scans plugins/
    ↓
Finds: openai_plugin.py, anthropic_plugin.py, mock_plugin.py
    ↓
Dynamically imports each .py file
    ↓
Finds BaseLLMProvider subclass
    ↓
Creates instance & initializes
    ↓
Registers with LLMManager
    ↓
✅ Provider available in UI!
```

---

## 📁 **Plugin Structure**

```
ki_chat_pattern_nicegui/
├── plugins/                        # Plugin directory
│   ├── _template_plugin.py        # Template for new plugins
│   ├── openai_plugin.py           # OpenAI provider
│   ├── anthropic_plugin.py        # Anthropic/Claude provider
│   ├── mock_plugin.py             # Test provider
│   └── your_custom_plugin.py      # Your plugin!
│
├── core/
│   ├── plugin_loader.py           # Auto-discovery engine
│   └── provider_config_manager.py # Configuration management
│
└── provider_config.json            # Provider settings
```

---

## ✨ **Creating a New Plugin**

### **Step 1: Copy Template**
```bash
cp plugins/_template_plugin.py plugins/my_provider_plugin.py
```

### **Step 2: Implement Required Methods**
```python
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo

class MyProvider(BaseLLMProvider):
    async def initialize(self):
        # Load API keys, create clients
        pass
    
    async def get_available_models(self) -> list[ModelInfo]:
        # Return list of models
        return [ModelInfo(...)]
    
    async def stream_chat(...) -> AsyncIterator[str]:
        # Stream responses
        yield "text chunk"
```

### **Step 3: Add to Config** (optional)
```json
// provider_config.json
{
  "id": "my_provider",
  "name": "My Provider",
  "enabled": true,
  "settings": [
    {"key": "api_key", "type": "password", "env_var": "MY_PROVIDER_API_KEY"}
  ]
}
```

### **Step 4: Restart App**
```bash
python main_nicegui_desktop.py
```

**That's it!** Your plugin is auto-discovered and loaded.

---

## 🚀 **Plugin Features**

### **Auto-Discovery**
- ✅ Drop `.py` file in `/plugins` → Automatically loaded
- ✅ No code changes needed in `main.py`
- ✅ Plugin errors don't crash the app

### **Hot-Reload** (coming soon)
- ⏳ Edit plugin → Reload without app restart
- ⏳ Disable plugin → Removed from UI
- ⏳ Enable plugin → Added to UI

### **Configuration**
- ✅ Settings via `provider_config.json`
- ✅ Enable/Disable via GUI
- ✅ API keys in `.env` (secure)

### **Community-Ready**
- ✅ Share plugins as single `.py` files
- ✅ Plugin marketplace possible
- ✅ Templates for common providers

---

## 📝 **Plugin Template Explained**

Every plugin needs these 3 methods:

### **1. `initialize()`**
```python
async def initialize(self):
    """
    Called on app startup AND when settings change.
    CRITICAL: You must handle re-initialization robustly!
    """
    # 1. Reset Error State (Crucial for recovery)
    self.config.init_error = None
    
    # 2. Close old client (Avoid leaks)
    if self.client:
        try: await self.client.close()
        except: pass
        
    # 3. Load & Sanitize Key
    self.api_key = os.getenv('YOUR_API_KEY')
    if self.api_key:
        self.api_key = self.api_key.strip()
        
    if not self.api_key:
        self.config.init_error = "API key missing"
        return
        
    # 4. Create new client
    # self.client = ...
```

### **2. `get_available_models()`**
```python
async def get_available_models(self) -> list[ModelInfo]:
    """Return models this provider supports"""
    return [
        ModelInfo(
            id="model-id",
            name="Display Name",
            provider="ProviderName",
            context_length=8000,
            supports_streaming=True
        )
    ]
```

### **3. `stream_chat()`**
```python
async def stream_chat(
    self,
    messages: list[Message],
    model_id: str,
    temperature: float,
    max_tokens: int
) -> AsyncIterator[str]:
    """Stream chat responses"""
    # Call your API
    async for chunk in api_stream:
        yield chunk.text
```

---

## 🔧 **Plugin Loader API**

### **Usage in Code:**
```python
from core.plugin_loader import PluginLoader

loader = PluginLoader(plugins_dir="plugins")

# Discover all plugins
plugins = loader.load_all_plugins()

# Load specific plugin
provider_class = loader.load_plugin("openai_plugin")

# Get plugin info
info = loader.get_plugin_info("openai_plugin")

# Reload plugin (hot-reload)
loader.reload_plugin("openai_plugin")
```

---

## 🎨 **Example: Cohere Plugin**

```python
# plugins/cohere_plugin.py
import os
from typing import AsyncIterator
from core.providers.base_provider import BaseLLMProvider
from core.providers.types import Message, ProviderConfig, ModelInfo

class CohereProvider(BaseLLMProvider):
    async def initialize(self):
        # 1. Reset & Clean
        self.config.init_error = None
        if self.client:
             try: await self.client.close()
             except: pass
             
        # 2. Key
        self.api_key = os.getenv('COHERE_API_KEY')
        if not self.api_key:
            self.config.init_error = "COHERE_API_KEY not set"
            return
        
        # 3. Client
        from cohere import AsyncClient
        self.client = AsyncClient(api_key=self.api_key.strip())
    
    async def get_available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                id="command-r",
                name="Command R",
                provider="Cohere",
                context_length=128000,
                supports_streaming=True
            )
        ]
    
    async def stream_chat(...) -> AsyncIterator[str]:
        stream = await self.client.chat_stream(
            model=model_id,
            message=messages[-1].content,
            chat_history=[...],
        )
        async for chunk in stream:
            if chunk.text:
                yield chunk.text
```

**Save, restart, done!** Cohere is now in your model dropdown.

---

## 🐛 **Debugging Plugins**

### **Check Plugin Status:**
```python
# Terminal output shows:
🔌 Plugin System: Loaded 3 plugin(s)
  ✓ Registered: openai
  ✓ Registered: anthropic
  ✗ Failed to register my_plugin: ImportError...
```

### **Common Issues:**

1. **Plugin not loaded**
   - Check filename ends with `.py`
   - Check it's in `plugins/` directory
   - Check no syntax errors

2. **Import errors**
   - Install required package: `pip install provider-sdk`
   - Check imports at top of file

3. **API errors**
   - Check API key in `.env`
   - Check provider_config.json has correct env_var

---

## 🎯 **Best Practices**

1. **Naming Convention:**
   - `provider_name_plugin.py` (e.g., `openai_plugin.py`)
   - Class name: `ProviderNameProvider` (e.g., `OpenAIProvider`)

2. **Error Handling:**
   - Set `self.config.init_error` on failures
   - Don't crash - return gracefully
   - Log errors to console

3. **Dependencies:**
   - Add to `requirements.txt` if needed
   - Use try/except for optional imports

4. **Testing:**
   - Start with Mock provider as example
   - Test with small messages first
   - Check streaming works

---

## 🌟 **What's Next?**

### **Phase 3 Complete:**
- ✅ Auto-Discovery
- ✅ Dynamic Loading
- ✅ Plugin Template
- ✅ Error Handling

### **Future (Phase 4):**
- ⏳ Hot-Reload (no app restart)
- ⏳ Plugin Marketplace
- ⏳ Plugin Sandboxing
- ⏳ Plugin Dependencies
- ⏳ Plugin Versioning

---

**🚀 You now have a production-ready plugin system!**

Share your plugins, import community plugins, and extend your AI chat app infinitely!
