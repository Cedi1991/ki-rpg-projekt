// Truhen (Gold + XP) und Heilkristalle. Beides respawnt nach einiger Zeit.
export default {
  id: 'loot',
  init(ctx) {
    const { THREE, scene } = ctx;
    ctx.pickups = [];
    const timers = { chest: 0, crystal: 0 };
    const rp = () => (ctx.rand() * 2 - 1) * (ctx.bounds - 1);

    ctx.spawnChest = (x, z, gold = 50) => {
      const g = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.4, 0.4), new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.5 }));
      body.position.y = 0.2;
      g.add(body);
      const lock = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.08), new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.8 }));
      lock.position.set(0, 0.2, 0.21);
      g.add(lock);
      g.position.set(x, 0, z);
      scene.add(g);
      const item = { type: 'chest', mesh: g, gold };
      ctx.pickups.push(item);
      return item;
    };

    ctx.spawnCrystal = (x, z, heal = 25, color = 0x34d399) => {
      const mesh = new THREE.Mesh(new THREE.OctahedronGeometry(0.25), new THREE.MeshBasicMaterial({ color }));
      mesh.position.set(x, 0.4, z);
      scene.add(mesh);
      const item = { type: 'crystal', mesh, heal };
      ctx.pickups.push(item);
      return item;
    };

    ctx.spawnChest(3.5, -3.5);
    ctx.spawnChest(-3.5, 2.5);
    ctx.spawnCrystal(4, -5, 25, 0x34d399);
    ctx.spawnCrystal(-4, -4, 25, 0x38bdf8);

    this._timers = timers;
    this._rp = rp;
  },
  update(ctx, dt) {
    const p = ctx.player;
    if (!p) return;
    const s = ctx.state;

    for (let i = ctx.pickups.length - 1; i >= 0; i--) {
      const it = ctx.pickups[i];
      if (it.type === 'crystal') {
        it.mesh.rotation.y += dt * 2;
        it.mesh.position.y = 0.4 + Math.sin(ctx.time * 3 + i) * 0.08;
      }
      if (s.dead) continue;
      const d = Math.hypot(p.group.position.x - it.mesh.position.x, p.group.position.z - it.mesh.position.z);
      if (d < 0.8) {
        if (it.type === 'chest') {
          s.gold += it.gold;
          s.xp += 30;
          ctx.log('Truhe geöffnet: +' + it.gold + ' Gold, +30 XP');
        } else {
          s.hp = Math.min(s.maxHp, s.hp + it.heal);
          ctx.log('Kristall: +' + it.heal + ' HP');
        }
        ctx.scene.remove(it.mesh);
        ctx.pickups.splice(i, 1);
        ctx.emit('pickup', { type: it.type });
      }
    }

    // Respawn, sobald von einer Sorte nichts mehr da ist.
    for (const type of ['chest', 'crystal']) {
      if (ctx.pickups.some((x) => x.type === type)) { this._timers[type] = 0; continue; }
      this._timers[type] += dt;
      if (this._timers[type] > 15) {
        this._timers[type] = 0;
        if (type === 'chest') { ctx.spawnChest(this._rp(), this._rp()); ctx.spawnChest(this._rp(), this._rp()); }
        else ctx.spawnCrystal(this._rp(), this._rp());
      }
    }
  },
  selfTest(ctx) {
    const pos = ctx.player.group.position;
    const goldBefore = ctx.state.gold;
    ctx.spawnChest(pos.x, pos.z, 50);
    ctx.step(2);
    if (ctx.state.gold < goldBefore + 50) throw new Error('Truhe gibt kein Gold');

    ctx.state.hp = Math.max(1, ctx.state.maxHp - 30);
    const hpBefore = ctx.state.hp;
    ctx.spawnCrystal(pos.x, pos.z, 25);
    ctx.step(2);
    if (ctx.state.hp <= hpBefore) throw new Error('Kristall heilt nicht');
    return true;
  },
};