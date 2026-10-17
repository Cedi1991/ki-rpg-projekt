#!/usr/bin/env python3
"""KI-Evolution: nimmt die nächste Aufgabe aus ROADMAP.md, lässt ein LLM ein JS-Spielmodul schreiben
und prüft es im Browser (tests/smoke_test.py). Der Orchestrator committet/pusht NICHT:
das macht der Workflow (als Pull Request)."""
import json
import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
ROADMAP = ROOT / "ROADMAP.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MANIFEST = ROOT / "game" / "manifest.json"
MODULES = ROOT / "game" / "modules"
API_DOC = ROOT / "game" / "API.md"

MODEL = os.environ.get("EVOLUTION_MODEL", "openai/gpt-oss-120b")
MAX_ATTEMPTS = 3
TEST_TIMEOUT = 150
MAX_TOKENS = 6000

TASK_RE = re.compile(r"^- \[( |x|!)\] ([a-z][a-z0-9-]{1,30}) \| ([^|]+?) \| ([^|]+)$")
FORBIDDEN = [
    r"\bfetch\s*\(", r"XMLHttpRequest", r"\bWebSocket\b", r"\beval\s*\(", r"new\s+Function",
    r"\bimport\s*\(", r"^\s*import\s", r"document\.write", r"<script", r"Math\.random",
    r"document\.cookie", r"sendBeacon",
]


def client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        timeout=90.0,
        max_retries=2,
    )


# ---------- Roadmap ----------
def read_tasks():
    tasks = []
    for idx, line in enumerate(ROADMAP.read_text(encoding="utf-8").splitlines()):
        m = TASK_RE.match(line.strip())
        if m:
            tasks.append({"line": idx, "mark": m.group(1), "id": m.group(2), "title": m.group(3).strip(), "desc": m.group(4).strip()})
    return tasks


def set_mark(task_id: str, mark: str):
    lines = ROADMAP.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = TASK_RE.match(line.strip())
        if m and m.group(2) == task_id:
            lines[i] = f"- [{mark}] {task_id} | {m.group(3).strip()} | {m.group(4).strip()}"
    ROADMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_task(task_id: str, title: str, desc: str):
    text = ROADMAP.read_text(encoding="utf-8").rstrip() + f"\n- [ ] {task_id} | {title} | {desc}\n"
    ROADMAP.write_text(text, encoding="utf-8")


# ---------- LLM ----------
def ask(prompt: str, system: str, max_tokens: int, temperature: float):
    resp = client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    choice = resp.choices[0]
    return choice.message.content or "", choice.finish_reason


def extract_code(text: str) -> str:
    m = re.search(r"```(?:javascript|js)?[ \t]*\n(.*?)(?:```|\Z)", text, re.DOTALL)
    return (m.group(1) if m else text).strip() + "\n"


def validate_module(task_id: str, code: str) -> str | None:
    if "export default" not in code:
        return "Es fehlt `export default { ... }`."
    if not re.search(r"id:\s*['\"]" + re.escape(task_id) + r"['\"]", code):
        return f"Das Modul muss `id: '{task_id}'` enthalten."
    for fn in ("init", "selfTest"):
        if not re.search(r"\b" + fn + r"\s*\(", code):
            return f"Die Methode {fn}() fehlt."
    for pat in FORBIDDEN:
        if re.search(pat, code, re.MULTILINE):
            return f"Verbotenes Muster im Code: {pat}"
    return None


def build_prompt(task, existing_code: str | None, last_error: str) -> str:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parts = [
        f"AUFGABE (Modul-ID `{task['id']}`): {task['title']}\n{task['desc']}",
        "MODUL-API UND REGELN:\n" + API_DOC.read_text(encoding="utf-8"),
        "BEREITS VORHANDENE MODULE: " + ", ".join(manifest["modules"]),
    ]
    if existing_code:
        parts.append("AKTUELLER CODE DIESES MODULS (erweitere ihn, behalte Funktionierendes):\n```js\n" + existing_code + "\n```")
    if last_error:
        parts.append("LETZTER FEHLER (unbedingt beheben):\n" + last_error[-2500:])
    parts.append(
        f"Antworte AUSSCHLIESSLICH mit dem vollständigen Inhalt von game/modules/{task['id']}.js "
        "in genau einem ```js-Codeblock. Kein erklärender Text. Halte den Code kompakt (unter ca. 250 Zeilen)."
    )
    return "\n\n".join(parts)


def propose_next_task() -> None:
    tasks = read_tasks()
    used = {t["id"] for t in tasks}
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prompt = (
        "Du planst die nächste Funktion für ein kleines isometrisches Dungeon-RPG im Browser (Three.js, Handy-Touch).\n"
        f"Bereits vorhandene Module: {', '.join(manifest['modules'])}\n"
        "Bisherige Aufgaben:\n" + "\n".join(f"- {t['id']}: {t['title']}" for t in tasks) + "\n\n"
        "Schlage GENAU EINE neue, kleine, konkrete und noch nicht vorhandene Funktion vor, die das Spiel sichtbar "
        "oder spielerisch verbessert und sich in EINEM Modul umsetzen lässt (keine Wiederholung bisheriger Aufgaben!).\n"
        "Antworte nur mit einer Zeile im Format:\n"
        "modul-id | Kurzer Titel | Genaue Beschreibung in 1-2 Sätzen, was das Modul tun soll\n"
        "Die ID: nur Kleinbuchstaben, Ziffern, Bindestriche. Keine senkrechten Striche im Text."
    )
    for _ in range(2):
        try:
            text, _ = ask(prompt, "Du bist ein pragmatischer Spiele-Designer.", 300, 0.8)
        except Exception as e:  # noqa: BLE001
            print(f"⚠️ Konnte keine Folgeaufgabe erzeugen: {e}")
            return
        line = text.strip().splitlines()[0].strip().strip("`").lstrip("- ").strip() if text.strip() else ""
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3 and re.fullmatch(r"[a-z][a-z0-9-]{1,30}", parts[0]) and parts[0] not in used:
            append_task(parts[0], parts[1], parts[2])
            print(f"🌟 Neue Aufgabe: {parts[0]} | {parts[1]}")
            return
        print(f"ℹ️ Vorschlag unbrauchbar oder doppelt: {line!r}")


# ---------- Tests ----------
def run_tests() -> tuple[bool, str]:
    # Bewusst minimale Umgebung: KEINE Secrets (GROQ_API_KEY, Tokens) für den Testlauf.
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "PLAYWRIGHT_BROWSERS_PATH", "THREE_LOCAL", "TMPDIR") if k in os.environ}
    try:
        r = subprocess.run(
            [sys.executable, "tests/smoke_test.py"], cwd=ROOT, env=env,
            capture_output=True, text=True, timeout=TEST_TIMEOUT,
        )
        return r.returncode == 0, (r.stdout + "\n" + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, "Test-Timeout überschritten."


def node_check(path: Path) -> str | None:
    try:
        r = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        return None
    return None if r.returncode == 0 else r.stderr.strip()


def set_output(key: str, value: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    value = re.sub(r"[^\w\s\-äöüÄÖÜß.,()]", "", value)[:120]
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


# ---------- Hauptablauf ----------
def main() -> int:
    print(f"🚀 KI-Evolution gestartet (Modell: {MODEL})")

    ok, out = run_tests()
    if not ok:
        print("❌ Ausgangszustand ist nicht grün, breche ab (kein Token-Verbrauch):\n" + out)
        return 1

    tasks = read_tasks()
    open_tasks = [t for t in tasks if t["mark"] == " "]
    if not open_tasks:
        print("✨ Keine offene Aufgabe, erzeuge eine neue.")
        propose_next_task()
        set_output("title", "Neue Aufgabe geplant")
        return 0

    task = open_tasks[0]
    print(f"🤖 Aufgabe: {task['id']} | {task['title']}")
    target = MODULES / f"{task['id']}.js"
    manifest_backup = MANIFEST.read_text(encoding="utf-8")
    original = target.read_text(encoding="utf-8") if target.exists() else None

    def restore():
        MANIFEST.write_text(manifest_backup, encoding="utf-8")
        if original is None:
            target.unlink(missing_ok=True)
        else:
            target.write_text(original, encoding="utf-8")

    last_error = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"— Versuch {attempt}/{MAX_ATTEMPTS}")
        try:
            text, finish = ask(
                build_prompt(task, original, last_error),
                "Du bist ein präziser JavaScript-Entwickler und lieferst nur Code.",
                MAX_TOKENS, 0.2,
            )
        except Exception as e:  # noqa: BLE001
            last_error = f"API-Fehler: {e}"
            print("⚠️", last_error)
            time.sleep(20)
            continue

        if finish == "length":
            last_error = "Die Antwort wurde abgeschnitten. Schreibe das Modul deutlich kürzer."
            print("⚠️", last_error)
            continue

        code = extract_code(text)
        problem = validate_module(task["id"], code)
        if problem:
            last_error = problem
            print("⚠️", problem)
            continue

        target.write_text(code, encoding="utf-8")
        syntax = node_check(target)
        if syntax:
            last_error = "Syntaxfehler:\n" + syntax
            print("⚠️", last_error)
            restore()
            continue

        manifest = json.loads(manifest_backup)
        if task["id"] not in manifest["modules"]:
            manifest["modules"].append(task["id"])
        manifest["version"] = int(time.time())
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        ok, out = run_tests()
        print(out)
        if ok:
            set_mark(task["id"], "x")
            with CHANGELOG.open("a", encoding="utf-8") as f:
                f.write(f"- {date.today().isoformat()}: {task['title']} (`{task['id']}`)\n")
            propose_next_task()
            set_output("title", f"Neues Feature: {task['title']}")
            print("✅ Fertig. Änderungen liegen lokal vor (der Workflow erstellt den Pull Request).")
            return 0

        last_error = out
        restore()

    set_mark(task["id"], "!")
    set_output("title", f"Aufgabe uebersprungen: {task['title']}")
    print(f"🛑 Aufgabe '{task['id']}' nach {MAX_ATTEMPTS} Versuchen als [!] markiert. Letzter Fehler:\n{last_error}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
