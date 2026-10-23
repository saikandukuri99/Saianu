// Deterministic keyframe engine: every visual is a pure function of time t (seconds),
// so any frame can be rendered independently (After Effects-style comp, written in code).
'use strict';
const W = 1920, H = 1080;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, p) => a + (b - a) * p;
const Ease = {
  lin: p => p,
  out2: p => 1 - (1 - p) * (1 - p),
  out3: p => 1 - Math.pow(1 - p, 3),
  out4: p => 1 - Math.pow(1 - p, 4),
  in2: p => p * p,
  in3: p => p * p * p,
  inOut3: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2,
  inOut5: p => p < .5 ? 16 * p ** 5 : 1 - Math.pow(-2 * p + 2, 5) / 2,
  outExpo: p => p >= 1 ? 1 : 1 - Math.pow(2, -10 * p),
  outBack: p => { const c1 = 1.55, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
};
// progress of a tween starting at a lasting d
const prog = (t, a, d, e = Ease.out3) => e(clamp((t - a) / d));

function $(sel, root = document) { return root.querySelector(sel); }
function $$(sel, root = document) { return [...root.querySelectorAll(sel)]; }
function el(html) { const d = document.createElement('div'); d.innerHTML = html.trim(); return d.firstElementChild; }

// fx: element enters at `at` (from -> rest) and optionally leaves at `out` (rest -> to).
// Props: o (opacity), x, y, s (scale), sx, sy, r (deg), blur (px), z (translateZ px)
function fx(e, t, o) {
  if (!e) return;
  const pin = o.at === undefined ? 1 : prog(t, o.at, o.dur ?? .8, o.ease ?? Ease.out3);
  const pout = o.out === undefined ? 0 : prog(t, o.out, o.outDur ?? .6, o.outEase ?? Ease.in2);
  const f = o.from || {}, to = o.to || {};
  const v = k => {
    const rest = k === 'o' || k === 's' || k === 'sx' || k === 'sy' ? 1 : 0;
    const a = f[k] ?? (k === 'o' ? 0 : rest), b = to[k] ?? (k === 'o' ? 0 : rest);
    return lerp(lerp(a, rest, pin), b, pout);
  };
  const op = v('o') * (o.max ?? 1);
  e.style.opacity = op.toFixed(4);
  e.style.visibility = op < 0.002 ? 'hidden' : 'visible';
  const s = v('s');
  e.style.transform = `${o.base || ''} translate3d(${v('x').toFixed(2)}px,${v('y').toFixed(2)}px,${v('z').toFixed(2)}px) scale(${(s * v('sx')).toFixed(4)},${(s * v('sy')).toFixed(4)}) rotate(${v('r').toFixed(3)}deg)`;
  const b = v('blur');
  e.style.filter = b > 0.05 ? `blur(${b.toFixed(2)}px)` : '';
  return op;
}

// Split text into word spans for per-word reveals.
function splitWords(e) {
  const walk = n => {
    [...n.childNodes].forEach(c => {
      if (c.nodeType === 3) {
        const frag = document.createDocumentFragment();
        c.textContent.split(/(\s+)/).forEach(w => {
          if (!w) return;
          if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(' ')); return; }
          const s = document.createElement('span'); s.className = 'w'; s.textContent = w; frag.appendChild(s);
        });
        c.replaceWith(frag);
      } else if (c.nodeType === 1 && !c.classList.contains('w')) walk(c);
    });
  };
  walk(e);
  return $$('.w', e);
}
// words rise in from blur, staggered
function wordsIn(words, t, at, opt = {}) {
  const st = opt.stagger ?? .07, d = opt.dur ?? .7;
  words.forEach((w, i) => fx(w, t, {
    at: at + i * st, dur: d, ease: Ease.out4,
    from: { o: 0, y: opt.y ?? 34, blur: opt.blur ?? 10, s: opt.s ?? 1 },
    out: opt.out, outDur: opt.outDur ?? .5, to: { o: 0, y: opt.outY ?? -20, blur: 8 },
  }));
}

// Highlight pill (blue bar wipes in, then text reveals left->right)
function pillIn(p, t, at, out) {
  const bar = $('.bar', p), tx = $('.tx', p);
  const a = prog(t, at, .55, Ease.outExpo), b = prog(t, at + .18, .75, Ease.out3);
  const o = out === undefined ? 1 : 1 - prog(t, out, .5, Ease.in2);
  p.style.opacity = o; p.style.visibility = o < .002 || a <= 0 ? 'hidden' : 'visible';
  bar.style.transform = `scaleX(${a})`;
  tx.style.clipPath = `inset(-20% ${(100 - b * 100).toFixed(2)}% -20% 0)`;
}

// SVG path draw-on (paths need pathLength="1")
function draw(path, t, at, dur = .9, e = Ease.inOut3, out, outDur = .5) {
  const p = prog(t, at, dur, e);
  const o = out === undefined ? 1 : 1 - prog(t, out, outDur, Ease.in2);
  path.style.strokeDashoffset = (1 - p).toFixed(4);
  path.style.opacity = (p > 0 ? 1 : 0) * o;
}

// Counter text
function count(e, t, at, dur, to, fmt = v => Math.round(v).toLocaleString('en-US')) {
  e.textContent = fmt(to * prog(t, at, dur, Ease.out3));
}
// typewriter
function type(e, t, at, cps, text, caret = true) {
  const n = Math.floor(clamp((t - at) * cps, 0, text.length));
  const blink = caret && t >= at - .4 && (n < text.length || Math.floor(t * 2) % 2 === 0) && t < at + text.length / cps + 1.2;
  e.innerHTML = escapeHtml(text.slice(0, n)) + (blink ? '<span class="caret"></span>' : '');
}
// decode/scramble text (glitch reveal)
const GLYPHS = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789_#$%';
function scramble(e, t, at, dur, text) {
  const p = clamp((t - at) / dur);
  if (t < at) { e.textContent = ''; return; }
  let s = '';
  for (let i = 0; i < text.length; i++) {
    const ci = i / text.length;
    if (text[i] === ' ' || p > ci * .7 + .3) s += text[i];
    else s += GLYPHS[(Math.floor(t * 24) * 7 + i * 13) % GLYPHS.length];
  }
  e.textContent = s;
}
function escapeHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

// Point along an SVG path for flowing pulses
function pulse(dot, path, t, at, period, phase = 0, alpha = 1) {
  if (t < at) { dot.style.opacity = 0; return; }
  const L = path.getTotalLength();
  const f = ((t - at) / period + phase) % 1;
  const pt = path.getPointAtLength(f * L);
  dot.setAttribute('cx', pt.x); dot.setAttribute('cy', pt.y);
  dot.style.opacity = (Math.sin(f * Math.PI) * alpha * prog(t, at, .4)).toFixed(3);
}

// seeded RNG
function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

// ---------------------------------------------------------------- background
const BG = (() => {
  const cv = document.getElementById('bg');
  const DPR = window.devicePixelRatio || 1;
  cv.width = W * DPR; cv.height = H * DPR;
  const g = cv.getContext('2d');
  const R = rng(20260);
  const COLS = [[0, 136, 207], [238, 36, 36], [92, 120, 255], [0, 160, 230], [238, 36, 36], [120, 96, 230]];
  const nodes = [];
  for (let i = 0; i < 120; i++) {
    nodes.push({
      x: R() * 2300 - 190, y: R() * 1400 - 160, z: .45 + R() * .85,
      vx: (R() - .5) * 7, vy: (R() - .5) * 5, ph: R() * 6.28, amp: 10 + R() * 22, c: COLS[Math.floor(R() * COLS.length)],
      tw: R() * 6.28,
    });
  }
  // soft glow sprite
  const sprite = (rgb, size) => {
    const c = document.createElement('canvas'); c.width = c.height = size;
    const x = c.getContext('2d'), gr = x.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    gr.addColorStop(0, `rgba(${rgb},1)`); gr.addColorStop(.25, `rgba(${rgb},.35)`); gr.addColorStop(1, `rgba(${rgb},0)`);
    x.fillStyle = gr; x.fillRect(0, 0, size, size); return c;
  };
  const SP = {}; COLS.forEach(c => SP[c.join()] = sprite(c.join(), 64));
  // static dither to fight banding in the big gradients
  const noise = document.createElement('canvas'); noise.width = noise.height = 256;
  { const x = noise.getContext('2d'), id = x.createImageData(256, 256), r = rng(7);
    for (let i = 0; i < id.data.length; i += 4) { const v = r() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 10; }
    x.putImageData(id, 0, 0); }
  const np = g.createPattern(noise, 'repeat');

  const state = { net: 1, glow: 1, focusX: 960, focusY: 540, black: 0 };
  function radial(x, y, r, rgb, a) {
    const gr = g.createRadialGradient(x, y, 0, x, y, r);
    gr.addColorStop(0, `rgba(${rgb},${a})`); gr.addColorStop(.5, `rgba(${rgb},${a * .35})`); gr.addColorStop(1, `rgba(${rgb},0)`);
    g.fillStyle = gr; g.fillRect(0, 0, W, H);
  }
  function render(t) {
    g.setTransform(DPR, 0, 0, DPR, 0, 0);
    const base = g.createLinearGradient(0, 0, W * .3, H);
    base.addColorStop(0, '#0a0826'); base.addColorStop(.55, '#08061d'); base.addColorStop(1, '#050414');
    g.fillStyle = base; g.fillRect(0, 0, W, H);
    const k = state.glow;
    radial(960 + Math.sin(t * .11) * 120, 520 + Math.cos(t * .09) * 60, 980, '48,38,123', .78 * k);           // indigo #30267b
    radial(180 + Math.sin(t * .13) * 90, 60 + Math.cos(t * .1) * 50, 880, '0,136,207', .30 * k);            // blue  #0088cf
    radial(1780 + Math.cos(t * .12) * 90, 1060 + Math.sin(t * .08) * 40, 820, '238,36,36', .24 * k);        // red   #ee2424
    radial(state.focusX, state.focusY, 520, '0,136,207', .07 * k);

    // AI network
    const P = nodes.map(n => {
      let x = n.x + n.vx * t + Math.sin(t * .35 + n.ph) * n.amp, y = n.y + n.vy * t + Math.cos(t * .29 + n.ph) * n.amp;
      x = ((x + 200) % 2320 + 2320) % 2320 - 200; y = ((y + 180) % 1440 + 1440) % 1440 - 180;
      // gentle parallax / depth around frame centre
      x = 960 + (x - 960) * (1 + (n.z - .9) * .06 * Math.sin(t * .05));
      return { x, y, n };
    });
    const net = state.net, MAXD = 215;
    g.lineWidth = 1;
    for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) {
      const a = P[i], b = P[j], dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
      if (d2 > MAXD * MAXD) continue;
      const d = Math.sqrt(d2), al = (1 - d / MAXD) * .26 * net * Math.min(a.n.z, b.n.z);
      if (al < .004) continue;
      const lg = g.createLinearGradient(a.x, a.y, b.x, b.y);
      lg.addColorStop(0, `rgba(${a.n.c},${al})`); lg.addColorStop(1, `rgba(${b.n.c},${al})`);
      g.strokeStyle = lg; g.lineWidth = .6 + a.n.z * .5;
      g.beginPath(); g.moveTo(a.x, a.y); g.lineTo(b.x, b.y); g.stroke();
      // data pulses travelling along some links
      if ((i * 31 + j * 17) % 7 === 0) {
        const f = ((t * (.22 + ((i + j) % 5) * .05)) + i * .137) % 1;
        const px = a.x + (b.x - a.x) * f, py = a.y + (b.y - a.y) * f;
        g.globalAlpha = Math.sin(f * Math.PI) * .55 * net * Math.min(1, al * 9);
        g.drawImage(SP[a.n.c.join()], px - 9, py - 9, 18, 18);
        g.globalAlpha = 1;
      }
    }
    for (const p of P) {
      const tw = .55 + .45 * Math.sin(t * 1.3 + p.n.tw);
      const s = 5 + p.n.z * 8;
      g.globalAlpha = .55 * net * p.n.z * tw;
      g.drawImage(SP[p.n.c.join()], p.x - s, p.y - s, s * 2, s * 2);
      g.globalAlpha = .7 * net * p.n.z;
      g.fillStyle = `rgb(${p.n.c})`;
      g.beginPath(); g.arc(p.x, p.y, .9 + p.n.z * 1.1, 0, 6.283); g.fill();
    }
    g.globalAlpha = 1;
    // vignette
    const v = g.createRadialGradient(960, 540, 420, 960, 540, 1250);
    v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(2,1,10,.72)');
    g.fillStyle = v; g.fillRect(0, 0, W, H);
    g.fillStyle = np; g.fillRect(0, 0, W, H);
    if (state.black > 0) { g.fillStyle = `rgba(0,0,0,${state.black})`; g.fillRect(0, 0, W, H); }
  }
  return { render, state };
})();
