# Patterns für eigene Apps nutzen

Dieses Dokument erklärt Entwicklern, wie sie die **Architektur-Patterns** aus dieser App in ihren **eigenen Projekten** verwenden können.

## 🎯 Zielgruppe

Du bist hier richtig, wenn du:
- ✅ Eine eigene App baust (Web, CLI, Discord-Bot, etc.)
- ✅ LLM-Integration brauchst
- ✅ Die Pattern/Architektur dieser App nutzen willst
- ✅ NICHT die komplette GUI übernehmen willst

**Nicht:** Wenn du diese App nur erweitern willst → siehe [03-provider-integration.md](./03-provider-integration.md)

---

## 🏗️ Was kannst du wiederverwenden?

### 1. **Core-Komponenten (standalone)**

Die Business-Logic funktioniert **unabhängig** von der UI:

```
core/
├── llm_manager.py        ← Provider-Orchestrierung
└── providers/
    ├── base_provider.py  ← Abstract Interface
    ├── types.py          ← Shared Models
    ├── openai_provider.py
    ├── anthropic_provider.py
    └── ...
```

**Diese kannst du 1:1 in eigene Apps kopieren!**

---

### 2. **Architektur-Patterns (Konzepte)**

Selbst wenn du nicht Python nutzt, kannst du die **Patterns** übernehmen:

- **Plugin-System** (Provider als Plugins)
- **Abstract Base Class** Pattern
- **Dependency Injection**
- **Strategy Pattern** (wählbare Algorithmen)
- **Adapter Pattern** (verschiedene APIs → einheitliches Interface)

---

## 📦 Szenario 1: Core-Logik in eigener App nutzen

**Use Case:** Du baust eine Web-App (Flask/FastAPI), willst aber die Provider-Logik wiederverwenden.

### Schritt 1: Core kopieren

```bash
# In deinem Projekt
mkdir my_web_app/llm_core
cp -r ki_chat_pattern/core/* my_web_app/llm_core/
```

### Schritt 2: Standalone nutzen

```python
# my_web_app/backend.py

from llm_core.llm_manager import LLMManager
from llm_core.providers.openai_provider import OpenAIProvider
from llm_core.providers.types import ProviderConfig, Message, Role

# Setup (einmalig beim App-Start)
llm_manager = LLMManager()

openai_config = ProviderConfig(name="OpenAI", api_key="sk-...")
openai_provider = OpenAIProvider(openai_config)
await openai_provider.initialize()
llm_manager.register_provider("openai", openai_provider)

llm_manager.active_provider_id = "openai"
llm_manager.active_model_id = "gpt-4"

# In deinem Endpoint
@app.post("/chat")
async def chat(request):
    user_msg = Message(role=Role.USER, content=request.json['message'])
    history = [user_msg]  # Oder aus Session laden
    
    response = ""
    async for chunk in llm_manager.stream_chat(history):
        response += chunk
        # Optional: per WebSocket streamen
    
    return {"response": response}
```

**Fertig!** Du nutzt jetzt die gleiche Provider-Infrastruktur.

---

## 🌐 Szenario 2: Web-App mit FastAPI

**Komplettes Beispiel:** Web-Chat mit dieser Core-Logic

### Dateistruktur

```
my_chat_web/
├── backend/
│   ├── main.py              # FastAPI App
│   ├── websocket_handler.py # Streaming
│   └── llm_core/            # Kopiert von ki_chat_pattern
│       ├── llm_manager.py
│       └── providers/
├── frontend/
│   ├── index.html
│   └── chat.js
└── requirements.txt
```

### Backend (FastAPI)

```python
# backend/main.py

from fastapi import FastAPI, WebSocket
from llm_core.llm_manager import LLMManager
from llm_core.providers.openai_provider import OpenAIProvider
from llm_core.providers.types import ProviderConfig, Message, Role
import os

app = FastAPI()

# Globaler LLMManager
llm_manager = LLMManager()

@app.on_event("startup")
async def setup_providers():
    # OpenAI
    openai_config = ProviderConfig(
        name="OpenAI",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    openai_provider = OpenAIProvider(openai_config)
    await openai_provider.initialize()
    llm_manager.register_provider("openai", openai_provider)
    
    llm_manager.active_provider_id = "openai"
    llm_manager.active_model_id = "gpt-4"

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        # Empfange User-Message
        data = await websocket.receive_json()
        user_msg = Message(role=Role.USER, content=data['message'])
        
        # Streaming-Response
        async for chunk in llm_manager.stream_chat([user_msg]):
            await websocket.send_json({"chunk": chunk})
        
        # End-Marker
        await websocket.send_json({"done": True})
```

### Frontend (JavaScript)

```javascript
// frontend/chat.js

const ws = new WebSocket('ws://localhost:8000/ws/chat');
const chatDiv = document.getElementById('chat');
const input = document.getElementById('input');

function sendMessage() {
    const message = input.value;
    
    // User-Message anzeigen
    chatDiv.innerHTML += `<div class="user">${message}</div>`;
    
    // An Backend senden
    ws.send(JSON.stringify({message: message}));
    
    // AI-Response (leerer Container)
    const aiDiv = document.createElement('div');
    aiDiv.className = 'ai';
    chatDiv.appendChild(aiDiv);
    
    input.value = '';
}

// Empfange Streaming-Chunks
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.chunk) {
        // Akkumuliere chunks in letztem AI-Div
        const aiDivs = document.querySelectorAll('.ai');
        const lastAi = aiDivs[aiDivs.length - 1];
        lastAi.textContent += data.chunk;
    }
    
    if (data.done) {
        console.log('Response complete');
    }
};
```

**Das war's!** Du hast die Core-Logic wiederverwendet, aber deine eigene UI gebaut.

---

## 🤖 Szenario 3: Discord-Bot

**Use Case:** Discord-Bot mit Multi-Provider-Support

```python
# discord_bot.py

import discord
from discord.ext import commands
from llm_core.llm_manager import LLMManager
from llm_core.providers.openai_provider import OpenAIProvider
from llm_core.providers.anthropic_provider import AnthropicProvider
from llm_core.providers.types import ProviderConfig, Message, Role

bot = commands.Bot(command_prefix='!')
llm_manager = LLMManager()

@bot.event
async def on_ready():
    # Setup Provider
    openai = OpenAIProvider(ProviderConfig(name="OpenAI"))
    await openai.initialize()
    llm_manager.register_provider("openai", openai)
    
    anthropic = AnthropicProvider(ProviderConfig(name="Anthropic"))
    await anthropic.initialize()
    llm_manager.register_provider("anthropic", anthropic)
    
    llm_manager.active_provider_id = "openai"
    llm_manager.active_model_id = "gpt-4"
    
    print(f'{bot.user} is ready!')

@bot.command(name='chat')
async def chat(ctx, *, message: str):
    """Chat mit KI"""
    
    user_msg = Message(role=Role.USER, content=message)
    
    # Typing-Indicator
    async with ctx.typing():
        response = ""
        async for chunk in llm_manager.stream_chat([user_msg]):
            response += chunk
    
    await ctx.send(response)

@bot.command(name='model')
async def switch_model(ctx, provider: str, model: str):
    """Wechsle Provider/Model: !model openai gpt-4"""
    
    llm_manager.active_provider_id = provider
    llm_manager.active_model_id = model
    
    await ctx.send(f'Switched to {model} on {provider}')

bot.run('YOUR_DISCORD_TOKEN')
```

**Features kostenlos:**
- ✅ Multi-Provider-Support (OpenAI, Claude, etc.)
- ✅ Easy Provider-Wechsel (`!model anthropic claude-3-opus`)
- ✅ Streaming (bot.typing)
- ✅ Erweiterbar (neue Provider einfach hinzufügen)

---

## 🖥️ Szenario 4: CLI-Tool

**Use Case:** Command-Line Chat-Client

```python
# cli_chat.py

import asyncio
from llm_core.llm_manager import LLMManager
from llm_core.providers.openai_provider import OpenAIProvider
from llm_core.providers.types import ProviderConfig, Message, Role

async def main():
    # Setup
    llm_manager = LLMManager()
    
    openai = OpenAIProvider(ProviderConfig(name="OpenAI"))
    await openai.initialize()
    llm_manager.register_provider("openai", openai)
    
    llm_manager.active_provider_id = "openai"
    llm_manager.active_model_id = "gpt-4"
    
    print("Chat started. Type 'exit' to quit.\n")
    
    history = []
    
    while True:
        # User-Input
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        user_msg = Message(role=Role.USER, content=user_input)
        history.append(user_msg)
        
        # AI-Response (streaming)
        print("AI: ", end='', flush=True)
        response_content = ""
        
        async for chunk in llm_manager.stream_chat(history):
            print(chunk, end='', flush=True)
            response_content += chunk
        
        print()  # Newline
        
        # Speichere Response in History
        ai_msg = Message(role=Role.ASSISTANT, content=response_content)
        history.append(ai_msg)

if __name__ == "__main__":
    asyncio.run(main())
```

**Ergebnis:**
```bash
$ python cli_chat.py
Chat started. Type 'exit' to quit.

You: Hello!
AI: Hello! How can I help you today?

You: What's Python?
AI: Python is a high-level programming language...
```

---

## 🔧 Szenario 5: Nur das Pattern (andere Sprache)

**Use Case:** Du programmierst in TypeScript/Java/Go, willst aber das Pattern nutzen.

### Das Pattern (konzeptionell)

**1. Abstract Provider Interface**

```typescript
// TypeScript-Beispiel

interface LLMProvider {
  initialize(): Promise<void>;
  getModels(): Promise<ModelInfo[]>;
  streamChat(modelId: string, messages: Message[]): AsyncGenerator<string>;
  checkHealth(): Promise<boolean>;
}

// Konkrete Implementation
class OpenAIProvider implements LLMProvider {
  async initialize() {
    // OpenAI-Client setup
  }
  
  async getModels() {
    return [
      { id: "gpt-4", name: "GPT-4", provider: "OpenAI" }
    ];
  }
  
  async *streamChat(modelId: string, messages: Message[]) {
    // API-Call zu OpenAI
    for (const chunk of response) {
      yield chunk;
    }
  }
  
  async checkHealth() {
    return true;
  }
}
```

**2. Manager mit Registry**

```typescript
class LLMManager {
  private providers: Map<string, LLMProvider> = new Map();
  private activeProviderId: string | null = null;
  private activeModelId: string | null = null;
  
  registerProvider(id: string, provider: LLMProvider) {
    this.providers.set(id, provider);
    if (!this.activeProviderId) {
      this.activeProviderId = id;
    }
  }
  
  async getAllModels(): Promise<ModelInfo[]> {
    const allModels: ModelInfo[] = [];
    
    for (const [providerId, provider] of this.providers) {
      const models = await provider.getModels();
      models.forEach(m => m.providerId = providerId);
      allModels.push(...models);
    }
    
    return allModels;
  }
  
  async *streamChat(messages: Message[]): AsyncGenerator<string> {
    const provider = this.providers.get(this.activeProviderId!);
    if (!provider) throw new Error("No active provider");
    
    yield* provider.streamChat(this.activeModelId!, messages);
  }
}
```

**3. Nutzung**

```typescript
// Setup
const manager = new LLMManager();

const openai = new OpenAIProvider({ apiKey: process.env.OPENAI_API_KEY });
await openai.initialize();
manager.registerProvider("openai", openai);

// Chat
for await (const chunk of manager.streamChat(messages)) {
  console.log(chunk);
}
```

**Das Pattern funktioniert in JEDER Sprache!**

---

## 🎨 Pattern-Prinzipien (universell)

### 1. **Dependency Injection**

**Statt:**
```python
# Schlecht - Hardcoded
class ChatApp:
    def __init__(self):
        self.openai_client = OpenAI(...)  # Fest verdrahtet!
```

**Besser:**
```python
# Gut - Injiziert
class ChatApp:
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager  # Flexibel!
```

**Vorteil:** Tests, Mocks, Provider-Wechsel einfach.

---

### 2. **Plugin-Registry**

**Pattern:**
```
Manager
  └─ Registry (Dict/Map)
      ├─ "openai" → OpenAIProvider
      ├─ "anthropic" → AnthropicProvider
      └─ "custom" → CustomProvider
```

**Vorteile:**
- Neue Plugins zur Laufzeit hinzufügen
- Kein Recompile nötig
- Plugins isoliert

---

### 3. **Strategy Pattern**

Verschiedene Algorithmen (Provider) austauschbar:

```python
# Gleicher Code für alle Provider
async for chunk in manager.stream_chat(messages):
    # Funktioniert mit OpenAI, Anthropic, etc.
    print(chunk)
```

**Kein if/else basierend auf Provider-Typ!**

---

### 4. **Adapter Pattern**

Verschiedene APIs → Einheitliches Interface:

```
OpenAI API (Struktur A) ──→ ┐
                            ├─→ BaseLLMProvider (einheitlich)
Anthropic API (Struktur B) ─→ ┘
```

**Vorteil:** Client-Code muss nur 1 Interface kennen.

---

## 📚 Code-Extraktion: Was brauchst du?

### Minimal (nur Provider-Logik)

```bash
# Kopiere diese Dateien:
core/providers/
├── base_provider.py      # Must-have
├── types.py              # Must-have
├── openai_provider.py    # Optional (nur wenn du OpenAI nutzt)
└── anthropic_provider.py # Optional (nur wenn du Claude nutzt)

core/llm_manager.py       # Must-have
```

**Dependencies:**
```txt
pydantic>=2.0.0
httpx>=0.27.0
openai>=1.0.0  # Falls OpenAI
anthropic>=0.18.0  # Falls Anthropic
```

---

### Mit Anpassungen

Wenn du z.B. **keine Pydantic** nutzen willst:

**Ersetze `types.py`:**

```python
# Statt Pydantic BaseModel
from dataclasses import dataclass
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class Message:
    role: Role
    content: str

@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
```

**Funktioniert genauso!**

---

## 🚀 Best Practices

### 1. **Behalte die Abstraktion**

Auch wenn du nur 1 Provider nutzt:

```python
# Schlecht (direkt OpenAI nutzen)
client = OpenAI(...)
response = client.chat.completions.create(...)

# Besser (über Manager)
llm_manager.register_provider("openai", OpenAIProvider(...))
response = await llm_manager.stream_chat(...)
```

**Warum:** Später hinzufügen von Providern ist trivial.

---

### 2. **Trenne UI von Logic**

```
UI-Layer (Flet/Web/CLI/Discord)
    ↓ (nutzt)
Core-Layer (LLMManager, Provider)
    ↓ (nutzt)
External APIs (OpenAI, Anthropic, etc.)
```

**Vorteil:** UI austauschen ohne Logic zu ändern.

---

### 3. **Async/Await konsequent**

```python
# Schlecht (blockierend)
def chat(message):
    response = requests.post(...)  # Blockiert UI!
    return response

# Besser (async)
async def chat(message):
    response = await httpx.post(...)  # Non-blocking
    return response
```

---

### 4. **Error-Handling pro Provider**

```python
async def stream_chat(self, model_id, messages):
    try:
        async for chunk in self.client.stream(...):
            yield chunk
    except ProviderAPIError as e:
        # Provider-spezifischer Fehler
        yield f"Error: {e}"
    except Exception as e:
        # Fallback
        yield f"Unexpected error: {e}"
```

**Vorteil:** Ein Provider-Fehler bringt nicht die ganze App zum Absturz.

---

## 🎯 Zusammenfassung

### Was du mitnehmen kannst:

✅ **Code (Python):**
- `core/` komplett kopieren
- In eigene App integrieren (Web, CLI, Bot, ...)

✅ **Patterns (universal):**
- Plugin-System
- Abstract Base Class / Interface
- Dependency Injection
- Strategy & Adapter Pattern

✅ **Konzepte:**
- Separation of Concerns
- Async-First
- Error-Resilience

---

### Typische Use-Cases:

| Deine App | Was übernehmen? | Aufwand |
|-----------|-----------------|---------|
| **FastAPI Web-App** | Core-Logic 1:1 | 30 Min |
| **Discord-Bot** | Core-Logic 1:1 | 20 Min |
| **CLI-Tool** | Core-Logic 1:1 | 15 Min |
| **Eigenes UI-Framework** | Core-Logic, eigene UI | 1-2 Std |
| **Andere Sprache** | Pattern/Konzepte | 3-5 Std |
| **Microservice** | LLMManager als Service | 2-3 Std |

---

## 📖 Weiterführend

- **Architektur verstehen**: [06-architecture.md](./06-architecture.md)
- **Provider erstellen**: [03-provider-integration.md](./03-provider-integration.md)
- **Pattern-Theorie**: [00-why-this-app.md](./00-why-this-app.md)

---

**Fragen?** → [GitHub Discussions](https://github.com/your-repo/discussions)

**Du hast ein cooles Projekt mit diesem Pattern gebaut?** → Zeig es uns! 🚀
