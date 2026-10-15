markdown
# Projekt-Roadmap: Modulare RPG- & Wirtschaftssimulation

## Architektur-Vorgaben für die KI
- Jedes neue System wird als eigenes Modul unter `src/` angelegt (z.B. `src/economy.py`, `src/combat.py`).
- Alle Funktionen müssen deterministisch testbar sein (bei Zufallslogik immer einen optionalen `seed` oder feste Parameter erlauben).
- Bestehende Klassen in `src/core.py` dürfen um neue Attribute/Methoden erweitert werden, solange alle alten Tests in `tests/test_core.py` grün bleiben.

## Geplant (Offen)

- [ ] Erstelle nach jedem todo ein logisch neues todo
- [ ] Erstelle das Spiel in 3d und erweitere es durchweg
- [x] Erstelle eine interaktive main.py als spielbares Text-Menü für das RPG und die Wirtschaftssimulation
- [ ] Erstelle ein Menü für den Handel im `main.py`
- [x] **Markt & Handel (`src/economy.py`)**: Implementiere eine Klasse `Merchant` mit einem eigenen Inventar und Goldbestand sowie den Methoden `buy_from_player(player, item_name)` und `sell_to_player(player, item_name)` inklusive dynamischer Preisfaktoren.
- [ ] Implementiere dynamische Preisregulierung basierend auf Angebot und Nachfrage
- [x] **Kampfsystem (`src/combat.py`)**: Implementiere eine `Monster`‑Datenklasse (Name, HP, Angriff, Gold‑Drop) und eine Funktion `resolve_combat_round(player, monster)`, die Schaden berechnet, Tod prüft und bei Sieg automatisch Gold an den Spieler vergibt.
- [ ] Implementiere Spezialangriffe und Statusveränderungen (z.B. Betäubung, Verbrennung)
- [x] **Crafting & Werkstätten (`src/crafting.py`)**: Implementiere ein Rezept‑System (`Recipe`), mit dem ein Spieler mehrere Rohstoffe aus seinem Inventar zu einem höherwertigen Item kombinieren kann (`craft_item(player, recipe)`).
- [ ] Implementiere Werkstatt‑Upgrades, die die Effizienz von Rezepten erhöhen
- [x] **Verbrauchsgüter & Buffs (`src/consumables.py`)**: Ermögliche das Benutzen von Heiltränken oder Nahrung aus dem Inventar (`use_item(player, item_name)`), um `hp` bis maximal `max_hp` wiederherzustellen.
- [ ] Implementiere Buff‑Stacking und Dauer‑Effekte (z.B. Schild, Geschwindigkeit)
- [x] **Speichern & Laden (`src/persistence.py`)**: Implementiere `save_player_to_json(player) -> str` und `load_player_from_json(json_str) -> Player`, um den kompletten Spielstand (inkl. Inventar) zu serialisieren.
- [ ] Implementiere Auto‑Save und Load‑Checkpoint-Mechanismen
- [x] **Mehrspieler‑Modus (`src/multiplayer.py`)**: Netzwerk‑Synchronisation, Server‑Client‑Architektur und Spieler‑Interaktion.
- [ ] Implementiere Synchronisation von Inventar und Quest‑Status zwischen Server und Clients
- [x] **Quests & Storyline (`src/quests.py`)**: Quest‑Logik, Belohnungen und Fortschritts‑Tracking.
- [ ] Implementiere Quest‑Dialog und NPC‑Interaktion im Quest‑System
- [x] **Grafische Benutzeroberfläche (`src/gui.py`)**: Grundlegendes UI mit `tkinter` für Inventar‑Anzeige und Interaktionen.
- [ ] Implementiere Drag‑&‑Drop‑Funktionalität für das Inventar im GUI
- [x] **Implementierung eines einfachen Dialogsystems (`src/dialogue.py`)**
- [ ] Implementiere NPC‑Dialog‑Bäume mit dynamischen Optionen basierend auf Quest‑Status
- [x] Erweiterung des Mehrspieler‑Modus um Lobby‑ und Chat‑Funktionen.
- [ ] Implementiere Voice‑Chat oder Sprach‑zu‑Text‑Integration für die Lobby
- [x] Persistenz für Quest‑Fortschritt in `src/persistence.py`.
- [ ] Implementiere ein Quest‑Log‑UI, das den Fortschritt aller aktiven Quests anzeigt