# Projekt-Roadmap: Modulares 3D-RPG & Wirtschaftssimulation

## Architektur-Vorgaben für die KI (WICHTIG)
- **Niemals modul.py bearbeiten!** Alle Änderungen müssen in den echten Modulen unter `src/` (z. B. `src/engine3d.py`, `src/core.py`, `src/economy.py`) vorgenommen werden.
- Jedes neue Feature wird als echtes Python-Modul implementiert.
- Alle Funktionen müssen deterministisch und testbar sein (mit pytest absichern in `tests/`).
- Bestehende Tests in `tests/` dürfen nicht fehlschlagen.

## Geplant (Offene Aufgaben)


- [ ] **Echtzeit-Wettersystem & Tag/Nacht-Zyklus (`src/weather.py`)**: Implementiere ein dynamisches Wettersystem, das Regen, Sturm und Sonnenschein simuliert und die Sichtweite sowie Kampffähigkeiten im Dungeon beeinflusst.
- [ ] **Prozedurales Fraktions- & Questsystem (`src/factions.py`)**: Erstelle ein System für rivalisierende Fraktionen, bei dem der Spieler durch Taten Rufpunkte sammelt, die Einfluss auf Handelspreise und NPC-Dialoge haben.
- [ ] **Erweitertes Magie- und Zaubersystem (`src/magic.py`)**: Programmiere ein Manasystem mit kombinierbaren Elementarzaubern, Wirkungsbereichen (AoE) und visuellen Effekt-Berechnungen für Kämpfe.
- [x] **3D-Engine & Rendering (`src/engine3d.py`)**: Implementiere eine einfache ASCII/Terminal-basierte 3D-Raycasting- oder Gitter-Engine (oder 3D-Prognose-Logik), damit sich der Spieler in einem 3D-Raum bewegen kann.
- [x] **3D-Welt & Positionierung (`src/world.py`)**: Erstelle eine 3D-Koordinaten-Logik (`x, y, z`), bei der der Spieler auf Händler und Monster im dreidimensionalen Raum trifft.
- [x] **Markt & Handel (`src/economy.py`)**: Implementiere exakt folgende Klassen und Funktionen:
  - Klasse `Item` mit Attributen `name` (str), `value` (int) und `weight` (float).
  - Klasse `Merchant` mit Attributen `name` (str), `inventory` (list von Item) und `gold` (int).
  - Methoden für `Merchant`: `buy_from_player(self, player, item_name)` und `sell_to_player(self, player, item_name)` mit einfacher Preislogik.
- [x] **Kampfsystem (`src/combat.py`)**: Implementiere eine Monster-Datenklasse (Name, HP, Angriff, Gold-Drop) und eine Funktion `resolve_combat_round(player, monster)` im 3D-Kontext.
- [x] **Crafting & Werkstätten (`src/crafting.py`)**: Implementiere ein Rezept-System (`Recipe`), mit dem ein Spieler mehrere Rohstoffe zu hochwertigeren Items kombinieren kann.
- [x] **Verbrauchsgüter & Buffs (`src/consumables.py`)**: Erlaube das Benutzen von Heiltränken oder Nahrung aus dem Inventar.
- [x] **Speichern & Laden (`src/persistence.py`)**: Implementiere `save_player_to_json(player)` und `load_player_from_json(json_str)`, um den Spielstand zu serialisieren.
- [x] **Tests absichern (`tests/test_engine3d.py`)**: Schreibe Unit-Tests für die neue 3D-Engine und stelle sicher, dass `pytest` fehlerfrei durchläuft.
- [x] **Dynamisches Wettersystem & Tageszyklus (`src/weather.py`)**: Implementiere eine `WeatherSystem`-Klasse, die deterministisch zwischen Zuständen (Sonnig, Regen, Sturm, Nebel) wechselt und diese auf die Spielmechaniken auswirkt (z. B. eingeschränkte Sichtweite in der 3D-Engine, veränderte Häufigkeit von Monster-Spawns oder Bonus-XP bei Sturm), wobei der Zustand über die `src/world.py`-Position und Zeitlogik synchronisiert wird.
- [x] **Magie- & Mana-System (`src/magic.py`)**: Implementiere ein `Spell`-Objekt mit Mana-Kosten, Wirkungsgrad und Kühlung, integriert mit dem Kampfsystem (`src/combat.py`) für Zauberangriffe und mit der 3D-Engine (`src/engine3d.py`) für räumliche Effekte (z. B. Flächenangriffe oder Teleportation), inklusive deterministischer Mana-Regeneration über den Tageszyklus in `src/weather.py`.
- [x] **Mehrschichtige Dungeon-Generierung & Boss-KI (`src/dungeon.py`)**: Implementiere einen deterministischen prozeduralen Dungeon-Generator, der mehrschichtige 3D-Gitterstrukturen mit verborgenen Schätzen und Felsfallen erzeugt, integriert mit `src/world.py` für die Kartennavigation und `src/combat.py` für eine adaptive Boss-KI, die ihre Taktik (Aggression, Flucht, Heilung basierend auf Wetter aus `src/weather.py`) dynamisch an den Spielerstand anpasst.
- [x] **Mehrschichtige Dungeon-Generierung & Boss-KI (`src/dungeon.py`)**: Implementiere einen deterministischen prozeduralen Dungeon-Generator, der mehrschichtige 3D-Gitterstrukturen mit verborgenen Schätzen und Felsfallen erzeugt, integriert mit `src/world.py` für die Kartennavigation und `src/combat.py` für eine adaptive Boss-KI, die ihre Taktik (Aggression, Flucht, Heilung basierend auf Wetter aus `src/weather.py`) dynamisch an den Spielerstand anpasst.
- [x] **Reputations- & Fraktions-System (`src/factions.py`)**: Implementiere ein dynamisches Reputations-Tracking für verschiedene Fraktionen (z. B. Händlergilde, Wächter, Räuber), das durch Handel (`src/economy.py`), Kämpfe (`src/combat.py`) und Questen beeinflusst wird; integriere Fraktions-Status, der Zugang zu exklusiven Ausrüstung, Preisnachlässen oder verborgenen Dungeon-Ebenen (`src/dungeon.py`) freischaltet und bei negativem Status Feindseligkeit oder Angriffe durch NPC-Gruppen auslöst.
- [x] **Dynamisches Quest- & Logbuch-System (`src/quests.py`)**: Implementiere ein `Quest`-System mit Zustandsmaschinen (Verfügbar, Aktiv, Abgeschlossen, Fehlschlagen), das über Events aus `src/combat.py` (Monster besiegen), `src/economy.py` (Items sammeln/handeln) und `src/dungeon.py` (Sektoren betreten) automatisch Fortschritt trackingt; integriere Belohnungen (Gold, Items, Reputation via `src/factions.py`), die deterministisch berechnet werden und in `src/persistence.py` serialisiert werden, sowie ein `QuestLog`, das den Spieler über aktive Ziele und verpasste
- [x] **Dynamisches NPC-Interaktions‑ & Dialogsystem (`src/npc_interaction.py`)**: Implementiere ein umfassendes System für NPC‑Verhalten und kontextbasierte Dialog
