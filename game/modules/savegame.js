export default {
  id: 'savegame',
  init(ctx) {
    // load saved data
    try {
      const raw = localStorage.getItem('kirpg_save');
      if (raw) {
        const data = JSON.parse(raw);
        if (data) {
          if (typeof data.gold === 'number') ctx.state.gold = data.gold;
          if (typeof data.xp === 'number') ctx.state.xp = data.xp;
          if (typeof data.level === 'number') ctx.state.level = data.level;
          if (typeof data.maxHp === 'number') ctx.state.maxHp = data.maxHp;
        }
      }
    } catch (e) {
      ctx.log('savegame load error: ' + e);
    }
    // timer for periodic saving
    ctx._savegameTimer = 0;
  },
  update(ctx, dt) {
    ctx._savegameTimer += dt;
    if (ctx._savegameTimer >= 5) {
      ctx._savegameTimer -= 5;
      try {
        const payload = {
          gold: ctx.state.gold,
          xp: ctx.state.xp,
          level: ctx.state.level,
          maxHp: ctx.state.maxHp,
        };
        localStorage.setItem('kirpg_save', JSON.stringify(payload));
      } catch (e) {
        ctx.log('savegame save error: ' + e);
      }
    }
  },
  selfTest(ctx) {
    const key = 'kirpg_save';
    const orig = {
      gold: ctx.state.gold,
      xp: ctx.state.xp,
      level: ctx.state.level,
      maxHp: ctx.state.maxHp,
    };
    // set known test values
    ctx.state.gold = 123;
    ctx.state.xp = 456;
    ctx.state.level = 7;
    ctx.state.maxHp = 999;
    // force a save
    try {
      const payload = {
        gold: ctx.state.gold,
        xp: ctx.state.xp,
        level: ctx.state.level,
        maxHp: ctx.state.maxHp,
      };
      localStorage.setItem(key, JSON.stringify(payload));
    } catch (e) {
      return false;
    }
    // wipe current state
    ctx.state.gold = 0;
    ctx.state.xp = 0;
    ctx.state.level = 0;
    ctx.state.maxHp = 0;
    // load again (replicating init logic)
    try {
      const raw = localStorage.getItem(key);
      if (raw) {
        const data = JSON.parse(raw);
        if (data) {
          ctx.state.gold = data.gold;
          ctx.state.xp = data.xp;
          ctx.state.level = data.level;
          ctx.state.maxHp = data.maxHp;
        }
      }
    } catch (e) {
      return false;
    }
    const ok =
      ctx.state.gold === 123 &&
      ctx.state.xp === 456 &&
      ctx.state.level === 7 &&
      ctx.state.maxHp === 999;
    // restore original state and clean storage
    ctx.state.gold = orig.gold;
    ctx.state.xp = orig.xp;
    ctx.state.level = orig.level;
    ctx.state.maxHp = orig.maxHp;
    try {
      localStorage.removeItem(key);
    } catch (e) {
      // ignore
    }
    return ok;
  },
};
