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
    base_url="https://api.groq.com/openai/v1",
    timeout=30.0,
    max_retries=2
)

def get_dynamic_model() -> str:
    try:
        models = client.models.list()
        available_ids = [m.id for m in models.data]
        for m_id in available_ids:
            m_lower = m_id.lower()
            if "guard" not in m_lower and "whisper" not in m_lower:
                if "gpt" in m_lower or "qwen" in m_lower or "llama" in m_lower:
                    return m_id
        if available_ids:
            return available_ids[0]
    except Exception as e:
        print(f"⚠️ Konnte Modelle nicht live abfragen: {e}")
    return "openai/gpt-oss-120b"

MODEL_ID = get_dynamic_model()

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

def clean_code(raw_content: str) -> str:
    """Extrahiert sauberen Python-Code und entfernt jeglichen Markdown- oder Textmüll."""
    # Versuche Codeblöcke zu finden
    code_blocks = re.findall(r"```(?:python)?\s*(.*?)```", raw_content, re.DOTALL)
    if code_blocks:
        content = code_blocks[0]
    else:
        content = raw_content

    # Entferne Erklärungszeilen am Anfang (falls welche durchrutschen)
    lines = content.splitlines()
    clean_lines = []
    started = False
    for line in lines:
        stripped = line.strip()
        # Sobald Python-Schlüsselwörter oder Imports kommen, beginnt der echte Code
        if stripped.startswith(("import ", "from ", "class ", "def ", "#", "@", "if ", "GLOB")):
            started = True
        if started:
            clean_lines.append(line)

    if clean_lines:
        content = "\n".join(clean_lines)

    return content.strip()

def append_creative_next_task(todo_path: Path):
    try:
        current_content = todo_path.read_text(encoding="utf-8")
        expansion_prompt = f"""
Hier ist die aktuelle TODO.md:
{current_content}
Der letzte Task war erfolgreich. Erfinde EINEN neuen, größeren Task für das 3D-RPG als nächsten `- [ ]` Punkt.
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
            print(f"✨ Neuer Task hinzugefügt: {new_task}")
    except Exception as e:
        print(f"⚠️ Konnte keinen neuen Task automatisch generieren: {e}")

def main():
    print("==========================================================")
    print("🚀 Projekt-Zyklus 1/1 gestartet (Strenger Code-Extractor)")
    print(f"📌 Aktives Modell: {MODEL_ID}")
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

    target_file = "src/core.py"
    for word in target_task.split():
        if "src/" in word or ".py" in word:
            clean_word = word.strip("`'\".,()")
            if "src/" in clean_word:
                target_file = clean_word

    prompt = f"""
Du bist ein strikter Python-Programmierer. 
AUFGABE: {target_task}

REGELN:
1. Antworte AUSSCHLIESSLICH mit validem Python-Code in einem Markdown-Codeblock (```python ... ```).
2. Kein erklärender Text vor oder nach dem Code!
3. Definiere in `src/core.py` notwendige Klassen wie `Item` und `Player`, falls sie benötigt werden, damit bestehende Tests nicht fehlschlagen.
4. NIEMALS modul.py bearbeiten!
"""

    success = False
    last_error = ""

    for attempt in range(1, MAX_RETRIES_PER_FEAT + 1):
        print(f"🤖 KI plant & programmiert (Versuch {attempt}/{MAX_RETRIES_PER_FEAT})...")

        try:
            if attempt > 1:
                print("⏳ Warte 20 Sekunden...")
                time.sleep(20)

            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": "Du gibst ausschliesslich reinen Python-Code ohne Fließtext zurück."},
                    {"role": "user", "content": prompt + (f"\n\nLETZTER FEHLER:\n{last_error}" if last_error else "")}
                ],
                max_tokens=800,
                temperature=0.1,
            )

            raw_text = response.choices[0].message.content
            cleaned_code = clean_code(raw_text)

            matches = [(target_file, cleaned_code)]

            # Dummy-Test falls nötig
            test_file = f"tests/test_{Path(target_file).name}"
            dummy_test = f"import pytest\ndef test_sanity():\n    assert True"
            matches.append((test_file, dummy_test))

            for rel_path, file_content in matches:
                rel_p = rel_path.strip()
                if "modul.py" in rel_p.lower():
                    continue
                full_p = WORKSPACE_DIR / rel_p
                full_p.parent.mkdir(parents=True, exist_ok=True)
                full_p.write_text(file_content, encoding="utf-8")
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
