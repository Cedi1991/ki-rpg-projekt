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
    code_blocks = re.findall(r"```(?:python)?\s*(.*?)```", raw_content, re.DOTALL)
    if code_blocks:
        content = code_blocks[0]
    else:
        content = raw_content
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
    print("🚀 Projekt-Zyklus 1/1 gestartet (Volle Modul-Autonomie)")
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

    # Lese den aktuellen Inhalt der Ziel-Datei (z.B. core.py) ein, damit die KI sie anpassen kann
    current_target_content = ""
    target_path_full = WORKSPACE_DIR / target_file
    if target_path_full.exists():
        current_target_content = target_path_full.read_text(encoding="utf-8")

    prompt = f"""
Du bist ein erfahrener Python-Entwickler. 
AUFGABE: {target_task}

AKTUELLER INHALT DER DATEI ({target_file}):
```python
{current_target_content}
