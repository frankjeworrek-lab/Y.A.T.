# Architektur & Entwicklung

Technische Dokumentation für Entwickler des **Y.A.T. (NiceGUI Edition)**.

## 🏗️ System-Architektur

### High-Level Overview

```
┌─────────────────────────────────────────────────────┐
│                 Presentation Layer                  │
│               (NiceGUI / PyWebView)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Sidebar  │  │ChatView  │  │ ProviderDialog   │   │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       │             │                 │             │
└───────┼─────────────┼─────────────────┼─────────────┘
        │             │                 │
┌───────▼─────────────▼─────────────────▼─────────────┐
│                 Core Logic Layer                    │
│          ┌───────────────────────┐                  │
│          │      LLMManager       │                  │
│          └──────────▲────────────┘                  │
│                     │                               │
│          ┌──────────┴────────────┐                  │
│          │     PluginLoader      │                  │
│          └──────────▲────────────┘                  │
└─────────────────────┼───────────────────────────────┘
                      │ Auto-Discovery
┌─────────────────────▼───────────────────────────────┐
│                Plugin Layer                         │
│               (plugins/*.py)                        │
│                                                     │
│  ┌────────┐   ┌─────────┐    ┌──────────┐           │
│  │OpenAI  │   │Anthropic│    │ Custom   │           │
│  │Plugin  │   │Plugin   │    │ Plugin   │           │
│  └────────┘   └─────────┘    └──────────┘           │
└─────────────────────────────────────────────────────┘
```

## 🧩 The Plugin System (Phase 3)

The application moved from hardcoded providers to a **dynamic plugin architecture**.

### 1. `PluginLoader` (`core/plugin_loader.py`)
- Scans `plugins/` directory for `.py` files.
- Dynamically imports modules.
- Identifies `BaseLLMProvider` subclasses.
- **Enabled Check**: Verifies with `ProviderConfigManager` if plugin is enabled before loading.

### 2. `ProviderConfigManager` (`core/provider_config_manager.py`)
- Manages `provider_config.json`.
- Handles ENABLED/DISABLED state.
- Does **NOT** store API keys (Security!).

### 3. Hot-Reloading
- **Config**: Changing settings updates the runtime immediately.
- **API Keys**: Saving keys in GUI triggers `_reload_providers()`, re-initializing all active plugins instantly.

## 🔐 Security Architecture

- **.env File**: API keys are ONLY stored here.
- **provider_config.json**: Stores metadata (model names, settings) but NO secrets.
- **Memory**: Keys are loaded into process memory via `os.environ` on startup/reload.

## 🎨 UI Architecture (NiceGUI)

- **Reactive State**: UI updates automatically on state changes.
- **Async-First**: All heavy operations (Streaming, API calls) are non-blocking `async`.
- **Context Handling**: Careful management of background tasks vs. UI slots (fixing `RuntimeError` in callbacks).

---

## 📁 Key Components

| Component | Responsibility |
|-----------|----------------|
| `main_nicegui_desktop.py` | Entry point. Starts web server + PyWebView window. |
| `core.plugin_loader` | The "Engine" that finds and loads providers. |
| `ui_nicegui.api_key_dialog` | Handles secure key entry and triggers Hot-Reload. |
| `plugins/` | Isolated provider logic. Sandbox-ready. |

---

## 🔄 Adding a New Provider

1. Create `plugins/my_provider.py`.
2. Inherit from `BaseLLMProvider`.
3. Implement `check_health()`, `get_models()`, `stream_chat()`.
4. (Optional) Add to `provider_config.json` for default settings.
5. **Restart not required** if Hot-Reload logic is extended to file system events (Phase 4). Currently: Restart app.
