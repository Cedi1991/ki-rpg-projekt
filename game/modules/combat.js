// Automatischer Nahkampf gegen den nächsten Gegner in Reichweite + Level-Up.
const RANGE = 1.6;
const COOLDOWN = 0.8;

export default {
  id: 'combat',
  init(ctx) {
    let cd = 0;
    this._cd = () => cd;
    this._setCd = (v) => { cd = v; };
  },
  update(ctx, dt) {
    const s = ctx.state;
    if (!ctx.player || !ctx.enemies) return;

    // Treffer-Blitz abklingen lassen
    for (const e of ctx.enemies) {
      const mat = e.mesh.material;
      mat.emissiveIntensity = Math.max(0.3, mat.emissiveIntensity - dt * 3);
    }
    if (s.dead) return;

    this._setCd(this._cd() - dt);
    if (this._cd() > 0) return;

    let best = null;
    let bestDist = RANGE;
    for (const e of ctx.enemies) {
      const d = Math.hypot(
        e.mesh.position.x - ctx.player.group.position.x,
        e.mesh.position.z - ctx.player.group.position.z
      );
      if (d < bestDist) { best = e; bestDist = d; }
    }
    if (!best) return;

    this._setCd(COOLDOWN);
    best.hp -= 12 + s.level * 3;
    best.mesh.material.emissiveIntensity = 1.6;
    ctx.emit('enemy:hit', { enemy: best });

    if (best.hp <= 0) {
      ctx.removeEnemy(best);
      const gold = 3 + Math.floor(ctx.rand() * 6);
      s.xp += best.xp;
      s.gold += gold;
      ctx.log('Gegner besiegt: +' + best.xp + ' XP, +' + gold + ' Gold');
      ctx.emit('enemy:killed', { enemy: best });
      while (s.xp >= s.level * 100) {
        s.xp -= s.level * 100;
        s.level += 1;
        s.maxHp += 10;
        s.hp = s.maxHp;
        ctx.log('Level ' + s.level + ' erreicht! Max-HP: ' + s.maxHp);
        ctx.emit('player:levelup', { level: s.level });
      }
    }
  },
  selfTest(ctx) {
    const s = ctx.state;
    const xpBefore = s.xp + s.level * 1000;
    const pos = ctx.player.group.position;
    const e = ctx.spawnEnemy(pos.x + 0.5, pos.z, 'slime');
    ctx.step(120);
    const killed = ctx.enemies.indexOf(e) === -1;
    if (!killed) ctx.removeEnemy(e);
    if (!killed) throw new Error('Gegner in Reichweite wurde nicht besiegt');
    if (s.xp + s.level * 1000 <= xpBefore) throw new Error('Kein XP-Gewinn nach Sieg');
    return true;
  },
};