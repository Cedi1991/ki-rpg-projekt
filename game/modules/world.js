// Dungeon-Boden, Wände, Licht.
export default {
  id: 'world',
  init(ctx) {
    const { THREE, scene } = ctx;

    scene.add(new THREE.AmbientLight(0x1e293b, 2.0));
    const sun = new THREE.DirectionalLight(0x58a6ff, 2.5);
    sun.position.set(10, 20, 10);
    scene.add(sun);

    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(12, 12, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8, metalness: 0.2 })
    );
    floor.rotation.x = -Math.PI / 2;
    scene.add(floor);
    ctx.floor = floor;

    const grid = new THREE.GridHelper(12, 12, 0x10b981, 0x065f46);
    grid.position.y = 0.02;
    scene.add(grid);

    const wallMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.9 });
    const back = new THREE.Mesh(new THREE.BoxGeometry(12, 5, 0.6), wallMat);
    back.position.set(0, 2.5, -6);
    scene.add(back);
    const left = new THREE.Mesh(new THREE.BoxGeometry(0.6, 5, 12), wallMat);
    left.position.set(-6, 2.5, 0);
    scene.add(left);
  },
  selfTest(ctx) {
    if (!ctx.floor) throw new Error('ctx.floor fehlt');
    return true;
  },
};