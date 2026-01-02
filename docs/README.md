# Y.A.T. - Dokumentation

Willkommen zur umfassenden Dokumentation für **Y.A.T.** – Ihrer professionellen, erweiterbaren AI-Chat-Anwendung.

> **⚠️ IMPORTANT NOTE FOR v2.0+**
> Y.A.T. now features an **Auto-Discovery Plugin System**.
> Old documentation references asking you to edit `main.py` to register providers are **obsolete**.
> To add a provider, simply drop a plugin file (e.g. `my_provider.py`) into the `plugins/` directory. **Do not edit `main.py`!**

## 📚 Dokumentationsübersicht

Diese Dokumentation ist in mehrere Bereiche unterteilt, um dir den Einstieg und die Nutzung so einfach wie möglich zu machen:

> **🔍 Tipp: Interaktive Suche**
> Du kannst die komplette Doku durchsuchen!
> ```bash
> python tools/search_docs.py
> ```

### 0. [⚡ Quick Start: Von Key bis Chat in 2 Minuten](./00-quick-start.md) 🔥
**START HIER!** - Du hast einen API-Key? Wähle dein Szenario und chatte in 2 Minuten!
- OpenAI? → 2 Minuten
- Anthropic/Claude? → 2 Minuten  
- Google Gemini? → 5 Minuten
- Kein Key? Mock-Provider → 30 Sekunden
- Lokal/Ollama? → 10 Minuten

### 0. [Warum Y.A.T.?](./00-why-this-app.md) 💡
**Lies das zuerst!** - Was ist das hier? Fertiges Produkt oder Template? Was bedeutet "erweiterbar"?
- Vollständige App vs. Pattern-Gerüst
- Vergleich mit Alternativen
- Erweiterbarkeit praktisch erklärt
- Anwendungsfälle & Vorteile

### 1. [Schnellstart-Anleitung](./01-getting-started.md)
**Für neue Nutzer** - Installiere die App und führe deinen ersten Chat in wenigen Minuten durch.
- Installation & Setup
- Erste Schritte
- Dein erstes Gespräch mit der KI

### 2. [Feature-Übersicht](./02-features.md)
**Lerne die Funktionen kennen** - Entdecke alle Möglichkeiten der Anwendung.
- Chat-Interface
- Model-Auswahl
- Markdown-Rendering
- Streaming-Antworten
- Datenschutz & Sicherheit

### 3. [Provider-Integration (Praxis)](./03-provider-integration.md) ⭐
**Der wichtigste Guide** - Verbinde deine Lieblings-AI-Services.
- OpenAI (ChatGPT) einrichten
- Anthropic (Claude) einrichten
- Google Gemini hinzufügen
- Ollama (lokale Models) nutzen
- Eigene Provider erstellen

### 4. [Konfiguration](./04-configuration.md)
**Personalisiere deine App** - Passe die Anwendung an deine Bedürfnisse an.
- API-Keys verwalten
- Provider aktivieren/deaktivieren
- Theme & UI-Anpassungen
- Erweiterte Einstellungen

### 5. [Fehlerbehandlung & FAQ](./05-troubleshooting.md)
**Probleme lösen** - Finde schnell Lösungen für häufige Probleme.
- API-Key-Fehler
- Verbindungsprobleme
- Provider-Fehler
- Performance-Optimierung

### 6. [Architektur & Entwicklung](./06-architecture.md)
**Für Entwickler** - Verstehe den technischen Aufbau und erweitere die App.
- System-Architektur
- Code-Struktur
- Neue Features entwickeln
- Best Practices

### 7. [Patterns für eigene Apps nutzen](./07-using-patterns.md) 🔥
**Für Entwickler** - Nutze diese Patterns in DEINEN Projekten!
- Core-Logik standalone verwenden
- Pattern-Extraktion (Web-App, Discord-Bot, CLI)
- Code-Beispiele für FastAPI, Discord.py, etc.
- Pattern-Konzepte in anderen Sprachen (TypeScript, Java, Go)

---

## 🚀 Wo solltest du anfangen?

- **Neu hier & hast API-Key?** → Starte mit [⚡ Quick Start](./00-quick-start.md) (2 Minuten!)
- **Was ist das hier?** → Lies [Warum Y.A.T.?](./00-why-this-app.md)
- **Verstehen wie's funktioniert?** → [Schnellstart-Anleitung](./01-getting-started.md)
- **Provider hinzufügen?** → Gehe direkt zur [Provider-Integration](./03-provider-integration.md)
- **Problem?** → Schau in die [Fehlerbehandlung](./05-troubleshooting.md)
- **Entwickler?** → Lies die [Architektur-Dokumentation](./06-architecture.md)

---

## 💡 Schnelle Links

| Aufgabe | Dokument | Abschnitt |
|---------|----------|-----------|
| App installieren | [Getting Started](./01-getting-started.md) | Installation |
| OpenAI einrichten | [Provider Integration](./03-provider-integration.md) | OpenAI Setup |
| Claude nutzen | [Provider Integration](./03-provider-integration.md) | Anthropic Setup |
| Lokale Models | [Provider Integration](./03-provider-integration.md) | Ollama Setup |
| API-Keys sichern | [Konfiguration](./04-configuration.md) | Sicherheit |
| Fehler beheben | [Troubleshooting](./05-troubleshooting.md) | Alle Abschnitte |
| Patterns nutzen | [Patterns für eigene Apps](./07-using-patterns.md) | Alle Szenarien |

---

## ❓ Häufig gestellte Fragen (FAQ)

### "Ist das eine fertige App oder nur ein Template?"

**Eine vollständig funktionierende Anwendung!** 

- ✅ Startet sofort mit `python main.py`
- ✅ Alle Provider funktionieren (mit API-Keys)
- ✅ GUI ist komplett, kein Placeholder
- ✅ Production-ready für viele Use-Cases

**Gleichzeitig:** Professionelle Architektur, die leicht erweiterbar ist.

→ Mehr Details: [Warum Y.A.T.?](./00-why-this-app.md)

### "Was bedeutet 'erweiterbar'?"

**Du kannst neue Features hinzufügen, OHNE bestehenden Code zu ändern.**

Beispiele:
- Neuer Provider (z.B. Cohere): **10 Minuten**, 0 Zeilen geändert
- Chat-Export-Feature: **15 Minuten**, ~2 Zeilen geändert
- Web-Suche Integration: **30 Minuten**, optional für Provider

→ Praktische Erklärung: [00-why-this-app.md](./00-why-this-app.md#-was-bedeutet-erweiterbar-praktisch-erklärt)

### "Brauche ich API-Keys?"

**Nein, zum Testen nicht!**

- Mock-Provider funktioniert ohne Keys
- Ollama (lokal) braucht keine API-Keys

**Ja, für echte LLMs:**
- OpenAI: [API-Key besorgen](./03-provider-integration.md#openai-api-key)
- Anthropic: [API-Key besorgen](./03-provider-integration.md#anthropic-api-key)

### "Kann ich lokale Modelle nutzen?"

**Ja! Mit Ollama.**

→ Vollständige Anleitung: [Ollama Setup](./03-provider-integration.md#-schritt-für-schritt-ollama-lokale-modelle)

- 100% offline
- 100% privat
- Kostenlos

### "Welche Provider werden unterstützt?"

**Aktuell fertig implementiert:**
- ✅ OpenAI (GPT-4, GPT-3.5, etc.)
- ✅ Anthropic (Claude 3 Familie)
- ✅ Mock (zum Testen)

**Code-Beispiele vorhanden:**
- ⚠️ Google Gemini
- ⚠️ Ollama (Community)

**Einfach selbst hinzuzufügen:**
- Cohere, Hugging Face, Mistral, Azure OpenAI, AWS Bedrock, Groq, ...

→ Anleitung: [Eigenen Provider erstellen](./03-provider-integration.md#-eigenen-provider-erstellen)

### "Funktioniert das auf Windows/Linux?"

**Ja!** Python & Flet sind plattformübergreifend.

- ✅ macOS
- ✅ Windows
- ✅ Linux

Kleine Unterschiede bei Umgebungsvariablen (siehe [Getting Started](./01-getting-started.md)).

### "Wie sicher sind meine API-Keys?"

**Sicher, wenn richtig konfiguriert:**

- ✅ Keys in `.env` (lokal, nicht in Git)
- ✅ `.env` bereits in `.gitignore`
- ✅ Keine Telemetrie, keine Cloud-Speicherung

→ Details: [Sicherheit](./04-configuration.md#-sicherheit--privacy)

### "Kostet die Nutzung Geld?"

**Depends:**

- Mock-Provider: **Kostenlos**
- Ollama (lokal): **Kostenlos**
- OpenAI/Anthropic: **Pay-per-use**

Kosten-Beispiel:
- 1000 Nachrichten mit GPT-3.5: ~$1-2
- 1000 Nachrichten mit GPT-4: ~$30-60

→ Mehr: [FAQ in Features](./02-features.md#-faq)

---

## 📞 Support & Community

- **GitHub Issues**: [Probleme melden](https://github.com/your-repo/issues)
- **Diskussionen**: [Community-Forum](https://github.com/your-repo/discussions)
- **Updates**: Prüfe regelmäßig auf neue Provider und Features

---

**Viel Erfolg mit Y.A.T.!** 🎉
