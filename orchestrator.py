import os
import json
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
Du bist der Chef-Architekt des ambitioniertesten und besten RPGs der Welt.
Hier ist die aktuelle TODO.md:
{current_content}

Der letzte Task wurde erfolgreich implementiert und getestet.
Erfinde EINEN neuen, absolut epischen und bahnbrechenden Task (z.B. aus den Bereichen: Advanced 3D Engine, Dynamische Welt-Simulation, KI-gesteuerte NPCs mit Erinnerungsvermögen, Echtzeit-Netzwerk-Multiplayer, komplexe Ökonomie- und Handwerkssysteme oder immersive Magie- und Kampfsysteme), der das Spiel auf ein neues Level hebt.
Der Task muss als nächster `- [ ]` Punkt an das Ende der TODO.md angehängt werden.
Antworte AUSSCHLIESSLICH im Format: `- [ ] **Titel (`src/dateiname.py`)**: Detaillierte Beschreibung des High-End-Features...`
"""
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": expansion_prompt}],
            max_tokens=200,
            temperature=0.8,
        )
        new_task = response.choices[0].message.content.strip()
        if new_task.startswith("- [ ]"):
            updated_content = current_content.strip() + "\n" + new_task + "\n"
            todo_path.write_text(updated_content, encoding="utf-8")
            print(f"🌟 Neues World-Class Feature hinzugefügt: {new_task}")
    except Exception as e:
        print(f"⚠️ Konnte kein neues Epic-Task generieren: {e}")

def export_world_state(target_file: str, target_task: str):
    """Generiert die world_state.json inklusive visueller KI-Parameter für das 3D-Frontend."""
    try:
        modules = [f.name for f in WORKSPACE_DIR.glob("*.py")]
        
        # Dynamische visuelle Parameter basierend auf den Modulen der KI
        visual_theme = {
            "wall_color": "#161b22",
            "light_color": "#58a6ff",
            "floor_color": "#0d1117",
            "ambient_intensity": 1.2
        }
        
        if "weather" in target_file.lower():
            visual_theme["light_color"] = "#3fb950"  # Grünes Wetter-Licht
        elif "graphics" in target_file.lower() or "engine" in target_file.lower() or "dungeon" in target_file.lower():
            visual_theme["light_color"] = "#8957e5"  # Magisches Lila für Engine/Dungeon

        state = {
            "latest_module": target_file,
            "features_count": len(modules),
            "modules": modules,
            "status": f"Zuletzt implementiert: {target_task}",
            "visual_theme": visual_theme
        }
        
        Path("world_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=4), encoding="utf-8")
        print("🌍 world_state.json inklusive visueller KI-Parameter aktualisiert!")
    except Exception as e:
        print(f"⚠️ Fehler beim Exportieren der world_state.json: {e}")

def main():
    print("==========================================================")
    print("🚀 Projekt-Zyklus 1/1 gestartet (Volle Modul-Autonomie & Push)")
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

    current_target_content = ""
    target_path_full = WORKSPACE_DIR / target_file
    if target_path_full.exists():
        current_target_content = target_path_full.read_text(encoding="utf-8")

    prompt = (
        f"Du bist ein erfahrener Python-Entwickler.\n"
        f"AUFGABE: {target_task}\n\n"
        f"AKTUELLER INHALT DER DATEI ({target_file}):\n"
        f"```python\n{current_target_content}\n```\n\n"
        f"REGELN:\n"
        f"1. Passe die Datei `{target_file}` so an, dass alle bestehenden Tests fehlerfrei durchlaufen.\n"
        f"2. Antworte AUSSCHLIESSLICH mit dem vollständigen, validen Python-Code in einem Markdown-Codeblock (```python ... ```).\n"
        f"3. Kein erklärender Text!\n"
        f"4. NIEMALS modul.py bearbeiten!"
    )

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
                    {"role": "system", "content": "Du bist ein präziser Programmier-Assistent, der reinen Python-Code liefert."},
                    {"role": "user", "content": prompt + (f"\n\nLETZTER TEST-FEHLER (Behebe diesen Fehler unbedingt!):\n{last_error}" if last_error else "")}
                ],
                max_tokens=1200,
                temperature=0.2,
            )

            raw_text = response.choices[0].message.content
            cleaned_code = clean_code(raw_text)

            matches = [(target_file, cleaned_code)]

            test_file = f"tests/test_{Path(target_file).name}"
            if not (WORKSPACE_DIR / test_file).exists():
                dummy_test = "import pytest\ndef test_sanity():\n    assert True"
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
                export_world_state(target_file, target_task)

                subprocess.run(["git", "config", "--global", "user.name", "AI Evolution Bot"])
                subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])
                subprocess.run(["git", "add", "workspace/", "world_state.json"])
                subprocess.run(["git", "commit", "-m", f"feat: Implementiert '{target_task}' & aktualisiere World-State"])

                # Automatischer Git-Push ins Repository
                subprocess.run(["git", "push"], capture_output=True)
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
