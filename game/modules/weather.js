// game/modules/weather.js
export default {
  id: 'weather',
  init(ctx) {
    // ---- Fog ----
    this._origFog = ctx.scene.fog || null;
    const baseDensity = 0.0005;
    ctx.scene.fog = new ctx.THREE.FogExp2(0xaaaaaa, baseDensity);
    this._fogBase = baseDensity;

    // ---- Rain particles ----
    const count = 800;
    const positions = new Float32Array(count * 3);
    const bounds = ctx.bounds;
    for (let i = 0; i < count; i++) {
      const ix = i * 3;
      positions[ix] = (ctx.rand() * 2 - 1) * bounds;      // x
      positions[ix + 1] = ctx.rand() * bounds * 2;        // y (0..2*bounds)
      positions[ix + 2] = (ctx.rand() * 2 - 1) * bounds;  // z
    }
    const geom = new ctx.THREE.BufferGeometry();
    geom.setAttribute('position', new ctx.THREE.BufferAttribute(positions, 3));
    const mat = new ctx.THREE.PointsMaterial({
      color: 0xddddff,
      size: 0.1,
      transparent: true,
      opacity: 0.6,
      depthWrite: false,
    });
    this._rain = new ctx.THREE.Points(geom, mat);
    ctx.scene.add(this._rain);

    // ---- Storm state ----
    this._storm = {
      active: false,
      timer: 0,
      cooldown: 30 + ctx.rand() * 30, // 30‑60 s until first storm
      duration: 12,                    // seconds
      playerSpeedBackup: 1,
    };
  },

  update(ctx, dt) {
    // ---- Rain animation ----
    const geom = this._rain.geometry;
    const pos = geom.attributes.position.array;
    const count = pos.length / 3;
    const fallSpeed = 30; // units per second
    const bounds = ctx.bounds;
    for (let i = 0; i < count; i++) {
      const ix = i * 3;
      pos[ix + 1] -= fallSpeed * dt;
      if (pos[ix + 1] < 0) {
        pos[ix] = (ctx.rand() * 2 - 1) * bounds;
        pos[ix + 1] = bounds * 2;
        pos[ix + 2] = (ctx.rand() * 2 - 1) * bounds;
      }
    }
    geom.attributes.position.needsUpdate = true;

    // ---- Fog density oscillation ----
    const time = ctx.time;
    const fog = ctx.scene.fog;
    const oscill = Math.sin(time * 0.07) * 0.0003;
    fog.density = this._fogBase + oscill + (this._storm.active ? 0.0007 : 0);

    // ---- Storm handling ----
    const s = this._storm;
    if (s.active) {
      s.timer -= dt;
      if (s.timer <= 0) {
        // end storm
        s.active = false;
        ctx.player.speedMul = s.playerSpeedBackup;
        s.cooldown = 30 + ctx.rand() * 30;
      }
    } else {
      s.cooldown -= dt;
      if (s.cooldown <= 0) {
        // start storm
        s.active = true;
        s.timer = s.duration;
        s.playerSpeedBackup = ctx.player.speedMul;
        ctx.player.speedMul = 0.85;
      }
    }
  },

  selfTest(ctx) {
    // --- Setup ---
    this.init(ctx);
    if (!(ctx.scene.fog instanceof ctx.THREE.FogExp2)) return false;
    if (!this._rain || !(this._rain instanceof ctx.THREE.Points)) return false;

    // Force immediate storm
    this._storm.cooldown = 0;
    ctx.step(1); // one frame -> storm should start
    if (Math.abs(ctx.player.speedMul - 0.85) > 0.001) return false;

    // Simulate storm duration + a bit
    const steps = Math.ceil((this._storm.duration + 1) / (1 / 60));
    ctx.step(steps);
    if (Math.abs(ctx.player.speedMul - 1) > 0.001) return false;

    // --- Cleanup ---
    ctx.scene.remove(this._rain);
    if (this._origFog) ctx.scene.fog = this._origFog;
    else ctx.scene.fog = null;
    return true;
  },
};
