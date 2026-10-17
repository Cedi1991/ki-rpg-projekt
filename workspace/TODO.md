# Projekt-Roadmap: Modulares 3D-RPG & Wirtschaftssimulation

## Architektur-Vorgaben für die KI (WICHTIG)
- **Niemals modul.py bearbeiten!** Alle Änderungen müssen in den echten Modulen unter `src/` (z. B. `src/engine3d.py`, `src/core.py`, `src/economy.py`) vorgenommen werden.
- Jedes neue Feature wird als echtes Python-Modul implementiert.
- Alle Funktionen müssen deterministisch und testbar sein (mit pytest absichern in `tests/`).
- Bestehende Tests in `tests/` dürfen nicht fehlschlagen.
- Nach jedem todo eine neues todo erstellen und größer denken um einzigartig zu werden 

## Geplant (Offene Aufgaben)


- [x] **Erweiterte Magie-Effekte (`src/magic.py`)**: Implementiere ein Manasystem mit Elementarzaubern und Flächenschaden, das direkt mit `src/combat.py` und `src/core.py` interagiert.
- [ ] **Dynamisches Wettersystem (`src/weather.py`)**: Programmiere Wettereffekte wie Sturm und Nebel, die die Sichtweite im Dungeon und die Boss-KI beeinflussen.
- [ ] **Fraktions- und Rufsystem (`src/factions.py`)**: Erstelle ein System für NPC-Gilden und Fraktionen mit Rufpunkten und Händler-Rabatten.
- [ ] **Echtzeit-Wettersystem & Dynamischer Tag/Nacht-Zyklus (`src/weather.py`)**: Implementiere ein dynamisches Wettersystem (Regen, Sturm, Nebel), das die Sichtweite im Dungeon, die Bewegungsgeschwindigkeit des Spielers und das Angriffsverhalten von Boss-Gegnern in Echtzeit beeinflusst.
- [ ] **Künstliche Intelligenz für lebendige NPCs mit Gedächtnis (`src/npc_ai.py`)**: Programmiere ein verhaltensbasiertes NPC-System, bei dem Charaktere sich an frühere Interaktionen und Diebstähle des Spielers erinnern und basierend darauf Handelspreise oder Quests anpassen.
- [ ] **Prozedurales Fraktions- und Gilden-Netzwerk (`src/factions.py`)**: Erstelle ein komplexes System rivalisierender Fraktionen, in dem der Spieler durch Quests und Entscheidungen Rufpunkte sammelt, die weltweite Bündnisse und Territoriums-Kontrollen triggern.
- [ ] **Komplexes Alchemie- und Handwerkssystem (`src/crafting.py`)**: Entwickle eine Multimaterial-Crafting-Engine mit Rezept-Entdeckungen, Qualitätsstufen (Legendär, Episch) und physikbasierten Attributen für Waffen und Tränke.
- [ ] **Echtzeit-Netzwerk-Multiplayer-Protokoll (`src/multiplayer.py`)**: Baue ein Websocket-basiertes Synchronisationsprotokoll für mehrere Spieler im selben Dungeon inklusive Live-Chat und gemeinsamer Boss-Raids.
- [ ] **Prozedurales Musik- und Sound-Generierungssystem (`src/audio.py`)**: Implementiere einen algorithmischen Sound-Generator, der basierend auf dem aktuellen Spielerstatus und der Bedrohung im Dungeon dynamisch epische orchestrale Musiksequenzen erzeugt.



