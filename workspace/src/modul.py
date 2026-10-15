markdown
# TODO.md
...
- [ ] **3‑D‑Visualisierung (`src/graphics_3d.py`)**: 
    - Grundgerüst für ein Fenster mit **pygame** (oder **pyglet** als Fallback).  
    - Klasse `Game3D` mit den Methoden  
        - `__init__(self, width: int = 800, height: int = 600, seed: int | None = None)` – legt Fenster und optionale Zufalls‑Seed fest.  
        - `load_assets(self) -> None` – lädt Platzhalter‑Sprites (z. B. farbige Rechtecke) für Spieler, Monster, Items.  
        - `render(self) -> None` – zeichnet aktuelle Spiel‑State‑Objekte (Player‑Position, Monster‑Position, Inventar‑Icons).  
        - `run(self, player: Player, monsters: list[Monster]) -> None` – Haupt‑Loop, der pro Frame `render()` aufruft und Eingaben (WASD) verarbeitet.  
    - Deterministisches Verhalten: Wenn ein `seed` übergeben wird, werden alle zufälligen Positionen und Bewegungen reproduzierbar.  
    - Unit‑Test `tests/test_graphics_3d.py` prüft, dass die Klasse ohne GUI‑Start instanziierbar ist und dass `load_assets()` keine Exceptions wirft.