# Provider-Integration (Praxis-Guide)

Dieser Guide zeigt dir **Schritt-für-Schritt**, wie du verschiedene KI-Provider anbindest und nutzt.

## 🎯 Übersicht

**Was sind Provider?**
Provider sind die verschiedenen KI-Dienste (OpenAI, Anthropic, Google, etc.), die du in der App nutzen kannst. Die App ist so designed, dass du **mehrere Provider gleichzeitig** nutzen kannst und einfach zwischen ihnen wechseln kannst.

**Unterstützte Provider:**
- ✅ OpenAI (ChatGPT)
- ✅ Anthropic (Claude)
- ✅ Google Gemini
- ✅ Ollama (lokale Modelle)
- ✅ Mock (für Tests)

---

## 🔑 API-Keys besorgen

Bevor du startest, benötigst du API-Keys von den jeweiligen Anbietern.

### OpenAI API-Key

1. Gehe zu [platform.openai.com](https://platform.openai.com)
2. Erstelle einen Account oder logge dich ein
3. Navigiere zu **API Keys** (links im Menü)
4. Klicke **"Create new secret key"**
5. Kopiere den Key (er wird nur einmal angezeigt!)

**Format:** `sk-proj-...` oder `sk-...`

### Anthropic API-Key

1. Gehe zu [console.anthropic.com](https://console.anthropic.com)
2. Erstelle einen Account oder logge dich ein
3. Navigiere zu **API Keys**
4. Klicke **"Create Key"**
5. Kopiere den Key

**Format:** `sk-ant-...`

### Google Gemini API-Key

1. Gehe zu [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Logge dich mit Google ein
3. Klicke **"Create API Key"**
4. Kopiere den Key

**Format:** `AIza...`

---

## 🛠️ Provider konfigurieren

### Methode 1: .env-Datei (Empfohlen)

Die einfachste und sicherste Methode:

**Schritt 1:** Erstelle `.env`-Datei
```bash
# Im Projektverzeichnis
cp .env.example .env
```

**Schritt 2:** Füge deine API-Keys ein
```bash
# .env Datei öffnen und Keys eintragen

OPENAI_API_KEY=sk-proj-dein-key-hier
ANTHROPIC_API_KEY=sk-ant-dein-key-hier
GEMINI_API_KEY=AIza-dein-key-hier
```

**Schritt 3:** App neu starten
```bash
python main.py
```

✅ **Fertig!** Die Provider sind jetzt verfügbar.

### Methode 2: Umgebungsvariablen (Terminal)

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-proj-dein-key"
export ANTHROPIC_API_KEY="sk-ant-dein-key"
python main.py
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-dein-key"
$env:ANTHROPIC_API_KEY="sk-ant-dein-key"
python main.py
```

---

## 🚀 Provider aktivieren/deaktivieren

Öffne `main.py` und passe die Provider-Registrierung an:

### Alle Provider aktiviert (Standard)
```python
# main.py (Lines ~18-36)

# Mock Provider (zum Testen)
mock_config = ProviderConfig(name="Mock Provider")
llm_manager.register_provider("mock", MockProvider(mock_config))

# OpenAI
from core.providers.openai_provider import OpenAIProvider
openai_config = ProviderConfig(name="OpenAI")
openai_provider = OpenAIProvider(openai_config)
await openai_provider.initialize()
llm_manager.register_provider("openai", openai_provider)

# Anthropic
from core.providers.anthropic_provider import AnthropicProvider
anthropic_config = ProviderConfig(name="Anthropic")
anthropic_provider = AnthropicProvider(anthropic_config)
await anthropic_provider.initialize()
llm_manager.register_provider("anthropic", anthropic_provider)
```

### Provider deaktivieren
Kommentiere einfach die entsprechenden Zeilen aus:

```python
# Anthropic deaktivieren
# from core.providers.anthropic_provider import AnthropicProvider
# anthropic_config = ProviderConfig(name="Anthropic")
# anthropic_provider = AnthropicProvider(anthropic_config)
# await anthropic_provider.initialize()
# llm_manager.register_provider("anthropic", anthropic_provider)
```

---

## 📋 Schritt-für-Schritt: OpenAI einrichten

### Komplettes Beispiel

**1. API-Key besorgen** (siehe oben)

**2. `.env`-Datei bearbeiten**
```bash
# .env
OPENAI_API_KEY=sk-proj-ABC123XYZ456...
```

**3. App starten**
```bash
python main.py
```

**4. Model auswählen**
- Öffne die App
- Sidebar → "Select Model"
- Wähle z.B. `gpt-4-turbo (OpenAI)`

**5. Los chatten!**
```
Du: Hallo GPT-4!
AI: Hallo! Wie kann ich dir heute helfen?
```

### Verfügbare OpenAI-Modelle

Nach der Konfiguration siehst du diese Modelle im Dropdown:

| Modell | Beschreibung |
|--------|--------------|
| gpt-4-turbo | Neuestes GPT-4, schnell & günstig |
| gpt-4 | Original GPT-4, sehr capable |
| gpt-3.5-turbo | Schnell & kostengünstig |

---

## 📋 Schritt-für-Schritt: Anthropic (Claude) einrichten

### Komplettes Beispiel

**1. API-Key besorgen**
- Gehe zu [console.anthropic.com](https://console.anthropic.com)
- Erstelle API-Key

**2. `.env` bearbeiten**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-ABC123...
```

**3. App starten**
```bash
python main.py
```

**4. Claude-Modell wählen**
- Sidebar → "Select Model"
- Wähle z.B. `Claude 3 Sonnet (Anthropic)`

### Verfügbare Claude-Modelle

| Modell | Beschreibung | Best For |
|--------|--------------|----------|
| Claude 3 Opus | Höchste Intelligenz | Komplexe Aufgaben |
| Claude 3 Sonnet | Balance | Allgemeine Nutzung |
| Claude 3 Haiku | Schnell & günstig | Einfache Tasks |

---

## 📋 Schritt-für-Schritt: Google Gemini einrichten

Gemini ist **noch nicht** in `main.py` registriert. Hier zeige ich dir, wie du es hinzufügst:

**1. API-Key besorgen** (siehe oben)

**2. `.env` bearbeiten**
```bash
GEMINI_API_KEY=AIzaSyC...
```

**3. Gemini-Provider in `main.py` registrieren**

Öffne `main.py` und füge nach den anderen Providern hinzu:

```python
# In main.py, nach anthropic_provider (circa Line 36)

from core.providers.gemini_provider import GeminiProvider
gemini_config = ProviderConfig(name="Google Gemini")
gemini_provider = GeminiProvider(gemini_config)
await gemini_provider.initialize()
llm_manager.register_provider("gemini", gemini_provider)
```

**4. Abhängigkeit installieren**
```bash
pip install google-generativeai
```

**5. App starten & nutzen**
```bash
python main.py
```

Jetzt siehst du Gemini-Modelle im Dropdown! 🎉

---

## 📋 Schritt-für-Schritt: Ollama (Lokale Modelle)

**Ollama** ermöglicht es dir, Modelle **lokal** auf deinem Computer auszuführen – ohne Internet, ohne API-Kosten, mit voller Privatsphäre!

### Voraussetzungen

**1. Ollama installieren**

**macOS:**
```bash
brew install ollama
```

**Windows/Linux:**
Lade von [ollama.ai](https://ollama.ai) herunter

**2. Ollama-Server starten**
```bash
ollama serve
```

**3. Ein Modell herunterladen**
```bash
# Beispiel: Llama 3.2 (3GB)
ollama pull llama3.2

# Weitere Optionen:
ollama pull mistral        # Mistral 7B
ollama pull codellama      # Code-spezialisiert
ollama pull phi3          # Sehr klein (2GB)
```

### Ollama-Provider erstellen

**1. Provider-Datei erstellen**

Erstelle eine neue Datei: `core/providers/ollama_provider.py`

```python
import httpx
from typing import AsyncGenerator, List
from .base_provider import BaseLLMProvider
from .types import Message, ModelInfo, ProviderConfig

class OllamaProvider(BaseLLMProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        
    async def initialize(self) -> None:
        # Check if Ollama is running
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    print("Warning: Ollama server not reachable")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")

    async def get_models(self) -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                data = response.json()
                
                return [
                    ModelInfo(
                        id=model["name"],
                        name=model["name"],
                        provider="Ollama (Local)"
                    )
                    for model in data.get("models", [])
                ]
        except:
            return []

    async def stream_chat(
        self, 
        model_id: str, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        # Convert to Ollama format
        ollama_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={
                        "model": model_id,
                        "messages": ollama_messages,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "message" in data:
                                content = data["message"].get("content", "")
                                if content:
                                    yield content
        except Exception as e:
            yield f"Error: {e}"

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False
```

**2. In `main.py` registrieren**

```python
# In main.py
from core.providers.ollama_provider import OllamaProvider

ollama_config = ProviderConfig(name="Ollama", base_url="http://localhost:11434")
ollama_provider = OllamaProvider(ollama_config)
await ollama_provider.initialize()
llm_manager.register_provider("ollama", ollama_provider)
```

**3. Nutzen**
- Starte Ollama: `ollama serve`
- Starte App: `python main.py`
- Wähle ein lokales Modell im Dropdown

**Vorteile von Ollama:**
- ✅ **100% Privat**: Daten verlassen deinen Computer nie
- ✅ **Kostenlos**: Keine API-Kosten
- ✅ **Offline**: Funktioniert ohne Internet
- ✅ **Schnell**: Direkter Zugriff, kein API-Overhead

---

## 🔧 Eigenen Provider erstellen

Du kannst **jeden** KI-Service anbinden! Hier ist ein Template:

### 1. Provider-Klasse erstellen

```python
# core/providers/custom_provider.py

from typing import AsyncGenerator, List
from .base_provider import BaseLLMProvider
from .types import Message, ModelInfo, ProviderConfig

class CustomProvider(BaseLLMProvider):
    async def initialize(self) -> None:
        # Setup: API-Client initialisieren, Keys validieren, etc.
        pass

    async def get_models(self) -> List[ModelInfo]:
        # Return: Liste der verfügbaren Modelle
        return [
            ModelInfo(id="model-1", name="My Model", provider="Custom")
        ]

    async def stream_chat(
        self, 
        model_id: str, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        # Implementierung: API-Call und Streaming
        yield "Hello from Custom Provider!"

    async def check_health(self) -> bool:
        # Check: Ist der Service erreichbar?
        return True
```

### 2. In `main.py` registrieren

```python
from core.providers.custom_provider import CustomProvider

custom_config = ProviderConfig(name="My Custom Service")
custom_provider = CustomProvider(custom_config)
await custom_provider.initialize()
llm_manager.register_provider("custom", custom_provider)
```

### Beispiele für Custom Provider

**Mögliche Dienste:**
- Cohere
- Hugging Face Inference API
- AWS Bedrock
- Azure OpenAI
- Groq
- Mistral AI
- Deine eigene API!

## 🎯 Best Practices

### Sicherheit
✅ **DO:**
- API-Keys in `.env` speichern
- `.env` nie in Git committen (ist bereits in `.gitignore`)
- Verschiedene Keys für Dev/Prod verwenden

❌ **DON'T:**
- Keys im Code hardcoden
- Keys öffentlich teilen (GitHub, Discord, etc.)
- Dasselbe Key-Paar für alles nutzen

### Performance
- **Start mit günstigen Modellen**: GPT-3.5, Claude Haiku
- **Nutze Streaming**: Bessere UX, keine Timeouts
- **Lokale Modelle für Privacy**: Ollama für sensitive Daten

### Kosten-Optimierung
- GPT-3.5-Turbo: ~$0.001/1K tokens (günstig)
- Claude Haiku: ~$0.00025/1K tokens (sehr günstig)
- Ollama: $0 (kostenlos, aber benötigt Hardware)

---

## 🐛 Troubleshooting

### "API Key not found"
**Problem:** Provider findet den API-Key nicht.

**Lösung:**
```bash
# 1. Prüfe .env-Datei
cat .env

# 2. Stelle sicher, dass der Key-Name stimmt
OPENAI_API_KEY=sk-...     ✅ Richtig
OPEN_AI_API_KEY=sk-...    ❌ Falsch

# 3. App neu starten
python main.py
```

### "Provider not initialized"
**Problem:** Provider konnte nicht initialisiert werden.

**Lösung:**
1. Prüfe API-Key Format
2. Prüfe Internet-Verbindung
3. Schau in die Konsole für Details

### Modell erscheint nicht im Dropdown
**Checkliste:**
- [ ] Provider in `main.py` registriert?
- [ ] API-Key korrekt in `.env`?
- [ ] Provider enabled? (`config.enabled = True`)
- [ ] App neu gestartet?

### Ollama-Verbindung schlägt fehl
```bash
# 1. Ist Ollama gestartet?
ps aux | grep ollama

# 2. Falls nicht:
ollama serve

# 3. Teste manuell:
curl http://localhost:11434/api/tags
```

---

## 📚 Weiterführendes

- **Konfiguration**: [Erweiterte Einstellungen](./04-configuration.md)
- **Fehlerbehandlung**: [Troubleshooting Guide](./05-troubleshooting.md)
- **Architektur**: [Technische Details](./06-architecture.md)

---

**Viel Erfolg beim Anbinden deiner Provider!** 🚀

Du hast Fragen? → [Community-Forum](https://github.com/your-repo/discussions)
