// Spielkern: lädt die Module aus game/manifest.json und treibt die Spielschleife an.
// Ein kaputtes Modul darf NIE das ganze Spiel stoppen: Fehler werden pro Modul abgefangen.

const THREE = window.THREE;
const statusEl = document.getElementById('status');
const container = document.getElementById('webgl-container');

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const params = new URLSearchParams(location.search);
const testMode = params.has('test');
const handlers = {};

const ctx = {
  THREE,
  container,
  bounds: 5.5, // Spielfeld: x/z von -bounds bis +bounds
  state: { hp: 100, maxHp: 100, gold: 0, xp: 0, level: 1, dead: false },
  time: 0,
  running: !testMode,
  modules: [],
  errors: [],
  rand: mulberry32(testMode ? 12345 : Date.now()),
  on(evt, fn) { (handlers[evt] = handlers[evt] || []).push(fn); },
  emit(evt, data) {
    (handlers[evt] || []).forEach((fn) => {
      try { fn(data); } catch (e) { reportError('event:' + evt, e); }
    });
  },
  log(msg) { console.log('[game]', msg); ctx.emit('log', String(msg)); },
};

function reportError(name, err) {
  const message = String((err && err.message) || err);
  ctx.errors.push({ module: name, error: message });
  console.error('[game] Fehler in', name, err);
  if (statusEl) {
    statusEl.classList.add('error');
    statusEl.textContent = '⚠️ Fehler in ' + name + ': ' + message;
  }
}

function setupScene() {
  const w = container.clientWidth || 360;
  const h = container.clientHeight || 340;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x04060b);
  scene.fog = new THREE.FogExp2(0x04060b, 0.04);

  const d = 7;
  const aspect = w / h;
  const camera = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 0.1, 1000);
  camera.position.set(12, 14, 12);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(w, h);
  renderer.shadowMap.enabled = true;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.3;
  container.appendChild(renderer.domElement);

  window.addEventListener('resize', () => {
    const nw = container.clientWidth || w;
    const nh = container.clientHeight || h;
    const na = nw / nh;
    camera.left = -d * na; camera.right = d * na; camera.top = d; camera.bottom = -d;
    camera.updateProjectionMatrix();
    renderer.setSize(nw, nh);
  });

  ctx.scene = scene;
  ctx.camera = camera;
  ctx.renderer = renderer;
}

function tick(dt) {
  ctx.time += dt;
  for (const m of ctx.modules) {
    if (m.disabled || typeof m.update !== 'function') continue;
    try { m.update(ctx, dt); } catch (e) { m.disabled = true; reportError(m.id, e); }
  }
}

// Deterministisch vorspulen (für Tests): n Schritte à dt Sekunden, ohne Rendern.
ctx.step = (n = 1, dt = 1 / 60) => { for (let i = 0; i < n; i++) tick(dt); };

async function runSelfTests() {
  const results = [];
  for (const m of ctx.modules) {
    if (typeof m.selfTest !== 'function') { results.push({ id: m.id, ok: false, error: 'selfTest fehlt' }); continue; }
    try {
      const r = await m.selfTest(ctx);
      results.push({ id: m.id, ok: r !== false });
    } catch (e) {
      results.push({ id: m.id, ok: false, error: String((e && e.message) || e) });
    }
  }
  return results;
}

window.__game = { ctx, ready: false, runSelfTests };

async function boot() {
  if (!THREE) throw new Error('Three.js konnte nicht geladen werden');
  setupScene();

  const res = await fetch('game/manifest.json', { cache: 'no-store' });
  if (!res.ok) throw new Error('manifest.json nicht ladbar (' + res.status + ')');
  const manifest = await res.json();
  ctx.manifest = manifest;

  for (const id of manifest.modules) {
    try {
      const mod = (await import('./modules/' + id + '.js?v=' + (manifest.version || 0))).default;
      if (!mod || typeof mod.init !== 'function') throw new Error('Modul braucht einen default-Export mit init()');
      mod.id = mod.id || id;
      mod.init(ctx);
      ctx.modules.push(mod);
    } catch (e) {
      reportError(id, e);
    }
  }

  if (statusEl && ctx.errors.length === 0) {
    statusEl.textContent = '🤖 ' + ctx.modules.length + ' Module aktiv: ' + ctx.modules.map((m) => m.id).join(', ');
  }

  ctx.renderer.render(ctx.scene, ctx.camera);
  window.__game.ready = true;

  let last = performance.now();
  function loop(now) {
    requestAnimationFrame(loop);
    if (!ctx.running) return;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    tick(dt);
    ctx.renderer.render(ctx.scene, ctx.camera);
  }
  requestAnimationFrame(loop);
}

boot().catch((e) => { reportError('boot', e); window.__game.ready = true; });
