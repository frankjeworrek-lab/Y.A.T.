# Architektur & Entwicklung

Technische Dokumentation für Entwickler, die **KI Chat Pattern** verstehen oder erweitern möchten.

## 🏗️ System-Architektur

### High-Level Overview

```
┌─────────────────────────────────────────────────────┐
│                   UI Layer (Flet)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Sidebar  │  │ChatView  │  │  InputArea       │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                      │                              │
│              ┌───────▼────────┐                     │
│              │  AppLayout     │                     │
│              └───────┬────────┘                     │
└──────────────────────┼──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Core Logic Layer                       │
│              ┌─────────────┐                        │
│              │ LLMManager  │                        │
│              └──────┬──────┘                        │
│                     │                               │
│     ┌───────────────┼───────────────┐               │
│     ▼               ▼               ▼               │
│  ┌────────┐   ┌─────────┐    ┌──────────┐          │
│  │OpenAI  │   │Anthropic│    │  Mock    │          │
│  │Provider│   │Provider │    │ Provider │          │
│  └────────┘   └─────────┘    └──────────┘          │
│       │             │              │                │
└───────┼─────────────┼──────────────┼────────────────┘
        │             │              │
┌───────▼─────────────▼──────────────▼────────────────┐
│              External APIs                          │
│    OpenAI API   Anthropic API    Mock Responses    │
└─────────────────────────────────────────────────────┘
```

### Design-Prinzipien

1. **Separation of Concerns**
   - UI weiß nichts über API-Details
   - Provider-Logic isoliert vom Core
   - Core-Logic UI-agnostisch

2. **Async-First**
   - Alle I/O-Operationen sind async
   - Keine UI-Blockierung
   - Streaming ermöglicht Echtzeit-Updates

3. **Plugin-Architektur**
   - Provider als austauschbare Plugins
   - Neue Provider ohne Core-Änderungen
   - Dependency Injection Pattern

4. **Type-Safety**
   - Pydantic für Datenvalidierung
   - Type Hints überall
   - IDE-Support & Auto-Completion

---

## 📁 Code-Struktur

```
ki_chat_pattern/
├── main.py                      # Einstiegspunkt, App-Initialisierung
├── requirements.txt             # Python-Dependencies
├── .env.example                 # Umgebungsvariablen-Template
├── .env                         # Echte Keys (gitignored)
│
├── core/                        # Business Logic
│   ├── llm_manager.py          # Provider-Management
│   └── providers/               # Provider-Implementierungen
│
├── ui/                          # User Interface (Flet)
│   ├── app_layout.py           # Main Layout & Orchestration
│   ├── sidebar.py              # Model-Selection, Settings
│   ├── chat_view.py            # Message Display
│   └── input_area.py           # User Input
│
├── storage/                     # Persistence Layer
│   ├── __init__.py
│   └── chat_db.py              # SQLite Database Logic
│
│       ├── types.py            # Shared Types (Pydantic)
│       ├── base_provider.py    # Abstract Base Class
│       ├── mock_provider.py    # Test-Provider
│       ├── openai_provider.py  # OpenAI Integration
│       ├── anthropic_provider.py # Anthropic Integration
│       └── gemini_provider.py  # Google Gemini (Example)
│
├── ui/                          # User Interface (Flet)
│   ├── app_layout.py           # Main Layout & Orchestration
│   ├── sidebar.py              # Model-Selection, Settings
│   ├── chat_view.py            # Message Display
│   └── input_area.py           # User Input
│
├── config/                      # (Future) Config Management
├── assets/                      # (Future) Images, Icons
└── docs/                        # Dokumentation
    ├── README.md               # Übersicht
    ├── 01-getting-started.md
    ├── 02-features.md
    ├── 03-provider-integration.md
    ├── 04-configuration.md
    ├── 05-troubleshooting.md
    └── 06-architecture.md      # This file
```

---

## 🔧 Core-Komponenten

### 1. LLMManager

**Zweck:** Zentrale Verwaltung aller LLM-Provider

**Verantwortlichkeiten:**
- Provider registrieren/verwalten
- Model-Listen aggregieren
- Aktiven Provider/Model tracken
- Stream-Aufrufe orchestrieren

**API:**
```python
class LLMManager:
    def register_provider(provider_id: str, provider: BaseLLMProvider)
    async def get_all_models() -> List[ModelInfo]
    async def stream_chat(messages: List[Message], ...) -> AsyncGenerator[str]
```

**Beispiel-Flow:**
```python
# 1. Provider registrieren
manager = LLMManager()
manager.register_provider("openai", OpenAIProvider(config))

# 2. Models abfragen
models = await manager.get_all_models()  # Aggregiert von allen Providern

# 3. Chat-Stream
async for chunk in manager.stream_chat(message_history):
    print(chunk)  # Echtzeit-Ausgabe
```

---

### 2. BaseLLMProvider (ABC)

**Zweck:** Contract für alle Provider-Implementierungen

**Interface:**
```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def initialize() -> None
        """Setup: API-Client initialisieren, Keys validieren"""
    
    @abstractmethod
    async def get_models() -> List[ModelInfo]
        """Model-Discovery: Welche Modelle sind verfügbar?"""
    
    @abstractmethod
    async def stream_chat(...) -> AsyncGenerator[str, None]
        """Streaming: Sende Messages, empfange Chunks"""
    
    @abstractmethod
    async def check_health() -> bool
        """Health-Check: Ist Service erreichbar?"""
```

**Implementierungs-Beispiel:**
```python
class CustomProvider(BaseLLMProvider):
    async def initialize(self) -> None:
        self.client = CustomAPI(api_key=self.config.api_key)
    
    async def get_models(self) -> List[ModelInfo]:
        return [ModelInfo(id="custom-1", name="Custom Model", ...)]
    
    async def stream_chat(self, model_id, messages, **kwargs):
        for word in "Hello from custom provider".split():
            await asyncio.sleep(0.1)  # Simulate delay
            yield word + " "
    
    async def check_health(self) -> bool:
        return self.client is not None
```

---

### 3. Pydantic Models (types.py)

**Zweck:** Type-Safety und Datenvalidierung

**Models:**

```python
class Role(str, Enum):
    """Message role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    """Single chat message"""
    role: Role
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ModelInfo(BaseModel):
    """Model metadata"""
    id: str
    name: str
    provider: str
    capabilities: List[ModelCapability] = [ModelCapability.CHAT]
    context_window: Optional[int] = None
    max_tokens: Optional[int] = None
    provider_id: Optional[str] = None  # Injected by LLMManager

class ProviderConfig(BaseModel):
    """Provider configuration"""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    enabled: bool = True
```

**Vorteile:**
- Auto-Validation (z.B. role muss USER|ASSISTANT|SYSTEM sein)
- IDE-Autocomplete
- JSON-Serialisierung out-of-the-box
- Dokumentation durch Types

---

### 4. Persistence Layer (storage/chat_db.py)

**Zweck:** Dauerhafte Speicherung von Chats und Messages

**Technologie:** `sqlite3` (Built-in, keine Extra-Dependency)

**Datenbank-Schema:**
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    updated_at TEXT,
    ...
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id TEXT,
    role TEXT,
    content TEXT,
    timestamp TEXT,
    metadata TEXT
);
```

**Interface:**
```python
class ChatDatabase:
    def create_conversation(self, ...) -> str
    def save_message(self, conversation_id, message: Message)
    def load_messages(self, conversation_id) -> List[Message]
    def get_conversations(self, limit=50) -> List[Dict]
```

---

## 🎨 UI-Architektur

### Component-Hierarchie

```
AppLayout (ft.Row)
│
├─ Sidebar (ft.Container)
│  ├─ ft.Text("KI Chat")
│  ├─ ft.Dropdown (Model Selection)
│  └─ ft.ElevatedButton (Settings)
│
├─ ft.VerticalDivider
│
└─ Main Content (ft.Container)
   ├─ ChatView (ft.Container)
   │  └─ ft.ListView (Messages)
   │     ├─ ft.Row (Message 1)
   │     ├─ ft.Row (Message 2)
   │     └─ ...
   │
   └─ InputArea (ft.Container)
      └─ ft.Row
         ├─ ft.TextField
         └─ ft.IconButton (Send)
```

### State Management

**Aktuell:** Component-lokaler State

```python
class AppLayout:
    def __init__(self, page, llm_manager):
        self.main_page = page
        self.llm_manager = llm_manager
        self.message_history: List[Message] = []  # App State
```

**Zukünftig:** Evtl. zentraler State-Manager (Redux-Style)

---

## 🔄 Datenfluss

### Message-Send-Flow

```
User tippt Nachricht → Enter/Send-Button
    ↓
InputArea.handle_submit()
    ↓
AppLayout.handle_input_submit()
    ↓
AppLayout.run_chat_flow() [async]
    ↓
├─ User-Message zu History hinzufügen
├─ ChatView.add_message(user_msg)
├─ Placeholder-AI-Message erstellen
├─ ChatView.add_message(assistant_msg)
    ↓
LLMManager.stream_chat(history)
    ↓
Provider.stream_chat(model_id, messages)
    ↓
[Streaming-Loop]
    ├─ Chunk empfangen
    ├─ ChatView.update_last_message(accumulated_content)
    └─ Repeat
    ↓
Final: assistant_msg.content = full_response
```

### Async-Pattern

**Wichtig:** UI-Callbacks (wie `on_submit`) können nicht direkt async sein.

**Lösung:** `asyncio.create_task()`

```python
def handle_input_submit(self, text):
    # Synchroner Callback
    asyncio.create_task(self.run_chat_flow(text))  # Async Task starten

async def run_chat_flow(self, text):
    # Async-Logic hier
    async for chunk in self.llm_manager.stream_chat(...):
        self.chat_view.update_last_message(...)
```

---

## 🛠️ Entwicklungs-Workflows

### Neuen Provider hinzufügen

**Schritt 1:** Provider-Klasse erstellen
```bash
touch core/providers/my_provider.py
```

**Schritt 2:** BaseLLMProvider implementieren
```python
from .base_provider import BaseLLMProvider

class MyProvider(BaseLLMProvider):
    # Implementiere alle abstract methods
    pass
```

**Schritt 3:** In `main.py` registrieren
```python
from core.providers.my_provider import MyProvider

my_config = ProviderConfig(name="My Service")
my_provider = MyProvider(my_config)
await my_provider.initialize()
llm_manager.register_provider("my_provider", my_provider)
```

**Fertig!** Model erscheint im Dropdown.

---

### Neues UI-Feature hinzufügen

**Beispiel:** "Clear Chat" Button

**Schritt 1:** UI-Element in Sidebar
```python
# ui/sidebar.py

clear_button = ft.ElevatedButton(
    "Clear Chat",
    on_click=self.handle_clear_chat
)

# In Column.controls hinzufügen
```

**Schritt 2:** Callback implementieren
```python
# ui/sidebar.py

def handle_clear_chat(self, e):
    # Callback zu AppLayout
    if self.on_clear_chat:
        self.on_clear_chat()
```

**Schritt 3:** Logic in AppLayout
```python
# ui/app_layout.py

self.sidebar = Sidebar(llm_manager, on_clear_chat=self.handle_clear_chat)

def handle_clear_chat(self):
    self.message_history.clear()
    self.chat_view.clear()
```

---

### Testing

**Aktuell:** Keine automatischen Tests

**Geplant:**
```python
# tests/test_providers.py

import pytest
from core.providers.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_mock_provider_streaming():
    provider = MockProvider(ProviderConfig(name="Test"))
    await provider.initialize()
    
    messages = [Message(role=Role.USER, content="Hello")]
    chunks = []
    
    async for chunk in provider.stream_chat("mock-gpt-4", messages):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    assert "mocked response" in "".join(chunks)
```

**Test-Setup:**
```bash
pip install pytest pytest-asyncio
pytest tests/
```

---

## 📦 Dependencies

### Production

| Package | Version | Zweck |
|---------|---------|-------|
| `flet` | >=0.21.0 | UI Framework |
| `pydantic` | >=2.0.0 | Data Validation |
| `httpx` | >=0.27.0 | Async HTTP Client |
| `python-dotenv` | >=1.0.0 | .env Loading |
| `openai` | >=1.0.0 | OpenAI SDK |
| `anthropic` | >=0.18.0 | Anthropic SDK |

### Optional

| Package | Zweck |
|---------|-------|
| `google-generativeai` | Gemini Support |
| `pytest` | Testing |
| `black` | Code Formatting |
| `mypy` | Type Checking |

---

## 🚀 Performance-Optimierungen

### Lazy Loading

Provider nur laden, wenn Keys vorhanden:
```python
if os.getenv("OPENAI_API_KEY"):
    from core.providers.openai_provider import OpenAIProvider
    # ...
```

### Caching

Model-Listen cachen (1 API-Call statt N):
```python
class LLMManager:
    def __init__(self):
        self._model_cache: Optional[List[ModelInfo]] = None
        self._cache_time: Optional[datetime] = None
    
    async def get_all_models(self):
        if self._model_cache and (datetime.now() - self._cache_time).seconds < 300:
            return self._model_cache  # Cache hit
        
        # Cache miss: Fresh fetch
        self._model_cache = await self._fetch_models()
        self._cache_time = datetime.now()
        return self._model_cache
```

### UI-Update-Batching

Nicht jedes Chunk einzeln rendern:
```python
buffer = ""
for i, chunk in enumerate(chunks):
    buffer += chunk
    if i % 10 == 0:  # Alle 10 chunks
        self.chat_view.update_last_message(buffer)
```

---

## 🔐 Sicherheits-Überlegungen

### API-Key-Handling

**DO:**
- ✅ Keys in `.env` speichern
- ✅ `.env` in `.gitignore`
- ✅ `os.getenv()` verwenden
- ✅ Keys verschlüsselt speichern (zukünftig)

**DON'T:**
- ❌ Keys in Code hardcoden
- ❌ Keys in Logs ausgeben
- ❌ Keys in Exception-Messages

### Input-Validation

Pydantic validiert automatisch:
```python
# Wirft ValidationError bei falschem Type
msg = Message(role="invalid", content="...")  # ❌ Fehler

msg = Message(role=Role.USER, content="...")  # ✅ OK
```

### Rate-Limiting

**Aktuell:** Nicht implementiert

**Zukünftig:**
```python
from ratelimit import limits

@limits(calls=10, period=60)  # 10 calls/minute
async def stream_chat(...):
    pass
```

---

## 🔮 Zukunfts-Features

### Persistente History

```python
# Vorgeschlagen: SQLite
import sqlite3

class HistoryManager:
    def save_conversation(self, messages: List[Message]):
        # Save to DB
        pass
    
    def load_conversation(self, conversation_id: str):
        # Load from DB
        pass
```

### Multi-Turn-Context

Automatisches Context-Window Management:
```python
def trim_history(messages, max_tokens=4000):
    """Keep only recent messages that fit in context"""
    # Token counting logic
    pass
```

### Plugin-System

```python
# plugins/sentiment_analysis.py
class SentimentPlugin(BasePlugin):
    def before_send(self, message):
        # Analyze vor dem Senden
        pass
    
    def after_receive(self, response):
        # Process Antwort
        pass
```

---

## 📚 Weitere Ressourcen

- **Getting Started**: [Installation & Setup](./01-getting-started.md)
- **Provider Guide**: [Provider hinzufügen](./03-provider-integration.md)
- **Troubleshooting**: [Häufige Probleme](./05-troubleshooting.md)

---

## 🤝 Contribution-Guidelines

**Interessiert mitzuarbeiten?**

1. **Fork** das Repo
2. **Branch** erstellen: `git checkout -b feature/my-feature`
3. **Code** schreiben (mit Type-Hints!)
4. **Tests** hinzufügen (wenn relevant)
5. **Commit**: `git commit -m "Add: My Feature"`
6. **Push**: `git push origin feature/my-feature`
7. **Pull Request** erstellen

**Code-Style:**
- Black für Formatting
- Type-Hints überall
- Docstrings für Public APIs

---

**Happy Coding!** 🚀
