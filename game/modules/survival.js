// Tod und Wiederbelebung: nach 3 s zurück am Start, halbes Gold, Gegner werden zurückgesetzt.
export default {
  id: 'survival',
  init(ctx) {
    this._timer = 0;
  },
  update(ctx, dt) {
    const s = ctx.state;
    if (!s.dead && s.hp <= 0) {
      s.dead = true;
      this._timer = 3;
      ctx.log('Du bist gefallen … Wiederbelebung in 3 s');
      ctx.emit('player:dead', {});
      return;
    }
    if (!s.dead) return;

    this._timer -= dt;
    if (this._timer <= 0) {
      s.dead = false;
      s.hp = s.maxHp;
      s.gold = Math.floor(s.gold / 2);
      [...ctx.enemies].forEach((e) => ctx.removeEnemy(e));
      ctx.player.group.position.set(0, 0, 0);
      ctx.player.target = null;
      ctx.log('Wiederbelebt. Halbes Gold verloren.');
      ctx.emit('player:respawn', {});
    }
  },
  selfTest(ctx) {
    const s = ctx.state;
    s.gold = 100;
    s.hp = 0;
    ctx.step(1);
    if (!s.dead) throw new Error('Tod wird nicht erkannt');
    ctx.step(240);
    if (s.dead || s.hp !== s.maxHp) throw new Error('Wiederbelebung funktioniert nicht');
    if (s.gold !== 50) throw new Error('Goldverlust falsch: ' + s.gold);
    return true;
  },
};