# Projekt-Roadmap: Modulares 3D-RPG & Wirtschaftssimulation

## Architektur-Vorgaben für die KI (WICHTIG)
- **Niemals modul.py bearbeiten!** Alle Änderungen müssen in den echten Modulen unter `src/` (z. B. `src/engine3d.py`, `src/core.py`, `src/economy.py`) vorgenommen werden.
- Jedes neue Feature wird als echtes Python-Modul implementiert.
- Alle Funktionen müssen deterministisch und testbar sein (mit pytest absichern in `tests/`).
- Bestehende Tests in `tests/` dürfen nicht fehlschlagen.
- Nach jedem todo eine neues todo erstellen und größer denken um einzigartig zu werden 

## Geplant (Offene Aufgaben)


- [ ] **Erweiterte Magie-Effekte (`src/magic.py`)**: Implementiere ein Manasystem mit Elementarzaubern und Flächenschaden, das direkt mit `src/combat.py` und `src/core.py` interagiert.
- [ ] **Dynamisches Wettersystem (`src/weather.py`)**: Programmiere Wettereffekte wie Sturm und Nebel, die die Sichtweite im Dungeon und die Boss-KI beeinflussen.
- [ ] **Fraktions- und Rufsystem (`src/factions.py`)**: Erstelle ein System für NPC-Gilden und Fraktionen mit Rufpunkten und Händler-Rabatten.


