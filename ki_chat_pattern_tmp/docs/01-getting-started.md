# Schnellstart-Anleitung

Willkommen bei **KI Chat Pattern**! Diese Anleitung bringt dich in wenigen Minuten zum Laufen.

## 📋 Voraussetzungen

Bevor du startest, stelle sicher, dass du Folgendes installiert hast:

- **Python 3.10 oder höher** ([Download](https://www.python.org/downloads/))
- **pip** (normalerweise mit Python installiert)
- Einen Code-Editor (optional, z.B. VS Code)

## 🔧 Installation

### Schritt 1: Repository klonen oder herunterladen

```bash
# Mit Git
git clone https://github.com/your-repo/ki_chat_pattern.git
cd ki_chat_pattern

# Oder: Lade das ZIP herunter und entpacke es
```

### Schritt 2: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**Was wird installiert?**
- `flet` - Moderne UI-Framework
- `pydantic` - Datenvalidierung
- `httpx` - HTTP-Client für API-Aufrufe
- `openai` - OpenAI API-Client
- `anthropic` - Anthropic API-Client
- `python-dotenv` - Umgebungsvariablen-Management

### Schritt 3: Umgebungskonfiguration erstellen

```bash
cp .env.example .env
```

Öffne die `.env`-Datei. Du siehst dort alle Einträge **auskommentiert** (mit `#` davor):

```bash
# .env
# OPENAI_API_KEY=sk-proj-DEIN-KEY-HIER-EINFUEGEN
# ANTHROPIC_API_KEY=sk-ant-DEIN-KEY-HIER-EINFUEGEN
```

👉 **Nimm nur EINEN Eintrag, den du besitzt:**
1.  Entferne das `#` am Anfang der Zeile (Einkommentieren).
2.  Ersetze den Platzhalter mit deinem echten Key.
3.  Lasse die anderen Zeilen mit `#` stehen ("Ignoriert").

Beispiel (wenn du nur OpenAI hast):
```bash
OPENAI_API_KEY=sk-proj-123456789abcdef...
# ANTHROPIC_API_KEY=... (bleibt inaktiv)
```

> 💡 **Tipp**: Du kannst die App auch ohne echte API-Keys starten! Der Mock-Provider ist standardmäßig aktiviert.

## 🚀 Erste Schritte

### App starten

```bash
python main.py
```

Die App öffnet sich automatisch in einem neuen Fenster!

### Dein erstes Gespräch

1. **Model auswählen**:
   - Links in der Sidebar findest du das Dropdown "Select Model"
   - Wähle ein verfügbares Model aus (z.B. "Mock GPT-4" zum Testen)

2. **Nachricht eingeben**:
   - Gib deine Frage im Textfeld unten ein
   - Drücke `Enter` oder klicke auf den Senden-Button

3. **Antwort empfangen**:
   - Die KI-Antwort erscheint in Echtzeit mit Streaming
   - Markdown-Formatierung wird automatisch gerendert

## 🎯 Wichtige Interface-Elemente

```
┌─────────────────────────────────────────────────┐
│ Sidebar         │ Chat-Bereich                  │
│                 │                               │
│ Model-Auswahl   │ ┌───────────────────────────┐ │
│ [Dropdown]      │ │ User: Hallo!              │ │
│                 │ └───────────────────────────┘ │
│ Chat History    │                               │
│ (kommt)         │ ┌───────────────────────────┐ │
│                 │ │ AI: Hallo! Wie kann ich   │ │
│ [Settings]      │ │     dir helfen?           │ │
│                 │ └───────────────────────────┘ │
│                 │                               │
│                 │ ┌───────────────────────────┐ │
│                 │ │ Eingabefeld...      [🔍][➤]│
│                 │ └───────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## ✅ Funktions-Check

Nach dem Start sollte Folgendes funktionieren:

- ✅ App startet ohne Fehler
- ✅ Mock-Provider ist verfügbar (z.B. "Mock GPT-4")
- ✅ Nachrichten werden gesendet
- ✅ Antworten erscheinen in Echtzeit
- ✅ Markdown wird korrekt angezeigt

## 🤔 Probleme beim Start?

### "ModuleNotFoundError"
```bash
# Lösung: Abhängigkeiten neu installieren
pip install -r requirements.txt --upgrade
```

### "API Key not found" Warnung
Das ist normal! Ohne echte API-Keys läuft die App mit dem Mock-Provider.

Um echte Anbieter zu nutzen:
→ Siehe [Provider-Integration](./03-provider-integration.md)

### App startet nicht
```bash
# Python-Version prüfen
python --version  # Sollte 3.10+ sein

# Alternativer Start
python3 main.py
```

## 🎓 Nächste Schritte

Jetzt wo die App läuft, empfehlen wir:

1. **Echte Provider hinzufügen**: [Provider-Integration Guide](./03-provider-integration.md)
2. **Features erkunden**: [Feature-Übersicht](./02-features.md)
3. **App konfigurieren**: [Konfiguration](./04-configuration.md)

---

**Glückwunsch! 🎉** Du hast KI Chat Pattern erfolgreich gestartet.

Bei Fragen: [Troubleshooting](./05-troubleshooting.md) oder [Community-Forum](https://github.com/your-repo/discussions)
