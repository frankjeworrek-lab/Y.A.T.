# Konfiguration

Lerne, wie du **KI Chat Pattern** an deine Bedürfnisse anpassen kannst.

## 📁 Konfigurationsdateien

### `.env` - Umgebungsvariablen

Die `.env`-Datei ist der **zentrale Ort** für API-Keys und sensible Konfiguration.

**Struktur:**
```bash
# .env

# API Keys
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

# Optionale Konfiguration
OPENAI_BASE_URL=https://api.openai.com/v1  # Custom endpoint
ANTHROPIC_BASE_URL=https://api.anthropic.com  # Custom endpoint
```

**Wichtig:**
- ✅ Wird automatisch geladen beim App-Start
- ✅ Bereits in `.gitignore` (nie committen!)
- ✅ Template verfügbar: `.env.example`

### `main.py` - Provider-Konfiguration

Hier aktivierst/deaktivierst du Provider und setzt Defaults:

```python
# main.py

# Standard-Provider festlegen
llm_manager.active_provider_id = "openai"  # Ändere zu deinem bevorzugten Provider
llm_manager.active_model_id = "gpt-4"      # Ändere zu deinem bevorzugten Modell
```

---

## 🔑 API-Keys verwalten

### Keys sicher speichern

**Beste Methode: .env-Datei**
```bash
# .env
OPENAI_API_KEY=sk-proj-abc123...
ANTHROPIC_API_KEY=sk-ant-xyz789...
```

**Vorteile:**
- ✅ Zentral verwaltbar
- ✅ Einfach zu ändern
- ✅ Automatisch ignoriert von Git
- ✅ Funktioniert auf allen Plattformen

### Keys rotieren

**Wann solltest du Keys ändern?**
- 🔄 Regelmäßig (z.B. alle 90 Tage)
- ⚠️ Bei Sicherheitsvorfällen
- 🔓 Wenn Key versehentlich öffentlich wurde

**Wie:**
1. Neuen Key beim Provider erstellen
2. `.env`-Datei aktualisieren
3. App neu starten
4. Alten Key beim Provider löschen

### Keys für verschiedene Umgebungen

**Entwicklung vs. Produktion:**

**.env.development**
```bash
OPENAI_API_KEY=sk-proj-dev-key-hier
```

**.env.production**
```bash
OPENAI_API_KEY=sk-proj-prod-key-hier
```

**Laden:**
```python
# main.py
from dotenv import load_dotenv
import os

# Lade je nach Umgebung
env = os.getenv("APP_ENV", "development")
load_dotenv(f".env.{env}")
```

---

## 🎛️ Provider-Konfiguration

### Provider aktivieren/deaktivieren

**In `main.py`:**

```python
# Provider aktivieren
openai_config = ProviderConfig(name="OpenAI", enabled=True)  # ✅ Aktiv
llm_manager.register_provider("openai", openai_provider)

# Provider deaktivieren
anthropic_config = ProviderConfig(name="Anthropic", enabled=False)  # ❌ Inaktiv
# Oder: Einfach auskommentieren
```

### Custom Base URLs

**Use Case:** Eigene API-Proxies, Azure OpenAI, etc.

```python
# OpenAI über Proxy
openai_config = ProviderConfig(
    name="OpenAI",
    base_url="https://my-proxy.example.com/v1"
)

# Azure OpenAI
azure_config = ProviderConfig(
    name="Azure OpenAI",
    base_url="https://your-resource.openai.azure.com",
    api_key=os.getenv("AZURE_OPENAI_KEY")
)
```

### Provider-spezifische Einstellungen

**Beispiel: Timeout erhöhen**

```python
# In der Provider-Klasse (core/providers/openai_provider.py)

self.client = AsyncOpenAI(
    api_key=api_key,
    base_url=self.config.base_url,
    timeout=60.0  # Default ist 30s
)
```

---

## 🎨 UI-Anpassungen

### Theme (aktuell: Dark Mode)

**Wo:** `main.py`, Zeile ~10

```python
async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK  # DARK, LIGHT, oder SYSTEM
```

**Optionen:**
- `DARK`: Immer Dark Mode
- `LIGHT`: Immer Light Mode
- `SYSTEM`: Folgt Systemeinstellung

### Fenster-Größe

```python
async def main(page: ft.Page):
    # Minimale Größe
    page.window_min_width = 800
    page.window_min_height = 600
    
    # Standard-Größe beim Start
    page.window_width = 1200
    page.window_height = 800
    
    # Maximiert starten
    page.window_maximized = True
```

### Farben anpassen

**Wo:** In den UI-Komponenten (`ui/` Ordner)

**Beispiel: Sidebar-Farbe ändern**

`ui/sidebar.py`, Zeile ~11:
```python
self.bgcolor = "surfaceVariant"  # Ändere zu einer anderen Farbe
```

**Verfügbare Farben:**
- Material Design: `"primary"`, `"secondary"`, `"surface"`, etc.
- Hex: `"#1E88E5"`
- RGB: `"rgb(30, 136, 229)"`

---

## ⚙️ Erweiterte Einstellungen

### Streaming ein/ausschalten

**Aktuell:** Streaming ist immer aktiv.

**Um es zu deaktivieren** (zeigt komplette Antwort am Ende):

In `core/llm_manager.py`:
```python
async def stream_chat(self, message_history, provider_id=None, model_id=None):
    # Option 1: Vollständige Antwort sammeln
    full_response = ""
    async for chunk in provider.stream_chat(mid, message_history):
        full_response += chunk
    yield full_response  # Nur einmal am Ende
    
    # Option 2: Normal streamen (aktuell)
    async for chunk in provider.stream_chat(mid, message_history):
        yield chunk
```

### System-Prompts

**Was sind System-Prompts?**
Anweisungen an die KI, wie sie sich verhalten soll.

**Beispiel:**
```python
# In ui/app_layout.py, run_chat_flow()

# System-Nachricht hinzufügen
system_msg = Message(
    role=Role.SYSTEM,
    content="Du bist ein hilfreicher Assistent der auf Deutsch antwortet."
)
self.message_history.insert(0, system_msg)  # Am Anfang einfügen
```

### Model-Parameter (Temperatur, etc.)

**Wo:** In den Provider-Implementierungen

**Beispiel: OpenAI-Provider**

`core/providers/openai_provider.py`, in `stream_chat()`:
```python
stream = await self.client.chat.completions.create(
    model=model_id,
    messages=openai_messages,
    stream=True,
    temperature=0.7,      # Kreativität (0.0 - 2.0)
    max_tokens=2000,      # Max. Antwort-Länge
    top_p=1.0,           # Nucleus sampling
    frequency_penalty=0,  # Wiederholungen vermeiden
    presence_penalty=0    # Themen-Vielfalt
)
```

**Parameter erklärt:**

| Parameter | Wert | Effekt |
|-----------|------|--------|
| `temperature` | 0.0 | Deterministisch, präzise |
| | 1.0 | Ausgewogen (Standard) |
| | 2.0 | Sehr kreativ, zufällig |
| `max_tokens` | 100 | Kurze Antworten |
| | 2000 | Mittellang (Standard) |
| | 4000+ | Lange Essays |
| `top_p` | 0.1 | Konservativ |
| | 1.0 | Alles möglich (Standard) |

---

## 📊 Logging & Debugging

### Konsolen-Ausgaben aktivieren

**Aktuell:** Warnings und Errors werden ausgegeben.

**Mehr Details:**
```python
# In main.py, am Anfang
import logging

logging.basicConfig(
    level=logging.DEBUG,  # DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Provider-Aufrufe loggen

`core/llm_manager.py`:
```python
async def stream_chat(self, message_history, provider_id=None, model_id=None):
    pid = provider_id or self.active_provider_id
    mid = model_id or self.active_model_id
    
    print(f"[DEBUG] Calling {pid} with model {mid}")  # Logging
    print(f"[DEBUG] Message count: {len(message_history)}")
    
    # ... rest des Codes
```

### Fehler-Tracking

**In jedem Provider** (`stream_chat()` Methode):
```python
try:
    async for chunk in stream:
        yield chunk
except Exception as e:
    import traceback
    print(f"[ERROR] {traceback.format_exc()}")  # Vollständiger Stack Trace
    yield f"Error: {e}"
```

---

## 🔒 Sicherheit & Privacy

### API-Keys schützen

**Best Practices:**
1. ✅ Nie keys im Code hardcoden
2. ✅ `.env` in `.gitignore` (bereits gemacht)
3. ✅ Unterschiedliche Keys für Dev/Prod
4. ✅ Keys regelmäßig rotieren

**Prüfen, ob `.env` in Git ist:**
```bash
git status  # .env sollte NICHT auftauchen
```

Falls doch:
```bash
# Aus Git entfernen (nicht vom Filesystem!)
git rm --cached .env
git commit -m "Remove .env from git"
```

### Lokale Daten

**Was wird gespeichert:**
- ✅ API-Keys: Nur in `.env` (nicht im RAM)
- ⚠️ Chat-History: Aktuell nur im RAM (geht verloren beim Schließen)
- ❌ Keine Telemetrie, keine Analytics

**Für maximale Privacy:**
- Nutze **Ollama** (100% lokal, kein Internet)
- Oder: Eigene Server mit Self-Hosted LLMs

---

## 📝 Konfigurationsdatei-Referenz

### Vollständige `.env`-Vorlage

```bash
# ============================================
# KI Chat Pattern - Configuration
# ============================================

# ---------------------------------------------
# Provider API Keys
# ---------------------------------------------
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

# ---------------------------------------------
# Custom Base URLs (Optional)
# ---------------------------------------------
# OPENAI_BASE_URL=https://api.openai.com/v1
# ANTHROPIC_BASE_URL=https://api.anthropic.com
# GEMINI_BASE_URL=https://generativelanguage.googleapis.com

# ---------------------------------------------
# App Settings (Optional)
# ---------------------------------------------
# APP_ENV=development  # development, production
# LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR
# DEFAULT_PROVIDER=openai
# DEFAULT_MODEL=gpt-4

# ---------------------------------------------
# Advanced (Optional)
# ---------------------------------------------
# API_TIMEOUT=30
# MAX_RETRIES=3
# STREAM_ENABLED=true
```

---

## 🚀 Performance-Tuning

### Startup-Zeit reduzieren

**Problem:** App braucht lange zum Starten.

**Lösung:**
```python
# In main.py: Nur benötigte Provider laden

# Statt alle Provider zu laden:
if os.getenv("OPENAI_API_KEY"):
    # Nur laden, wenn Key vorhanden
    openai_provider = OpenAIProvider(openai_config)
    await openai_provider.initialize()
    llm_manager.register_provider("openai", openai_provider)
```

### Streaming-Performance

**Chunk-Größe anpassen:**

In Provider-Implementierungen (z.B. `openai_provider.py`):
```python
# Größere Chunks = weniger Updates, schneller
# Kleinere Chunks = flüssiger, bessere UX

async for chunk in stream:
    if chunk.choices[0].delta.content:
        # Sammle z.B. 10 Zeichen bevor Update
        buffer += chunk.choices[0].delta.content
        if len(buffer) >= 10:
            yield buffer
            buffer = ""
```

---

## 📚 Weitere Ressourcen

- **Provider-Integration**: [Detaillierter Guide](./03-provider-integration.md)
- **Troubleshooting**: [Probleme lösen](./05-troubleshooting.md)
- **Architektur**: [Technische Details](./06-architecture.md)

---

**Fragen zur Konfiguration?** → [Community-Forum](https://github.com/your-repo/discussions)
