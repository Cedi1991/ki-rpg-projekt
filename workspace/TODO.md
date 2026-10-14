# Projekt-Roadmap: Modulare RPG- & Wirtschaftssimulation

## Architektur-Vorgaben für die KI
- Jedes neue System wird als eigenes Modul unter `src/` angelegt (z.B. `src/economy.py`, `src/combat.py`).
- Alle Funktionen müssen deterministisch testbar sein (bei Zufallslogik immer einen optionalen `seed` oder feste Parameter erlauben).
- Bestehende Klassen in `src/core.py` dürfen um neue Attribute/Methoden erweitert werden, solange alle alten Tests in `tests/test_core.py` grün bleiben.

## Geplant (Offen)
- [x] **Markt & Handel (`src/economy.py`)**: Implementiere eine Klasse `Merchant` mit einem eigenen Inventar und Goldbestand sowie den Methoden `buy_from_player(player, item_name)` und `sell_to_player(player, item_name)` inklusive dynamischer Preisfaktoren.
- [x] **Kampfsystem (`src/combat.py`)**: Implementiere eine `Monster`‑Datenklasse (Name, HP, Angriff, Gold‑Drop) und eine Funktion `resolve_combat_round(player, monster)`, die Schaden berechnet, Tod prüft und bei Sieg automatisch Gold an den Spieler vergibt.
- [x] **Crafting & Werkstätten (`src/crafting.py`)**: Implementiere ein Rezept‑System (`Recipe`), mit dem ein Spieler mehrere Rohstoffe aus seinem Inventar zu einem höherwertigen Item kombinieren kann (`craft_item(player, recipe)`).
- [x] **Verbrauchsgüter & Buffs (`src/consumables.py`)**: Ermögliche das Benutzen von Heiltränken oder Nahrung aus dem Inventar (`use_item(player, item_name)`), um `hp` bis maximal `max_hp` wiederherzustellen.
- [x] **Speichern & Laden (`src/persistence.py`)**: Implementiere `save_player_to_json(player) -> str` und `load_player_from_json(json_str) -> Player`, um den kompletten Spielstand (inkl. Inventar) zu serialisieren.
- [x] **Mehrspieler‑Modus (`src/multiplayer.py`)**: Netzwerk‑Synchronisation, Server‑Client‑Architektur und Spieler‑Interaktion.
- [x] **Quests & Storyline (`src/quests.py`)**: Quest‑Logik, Belohnungen und Fortschritts‑Tracking.
- [x] **Grafische Benutzeroberfläche (`src/gui.py`)**: Grundlegendes UI mit `tkinter` für Inventar‑Anzeige und Interaktionen.
- [x] **Implementierung eines einfachen Dialogsystems (`src/dialogue.py`)**
- [ ] Implementierung eines einfachen Dialogsystems (`src/dialogue.py`).
- [ ] Erweiterung des Mehrspieler‑Modus um Lobby‑ und Chat‑Funktionen.
- [ ] Persistenz für Quest‑Fortschritt in `src/persistence.py`.

## Weitere Ideen (optional)
- [ ] Implementierung eines einfachen Dialogsystems (`src/dialogue.py`).
- [ ] Erweiterung des Mehrspieler‑Modus um Lobby‑ und Chat‑Funktionen.
- [ ] Persistenz für Quest‑Fortschritt in `src/persistence.py`.
