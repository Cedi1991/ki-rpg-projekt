import os
import subprocess
import time
import json
from pathlib import Path
from pydantic import BaseModel, Field
from openai import OpenAI

# --- KONFIGURATION FÜR GITHUB ACTIONS ---
WORKSPACE_DIR = Path("workspace").resolve()
TODO_FILE = WORKSPACE_DIR / "TODO.md"

MAX_ITERATIONS = 1                 
MAX_RETRIES_PER_FEAT = 3           
TEST_TIMEOUT_SECONDS = 15          

# Verbindung zur kostenlosen Groq-API
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def get_best_available_model() -> str:
    """Fragt automatisch bei Groq nach den verfügbaren Modellen und wählt ein passendes aus."""
    try:
        models = client.models.list()
        available_ids = [m.id for m in models.data]
        print(verfügbare_modelle := f"🔍 Verfügbare Modelle von Groq: {available_ids}")
        
        # Suche bevorzugt nach llama-3.3 oder anderen starken Llama-Modellen
        for pref in ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama3-70b-8192"]:
            if pref in available_ids:
                return pref
                
        # Falls keines der bevorzugten da ist, nimm das erste verfügbare Llama-Modell
        for m_id in available_ids:
            if "llama" in m_id.lower():
                return m_id
                
        # Fallback auf das allererste in der Liste
        if available_ids:
            return available_ids[0]
            
    except Exception as e:
        print(f"⚠️ Konnte Modelle nicht automatisch abfragen: {e}")
        
    return "llama-3.3-70b-versatile" # Sicherer Standard-Fallback

MODEL_ID = get_best_available_model()

class FileChange(BaseModel):
    relative_path: str = Field(description="Relativer Pfad innerhalb von workspace/, z.B. 'src/economy.py'")
    content: str = Field(description="Der vollständige Python-Quellcode für diese Datei.")

class FeatureImplementation(BaseModel):
    explanation: str = Field(description="Kurze Erklärung der Implementierung.")
    files: list[FileChange] = Field(description="Liste aller geänderten oder neu erstellten Dateien.")

def run_tests() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["pytest", "workspace/tests/", "-v"],
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT_SECONDS,
            env={**os.environ, "PYTHONPATH": str(WORKSPACE_DIR)}
        )
        return (result.returncode == 0), result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Fehler: Test-Timeout überschritten."
    except Exception as e:
        return False, f"Fehler beim Ausführen von pytest: {str(e)}"

def rollback_workspace():
    print("🔄 [ROLLBACK] Setze gesamten Workspace auf den letzten stabilen Git-Commit zurück...")
    subprocess.run(["git", "checkout", "workspace/"], capture_output=True)
    subprocess.run(["git", "clean", "-fd", "workspace/"], capture_output=True)

def main():
    print("==========================================================")
    print("🚀 Projekt-Zyklus 1/1 gestartet (Groq Auto-Discovery)")
    print(f"📌 Automatisch gewähltes Modell: {MODEL_ID}")
    print("==========================================================")

    if not TODO_FILE.exists():
        print(f"❌ Fehler: TODO.md nicht gefunden unter {TODO_FILE}")
        return

    todo_content = TODO_FILE.read_text(encoding="utf-8")
    lines = todo_content.splitlines()
    target_line_idx = -1
    target_task = None
    
    for idx, line in enumerate(lines):
        if line.strip().startswith("- [ ]"):
            target_line_idx = idx
            target_task = line.strip()[5:].strip()
            break

    if not target_task:
        print("✨ Keine offenen Aufgaben mehr in der TODO.md!")
        return

    print(f"🤖 Nächste Aufgabe für die KI: {target_task}")

    codebase_context = ""
    for path in WORKSPACE_DIR.rglob("*.py"):
        rel_path = path.relative_to(WORKSPACE_DIR)
        codebase_context += f"\n\n--- DATEI: {rel_path} ---\n{path.read_text(encoding='utf-8')}"

    prompt = f"""
Du bist ein autonomer Software-Architekt und Senior Python Developer.
Dein Ziel ist es, das modulare RPG- und Wirtschaftssimulations-Projekt Schritt für Schritt zu erweitern.

AKTUELLE ROADMAP (TODO.md):
{todo_content}

ZU LÖSENDE AUFGABE:
{target_task}

BESTEHENDE CODEBASIS:
{codebase_context}

ARCHITEKTUR-VORGABEN:
1. Jedes neue System wird als eigenes Modul unter src/ angelegt (z.B. src/economy.py, src/combat.py).
2. Alle Funktionen müssen deterministisch testbar sein (bei Zufallslogik immer einen optionalen 'seed' oder feste Parameter erlauben).
3. Du musst zu jedem neuen Modul direkt passende Unit-Tests unter tests/test_*.py schreiben!
4. Bestehende Klassen in src/core.py dürfen um neue Attribute/Methoden erweitert werden, solange alle alten Tests in tests/test_core.py grün bleiben.

Antworte AUSSCHLIESSLICH als gültiges JSON-Objekt mit folgender Struktur:
{{
  "explanation": "Kurze Erklärung",
  "files": [
    {{
      "relative_path": "pfad/zur/datei.py",
      "content": "vollständiger python code..."
    }}
  ]
}}
"""

    success = False
    last_error = ""

    for attempt in range(1, MAX_RETRIES_PER_FEAT + 1):
        print(f"🤖 KI plant & programmiert (Versuch {attempt}/{MAX_RETRIES_PER_FEAT})...")
        
        try:
            if attempt > 1:
                print("⏳ Warte 5 Sekunden...")
                time.sleep(5)

            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": "Du bist ein präziser Programmier-Assistent und antwortest strikt in validem JSON."},
                    {"role": "user", "content": prompt + (f"\n\nLETZTER FEHLER BEIM TESTEN:\n{last_error}" if last_error else "")}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            
            raw_text = response.choices[0].message.content
            data = json.loads(raw_text)
            
            for f_change in data.get("files", []):
                rel_p = f_change["relative_path"]
                full_p = WORKSPACE_DIR / rel_p
                full_p.parent.mkdir(parents=True, exist_ok=True)
                full_p.write_text(f_change["content"], encoding="utf-8")
                print(f"📝 Datei geschrieben: {rel_p}")

            print("🧪 Führe Tests aus...")
            test_passed, test_output = run_tests()
            
            if test_passed:
                print("✅ Alle Tests erfolgreich bestanden!")
                success = True
                lines[target_line_idx] = f"- [x] {target_task}"
                TODO_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
                break
            else:
                print(f"❌ Tests fehlgeschlagen:\n{test_output}")
                last_error = test_output
                rollback_workspace()

        except Exception as e:
            print(f"⚠️ API-Fehler (Versuch {attempt}): {str(e)}")
            last_error = str(e)
            rollback_workspace()

    if not success:
        print(f"🛑 Feature konnte nach {MAX_RETRIES_PER_FEAT} Versuchen nicht stabil integriert werden.")
        rollback_workspace()

if __name__ == "__main__":
    main()
