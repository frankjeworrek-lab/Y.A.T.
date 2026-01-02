# KI Chat Pattern

A professional, extensible AI Chat application built with Python and Flet.

## Features
- **Extensible Provider System**: Easy to add new LLM providers (OpenAI, Anthropic, Ollama, etc.).
- **Modern UI**: Dark mode, responsive layout, Markdown rendering with code highlighting.
- **Real-time Streaming**: Smooth text streaming from providers.
- **Architecture**: Clean MVC-inspired separation of concerns.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configuration:
   - Create a `.env` file in the root directory.
   - Add your API keys:
     ```
     OPENAI_API_KEY=sk-...
     ```

3. Run the application:
   ```bash
   python main.py
   ```

## 📚 Dokumentation

Eine **vollständige, praxisorientierte Dokumentation** findest du im `docs/` Ordner:

→ **[📖 Zur vollständigen Dokumentation](./docs/README.md)**

> **🔍 Tipp: Interaktive Suche**  
> Finde Antworten sofort: `python tools/search_docs.py`

**Schnellzugriff:**
- [Schnellstart-Anleitung](./docs/01-getting-started.md) - Installation & erste Schritte
- [Feature-Übersicht](./docs/02-features.md) - Alle Funktionen erklärt  
- [Provider-Integration](./docs/03-provider-integration.md) ⭐ - OpenAI, Claude, Gemini & mehr anbinden
- [Konfiguration](./docs/04-configuration.md) - App personalisieren
- [Troubleshooting](./docs/05-troubleshooting.md) - Probleme lösen
- [Architektur](./docs/06-architecture.md) - Für Entwickler

## 🎯 Highlights

- ✅ **Multi-Provider**: OpenAI, Anthropic, Google Gemini, Ollama und mehr
- ✅ **Echtzeit-Streaming**: Antworten erscheinen live wie beim Tippen
- ✅ **Markdown-Support**: Code-Highlighting, Tabellen, Listen, etc.
- ✅ **Erweiterbar**: Eigene Provider in Minuten hinzufügen
- ✅ **Modern UI**: Dark Mode, Material Design 3
- ✅ **Generische Architektur**: Professionelles Plugin-System

## Structure
- `main.py`: Application entry point.
- `core/`: Logic and providers.
- `ui/`: Flet UI components.
