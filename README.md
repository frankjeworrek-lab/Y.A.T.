# Y.A.T. (Yet Another Talk)

> **Version 2.0** — *The "Refined Flow" Update*

Y.A.T. is a premium, distraction-free AI terminal designed for "Deep Work" and fluid dialogue. Built with **Python**, **NiceGUI**, and **PyWebView**, it combines the power of a terminal with the aesthetics of a modern web app.

---

## 🌟 Key Features (v2.0)

### 🎨 Premium Aesthetics & Theming
- **Dynamic Theme Engine**: Switch instantly between 5 curated themes:
  - 🌙 *Midnight Pro* (Default)
  - ❄️ *Nordic Frost*
  - 🔮 *Cyberpunk Neon*
  - 📟 *Retro Terminal*
  - 🧛 *Dracula*
- **UI Scaling**: Adjustable interface density via settings slider (12px - 20px base size).
- **Glassmorphic Design**: Modern, clean visuals with reduced distraction.

### 🧠 Multi-Provider Intelligence
- **True Plugin System**: Drop `.py` files in `plugins/` to add new models.
- **Supported Providers**:
  - 🟢 **OpenAI** (GPT-4o, etc.)
  - 🟣 **Anthropic** (Claude 3.5 Sonnet, Opus)
  - 🔵 **Google** (Gemini Pro)
- **Hot-Swapping**: Switch active models instantly without context loss.

### ⚙️ Unified Preferences
- **Centralized Control**: Manage API Keys, Active Models, and Appearance in one dialog.
- **Robust Configuration**: Settings persist `provider_config.json` and `.env` (secrets).

### 📐 Dual-Mode Architecture
- 🖥️ **Desktop Mode**: Runs as a standalone native app window (via PyWebView).
- 🌐 **Web Mode**: Runs in your browser for remote access or debugging.

---

## 🚀 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Setup
Create a `.env` file for your keys (optional, can also be set in UI):
```properties
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### 3. Launch
**Standard Desktop Mode (Recommended):**
```bash
python main.py
```

**Web / Browser Mode:**
```bash
python main.py --web
```

---

## 🧩 How to Use

### The "Preferences" Center
Click the **Preferences** button (Slider Icon) in the sidebar footer to:
1.  **AI Providers Tab**: Enable/Disable providers and enter API Keys.
2.  **Appearance Tab**: Select your favorite theme and adjust text size.

### Plugin System
Providers are located in `plugins/`. The system auto-discovers them at startup.
To add a new LLM, simply duplicate `plugins/_template_plugin.py` and implement the interface.

---

## 📦 Deployment (macOS App)

To turn Y.A.T. into a standalone `Y.A.T.app` with a proper Dock icon:

1.  Ensure you have `logo/dock.png` (App Icon) present.
2.  Run the build script:
    ```bash
    ./build_mac.sh
    ```
3.  The app will be generated in `dist/Y.A.T.app`.
4.  Drag it to your Applications folder.

---

## 📁 Project Structure

```
ki_chat_pattern_nicegui/
├── main.py                 # Unified Entry Point (Desktop & Web)
├── plugins/                # LLM Provider Plugins
│   ├── openai_plugin.py
│   ├── anthropic_plugin.py
│   └── google_plugin.py
├── ui_nicegui/             # UI Components (Sidebar, Chat, Settings)
├── core/                   # Logic Managers (LLM, Config)
├── storage/                # Chat History Database
├── logo/                   # Branding Assets
└── .env                    # Secrets Storage
```

---
*Architected for Flow.*

## 🏆 Credits

**Architect & Lead Design:** Frank Jeworrek
*Concept, UX Philosophy, and System Architecture.*

**Powered by:** NiceGUI & Antigravity
