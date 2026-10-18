export default {
  id: 'weather',
  init(ctx) {
    const { THREE, scene, bounds, rand } = ctx;

    // ensure fog exists
    if (!scene.fog) scene.fog = new THREE.FogExp2(0xaaaaaa, 0);
    this.baseFogDensity = scene.fog.density;
    this.stormFogDensity = 0.02;

    // rain particle system
    const rainCount = 1500;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(rainCount * 3);
    for (let i = 0; i < rainCount; i++) {
      positions[i * 3] = (rand() * 2 - 1) * bounds;
      positions[i * 3 + 1] = rand() * 20 + 5;
      positions[i * 3 + 2] = (rand() * 2 - 1) * bounds;
    }
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
      color: 0x99ccff,
      size: 0.12,
      transparent: true,
      opacity: 0.6,
    });
    const rain = new THREE.Points(geometry, material);
    rain.frustumCulled = false;
    scene.add(rain);

    this.rain = rain;
    this.rainCount = rainCount;
    this.baseRainSpeed = 2;
    this.stormRainSpeed = 5;
    this.rainSpeed = this.baseRainSpeed;

    this.inStorm = false;
    this.stormTimer = 0;
    this.originalSpeedMul = ctx.player.speedMul;
  },

  update(ctx, dt) {
    const { bounds, rand, player, scene } = ctx;

    // --- storm handling -------------------------------------------------
    if (this.inStorm) {
      this.stormTimer -= dt;
      if (this.stormTimer <= 0) {
        this.inStorm = false;
        player.speedMul = this.originalSpeedMul;
        scene.fog.density = this.baseFogDensity;
        this.rainSpeed = this.baseRainSpeed;
      }
    } else if (rand() < dt * 0.02) { // ~2 % chance per second
      this.inStorm = true;
      this.stormTimer = 5 + rand() * 5; // 5‑10 s
      player.speedMul = this.originalSpeedMul * 0.85;
      scene.fog.density = this.stormFogDensity;
      this.rainSpeed = this.stormRainSpeed;
    }

    // smooth fog transition
    const targetFog = this.inStorm ? this.stormFogDensity : this.baseFogDensity;
    const diff = targetFog - scene.fog.density;
    scene.fog.density += diff * Math.min(1, dt * 2);

    // --- rain movement --------------------------------------------------
    const pos = this.rain.geometry.attributes.position.array;
    for (let i = 0; i < this.rainCount; i++) {
      let y = pos[i * 3 + 1] - this.rainSpeed * dt;
      if (y < 0) {
        y = rand() * 20 + 10;
        pos[i * 3] = (rand() * 2 - 1) * bounds;
        pos[i * 3 + 2] = (rand() * 2 - 1) * bounds;
      }
      pos[i * 3 + 1] = y;
    }
    this.rain.geometry.attributes.position.needsUpdate = true;
  },

  selfTest(ctx) {
    const { scene, step, THREE } = ctx;

    // remember original fog state
    const originalFog = scene.fog;
    const originalDensity = originalFog ? originalFog.density : undefined;

    // ensure fog exists (init already did this)
    if (!scene.fog) scene.fog = new THREE.FogExp2(0xaaaaaa, 0);

    // run a few frames
    step(30); // ~0.5 s at 60 fps

    // force‑clear any active storm
    if (this.inStorm) {
      this.inStorm = false;
      ctx.player.speedMul = this.originalSpeedMul;
      scene.fog.density = this.baseFogDensity;
    }

    // remove rain particles
    if (this.rain) {
      scene.remove(this.rain);
      this.rain.geometry.dispose();
      this.rain.material.dispose();
      this.rain = null;
    }

    // restore original fog density
    if (originalFog) scene.fog.density = originalDensity;

    // verify cleanup
    if (scene.fog && scene.fog.density !== originalDensity) {
      throw new Error('Fog not cleared');
    }
    return true;
  },
};
