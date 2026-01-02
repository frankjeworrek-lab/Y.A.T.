# Fehlerbehandlung & FAQ

Schnelle Lösungen für häufige Probleme bei **KI Chat Pattern**.

## 🔍 Schnelldiagnose

**App startet nicht?** → [Startup-Probleme](#startup-probleme)  
**API-Key-Fehler?** → [API-Key-Probleme](#api-key-probleme)  
**Kein Model verfügbar?** → [Provider-Probleme](#provider-probleme)  
**Verbindungsfehler?** → [Netzwerk-Probleme](#netzwerk-probleme)  
**Langsame Antworten?** → [Performance-Probleme](#performance-probleme)

---

## 🚨 Startup-Probleme

### App startet nicht / Sofortiger Crash

**Symptom:**
```bash
$ python main.py
ModuleNotFoundError: No module named 'flet'
```

**Lösung:**
```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Falls das nicht hilft: Fresh install
pip uninstall -y flet pydantic httpx openai anthropic python-dotenv
pip install -r requirements.txt
```

---

### "Python-Version nicht unterstützt"

**Symptom:**
```bash
SyntaxError: invalid syntax
```

**Lösung:**
```bash
# Python-Version prüfen
python --version

# Muss 3.10+ sein
# Falls älter: Python upgraden oder python3 nutzen
python3 main.py
```

---

### "DeprecationWarning: app() is deprecated"

**Symptom:**
```
DeprecationWarning: app() is deprecated since version 0.70.0
```

**Lösung:**
Das ist nur eine Warnung, die App funktioniert trotzdem. Kann ignoriert werden.

Um sie zu entfernen, öffne `main.py`:
```python
# Zeile 50, ändere:
if __name__ == "__main__":
    ft.app(target=main)  # Alt: Funktioniert, aber deprecated

# Nach neuerer Syntax (falls verfügbar):
if __name__ == "__main__":
    ft.run(app=main)  # Neu: Aber check Flet-Docs für exakte Syntax
```

---

## 🔑 API-Key-Probleme

### ⚠️ "No Key found" in der Sidebar

**Symptom:**
Du siehst ein gelbes Warndreieck unter dem Model-Dropdown:
> ⚠️ **OpenAI: No Key found (Check .env / Docs)**

**Ursache:**
Die App konnte deinen API-Key nicht laden. Oft ist der Eintrag in der `.env`-Datei noch auskommentiert oder fehlt.

**Das ist OK wenn:**
- ✅ Du nur den Mock-Provider nutzen willst
- ✅ Du nur einen Provider nutzt (z.B. nur OpenAI)

**Lösung (falls du echte Provider willst):**

1.  **Öffne die `.env`-Datei.**
2.  **Suche deinen Provider:**
    ```bash
    # OPENAI_API_KEY=sk-...  <-- Das '#' muss weg!
    ```
3.  **Entferne das Raute-Zeichen (#):**
    ```bash
    OPENAI_API_KEY=sk-...    <-- So ist es richtig!
    ```
4.  **Starte die App neu.**
    ```bash
    python main.py
    ```

---

### "Invalid API Key" Fehler

**Symptom:**
```
Error: Invalid authentication credentials
```

**Checkliste:**
- [ ] Key richtig kopiert? (Kein Leerzeichen am Ende)
- [ ] Richtiger Key-Name in `.env`? (`OPENAI_API_KEY` nicht `OPEN_AI_API_KEY`)
- [ ] Key noch aktiv? (Beim Provider prüfen)
- [ ] Guthaben vorhanden? (Bei OpenAI/Anthropic Account prüfen)

**Testen:**
```bash
# Prüfe .env-Datei
cat .env | grep OPENAI

# Sollte ausgeben:
# OPENAI_API_KEY=sk-proj-...
```

---

### Keys werden nicht geladen

**Symptom:**
App startet, aber Provider sagen "Not initialized"

**Lösung:**

**1. Prüfe, ob `.env` existiert:**
```bash
ls -la | grep .env
# Sollte .env anzeigen (nicht nur .env.example)
```

**2. Prüfe Datei-Rechte:**
```bash
chmod 600 .env  # Nur Owner kann lesen/schreiben
```

**3. Prüfe, ob dotenv geladen wird:**

In `main.py`, Zeile ~8:
```python
load_dotenv()  # Muss VOR den Provider-Initialisierungen sein!
```

---

## 🔌 Provider-Probleme

### Kein Model im Dropdown sichtbar

**Symptom:**
Dropdown "Select Model" ist leer

**Checkliste:**
1. **Provider registriert?**
   ```python
   # In main.py: Diese Zeilen müssen existieren
   llm_manager.register_provider("openai", openai_provider)
   ```

2. **Provider enabled?**
   ```python
   openai_config = ProviderConfig(name="OpenAI", enabled=True)  # Muss True sein
   ```

3. **API-Key vorhanden?**
   Provider ohne gültigen Key liefern oft leere Model-Listen.

4. **Internet-Verbindung?**
   ```bash
   # Test
   curl https://api.openai.com/v1/models
   ```

---

### "Provider not initialized"

**Symptom:**
```
Error: Provider not initialized
```

**Lösung:**

**1. Prüfe initialize()-Aufruf:**
```python
# In main.py: Muss AWAIT haben!
await openai_provider.initialize()  # ✅ Richtig
openai_provider.initialize()        # ❌ Falsch (kein await)
```

**2. Prüfe Provider-Logs:**
Schau in der Konsole, welcher Fehler bei Initialisierung auftrat.

**3. Provider-Health-Check:**
```python
# Quick-Test in main.py nach Initialisierung
health = await openai_provider.check_health()
print(f"OpenAI health: {health}")  # Sollte True sein
```

---

### Ollama-Verbindung schlägt fehl

**Symptom:**
```
Warning: Could not connect to Ollama
```

**Lösung:**

**1. Ist Ollama gestartet?**
```bash
# Prüfen
ps aux | grep ollama

# Falls nicht gestartet:
ollama serve
```

**2. Läuft auf richtigem Port?**
```bash
# Test
curl http://localhost:11434/api/tags

# Sollte JSON mit Modellen zurückgeben
```

**3. Firewall-Blockierung?**
```bash
# Temporär Firewall testen (macOS)
sudo pfctl -d  # Firewall aus
python main.py  # Testen
sudo pfctl -e  # Firewall an
```

---

## 🌐 Netzwerk-Probleme

### Timeout-Fehler

**Symptom:**
```
Error: Request timed out
```

**Lösung:**

**1. Timeout erhöhen:**

In den Provider-Dateien (z.B. `openai_provider.py`):
```python
self.client = AsyncOpenAI(
    api_key=api_key,
    timeout=120.0  # Von 30s auf 120s erhöhen
)
```

**2. Internet-Verbindung prüfen:**
```bash
ping 8.8.8.8  # Google DNS
ping api.openai.com
```

**3. VPN/Proxy?**
Falls du VPN/Proxy nutzt, könnte das Probleme verursachen:
```bash
# Test ohne VPN
# Oder: Proxy in .env konfigurieren
```

---

### SSL/Zertifikatsfehler

**Symptom:**
```
SSLError: certificate verify failed
```

**Lösung:**

**macOS:**
```bash
# Zertifikate installieren
/Applications/Python\ 3.*/Install\ Certificates.command
```

**Generell:**
```bash
# httpx SSL-Verify deaktivieren (NUR für Debugging!)
# In Provider-Code:
import httpx
client = httpx.AsyncClient(verify=False)  # ⚠️ Nur temporär!
```

---

## ⚡ Performance-Probleme

### Langsame Antworten

**Symptom:**
Antworten brauchen sehr lange

**Checkliste:**
1. **Langsames Model?**
   - GPT-4: ~20-30s für lange Antworten
   - GPT-3.5: ~5-10s
   - **Lösung:** Schnelleres Model wählen

2. **Schwache Internet-Verbindung?**
   ```bash
   speedtest-cli  # Speed testen
   ```

3. **Rate Limits?**
   Provider könnten dich drosseln:
   ```
   Error: Rate limit exceeded
   ```
   **Lösung:** Warte 60s oder upgrade deinen Plan

---

### UI friert ein

**Symptom:**
UI reagiert nicht während Antwortgenerierung

**Das ist normal!**  
Async-Streaming sollte UI nicht blocken, aber bei sehr langen Antworten kann es kurze "Hänger" geben.

**Lösung:**
Bereits implementiert (async/await). Falls Problem bleibt:
```python
# In ui/app_layout.py, run_chat_flow()
# Füge regelmäßige Updates ein:

for i, chunk in enumerate(chunks):
    current_content += chunk
    if i % 5 == 0:  # Nur jedes 5. Chunk updaten
        self.chat_view.update_last_message(current_content)
```

---

## 🐛 Häufige Fehler

### AttributeError: 'str' object has no attribute 'value'

**Symptom:**
```python
AttributeError: 'str' object has no attribute 'value'
```

**Lösung:**
Role ist ein Enum, nutze `.value`:
```python
# Falsch:
{"role": m.role, "content": m.content}

# Richtig:
{"role": m.role.value, "content": m.content}  # .value!
```

---

### Markdown wird nicht gerendert

**Symptom:**
Code-Blöcke erscheinen als Text

**Lösung:**
Prüfe `ui/chat_view.py`:
```python
ft.Markdown(
    message.content,
    selectable=True,
    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,  # Muss gesetzt sein
    code_theme="atom-one-dark",
)
```

---

### Streaming stoppt mittendrin

**Symptom:**
Antwort bricht ab, unvollständig

**Mögliche Ursachen:**
1. **Token-Limit erreicht**
   ```python
   # In Provider: max_tokens erhöhen
   stream = await self.client.chat.completions.create(
       model=model_id,
       max_tokens=4000,  # Erhöhen
   )
   ```

2. **Content-Filter** (bei OpenAI/Anthropic)
   Sensible Inhalte werden abgelehnt.

3. **API-Fehler**
   Schau in Konsole für Error-Messages.

---

## 💡 FAQ

### Kann ich mehrere Provider gleichzeitig nutzen?

**Ja!** Registriere alle Provider in `main.py`, dann kannst du im Dropdown wechseln.

---

### Werden meine Chats gespeichert?

**Ja!** 
- Automatische Speicherung in `chat_history.db` (SQLite)
- **History in Sidebar:** Alte Chats laden und fortsetzen
- **Löschen:** Chat auswählen und löschen (noch in Planung im UI)

---

### Kostet die Nutzung Geld?

**Depends:**
- **Mock-Provider:** Kostenlos
- **Ollama (lokal):** Kostenlos
- **OpenAI/Anthropic/Google:** Ja, Pay-as-you-go

**Kosten-Beispiel (OpenAI):**
- 1000 Nachrichten mit GPT-3.5: ~$1-2
- 1000 Nachrichten mit GPT-4: ~$30-60

---

### Kann ich die App ohne Internet nutzen?

**Ja!** Mit Ollama:
1. Ollama installieren
2. Modell herunterladen: `ollama pull llama3.2`
3. Ollama-Provider in App aktivieren
4. Komplett offline nutzbar

---

### Funktioniert die App auf Windows/Linux?

**Ja!** Python & Flet sind plattformübergreifend.

**Windows-spezifisch:**
- PowerShell für Umgebungsvariablen nutzen
- Evtl. `python` statt `python3`

---

## 🆘 Weitere Hilfe

### Debug-Mode aktivieren

```python
# In main.py, am Anfang
import logging
logging.basicConfig(level=logging.DEBUG)
```

Jetzt siehst du detaillierte Logs in der Konsole.

---

### Community Support

- **GitHub Issues:** [Bugs melden](https://github.com/your-repo/issues)
- **Discussions:** [Fragen stellen](https://github.com/your-repo/discussions)
- **Discord:** [Community-Chat](https://discord.gg/your-server)

---

### Logs sammeln für Bug-Report

```bash
# App mit Logging starten
python main.py 2>&1 | tee debug.log

# debug.log dann in Issue posten
```

---

## 📚 Weiterführende Docs

- **Installation:** [Getting Started](./01-getting-started.md)
- **Provider-Setup:** [Provider Integration](./03-provider-integration.md)
- **Konfiguration:** [Configuration Guide](./04-configuration.md)

---

**Problem nicht gelöst?** → [Issue erstellen](https://github.com/your-repo/issues/new) mit:
- Fehlermeldung (vollständig)
- Python-Version
- Betriebssystem
- Schritte zur Reproduktion

Wir helfen gerne! 🚀
