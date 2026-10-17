# Modul-API (wird der KI bei jeder Aufgabe mitgegeben)

Jedes Feature ist EINE Datei `game/modules/<id>.js` mit genau diesem Aufbau:

```js
export default {
  id: '<id>',                 // muss dem Dateinamen entsprechen
  init(ctx) { /* Objekte anlegen, Events abonnieren */ },
  update(ctx, dt) { /* jeden Frame, dt in Sekunden */ },
  selfTest(ctx) { /* wirft einen Fehler oder gibt false zurück, wenn das Feature nicht funktioniert; sonst true */ },
};
```

Keine `import`-Anweisungen. Three.js kommt über `ctx.THREE`.
In `init` nur auf Felder zugreifen, die garantiert existieren (siehe unten). Alles andere erst in `update`.

## Garantiert in `init` vorhanden
- `ctx.THREE`, `ctx.scene`, `ctx.camera`, `ctx.renderer`, `ctx.container`
- `ctx.state` = `{ hp, maxHp, gold, xp, level, dead }` (frei erweiterbar)
- `ctx.bounds` (Spielfeld reicht von -bounds bis +bounds in x und z, Boden liegt bei y=0)
- `ctx.rand()` (seeded Zufall 0..1, im Test deterministisch; NIE `Math.random` benutzen)
- `ctx.on(event, fn)`, `ctx.emit(event, data)`, `ctx.log(text)`
- `ctx.step(n)` simuliert n Frames (nur für `selfTest`)
- `ctx.time` (Sekunden seit Start)

## Von anderen Modulen (vor deinem geladen)
- `ctx.floor` (Mesh des Bodens), `ctx.player` = `{ group, aura, speed, speedMul, target }`
  - `ctx.player.group.position` ist die Position; `speedMul` darf zur Tempo-Änderung gesetzt werden
- `ctx.enemies` (Array) mit Einträgen `{ mesh, kind, hp, maxHp, speed, damage, xp, size, cd }`
  - `ctx.spawnEnemy(x, z, kind)` (kind: 'slime' | 'skeleton'), `ctx.removeEnemy(enemy)`
- `ctx.pickups` (Array), `ctx.spawnChest(x, z, gold)`, `ctx.spawnCrystal(x, z, heal, color)`

## Events
`log`, `player:hit {damage}`, `player:dead`, `player:respawn`, `player:levelup {level}`,
`enemy:hit {enemy}`, `enemy:killed {enemy}`, `pickup {type}`

## Regeln
- Nur die eigene Moduldatei ändern. Andere Module nie überschreiben.
- Räume im `update` nach, was du erzeugst (Meshes entfernen, wenn nicht mehr gebraucht).
- Keine Netzwerkzugriffe (`fetch`, `XMLHttpRequest`, `WebSocket`), kein `eval`/`new Function`/`import()`.
- `localStorage` nur mit Schlüsseln, die mit `kirpg_` beginnen, immer in try/catch.
- Das Spielfeld ist klein und läuft auf dem Handy: wenige Meshes, keine schweren Shader.
- `selfTest` muss das Feature wirklich prüfen (nicht einfach `return true`) und den Spielzustand danach halbwegs sauber hinterlassen.