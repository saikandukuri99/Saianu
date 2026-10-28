'use strict';
// Flat-style illustration assets. Every asset: fn(parent, opts) -> group centered on its own origin.
const A = {};
const R = (parent, x, y, w, h, fill, rx = 0, extra = {}) => el('rect', Object.assign({ x, y, width: w, height: h, rx, fill }, extra), parent);
const C = (parent, cx, cy, r, fill, extra = {}) => el('circle', Object.assign({ cx, cy, r, fill }, extra), parent);
const P = (parent, d, fill, extra = {}) => el('path', Object.assign({ d, fill }, extra), parent);
const L = (parent, x1, y1, x2, y2, stroke, w = 8, extra = {}) => el('line', Object.assign({ x1, y1, x2, y2, stroke, 'stroke-width': w, 'stroke-linecap': 'round' }, extra), parent);

// ------------------------------------------------------------ person (bust)
const SKIN = { light: ['#F2C7A5', '#E0A982'], tan: ['#D69A6B', '#BF7F52'], brown: ['#B9774A', '#9A5E36'], dark: ['#8A5530', '#6E4023'] };
A.person = (parent, o = {}) => {
  const sk = SKIN[o.skin || 'tan'], shirt = o.shirt || '#4C6FFF', shirt2 = o.shirt2 || '#3652D6', hairC = o.hairColor || '#1d1b24';
  const g = gnode(parent, { mask: 'url(#mBust)' }), parts = g.parts = {};
  // arms (behind body so they overlap nicely)
  const mkArm = (sgn) => {
    const a = gnode(g); T(a, { x: sgn * 104, y: -112 });
    L(a, 0, 0, 0, 92, shirt, 40);
    C(a, 0, 100, 21, sk[0]);
    return a;
  };
  parts.armL = mkArm(-1); parts.armR = mkArm(1);
  // body
  const body = gnode(g); parts.body = body;
  P(body, 'M -112 0 L -112 -58 Q -112 -132 -44 -142 L 44 -142 Q 112 -132 112 -58 L 112 0 Z', shirt);
  P(body, 'M -44 -142 Q 0 -108 44 -142 L 30 -150 L -30 -150 Z', shirt2);
  if (o.hoodie) { C(body, -34, -126, 9, '#fff', { opacity: .85 }); C(body, 34, -126, 9, '#fff', { opacity: .85 }); L(body, -34, -122, -34, -80, '#fff', 4, { opacity: .8 }); L(body, 34, -122, 34, -80, '#fff', 4, { opacity: .8 }); }
  if (o.tie) { P(body, 'M -12 -140 L 12 -140 L 18 -100 L 0 -70 L -18 -100 Z', o.tie); }
  if (o.kurta) { L(body, 0, -142, 0, -60, shirt2, 5); [-30, -48, -66].forEach(y => C(body, 0, y, 4, '#fff', { opacity: .9 })); }
  // neck + head
  R(g, -22, -170, 44, 40, sk[1], 14);
  const head = gnode(g); parts.head = head; T(head, { x: 0, y: -232 });
  if (o.hair === 'long' || o.hair === 'bun-long') P(head, 'M -76 8 Q -92 -90 0 -96 Q 92 -90 76 8 Q 70 40 40 48 L -40 48 Q -70 40 -76 8 Z', hairC);
  C(head, -62, 6, 14, sk[1]); C(head, 62, 6, 14, sk[1]);
  head.appendChild(el('ellipse', { cx: 0, cy: 0, rx: 64, ry: 72, fill: sk[0] }));
  // hair styles
  const hs = o.hair || 'short';
  if (hs === 'short') P(head, 'M -68 -6 Q -76 -88 0 -90 Q 76 -88 68 -6 Q 50 -52 0 -48 Q -50 -52 -68 -6 Z', hairC);
  if (hs === 'grey') { P(head, 'M -68 -4 Q -74 -84 0 -86 Q 74 -84 68 -4 Q 52 -44 0 -42 Q -52 -44 -68 -4 Z', '#D8D8E0'); P(head, 'M -68 6 Q -72 -10 -62 -22 L -62 14 Z', '#D8D8E0'); P(head, 'M 68 6 Q 72 -10 62 -22 L 62 14 Z', '#D8D8E0'); }
  if (hs === 'bald') { P(head, 'M -66 -2 Q -70 -26 -60 -38 L -60 8 Z', '#B9B9C6'); P(head, 'M 66 -2 Q 70 -26 60 -38 L 60 8 Z', '#B9B9C6'); }
  if (hs === 'cap') { P(head, 'M -70 -30 Q -74 -96 0 -98 Q 74 -96 70 -30 Z', o.capColor || '#FF5A5F'); P(head, 'M -74 -30 Q 0 -44 100 -26 Q 70 -14 -74 -22 Z', o.capColor2 || '#E5384F'); }
  if (hs === 'long') P(head, 'M -70 -4 Q -78 -90 0 -92 Q 78 -90 70 -4 Q 40 -60 0 -52 Q -40 -60 -70 -4 Z', hairC);
  if (hs === 'bun') { C(head, 0, -98, 26, hairC); P(head, 'M -68 -6 Q -76 -88 0 -90 Q 76 -88 68 -6 Q 50 -52 0 -48 Q -50 -52 -68 -6 Z', hairC); }
  if (hs === 'curly') { [-50, -26, 0, 26, 50].forEach((x, i) => C(head, x, -66 - (i % 2) * 8, 24, hairC)); P(head, 'M -66 -6 Q -70 -60 0 -62 Q 70 -60 66 -6 Q 50 -40 0 -38 Q -50 -40 -66 -6 Z', hairC); }
  // face
  const eyes = gnode(head); parts.eyes = eyes;
  [-26, 26].forEach(x => { el('ellipse', { cx: x, cy: -2, rx: 9, ry: 11, fill: '#1b1626' }, eyes); C(eyes, x + 3, -6, 3.2, '#fff'); });
  const brows = gnode(head); parts.brows = brows;
  const bL = L(brows, -40, -26, -14, -28, hairC === '#1d1b24' ? '#2a2233' : hairC, 6); const bR = L(brows, 14, -28, 40, -26, hairC === '#1d1b24' ? '#2a2233' : hairC, 6);
  parts.bL = bL; parts.bR = bR;
  C(head, -44, 22, 11, '#FF8E8E', { opacity: .35 }); C(head, 44, 22, 11, '#FF8E8E', { opacity: .35 });
  P(head, 'M -5 14 Q 0 20 5 14', sk[1], { fill: 'none', stroke: sk[1], 'stroke-width': 4, 'stroke-linecap': 'round' });
  parts.mouth = el('path', { d: 'M -24 36 Q 0 56 24 36', fill: 'none', stroke: '#5a2a2a', 'stroke-width': 6, 'stroke-linecap': 'round' }, head);
  if (o.mustache) P(head, 'M -34 28 Q -16 18 0 26 Q 16 18 34 28 Q 16 36 0 30 Q -16 36 -34 28 Z', o.mustacheColor || '#2a2233');
  if (o.glasses) { C(head, -26, -2, 20, 'none', { stroke: '#1f2235', 'stroke-width': 5 }); C(head, 26, -2, 20, 'none', { stroke: '#1f2235', 'stroke-width': 5 }); L(head, -6, -4, 6, -4, '#1f2235', 5); }
  if (o.earphones) { C(head, -64, 10, 8, '#fff'); C(head, 64, 10, 8, '#fff'); }
  if (o.headphones) { P(head, 'M -70 8 Q -72 -92 0 -94 Q 72 -92 70 8', 'none', { stroke: '#222', 'stroke-width': 10, 'stroke-linecap': 'round' }); R(head, -82, -6, 22, 40, '#222', 10); R(head, 60, -6, 22, 40, '#222', 10); }
  if (o.bindi) C(head, 0, -34, 6, '#E5384F');
  g.setMood = m => {
    const M = {
      smile: ['M -24 36 Q 0 58 24 36', -26, -28, 28, -26],
      grin: ['M -28 32 Q 0 66 28 32 Z', -28, -30, 30, -28],
      worry: ['M -20 46 Q 0 30 20 46', -18, -34, 18, -34],
      flat: ['M -18 42 L 18 42', -26, -28, 28, -26],
      o: ['M -8 38 Q 0 32 8 38 Q 8 54 0 54 Q -8 54 -8 38 Z', -30, -36, 30, -36],
      angry: ['M -20 46 Q 0 36 20 46', -12, -40, 12, -40],
      think: ['M -16 42 Q 6 40 20 36', -26, -34, 26, -26],
    }[m] || null;
    if (!M) return;
    parts.mouth.setAttribute('d', M[0]);
    parts.mouth.setAttribute('fill', m === 'o' || m === 'grin' ? '#7a2e3a' : 'none');
    parts.bL.setAttribute('y1', M[2]); parts.bL.setAttribute('y2', M[2] + (m === 'angry' ? 12 : m === 'worry' ? -8 : 0));
    parts.bR.setAttribute('y1', M[4] + (m === 'angry' ? 12 : m === 'worry' ? -8 : 0)); parts.bR.setAttribute('y2', M[4]);
  };
  g.idle = (lt, ph = 0) => {
    const b = bob(lt, 4, .5, ph);
    T(parts.body, { y: b * .3 }); T(parts.head, { x: 0, y: -232 + b, r: bob(lt, 1.6, .35, ph) });
    const blink = (lt + ph) % 3.2; T(parts.eyes, { sy: blink > 3.05 ? .1 : 1 });
  };
  g.setMood(o.mood || 'smile');
  return g;
};

// ------------------------------------------------------------ icons
A.coin = (parent, o = {}) => {
  const g = gnode(parent), r = o.r || 60;
  C(g, 0, 0, r, 'url(#gGold)'); C(g, 0, 0, r * .8, 'none', { stroke: '#C98412', 'stroke-width': r * .07 });
  txt(g, o.sym || '₹', { size: r * 1.05, fill: '#B8730A', font: 'en', y: r * .36, weight: 700 });
  return g;
};
A.bank = (parent, o = {}) => {
  const g = gnode(parent);
  P(g, 'M -130 -60 L 0 -150 L 130 -60 Z', 'url(#gGold)');
  R(g, -130, -60, 260, 20, '#FFF1C9', 4);
  [-100, -50, 0, 50, 100].forEach(x => { R(g, x - 14, -40, 28, 110, '#fff', 6); R(g, x - 18, -44, 36, 10, '#E9EDFB', 3); });
  R(g, -140, 70, 280, 22, '#E9EDFB', 5); R(g, -150, 92, 300, 22, '#C8D0EE', 5);
  C(g, 0, -92, 20, '#fff'); txt(g, '₹', { size: 26, fill: '#C98412', font: 'en', y: -83 });
  return g;
};
A.vault = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {};
  R(g, -130, -130, 260, 260, '#5C6785', 24); R(g, -112, -112, 224, 224, '#8791AD', 16);
  C(g, 0, 0, 78, '#4A5470'); C(g, 0, 0, 66, '#B8C1DA');
  const w = gnode(g); parts.wheel = w;
  C(w, 0, 0, 30, '#6B7592');
  for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; L(w, 0, 0, Math.cos(a) * 50, Math.sin(a) * 50, '#6B7592', 10); C(w, Math.cos(a) * 54, Math.sin(a) * 54, 8, '#3F4862'); }
  C(w, 0, 0, 12, '#FFD66B');
  R(g, -150, -70, 20, 40, '#3F4862', 6); R(g, -150, 30, 20, 40, '#3F4862', 6);
  return g;
};
A.piggy = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {};
  P(g, 'M 98 -10 Q 140 -34 122 -60 Q 100 -50 104 -26', 'none', { stroke: '#F58AA5', 'stroke-width': 10, 'stroke-linecap': 'round' });
  [-60, 56].forEach(x => R(g, x, 40, 34, 56, '#F58AA5', 12));
  el('ellipse', { cx: 0, cy: 0, rx: 118, ry: 86, fill: '#FFA3BC' }, g);
  P(g, 'M -60 -70 L -40 -122 L -4 -80 Z', '#F58AA5'); P(g, 'M 10 -80 L 42 -118 L 62 -64 Z', '#F58AA5');
  el('ellipse', { cx: -112, cy: 6, rx: 34, ry: 28, fill: '#F58AA5' }, g); C(g, -118, 4, 6, '#B8456A'); C(g, -102, 4, 6, '#B8456A');
  C(g, -62, -26, 9, '#2a1b36'); R(g, -14, -88, 56, 10, '#C8456A', 5);
  const coin = parts.coin = gnode(g); A.coin(coin, { r: 34 }); T(coin, { x: 14, y: -140 });
  return g;
};
A.calendar = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {}, w = o.w || 200, h = o.h || 220;
  R(g, -w / 2, -h / 2, w, h, '#fff', 20, { filter: 'url(#fSoft)' });
  P(g, `M ${-w / 2} ${-h / 2 + 56} L ${-w / 2} ${-h / 2 + 20} Q ${-w / 2} ${-h / 2} ${-w / 2 + 20} ${-h / 2} L ${w / 2 - 20} ${-h / 2} Q ${w / 2} ${-h / 2} ${w / 2} ${-h / 2 + 20} L ${w / 2} ${-h / 2 + 56} Z`, o.color || '#E5384F');
  R(g, -w / 2 + 40, -h / 2 - 12, 14, 32, '#444', 7); R(g, w / 2 - 54, -h / 2 - 12, 14, 32, '#444', 7);
  txt(g, o.label || 'EMI', { size: 64, fill: '#E5384F', font: 'en', y: 36 });
  txt(g, o.sub || '₹', { size: 36, fill: '#9AA3C7', font: 'en', y: 80, weight: 600 });
  return g;
};
A.bag = (parent, o = {}) => {
  const g = gnode(parent), c = o.color || '#FF5A5F', c2 = o.color2 || '#E5384F';
  P(g, 'M -46 -40 Q -46 -90 0 -90 Q 46 -90 46 -40', 'none', { stroke: c2, 'stroke-width': 10, 'stroke-linecap': 'round' });
  P(g, 'M -66 -50 L 66 -50 L 80 90 Q 80 100 70 100 L -70 100 Q -80 100 -80 90 Z', c);
  P(g, 'M -66 -50 L 66 -50 L 70 -20 L -70 -20 Z', c2, { opacity: .55 });
  C(g, -26, -50, 7, '#fff'); C(g, 26, -50, 7, '#fff');
  txt(g, o.mark || '%', { size: 54, fill: '#fff', font: 'en', y: 52 });
  return g;
};
A.phone = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {};
  R(g, -62, -120, 124, 240, '#1c2038', 22, { filter: 'url(#fSoft)' }); R(g, -54, -108, 108, 216, o.screen || '#2d3a6b', 14);
  R(g, -20, -116, 40, 6, '#0e1020', 3);
  return g;
};
A.chart = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {}, w = o.w || 360, h = o.h || 220, col = o.color || '#3DDC97';
  R(g, -w / 2 - 20, -h / 2 - 20, w + 40, h + 40, 'rgba(255,255,255,.08)', 22, { stroke: 'rgba(255,255,255,.22)', 'stroke-width': 3 });
  [0.25, .5, .75].forEach(k => L(g, -w / 2, -h / 2 + h * k, w / 2, -h / 2 + h * k, 'rgba(255,255,255,.12)', 2));
  const pts = o.pts || [.9, .78, .84, .6, .66, .4, .46, .18, .1];
  const d = pts.map((y, i) => `${i ? 'L' : 'M'} ${(-w / 2 + (w * i / (pts.length - 1))).toFixed(1)} ${(-h / 2 + h * y).toFixed(1)}`).join(' ');
  const line = parts.line = P(g, d, 'none', { stroke: col, 'stroke-width': 10, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  parts.pts = pts.map((y, i) => [(-w / 2 + (w * i / (pts.length - 1))), (-h / 2 + h * y)]);
  const tip = parts.tip = C(g, 0, 0, 14, col, { stroke: '#fff', 'stroke-width': 4 });
  g.setProgress = k => {
    draw(line, k);
    const n = pts.length - 1, f = clamp(k) * n, i = Math.min(n - 1, Math.floor(f)), u = f - i;
    const a = parts.pts[i], b = parts.pts[i + 1];
    tip.setAttribute('cx', lerp(a[0], b[0], u)); tip.setAttribute('cy', lerp(a[1], b[1], u));
    tip.setAttribute('opacity', k > 0.01 ? 1 : 0);
  };
  g.setProgress(0);
  return g;
};
A.bulb = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {};
  const glow = parts.glow = C(g, 0, -20, 190, 'url(#gGlowGold)'); glow.setAttribute('opacity', 0);
  const rays = parts.rays = gnode(g);
  for (let i = 0; i < 10; i++) { const a = (i / 10) * Math.PI * 2; L(rays, Math.cos(a) * 130, -20 + Math.sin(a) * 130, Math.cos(a) * 168, -20 + Math.sin(a) * 168, '#FFD66B', 9); }
  const b = parts.glass = P(g, 'M -66 -30 Q -66 -110 0 -112 Q 66 -110 66 -30 Q 66 4 38 36 L 38 60 L -38 60 L -38 36 Q -66 4 -66 -30 Z', '#6B7592');
  R(g, -38, 62, 76, 18, '#AAB4D0', 6); R(g, -30, 82, 60, 16, '#8791AD', 6); R(g, -14, 98, 28, 10, '#6B7592', 5);
  g.setOn = k => { b.setAttribute('fill', mixc('#6B7592', '#FFE066', k)); glow.setAttribute('opacity', k); rays.setAttribute('opacity', k); };
  g.setOn(0);
  return g;
};
A.book = (parent, o = {}) => {
  const g = gnode(parent), c = o.color || '#2F5BFF', c2 = o.color2 || '#1B3BC4';
  R(g, -110, -150, 220, 300, c2, 14, { filter: 'url(#fShadow)' });
  R(g, -98, -150, 208, 300, c, 12);
  R(g, -98, -150, 26, 300, c2, 6, { opacity: .55 });
  R(g, 100, -138, 14, 276, '#F4F1E6', 4);
  if (o.title !== false) {
    const lines = o.lines || ['THE', 'PSYCHOLOGY', 'OF MONEY'];
    txt(g, lines[0], { size: 26, fill: '#FFE08A', font: 'en', y: -80, weight: 600, ls: 6 });
    txt(g, lines[1], { size: 29, fill: '#fff', font: 'en', y: -34, weight: 700 });
    txt(g, lines[2], { size: 29, fill: '#fff', font: 'en', y: 6, weight: 700 });
    C(g, 6, 78, 36, 'none', { stroke: '#FFE08A', 'stroke-width': 5 });
    txt(g, '₹', { size: 44, fill: '#FFE08A', font: 'en', y: 94, x: 6 });
  }
  return g;
};
A.magnifier = (parent, o = {}) => {
  const g = gnode(parent), r = o.r || 74;
  L(g, r * .7, r * .7, r * 1.7, r * 1.7, '#C98412', 20); L(g, r * .7, r * .7, r * 1.2, r * 1.2, '#FFD66B', 20);
  C(g, 0, 0, r, 'rgba(160,220,255,.22)', { stroke: '#EAF2FF', 'stroke-width': 14 });
  P(g, `M ${-r * .5} ${-r * .3} Q ${-r * .3} ${-r * .6} ${r * .1} ${-r * .6}`, 'none', { stroke: '#fff', 'stroke-width': 7, 'stroke-linecap': 'round', opacity: .8 });
  return g;
};
A.globe = (parent, o = {}) => {
  const g = gnode(parent), r = o.r || 150, parts = g.parts = {};
  const id = 'gc' + Math.floor(Math.random() * 1e6);
  const cp = el('clipPath', { id }, DEFS); C(cp, 0, 0, r, '#000');
  rgrad(id + 'o', [[0, '#5CC8FF'], [1, '#1B63D6']]).setAttribute('cx', '40%');
  C(g, 0, 0, r, `url(#${id}o)`);
  const land = gnode(g, { 'clip-path': `url(#${id})` }); parts.land = land;
  const cont = [
    'M -80 -60 Q -40 -110 0 -80 Q 30 -50 10 -20 Q -20 0 -30 40 Q -60 60 -90 10 Q -110 -30 -80 -60 Z',
    'M 40 -20 Q 90 -60 130 -20 Q 150 20 110 50 Q 70 90 50 50 Q 20 20 40 -20 Z',
    'M -20 70 Q 20 60 40 90 Q 20 130 -30 120 Z',
  ];
  const strip = gnode(land);
  for (let k = -1; k <= 1; k++) { const s = gnode(strip); s.setAttribute('transform', `translate(${k * 2 * r * 1.0} 0)`); cont.forEach(d => P(s, d, '#4CCB86', { opacity: .95 })); }
  parts.strip = strip;
  C(g, 0, 0, r, 'none', { stroke: 'rgba(255,255,255,.55)', 'stroke-width': 5 });
  el('ellipse', { cx: 0, cy: 0, rx: r * .42, ry: r, fill: 'none', stroke: 'rgba(255,255,255,.28)', 'stroke-width': 3 }, g);
  L(g, -r, 0, r, 0, 'rgba(255,255,255,.28)', 3);
  C(g, -r * .35, -r * .4, r * .45, 'url(#gGlow)', { opacity: .35 });
  g.spin = lt => strip.setAttribute('transform', `translate(${((lt * 22) % (2 * r)).toFixed(1)} 0)`);
  return g;
};
A.pin = (parent, o = {}) => { const g = gnode(parent); P(g, 'M 0 90 Q -70 10 -70 -30 Q -70 -90 0 -90 Q 70 -90 70 -30 Q 70 10 0 90 Z', o.color || '#FF5A5F'); C(g, 0, -34, 26, '#fff'); return g; };
A.house = (parent, o = {}) => {
  const g = gnode(parent);
  P(g, 'M -100 -10 L 0 -100 L 100 -10 Z', o.roof || '#FF5A5F'); R(g, -78, -10, 156, 100, o.wall || '#FFE8C2', 8);
  R(g, -22, 24, 44, 66, '#B8764A', 8); R(g, -66, 8, 34, 34, '#8EC9FF', 6); R(g, 32, 8, 34, 34, '#8EC9FF', 6);
  return g;
};
A.eye = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {};
  P(g, 'M -110 0 Q 0 -90 110 0 Q 0 90 -110 0 Z', '#fff', { filter: 'url(#fSoft)' });
  const pu = parts.pupil = gnode(g); C(pu, 0, 0, 40, o.iris || '#3F7BFF'); C(pu, 0, 0, 18, '#111'); C(pu, 12, -14, 8, '#fff');
  return g;
};
A.calculator = (parent, o = {}) => {
  const g = gnode(parent);
  R(g, -90, -125, 180, 250, '#2A3050', 22, { filter: 'url(#fSoft)' }); R(g, -72, -105, 144, 56, '#B9F3D6', 10);
  txt(g, o.display || '2 + 2', { size: 36, fill: '#0B6B4B', font: 'en', y: -64, anchor: 'end', x: 62 });
  for (let r = 0; r < 4; r++)for (let c = 0; c < 3; c++) R(g, -70 + c * 50, -30 + r * 38, 40, 30, c === 2 && r < 3 ? '#FFB84D' : '#5B6591', 8);
  return g;
};
A.heart = (parent, o = {}) => { const g = gnode(parent); P(g, 'M 0 60 Q -110 -10 -70 -60 Q -30 -90 0 -44 Q 30 -90 70 -60 Q 110 -10 0 60 Z', o.color || '#FF4D6D'); P(g, 'M -52 -44 Q -40 -62 -22 -56', 'none', { stroke: '#fff', 'stroke-width': 8, 'stroke-linecap': 'round', opacity: .6 }); return g; };
A.gear = (parent, o = {}) => {
  const g = gnode(parent), r = o.r || 80, n = o.n || 10, col = o.color || '#9AA6D6';
  let d = ''; for (let i = 0; i < n * 2; i++) { const a0 = (i / (n * 2)) * Math.PI * 2, a1 = ((i + 1) / (n * 2)) * Math.PI * 2, rr = i % 2 ? r : r * 1.22; d += (i ? 'L' : 'M') + (Math.cos(a0) * rr).toFixed(1) + ' ' + (Math.sin(a0) * rr).toFixed(1) + ' L ' + (Math.cos(a1 - .02) * rr).toFixed(1) + ' ' + (Math.sin(a1 - .02) * rr).toFixed(1) + ' '; }
  P(g, d + 'Z', col); C(g, 0, 0, r * .5, o.hole || '#1b1f4a');
  return g;
};
A.puzzle = (parent, o = {}) => {
  const g = gnode(parent), c = o.color || '#FF8A3D', s = 90, k = 26;
  // square piece with knobs: sides = [top,right,bottom,left] each 1 out, -1 in, 0 flat
  const sd = o.sides || [1, 1, -1, -1];
  const knob = (x0, y0, x1, y1, dir) => { // from (x0,y0) to (x1,y1), bulge by dir*k perpendicular
    if (!dir) return `L ${x1} ${y1} `;
    const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, dx = x1 - x0, dy = y1 - y0, len = Math.hypot(dx, dy), nx = dy / len, ny = -dx / len;
    const ux = dx / len, uy = dy / len, b = dir * k, w = 14;
    return `L ${mx - ux * w} ${my - uy * w} C ${mx - ux * w + nx * b} ${my - uy * w + ny * b} ${mx - ux * 30 + nx * b * 1.7} ${my - uy * 30 + ny * b * 1.7} ${mx + nx * b * 1.7} ${my + ny * b * 1.7} C ${mx + ux * 30 + nx * b * 1.7} ${my + uy * 30 + ny * b * 1.7} ${mx + ux * w + nx * b} ${my + uy * w + ny * b} ${mx + ux * w} ${my + uy * w} L ${x1} ${y1} `;
  };
  const d = `M ${-s} ${-s} ` + knob(-s, -s, s, -s, -sd[0]) + knob(s, -s, s, s, -sd[1]) + knob(s, s, -s, s, -sd[2]) + knob(-s, s, -s, -s, -sd[3]) + 'Z';
  P(g, d, c, { stroke: 'rgba(0,0,0,.18)', 'stroke-width': 4, 'stroke-linejoin': 'round', filter: 'url(#fSoft)' });
  return g;
};
A.thumb = (parent, o = {}) => {
  const g = gnode(parent), c = o.color || '#FFC857';
  R(g, -100, -10, 52, 110, '#4C6FFF', 12);
  P(g, 'M -34 -6 L 10 -100 Q 36 -118 52 -90 L 40 -30 L 96 -30 Q 126 -26 118 8 L 106 76 Q 100 104 70 104 L -34 104 Z', c);
  return g;
};
A.bell = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {}, c = o.color || '#FFC857';
  const b = parts.b = gnode(g);
  P(b, 'M -70 40 Q -70 -10 -60 -40 Q -44 -90 0 -92 Q 44 -90 60 -40 Q 70 -10 70 40 Z', c); R(b, -86, 38, 172, 20, '#E9A02A', 10); C(b, 0, -100, 12, c); C(b, 0, 76, 16, '#E9A02A');
  return g;
};
A.bubble = (parent, o = {}) => {
  const g = gnode(parent), w = o.w || 260, h = o.h || 150, c = o.fill || '#fff';
  const tail = o.tail || 'bl';
  P(g, `M ${-w / 2 + 30} ${-h / 2} L ${w / 2 - 30} ${-h / 2} Q ${w / 2} ${-h / 2} ${w / 2} ${-h / 2 + 30} L ${w / 2} ${h / 2 - 30} Q ${w / 2} ${h / 2} ${w / 2 - 30} ${h / 2} L ${tail === 'bl' ? -w / 2 + 90 : w / 2 - 50} ${h / 2} L ${tail === 'bl' ? -w / 2 + 40 : w / 2 - 20} ${h / 2 + 46} L ${tail === 'bl' ? -w / 2 + 50 : w / 2 - 100} ${h / 2} L ${-w / 2 + 30} ${h / 2} Q ${-w / 2} ${h / 2} ${-w / 2} ${h / 2 - 30} L ${-w / 2} ${-h / 2 + 30} Q ${-w / 2} ${-h / 2} ${-w / 2 + 30} ${-h / 2} Z`, c, { filter: 'url(#fSoft)', stroke: o.stroke || 'none', 'stroke-width': o.sw || 0 });
  return g;
};
A.thought = (parent, o = {}) => { // cloud-like thought bubble with dots toward lower-left
  const g = gnode(parent), w = o.w || 300, h = o.h || 170, c = o.fill || '#fff';
  const cl = gnode(g, { filter: 'url(#fSoft)' });
  el('ellipse', { cx: 0, cy: 0, rx: w / 2, ry: h / 2, fill: c }, cl);
  [[-w / 2 + 40, -h / 2 + 30, 50], [-w / 4, -h / 2 + 4, 56], [w / 6, -h / 2 + 2, 58], [w / 2 - 50, -h / 2 + 34, 48], [w / 2 - 30, h / 2 - 50, 48], [-w / 2 + 34, h / 2 - 44, 46], [0, h / 2 - 6, 54]].forEach(([x, y, r]) => C(cl, x, y, r, c));
  C(g, -w / 2 + 6, h / 2 + 34, 16, c); C(g, -w / 2 - 22, h / 2 + 70, 10, c);
  return g;
};
A.star = (parent, o = {}) => {
  const g = gnode(parent), r = o.r || 60, n = o.n || 5; let d = '';
  for (let i = 0; i < n * 2; i++) { const a = -Math.PI / 2 + (i / (n * 2)) * Math.PI * 2, rr = i % 2 ? r * (o.inner || .45) : r; d += (i ? 'L' : 'M') + (Math.cos(a) * rr).toFixed(1) + ' ' + (Math.sin(a) * rr).toFixed(1) + ' '; }
  P(g, d + 'Z', o.fill || 'url(#gGold)'); return g;
};
A.check = (parent, o = {}) => { const g = gnode(parent), r = o.r || 48; C(g, 0, 0, r, 'url(#gMint)'); P(g, `M ${-r * .42} ${r * .02} L ${-r * .1} ${r * .34} L ${r * .46} ${-r * .3}`, 'none', { stroke: '#fff', 'stroke-width': r * .24, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }); return g; };
A.cross = (parent, o = {}) => { const g = gnode(parent), r = o.r || 48; C(g, 0, 0, r, 'url(#gCoral)'); L(g, -r * .36, -r * .36, r * .36, r * .36, '#fff', r * .24); L(g, r * .36, -r * .36, -r * .36, r * .36, '#fff', r * .24); return g; };
A.warning = (parent, o = {}) => { const g = gnode(parent); P(g, 'M 0 -90 L 96 70 L -96 70 Z', '#FFC857', { stroke: '#FFC857', 'stroke-width': 14, 'stroke-linejoin': 'round' }); R(g, -8, -36, 16, 62, '#7A4A00', 8); C(g, 0, 46, 9, '#7A4A00'); return g; };
A.wallet = (parent, o = {}) => {
  const g = gnode(parent), c = o.color || '#8B5CF6';
  R(g, -110, -70, 220, 150, c, 22, { filter: 'url(#fSoft)' }); R(g, -110, -70, 220, 44, '#6C3BE8', 22); R(g, 30, -8, 100, 56, '#B79CFF', 16); C(g, 62, 20, 10, '#fff');
  return g;
};
A.cloud = (parent, o = {}) => {
  const g = gnode(parent), c = o.color || '#C9CFE8';
  [[-60, 10, 44], [-14, -16, 56], [44, 0, 48], [86, 22, 34], [-96, 28, 30]].forEach(([x, y, r]) => C(g, x, y, r, c)); R(g, -96, 20, 190, 34, c, 17);
  return g;
};
A.sun = (parent, o = {}) => {
  const g = gnode(parent), r = o.r || 56, parts = g.parts = {};
  const rays = parts.rays = gnode(g); for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; L(rays, Math.cos(a) * (r + 18), Math.sin(a) * (r + 18), Math.cos(a) * (r + 44), Math.sin(a) * (r + 44), '#FFD66B', 9); }
  C(g, 0, 0, r, 'url(#gGold)'); return g;
};
A.bolt = (parent, o = {}) => { const g = gnode(parent); P(g, 'M 14 -90 L -50 10 L -6 10 L -22 90 L 52 -18 L 8 -18 Z', o.fill || '#FFD66B'); return g; };
A.flame = (parent, o = {}) => { const g = gnode(parent); P(g, 'M 0 -100 Q 40 -50 54 -10 Q 70 50 30 84 Q 0 100 -30 84 Q -70 50 -50 0 Q -40 -26 -20 -40 Q -20 -10 0 -10 Q 14 -50 0 -100 Z', '#FF7A33'); P(g, 'M 0 -30 Q 28 6 30 40 Q 30 70 0 76 Q -30 70 -28 40 Q -26 10 0 -30 Z', '#FFD66B'); return g; };
A.rocket = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {};
  const fl = parts.fire = gnode(g); P(fl, 'M -22 70 Q 0 160 22 70 Z', '#FF7A33'); P(fl, 'M -12 70 Q 0 120 12 70 Z', '#FFE066');
  P(g, 'M 0 -110 Q 52 -50 40 70 L -40 70 Q -52 -50 0 -110 Z', '#F2F4FF'); C(g, 0, -20, 22, '#4C6FFF', { stroke: '#2B3DB5', 'stroke-width': 6 });
  P(g, 'M -40 20 L -78 80 L -40 66 Z', '#FF5A5F'); P(g, 'M 40 20 L 78 80 L 40 66 Z', '#FF5A5F'); P(g, 'M 0 -110 Q 26 -84 32 -64 L -32 -64 Q -26 -84 0 -110 Z', '#FF5A5F');
  return g;
};
A.tag = (parent, o = {}) => {
  const g = gnode(parent);
  P(g, 'M -90 -50 L 50 -50 L 100 0 L 50 50 L -90 50 Q -104 50 -104 36 L -104 -36 Q -104 -50 -90 -50 Z', o.color || '#FF5A5F', { filter: 'url(#fSoft)' }); C(g, 62, 0, 9, 'rgba(0,0,0,.3)');
  txt(g, o.label || '₹100', { size: 42, fill: '#fff', font: 'en', x: -44, y: 15 });
  return g;
};
A.hand = (parent, o = {}) => { // pointer cursor
  const g = gnode(parent);
  P(g, 'M -6 -60 Q -6 -76 8 -76 Q 22 -76 22 -60 L 22 -20 L 30 -22 Q 40 -24 42 -14 L 44 -12 Q 54 -14 58 -4 L 60 -2 Q 70 -2 72 10 L 72 40 Q 72 80 40 84 L 6 84 Q -16 84 -26 62 L -50 18 Q -56 6 -46 2 Q -36 -2 -28 10 L -6 38 Z', '#fff', { stroke: '#222', 'stroke-width': 5, 'stroke-linejoin': 'round' });
  return g;
};
A.avatar = (parent, o = {}) => { const g = gnode(parent), r = o.r || 40; C(g, 0, 0, r, o.bg || '#6C3BE8'); C(g, 0, -r * .2, r * .34, '#fff', { opacity: .9 }); P(g, `M ${-r * .62} ${r * .78} Q 0 ${-r * .2} ${r * .62} ${r * .78} Z`, '#fff', { opacity: .9 }); return g; };
A.polaroid = (parent, o = {}) => {
  const g = gnode(parent);
  R(g, -80, -90, 160, 190, '#fff', 8, { filter: 'url(#fSoft)' }); R(g, -66, -76, 132, 120, o.bg || '#7FA8FF', 4);
  txt(g, o.emoji || '📷', { size: 70, y: 8, font: 'en' }); txt(g, o.cap || '', { size: 24, fill: '#444', y: 80, weight: 600 });
  return g;
};
A.sparkle = (parent, o = {}) => { const g = gnode(parent), r = o.r || 24; P(g, `M 0 ${-r} Q 4 -4 ${r} 0 Q 4 4 0 ${r} Q -4 4 ${-r} 0 Q -4 -4 0 ${-r} Z`, o.fill || '#fff'); return g; };
A.arrow = (parent, o = {}) => { const g = gnode(parent), l = o.len || 160, c = o.color || '#fff'; L(g, -l / 2, 0, l / 2 - 10, 0, c, o.w || 14); P(g, `M ${l / 2 - 34} -28 L ${l / 2 + 6} 0 L ${l / 2 - 34} 28`, 'none', { stroke: c, 'stroke-width': o.w || 14, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }); return g; };
A.rays = (parent, o = {}) => { // sunburst
  const g = gnode(parent), n = o.n || 16, r = o.r || 900;
  for (let i = 0; i < n; i++) { const a0 = i / n * Math.PI * 2, a1 = (i + .5) / n * Math.PI * 2; P(g, `M 0 0 L ${Math.cos(a0) * r} ${Math.sin(a0) * r} L ${Math.cos(a1) * r} ${Math.sin(a1) * r} Z`, o.fill || 'rgba(255,255,255,.07)'); }
  return g;
};
A.shadow = (parent, w = 220, y = 0, o = .28) => { const e = el('ellipse', { cx: 0, cy: y, rx: w, ry: w * .12, fill: '#000', opacity: o }, parent); return e; };
A.card = (parent, w, h, o = {}) => { const g = gnode(parent); R(g, -w / 2, -h / 2, w, h, o.fill || 'rgba(255,255,255,.1)', o.rx == null ? 32 : o.rx, { stroke: o.stroke || 'rgba(255,255,255,.28)', 'stroke-width': o.sw == null ? 3 : o.sw, filter: o.shadow ? 'url(#fShadow)' : undefined }); return g; };
