# Quick Start: Von API-Key bis Chat in 2 Minuten

**Du hast einen API-Key und willst SOFORT chatten?** Hier entlang! ⚡

## 📋 Welcher Provider ist für dich am einfachsten?

| Provider | Setup | Status | Warum so? |
|----------|-------|--------|-----------|
| **OpenAI** | ⚡ 2 Min | ✅ **Fertig eingebaut** | Nur Key eintragen → läuft! |
| **Anthropic** | ⚡ 2 Min | ✅ **Fertig eingebaut** | Nur Key eintragen → läuft! |
| **Gemini** | ⚠️ 5 Min | ⚠️ **Braucht Aktivierung** | Extra-Bibliothek + Code in main.py |
| **Mock** | 🚀 30 Sek | ✅ **Immer aktiv** | Kein Key nötig, zum Testen |
| **Ollama** | 🔧 10 Min | ⚠️ **Setup nötig** | Lokale Installation + Provider-Code |

**💡 Tipp:** Hast du OpenAI oder Anthropic? → **Schnellster Weg!**  
**💡 Tipp:** Willst du nur testen? → **Mock-Provider** (keine Konfiguration)

---

## 🎯 Wähle dein Szenario:

➡️ [Ich habe OpenAI-Key](#openai-2-minuten) ✅ **Sofort ready**  
➡️ [Ich habe Anthropic/Claude-Key](#anthropic-2-minuten) ✅ **Sofort ready**  
➡️ [Ich habe Google Gemini-Key](#gemini-5-minuten) ⚠️ **Extra-Schritte**  
➡️ [Ich will ohne Key testen](#ohne-key-30-sekunden) ✅ **Keine Config**  
➡️ [Ich will lokal/offline (Ollama)](#ollama-10-minuten) ⚠️ **Setup-Aufwand**

---

## OpenAI (2 Minuten)

> **✅ Warum so schnell?** OpenAI-Provider ist **bereits in der App eingebaut**.  
> Du musst nur deinen API-Key eintragen - kein Code ändern!

**Du hast:** API-Key von [platform.openai.com](https://platform.openai.com)  
**Format:** `sk-proj-...` oder `sk-...`

### Schritt 1: Dependencies installieren

```bash
cd ki_chat_pattern
pip install -r requirements.txt
```

### Schritt 2: API-Key hinterlegen

```bash
# Erstelle .env-Datei (Kopie der Vorlage)
cp .env.example .env
```

Öffne `.env`. Du siehst dort alle Provider **auskommentiert** (mit `#` davor).

Suche den OpenAI-Abschnitt:
```bash
# OPENAI_API_KEY=sk-proj-DEIN-KEY-HIER-EINFUEGEN
```

👉 **Schritt A:** Entferne das `#` am Anfang der Zeile.  
👉 **Schritt B:** Ersetze den Platzhalter mit deinem echten Key.

Das Ergebnis sollte so aussehen:
```bash
OPENAI_API_KEY=sk-proj-12345...
# (Andere Zeilen bleiben mit # auskommentiert)
```

**Speichern nicht vergessen!**

### Schritt 3: App starten

```bash
python main.py
```

### Schritt 4: Chatten!

1. **App öffnet sich** automatisch
2. **Sidebar links:** Dropdown "Select Model"
3. **Wähle:** `gpt-4-turbo (OpenAI)` oder `gpt-3.5-turbo (OpenAI)`
4. **Unten:** Tippe deine Nachricht
5. **Enter** oder Send-Button → **Fertig!** 🎉

**Erwartetes Ergebnis:**
```
You: Hallo GPT-4!
AI: Hallo! Wie kann ich dir heute helfen? [streaming...]
```

---

## Anthropic (2 Minuten)

> **✅ Warum so schnell?** Anthropic-Provider ist **bereits in der App eingebaut**.  
> Du musst nur deinen API-Key eintragen - kein Code ändern!

**Du hast:** API-Key von [console.anthropic.com](https://console.anthropic.com)  
**Format:** `sk-ant-...`

### Schritt 1: Dependencies installieren

```bash
cd ki_chat_pattern
pip install -r requirements.txt
```

### Schritt 2: API-Key hinterlegen

```bash
# Erstelle .env-Datei
cp .env.example .env
```

Öffne `.env`. Du siehst dort alle Provider **auskommentiert** (mit `#` davor).

Suche den Anthropic-Abschnitt:
```bash
# ANTHROPIC_API_KEY=sk-ant-DEIN-KEY-HIER-EINFUEGEN
```

👉 **Schritt A:** Entferne das `#` am Anfang der Zeile.  
👉 **Schritt B:** Ersetze den Platzhalter mit deinem echten Key.

Das Ergebnis sollte so aussehen:
```bash
ANTHROPIC_API_KEY=sk-ant-12345...
# (Andere Zeilen bleiben mit # auskommentiert)
```

**Speichern nicht vergessen!**

### Schritt 3: App starten

```bash
python main.py
```

### Schritt 4: Chatten!

1. **Dropdown "Select Model"** → Wähle `Claude 3 Sonnet (Anthropic)` oder `Claude 3 Opus (Anthropic)`
2. **Nachricht tippen** → Enter
3. **Streaming-Antwort** erscheint! 🎉

**Erwartetes Ergebnis:**
```
You: Hi Claude!
AI: Hello! I'm Claude, an AI assistant created by Anthropic... [streaming...]
```

---

## Gemini (5 Minuten)

> **⚠️ Warum länger?** Gemini ist NICHT vorinstalliert.  
> Du musst:  
> 1. Extra-Bibliothek installieren (`pip install google-generativeai`)  
> 2. Provider-Code in `main.py` aktivieren (Copy & Paste unten)

**Du hast:** API-Key von [Google AI Studio](https://makersuite.google.com/app/apikey)  
**Format:** `AIza...`

### Schritt 1: Dependencies installieren

```bash
cd ki_chat_pattern
pip install -r requirements.txt
pip install google-generativeai  # Extra für Gemini
```

### Schritt 2: API-Key hinterlegen

```bash
# Erstelle .env-Datei
cp .env.example .env
```

Öffne `.env` und füge ein:

```bash
GEMINI_API_KEY=AIza-DEIN-KEY-HIER
```

**Speichern!**

### Schritt 3: Gemini-Provider aktivieren

Öffne `main.py` und füge **nach Zeile 36** (nach `anthropic_provider`) ein:

```python
# Google Gemini Provider
from core.providers.gemini_provider import GeminiProvider
gemini_config = ProviderConfig(name="Google Gemini")
gemini_provider = GeminiProvider(gemini_config)
await gemini_provider.initialize()
llm_manager.register_provider("gemini", gemini_provider)
```

**Speichern!**

### Schritt 4: (Optional) Als Standard setzen

In der gleichen `main.py`, Zeilen ~37-38:

```python
# Set init defaults
llm_manager.active_provider_id = "gemini"  # Statt "mock"
llm_manager.active_model_id = "gemini-2.0-flash-exp"
```

### Schritt 5: App starten

```bash
python main.py
```

### Schritt 6: Chatten!

1. **Dropdown:** Wähle `gemini-2.0-flash-exp (Google Gemini)` oder `gemini-pro (Google Gemini)`
2. **Los chatten!** 🎉

**Erwartetes Ergebnis:**
```
You: Hello Gemini!
AI: Hello! How can I help you today? [streaming...]
```

---

## Ohne Key (30 Sekunden)

**Du willst nur testen ohne API-Keys?**

### Schritt 1: Dependencies installieren

```bash
cd ki_chat_pattern
pip install -r requirements.txt
```

### Schritt 2: App starten

```bash
python main.py
```

### Schritt 3: Mock-Provider nutzen

1. **Dropdown:** Wähle `Mock GPT-4 (MockProvider)`
2. **Nachricht tippen** → Enter
3. **Mock-Antwort** erscheint (simuliert) 🎭

**Was du siehst:**
```
You: Test message
AI: This is a mocked response from mock-gpt-4. I received your message: 'Test message'... [streaming...]
```

**Zweck:** UI/Features testen, ohne echte API-Kosten.

---

## Ollama (10 Minuten)

**Du willst 100% lokal/offline, kostenlos?**

### Schritt 1: Ollama installieren

**macOS:**
```bash
brew install ollama
```

**Windows/Linux:** Download von [ollama.ai](https://ollama.ai)

### Schritt 2: Ollama starten

```bash
ollama serve
```

**Neues Terminal öffnen!**

### Schritt 3: Model herunterladen

```bash
# Llama 3.2 (3GB) - Empfohlen
ollama pull llama3.2

# Oder andere:
ollama pull mistral      # 7GB
ollama pull phi3         # 2GB (klein & schnell)
ollama pull codellama    # Code-spezialisiert
```

### Schritt 4: App-Dependencies

```bash
cd ki_chat_pattern
pip install -r requirements.txt
```

### Schritt 5: Ollama-Provider Code erstellen

Die Datei `core/providers/ollama_provider.py` existiert bereits! (Siehe `03-provider-integration.md` für den Code)

Falls nicht, erstelle sie mit diesem Inhalt:

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

### Schritt 6: In main.py registrieren

Öffne `main.py` und füge nach den anderen Providern ein:

```python
# Ollama Provider
from core.providers.ollama_provider import OllamaProvider

ollama_config = ProviderConfig(name="Ollama", base_url="http://localhost:11434")
ollama_provider = OllamaProvider(ollama_config)
await ollama_provider.initialize()
llm_manager.register_provider("ollama", ollama_provider)
```

### Schritt 7: App starten

```bash
python main.py
```

### Schritt 8: Lokal chatten!

1. **Dropdown:** Wähle `llama3.2 (Ollama (Local))`
2. **Komplett offline chatten!** 🔒

**Vorteile:**
- ✅ 100% privat
- ✅ Kostenlos
- ✅ Keine Internet-Abhängigkeit
- ✅ Eigenes Model-Hosting

---

## 🎯 Zusammenfassung

| Provider | Setup-Zeit | Kosten | Privacy | Internet nötig? |
|----------|------------|--------|---------|-----------------|
| **OpenAI** | 2 Min | Pay-per-use | Cloud | ✅ |
| **Anthropic** | 2 Min | Pay-per-use | Cloud | ✅ |
| **Gemini** | 5 Min | Free Tier | Cloud | ✅ |
| **Mock** | 30 Sek | Kostenlos | 100% lokal | ❌ |
| **Ollama** | 10 Min | Kostenlos | 100% lokal | ❌ |

---

## ❓ Häufige Probleme

### "Warning: API Key not found"

**→ Lösung:** 
1. Prüfe `.env`-Datei: `cat .env`
2. Key-Name korrekt? (`OPENAI_API_KEY` nicht `OPEN_AI_API_KEY`)
3. App neu starten

### "Kein Model im Dropdown"

**→ Lösung:**
1. Provider registriert in `main.py`?
2. API-Key korrekt?
3. Internet-Verbindung (außer Mock/Ollama)?

### "Ollama-Verbindung fehlgeschlagen"

**→ Lösung:**
```bash
# Prüfe ob Ollama läuft:
ps aux | grep ollama

# Falls nicht:
ollama serve

# Test:
curl http://localhost:11434/api/tags
```

---

## 🚀 Nächste Schritte

✅ **Du chattest bereits?** → Probiere [Features aus](./02-features.md)  
✅ **Mehrere Provider?** → [Provider-Integration](./03-provider-integration.md)  
✅ **Eigene Provider?** → [Patterns nutzen](./07-using-patterns.md)

---

**Probleme?** Schreib uns im [GitHub Discussions](https://github.com/your-repo/discussions)

**Es funktioniert?** Gib uns einen ⭐ auf GitHub! 🎉
