# Roadmap

Format pro Zeile: `- [ ] modul-id | Titel | Beschreibung` (`[x]` erledigt, `[!]` übersprungen).
Die KI bearbeitet immer die oberste offene Aufgabe und baut sie als `game/modules/<modul-id>.js`.
Du kannst jederzeit eigene Aufgaben ergänzen oder die Reihenfolge ändern.

- [x] weather | Regen und Nebel | Wechselnde Wetterphasen: Regentropfen als Partikel (THREE.Points) und eine Nebeldichte, die sich langsam ändert (scene.fog.density). Bei Sturm sinkt ctx.player.speedMul auf 0.85, danach wieder 1.
- [!] boss | Boss-Gegner | Sobald der Spieler Level 3 erreicht, erscheint einmalig ein großer Boss (viel HP, langsam, hoher Schaden) mit einer HP-Leiste über dem Kopf. Sieg gibt viel XP und Gold.
- [x] minimap | Minimap | Eine kleine 2D-Karte (Canvas, oben rechts im Spielfeld-Container eingeblendet) zeigt Spieler, Gegner, Truhen und Kristalle als Punkte.
- [x] savegame | Spielstand speichern | Gold, XP, Level und Max-HP werden alle 5 Sekunden in localStorage (Schlüssel kirpg_save) gespeichert und beim Start geladen.
- [!] floating-text | Schadenszahlen | Beim Treffer erscheinen kurz aufsteigende Zahlen (Sprites) über Gegnern und Spieler, die nach einer Sekunde verschwinden.
- [ ] torches | Fackeln und Licht | Mehrere flackernde Punktlichter (THREE.PointLight) an den Wänden, die atmosphärisch pulsieren, mit maximal 4 Lichtern wegen Handy-Leistung.
- [ ] trap-system | Fallen & Trigger | Fügt im Dungeon zufällig platzierte Fallen hinzu, die bei Betreten Schaden, Betäubung oder Status‑Effekte auslösen und durch kleine Part
- [ ] ambient-sounds | Ambient Sounds | Spielumgebung erzeugt kontextabhängige Hintergrundgeräusche (Wasserplätschern, Wind, entfernte Monstergeräusche) die je nach Wetter und Gebiet variieren und die Immersion steigern.
- [ ] status-effects | Status‑Effekte | Fügt temporäre Zustände wie Gift, Betäubung oder Regeneration hinzu, die über Zeit auf Spieler und Gegner wirken und deren Attribute beeinflussen.
