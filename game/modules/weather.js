export default {
  id: 'weather',
  init(ctx) {
    // ---- Fog setup ---------------------------------------------------------
    if (!ctx.scene.fog) {
      ctx.scene.fog = new ctx.THREE.FogExp2(0xaaaaaa, 0);
    }
    // ---- Rain particle system -----------------------------------------------
    const rainCount = 800;
    const geom = new ctx.THREE.BufferGeometry();
    const positions = new Float32Array(rainCount * 3);
    const bounds = ctx.bounds;
    for (let i = 0; i < rainCount; i++) {
      const idx = i * 3;
      positions[idx] = (ctx.rand() * 2 - 1) * bounds;      // x
      positions[idx + 1] = ctx.rand() * 20 + 5;            // y (5‑25)
      positions[idx + 2] = (ctx.rand() * 2 - 1) * bounds;  // z
    }
    geom.setAttribute('position', new ctx.THREE.BufferAttribute(positions, 3));
    const mat = new ctx.THREE.PointsMaterial({
      color: 0xddddff,
      size: 0.12,
      transparent: true,
      opacity: 0.6,
      depthWrite: false,
    });
    const rain = new ctx.THREE.Points(geom, mat);
    rain.visible = false; // start hidden
    ctx.scene.add(rain);
    this.rain = rain;
    this.rainGeom = geom;
    this.rainPos = positions;
    this.rainCount = rainCount;

    // ---- Internal state ------------------------------------------------------
    this.phase = 'clear'; // clear → rain → fog → storm → repeat
    this.phaseTime = 0;
    this.phaseDur = {
      clear: 12,
      rain: 15,
      fog: 12,
      storm: 10,
    };
    this.targetFog = {
      clear: 0,
      rain: 0.002,
      fog: 0.008,
      storm: 0.015,
    };
    this.originalSpeedMul = ctx.player.speedMul;
  },

  update(ctx, dt) {
    // ---- Phase handling ------------------------------------------------------
    this.phaseTime += dt;
    if (this.phaseTime >= this.phaseDur[this.phase]) {
      // advance phase
      const order = ['clear', 'rain', 'fog', 'storm'];
      const idx = (order.indexOf(this.phase) + 1) % order.length;
      this.phase = order[idx];
      this.phaseTime = 0;
    }

    // ---- Fog interpolation ---------------------------------------------------
    const fog = ctx.scene.fog;
    const target = this.targetFog[this.phase];
    const diff = target - fog.density;
    fog.density += diff * dt * 0.5; // smooth change

    // ---- Rain visibility ------------------------------------------------------
    const showRain = this.phase === 'rain' || this.phase === 'storm';
    if (this.rain.visible !== showRain) this.rain.visible = showRain;

    // ---- Rain particle movement -----------------------------------------------
    if (showRain) {
      const pos = this.rainPos;
      const bounds = ctx.bounds;
      const fallSpeed = 12; // units per second
      for (let i = 0; i < this.rainCount; i++) {
        const idx = i * 3;
        pos[idx + 1] -= fallSpeed * dt;
        if (pos[idx + 1] < 0) {
          pos[idx] = (ctx.rand() * 2 - 1) * bounds;
          pos[idx + 1] = ctx.rand() * 20 + 10;
          pos[idx + 2] = (ctx.rand() * 2 - 1) * bounds;
        }
      }
      this.rainGeom.attributes.position.needsUpdate = true;
    }

    // ---- Storm speed effect ---------------------------------------------------
    if (this.phase === 'storm') {
      ctx.player.speedMul = 0.85;
    } else {
      // restore only if we changed it before
      if (ctx.player.speedMul !== this.originalSpeedMul) {
        ctx.player.speedMul = this.originalSpeedMul;
      }
    }
  },

  selfTest(ctx) {
    // Preserve original state
    const origFog = ctx.scene.fog ? ctx.scene.fog.density : 0;
    const origPhase = this.phase;
    const origPhaseTime = this.phaseTime;
    const origSpeedMul = ctx.player.speedMul;

    // Ensure fog object exists
    if (!ctx.scene.fog) ctx.scene.fog = new ctx.THREE.FogExp2(0xaaaaaa, 0);
    ctx.scene.fog.density = 0;

    // Force rain phase to test fog increase
    this.phase = 'rain';
    this.phaseTime = 0;

    // Simulate a few frames (approx 1 second)
    ctx.step(60);

    const increased = ctx.scene.fog.density > 0;
    // Restore state
    ctx.scene.fog.density = origFog;
    this.phase = origPhase;
    this.phaseTime = origPhaseTime;
    ctx.player.speedMul = origSpeedMul;

    if (!increased) throw new Error('fog not increased');
    return true;
  },
};
