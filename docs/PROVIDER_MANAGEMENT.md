# Provider Management System

## 🎯 Overview

Das Provider-Management-System ermöglicht es, AI-Provider direkt aus der GUI zu konfigurieren, zu aktivieren/deaktivieren und zu verwalten.

## 📁 Architektur

```
ki_chat_pattern_nicegui/
├── provider_config.json              # Provider-Definitionen
├── core/
│   └── provider_config_manager.py   # Config-Management-Logic
└── ui_nicegui/
    ├── provider_settings_dialog.py  # GUI für Provider-Settings
    ├── api_key_dialog.py            # GUI für API-Keys
    └── sidebar.py                    # Integration (2 Buttons)
```

## 🔧 Komponenten

### 1. **Provider Config (JSON)**
- Definiert alle verfügbaren Provider
- Schema für Settings
- Status-Tracking
- Enable/Disable-State

### 2. **ProviderConfigManager**
```python
from core.provider_config_manager import ProviderConfigManager

manager = ProviderConfigManager()

# Get all providers
providers = manager.get_all_providers()

# Enable/Disable
manager.enable_provider('openai')
manager.disable_provider('ollama')

# Update config
manager.update_provider_config('openai', {
    'organization_id': 'org-123'
})
```

### 3. **Provider Settings Dialog**
- Liste aller Provider mit Status
- Toggle on/off
- Provider-spezifische Einstellungen
- Save zu .env und provider_config.json

## 🎨 GUI Features

### **Sidebar**
- ✅ **"Manage Providers"** Button
  - Öffnet Provider-Settings-Dialog
  - Zeigt alle Provider mit Status
  
- ✅ **"Configure API Keys"** Button
  - Öffnet API-Key-Quick-Config
  - Nur für API-Keys

### **Provider Settings Dialog**
```
┌─────────────────────────────────────┐
│ Provider Management                  │
├─────────────────────────────────────┤
│                                     │
│ ┌─ OpenAI ─────────────────────┐  │
│ │ [x] Enabled    Status: ✅    │  │
│ │                               │  │
│ │ API Key: sk-***              │  │
│ │ Organization ID: (optional)  │  │
│ │ Base URL: api.openai.com     │  │
│ └───────────────────────────────┘  │
│                                     │
│ ┌─ Anthropic ───────────────────┐  │
│ │ [x] Enabled    Status: ✅    │  │
│ │                               │  │
│ │ API Key: sk-ant-***          │  │
│ └───────────────────────────────┘  │
│                                     │
│ ┌─ Google Gemini ───────────────┐  │
│ │ [ ] Disabled   Status: ⚠️    │  │
│ └───────────────────────────────┘  │
│                                     │
│          [Cancel]  [Save & Apply]   │
└─────────────────────────────────────┘
```

## 🔄 Workflow

### **User-Workflow:**
1. Klick auf **"Manage Providers"**
2. Toggle Provider on/off
3. Configure Settings für aktive Provider
4. **Save & Apply**
5. App neu starten

### **Technischer Flow:**
```
User Action
    ↓
Provider Settings Dialog
    ↓
ProviderConfigManager
    ↓
├─ Update provider_config.json
├─ Update .env file
└─ Update os.environ
    ↓
Restart App → Changes applied
```

## 📝 Provider Schema

```json
{
  "id": "provider_id",
  "name": "Display Name",
  "type": "cloud|local",
  "icon": "material_icon_name",
  "color": "tailwind_color",
  "enabled": true|false,
  "config": {
    "api_key_env": "ENV_VAR_NAME",
    "base_url": "https://api.example.com"
  },
  "settings": [
    {
      "key": "api_key",
      "label": "API Key",
      "type": "password|text|boolean|number",
      "required": true|false,
      "env_var": "ENV_VAR_NAME",
      "default": "default_value"
    }
  ]
}
```

## ✨ Features

### **Aktuell (Phase 1 + 2):**
- ✅ Provider-Liste anzeigen
- ✅ Enable/Disable Toggle
- ✅ Status-Badges (Active, Disabled, Error)
- ✅ Provider-spezifische Settings
- ✅ API-Key-Management
- ✅ Save zu .env
- ✅ Dynamic Config-Loading

### **Zukünftig (Phase 3):**
- ⏳ Custom Provider hinzufügen
- ⏳ Provider-Templates
- ⏳ Health-Check-Button
- ⏳ Hot-Reload (ohne App-Restart)
- ⏳ Provider-Marketplace

## 🚀 Nutzung

### **Neuen Provider hinzufügen:**
1. Bearbeite `provider_config.json`
2. Füge neue Provider-Definition hinzu
3. Restart App
4. Provider erscheint in "Manage Providers"

### **Provider deaktivieren:**
1. "Manage Providers" öffnen
2. Toggle bei Provider aus
3. Save & Apply
4. Restart App

## 🔐 Security

- API-Keys werden in `.env` gespeichert (git-ignored)
- Password-Felder mit Toggle-Button
- Keine Keys im JSON (nur Referenzen)
- Environment-Variable-Isolation

## 🎯 Best Practices

1. **Entwicklung:** Nutze "Manage Providers" statt `.env` manuell zu bearbeiten
2. **Testing:** Disable ungenutzte Provider für bessere Performance
3. **Production:** Nutze nur benötigte Provider
4. **Security:** API-Keys nie in `provider_config.json` speichern

---

**Status:** ✅ Phase 1 + 2 Implementiert
**Version:** 1.0.0
**Letzte Änderung:** 2026-01-01
