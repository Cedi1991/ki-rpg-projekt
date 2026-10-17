// Spielfigur + Tippen-zum-Laufen.
export default {
  id: 'player',
  init(ctx) {
    const { THREE, scene } = ctx;
    const group = new THREE.Group();
    const armor = new THREE.MeshStandardMaterial({ color: 0x111827, metalness: 0.95, roughness: 0.2 });

    const torso = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.65, 0.3), armor);
    torso.position.y = 0.5;
    group.add(torso);
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.32, 0.32), armor);
    head.position.y = 0.95;
    group.add(head);
    const visor = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.06, 0.35), new THREE.MeshBasicMaterial({ color: 0x38bdf8 }));
    visor.position.set(0, 0.98, 0);
    group.add(visor);
    const sword = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.1, 0.04), new THREE.MeshBasicMaterial({ color: 0x34d399 }));
    sword.position.set(0.45, 0.5, 0.25);
    sword.rotation.z = -0.3;
    group.add(sword);
    const aura = new THREE.Mesh(
      new THREE.RingGeometry(0.5, 0.7, 32),
      new THREE.MeshBasicMaterial({ color: 0x10b981, side: THREE.DoubleSide, transparent: true, opacity: 0.9 })
    );
    aura.rotation.x = -Math.PI / 2;
    aura.position.y = 0.03;
    group.add(aura);
    scene.add(group);

    // speedMul: andere Module (z. B. Wetter) dürfen das Tempo skalieren.
    ctx.player = { group, aura, speed: 3.4, speedMul: 1, target: null };

    const el = ctx.renderer.domElement;
    const ray = new THREE.Raycaster();
    const m = new THREE.Vector2();
    el.addEventListener('pointerdown', (e) => {
      if (!ctx.floor || ctx.state.dead) return;
      const r = el.getBoundingClientRect();
      m.x = ((e.clientX - r.left) / r.width) * 2 - 1;
      m.y = -((e.clientY - r.top) / r.height) * 2 + 1;
      ray.setFromCamera(m, ctx.camera);
      const hit = ray.intersectObject(ctx.floor)[0];
      if (hit) {
        const b = ctx.bounds - 0.5;
        ctx.player.target = new THREE.Vector3(
          Math.max(-b, Math.min(b, hit.point.x)), 0, Math.max(-b, Math.min(b, hit.point.z))
        );
      }
    });
  },
  update(ctx, dt) {
    const p = ctx.player;
    p.aura.rotation.z += 0.025;
    if (ctx.state.dead || !p.target) return;
    const pos = p.group.position;
    const dx = p.target.x - pos.x;
    const dz = p.target.z - pos.z;
    const dist = Math.hypot(dx, dz);
    const step = p.speed * p.speedMul * dt;
    if (dist <= step) {
      pos.x = p.target.x; pos.z = p.target.z; p.target = null;
    } else {
      pos.x += (dx / dist) * step;
      pos.z += (dz / dist) * step;
      p.group.rotation.y = Math.atan2(dx, dz);
    }
  },
  selfTest(ctx) {
    const p = ctx.player;
    p.group.position.set(0, 0, 0);
    p.target = new ctx.THREE.Vector3(2, 0, 2);
    ctx.step(120);
    const d = Math.hypot(p.group.position.x - 2, p.group.position.z - 2);
    p.target = null;
    p.group.position.set(0, 0, 0);
    if (d > 0.2) throw new Error('Spieler erreicht Ziel nicht (Abstand ' + d.toFixed(2) + ')');
    return true;
  },
};