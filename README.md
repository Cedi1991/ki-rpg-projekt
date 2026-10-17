# KI-RPG – ein Spiel, das sich selbst weiterentwickelt

Isometrisches Dungeon-RPG im Browser (Three.js). Alle paar Stunden nimmt eine KI die nächste Aufgabe aus
`ROADMAP.md`, schreibt ein neues Spielmodul, testet es im Browser und öffnet einen **Pull Request**.
Du siehst den Vorschlag, mergst ihn (oder nicht), und das Spiel ist live.

## Aufbau
- `index.html` – Seite, lädt `game/main.js`
- `game/main.js` – Kern: Szene, Spielschleife, Modul-Lader (ein kaputtes Modul stoppt nie das Spiel)
- `game/modules/*.js` – ein Feature pro Datei; `game/manifest.json` listet die aktiven Module
- `game/API.md` – Vertrag für Module (geht bei jeder Aufgabe an die KI)
- `ROADMAP.md` – Aufgabenliste, die KI hängt nach jedem Erfolg eine neue an
- `orchestrator.py` – Ablauf: Aufgabe → Code → Syntax-Check → Browser-Test → bei Erfolg Aufgabe abhaken
- `tests/smoke_test.py` – lädt das Spiel headless, führt `selfTest()` jedes Moduls aus

## Einrichten (einmalig)
1. Neues Repository auf GitHub anlegen und diese Dateien hochladen.
2. **Settings → Secrets and variables → Actions → New repository secret**: Name `GROQ_API_KEY`, Wert = dein Groq-Schlüssel.
3. **Settings → Actions → General → Workflow permissions**: „Read and write permissions“ und
   „Allow GitHub Actions to create and approve pull requests“ aktivieren.
4. **Settings → Pages**: Source „Deploy from a branch“, Branch `main`, Ordner `/ (root)`.
5. Tab **Actions → KI-Evolution → Run workflow** für den ersten Lauf.

## Lokal testen
```
pip install playwright && python -m playwright install chromium
python tests/smoke_test.py
```
