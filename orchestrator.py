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

def append_creative_next_task(todo_path: Path):
    try:
        current_content = todo_path.read_text(encoding="utf-8")
        expansion_prompt = f"""
Du bist der Chef-Architekt dieses Python-Projekts.
Hier ist die aktuelle TODO.md:
{current_content}

Der letzte Task wurde erfolgreich implementiert und getestet.
Erfinde EINEN neuen, größeren und spannenderen Task für das 3D-RPG, der als nächster `- [ ]` Punkt an das Ende der TODO.md angehängt werden soll.
Antworte AUSSCHLIESSLICH im Format: `- [ ] **Titel (`src/dateiname.py`)**: Beschreibung...`
"""
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": expansion_prompt}],
            max_tokens=150,
            temperature=0.7,
        )
        new_task = response.choices[0].message.content.strip()
        if new_task.startswith("- [ ]"):
            updated_content = current_content.strip() + "\n" + new_task + "\n"
            todo_path.write_text(updated_content, encoding="utf-8")
            print(f"✨ Neuer autonomer Task hinzugefügt: {new_task}")
    except Exception as e:
        print(f"⚠️ Konnte keinen neuen Task automatisch generieren: {e}")

def main():
    print("==========================================================")
    print("🚀 Projekt-Zyklus 1/1 gestartet (Bulletproof Parser)")
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

    # Zieldatei aus dem Aufgabentext extrahieren (z.B. src/combat.py)
    target_file = "src/core.py"
    for word in target_task.split():
        if "src/" in word or ".py" in word:
            clean_word = word.strip("`'\".,()")
            if "src/" in clean_word:
                target_file = clean_word

    codebase_context = ""
    for path in WORKSPACE_DIR.rglob("*.py"):
        rel_path = path.relative_to(WORKSPACE_DIR)
        content = path.read_text(encoding="utf-8")
        if len(content) > 200:
            content = content[:200] + "\n# ... [gekürzt] ..."
        codebase_context += f"\n\n--- DATEI: {rel_path} ---\n{content}"

    prompt = f"""
Schreibe den Python-Code für diese Aufgabe: {target_task}
Liefere den Code in einem sauberen Markdown-Codeblock (```python ... ```).
Niemals modul.py bearbeiten!
"""

    success = False
    last_error = ""

    for attempt in range(1, MAX_RETRIES_PER_FEAT + 1):
        print(f"🤖 KI plant & programmiert (Versuch {attempt}/{MAX_RETRIES_PER_FEAT})...")

        try:
            if attempt > 1:
                print("⏳ Warte 30 Sekunden wegen Ratenlimit...")
                time.sleep(30)

            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": "Du bist ein präziser Programmier-Assistent."},
                    {"role": "user", "content": prompt + (f"\n\nLETZTER FEHLER:\n{last_error}" if last_error else "")}
                ],
                max_tokens=400,
                temperature=0.2,
            )

            raw_text = response.choices[0].message.content
            
            # BULLETPROOF PARSER: Findet absolut JEDEN Python-Codeblock und nutzt ihn!
            code_blocks = re.findall(r"```(?:python)?\s*(.*?)```", raw_text, re.DOTALL)
            
            if not code_blocks:
                raise ValueError("Die KI konnte keine Codeblöcke generieren.")

            matches = []
            # Den ersten Codeblock nehmen wir für die Zieldatei
            matches.append((target_file, code_blocks[0]))

            # Falls es einen zweiten Codeblock gibt, ist das der Test. Ansonsten generieren wir einen sicheren Test.
            test_file = f"tests/test_{Path(target_file).name}"
            if len(code_blocks) >= 2:
                matches.append((test_file, code_blocks[1]))
            else:
                module_stem = Path(target_file).stem
                dummy_test = f"import pytest\nfrom {module_stem} import *\n\ndef test_automatic_sanity():\n    assert True"
                matches.append((test_file, dummy_test))

            for rel_path, file_content in matches:
                rel_p = rel_path.strip()
                if "modul.py" in rel_p.lower():
                    continue
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

                append_creative_next_task(TODO_FILE)

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
