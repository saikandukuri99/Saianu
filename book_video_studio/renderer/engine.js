'use strict';
// ---------------------------------------------------------------- basics
const W = 1920, H = 1080, NS = 'http://www.w3.org/2000/svg';
const $ = id => document.getElementById(id);
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (lt, a, b) => clamp((lt - a) / (b - a));
const E = {
  lin: t => t,
  out2: t => 1 - (1 - t) * (1 - t),
  out3: t => 1 - Math.pow(1 - t, 3),
  out5: t => 1 - Math.pow(1 - t, 5),
  in2: t => t * t,
  in3: t => t * t * t,
  inOut: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  backBig: t => { const c1 = 2.8, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  elastic: t => t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI) / 3) + 1,
  bounce: t => { const n = 7.5625, d = 2.75; if (t < 1 / d) return n * t * t; if (t < 2 / d) return n * (t -= 1.5 / d) * t + .75; if (t < 2.5 / d) return n * (t -= 2.25 / d) * t + .9375; return n * (t -= 2.625 / d) * t + .984375; },
};
// deterministic pseudo random
function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

function el(tag, attrs, parent) {
  const n = document.createElementNS(NS, tag);
  if (attrs) for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(n);
  return n;
}
const gnode = (parent, attrs) => el('g', attrs, parent);

// transform/opacity state per node
function T(n, p) {
  const s = n.__s || (n.__s = { x: 0, y: 0, s: 1, sx: null, sy: null, r: 0, o: 1 });
  for (const k in p) s[k] = p[k];
  const sx = s.sx == null ? s.s : s.sx, sy = s.sy == null ? s.s : s.sy;
  n.setAttribute('transform', `translate(${s.x.toFixed(2)} ${s.y.toFixed(2)}) rotate(${s.r.toFixed(2)}) scale(${(sx || 0.0001).toFixed(4)} ${(sy || 0.0001).toFixed(4)})`);
  n.setAttribute('opacity', clamp(s.o).toFixed(3));
  return n;
}

// ---------------------------------------------------------------- text
const FONT = {
  te: "'TeSans','Pop','Noto Color Emoji',sans-serif",
  serif: "'TeSerif','TeSans','Pop',serif",
  en: "'Pop','TeSans','Noto Color Emoji',sans-serif",
};
function txt(parent, s, o = {}) {
  const t = el('text', {
    x: o.x || 0, y: o.y || 0, 'font-size': o.size || 60, 'font-weight': o.weight || 700,
    fill: o.fill || '#fff', 'text-anchor': o.anchor || 'middle', 'font-family': FONT[o.font || 'te'],
  }, parent);
  if (o.stroke) { t.setAttribute('stroke', o.stroke); t.setAttribute('stroke-width', o.sw || 8); t.setAttribute('paint-order', 'stroke'); t.setAttribute('stroke-linejoin', 'round'); }
  if (o.ls) t.setAttribute('letter-spacing', o.ls);
  t.textContent = s;
  return t;
}
const _mc = {};
function tw(s, size, weight = 700, font = 'te') {
  const key = s + '|' + size + '|' + weight + '|' + font;
  if (_mc[key] != null) return _mc[key];
  const t = el('text', { 'font-size': size, 'font-weight': weight, 'font-family': FONT[font] }, $('measure'));
  t.textContent = s;
  const w = t.getComputedTextLength();
  t.remove();
  return (_mc[key] = w);
}
// text in a rounded pill; returns group (origin = pill center)
function pill(parent, s, o = {}) {
  const size = o.size || 44, padX = o.padX == null ? 34 : o.padX, h = o.h || size * 1.75;
  const w = tw(s, size, o.weight || 700, o.font || 'te') + padX * 2;
  const g = gnode(parent);
  el('rect', { x: -w / 2, y: -h / 2, width: w, height: h, rx: o.rx == null ? h / 2 : o.rx, fill: o.bg || '#fff', stroke: o.stroke || 'none', 'stroke-width': o.sw || 0, opacity: o.bgo == null ? 1 : o.bgo }, g);
  const t = txt(g, s, { size, fill: o.fill || '#111', weight: o.weight || 700, font: o.font || 'te', y: size * 0.36 });
  g.__w = w; g.__h = h; g.__t = t;
  return g;
}
// a row of separately animatable words, centered on x
function wordRow(parent, s, o = {}) {
  const size = o.size || 80, words = s.split(' ').filter(Boolean), gap = (o.gap == null ? .28 : o.gap) * size;
  const ws = words.map(w => tw(w, size, o.weight || 700, o.font || 'te'));
  const total = ws.reduce((a, b) => a + b, 0) + gap * (words.length - 1);
  const g = gnode(parent); let x = -total / 2; const nodes = [];
  words.forEach((w, i) => {
    const n = gnode(g); n.__x = x + ws[i] / 2;
    txt(n, w, { size, fill: o.fill || '#fff', weight: o.weight || 700, font: o.font || 'te', stroke: o.stroke, sw: o.sw, y: o.y || 0 });
    T(n, { x: n.__x, y: 0 });
    nodes.push(n); x += ws[i] + gap;
  });
  g.__words = nodes; g.__w = total;
  return g;
}

// ---------------------------------------------------------------- animation helpers
function pop(n, lt, t0, o = {}) {
  const d = o.d || .5, p = seg(lt, t0, t0 + d);
  if (p <= 0) return T(n, { o: 0, s: 0.0001, x: o.x == null ? (n.__s ? n.__s.x : 0) : o.x, y: o.y == null ? (n.__s ? n.__s.y : 0) : o.y });
  const k = (o.s == null ? 1 : o.s) * (o.big ? E.backBig(p) : E.back(p));
  const u = { s: k, o: Math.min(1, p * 4) };
  if (o.x != null) u.x = o.x; if (o.y != null) u.y = o.y; if (o.r != null) u.r = o.r;
  return T(n, u);
}
function rise(n, lt, t0, o = {}) {
  const d = o.d || .6, p = seg(lt, t0, t0 + d), e = E.out3(p);
  const bx = o.x == null ? 0 : o.x, by = o.y == null ? 0 : o.y;
  return T(n, { x: bx + (o.dx || 0) * (1 - e), y: by + (o.dy == null ? 50 : o.dy) * (1 - e), o: Math.min(1, p * 3), s: o.s == null ? 1 : o.s });
}
function fade(n, lt, t0, d = .4) { return T(n, { o: seg(lt, t0, t0 + d) }); }
function typeText(node, str, lt, t0, cps = 14) {
  const n = Math.floor(clamp((lt - t0) * cps, 0, str.length));
  node.textContent = str.slice(0, n);
  return n;
}
function pathLen(p) { if (p.__len == null) p.__len = p.getTotalLength(); return p.__len; }
function draw(p, k) { const L = pathLen(p); p.setAttribute('stroke-dasharray', L); p.setAttribute('stroke-dashoffset', (L * (1 - clamp(k))).toFixed(1)); }
const bob = (lt, amp = 8, f = 1.1, ph = 0) => Math.sin(lt * f * 2 * Math.PI + ph) * amp;

// ---------------------------------------------------------------- defs
const DEFS = $('defs');
function lgrad(id, stops, x1 = 0, y1 = 0, x2 = 0, y2 = 1) {
  const g = el('linearGradient', { id, x1, y1, x2, y2 }, DEFS);
  stops.forEach(([o, c, a]) => el('stop', { offset: o, 'stop-color': c, 'stop-opacity': a == null ? 1 : a }, g)); return g;
}
function rgrad(id, stops) {
  const g = el('radialGradient', { id }, DEFS);
  stops.forEach(([o, c, a]) => el('stop', { offset: o, 'stop-color': c, 'stop-opacity': a == null ? 1 : a }, g)); return g;
}
lgrad('gGold', [[0, '#FFE08A'], [1, '#F2A93B']]);
lgrad('gMint', [[0, '#6EF0B4'], [1, '#18B27A']]);
lgrad('gCoral', [[0, '#FF8A8A'], [1, '#E5384F']]);
lgrad('gSky', [[0, '#7FDBFF'], [1, '#2F7BFF']]);
lgrad('gViolet', [[0, '#B79CFF'], [1, '#6C3BE8']]);
lgrad('gWhite', [[0, '#FFFFFF'], [1, '#D9DEF2']]);
rgrad('gGlow', [[0, '#fff', .9], [1, '#fff', 0]]);
rgrad('gGlowGold', [[0, '#FFD66B', .85], [1, '#FFD66B', 0]]);
rgrad('gGlowCoral', [[0, '#FF5A6E', .8], [1, '#FF5A6E', 0]]);
rgrad('gGlowMint', [[0, '#4DF0B0', .8], [1, '#4DF0B0', 0]]);
rgrad('gGlowSky', [[0, '#5AB8FF', .8], [1, '#5AB8FF', 0]]);
rgrad('gVig', [[0.55, '#000', 0], [1, '#000', .55]]);
el('filter', { id: 'fShadow', x: '-30%', y: '-30%', width: '160%', height: '170%' }, DEFS).innerHTML =
  '<feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#000" flood-opacity=".38"/>';
el('filter', { id: 'fSoft', x: '-20%', y: '-20%', width: '140%', height: '150%' }, DEFS).innerHTML =
  '<feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#000" flood-opacity=".28"/>';

lgrad('gBustFade', [[0, '#fff'], [.74, '#fff'], [1, '#000']]);
el('mask', { id: 'mBust', maskUnits: 'userSpaceOnUse', x: -400, y: -500, width: 800, height: 520 }, DEFS).innerHTML =
  '<rect x="-400" y="-500" width="800" height="520" fill="url(#gBustFade)"/>';

// ---------------------------------------------------------------- themes + background
const THEMES = {
  night:   ['#0a0e30', '#2a1c70', '#FFC857'],
  dusk:    ['#1b0f33', '#63306f', '#FFB36B'],
  sepia:   ['#150f08', '#5b4228', '#E9C58B'],
  sunrise: ['#15235f', '#e2674a', '#FFE08A'],
  day:     ['#0d3563', '#27a9c4', '#FFE08A'],
  royal:   ['#190f4a', '#6b2fb3', '#FFD66B'],
  green:   ['#06262a', '#12766b', '#FFE08A'],
  crimson: ['#240a16', '#8a2145', '#FFC857'],
};
function hex(c) { return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)]; }
function mixc(a, b, t) { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], t))).join(',')})`; }

const BG = $('bg');
const bgGrad = lgrad('gBg', [[0, '#000'], [1, '#000']], 0, 0, .3, 1);
const bgStops = bgGrad.querySelectorAll('stop');
el('rect', { x: 0, y: 0, width: W, height: H, fill: 'url(#gBg)' }, BG);
const blobs = [0, 1, 2].map(i => el('circle', { r: 520 + i * 90, fill: 'url(#gGlow)', opacity: .12 }, BG));
const pr = rng(7);
const parts = Array.from({ length: 46 }, () => {
  const c = el('circle', { r: 2 + pr() * 5, fill: '#fff' }, BG);
  c.__p = { x: pr() * W, y: pr() * H, sp: 12 + pr() * 28, ph: pr() * 6.28, a: .12 + pr() * .3 };
  return c;
});
function updateBg(t, A, B, k) {
  const a = THEMES[A] || THEMES.night, b = THEMES[B] || THEMES.night;
  bgStops[0].setAttribute('stop-color', mixc(a[0], b[0], k));
  bgStops[1].setAttribute('stop-color', mixc(a[1], b[1], k));
  blobs.forEach((c, i) => {
    c.setAttribute('cx', 960 + Math.sin(t * .13 + i * 2.1) * 520);
    c.setAttribute('cy', 540 + Math.cos(t * .11 + i * 1.7) * 280);
    c.setAttribute('fill', i === 1 ? 'url(#gGlowGold)' : 'url(#gGlow)');
    c.setAttribute('opacity', i === 1 ? .10 : .09);
  });
  parts.forEach(c => {
    const p = c.__p;
    c.setAttribute('cx', (p.x + Math.sin(t * .4 + p.ph) * 40) % W);
    c.setAttribute('cy', ((p.y - t * p.sp) % H + H) % H);
    c.setAttribute('opacity', p.a * (.6 + .4 * Math.sin(t * 1.3 + p.ph)));
  });
}
function accent(themeName) { return (THEMES[themeName] || THEMES.night)[2]; }
