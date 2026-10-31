'use strict';
// Episode 2, black theme, flat 2D motion graphics. Act 1 (hook) and act 2 (everyone is different).
Object.assign(THEMES, {
  night:   ['#000000', '#0c0c12', '#FFC857'],
  dusk:    ['#030304', '#171108', '#FFB36B'],
  sepia:   ['#030302', '#14100a', '#E9C58B'],
  sunrise: ['#000000', '#16110a', '#FFE08A'],
  day:     ['#000000', '#0a1018', '#8CD8FF'],
  royal:   ['#000000', '#120f1c', '#FFD66B'],
  green:   ['#000000', '#07130f', '#3DDC97'],
  crimson: ['#050102', '#1a060a', '#FF5A6E'],
});
lgrad('gBeam', [[0, '#FFF3C4', .55], [1, '#FFF3C4', 0]], 0, 0, 1, 0);
const GOLD = '#FFC857', RED = '#FF4D5E', GREEN = '#3DDC97', SKY = '#6EC8FF', INK = '#0a0a10';

// ------------------------------------------------------------------ assets
A.car = (parent, o = {}) => {
  const g = gnode(parent), parts = g.parts = {}, c1 = o.color || RED, c2 = o.color2 || '#A31B30';
  parts.beam = P(g, 'M 214 2 L 700 -80 L 700 90 Z', 'url(#gBeam)'); if (o.beam === false) parts.beam.setAttribute('opacity', 0);
  el('ellipse', { cx: 0, cy: 54, rx: 230, ry: 9, fill: 'rgba(255,255,255,.07)' }, g);
  P(g, 'M -215 8 L -232 -12 L -190 -12 Z', c2);
  P(g, 'M -215 30 L -215 6 Q -192 -8 -122 -12 L -62 -40 Q 0 -60 72 -40 L 132 -12 Q 196 -8 218 10 L 218 30 Z', c1);
  P(g, 'M -215 30 L 218 30 L 214 44 L -210 44 Z', c2);
  P(g, 'M -52 -31 Q 6 -49 64 -31 L 104 -12 L -88 -12 Z', '#0b0f18');
  P(g, 'M -40 -30 Q 6 -42 52 -30', 'none', { stroke: 'rgba(255,255,255,.35)', 'stroke-width': 3, 'stroke-linecap': 'round' });
  P(g, 'M -140 -2 Q 0 -14 160 -2', 'none', { stroke: 'rgba(255,255,255,.28)', 'stroke-width': 3, 'stroke-linecap': 'round' });
  L(g, 4, -12, 4, 30, 'rgba(0,0,0,.4)', 3);
  R(g, 196, 2, 22, 9, '#FFF1B8', 4); R(g, -218, 4, 10, 10, '#FF3B4E', 3);
  parts.wheels = [-118, 122].map(x => {
    C(g, x, 38, 38, '#050509'); const w = gnode(g); C(w, 0, 0, 31, '#15151c'); C(w, 0, 0, 21, '#C9CFE8');
    for (let i = 0; i < 5; i++) { const a = i * Math.PI * 2 / 5; L(w, 0, 0, Math.cos(a) * 19, Math.sin(a) * 19, '#5B6591', 5); }
    C(w, 0, 0, 6, '#2a2a33'); T(w, { x, y: 38 }); return w;
  });
  g.spin = (lt, sp) => parts.wheels.forEach(w => T(w, { r: lt * sp }));
  return g;
};
function skyline(parent, seed, fill, hMin, hMax, baseY) {
  const g = gnode(parent), r = rng(seed); let x = -100;
  while (x < 2300) {
    const w = 90 + r() * 120, h = hMin + r() * (hMax - hMin); R(g, x, baseY - h, w, h, fill);
    for (let wy = baseY - h + 20; wy < baseY - 30; wy += 34) for (let wx = x + 14; wx < x + w - 22; wx += 30) if (r() < .32) R(g, wx, wy, 12, 16, r() < .5 ? 'rgba(255,200,87,.8)' : 'rgba(255,255,255,.55)', 2);
    x += w + 6;
  }
  return g;
}
function bill(parent, s = 1) { const g = gnode(parent); R(g, -48 * s, -26 * s, 96 * s, 52 * s, '#1f9d62', 6 * s, { stroke: '#8CF0C4', 'stroke-width': 3 }); C(g, 0, 0, 15 * s, 'none', { stroke: '#8CF0C4', 'stroke-width': 3 }); txt(g, '₹', { size: 24 * s, font: 'en', fill: '#CFFBE6', y: 9 * s }); return g; }
function head(parent, o = {}) { // simple silhouette bust, reuses the person asset with dark clothing
  return A.person(parent, Object.assign({ skin: 'tan', hair: 'short', shirt: '#2a2f48', shirt2: '#1c2034', mood: 'smile' }, o));
}
function dust(c, n, seed, col = '#fff') {
  const r = rng(seed), it = []; for (let i = 0; i < n; i++) { const d = C(c.g, 0, 0, 3 + r() * 4, col, { opacity: 0 }); it.push({ d, x: r() * 1920, y: 200 + r() * 600, ph: r() * 6, t0: r() * 1.2 }); }
  return lt => it.forEach(o => { const k = lt - o.t0; o.d.setAttribute('cx', o.x + Math.sin(k + o.ph) * 30); o.d.setAttribute('cy', o.y - k * 25); o.d.setAttribute('opacity', k > 0 ? .5 * Math.min(1, k) : 0); });
}

// ============================================================== 1.1 expensive car passes by
V.carPass = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sk2 = skyline(g, 9, '#0c0d14', 120, 300, 780), sk1 = skyline(g, 3, '#161824', 90, 220, 780);
  R(g, -100, 780, 2200, 320, '#050507'); R(g, -100, 776, 2200, 5, 'rgba(255,200,87,.6)');
  const dash = gnode(g); for (let i = 0; i < 18; i++) R(dash, i * 160, 930, 90, 10, 'rgba(255,255,255,.45)', 4);
  const car = gnode(g); const cr = A.car(car, { color: RED }); T(car, { x: -600, y: 700, s: 1.55 });
  const lines = Array.from({ length: 6 }, (_, i) => L(g, 0, 0, 0, 0, 'rgba(255,255,255,.35)', 4));
  const price = gnode(g); const pt = txt(price, tx.price, { size: 120, font: 'en', fill: GOLD, weight: 700, stroke: '#000', sw: 14 }); T(price, { x: 960, y: 260, o: 0 });
  const tag = pill(g, tx.tag, { size: 44, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }); T(tag, { x: 960, y: 140, o: 0 });
  const cx = p => p < .5 ? lerp(-520, 960, E.out3(p / .5)) : lerp(960, 2500, E.in3((p - .5) / .5));
  c.cue(.05, 'whoosh'); c.cue(dur * .45, 'ding'); c.cue(dur * .55, 'whoosh');
  return lt => {
    const p = clamp(lt / dur), x = cx(p), v = (cx(clamp(p + .01)) - x) / (dur * .01) / 30;
    T(sk2, { x: -lt * 14 }); T(sk1, { x: -lt * 40 }); dash.setAttribute('transform', `translate(${-(lt * 420 * (.2 + Math.abs(v) / 30)) % 160} 0)`);
    T(car, { x, y: 700 + bob(lt, 3, 3), s: 1.55 }); cr.spin(lt, Math.abs(v) * 40 + 40);
    lines.forEach((l, i) => { const len = Math.min(380, Math.abs(v) * 14); l.setAttribute('x1', x - 360 - i * 18); l.setAttribute('x2', x - 360 - len - i * 18); l.setAttribute('y1', l.setAttribute('y2', 640 + i * 22) || 640 + i * 22); l.setAttribute('y2', 640 + i * 22); l.setAttribute('opacity', len > 20 ? .5 : 0); });
    pop(price, lt, dur * .42, { x: 960, y: 260, big: true }); rise(tag, lt, .2, { x: 960, y: 140, dy: -30 });
  };
};

// ============================================================== 1.2 "what's the first thing we think?"
V.thoughtFirst = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = head(g, { mood: 'think' }); T(me, { x: 560, y: 860, s: 1.7 });
  const bub = gnode(g); A.thought(bub, { w: 760, h: 380, fill: '#17171f' }); bub.querySelectorAll('ellipse,circle').forEach(n => { n.setAttribute('stroke', 'rgba(255,255,255,.55)'); n.setAttribute('stroke-width', 4); }); txt(bub, '?', { size: 280, font: 'en', fill: GOLD, y: 90, weight: 700 }); T(bub, { x: 1250, y: 430, o: 0 });
  const qs = [0, 1, 2, 3].map(i => { const q = gnode(g); txt(q, '?', { size: 90 + i * 14, font: 'en', fill: i % 2 ? GOLD : '#fff', y: 30 }); T(q, { o: 0 }); return q; });
  const qp = [[880, 230], [1700, 250], [1760, 560], [820, 500]];
  const lab = pill(g, tx.q, { size: 60, bg: GOLD, fill: '#1b1100' }); T(lab, { x: 1250, y: 780, o: 0 }); const hint = pill(g, tx.hint, { size: 40, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 }); T(hint, { x: 1250, y: 120, o: 0 });
  c.cue(.3, 'pop'); qs.forEach((q, i) => c.cue(.6 + i * .3, 'pop', .5)); c.cue(dur * .6, 'ping');
  return lt => {
    me.idle(lt); const e = E.out3(seg(lt, 0, .5)); T(me, { x: lerp(380, 560, e), y: 860, s: 1.7, o: e });
    pop(bub, lt, .3, { x: 1250, y: 430 + bob(lt, 8, .5), big: true }); qs.forEach((q, i) => pop(q, lt, .6 + i * .3, { x: qp[i][0], y: qp[i][1] + bob(lt, 10, .7, i), r: (i - 1.5) * 10 }));
    rise(lab, lt, dur * .5, { x: 1250, y: 780, dy: 30 }); rise(hint, lt, .1, { x: 1250, y: 120, dy: -20 });
  };
};

// ============================================================== 1.3 "he has too much money, wasting it"
V.judgeBubble = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = head(g, { mood: 'angry', skin: 'brown' }); T(me, { x: 480, y: 860, s: 1.7 });
  const sb = gnode(g); A.bubble(sb, { w: 980, h: 250, fill: '#fff', tail: 'bl' }); txt(sb, tx.say, { size: 80, fill: '#12121a', y: 28 }); T(sb, { x: 1290, y: 300, o: 0 });
  const bills = Array.from({ length: 7 }, (_, i) => { const b = bill(g, .9); T(b, { o: 0 }); return b; });
  const flames = []; const tg = pill(g, tx.tag, { size: 52, bg: RED, fill: '#fff' }); T(tg, { x: 1290, y: 700, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .35, 'whoosh'); c.cue(dur * .6, 'error');
  return lt => {
    me.idle(lt, 2); T(me, { x: 480, y: 860, s: 1.7 }); pop(sb, lt, .2, { x: 1290, y: 300, big: true });
    bills.forEach((b, i) => { const k = lt - (dur * .3 + i * .18); if (k < 0) { T(b, { o: 0 }); return; } T(b, { x: 1000 + k * 330 + i * 30, y: 640 - k * 120 - Math.sin(k * 3 + i) * 40, r: k * 120 + i * 20, o: 1 - clamp(k / 1.8), s: 1 }); });
    rise(tg, lt, dur * .55, { x: 1290, y: 700, dy: 30 });
  };
};

// ============================================================== 1.4 "is it really a waste?"
V.wasteQ = c => {
  const { g, S, dur } = c, tx = S.txt;
  dust(c, 18, 5);
  const car = gnode(g); const cr = A.car(car, { color: RED, beam: false }); T(car, { x: 960, y: 760, s: 1.2 });
  const big = fitRow(g, tx.main, { size: 150, fill: '#fff', stroke: '#000', sw: 14, maxW: 1500 }); T(big, { x: 960, y: 360 });
  const w = gnode(g); const wt = txt(w, tx.a, { size: 90, fill: RED, y: 30 }); const ln = L(w, -180, 0, 180, 0, RED, 10); T(w, { x: 960, y: 560, o: 0 });
  const qm = gnode(g); txt(qm, tx.b, { size: 230, font: 'en', fill: GOLD, y: 80, weight: 700 }); T(qm, { x: 1500, y: 520, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .45, 'stamp'); c.cue(dur * .7, 'riser', .6);
  return lt => {
    big.__row.__words.forEach((wd, i) => pop(wd, lt, .1 + i * .25, { x: wd.__x, y: 0, d: .5, big: true }));
    pop(car, lt, .0, { x: 960, y: 760 + bob(lt, 4, 1), s: 1.2, d: .5 }); cr.spin(lt, 0);
    pop(w, lt, dur * .4, { x: 960, y: 560, big: true }); ln.setAttribute('opacity', seg(lt, dur * .5, dur * .6)); pop(qm, lt, dur * .65, { x: 1500, y: 520 + bob(lt, 10, .8), big: true, r: bob(lt, 6, .5) });
  };
};

// ============================================================== 1.5 "or does he think differently?"
V.otherThought = c => {
  const { g, S, dur } = c, tx = S.txt;
  const L_ = gnode(g), R_ = gnode(g); T(L_, { x: 520, y: 520 }); T(R_, { x: 1400, y: 520 });
  const a = head(L_, { mood: 'flat' }); T(a, { x: 0, y: 330, s: 1.4 }); const ab = gnode(L_); A.thought(ab, { w: 520, h: 250, fill: '#2a0d12' }); txt(ab, 'డబ్బు వృధా', { size: 64, fill: '#FF8A94', y: 20 }); T(ab, { x: 0, y: -270, s: 1 });
  const b = head(R_, { mood: 'grin', skin: 'brown' }); T(b, { x: 0, y: 330, s: 1.4 }); const bb = gnode(R_); A.thought(bb, { w: 520, h: 250, fill: '#1c1c24' }); bb.querySelectorAll('ellipse,circle').forEach(n => { n.setAttribute('stroke', 'rgba(255,200,87,.7)'); n.setAttribute('stroke-width', 4); }); const bulb = gnode(bb); const bulbA = A.bulb(bulb, {}); T(bulb, { y: -6, s: .55 }); T(bb, { x: 0, y: -270 });
  const vs = gnode(g); C(vs, 0, 0, 62, GOLD); txt(vs, 'VS', { size: 50, font: 'en', fill: '#1b1100', y: 17, weight: 700 }); T(vs, { x: 960, y: 520, o: 0 });
  const tg = pill(g, tx.tag, { size: 52, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 }); T(tg, { x: 960, y: 110, o: 0 });
  c.cue(.1, 'pop'); c.cue(dur * .45, 'pop'); c.cue(dur * .6, 'switch'); c.cue(dur * .6 + .1, 'ding');
  return lt => {
    a.idle(lt); b.idle(lt, 1); pop(ab, lt, .15, { x: 0, y: -270 + bob(lt, 6, .5), big: true }); pop(bb, lt, dur * .4, { x: 0, y: -270 + bob(lt, 6, .5, 1), big: true });
    bulbA.setOn(E.out3(seg(lt, dur * .6, dur * .6 + .35))); pop(vs, lt, dur * .35, { x: 960, y: 520, big: true }); rise(tg, lt, .05, { x: 960, y: 110, dy: -20 });
  };
};

// ============================================================== 1.6 title: one car, two thoughts
V.titleOneCar = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 22, fill: 'rgba(255,200,87,.08)' }); T(rays, { x: 960, y: 520 });
  const glowc = C(g, 960, 520, 520, 'url(#gGlowGold)', { opacity: .3 });
  const lc = gnode(g), rc = gnode(g);
  const carL = gnode(lc); A.car(carL, { color: RED, beam: false }); const carR = gnode(rc); A.car(carR, { color: '#FFC857', color2: '#B07A10', beam: false });
  const clipL = el('clipPath', { id: 'cl' + Math.floor(Math.random() * 1e6) }, DEFS); R(clipL, -400, -200, 400, 400, '#000'); const clipR = el('clipPath', { id: 'cr' + Math.floor(Math.random() * 1e6) }, DEFS); R(clipR, 0, -200, 400, 400, '#000');
  lc.setAttribute('clip-path', `url(#${clipL.id})`); rc.setAttribute('clip-path', `url(#${clipR.id})`);
  const l1 = fitRow(g, tx.l1, { size: 120, fill: '#fff', stroke: '#000', sw: 14, maxW: 1200 }); T(l1, { x: 960, y: 190 });
  const l2 = fitRow(g, tx.l2, { size: 140, fill: GOLD, stroke: '#000', sw: 16, maxW: 1500 }); T(l2, { x: 960, y: 880 });
  const bs = rain(c, 14, 4, it => A.coin(it, { r: 26 }));
  c.cue(.05, 'impact'); c.flash(.02, .3, '#fff', .45); c.cue(.9, 'sparkle'); c.cue(1.6, 'tada');
  return lt => {
    T(rays, { x: 960, y: 520, r: lt * 6 });
    const open = E.inOut(seg(lt, dur * .35, dur * .7)); T(lc, { x: 960 - open * 300, y: 560, s: 1.8, o: seg(lt, 0, .3) }); T(rc, { x: 960 + open * 300, y: 560, s: 1.8, o: seg(lt, 0, .3) });
    l1.__row.__words.forEach((w, i) => pop(w, lt, .2 + i * .3, { x: w.__x, y: 0, d: .5 })); l2.__row.__words.forEach((w, i) => pop(w, lt, .9 + i * .3, { x: w.__x, y: 0, d: .6, big: true }));
    bs(Math.max(0, lt - .5));
  };
};

// ============================================================== 2.1 no two people are alike
V.noTwoAlike = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.tag, { y: 120, size: 48, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 });
  const defs = [[{ skin: 'tan', hair: 'grey', glasses: true, shirt: '#3a4466' }, 380, '#4CC9F0'], [{ skin: 'brown', hair: 'cap', capColor: RED, capColor2: '#a31b30', shirt: '#1d4d44' }, 960, GOLD], [{ skin: 'light', hair: 'bun', hairColor: '#4a2a1c', shirt: '#5b2f4c' }, 1540, '#FF8AD0']];
  const ps = defs.map(([o, x, col], i) => { const gr = gnode(g); const p = head(gr, o); T(p, { y: 340, s: 1.3 }); const w = gnode(gr); A.wallet(w, { color: col }); T(w, { x: 0, y: 380 - 10, s: .5 }); const lt = C(gr, 0, -10, 8, col); lt.setAttribute('opacity', 0); T(gr, { x, y: 480, o: 0 }); gr.__p = p; gr.__col = col; return gr; });
  const ne = gnode(g); C(ne, 0, 0, 56, GOLD); txt(ne, '≠', { size: 90, font: 'en', fill: '#1b1100', y: 28 }); T(ne, { x: 670, y: 420, o: 0 }); const ne2 = gnode(g); C(ne2, 0, 0, 56, GOLD); txt(ne2, '≠', { size: 90, font: 'en', fill: '#1b1100', y: 28 }); T(ne2, { x: 1250, y: 420, o: 0 });
  const mt = fitRow(g, tx.main, { size: 100, fill: '#fff', stroke: '#000', sw: 12, maxW: 1400 }); T(mt, { x: 960, y: 880 });
  c.cue(.1, 'pop'); c.cue(.4, 'pop'); c.cue(.7, 'pop'); c.cue(dur * .6, 'stamp');
  return lt => {
    rise(top, lt, .05, { x: 960, y: 120, dy: -20 }); ps.forEach((gr, i) => { pop(gr, lt, .1 + i * .3, { x: [380, 960, 1540][i], y: 480 + bob(lt, 6, .5, i), big: true }); gr.__p.idle(lt, i); });
    pop(ne, lt, dur * .55, { x: 670, y: 420, big: true }); pop(ne2, lt, dur * .62, { x: 1250, y: 420, big: true }); mt.__row.__words.forEach((w, i) => pop(w, lt, dur * .5 + i * .15, { x: w.__x, y: 0, d: .5 }));
  };
};

// ============================================================== 2.2 experiences, goals, priorities
V.threeTraits = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 120, size: 52, bg: GOLD, fill: '#1b1100', stroke: 'none' });
  const cards = [[tx.t1, 'pol'], [tx.t2, 'target'], [tx.t3, 'list']].map(([lab, k], i) => {
    const gr = gnode(g); A.card(gr, 480, 560, { fill: 'rgba(255,255,255,.06)', stroke: 'rgba(255,200,87,.45)', sw: 3, shadow: true });
    const ic = gnode(gr);
    if (k === 'pol') { A.polaroid(ic, { emoji: '🌍', bg: '#2a3a6a' }); T(ic, { s: 1.5, r: -6, y: -40 }); }
    if (k === 'target') { [150, 105, 60].forEach((r, j) => C(ic, 0, 0, r, j % 2 ? '#fff' : RED)); C(ic, 0, 0, 22, GOLD); L(ic, 0, 0, 120, -120, '#fff', 8); P(ic, 'M 100 -140 L 140 -100 L 150 -150 Z', GOLD); T(ic, { y: -40, s: .95 }); }
    if (k === 'list') { [0, 1, 2].forEach(j => { C(ic, -110, -90 + j * 90, 22, j === 0 ? GOLD : 'rgba(255,255,255,.25)'); R(ic, -70, -104 + j * 90, 190 - j * 30, 28, j === 0 ? '#fff' : 'rgba(255,255,255,.35)', 14); }); T(ic, { y: -30 }); }
    const p = pill(gr, lab, { size: 52, bg: GOLD, fill: '#1b1100' }); T(p, { y: 215 }); T(gr, { x: 360 + i * 600, y: 520, o: 0 }); return gr;
  });
  const t0 = [dur * .12, dur * .38, dur * .64]; t0.forEach(t => c.cue(t, 'pop'));
  return lt => { rise(top, lt, .05, { x: 960, y: 120, dy: -20 }); cards.forEach((gr, i) => { pop(gr, lt, t0[i], { x: 360 + i * 600, y: 520 + bob(lt, 6, .5, i), big: true }); }); };
};

// ============================================================== 2.3 savings vs experiences
V.saverVsExp = c => {
  const { g, S, dur } = c, tx = S.txt;
  const L_ = gnode(g), R_ = gnode(g); A.card(L_, 700, 620, { fill: 'rgba(61,220,151,.07)', stroke: 'rgba(61,220,151,.55)', sw: 3 }); A.card(R_, 700, 620, { fill: 'rgba(110,200,255,.07)', stroke: 'rgba(110,200,255,.55)', sw: 3 });
  T(L_, { x: 480, y: 520, o: 0 }); T(R_, { x: 1440, y: 520, o: 0 });
  const pig = gnode(L_); A.piggy(pig, {}); T(pig, { y: -20, s: 1.2 }); const lp = pill(L_, tx.a, { size: 56, bg: GREEN, fill: '#04281b' }); T(lp, { y: 230 });
  const plane = gnode(R_); const pb = gnode(plane); P(pb, 'M -150 10 L 140 -20 Q 190 -22 190 0 Q 190 22 140 24 L -150 40 L -120 12 Z', '#fff'); P(pb, 'M -20 6 L -80 -110 L -40 -110 L 60 0 Z', '#C9CFE8'); P(pb, 'M -20 30 L -80 140 L -40 140 L 60 40 Z', '#9AA6D6'); P(pb, 'M -150 10 L -176 -44 L -148 -44 L -108 8 Z', SKY); [0, 1, 2, 3, 4].forEach(i => C(pb, 60 + i * 20, 0, 6, '#2b3a6a')); T(plane, { y: -20, s: 1.15 });
  const trail = P(R_, 'M -330 120 Q -150 20 0 60', 'none', { stroke: 'rgba(110,200,255,.45)', 'stroke-width': 6, 'stroke-dasharray': '4 18', 'stroke-linecap': 'round' });
  const rp = pill(R_, tx.b, { size: 56, bg: SKY, fill: '#02283a' }); T(rp, { y: 230 });
  const vs = gnode(g); C(vs, 0, 0, 66, GOLD); txt(vs, tx.vs, { size: 52, font: 'en', fill: '#1b1100', y: 18, weight: 700 }); T(vs, { x: 960, y: 520, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .45, 'whoosh'); c.cue(dur * .8, 'pop');
  return lt => {
    pop(L_, lt, .1, { x: 480, y: 520, d: .5 }); pop(R_, lt, dur * .42, { x: 1440, y: 520, d: .5 }); pop(vs, lt, dur * .8, { x: 960, y: 520, big: true });
    pig.parts && 0; T(pig, { y: -20 + bob(lt, 8, .6), s: 1.2 }); T(plane, { x: Math.sin(lt * .9) * 40, y: -20 + bob(lt, 10, .7), r: -8 + bob(lt, 3, .6), s: 1.15 });
  };
};

// ============================================================== 2.4 iceberg: we only judge the surface
V.iceberg = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 110, size: 50, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 });
  R(g, 0, 380, 1920, 700, 'rgba(20,70,120,.55)'); const wave = P(g, 'M 0 380 Q 120 360 240 380 T 480 380 T 720 380 T 960 380 T 1200 380 T 1440 380 T 1680 380 T 1920 380 L 1920 420 L 0 420 Z', 'rgba(110,200,255,.5)');
  const ice = gnode(g); P(ice, 'M 760 380 L 860 250 L 930 300 L 1010 190 L 1110 330 L 1170 380 Z', '#EAF6FF'); P(ice, 'M 1010 190 L 1110 330 L 1050 330 Z', '#C2E3FA'); P(ice, 'M 740 380 L 700 560 L 780 760 L 940 900 L 1120 860 L 1230 700 L 1200 520 L 1190 380 Z', 'rgba(150,200,240,.55)');
  const car = gnode(g); A.car(car, { color: RED, beam: false }); T(car, { x: 960, y: 245, s: .42 });
  const tipl = pill(g, tx.tip, { size: 44, bg: '#fff', fill: '#10202e' }); T(tipl, { x: 1500, y: 250, o: 0 });
  const icons = [['🏠', 'కలలు'], ['💔', 'కష్టాలు'], ['🎯', 'లక్ష్యాలు']].map(([e, l], i) => { const gr = gnode(g); txt(gr, e, { size: 84, font: 'en', y: 20 }); const p = pill(gr, l, { size: 36, bg: 'rgba(255,255,255,.14)', fill: '#fff' }); T(p, { y: 76 }); T(gr, { x: 900 + (i - 1) * 190 + (i === 1 ? 0 : 0), y: 600 + (i % 2) * 90, o: 0 }); return gr; });
  const deepl = pill(g, tx.deep, { size: 44, bg: GOLD, fill: '#1b1100' }); T(deepl, { x: 1500, y: 700, o: 0 });
  const mg = gnode(g); A.magnifier(mg, { r: 56 }); T(mg, { x: 620, y: 300, o: 0, s: 1.2 });
  c.cue(.1, 'whoosh'); c.cue(dur * .25, 'pop'); icons.forEach((_, i) => c.cue(dur * (.5 + i * .12), 'pop', .6)); c.cue(dur * .8, 'ding');
  return lt => {
    rise(top, lt, .05, { x: 960, y: 110, dy: -20 }); T(wave, { x: Math.sin(lt * 1.2) * 20 }); rise(ice, lt, .1, { dy: 80, d: .7 }); pop(car, lt, dur * .1, { x: 960, y: 245, s: .42, d: .5 });
    pop(mg, lt, dur * .2, { x: 600 + Math.sin(lt * 2) * 60, y: 300 + Math.cos(lt * 2) * 20, s: 1.2, big: true }); rise(tipl, lt, dur * .3, { x: 1500, y: 250, dx: 60, dy: 0 });
    icons.forEach((gr, i) => pop(gr, lt, dur * (.5 + i * .12), { x: 900 + (i - 1) * 190, y: 600 + (i % 2) * 90 + bob(lt, 6, .5, i), big: true })); rise(deepl, lt, dur * .75, { x: 1500, y: 700, dx: 60, dy: 0 });
  };
};

// ============================================================== 2.5 what is in their mind?
V.mindUnknown = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = head(g, { mood: 'think' }); T(me, { x: 420, y: 880, s: 1.9 });
  const cloud = gnode(g); A.thought(cloud, { w: 820, h: 440, fill: 'rgba(255,255,255,.07)' }); cloud.querySelectorAll('ellipse,circle').forEach(n => { n.setAttribute('stroke', 'rgba(255,255,255,.35)'); n.setAttribute('stroke-width', 3); });
  const items = [['🏠', -230, -60], ['💔', 0, -110], ['🎯', 230, -50], ['👨‍👩‍👧', -100, 80], ['🚗', 130, 90]].map(([e, x, y], i) => { const t = gnode(cloud); txt(t, e, { size: 86, font: 'en', y: 28 }); T(t, { x, y, o: 0 }); t.__p = [x, y]; return t; });
  T(cloud, { x: 1250, y: 380, o: 0 });
  const q = gnode(g); txt(q, '?', { size: 340, font: 'en', fill: GOLD, y: 120, weight: 700, stroke: '#000', sw: 16 }); T(q, { x: 1700, y: 640, o: 0, r: 8 });
  const mt = fitRow(g, tx.main, { size: 92, fill: '#fff', stroke: '#000', sw: 12, maxW: 1100 }); T(mt, { x: 1250, y: 770 });
  c.cue(.2, 'pop'); items.forEach((_, i) => c.cue(dur * (.25 + i * .1), 'pop', .5)); c.cue(dur * .75, 'ping');
  return lt => {
    me.idle(lt); pop(cloud, lt, .15, { x: 1250, y: 380 + bob(lt, 6, .5), big: true });
    items.forEach((t, i) => pop(t, lt, dur * (.25 + i * .1), { x: t.__p[0], y: t.__p[1] + bob(lt, 6, .6, i), big: true })); pop(q, lt, dur * .7, { x: 1700, y: 640 + bob(lt, 8, .8), big: true, r: 8 });
    mt.__row.__words.forEach((w, i) => pop(w, lt, dur * .3 + i * .15, { x: w.__x, y: 0, d: .5 }));
  };
};
