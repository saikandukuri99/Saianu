// Solix reel B-roll – 5 vertical (1080x1920) motion-graphics clips.
// draw(scene, t, variant)  variant: 'full' | 'clean' | 'alpha'
const W = 1080, H = 1920, DUR = 6;
const C = document.getElementById('c'), X = C.getContext('2d');
const RED = '#ee2424', RED2 = '#ff3434', BLUE = '#0088cf', SKY = '#40ace8', ICE = '#bfe6ff';

// ---------- helpers ----------
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const eo = t => 1 - Math.pow(1 - t, 3);
const eo5 = t => 1 - Math.pow(1 - t, 5);
const ei = t => t * t * t;
function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function hex(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; }
function rgba(h, a) { const [r, g, b] = hex(h); return `rgba(${r},${g},${b},${a})`; }
function mix(h1, h2, t) { const a = hex(h1), b = hex(h2); return '#' + a.map((v, i) => Math.round(lerp(v, b[i], t)).toString(16).padStart(2, '0')).join(''); }
function mk(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }

const SPR = {};
function sprite(col) { // soft round glow sprite
  if (SPR[col]) return SPR[col];
  const c = mk(128, 128), g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, rgba(col, 1)); gr.addColorStop(.18, rgba(col, .75)); gr.addColorStop(.45, rgba(col, .22)); gr.addColorStop(1, rgba(col, 0));
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return SPR[col] = c;
}
function glow(ctx, x, y, r, col, a = 1) { if (a <= 0 || r <= 0) return; const g0 = ctx.globalAlpha; ctx.globalAlpha = g0 * Math.min(1, a); ctx.drawImage(sprite(col), x - r, y - r, 2 * r, 2 * r); ctx.globalAlpha = g0; }
function radial(x, y, r, col, a) { const g = X.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, rgba(col, a)); g.addColorStop(1, rgba(col, 0)); X.fillStyle = g; X.fillRect(x - r, y - r, 2 * r, 2 * r); }
function poly(ctx, pts) { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); }
function glowStroke(ctx, pts, col, w, a = 1, close = false) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (const [lw, al] of [[w * 7, .07], [w * 3, .22], [w, 1]]) { ctx.globalAlpha = al * a; ctx.lineWidth = lw; poly(ctx, pts); if (close) ctx.closePath(); ctx.stroke(); }
  ctx.restore();
}
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
// cubic bezier point
function bz(p0, p1, p2, p3, t) { const u = 1 - t; return [u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0], u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]]; }
function polyLen(pts) { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; }
function partial(pts, f) { // first fraction f of a polyline
  if (f >= 1) return pts; if (f <= 0) return [pts[0]];
  const L = polyLen(pts) * f; let acc = 0; const out = [pts[0]];
  for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); if (acc + d >= L) { const k = (L - acc) / d; out.push([lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k)]); return out; } acc += d; out.push(pts[i]); }
  return out;
}
function along(pts, f) { const p = partial(pts, f); return p[p.length - 1]; }

// ---------- shared look ----------
const BOKEH = (() => { const r = rng(7), a = []; for (let i = 0; i < 46; i++) a.push({ x: r() * W, y: r() * H, s: 6 + r() * 34, v: 8 + r() * 30, c: r() < .22 ? RED : (r() < .5 ? SKY : BLUE), a: .08 + r() * .22, p: r() * 6 }); return a; })();
const GRAIN = (() => { const out = []; const r = rng(99); for (let k = 0; k < 4; k++) { const c = mk(540, 960), g = c.getContext('2d'), id = g.createImageData(540, 960); for (let i = 0; i < id.data.length; i += 4) { const v = r() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; } g.putImageData(id, 0, 0); out.push(c); } return out; })();

function background(t, gy = 760) {
  const g = X.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#061232'); g.addColorStop(.42, '#0a1d4c'); g.addColorStop(.75, '#06123a'); g.addColorStop(1, '#030817');
  X.fillStyle = g; X.fillRect(0, 0, W, H);
  radial(540, gy, 760, BLUE, .26);
  radial(980 + 50 * Math.sin(t * .7), 1640, 720, RED, .17);
  radial(80, 220 + 30 * Math.sin(t * .5), 560, RED, .07);
}
function bokeh(t, k = 1) {
  X.save(); X.globalCompositeOperation = 'lighter';
  for (const b of BOKEH) { const y = ((b.y - t * b.v) % H + H) % H, x = b.x + 18 * Math.sin(t * .4 + b.p); glow(X, x, y, b.s * 2.2, b.c, b.a * k * (.7 + .3 * Math.sin(t * 1.3 + b.p))); }
  X.restore();
}
function finish(t, textZone = false) {
  if (textZone) { // gentle darkening behind the title zone (also in the clean plate, for consistency)
    const g = X.createLinearGradient(0, 1130, 0, 1800); g.addColorStop(0, 'rgba(2,6,20,0)'); g.addColorStop(.45, 'rgba(2,6,20,.42)'); g.addColorStop(1, 'rgba(2,6,20,.2)');
    X.fillStyle = g; X.fillRect(0, 1130, W, 670);
  }
  const v = X.createRadialGradient(540, 900, 380, 540, 960, 1250); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,8,.62)');
  X.fillStyle = v; X.fillRect(0, 0, W, H);
  X.save(); X.globalAlpha = .045; X.globalCompositeOperation = 'overlay'; X.drawImage(GRAIN[Math.floor(t * 30) % 4], 0, 0, W, H); X.restore();
}

// ---------- title ----------
const TITLES = {
  1: [[['THE', 0], ['EVOLUTION', 0]], [['OF', 0], ['AI', 1]]],
  2: [[['BUILT', 0], ['FOR', 0]], [['REAL-WORLD', 1]], [['APPLICATION', 0]]],
  3: [[['DESIGNED', 0]], [['FOR', 0], ['EXPERTS', 1]]],
  4: [[['FROM', 0], ['AI', 0], ['OUTPUT', 0]], [['TO', 0], ['REAL', 1], ['VALUE', 1]]],
  5: [[['BRIDGING', 0], ['AI', 0], ['&', 1]], [['HUMAN', 0], ['EXPERTISE', 1]]],
};
function title(t, lines) {
  X.save();
  let fs = 150; const maxW = 940;
  const meas = () => { X.font = `${fs}px IDB`; const sp = fs * .24; return { sp, w: lines.map(l => l.reduce((s, [w]) => s + X.measureText(w).width, 0) + sp * (l.length - 1)) }; };
  let m = meas(); const mx = Math.max(...m.w); if (mx > maxW) { fs = fs * maxW / mx; m = meas(); }
  const lh = fs * .98, cap = fs * .73, n = lines.length;
  const blockH = (n - 1) * lh + cap, top = 1405 - blockH / 2 + cap; // first baseline
  const s = 1 + .025 * t / DUR, cy = top - cap + blockH / 2;
  X.translate(540, cy); X.scale(s, s); X.translate(-540, -cy);
  // red accent bar
  const pb = eo5(seg(t, .12, .7));
  X.fillStyle = RED; X.shadowColor = 'rgba(238,36,36,.7)'; X.shadowBlur = 18;
  X.fillRect(540 - 75 * pb, top - cap - 52, 150 * pb, 10);
  X.shadowBlur = 0;
  lines.forEach((l, i) => {
    const d = .28 + i * .13, p = eo5(seg(t, d, d + .9));
    const base = top + i * lh;
    X.save(); X.beginPath(); X.rect(0, base - cap - fs * .12, W, cap + fs * .12 + 40); X.clip();
    const yo = (1 - p) * fs * 1.05;
    let x = 540 - m.w[i] / 2;
    for (const [w, red] of l) {
      X.shadowColor = 'rgba(0,2,14,.65)'; X.shadowBlur = 34; X.shadowOffsetY = 8;
      X.fillStyle = red ? RED2 : '#ffffff'; X.fillText(w, x, base + yo);
      x += X.measureText(w).width + m.sp;
    }
    X.restore();
  });
  X.restore();
}

// =====================================================================
// SCENE 1 – THE EVOLUTION OF AI : vintage computer -> particles -> AI chip & network
// =====================================================================
const S1 = { cx: 540, cy: 740 };
function drawComputer(ctx, t) {
  const fl = 1 + .012 * Math.sin(t * 2.1);
  ctx.save(); ctx.translate(540, 700 + 6 * Math.sin(t * 1.3)); ctx.scale(fl, fl); ctx.translate(-540, -700);
  // monitor body
  let g = ctx.createLinearGradient(0, 420, 0, 860); g.addColorStop(0, '#24386c'); g.addColorStop(1, '#0d1838');
  rr(ctx, 270, 420, 540, 430, 46); ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = rgba(SKY, .55); ctx.stroke();
  rr(ctx, 290, 440, 500, 390, 34); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,255,255,.08)'; ctx.stroke();
  // screen
  rr(ctx, 322, 470, 436, 300, 28); g = ctx.createRadialGradient(540, 620, 20, 540, 620, 300); g.addColorStop(0, '#0b3d63'); g.addColorStop(1, '#03111f'); ctx.fillStyle = g; ctx.fill();
  ctx.save(); rr(ctx, 322, 470, 436, 300, 28); ctx.clip();
  ctx.font = '27px MONO'; ctx.fillStyle = '#6fd6ff'; ctx.shadowColor = '#40ace8'; ctx.shadowBlur = 14;
  const L = ['SYSTEM READY.', '> LOAD "AI"', '> RUN', 'PROCESSING'];
  let chars = Math.floor((t - .25) * 20);
  L.forEach((s, i) => { if (chars <= 0) return; const sh = s.slice(0, chars); chars -= s.length + 3; ctx.fillText(sh, 352, 522 + i * 44); if (chars <= 0 && Math.floor(t * 3) % 2 === 0) ctx.fillRect(352 + ctx.measureText(sh).width + 4, 500 + i * 44, 16, 26); });
  ctx.shadowBlur = 0;
  // progress blocks
  const pr = seg(t, 1.3, 2.3); ctx.strokeStyle = '#6fd6ff'; ctx.lineWidth = 2; ctx.strokeRect(352, 700, 376, 30);
  ctx.fillStyle = '#6fd6ff'; for (let i = 0; i < Math.floor(pr * 18); i++) ctx.fillRect(357 + i * 20.6, 705, 16, 20);
  ctx.fillStyle = 'rgba(0,0,0,.28)'; for (let y = 470; y < 770; y += 4) ctx.fillRect(322, y, 436, 2);
  ctx.restore();
  // stand + base
  g = ctx.createLinearGradient(0, 850, 0, 920); g.addColorStop(0, '#1a2b58'); g.addColorStop(1, '#0b1532');
  ctx.fillStyle = g; poly(ctx, [[480, 850], [600, 850], [630, 900], [450, 900]]); ctx.fill();
  rr(ctx, 380, 898, 320, 26, 13); ctx.fill(); ctx.strokeStyle = rgba(SKY, .35); ctx.lineWidth = 2; ctx.stroke();
  // keyboard
  poly(ctx, [[300, 960], [780, 960], [830, 1050], [250, 1050]]); ctx.closePath(); g = ctx.createLinearGradient(0, 960, 0, 1050); g.addColorStop(0, '#22356a'); g.addColorStop(1, '#0e1a3c'); ctx.fillStyle = g; ctx.fill(); ctx.strokeStyle = rgba(SKY, .45); ctx.stroke();
  for (let r = 0; r < 3; r++) for (let k = 0; k < 12; k++) { const y = 972 + r * 24, sx = lerp(318, 272, (y - 960) / 90), ex = lerp(762, 808, (y - 960) / 90); const kw = (ex - sx) / 12; ctx.fillStyle = (r === 1 && k === Math.floor(t * 9) % 12 && t < 2.2) ? RED : 'rgba(150,200,255,.22)'; ctx.fillRect(sx + k * kw + 3, y, kw - 6, 17); }
  // power LED
  glow(ctx, 760, 805, 16, RED, .9);
  ctx.restore();
}
let S1P = null;
function s1Prep() {
  if (S1P) return S1P;
  const c = mk(W, H), g = c.getContext('2d'); drawComputer(g, 2.4);
  const d = g.getImageData(0, 0, W, H).data, r = rng(11), src = [];
  while (src.length < 1400) { const x = 240 + r() * 600, y = 400 + r() * 680, i = (Math.floor(y) * W + Math.floor(x)) * 4; if (d[i + 3] > 200 && (d[i] + d[i + 1] + d[i + 2]) > 60) src.push([x, y, `rgb(${d[i]},${d[i + 1]},${d[i + 2]})`]); }
  // targets: chip outline, pins, network lines, nodes
  const segs = [], nodes1 = [], nodes2 = [];
  const cs = 150; const box = [[540 - cs, S1.cy - cs], [540 + cs, S1.cy - cs], [540 + cs, S1.cy + cs], [540 - cs, S1.cy + cs], [540 - cs, S1.cy - cs]];
  for (let i = 0; i < 4; i++) segs.push([box[i], box[i + 1]]);
  const pins = [];
  for (let k = 0; k < 5; k++) { const o = -100 + k * 50; pins.push([[540 + o, S1.cy - cs], [540 + o, S1.cy - cs - 46]], [[540 + o, S1.cy + cs], [540 + o, S1.cy + cs + 46]], [[540 - cs, S1.cy + o], [540 - cs - 46, S1.cy + o]], [[540 + cs, S1.cy + o], [540 + cs + 46, S1.cy + o]]); }
  segs.push(...pins);
  for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2 + .3; nodes1.push([540 + Math.cos(a) * 300, S1.cy + Math.sin(a) * 300]); }
  for (let i = 0; i < 14; i++) { const a = i / 14 * Math.PI * 2; nodes2.push([540 + Math.cos(a) * 420, S1.cy + Math.sin(a) * 420 * .98]); }
  const links = [];
  pins.forEach((p, i) => { const e = p[1]; let best = nodes1[0], bd = 1e9; nodes1.forEach(n => { const dd = Math.hypot(n[0] - e[0], n[1] - e[1]); if (dd < bd) { bd = dd; best = n; } }); if (i % 2 === 0) links.push([e, best]); });
  nodes1.forEach((n, i) => { const sorted = nodes2.slice().sort((a, b) => Math.hypot(a[0] - n[0], a[1] - n[1]) - Math.hypot(b[0] - n[0], b[1] - n[1])); links.push([n, sorted[0]], [n, sorted[1]]); links.push([n, nodes1[(i + 1) % nodes1.length]]); });
  segs.push(...links);
  const tg = [];
  const total = segs.reduce((s, q) => s + Math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]), 0);
  segs.forEach(q => { const L = Math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]); const n = Math.max(2, Math.round(L / total * 1100)); for (let k = 0; k < n; k++) { const f = r(); tg.push([lerp(q[0][0], q[1][0], f), lerp(q[0][1], q[1][1], f)]); } });
  [...nodes1, ...nodes2].forEach(n => { for (let k = 0; k < 12; k++) tg.push([n[0] + (r() - .5) * 18, n[1] + (r() - .5) * 18]); });
  const parts = src.map((s, i) => ({ s, e: tg[i % tg.length], d: r(), w: (r() - .5) * 260, red: r() < .18 }));
  return S1P = { parts, pins, links, nodes1, nodes2, box };
}
function drawAI(t, a) {
  if (a <= 0) return;
  const P = s1Prep(), cy = S1.cy;
  X.save(); X.globalAlpha = a;
  X.save(); X.globalCompositeOperation = 'lighter';
  P.links.forEach((l, i) => { X.strokeStyle = rgba(i % 5 === 0 ? RED : SKY, .35); X.lineWidth = 2; X.beginPath(); X.moveTo(...l[0]); X.lineTo(...l[1]); X.stroke(); });
  P.links.forEach((l, i) => { const f = ((t * .55 + i * .137) % 1); const x = lerp(l[0][0], l[1][0], f), y = lerp(l[0][1], l[1][1], f); glow(X, x, y, 16, i % 4 === 0 ? RED : ICE, .9 * a); });
  P.pins.forEach(p => { X.strokeStyle = rgba(SKY, .9); X.lineWidth = 5; X.beginPath(); X.moveTo(...p[0]); X.lineTo(...p[1]); X.stroke(); });
  [...P.nodes1, ...P.nodes2].forEach((n, i) => { const pu = .6 + .4 * Math.sin(t * 3 + i); glow(X, n[0], n[1], 34 * pu, i % 6 === 0 ? RED : SKY, .9); glow(X, n[0], n[1], 10, '#ffffff', .9); });
  X.restore();
  // chip
  const br = .5 + .5 * Math.sin(t * 2.4);
  X.save(); X.shadowColor = rgba(SKY, .9); X.shadowBlur = 40 + 20 * br;
  rr(X, 390, cy - 150, 300, 300, 34); let g = X.createLinearGradient(390, cy - 150, 690, cy + 150); g.addColorStop(0, '#16336e'); g.addColorStop(1, '#0a1840'); X.fillStyle = g; X.fill();
  X.shadowBlur = 0; X.lineWidth = 5; X.strokeStyle = SKY; X.stroke();
  rr(X, 440, cy - 100, 200, 200, 22); X.lineWidth = 3; X.strokeStyle = rgba(RED, .95); X.stroke();
  X.shadowColor = rgba(SKY, 1); X.shadowBlur = 20; X.fillStyle = '#fff'; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) { X.beginPath(); X.arc(500 + i * 40, cy - 40 + j * 40, (i === 1 && j === 1) ? 14 : 8, 0, Math.PI * 2); X.fill(); } X.strokeStyle = '#fff'; X.lineWidth = 3; X.beginPath(); for (let i = 0; i < 3; i++) { X.moveTo(500 + i * 40, cy - 40); X.lineTo(500 + i * 40, cy + 40); X.moveTo(500, cy - 40 + i * 40); X.lineTo(580, cy - 40 + i * 40); } X.stroke();
  X.restore();
  X.restore();
}
function scene1(t) {
  background(t, 960); bokeh(t);
  X.save(); X.translate(0, 230);
  // timeline 1956 -> 2026
  const tp = eio(seg(t, .3, 4.6)), yr = Math.round(lerp(1956, 2026, tp));
  X.save(); X.globalAlpha = seg(t, 0, .5);
  X.fillStyle = 'rgba(255,255,255,.18)'; X.fillRect(190, 300, 700, 4);
  const gr = X.createLinearGradient(190, 0, 890, 0); gr.addColorStop(0, SKY); gr.addColorStop(1, RED); X.fillStyle = gr; X.fillRect(190, 300, 700 * tp, 4);
  glow(X, 190 + 700 * tp, 302, 30, tp > .98 ? RED : SKY, 1); glow(X, 190 + 700 * tp, 302, 9, '#ffffff', 1);
  X.font = '26px MONO'; X.fillStyle = 'rgba(255,255,255,.55)'; X.textAlign = 'left'; X.fillText('1956', 190, 350); X.textAlign = 'right'; X.fillText('TODAY', 890, 350);
  X.textAlign = 'center'; X.font = '58px MONO'; X.fillStyle = tp > .98 ? RED2 : '#ffffff'; X.fillText(String(yr), 540, 270);
  X.restore();
  // computer + glitch
  const ca = 1 - seg(t, 2.75, 3.1);
  if (ca > 0) {
    const off = mk(W, H), g = off.getContext('2d'); drawComputer(g, t);
    const gl = seg(t, 2.25, 2.75);
    if (gl > 0 && gl < 1 || t >= 2.75) {
      const r = rng(Math.floor(t * 30) + 3);
      X.save(); X.globalAlpha = ca; X.globalCompositeOperation = 'lighter';
      for (let y = 400; y < 1080; y += 18 + Math.floor(r() * 30)) { const h = 10 + r() * 40, dx = (r() - .5) * 120 * gl; X.drawImage(off, 0, y, W, h, dx, y, W, h); }
      X.globalAlpha = .45 * ca * gl; X.filter = 'hue-rotate(140deg)'; X.drawImage(off, 14 * gl, 0); X.filter = 'none';
      X.restore();
    } else { X.globalAlpha = ca; X.drawImage(off, 0, 0); X.globalAlpha = 1; }
    if (t > 2.45 && t < 2.8) { X.fillStyle = `rgba(160,220,255,${.35 * (1 - seg(t, 2.45, 2.8))})`; X.fillRect(0, 0, W, H); }
  }
  // particles
  const P = s1Prep();
  if (t > 2.5 && t < 4.9) {
    X.save(); X.globalCompositeOperation = 'lighter';
    const fade = 1 - seg(t, 4.2, 4.9);
    for (const p of P.parts) {
      const k = eio(seg(t, 2.55 + p.d * .5, 3.75 + p.d * .5));
      const x = lerp(p.s[0], p.e[0], k) + Math.sin(k * Math.PI) * p.w, y = lerp(p.s[1], p.e[1], k) + Math.sin(k * Math.PI) * p.w * .35;
      const col = k > .5 ? (p.red ? RED : SKY) : SKY;
      glow(X, x, y, 7 + 5 * Math.sin(k * Math.PI), col, .8 * fade);
    }
    X.restore();
  }
  drawAI(t, eo(seg(t, 3.7, 4.6)));
  X.restore();
  finish(t);
}

// =====================================================================
// SCENE 2 – BUILT FOR REAL-WORLD APPLICATION : data-center corridor + live HUD
// =====================================================================
const S2 = (() => { const r = rng(21), leds = []; for (let i = 0; i < 400; i++) leds.push({ ph: r() * 10, rt: .6 + r() * 3, c: r() < .16 ? RED : (r() < .25 ? '#ffffff' : SKY), th: r() * .9 - .2 }); return { leds }; })();
function scene2(t) {
  background(t, 820);
  const VX = 540, VY = 820, F = 760, cz = t * 1.35;
  const P = (x, y, z) => [VX + x * F / z, VY - y * F / z];
  const fog = z => clamp(z / 26);
  // far glow
  radial(VX, VY, 520, SKY, .25); radial(VX, VY, 160, '#ffffff', .25);
  const SEG = 1.3, N = 24, HW = 1.55, YB = -1.45, YT = 1.75;
  // floor & ceiling lines
  X.save(); X.globalCompositeOperation = 'lighter';
  for (let i = -3; i <= 3; i++) { const x = i * .5; const a = P(x, YB, .35), b = P(x, YB, 40); X.strokeStyle = rgba(BLUE, .22); X.lineWidth = 2; X.beginPath(); X.moveTo(...a); X.lineTo(...b); X.stroke(); }
  for (let k = 0; k < 40; k++) { const z = k * 1 - (cz % 1); if (z < .4) continue; const a = P(-HW, YB, z), b = P(HW, YB, z); X.strokeStyle = rgba(BLUE, .25 * (1 - fog(z))); X.lineWidth = 2; X.beginPath(); X.moveTo(...a); X.lineTo(...b); X.stroke(); }
  // ceiling light strips
  for (const x of [-.55, .55]) { const pts = []; for (let z = .5; z < 34; z += .5) pts.push(P(x, YT, z)); glowStroke(X, pts, ICE, 5, .55); }
  X.restore();
  // racks (far -> near)
  const order = [];
  for (let i = 0; i < N; i++) { let z1 = i * SEG - (cz % SEG); const z2 = z1 + SEG - .1; if (z2 < .36) continue; order.push([Math.max(.36, z1), z2, i + Math.floor(cz / SEG)]); }
  order.sort((a, b) => b[0] - a[0]);
  for (const [z1, z2, id] of order) {
    for (const side of [-1, 1]) {
      const x = side * HW, q = [P(x, YT, z1), P(x, YT, z2), P(x, YB, z2), P(x, YB, z1)];
      const f = fog(z1);
      X.fillStyle = mix('#0d1c44', '#0a1d4c', f); poly(X, q); X.closePath(); X.fill();
      X.strokeStyle = rgba(SKY, .45 * (1 - f)); X.lineWidth = 2; X.stroke();
      // rack units
      X.strokeStyle = rgba('#000000', .35); X.lineWidth = 1;
      for (let u = 1; u < 10; u++) { const y = lerp(YB, YT, u / 10); const a = P(x, y, z1), b = P(x, y, z2); X.beginPath(); X.moveTo(...a); X.lineTo(...b); X.stroke(); }
      X.save(); X.globalCompositeOperation = 'lighter';
      for (let u = 0; u < 10; u++) for (let c = 0; c < 4; c++) {
        const L = S2.leds[(id * 97 + u * 13 + c * 7 + (side > 0 ? 5 : 0)) % 400 + 0];
        const on = Math.sin(t * L.rt * 3 + L.ph) > L.th; if (!on) continue;
        const z = lerp(z1, z2, .15 + c * .2), y = lerp(YB, YT, (u + .5) / 10);
        const p = P(x, y, z), s = Math.max(3, 40 / z);
        glow(X, p[0], p[1], s, L.c, (1 - f) * .95);
      }
      X.restore();
    }
  }
  // HUD
  const hud = (x, y, w, h, t0, fn) => {
    const p = eo5(seg(t, t0, t0 + .6)); if (p <= 0) return;
    X.save(); X.globalAlpha = p; X.translate(x + w / 2, y + h / 2); X.scale(.9 + .1 * p, .9 + .1 * p); X.translate(-w / 2, -h / 2);
    rr(X, 0, 0, w, h, 18); X.fillStyle = 'rgba(8,24,64,.62)'; X.fill(); X.strokeStyle = rgba(SKY, .75); X.lineWidth = 2; X.stroke();
    X.fillStyle = RED; X.fillRect(0, 24, 5, 34);
    fn(w, h); X.restore();
  };
  hud(70, 400, 390, 230, .8, (w, h) => {
    X.font = '24px MONO'; X.fillStyle = ICE; X.fillText('AI WORKLOAD', 26, 50);
    for (let i = 0; i < 7; i++) { const v = .35 + .5 * Math.abs(Math.sin(t * 1.6 + i * 1.3)); X.fillStyle = i === 4 ? RED : SKY; X.fillRect(28 + i * 49, h - 26 - v * 120, 32, v * 120); }
  });
  hud(620, 560, 390, 180, 1.2, (w, h) => {
    X.font = '24px MONO'; X.fillStyle = ICE; X.fillText('STATUS', 26, 50);
    glow(X, 300, 42, 22, RED, .6 + .4 * Math.sin(t * 6)); glow(X, 300, 42, 7, '#fff', 1);
    X.fillStyle = '#fff'; X.font = '26px IDX'; X.fillText('LIVE', 322, 51);
    const pts = []; for (let i = 0; i <= 60; i++) { const xx = 26 + i * 5.6; pts.push([xx, 120 + 26 * Math.sin(i * .35 + t * 5) * Math.sin(i * .09 + t)]); }
    glowStroke(X, pts, SKY, 3, .9);
  });
  hud(140, 1000, 330, 120, 1.6, (w, h) => {
    X.font = '22px MONO'; X.fillStyle = ICE; X.fillText('NODES ONLINE', 26, 46);
    for (let i = 0; i < 12; i++) { X.fillStyle = (i <= Math.floor(seg(t, 1.8, 3.6) * 12)) ? SKY : 'rgba(255,255,255,.15)'; X.fillRect(26 + i * 24, 66, 18, 30); }
  });
  hud(610, 970, 340, 130, 2.0, (w, h) => {
    X.font = '22px MONO'; X.fillStyle = ICE; X.fillText('DEPLOYMENT', 26, 46);
    const p = eio(seg(t, 2.2, 4.4)); X.fillStyle = 'rgba(255,255,255,.15)'; X.fillRect(26, 70, 288, 16);
    const g = X.createLinearGradient(26, 0, 314, 0); g.addColorStop(0, SKY); g.addColorStop(1, RED); X.fillStyle = g; X.fillRect(26, 70, 288 * p, 16);
    X.fillStyle = '#fff'; X.font = '22px MONO'; X.fillText(p >= 1 ? 'COMPLETE' : Math.round(p * 100) + '%', 26, 116);
  });
  // reticle at VP
  const rp = eo(seg(t, .5, 1.4));
  if (rp > 0) {
    X.save(); X.globalAlpha = rp; X.translate(VX, VY); X.globalCompositeOperation = 'lighter';
    X.rotate(t * .5); X.strokeStyle = rgba(SKY, .9); X.lineWidth = 3; X.setLineDash([40, 22]); X.beginPath(); X.arc(0, 0, 130 * (1.3 - .3 * rp), 0, Math.PI * 2); X.stroke();
    X.rotate(-t * 1.2); X.strokeStyle = rgba(RED, .9); X.setLineDash([12, 30]); X.beginPath(); X.arc(0, 0, 96, 0, Math.PI * 2); X.stroke();
    X.restore();
  }
  bokeh(t, .5);
  finish(t);
}

// =====================================================================
// SCENE 3 – DESIGNED FOR EXPERTS : over-the-shoulder expert + holographic dashboard
// =====================================================================
const S3 = (() => { const r = rng(31), line = []; let v = .45; for (let i = 0; i <= 40; i++) { v = clamp(v + (r() - .44) * .14, .12, .9); line.push(v); } line[29] = .93; return { line, bars: [.42, .58, .5, .74, .66, .88] }; })();
function panel(x, y, w, h, a) { X.save(); X.globalAlpha = a; rr(X, x, y, w, h, 22); X.fillStyle = 'rgba(8,26,70,.55)'; X.fill(); X.strokeStyle = rgba(SKY, .7); X.lineWidth = 2; X.stroke(); X.restore(); }
function scene3(t) {
  background(t, 640); bokeh(t, .7);
  const z = 1 + .055 * eio(seg(t, 0, DUR));
  X.save(); X.translate(540, 700); X.scale(z, z); X.translate(-540, -700);
  // holographic grid backdrop
  X.save(); X.globalAlpha = .18; X.strokeStyle = SKY; X.lineWidth = 1; for (let x = 60; x < W; x += 60) { X.beginPath(); X.moveTo(x, 200); X.lineTo(x, 1100); X.stroke(); } for (let y = 200; y < 1100; y += 60) { X.beginPath(); X.moveTo(60, y); X.lineTo(1020, y); X.stroke(); } X.restore();
  // main chart
  const A = { x: 80, y: 230, w: 920, h: 470 };
  panel(A.x, A.y, A.w, A.h, eo5(seg(t, .05, .6)));
  X.save(); X.globalAlpha = eo5(seg(t, .05, .6));
  X.font = '24px MONO'; X.fillStyle = ICE; X.fillText('MODEL PERFORMANCE', A.x + 32, A.y + 52);
  X.fillStyle = RED; X.fillRect(A.x + 32, A.y + 66, 60, 4);
  X.strokeStyle = 'rgba(255,255,255,.09)'; for (let i = 1; i < 5; i++) { const y = A.y + 100 + i * 72; X.beginPath(); X.moveTo(A.x + 32, y); X.lineTo(A.x + A.w - 32, y); X.stroke(); }
  const pts = S3.line.map((v, i) => [A.x + 40 + i * (A.w - 80) / 40, A.y + A.h - 40 - v * (A.h - 170)]);
  const lp = eio(seg(t, .5, 2.6)); const part = partial(pts, lp);
  if (part.length > 1) {
    const g = X.createLinearGradient(0, A.y + 120, 0, A.y + A.h); g.addColorStop(0, rgba(SKY, .35)); g.addColorStop(1, rgba(SKY, 0));
    X.fillStyle = g; poly(X, part); X.lineTo(part[part.length - 1][0], A.y + A.h - 40); X.lineTo(part[0][0], A.y + A.h - 40); X.closePath(); X.fill();
    glowStroke(X, part, SKY, 4, 1); const e = part[part.length - 1]; glow(X, e[0], e[1], 26, '#ffffff', 1);
  }
  // insight marker
  const ip = eo5(seg(t, 3.0, 3.6));
  if (ip > 0) {
    const p = pts[29]; X.save(); X.globalCompositeOperation = 'lighter';
    X.strokeStyle = rgba(RED, ip); X.lineWidth = 4; X.beginPath(); X.arc(p[0], p[1], 20 + 30 * (1 - ip) + 6 * Math.sin(t * 6), 0, Math.PI * 2); X.stroke(); glow(X, p[0], p[1], 40, RED, ip); X.restore();
    X.globalAlpha = ip; X.beginPath(); X.arc(p[0], p[1] - 78, 34 * (.6 + .4 * ip), 0, Math.PI * 2); X.fillStyle = RED; X.shadowColor = RED; X.shadowBlur = 24; X.fill(); X.shadowBlur = 0;
    X.strokeStyle = '#fff'; X.lineWidth = 6; X.lineCap = 'round'; X.lineJoin = 'round'; poly(X, [[p[0] - 13, p[1] - 78], [p[0] - 3, p[1] - 67], [p[0] + 15, p[1] - 90]]); X.stroke();
    poly(X, [[p[0] - 12, p[1] - 43], [p[0] + 12, p[1] - 43], [p[0], p[1] - 28]]); X.fillStyle = RED; X.fill(); X.globalAlpha = 1;
  }
  X.restore();
  // bars panel
  const B = { x: 80, y: 730, w: 440, h: 300 }; const ba = eo5(seg(t, .35, .9));
  panel(B.x, B.y, B.w, B.h, ba);
  X.save(); X.globalAlpha = ba; X.font = '22px MONO'; X.fillStyle = ICE; X.fillText('SIGNALS', B.x + 28, B.y + 46);
  S3.bars.forEach((v, i) => { const p = eo(seg(t, .9 + i * .12, 1.9 + i * .12)); const bh = v * 190 * p; X.fillStyle = i === 5 ? RED : SKY; X.fillRect(B.x + 36 + i * 66, B.y + B.h - 28 - bh, 42, bh); });
  X.restore();
  // donut panel
  const D = { x: 560, y: 730, w: 440, h: 300 }; const da = eo5(seg(t, .5, 1.05));
  panel(D.x, D.y, D.w, D.h, da);
  X.save(); X.globalAlpha = da; X.font = '22px MONO'; X.fillStyle = ICE; X.fillText('CONFIDENCE', D.x + 28, D.y + 46);
  const dp = eio(seg(t, 1.0, 3.2)) * .94, cx = D.x + D.w / 2, cy = D.y + 175;
  X.lineWidth = 26; X.strokeStyle = 'rgba(255,255,255,.1)'; X.beginPath(); X.arc(cx, cy, 90, 0, Math.PI * 2); X.stroke();
  X.strokeStyle = SKY; X.lineCap = 'round'; X.beginPath(); X.arc(cx, cy, 90, -Math.PI / 2, -Math.PI / 2 + dp * Math.PI * 2); X.stroke();
  X.strokeStyle = RED; X.lineWidth = 8; X.beginPath(); X.arc(cx, cy, 58, -Math.PI / 2, -Math.PI / 2 + dp * Math.PI * 2 * .7); X.stroke();
  X.fillStyle = '#fff'; X.font = '46px IDB'; X.textAlign = 'center'; X.fillText(Math.round(dp * 100) + '%', cx, cy + 16); X.textAlign = 'left';
  X.restore();
  // scan line
  const sy = 230 + ((t * .45) % 1) * 800; X.save(); X.globalCompositeOperation = 'lighter'; const sg = X.createLinearGradient(0, sy - 40, 0, sy); sg.addColorStop(0, rgba(SKY, 0)); sg.addColorStop(1, rgba(SKY, .18)); X.fillStyle = sg; X.fillRect(80, sy - 40, 920, 40); X.restore();
  // focus reticle (expert's attention)
  const path = [[300, 900], [760, 880], [pts[18][0], pts[18][1]], [pts[29][0], pts[29][1]]];
  const fk = seg(t, .8, 3.0) * 3, fi = Math.min(2, Math.floor(fk)), ff = eio(fk - fi);
  const fpos = [lerp(path[fi][0], path[fi + 1][0], ff), lerp(path[fi][1], path[fi + 1][1], ff)];
  const fa = seg(t, .8, 1.2) * (1 - seg(t, 3.0, 3.3));
  if (fa > 0) { X.save(); X.globalAlpha = fa; X.strokeStyle = ICE; X.lineWidth = 3; X.translate(...fpos); X.rotate(t); for (let k = 0; k < 4; k++) { X.rotate(Math.PI / 2); X.beginPath(); X.arc(0, 0, 44, -.5, .5); X.stroke(); } X.restore(); }
  X.restore();
  // expert silhouette (parallax)
  const zs = 1 + .085 * eio(seg(t, 0, DUR));
  X.save(); X.translate(540, 1500); X.scale(zs, zs); X.translate(-540, -1500 + 10 * (1 - eo(seg(t, 0, 1.2))));
  const sil = new Path2D();
  sil.moveTo(60, 1920); sil.bezierCurveTo(70, 1500, 140, 1330, 330, 1270); sil.bezierCurveTo(420, 1245, 455, 1225, 462, 1180);
  sil.bezierCurveTo(430, 1150, 410, 1090, 410, 1030); sil.bezierCurveTo(410, 930, 470, 870, 540, 870); sil.bezierCurveTo(615, 870, 672, 930, 672, 1030);
  sil.bezierCurveTo(672, 1090, 652, 1150, 620, 1180); sil.bezierCurveTo(627, 1225, 662, 1245, 752, 1270); sil.bezierCurveTo(942, 1330, 1012, 1500, 1022, 1920); sil.closePath();
  const sg2 = X.createLinearGradient(0, 870, 0, 1920); sg2.addColorStop(0, '#071030'); sg2.addColorStop(1, '#02040e'); X.fillStyle = sg2; X.fill(sil);
  X.save(); X.globalCompositeOperation = 'lighter'; X.lineWidth = 3; X.strokeStyle = rgba(SKY, .75); X.shadowColor = SKY; X.shadowBlur = 24; X.stroke(sil); X.restore();
  // headset accent (red rim on ear)
  X.save(); X.globalCompositeOperation = 'lighter'; X.strokeStyle = rgba(RED, .85); X.lineWidth = 5; X.shadowColor = RED; X.shadowBlur = 20; X.beginPath(); X.arc(540, 1020, 150, Math.PI * 1.1, Math.PI * 1.9); X.stroke(); X.restore();
  X.restore();
  finish(t);
}

// =====================================================================
// SCENE 4 – FROM AI OUTPUT TO REAL VALUE : chaos -> AI lens -> clean insight chart
// =====================================================================
const S4 = (() => {
  const r = rng(41), N = 620, parts = [], tg = [];
  const bars = [.32, .45, .55, .68, .82, 1.0], bw = 92, gap = 34, x0 = 540 - (bars.length * bw + (bars.length - 1) * gap) / 2, base = 1170, maxH = 300, cell = 13;
  bars.forEach((v, b) => { const h = v * maxH; for (let yy = 0; yy < h; yy += cell) for (let xx = 0; xx < bw; xx += cell) tg.push([x0 + b * (bw + gap) + xx + cell / 2, base - yy - cell / 2, b]); });
  for (let i = 0; i < N; i++) parts.push({ x: 90 + r() * 900, y: 170 + r() * 420, ph: r() * 10, sp: .5 + r() * 2, s: 1.55 + r() * 1.5, c: r() < .2 ? RED : (r() < .5 ? '#ffffff' : SKY) });
  parts.sort((a, b) => a.s - b.s);
  // assign targets in order (bars build left->right, bottom->top)
  const step = tg.length / N; parts.forEach((p, i) => { p.t = tg[Math.floor(i * step)]; });
  const glyphs = []; for (let c = 0; c < 16; c++) glyphs.push({ x: 40 + c * 66, sp: 120 + r() * 160, off: r() * 600, ch: Array.from({ length: 14 }, () => r() < .5 ? (r() < .5 ? '0' : '1') : '0123456789ABCDEF'[Math.floor(r() * 16)]) });
  return { parts, bars, bw, gap, x0, base, maxH, glyphs, lens: [540, 700] };
})();
function scene4(t) {
  background(t, 960); bokeh(t, .5);
  X.save(); X.translate(0, 270);
  const L = S4.lens;
  // glyph rain (chaos)
  const ga = .5 * (1 - seg(t, 2.4, 3.4));
  if (ga > 0) { X.save(); X.font = '26px MONO'; X.textAlign = 'center'; S4.glyphs.forEach((g, i) => { g.ch.forEach((ch, k) => { const y = 120 + ((k * 34 + g.off + t * g.sp) % 520); X.fillStyle = rgba(k % 7 === 0 ? RED : SKY, ga * (y / 640)); X.fillText(ch, g.x, y); }); }); X.restore(); }
  // tangled lines among early particles
  const tl = 1 - seg(t, 1.6, 2.8);
  const pos = S4.parts.map(p => [p.x + 26 * Math.sin(t * p.sp + p.ph), p.y + 22 * Math.cos(t * p.sp * 1.3 + p.ph)]);
  if (tl > 0) { X.save(); X.strokeStyle = rgba(SKY, .16 * tl); X.lineWidth = 1.5; X.beginPath(); for (let i = 0; i < 160; i++) { const a = pos[i], b = pos[(i * 7 + 13) % S4.parts.length]; X.moveTo(...a); X.lineTo(...b); } X.stroke(); X.restore(); }
  // lens
  const lp = eo5(seg(t, .6, 1.4)), act = seg(t, 1.5, 2.2) * (1 - seg(t, 3.8, 4.6));
  if (lp > 0) {
    X.save(); X.globalAlpha = lp; X.translate(...L);
    X.save(); X.globalCompositeOperation = 'lighter'; glow(X, 0, 0, 230 + 60 * act, SKY, .5 + .4 * act); glow(X, 0, 0, 80, '#ffffff', .35 + .5 * act); X.restore();
    for (let k = 0; k < 2; k++) { X.save(); X.rotate((k ? -1 : 1) * t * .6 + k * .5); const R = k ? 70 : 104; const hx = []; for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2; hx.push([Math.cos(a) * R, Math.sin(a) * R]); } glowStroke(X, hx, k ? RED : SKY, 4, 1, true); X.restore(); }
    X.fillStyle = '#fff'; X.beginPath(); X.arc(0, 0, 16, 0, Math.PI * 2); X.fill();
    X.restore();
  }
  // particles
  X.save(); X.globalCompositeOperation = 'lighter';
  const solid = eo(seg(t, 4.0, 4.6));
  S4.parts.forEach((p, i) => {
    const k1 = ei(seg(t, p.s, p.s + .55)), k2 = eo(seg(t, p.s + .55, p.s + 1.25));
    let x, y, col = p.c, r = 9, a = .85;
    if (k1 < 1) { x = lerp(pos[i][0], L[0], k1); y = lerp(pos[i][1], L[1], k1); if (k1 > 0) r = 9 - 4 * k1; }
    else { const tg = p.t; x = lerp(L[0], tg[0], k2); y = lerp(L[1], tg[1], k2) + Math.sin(k2 * Math.PI) * -40; col = tg[2] === 5 ? RED : SKY; r = 5 + 3 * k2; a = .9 * (1 - solid * .85); }
    glow(X, x, y, r, col, a);
  });
  X.restore();
  // solid chart
  if (solid > 0) {
    X.save(); X.globalAlpha = solid;
    S4.bars.forEach((v, b) => { const x = S4.x0 + b * (S4.bw + S4.gap), h = v * S4.maxH; const g = X.createLinearGradient(0, S4.base - h, 0, S4.base); g.addColorStop(0, b === 5 ? RED2 : SKY); g.addColorStop(1, b === 5 ? '#8c0f16' : '#0a4a8a'); X.fillStyle = g; rr(X, x, S4.base - h, S4.bw - 6, h, [10, 10, 0, 0]); X.fill(); });
    X.fillStyle = 'rgba(255,255,255,.4)'; X.fillRect(S4.x0 - 20, S4.base + 4, S4.bars.length * (S4.bw + S4.gap) + 6, 3);
    X.restore();
    // trend arrow
    const ap = eio(seg(t, 4.3, 5.2));
    const pts = S4.bars.map((v, b) => [S4.x0 + b * (S4.bw + S4.gap) + S4.bw / 2 - 3, S4.base - v * S4.maxH - 46]);
    pts[pts.length - 1] = [pts[pts.length - 1][0] + 20, pts[pts.length - 1][1] - 20];
    if (ap > 0) {
      const pp = partial(pts, ap); glowStroke(X, pp, '#ffffff', 6, 1);
      const e = pp[pp.length - 1], q = pp[Math.max(0, pp.length - 2)], an = Math.atan2(e[1] - q[1], e[0] - q[0]);
      X.save(); X.translate(...e); X.rotate(an); X.fillStyle = '#fff'; poly(X, [[14, 0], [-20, -18], [-20, 18]]); X.closePath(); X.fill(); X.restore();
    }
    // value badge
    const vb = eo5(seg(t, 4.9, 5.4));
    if (vb > 0) {
      X.save(); X.globalAlpha = vb; X.translate(880, 800); X.scale(.7 + .3 * vb, .7 + .3 * vb);
      X.beginPath(); X.arc(0, 0, 52, 0, Math.PI * 2); X.fillStyle = RED; X.shadowColor = rgba(RED, .8); X.shadowBlur = 30; X.fill(); X.shadowBlur = 0;
      X.strokeStyle = '#fff'; X.lineWidth = 7; X.lineCap = 'round'; X.lineJoin = 'round'; poly(X, [[-20, 0], [-5, 16], [22, -16]]); X.stroke();
      X.fillStyle = '#fff'; X.font = '38px IDB'; X.textBaseline = 'middle'; X.fillText('VALUE', -46, 2);
      X.restore();
    }
  }
  // labels
  X.save(); X.font = '24px MONO'; X.textAlign = 'center';
  X.fillStyle = rgba('#ffffff', .6 * (1 - seg(t, 2.2, 3.0)) * seg(t, .2, .8)); X.fillText('RAW AI OUTPUT', 540, 150);
  X.fillStyle = rgba(ICE, .8 * seg(t, 3.4, 4.0)); X.fillText('ACTIONABLE INSIGHT', 540, 1225);
  X.restore();
  X.restore();
  finish(t);
}

// =====================================================================
// SCENE 5 – BRIDGING AI & HUMAN EXPERTISE : human profile <-> AI profile, light bridge
// =====================================================================
const PROF = [[.28, 1.30], [.27, 1.10], [.18, .95], [.10, .76], [.07, .56], [.11, .36], [.21, .19], [.37, .07], [.55, .035], [.70, .075], [.80, .16], [.86, .29], [.885, .40], [.875, .465], [.905, .53], [.955, .615], [.968, .655], [.925, .685], [.915, .725], [.948, .758], [.918, .79], [.94, .82], [.905, .86], [.915, .905], [.862, .955], [.77, .978], [.705, 1.02], [.685, 1.12], [.72, 1.30]];
function profPath(x0, y0, s, flip) {
  const P = PROF.map(([u, v]) => [flip ? x0 + (1 - u) * s : x0 + u * s, y0 + v * s]);
  const p = new Path2D(); p.moveTo(...P[0]);
  for (let i = 0; i < P.length - 1; i++) { const a = P[Math.max(0, i - 1)], b = P[i], c = P[i + 1], d = P[Math.min(P.length - 1, i + 2)]; p.bezierCurveTo(b[0] + (c[0] - a[0]) / 6, b[1] + (c[1] - a[1]) / 6, c[0] - (d[0] - b[0]) / 6, c[1] - (d[1] - b[1]) / 6, c[0], c[1]); }
  const last = P[P.length - 1]; p.lineTo(last[0], y0 + 1.6 * s); p.lineTo(P[0][0], y0 + 1.6 * s); p.closePath(); return p;
}
const HS = 400, HY = 470, HL = 30, HR = W - 30 - HS;
let S5P = null;
function s5Prep() {
  if (S5P) return S5P;
  const c = mk(W, H), g = c.getContext('2d'), pa = profPath(HR, HY, HS, true), r = rng(51), dots = [];
  let tries = 0; while (dots.length < 230 && tries < 20000) { tries++; const x = HR + r() * HS, y = HY + r() * HS * 1.22; if (g.isPointInPath(pa, x, y) && dots.every(d => Math.hypot(d[0] - x, d[1] - y) > 22)) dots.push([x, y, r()]); }
  const links = []; dots.forEach((d, i) => { const ns = dots.map((e, j) => [Math.hypot(e[0] - d[0], e[1] - d[1]), j]).filter(q => q[1] !== i).sort((a, b) => a[0] - b[0]).slice(0, 3); ns.forEach(([dist, j]) => { if (j > i && dist < 70) links.push([i, j]); }); });
  const hum = []; tries = 0; const ph = profPath(HL, HY, HS, false); while (hum.length < 40 && tries < 9000) { tries++; const x = HL + r() * HS, y = HY + r() * HS * .9; if (g.isPointInPath(ph, x, y)) hum.push([x, y, r()]); }
  return S5P = { dots, links, hum, pa, ph };
}
function scene5(t) {
  background(t, 900); bokeh(t, .6);
  X.save(); X.translate(0, 190);
  const P = s5Prep();
  // faint background network
  X.save(); X.globalAlpha = .12; X.strokeStyle = SKY; X.lineWidth = 1; const br = rng(5); X.beginPath(); for (let i = 0; i < 40; i++) { X.moveTo(br() * W, br() * 1200); X.lineTo(br() * W, br() * 1200); } X.stroke(); X.restore();
  const sl = eo5(seg(t, 0, 1.2));
  // human (left)
  X.save(); X.translate(-70 * (1 - sl), 0); X.globalAlpha = sl;
  const hg = X.createLinearGradient(HL, 0, HL + HS, 0); hg.addColorStop(0, '#060c24'); hg.addColorStop(1, '#1a1440'); X.fillStyle = hg; X.fill(P.ph);
  X.save(); X.clip(P.ph); radial(HL + HS * .55, HY + HS * .35, 260, RED, .35 + .15 * Math.sin(t * 2)); X.restore();
  X.save(); X.globalCompositeOperation = 'lighter'; X.strokeStyle = rgba(RED, .95); X.lineWidth = 4; X.shadowColor = RED; X.shadowBlur = 30; X.stroke(P.ph); X.restore();
  // blue sparks received from AI
  const rc = seg(t, 3.0, 4.5);
  X.save(); X.globalCompositeOperation = 'lighter'; P.hum.forEach((h, i) => { if (h[2] < rc) glow(X, h[0], h[1], 14 + 6 * Math.sin(t * 4 + i), SKY, .85); }); X.restore();
  X.restore();
  // AI (right)
  X.save(); X.translate(70 * (1 - sl), 0);
  X.save(); X.globalAlpha = .55 * sl; X.fillStyle = '#071a44'; X.fill(P.pa); X.restore();
  X.save(); X.globalCompositeOperation = 'lighter'; X.globalAlpha = sl; X.strokeStyle = rgba(SKY, .9); X.lineWidth = 3; X.setLineDash([3, 9]); X.lineCap = 'round'; X.stroke(P.pa); X.restore();
  const dp = seg(t, .2, 1.8);
  X.save(); X.globalCompositeOperation = 'lighter';
  X.strokeStyle = rgba(SKY, .32); X.lineWidth = 1.5; X.beginPath(); P.links.forEach(([i, j]) => { if (P.dots[i][2] < dp && P.dots[j][2] < dp) { X.moveTo(P.dots[i][0], P.dots[i][1]); X.lineTo(P.dots[j][0], P.dots[j][1]); } }); X.stroke();
  const rr2 = seg(t, 3.0, 4.6);
  P.dots.forEach((d, i) => { if (d[2] >= dp) return; const red = d[2] < rr2 * .25; glow(X, d[0], d[1], 9 + 4 * Math.sin(t * 3 + i), red ? RED : ICE, .9); });
  X.restore();
  X.restore();
  // bridge
  const A = [HL + HS * .9, HY + HS * .36], B = [HR + HS * .1, HY + HS * .36], M = [540, HY + HS * .3];
  const cL = [[A[0], A[1]], [A[0] + 40, A[1] - 90], [M[0] - 60, M[1] - 80], M], cR = [[B[0], B[1]], [B[0] - 40, B[1] - 90], [M[0] + 60, M[1] - 80], M];
  const curve = (c, n = 40) => Array.from({ length: n + 1 }, (_, k) => bz(c[0], c[1], c[2], c[3], k / n));
  const pl = curve(cL), pr = curve(cR);
  const gp = eio(seg(t, 1.2, 2.4));
  if (gp > 0) { glowStroke(X, partial(pl, gp), RED, 4, 1); glowStroke(X, partial(pr, gp), SKY, 4, 1); const e1 = along(pl, gp), e2 = along(pr, gp); X.save(); X.globalCompositeOperation = 'lighter'; glow(X, e1[0], e1[1], 30, '#ffffff', gp < 1 ? 1 : 0); glow(X, e2[0], e2[1], 30, '#ffffff', gp < 1 ? 1 : 0); X.restore(); }
  // lower bridge strands
  const lp2 = eio(seg(t, 1.6, 2.8));
  const pl2 = curve([[HL + HS * .93, HY + HS * .6], [470, HY + HS * .75], [610, HY + HS * .75], [HR + HS * .07, HY + HS * .6]]);
  if (lp2 > 0) { glowStroke(X, partial(pl2, lp2), mix(RED, SKY, .5), 2.5, .7); }
  // meeting flash + orb
  const meet = seg(t, 2.35, 2.6), orb = eo5(seg(t, 2.4, 3.2));
  if (meet > 0 && meet < 1) { X.save(); X.globalCompositeOperation = 'lighter'; glow(X, M[0], M[1], 600 * meet, '#ffffff', .8 * (1 - meet)); X.restore(); }
  if (orb > 0) {
    X.save(); X.globalCompositeOperation = 'lighter'; const pu = 1 + .08 * Math.sin(t * 4);
    glow(X, M[0], M[1], 190 * orb * pu, BLUE, .8); glow(X, M[0] - 20, M[1], 120 * orb * pu, RED, .6); glow(X, M[0], M[1], 60 * orb * pu, '#ffffff', 1);
    X.translate(...M); X.rotate(t * .9); X.strokeStyle = rgba(ICE, .8 * orb); X.lineWidth = 2.5; X.setLineDash([26, 14]); X.beginPath(); X.arc(0, 0, 96 * orb, 0, Math.PI * 2); X.stroke();
    X.rotate(-t * 2); X.strokeStyle = rgba(RED, .8 * orb); X.setLineDash([8, 20]); X.beginPath(); X.arc(0, 0, 128 * orb, 0, Math.PI * 2); X.stroke();
    X.restore();
    // flowing exchange particles
    X.save(); X.globalCompositeOperation = 'lighter';
    for (let k = 0; k < 10; k++) { const f = ((t - 2.4) * .55 + k / 10) % 1; const p1 = along(pl, f), p2 = along(pr, f), p3 = along(pl2, f), p4 = along(pl2, 1 - f); glow(X, p1[0], p1[1], 13, '#ffd2d2', orb); glow(X, p2[0], p2[1], 13, ICE, orb); glow(X, p3[0], p3[1], 9, RED, orb * lp2); glow(X, p4[0], p4[1], 9, SKY, orb * lp2); }
    X.restore();
  }
  // labels
  X.save(); X.font = '26px MONO'; X.textAlign = 'center'; const la = seg(t, 1.0, 1.6);
  X.fillStyle = rgba('#ffd9d9', .85 * la); X.fillText('HUMAN', HL + HS * .45, HY + HS * 1.45);
  X.fillStyle = rgba(ICE, .85 * la); X.fillText('AI', HR + HS * .55, HY + HS * 1.45);
  X.restore();
  X.restore();
  finish(t);
}

// ---------- entry ----------
const SCENES = { 1: scene1, 2: scene2, 3: scene3, 4: scene4, 5: scene5 };
function draw(s, t, variant) {
  X.setTransform(1, 0, 0, 1, 0, 0); X.globalAlpha = 1; X.globalCompositeOperation = 'source-over'; X.filter = 'none';
  X.textAlign = 'left'; X.textBaseline = 'alphabetic'; X.setLineDash([]); X.lineCap = 'butt';
  X.clearRect(0, 0, W, H);
  const ft = X.fillText; if (variant === 'clean') X.fillText = () => {};
  if (variant !== 'alpha') { X.save(); SCENES[s](t); X.restore(); X.setLineDash([]); X.textAlign = 'left'; X.textBaseline = 'alphabetic'; }
  X.fillText = ft;
  if (variant === 'full' || variant === 'alpha') title(t, TITLES[s]);
}
window.draw = draw;
window.ready = Promise.all(['IDB', 'IDX', 'ISB', 'MONO'].map(f => document.fonts.load(`40px ${f}`)));
