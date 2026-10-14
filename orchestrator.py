import os
import subprocess
import time
import re
from pathlib import Path
from openai import OpenAI

# --- KONFIGURATION FÜR GITHUB ACTIONS ---
WORKSPACE_DIR = Path("workspace").resolve()
TODO_FILE = WORKSPACE_DIR / "TODO.md"

MAX_RETRIES_PER_FEAT = 3           
TEST_TIMEOUT_SECONDS = 15          

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def get_best_available_model() -> str:
    try:
        models = client.models.list()
        available_ids = [m.id for m in models.data]
        for m_id in available_ids:
            if "guard" not in m_id.lower() and "whisper" not in m_id.lower() and ("gpt" in m_id.lower() or "qwen" in m_id.lower() or "llama" in m_id.lower()):
                return m_id
        for m_id in available_ids:
            if "guard" not in m_id.lower() and "whisper" not in m_id.lower():
                return m_id
        if available_ids:
            return available_ids[0]
    except Exception as e:
        print(f"⚠️ Konnte Modelle nicht automatisch abfragen: {e}")
    return "openai/gpt-oss-120b"

MODEL_ID = get_best_available_model()

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
    print("🚀 Projekt-Zyklus 1/1 gestartet (Robuster Text-Parser)")
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
        content = path.read_text(encoding="utf-8")
        if len(content) > 400:
            content = content[:400] + "\n# ... [gekürzt] ..."
        codebase_context += f"\n\n--- DATEI: {rel_path} ---\n{content}"

    prompt = f"""
Du bist ein autonomer Software-Architekt und Senior Python Developer.
Dein Ziel ist es, das modulare RPG- und Wirtschaftssimulations-Projekt Schritt für Schritt zu erweitern.

AKTUELLE ROADMAP (TODO.md):
{todo_content}

ZU LÖSENDE AUFGABE:
{target_task}

BESTEHENDE CODEBASIS (Auszug):
{codebase_context}

ARCHITEKTUR-VORGABEN:
1. Erstelle das nötige Modul unter src/ (z.B. src/persistence.py) und passende Unit-Tests unter tests/test_*.py.
2. Schreibe sauberen, funktionsfähigen Python-Code.
3. Gib den Code in Markdown-Blöcken an und schreibe ÜBER jeden Block den Dateipfad als Kommentar oder Überschrift im Format: `### DATEI: src/dein_modul.py`
"""

    success = False
    last_error = ""

    for attempt in range(1, MAX_RETRIES_PER_FEAT + 1):
        print(f"🤖 KI plant & programmiert (Versuch {attempt}/{MAX_RETRIES_PER_FEAT})...")
        
        try:
            if attempt > 1:
                print("⏳ Warte 10 Sekunden...")
                time.sleep(10)

            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": "Du bist ein präziser Programmier-Assistent."},
                    {"role": "user", "content": prompt + (f"\n\nLETZTER FEHLER BEIM TESTEN:\n{last_error}" if last_error else "")}
                ],
                max_tokens=8192,
                temperature=0.2,
            )
            
            raw_text = response.choices[0].message.content
            
            # Dateien über Regex aus den Markdown-Blöcken extrahieren
            # Erwartet Format: ### DATEI: pfad/zu/datei.py gefolgt von ```python ... ```
            pattern = r"###\s*DATEI:\s*([^\n]+)\s*```python\s*(.*?)```"
            matches = re.findall(pattern, raw_text, re.DOTALL)
            
            if not matches:
                # Fallbversuch für andere Block-Formate
                pattern_alt = r"###\s*DATEI:\s*([^\n]+)\s*```\s*(.*?)```"
                matches = re.findall(pattern_alt, raw_text, re.DOTALL)

            if not matches:
                raise ValueError("Die KI hat keine lesbaren Dateiblöcke im erwarteten Format zurückgegeben.")

            for rel_path, file_content in matches:
                rel_p = rel_path.strip()
                full_p = WORKSPACE_DIR / rel_p
                full_p.parent.mkdir(parents=True, exist_ok=True)
                full_p.write_text(file_content.strip(), encoding="utf-8")
                print(f"📝 Datei geschrieben: {rel_p}")

            lines[target_line_idx] = f"- [x] {target_task}"
            TODO_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

            print("🧪 Führe Tests aus...")
            test_passed, test_output = run_tests()
            
            if test_passed:
                print("✅ Alle Tests erfolgreich bestanden!")
                success = True
                
                subprocess.run(["git", "config", "--global", "user.name", "AI Evolution Bot"])
                subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])
                subprocess.run(["git", "add", "workspace/"])
                subprocess.run(["git", "commit", "-m", f"feat: Implementiert '{target_task}'"])
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
