import os
import subprocess
import time
from pathlib import Path
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# --- KONFIGURATION FÜR GITHUB ACTIONS ---
WORKSPACE_DIR = Path("workspace").resolve()
TODO_FILE = WORKSPACE_DIR / "TODO.md"
MODEL_ID = "gemini-2.5-flash"
MAX_ITERATIONS = 1              # Pro stündlichem GitHub-Lauf genau 1 neues Feature bauen
MAX_RETRIES_PER_FEATURE = 3     # Bis zu 3 Selbstkorrektur-Versuche bei roten Tests
TEST_TIMEOUT_SECONDS = 15       # Schutz vor Endlosschleifen
SLEEP_BETWEEN_LOOPS = 0         # Keine Pause nötig bei GitHub Actions

client = genai.Client()

# --- DATENMODELLE FÜR MULTI-FILE OUTPUT ---
class FileChange(BaseModel):
    relative_path: str = Field(
        description="Relativer Pfad innerhalb von workspace/, z.B. 'src/economy.py' oder 'tests/test_economy.py'"
    )
    content: str = Field(
        description="Der vollständige Python-Code für diese Datei."
    )

class ProjectEvolution(BaseModel):
    commit_message: str = Field(
        description="Kurze Git-Commit-Message für das umgesetzte Feature (z.B. 'Feat: Add economy merchant module')"
    )
    plan_and_reasoning: str = Field(
        description="Erklärung, welcher Punkt aus TODO.md umgesetzt wurde und welche neuen Aufgaben hinzugefügt wurden."
    )
    updated_todo_md: str = Field(
        description="Der vollständige, aktualisierte Inhalt der TODO.md (erledigte Aufgabe auf [x] setzen, 1-2 neue Ideen unter 'Geplant' ergänzen)."
    )
    files_to_write: list[FileChange] = Field(
        description="Liste aller neuen oder geänderten Code- und Test-Dateien im workspace."
    )

# --- SICHERHEITS- & DATEISYSTEM-FUNKTIONEN ---
def safe_resolve_path(rel_path: str) -> Path:
    """Verhindert Path-Traversal-Angriffe (z.B. '../orchestrator.py')."""
    cleaned = rel_path.lstrip("/\\")
    if cleaned.startswith("workspace/"):
        cleaned = cleaned[len("workspace/"):]
    
    target_path = (WORKSPACE_DIR / cleaned).resolve()
    if not target_path.is_relative_to(WORKSPACE_DIR):
        raise ValueError(f"Sicherheitsverstoß: Pfad '{rel_path}' liegt außerhalb von {WORKSPACE_DIR}!")
    if target_path.name == "orchestrator.py" or ".git" in target_path.parts:
        raise ValueError(f"Sicherheitsverstoß: Zugriff auf '{rel_path}' ist verboten!")
    return target_path

def get_workspace_snapshot() -> str:
    """Liest alle relevanten Dateien im Workspace ein und baut einen Kontext-String."""
    snapshot = []
    for path in sorted(WORKSPACE_DIR.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and not path.name.startswith("."):
            rel_path = path.relative_to(WORKSPACE_DIR)
            content = path.read_text(encoding="utf-8")
            snapshot.append(f"--- DATEI: {rel_path} ---\n```\n{content}\n```\n")
    return "\n".join(snapshot)

def apply_changes(evolution: ProjectEvolution) -> None:
    """Schreibt die aktualisierte TODO.md sowie alle geänderten/neuen Module auf die Festplatte."""
    TODO_FILE.write_text(evolution.updated_todo_md, encoding="utf-8")
    
    for file_change in evolution.files_to_write:
        target = safe_resolve_path(file_change.relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(file_change.content, encoding="utf-8")
        print(f"  📄 Geschrieben: {target.relative_to(WORKSPACE_DIR)}")

# --- GIT & TEST FUNKTIONEN ---
def run_cmd(cmd: list[str], timeout: int = 30, env: dict | None = None) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False, env=env
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT: Befehl '{' '.join(cmd)}' überschritt {timeout}s."

def run_tests() -> tuple[bool, str]:
    """Führt pytest im Workspace aus (mit gesetztem PYTHONPATH auf workspace/)."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(WORKSPACE_DIR)
    return run_cmd(
        ["pytest", str(WORKSPACE_DIR / "tests"), "-v", "--tb=short"],
        timeout=TEST_TIMEOUT_SECONDS,
        env=env,
    )

def git_commit(message: str) -> None:
    run_cmd(["git", "add", str(WORKSPACE_DIR)])
    run_cmd(["git", "commit", "-m", message])

def git_rollback() -> None:
    """Setzt geänderte Dateien zurück UND löscht neu erstellte (untracked) Dateien im Workspace."""
    print("🔄 [ROLLBACK] Setze gesamten Workspace auf den letzten stabilen Git-Commit zurück...")
    run_cmd(["git", "checkout", "HEAD", "--", str(WORKSPACE_DIR)])
    run_cmd(["git", "clean", "-fd", str(WORKSPACE_DIR)])

def get_git_history() -> str:
    _, log = run_cmd(["git", "log", "-n", "10", "--oneline"])
    return log

# --- KI-AGENTEN-AUFRUF ---
def generate_project_evolution(workspace_snapshot: str, git_log: str, last_error: str = "") -> ProjectEvolution:
    system_instruction = (
        "Du bist ein autonomer Senior-Python-Architekt. Du entwickelst ein modulares Projekt im Ordner `workspace/` weiter.\n"
        "ARCHITEKTUR- & SICHERHEITSREGELN:\n"
        "1. Arbeite die `TODO.md` ab: Wähle pro Durchlauf GENAU EINE offene Aufgabe `[ ]` aus, setze sie um und markiere sie als `[x]`.\n"
        "2. Wenn weniger als 3 offene Aufgaben in `TODO.md` stehen, füge 1-2 neue, sinnvolle Feature-Ideen zur `TODO.md` hinzu.\n"
        "3. Halte den Code modular: Lege neue Funktionalitäten in eigenen Modulen unter `src/` an und schreibe passende Unit-Tests unter `tests/test_<modul>.py`.\n"
        "4. Imports in Tests müssen immer relativ zum Workspace-Root sein (z.B. `from src.economy import ...`).\n"
        "5. Lösche niemals bestehende Funktionalität oder bestehende Tests, es sei denn zur Fehlerbehebung.\n"
        "6. Gib in `files_to_write` immer den VOLLSTÄNDIGEN Dateiinhalt der jeweiligen Datei an (keine Platzhalter wie `# rest of code`).\n"
        "7. Nutze nur die Python-Standardbibliothek. Keine Systemaufrufe (`os.system`, `subprocess`) oder Dateioperationen außerhalb des Speichers."
    )

    prompt = f"""
### Bisherige Git-Historie:
{git_log}

### Aktueller Zustand aller Dateien im Workspace:
{workspace_snapshot}
"""
    if last_error:
        prompt += (
            f"\n### ⚠️ FEHLER IM LETZTEN DURCHLAUF!\n"
            f"Deine letzten Änderungen führten zu folgendem Fehler. Analysiere und korrigiere ihn:\n```\n{last_error}\n```"
        )
    else:
        prompt += "\nSetze nun die nächste offene Aufgabe aus `TODO.md` um und liefere den neuen Code sowie die Tests."

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ProjectEvolution,
            temperature=0.3,
        ),
    )
    return response.parsed

# --- HAUPTSCHLEIFE ---
def main():
    ok, out = run_tests()
    if not ok:
        raise RuntimeError(f"Start-Tests im Workspace schlagen fehl:\n{out}")

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n{'='*65}\n🚀 Projekt-Zyklus {iteration}/{MAX_ITERATIONS} gestartet\n{'='*65}")
        
        git_log = get_git_history()
        last_error = ""
        success = False

        for attempt in range(1, MAX_RETRIES_PER_FEATURE + 1):
            print(f"🤖 KI plant & programmiert (Versuch {attempt}/{MAX_RETRIES_PER_FEATURE})...")
            try:
                current_snapshot = get_workspace_snapshot()
                
                evolution = generate_project_evolution(current_snapshot, git_log, last_error)
                print(f"🎯 Commit-Ziel: {evolution.commit_message}")
                print(f"🧠 Planung: {evolution.plan_and_reasoning}")

                apply_changes(evolution)

                print("🧪 Führe gesamte pytest-Suite aus...")
                passed, test_output = run_tests()

                if passed:
                    print("✅ Alle Modul-Tests grün! Committe Änderungen in Git.")
                    git_commit(evolution.commit_message)
                    success = True
                    break
                else:
                    print(f"❌ Tests fehlgeschlagen (Versuch {attempt}):\n{test_output}")
                    last_error = test_output

            except Exception as e:
                print(f"⚠️ Fehler bei Ausführung oder Sicherheits-Check: {e}")
                last_error = str(e)

        if not success:
            print(f"🛑 Feature konnte nach {MAX_RETRIES_PER_FEATURE} Versuchen nicht stabil integriert werden.")
            git_rollback()

        if SLEEP_BETWEEN_LOOPS > 0:
            time.sleep(SLEEP_BETWEEN_LOOPS)

    print("\n🎉 Evolutions-Lauf beendet! Aktuelle Git-Historie:")
    print(get_git_history())
    print("\n📋 Aktueller Stand der TODO.md:")
    print(TODO_FILE.read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
