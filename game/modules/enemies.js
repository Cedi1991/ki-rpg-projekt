// Gegner: verfolgen den Spieler und verursachen Kontaktschaden.
const KINDS = {
  slime:    { hp: 30, speed: 1.2, damage: 6, xp: 20, color: 0x22c55e, size: 0.3 },
  skeleton: { hp: 45, speed: 1.8, damage: 9, xp: 35, color: 0xe5e7eb, size: 0.35 },
};
const AGGRO = 7;
const HIT_DISTANCE = 0.7;

export default {
  id: 'enemies',
  init(ctx) {
    const { THREE, scene } = ctx;
    ctx.enemies = [];
    let spawnTimer = 0;

    ctx.spawnEnemy = (x, z, kind = 'slime') => {
      const cfg = KINDS[kind] || KINDS.slime;
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(cfg.size, 12, 10),
        new THREE.MeshStandardMaterial({ color: cfg.color, emissive: cfg.color, emissiveIntensity: 0.3 })
      );
      mesh.position.set(x, cfg.size, z);
      scene.add(mesh);
      const enemy = { mesh, kind, hp: cfg.hp, maxHp: cfg.hp, speed: cfg.speed, damage: cfg.damage, xp: cfg.xp, size: cfg.size, cd: 0 };
      ctx.enemies.push(enemy);
      return enemy;
    };

    ctx.removeEnemy = (enemy) => {
      scene.remove(enemy.mesh);
      const i = ctx.enemies.indexOf(enemy);
      if (i >= 0) ctx.enemies.splice(i, 1);
    };

    ctx.spawnEnemy(4, -4, 'slime');
    ctx.spawnEnemy(-4, 4, 'slime');
    ctx.spawnEnemy(4, 4, 'slime');

    this._timer = () => spawnTimer;
    this._setTimer = (v) => { spawnTimer = v; };
  },
  update(ctx, dt) {
    const p = ctx.player;
    if (!p || ctx.state.dead) return;

    // Nachschub: alle 6 s ein neuer Gegner, bis zu 2 + Level (max. 8).
    this._setTimer(this._timer() + dt);
    if (this._timer() > 6 && ctx.enemies.length < Math.min(8, 2 + ctx.state.level)) {
      this._setTimer(0);
      const edge = ctx.bounds - 0.7;
      const side = ctx.rand() < 0.5 ? -1 : 1;
      const along = (ctx.rand() * 2 - 1) * edge;
      const x = ctx.rand() < 0.5 ? side * edge : along;
      const z = x === along ? side * edge : along;
      ctx.spawnEnemy(x, z, ctx.state.level >= 2 && ctx.rand() < 0.4 ? 'skeleton' : 'slime');
    }

    for (const e of ctx.enemies) {
      const dx = p.group.position.x - e.mesh.position.x;
      const dz = p.group.position.z - e.mesh.position.z;
      const dist = Math.hypot(dx, dz);
      e.cd = Math.max(0, e.cd - dt);

      if (dist < AGGRO && dist > HIT_DISTANCE * 0.8) {
        e.mesh.position.x += (dx / dist) * e.speed * dt;
        e.mesh.position.z += (dz / dist) * e.speed * dt;
      }
      e.mesh.position.y = e.size + Math.abs(Math.sin(ctx.time * 4 + e.size * 10)) * 0.1;

      if (dist <= HIT_DISTANCE && e.cd === 0) {
        ctx.state.hp = Math.max(0, ctx.state.hp - e.damage);
        e.cd = 1;
        ctx.emit('player:hit', { damage: e.damage });
      }
    }
  },
  selfTest(ctx) {
    const before = ctx.enemies.length;
    const e = ctx.spawnEnemy(1, 1, 'slime');
    if (ctx.enemies.length !== before + 1) throw new Error('spawnEnemy funktioniert nicht');
    ctx.removeEnemy(e);
    if (ctx.enemies.length !== before) throw new Error('removeEnemy funktioniert nicht');
    return true;
  },
};