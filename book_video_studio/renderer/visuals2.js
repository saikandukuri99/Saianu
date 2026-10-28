'use strict';
// Scenes 3-5: "your world is small", history examples, the other side
const DAD = { skin: 'tan', hair: 'grey', glasses: true, mustache: true, shirt: '#7C8DB5', shirt2: '#5E6E96', kurta: true };
const YOUTH = { skin: 'brown', hair: 'cap', capColor: '#FF5A5F', capColor2: '#E5384F', shirt: '#2FB8A6', shirt2: '#1E8E7F', hoodie: true, earphones: true };

// ============================================================== 3.1 not only maths
V.calcNo = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 620, 520, 460, 'url(#gGlowSky)', .25);
  const top = topPill(c, tx.top, { y: 120, size: 54, bg: '#FFC857', fill: '#2a1b00', stroke: 'none' });
  const calc = gnode(g); A.calculator(calc, { display: '5 × 12' }); T(calc, { x: 620, y: 520, s: 1.9 });
  const x = A.cross(g, { r: 90 }); T(x, { x: 830, y: 330, o: 0 });
  const items = [['heart', tx.p1, 1330, 330], ['polaroid', tx.p2, 1500, 540], ['house', tx.p3, 1260, 720]].map(([k, label, px, py], i) => {
    const n = gnode(g); const ic = gnode(n);
    if (k === 'heart') A.heart(ic, {}); if (k === 'house') A.house(ic, {}); if (k === 'polaroid') A.polaroid(ic, { emoji: '🧒', cap: '' });
    T(ic, { s: k === 'house' ? 1 : 1.1, y: -20 });
    const p = pill(n, label, { size: 42, bg: '#fff', fill: '#1d0f4a' }); T(p, { y: 130 });
    n.__p = [px, py]; return n;
  });
  c.cue(.2, 'whoosh'); c.cue(dur * .3, 'stamp'); c.shake(dur * .3, 8, .3); items.forEach((n, i) => c.cue(dur * (.5 + i * .13), 'pop'));
  return lt => {
    rise(top, lt, .05, { x: 960, y: 120, dy: -30 });
    pop(calc, lt, .15, { x: 620 + bob(lt, 4, .4), y: 520, s: 1.9, d: .5 });
    pop(x, lt, dur * .3, { x: 830, y: 330, big: true, d: .5 });
    items.forEach((n, i) => pop(n, lt, dur * (.5 + i * .13), { x: n.__p[0], y: n.__p[1] + bob(lt, 8, .5, i), big: true }));
  };
};

// ============================================================== 3.2 where / home / what we saw
V.lifeTimeline = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 120, size: 50, bg: 'rgba(255,255,255,.14)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 });
  const xs = [300, 700, 1100], T0 = [.02, .24, .46];
  const nodes = [['pin', tx.n1], ['house', tx.n2], ['eye', tx.n3]].map(([k, label], i) => {
    const n = gnode(g); const disc = C(n, 0, 0, 130, 'rgba(255,255,255,.1)', { stroke: 'rgba(255,255,255,.4)', 'stroke-width': 4 });
    const ic = gnode(n); if (k === 'pin') A.pin(ic, {}); if (k === 'house') A.house(ic, {}); if (k === 'eye') { const e = A.eye(ic, {}); n.__eye = e; }
    T(ic, { s: k === 'pin' ? .95 : .9, y: k === 'pin' ? -10 : 0 });
    const p = pill(n, label, { size: 42, bg: '#fff', fill: '#1d0f4a' }); T(p, { y: 200 });
    return n;
  });
  const arrows = [0, 1].map(i => { const a = gnode(g); A.arrow(a, { len: 150, color: '#FFC857' }); return a; });
  const arrW = gnode(g); A.arrow(arrW, { len: 160, color: '#FFC857' });
  const wal = gnode(g); const wg = gnode(wal); A.wallet(wg, {}); T(wg, { s: 1.2 }); const wp = pill(wal, tx.n4, { size: 44, bg: '#FFC857', fill: '#2a1b00' }); T(wp, { y: 200 });
  const rn = gnode(g); const tg = txt(rn, '', { size: 10 });
  nodes.forEach((n, i) => c.cue(dur * T0[i], 'pop')); c.cue(dur * .72, 'whoosh'); c.cue(dur * .8, 'ding');
  return lt => {
    rise(top, lt, .05, { x: 960, y: 120, dy: -30 });
    nodes.forEach((n, i) => { pop(n, lt, dur * T0[i], { x: xs[i], y: 470 + bob(lt, 6, .5, i), big: true }); if (n.__eye) { const pu = n.__eye.parts.pupil; T(pu, { x: Math.sin(lt * 2) * 30, y: 0 }); } });
    arrows.forEach((a, i) => pop(a, lt, dur * (T0[i + 1] - .08), { x: xs[i] + 200, y: 470, d: .4 }));
    pop(arrW, lt, dur * .68, { x: 1330, y: 470, d: .4 });
    pop(wal, lt, dur * .74, { x: 1620, y: 470 + bob(lt, 6, .5), big: true });
  };
};

// ============================================================== 3.3 the whole world
V.globeAll = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 18, fill: 'rgba(255,255,255,.05)' }); T(rays, { x: 960, y: 480 });
  const gl = gnode(g); const globe = A.globe(gl, { r: 210 }); T(gl, { x: 960, y: 480, o: 0 });
  const tok = ['coin', 'bolt', 'flame', 'tag', 'heart', 'star'].map((k, i) => {
    const n = gnode(g); const ic = gnode(n); const o = {};
    if (k === 'coin') A.coin(ic, { r: 46 }); if (k === 'bolt') A.bolt(ic, {}); if (k === 'flame') A.flame(ic, {}); if (k === 'tag') A.tag(ic, { label: '₹99' }); if (k === 'heart') A.heart(ic, {}); if (k === 'star') A.star(ic, { r: 60 });
    T(ic, { s: k === 'tag' ? .8 : .72 }); n.__a = i / 6 * Math.PI * 2 + .4; return n;
  });
  const top = topPill(c, tx.top, { y: 120, size: 52, bg: '#FFC857', fill: '#2a1b00', stroke: 'none' });
  const eyeN = gnode(g); const ey = A.eye(eyeN, {}); T(eyeN, { x: 1540, y: 760, s: .8, o: 0 });
  const xx = A.cross(g, { r: 44 }); T(xx, { x: 1640, y: 700, o: 0 });
  const bp = pill(g, tx.bottom, { size: 50, bg: '#fff', fill: '#1d0f4a' }); T(bp, { x: 960, y: 810, o: 0 });
  c.cue(.1, 'whoosh'); tok.forEach((n, i) => c.cue(.4 + i * .18, 'pop', .6)); c.cue(dur * .6, 'error');
  return lt => {
    T(rays, { x: 960, y: 480, r: lt * 5 }); rise(top, lt, .05, { x: 960, y: 120, dy: -30 });
    pop(gl, lt, .05, { x: 960, y: 480 + bob(lt, 8, .4), d: .7 }); globe.spin(lt);
    tok.forEach((n, i) => { const p = seg(lt, .4 + i * .18, .9 + i * .18), a = n.__a + lt * .35, rx = 400, ry = 235; pop(n, lt, .4 + i * .18, { x: 960 + Math.cos(a) * rx, y: 480 + Math.sin(a) * ry, big: true, d: .4 }); });
    pop(eyeN, lt, dur * .5, { x: 1540, y: 760, s: .8 }); pop(xx, lt, dur * .6, { x: 1640, y: 700, big: true }); rise(bp, lt, dur * .55, { x: 960, y: 810, dy: 30 });
    T(ey.parts.pupil, { x: Math.sin(lt * 3) * 20, y: 0 });
  };
};

// ============================================================== 3.4 only a small part
V.spotlightWorld = c => {
  const { g, S, dur } = c, tx = S.txt;
  const gl = gnode(g); const globe = A.globe(gl, { r: 230 }); T(gl, { x: 960, y: 470 });
  const dim = C(g, 960, 470, 232, '#05061a', { opacity: 0 });
  const lens = gnode(g); const ringc = C(lens, 0, 0, 140, 'rgba(255,214,107,.18)', { stroke: '#FFD66B', 'stroke-width': 10 });
  const cp = el('clipPath', { id: 'lens' + Math.floor(Math.random() * 1e6) }, DEFS); C(cp, 0, 0, 132, '#000');
  const inner = gnode(lens, { 'clip-path': `url(#${cp.id})` });
  R(inner, -140, -140, 280, 280, '#1b3a7a'); P(inner, 'M -140 60 L 140 60 L 140 140 L -140 140 Z', '#3a8f5c');
  const mh = gnode(inner); A.house(mh, { roof: '#FF5A5F' }); T(mh, { x: -30, y: 10, s: .7 }); const mp = gnode(inner); A.person(mp, { skin: 'tan', hair: 'short', shirt: '#FFC857', shirt2: '#E9A02A' }); T(mp, { x: 60, y: 140, s: .42 });
  const cap = pill(g, tx.small, { size: 46, bg: '#FFC857', fill: '#2a1b00' }); T(cap, { x: 960, y: 800, o: 0 });
  const eq = fitRow(g, tx.eq, { size: 84, fill: '#fff', stroke: '#1d0f4a', sw: 12, maxW: 1500 }); T(eq, { x: 960, y: 140 });
  c.cue(.2, 'whoosh'); c.cue(dur * .38, 'zoom'); c.cue(dur * .6, 'ding');
  return lt => {
    T(gl, { x: 960, y: 470, s: lerp(1, 1.1, seg(lt, 0, dur)) }); globe.spin(lt);
    const p = E.inOut(seg(lt, dur * .35, dur * .75));
    dim.setAttribute('opacity', .62 * p); dim.setAttribute('r', 232 * lerp(1, 1.1, seg(lt, 0, dur)));
    const sx = lerp(1150, 960, p), sy = lerp(380, 470, p), sc = lerp(.34, 1.55, p);
    T(lens, { x: sx, y: sy + bob(lt, 4, .6), s: sc, o: seg(lt, .15, .5) });
    pop(cap, lt, dur * .55, { x: 960, y: 800, d: .5 });
    eq.__row.__words.forEach((w, i) => pop(w, lt, dur * .62 + i * .16, { x: w.__x, y: 0, d: .5 }));
  };
};

// ============================================================== 4.1 inflation
V.inflation = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 700, 560, 520, 'url(#gGlowCoral)', .2);
  const top = fitRow(g, tx.top, { size: 70, fill: '#fff', stroke: '#2a0b16', sw: 12, maxW: 1500 }); T(top, { x: 960, y: 130 });
  const steps = [['₹10', 460, 740, '#4CC9F0'], ['₹50', 700, 620, '#3DDC97'], ['₹200', 940, 480, '#FFC857'], ['₹1000', 1180, 330, '#FF5A5F']].map(([l, x, y, col], i) => { const n = gnode(g); A.tag(n, { label: l, color: col }); n.__p = [x, y]; return n; });
  const fl = gnode(g); A.flame(fl, {}); T(fl, { x: 1300, y: 200, s: 1.2, o: 0 });
  const coin = gnode(g); A.coin(coin, { r: 90 }); T(coin, { x: 1560, y: 600 });
  const dn = gnode(g); A.arrow(dn, { len: 120, color: '#FF5A5F', w: 18 }); T(dn, { x: 1560, y: 770, r: 90, o: 0 });
  const lab = pill(g, tx.coin, { size: 44, bg: '#FF5A5F', fill: '#fff' }); T(lab, { x: 1560, y: 860, o: 0 });
  steps.forEach((n, i) => c.cue(.25 + i * dur * .13, 'pop')); c.cue(dur * .6, 'melt');
  return lt => {
    top.__row.__words.forEach((w, i) => pop(w, lt, .05 + i * .1, { x: w.__x, y: 0, d: .45 }));
    steps.forEach((n, i) => pop(n, lt, .25 + i * dur * .13, { x: n.__p[0], y: n.__p[1] + bob(lt, 6, .6, i), r: -8 + i * 2, big: true }));
    pop(fl, lt, dur * .5, { x: 1300, y: 200 + bob(lt, 6, 1.5), s: 1.2, big: true });
    const k = 1 - .45 * E.inOut(seg(lt, dur * .55, dur * .9));
    pop(coin, lt, .3, { x: 1560, y: 600 + bob(lt, 6, .5), s: k, d: .5 });
    pop(dn, lt, dur * .6, { x: 1560, y: 770, r: 90, d: .4 }); pop(lab, lt, dur * .65, { x: 1560, y: 860, d: .5 });
  };
};

// ============================================================== 4.2 great depression
V.depression = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = fitRow(g, tx.top, { size: 78, fill: '#F3DDB8', stroke: '#150f08', sw: 12, maxW: 1560 }); T(top, { x: 960, y: 130 });
  const yr = txt(g, tx.year, { size: 56, font: 'en', fill: '#E9C58B', weight: 600, ls: 10, x: 960, y: 205 });
  const a = gnode(g); A.card(a, 520, 420, { fill: 'rgba(233,197,139,.08)', stroke: 'rgba(233,197,139,.45)', shadow: true }); T(a, { x: 360, y: 560, o: 0 });
  const cg = gnode(a); const chart = A.chart(cg, { color: '#FF6B6B', w: 380, h: 190, pts: [.1, .16, .08, .3, .5, .46, .8, .95] }); T(cg, { y: -20 });
  const p1 = pill(a, tx.p1, { size: 38, bg: '#E9C58B', fill: '#2a1b00' }); T(p1, { y: 170 });
  const b = gnode(g); A.card(b, 520, 420, { fill: 'rgba(233,197,139,.08)', stroke: 'rgba(233,197,139,.45)', shadow: true }); T(b, { x: 960, y: 560, o: 0 });
  const bk = gnode(b); A.bank(bk, {}); T(bk, { y: -30, s: .95 });
  const cl = gnode(b); const shut = R(cl, -130, -100, 260, 0, '#6B7592', 6, { stroke: '#3F4862', 'stroke-width': 3 });
  const sign = gnode(b); R(sign, -100, -22, 200, 56, '#FF5A5F', 10); txt(sign, 'CLOSED', { size: 38, font: 'en', fill: '#fff', y: 15, ls: 4 }); T(sign, { y: -20, o: 0 });
  const p2 = pill(b, tx.p2, { size: 38, bg: '#E9C58B', fill: '#2a1b00' }); T(p2, { y: 170 });
  const d = gnode(g); A.card(d, 520, 420, { fill: 'rgba(233,197,139,.08)', stroke: 'rgba(233,197,139,.45)', shadow: true }); T(d, { x: 1560, y: 560, o: 0 });
  const pp = gnode(d); A.person(pp, { skin: 'tan', hair: 'short', shirt: '#8D7B5B', shirt2: '#6E5E43', mood: 'worry' }); T(pp, { y: 100, s: .85 });
  const pk = gnode(d); R(pk, -90, -140, 180, 90, '#fff', 8); txt(pk, 'JOB LOSS', { size: 32, font: 'en', fill: '#B3262F', y: -82, ls: 2 }); R(pk, -70, -64, 140, 6, '#ddd', 3); T(pk, { r: -8, o: 0 });
  const p3 = pill(d, tx.p3, { size: 38, bg: '#E9C58B', fill: '#2a1b00' }); T(p3, { y: 170 });
  const t1 = dur * .0, t2 = dur * .3, t3 = dur * .6;
  c.cue(.1, 'whoosh'); c.cue(t1 + .6, 'crash'); c.cue(t2 + .5, 'whoosh'); c.cue(t2 + 1.2, 'thud'); c.shake(t2 + 1.2, 10, .35); c.cue(t3 + .4, 'whoosh'); c.cue(t3 + 1.1, 'stamp');
  return lt => {
    top.__row.__words.forEach((w, i) => pop(w, lt, .05 + i * .12, { x: w.__x, y: 0, d: .45 })); yr.setAttribute('opacity', seg(lt, .4, .8));
    rise(a, lt, .2, { x: 360, y: 560, dy: 60 }); chart.setProgress(E.inOut(seg(lt, .5, 1.6)));
    rise(b, lt, t2, { x: 960, y: 560, dy: 60 }); const s = E.inOut(seg(lt, t2 + .5, t2 + 1.3)); shut.setAttribute('height', 190 * s); T(sign, { o: 0 }); pop(sign, lt, t2 + 1.2, { y: -20, r: -6, big: true, d: .4 });
    rise(d, lt, t3, { x: 1560, y: 560, dy: 60 }); pop(pk, lt, t3 + .5, { y: -90 + bob(lt, 5, .6), r: -8, big: true });
  };
};

// ============================================================== 4.3 market = danger
V.fearMarket = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 520, 560, 'url(#gGlowCoral)', .22);
  const card = gnode(g); const f1 = gnode(card), f2 = gnode(card);
  A.card(f1, 1100, 520, { fill: 'rgba(61,220,151,.12)', stroke: 'rgba(61,220,151,.7)', sw: 5, shadow: true });
  const rk = gnode(f1); A.rocket(rk, {}); T(rk, { x: -330, y: -20, s: 1.4 });
  const cg = gnode(f1); A.chart(cg, { color: '#3DDC97', w: 360, h: 200, pts: [.9, .78, .7, .5, .56, .3, .2, .06] }).setProgress(1); T(cg, { x: 100, y: -40 });
  const l1 = pill(f1, tx.good, { size: 64, bg: '#3DDC97', fill: '#04281b' }); T(l1, { y: 190 });
  A.card(f2, 1100, 520, { fill: 'rgba(255,90,95,.14)', stroke: 'rgba(255,90,95,.8)', sw: 5, shadow: true });
  const wr = gnode(f2); A.warning(wr, {}); T(wr, { x: -300, y: -20, s: 1.7 });
  const cg2 = gnode(f2); A.chart(cg2, { color: '#FF5A5F', w: 360, h: 200, pts: [.1, .2, .16, .4, .36, .62, .7, .94] }).setProgress(1); T(cg2, { x: 100, y: -40 });
  const l2 = pill(f2, tx.bad, { size: 64, bg: '#FF5A5F', fill: '#fff' }); T(l2, { y: 190 });
  const lab = pill(g, tx.label, { size: 46, bg: '#fff', fill: '#1d0f4a' }); T(lab, { x: 960, y: 170, o: 0 });
  const xx = A.cross(g, { r: 70 }); T(xx, { x: 1400, y: 380, o: 0 });
  const fl = dur * .5;
  c.cue(.1, 'whoosh'); c.cue(fl - .2, 'stamp'); c.cue(fl + .2, 'flip'); c.cue(fl + .7, 'alarm'); c.shake(fl + .7, 8, .3);
  return lt => {
    rise(lab, lt, .1, { x: 960, y: 170, dy: -20 });
    rise(card, lt, .05, { x: 960, y: 560, dy: 60 });
    pop(xx, lt, fl - .35, { x: 1400, y: 380, big: true });
    const p = seg(lt, fl, fl + .5), sx = Math.abs(Math.cos(p * Math.PI)); const first = p < .5;
    f1.setAttribute('display', first ? 'inline' : 'none'); f2.setAttribute('display', first ? 'none' : 'inline');
    T(f1, { sx: sx, sy: 1 }); T(f2, { sx: sx, sy: 1 }); if (p >= .5) T(wr, { x: -300 + Math.sin(lt * 30) * 4, y: -20, s: 1.7 });
    if (p >= 1) xx.setAttribute('opacity', 0); if (p > .5) xx.setAttribute('opacity', 0);
  };
};

// ============================================================== 5.1 the other side (coin flip)
V.otherSide = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 20, fill: 'rgba(255,224,138,.12)' }); T(rays, { x: 960, y: 500 });
  const coin = gnode(g); const side1 = gnode(coin), side2 = gnode(coin);
  C(side1, 0, 0, 220, '#4B4F6B', { stroke: '#8A90B5', 'stroke-width': 14 }); C(side1, 0, 0, 180, '#3A3D57'); const cl = gnode(side1); A.cloud(cl, { color: '#8A90B5' }); T(cl, { s: 1.3 });
  C(side2, 0, 0, 220, 'url(#gGold)', { stroke: '#FFF1C9', 'stroke-width': 14 }); C(side2, 0, 0, 180, '#FFD66B'); const sn = gnode(side2); const sunG = A.sun(sn, { r: 68 });
  T(coin, { x: 960, y: 470 });
  const t = fitRow(g, tx.main, { size: 110, fill: '#fff', stroke: '#1b2a6b', sw: 14, maxW: 1500 }); T(t, { x: 960, y: 830 });
  c.cue(.2, 'whoosh'); c.cue(.45, 'coinflip'); c.cue(dur * .55, 'sparkle');
  const flipAt = dur * .3;
  return lt => {
    T(rays, { x: 960, y: 500, r: lt * 8, o: seg(lt, dur * .3, dur * .7) });
    const p = seg(lt, .15, flipAt + .9), ang = p * Math.PI * 5; const sx = Math.cos(ang);
    const showSun = sx < 0 || p >= 1 ? true : false; const face2 = p >= 1 ? true : (Math.cos(ang) < 0);
    side1.setAttribute('display', face2 ? 'none' : 'inline'); side2.setAttribute('display', face2 ? 'inline' : 'none');
    const y = 470 - Math.sin(p * Math.PI) * 120; T(coin, { x: 960, y: y, sx: Math.max(.02, Math.abs(sx)), sy: 1 });
    if (p >= 1) T(coin, { x: 960, y: 470 + bob(lt, 8, .5), sx: 1, sy: 1 });
    t.__row.__words.forEach((w, i) => pop(w, lt, flipAt + .5 + i * .2, { x: w.__x, y: 0, d: .55, big: true }));
    T(sunG.parts.rays, { r: lt * 30 });
  };
};

// ============================================================== 5.2 youth / bull market
V.youthBull = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 520, 640, 420, 'url(#gGlowMint)', .2);
  const me = A.person(g, Object.assign({ headphones: true, mood: 'grin' }, YOUTH, { earphones: false })); T(me, { x: 480, y: 840, s: 1.5 });
  const nm = topPill(c, tx.name, { x: 480, y: 235, size: 42, bg: '#4CC9F0', fill: '#02283a', stroke: 'none' });
  const card = gnode(g); A.card(card, 760, 440, { fill: 'rgba(61,220,151,.1)', stroke: 'rgba(61,220,151,.6)', shadow: true });
  const ch = gnode(card); const chart = A.chart(ch, { color: '#3DDC97', w: 520, h: 220, pts: [.9, .8, .84, .66, .7, .5, .52, .3, .34, .1] }); T(ch, { y: 20 });
  const up = txt(card, '▲ +24%', { size: 54, font: 'en', fill: '#3DDC97', y: -170, weight: 700 });
  T(card, { x: 1400, y: 420, o: 0 });
  const rk = gnode(g); const rkk = A.rocket(rk, {}); T(rk, { x: 1720, y: 700, s: .8, o: 0 });
  const bub = gnode(g); A.thought(bub, { w: 600, h: 200, fill: '#fff' });
  const b1 = txt(bub, tx.b1, { size: 46, fill: '#1d0f4a', y: -10 }); const b2 = txt(bub, tx.b2, { size: 56, fill: '#E5384F', y: 56 });
  T(bub, { x: 1040, y: 740, o: 0, s: .95 });
  c.cue(.15, 'whoosh'); c.cue(.6, 'riser', .6); c.cue(dur * .55, 'pop'); c.cue(dur * .6, 'whoosh');
  return lt => {
    me.idle(lt, .5); rise(nm, lt, .05, { x: 480, y: 235, dy: -30 });
    const e = E.out3(seg(lt, .05, .55)); T(me, { x: lerp(300, 480, e), y: 840, s: 1.5, o: e });
    rise(card, lt, .3, { x: 1400, y: 420, dx: 120, dy: 0 }); chart.setProgress(E.inOut(seg(lt, .6, dur * .7)));
    pop(rk, lt, dur * .4, { x: 1720, y: 700 - 140 * E.in2(seg(lt, dur * .45, dur)), s: .8, big: true }); T(rkk.parts.fire, { sy: 1 + Math.sin(lt * 40) * .15 });
    pop(bub, lt, dur * .55, { x: 1040, y: 740 + bob(lt, 5, .6), s: .95, big: true });
  };
};

// ============================================================== 5.3 two different worlds
V.twoWorlds = c => {
  const { g, S, dur } = c, tx = S.txt;
  const L_ = gnode(g), R_ = gnode(g);
  // left (dark storm)
  const lbg = R(L_, 0, 0, 880, 760, '#1a1230', 40, { opacity: .85 }); T(L_, { x: 100, y: 130, o: 0 });
  const rbg = R(R_, 0, 0, 880, 760, '#2fa4d6', 40, { opacity: .9 }); T(R_, { x: 940, y: 130, o: 0 });
  const cl = gnode(L_); A.cloud(cl, { color: '#59608A' }); T(cl, { x: 640, y: 140, s: 1.3 }); const bolt = gnode(L_); A.bolt(bolt, {}); T(bolt, { x: 630, y: 290, s: .8 });
  const sn = gnode(R_); const sunG = A.sun(sn, { r: 60 }); T(sn, { x: 200, y: 160, s: 1.2 });
  const cl2 = gnode(R_); A.cloud(cl2, { color: '#fff' }); T(cl2, { x: 680, y: 190, s: .8, o: .9 });
  const dad = A.person(L_, Object.assign({ mood: 'worry' }, DAD)); T(dad, { x: 440, y: 740, s: 1.55 });
  const fr = A.person(R_, Object.assign({ mood: 'grin' }, YOUTH)); T(fr, { x: 440, y: 740, s: 1.55 });
  const lp = pill(L_, tx.l, { size: 44, bg: '#E9C58B', fill: '#2a1b00' }); T(lp, { x: 440, y: 66 });
  const rp = pill(R_, tx.r, { size: 44, bg: '#FFE08A', fill: '#2a1b00' }); T(rp, { x: 440, y: 66 });
  const neq = gnode(g); const nb = C(neq, 0, 0, 74, '#FFC857', { stroke: '#fff', 'stroke-width': 8 }); txt(neq, '≠', { size: 110, font: 'en', fill: '#2a1b00', y: 36 }); T(neq, { x: 960, y: 500, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .3, 'whoosh'); c.cue(dur * .6, 'pop'); c.cue(dur * .6 + .05, 'ding', .7);
  return lt => {
    rise(L_, lt, .05, { x: 100, y: 130, dx: -200, dy: 0, d: .6 }); rise(R_, lt, dur * .3, { x: 940, y: 130, dx: 200, dy: 0, d: .6 });
    dad.idle(lt); fr.idle(lt, 1); T(bolt, { x: 630, y: 290, s: .8, o: Math.sin(lt * 9) > .6 ? 1 : .15 });
    T(sunG.parts.rays, { r: lt * 25 });
    pop(neq, lt, dur * .6, { x: 960, y: 500, big: true });
  };
};

// ============================================================== 5.4 both decisions feel right
V.bothRight = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 120, size: 54, bg: '#3DDC97', fill: '#04281b', stroke: 'none' });
  const mk = (x, ab, text, who) => {
    const grp = gnode(g); const th = gnode(grp); A.thought(th, { w: 620, h: 230, fill: '#fff' });
    txt(th, text[0], { size: 46, fill: '#1d0f4a', y: -8 }); txt(th, text[1], { size: 54, fill: '#0E8F5E', y: 56 });
    T(th, { x: 0, y: 0, s: 1 });
    const p = A.person(grp, who); T(p, { x: 0, y: 590, s: 1.05 });
    const ck = A.check(grp, { r: 60 }); T(ck, { x: 260, y: -100, o: 0 });
    T(grp, { x: x, y: 330, o: 0 }); grp.__p = p; grp.__ck = ck; return grp;
  };
  const a = mk(520, 0, tx.a, Object.assign({ mood: 'smile' }, DAD)), b = mk(1400, 1, tx.b, Object.assign({ mood: 'smile' }, YOUTH));
  c.cue(.1, 'pop'); c.cue(.8, 'ding'); c.cue(dur * .5, 'pop'); c.cue(dur * .5 + .7, 'ding');
  return lt => {
    rise(top, lt, .05, { x: 960, y: 120, dy: -30 });
    pop(a, lt, .15, { x: 520, y: 330 + bob(lt, 4, .5), big: true }); pop(a.__ck, lt, .75, { x: 260, y: -100, big: true }); a.__p.idle(lt);
    pop(b, lt, dur * .45, { x: 1400, y: 330 + bob(lt, 4, .5, 1), big: true }); pop(b.__ck, lt, dur * .45 + .6, { x: 260, y: -100, big: true }); b.__p.idle(lt, 1);
  };
};

// ============================================================== 5.5 their logic
V.logicGears = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 460, 560, 'url(#gGlowGold)', .3);
  const gs = [[A.gear, 760, 470, 120, 12, '#8B9BE0', 1], [null, 1010, 380, 90, 10, '#FFC857', -1.33], [null, 1150, 560, 70, 8, '#4CC9F0', 1.7]].map(([_, x, y, r, n, col, sp]) => { const n_ = gnode(g); A.gear(n_, { r, n, color: col }); n_.__p = [x, y, sp]; return n_; });
  const bulb = gnode(g); const bb = A.bulb(bulb, {}); T(bulb, { x: 1480, y: 430, s: 1.1, o: 0 });
  const t = fitRow(g, tx.main, { size: 120, fill: '#FFD66B', stroke: '#2a1450', sw: 16, maxW: 1300 }); T(t, { x: 960, y: 800 });
  c.cue(.1, 'gear', .7); c.cue(dur * .5, 'switch'); c.cue(dur * .5 + .1, 'ding');
  return lt => {
    gs.forEach((n, i) => { pop(n, lt, .1 + i * .2, { x: n.__p[0], y: n.__p[1], r: lt * 40 * n.__p[2], big: true }); });
    pop(bulb, lt, dur * .45, { x: 1480, y: 430 + bob(lt, 6, .5), s: 1.1, d: .5 }); bb.setOn(E.out3(seg(lt, dur * .5, dur * .5 + .4)));
    t.__row.__words.forEach((w, i) => pop(w, lt, dur * .4 + i * .2, { x: w.__x, y: 0, d: .55, big: true }));
  };
};
