// Anzeige: HP / Gold / XP / Level und die Konsole unter dem Spielfeld.
export default {
  id: 'hud',
  init(ctx) {
    const con = document.getElementById('console');
    ctx.on('log', (msg) => {
      if (!con) return;
      const line = document.createElement('div');
      line.textContent = '> ' + msg;
      con.appendChild(line);
      while (con.children.length > 40) con.removeChild(con.firstChild);
      con.scrollTop = con.scrollHeight;
    });
    this._last = {};
    ctx.log('Willkommen! Tippe aufs Spielfeld, um dich zu bewegen.');
  },
  update(ctx) {
    const s = ctx.state;
    const values = {
      hp: s.hp + '/' + s.maxHp,
      gold: String(s.gold),
      xp: s.xp + '/' + s.level * 100,
      level: String(s.level),
    };
    for (const [id, text] of Object.entries(values)) {
      if (this._last[id] === text) continue;
      this._last[id] = text;
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    }
  },
  selfTest(ctx) {
    ctx.step(1);
    const el = document.getElementById('gold');
    if (!el || el.textContent !== String(ctx.state.gold)) throw new Error('HUD zeigt Gold nicht korrekt an');
    return true;
  },
};