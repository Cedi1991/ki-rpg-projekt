export default {
  id: 'minimap',
  init(ctx) {
    const size = 150;
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    canvas.style.position = 'absolute';
    canvas.style.top = '10px';
    canvas.style.right = '10px';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '1000';
    canvas.style.background = 'rgba(0,0,0,0.3)';
    canvas.style.border = '1px solid rgba(255,255,255,0.5)';
    ctx.container.appendChild(canvas);
    this.canvas = canvas;
    this.ctx2d = canvas.getContext('2d');
  },

  update(ctx, dt) {
    const { bounds, player, enemies, pickups } = ctx;
    const canvas = this.canvas;
    const ctx2d = this.ctx2d;
    if (!canvas || !ctx2d) return;

    const scale = canvas.width / (2 * bounds);
    ctx2d.clearRect(0, 0, canvas.width, canvas.height);
    ctx2d.fillStyle = 'rgba(0,0,0,0.2)';
    ctx2d.fillRect(0, 0, canvas.width, canvas.height);

    const draw = (pos, color, radius) => {
      const x = (pos.x + bounds) * scale;
      const y = (bounds - pos.z) * scale;
      ctx2d.beginPath();
      ctx2d.arc(x, y, radius, 0, Math.PI * 2);
      ctx2d.fillStyle = color;
      ctx2d.fill();
    };

    // player
    if (player && player.group && player.group.position) {
      draw(player.group.position, '#00f', 4);
    }

    // enemies
    if (Array.isArray(enemies)) {
      enemies.forEach(e => {
        if (e.mesh && e.mesh.position) draw(e.mesh.position, '#f00', 3);
      });
    }

    // pickups (chests, crystals)
    if (Array.isArray(pickups)) {
      pickups.forEach(p => {
        if (!p.mesh || !p.mesh.position) return;
        let col = '#fff';
        if (p.type === 'chest') col = '#ff0';
        else if (p.type === 'crystal') col = '#0ff';
        draw(p.mesh.position, col, 2);
      });
    }
  },

  selfTest(ctx) {
    if (!this.canvas || !this.canvas.parentNode) {
      throw new Error('Minimap canvas not created');
    }
    if (!ctx.player || !ctx.player.group || !ctx.player.group.position) {
      throw new Error('Player data missing');
    }
    // run a single update to ensure no runtime errors
    this.update(ctx, 0);
    if (this.canvas.width === 0 || this.canvas.height === 0) {
      throw new Error('Canvas has zero size');
    }
    return true;
  },
};
