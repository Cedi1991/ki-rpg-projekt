# Projekt-Roadmap: Modulares 3D-RPG & Wirtschaftssimulation

## Architektur-Vorgaben für die KI (WICHTIG)
- **Niemals modul.py bearbeiten!** Alle Änderungen müssen in den echten Modulen unter `src/` (z. B. `src/engine3d.py`, `src/core.py`, `src/economy.py`) vorgenommen werden.
- Jedes neue Feature wird als echtes Python-Modul implementiert.
- Alle Funktionen müssen deterministisch und testbar sein (mit pytest absichern in `tests/`).
- Bestehende Tests in `tests/` dürfen nicht fehlschlagen.

## Geplant (Offene Aufgaben)

- [x] **3D-Engine & Rendering (`src/engine3d.py`)**: Implementiere eine einfache ASCII/Terminal-basierte 3D-Raycasting- oder Gitter-Engine (oder 3D-Prognose-Logik), damit sich der Spieler in einem 3D-Raum bewegen kann.
- [ ] **3D-Welt & Positionierung (`src/world.py`)**: Erstelle eine 3D-Koordinaten-Logik (`x, y, z`), bei der der Spieler auf Händler und Monster im dreidimensionalen Raum trifft.
- [ ] **Markt & Handel (`src/economy.py`)**: Implementiere eine Klasse `Merchant` mit eigenem Inventar und dynamischer Preisregulierung basierend auf Angebot und Nachfrage.
- [ ] **Kampfsystem (`src/combat.py`)**: Implementiere eine Monster-Datenklasse (Name, HP, Angriff, Gold-Drop) und eine Funktion `resolve_combat_round(player, monster)` im 3D-Kontext.
- [ ] **Crafting & Werkstätten (`src/crafting.py`)**: Implementiere ein Rezept-System (`Recipe`), mit dem ein Spieler mehrere Rohstoffe zu hochwertigeren Items kombinieren kann.
- [ ] **Verbrauchsgüter & Buffs (`src/consumables.py`)**: Erlaube das Benutzen von Heiltränken oder Nahrung aus dem Inventar.
- [ ] **Speichern & Laden (`src/persistence.py`)**: Implementiere `save_player_to_json(player)` und `load_player_from_json(json_str)`, um den Spielstand zu serialisieren.
- [ ] **Tests absichern (`tests/test_engine3d.py`)**: Schreibe Unit-Tests für die neue 3D-Engine und stelle sicher, dass `pytest` fehlerfrei durchläuft.
