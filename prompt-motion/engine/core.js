/* Motor Prompt Motion — todo es una función pura del tiempo.
 *
 * Una composición HTML define:
 *   window.COMP = { width, height, fps, duration, bpm }
 *   window.seek = (t) => { ... }   // coloca TODA la pantalla en el instante t (segundos)
 *
 * Reglas: ninguna transición CSS, ningún temporizador, ningún estado guardado entre fotogramas.
 * El renderizador (render.mjs) llama a seek(t) en cada fotograma y captura la imagen.
 * En el navegador: vista previa automática en bucle (espacio = pausa, ←/→ = fotograma a fotograma).
 */
(function () {
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, p) => a + (b - a) * p;
  // progreso 0→1 de t entre a y b (limitado)
  const prog = (t, a, b) => clamp((t - a) / (b - a));

  // Easings (nunca lineal para un movimiento visible)
  const ease = {
    outExpo: (p) => (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p)),
    inExpo: (p) => (p <= 0 ? 0 : Math.pow(2, 10 * p - 10)),
    inOutCubic: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    outCubic: (p) => 1 - Math.pow(1 - p, 3),
    inOutQuint: (p) => (p < 0.5 ? 16 * p ** 5 : 1 - Math.pow(-2 * p + 2, 5) / 2),
  };

  // Spring de forma cerrada: respuesta al escalón de un muelle amortiguado, de 0 a 1, t en segundos.
  // Función pura del tiempo → determinista, se puede renderizar en cualquier orden.
  const SPRINGS = {
    snappy: { stiffness: 260, damping: 26, mass: 1 }, // overshoot mínimo
    smooth: { stiffness: 140, damping: 24, mass: 1 }, // sin overshoot visible
    soft: { stiffness: 90, damping: 20, mass: 1 },
    pop: { stiffness: 320, damping: 22, mass: 1 }, // pequeño rebote, para los "clics"
  };
  function spring(t, cfg = SPRINGS.snappy) {
    if (t <= 0) return 0;
    const { stiffness: k, damping: c, mass: m } = typeof cfg === "string" ? SPRINGS[cfg] : cfg;
    const w0 = Math.sqrt(k / m);
    const z = c / (2 * Math.sqrt(k * m));
    if (z < 1) {
      const wd = w0 * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + ((z * w0) / wd) * Math.sin(wd * t));
    }
    if (z === 1) return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
    const wh = w0 * Math.sqrt(z * z - 1);
    return 1 - Math.exp(-z * w0 * t) * (Math.cosh(wh * t) + ((z * w0) / wh) * Math.sinh(wh * t));
  }

  // Valor que cambia de objetivo varias veces = suma de un spring por cambio.
  //   track(t, 0, [[1.5, 360], [3, 120], [6, 360]], "snappy")
  function track(t, initial, keys, cfg = "snappy") {
    let v = initial;
    let prev = initial;
    for (const [at, target] of keys) {
      v += (target - prev) * spring(t - at, cfg);
      prev = target;
    }
    return v;
  }

  // Interpolación con varios keyframes y easing por tramo: keys = [[t, v], ...]
  function keyframes(t, keys, easing = ease.inOutCubic) {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [t1, v1] = keys[i];
      const [t0, v0] = keys[i - 1];
      if (t <= t1) return lerp(v0, v1, easing(prog(t, t0, t1)));
    }
    return keys[keys.length - 1][1];
  }

  // Rejilla de tempo
  const beats = (bpm) => ({
    beat: (n) => (n * 60) / bpm,
    bar: (n) => (n * 4 * 60) / bpm,
    // pulso 1→0 que cae después de cada tiempo (para "respirar" al ritmo)
    pulse: (t, decay = 8) => Math.exp(-decay * ((t % (60 / bpm)) / (60 / bpm))),
  });

  // Punto sobre una curva de Bézier cúbica (trayectorias de cursor naturales)
  function bezier(p, a, b, c, d) {
    const u = 1 - p;
    return [
      u * u * u * a[0] + 3 * u * u * p * b[0] + 3 * u * p * p * c[0] + p * p * p * d[0],
      u * u * u * a[1] + 3 * u * u * p * b[1] + 3 * u * p * p * c[1] + p * p * p * d[1],
    ];
  }

  const timecode = (t, fps) => {
    const f = Math.floor(t * fps);
    const s = Math.floor(f / fps);
    return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}:${String(f % fps).padStart(2, "0")}`;
  };

  const $ = (sel) => document.querySelector(sel);
  const css = (el, styles) => {
    if (typeof el === "string") el = $(el);
    if (el) Object.assign(el.style, styles);
  };

  window.PM = { clamp, lerp, prog, ease, spring, SPRINGS, track, keyframes, beats, bezier, timecode, $, css };

  // ---------- Vista previa en el navegador (desactivada durante el render) ----------
  window.addEventListener("load", () => {
    if (window.__RENDERING__ || !window.COMP || !window.seek) return;
    const { duration, fps } = window.COMP;
    let t = 0, playing = true, last = performance.now();
    const fit = () => {
      const s = Math.min(innerWidth / COMP.width, innerHeight / COMP.height);
      css(document.body, { transform: `scale(${s})`, transformOrigin: "0 0" });
    };
    fit();
    addEventListener("resize", fit);
    addEventListener("keydown", (e) => {
      if (e.code === "Space") playing = !playing;
      if (e.code === "ArrowRight") { playing = false; t = Math.min(duration, t + 1 / fps); }
      if (e.code === "ArrowLeft") { playing = false; t = Math.max(0, t - 1 / fps); }
      window.seek(t);
    });
    const loop = (now) => {
      if (playing) t = (t + (now - last) / 1000) % duration;
      last = now;
      window.seek(t);
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  });
})();
