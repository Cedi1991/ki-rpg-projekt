#!/usr/bin/env python3
"""Browser-Test: lädt das Spiel headless, prüft Fehler und führt die selfTest()-Funktionen aller Module aus.

Exit-Code 0 = alles grün, 1 = Fehler (Meldung auf stdout, wird an die KI zurückgegeben).
Optional: THREE_LOCAL=/pfad/three.min.js ersetzt das CDN (für Offline-Läufe).
"""
import functools
import http.server
import json
import os
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main() -> int:
    manifest = json.loads((ROOT / "game" / "manifest.json").read_text(encoding="utf-8"))
    expected = manifest["modules"]
    problems = []

    httpd = serve()
    url = f"http://127.0.0.1:{httpd.server_address[1]}/index.html?test=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
        )
        page = browser.new_page(viewport={"width": 420, "height": 800})
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        three_local = os.environ.get("THREE_LOCAL")
        if three_local:
            page.route(
                "**/three.min.js",
                lambda route: route.fulfill(path=three_local, content_type="application/javascript"),
            )

        page.goto(url)
        try:
            page.wait_for_function("window.__game && window.__game.ready", timeout=30000)
        except Exception:
            problems.append("Spiel wurde nicht bereit (Timeout beim Laden).")

        if not problems:
            errors = page.evaluate("window.__game.ctx.errors")
            for err in errors:
                problems.append(f"Fehler in Modul '{err['module']}': {err['error']}")

            loaded = page.evaluate("window.__game.ctx.modules.map(m => m.id)")
            missing = [m for m in expected if m not in loaded]
            if missing:
                problems.append(f"Module nicht geladen: {', '.join(missing)}")

            if page.locator("canvas").count() == 0:
                problems.append("Kein <canvas> gefunden.")

            if not problems:
                # Spiel erst ein paar Sekunden simulieren, dann Selbsttests.
                try:
                    page.evaluate("window.__game.ctx.step(180)")
                except Exception as e:
                    problems.append(f"Fehler beim Simulieren: {e}")
                results = page.evaluate("window.__game.runSelfTests()")
                for r in results:
                    if not r["ok"]:
                        problems.append(f"selfTest von '{r['id']}' fehlgeschlagen: {r.get('error', 'false zurückgegeben')}")
                errors_after = page.evaluate("window.__game.ctx.errors")
                for err in errors_after[len(errors):]:
                    problems.append(f"Laufzeitfehler in '{err['module']}': {err['error']}")

        for e in page_errors:
            problems.append(f"Browser-Fehler: {e}")
        browser.close()
    httpd.shutdown()

    if problems:
        print("TESTS FEHLGESCHLAGEN:")
        for line in problems:
            print(" -", line)
        return 1
    print(f"OK: {len(expected)} Module geladen, alle selfTests bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())