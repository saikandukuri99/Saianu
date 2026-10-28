'use strict';
// Scenes 6-9: not about intelligence, applies to you, three actions, outro

// ============================================================== 6.1 "notice"
V.notice = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 16, fill: 'rgba(255,255,255,.07)' }); T(rays, { x: 960, y: 500 });
  spot(c, 960, 500, 480, 'url(#gGlowGold)', .35);
  const mg = gnode(g); A.magnifier(mg, { r: 120 }); T(mg, { x: 780, y: 420, s: 1.6, o: 0 });
  const ex = gnode(g); const sb = gnode(ex); A.star(sb, { r: 150, n: 12, inner: .78, fill: '#FF5A5F' }); txt(ex, '!', { size: 200, font: 'en', fill: '#fff', y: 70 }); T(ex, { x: 1240, y: 360, o: 0 });
  const t = pill(g, tx.main, { size: 90, bg: '#FFC857', fill: '#2a1b00', h: 150, padX: 60 }); T(t, { x: 960, y: 780, o: 0 });
  c.cue(.05, 'whoosh'); c.cue(.25, 'ping'); c.cue(.4, 'pop');
  return lt => {
    T(rays, { x: 960, y: 500, r: lt * 10 });
    pop(mg, lt, .05, { x: 780 + Math.sin(lt * 3) * 90, y: 420 + Math.cos(lt * 3.4) * 50, s: 1.6, big: true });
    pop(ex, lt, .25, { x: 1240, y: 360 + bob(lt, 8, 1.2), r: bob(lt, 6, 1), big: true });
    pop(t, lt, .3, { x: 960, y: 780, big: true });
  };
};

// ============================================================== 6.2 not smart vs. not smart
V.notSmart = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mk = (x, on, label, col) => {
    const n = gnode(g); A.card(n, 640, 520, { fill: on ? 'rgba(255,214,107,.12)' : 'rgba(255,255,255,.07)', stroke: on ? 'rgba(255,214,107,.7)' : 'rgba(255,255,255,.3)', sw: 4, shadow: true });
    const b = gnode(n); const bb = A.bulb(b, {}); T(b, { y: -40, s: 1.1 }); bb.setOn(on ? 1 : 0);
    const p = pill(n, label, { size: 50, bg: col, fill: on ? '#2a1b00' : '#fff' }); T(p, { y: 190 });
    T(n, { x, y: 500, o: 0 }); return n;
  };
  const a = mk(520, true, tx.a, '#FFC857'), b = mk(1400, false, tx.b, '#5B6591');
  const sl = L(g, 160, 250, 1760, 780, '#FF5A5F', 22); sl.setAttribute('opacity', 0);
  const no = A.cross(g, { r: 70 }); T(no, { x: 960, y: 520, o: 0 });
  const nt = pill(g, tx.no, { size: 56, bg: '#FF5A5F', fill: '#fff' }); T(nt, { x: 960, y: 140, o: 0 });
  c.cue(.1, 'pop'); c.cue(dur * .3, 'pop'); c.cue(dur * .6, 'stamp'); c.shake(dur * .6, 8, .3);
  return lt => {
    pop(a, lt, .1, { x: 520, y: 500 + bob(lt, 5, .5), big: true }); pop(b, lt, dur * .3, { x: 1400, y: 500 + bob(lt, 5, .5, 1), big: true });
    const p = E.out3(seg(lt, dur * .6, dur * .6 + .35)); sl.setAttribute('x2', lerp(160, 1760, p)); sl.setAttribute('y2', lerp(250, 780, p)); sl.setAttribute('opacity', p > 0 ? 1 : 0);
    pop(no, lt, dur * .6 + .2, { x: 960, y: 520, big: true }); rise(nt, lt, dur * .55, { x: 960, y: 140, dy: -30 });
  };
};

// ============================================================== 6.3 different info, different experience
V.differentData = c => {
  const { g, S, dur } = c, tx = S.txt;
  const lcol = gnode(g), rcol = gnode(g);
  A.card(lcol, 700, 560, { fill: 'rgba(76,201,240,.1)', stroke: 'rgba(76,201,240,.6)', sw: 4, shadow: true }); T(lcol, { x: 520, y: 500, o: 0 });
  A.card(rcol, 700, 560, { fill: 'rgba(255,138,61,.1)', stroke: 'rgba(255,138,61,.65)', sw: 4, shadow: true }); T(rcol, { x: 1400, y: 500, o: 0 });
  const docs = [0, 1, 2].map(i => { const d = gnode(lcol); R(d, -150, -110, 300, 190, '#fff', 16, { filter: 'url(#fSoft)' }); R(d, -120, -80, 150, 16, '#4CC9F0', 8); [0, 1, 2].forEach(k => R(d, -120, -46 + k * 30, 240 - k * 40, 12, '#C8D0EE', 6)); T(d, { x: -50 + i * 50, y: -40 + i * 18 - 20, r: -6 + i * 6, o: 0 }); return d; });
  const pols = [['🌧️', '#7FA8FF'], ['🏦', '#FFD66B'], ['👨‍👩‍👧', '#FF9AA2']].map(([e, bg], i) => { const d = gnode(rcol); A.polaroid(d, { emoji: e, bg, cap: '' }); T(d, { x: -110 + i * 110, y: -40 + (i % 2) * 30, r: -10 + i * 10, o: 0 }); return d; });
  const lp = pill(lcol, tx.l, { size: 50, bg: '#4CC9F0', fill: '#02283a' }); T(lp, { y: 220 });
  const rp = pill(rcol, tx.r, { size: 50, bg: '#FF8A3D', fill: '#2a1200' }); T(rp, { y: 220 });
  const ne = gnode(g); C(ne, 0, 0, 62, '#FFC857', { stroke: '#fff', 'stroke-width': 7 }); txt(ne, '≠', { size: 96, font: 'en', fill: '#2a1b00', y: 31 }); T(ne, { x: 960, y: 500, o: 0 });
  c.cue(.1, 'whoosh'); docs.forEach((d, i) => c.cue(.3 + i * .15, 'pop', .6)); c.cue(dur * .45, 'whoosh'); pols.forEach((d, i) => c.cue(dur * .5 + i * .15, 'pop', .6)); c.cue(dur * .8, 'ding');
  return lt => {
    rise(lcol, lt, .05, { x: 520, y: 500, dx: -100, dy: 0 }); rise(rcol, lt, dur * .42, { x: 1400, y: 500, dx: 100, dy: 0 });
    docs.forEach((d, i) => pop(d, lt, .3 + i * .15, { x: -50 + i * 50, y: -40 + i * 18 - 20, r: -6 + i * 6, big: true }));
    pols.forEach((d, i) => pop(d, lt, dur * .5 + i * .15, { x: -110 + i * 110, y: -40 + (i % 2) * 30, r: -10 + i * 10, big: true }));
    pop(ne, lt, dur * .78, { x: 960, y: 500, big: true });
  };
};

// ============================================================== 6.4 "that's all."
V.thatsAll = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 520, 520, 'url(#gGlowGold)', .3);
  const t = fitRow(g, tx.main, { size: 300, fill: '#fff', stroke: '#1d0f4a', sw: 22, maxW: 1400 }); T(t, { x: 960, y: 600 });
  const u = R(g, 560, 700, 0, 14, '#FFC857', 7);
  c.cue(.05, 'thud'); c.shake(.05, 10, .3);
  return lt => {
    t.__row.__words.forEach((w, i) => pop(w, lt, .02 + i * .1, { x: w.__x, y: 0, d: .45, big: true }));
    u.setAttribute('width', 800 * E.out3(seg(lt, .3, .8)));
  };
};

// ============================================================== 6.5 puzzle pieces
V.puzzle = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 500, 520, 'url(#gGlowGold)', .22);
  const a = gnode(g), b = gnode(g);
  const pa = gnode(a); A.puzzle(pa, { color: '#FF8A3D', sides: [0, -1, 0, 0] });
  const pb = gnode(b); A.puzzle(pb, { color: '#4C8DFF', sides: [0, 0, 0, 1] });
  const world = gnode(g); const gl = A.globe(world, { r: 80 }); T(world, { x: 960, y: 500, o: 0, s: 1 });
  const la = pill(g, tx.l, { size: 44, bg: '#FF8A3D', fill: '#2a1200' }); T(la, { x: 560, y: 210, o: 0 });
  const lb = pill(g, tx.r, { size: 44, bg: '#4C8DFF', fill: '#fff' }); T(lb, { x: 1360, y: 210, o: 0 });
  const fin = pill(g, tx.fin, { size: 56, bg: '#3DDC97', fill: '#04281b' }); T(fin, { x: 960, y: 800, o: 0 });
  const tA = .05, tB = dur * .38, tS = dur * .7;
  c.cue(tA, 'whoosh'); c.cue(tB, 'whoosh'); c.cue(tS, 'snap'); c.cue(tS + .1, 'ding'); c.cue(tS + .25, 'sparkle', .7); c.flash(tS, .25, '#fff', .35);
  return lt => {
    const sa = E.out3(seg(lt, tA, tA + .7)), sb = E.out3(seg(lt, tB, tB + .7)), sn = E.back(seg(lt, tS - .05, tS + .3));
    const xa = lerp(-300, 560, sa), xb = lerp(2200, 1360, sb);
    const xa2 = lt >= tS ? lerp(560, 816, sn) : xa;
    T(a, { x: lt >= tS ? xa2 : xa, y: 520 + bob(lt, 8, .5), s: 1.6, o: sa, r: lt >= tS ? 0 : -8 * (1 - sa) });
    T(b, { x: lt >= tS ? lerp(1360, 1104, sn) : xb, y: 520 + bob(lt, 8, .5, 1), s: 1.6, o: sb, r: lt >= tS ? 0 : 8 * (1 - sb) });
    fade(la, lt, tA + .3); fade(lb, lt, tB + .3);
    if (lt >= tS) { la.setAttribute('opacity', 1 - seg(lt, tS, tS + .3)); lb.setAttribute('opacity', 1 - seg(lt, tS, tS + .3)); }
    rise(fin, lt, tS + .3, { x: 960, y: 800, dy: 30 });
  };
};

// ============================================================== 7.1 important point
V.important = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 22, fill: 'rgba(255,200,87,.12)' }); T(rays, { x: 960, y: 500 });
  const st = gnode(g); A.star(st, { r: 250, n: 14, inner: .8, fill: 'url(#gGold)' }); T(st, { x: 960, y: 430, o: 0 });
  const ex = txt(g, '!', { size: 300, font: 'en', fill: '#B8730A', x: 960, y: 535 }); ex.setAttribute('opacity', 0);
  const t = pill(g, tx.main, { size: 74, bg: '#fff', fill: '#1d0f4a', h: 130, padX: 54 }); T(t, { x: 960, y: 880, o: 0 });
  c.cue(.05, 'impact', .8); c.cue(.4, 'ping');
  return lt => {
    T(rays, { x: 960, y: 500, r: lt * 12 });
    pop(st, lt, .05, { x: 960, y: 430, r: lt * 14, big: true, d: .6 }); ex.setAttribute('opacity', seg(lt, .25, .45));
    ex.setAttribute('transform', `translate(0 ${bob(lt, 6, 1.2)})`);
    pop(t, lt, .35, { x: 960, y: 790, big: true });
  };
};

// ============================================================== 7.2 applies to you
V.appliesYou = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 560, 460, 'url(#gGlowSky)', .3);
  const rings = [0, 1, 2].map(i => { const r = C(g, 960, 480, 100, 'none', { stroke: '#4CC9F0', 'stroke-width': 6 }); return r; });
  const me = A.person(g, { skin: 'tan', hair: 'short', shirt: '#FFC857', shirt2: '#E9A02A', mood: 'grin' }); T(me, { x: 960, y: 800, s: 1.35 });
  const you = txt(g, tx.you, { size: 200, font: 'en', fill: '#FFC857', stroke: '#2a1450', sw: 20, x: 960, y: 250, weight: 700, ls: 12 }); you.setAttribute('opacity', 0);
  const hand = gnode(g); A.hand(hand, {}); T(hand, { x: 1560, y: 460, r: -90, s: 1.6, o: 0 });
  const pt = pill(g, tx.main, { size: 62, bg: '#4CC9F0', fill: '#02283a' }); T(pt, { x: 960, y: 860, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(.4, 'pop'); c.cue(dur * .45, 'ding');
  return lt => {
    me.idle(lt); const e = E.out3(seg(lt, 0, .5)); T(me, { x: 960, y: lerp(900, 800, e), s: 1.35, o: e });
    rings.forEach((r, i) => { const k = ((lt * .6 + i / 3) % 1); r.setAttribute('r', 160 + k * 420); r.setAttribute('opacity', (1 - k) * .6 * seg(lt, .3, .6)); });
    you.setAttribute('opacity', seg(lt, .3, .5)); you.setAttribute('transform', `translate(0 ${Math.sin(lt * 2) * 6})`);
    pop(hand, lt, .6, { x: 1500 - bob(lt, 20, 1) * 1, y: 480, r: -90, s: 1.6, big: true });
    rise(pt, lt, dur * .35, { x: 960, y: 860, dy: 30 });
  };
};

// ============================================================== 7.3 habits <- memories
V.habitsMemories = c => {
  const { g, S, dur } = c, tx = S.txt;
  const hl = pill(g, tx.hl, { size: 44, bg: '#FFC857', fill: '#2a1b00' }); T(hl, { x: 480, y: 130, o: 0 });
  const hr = pill(g, tx.hr, { size: 44, bg: '#fff', fill: '#1d0f4a' }); T(hr, { x: 1440, y: 130, o: 0 });
  const rowsY = [340, 560, 780];
  const habits = [['piggy', tx.h1], ['bag', tx.h2], ['wallet', tx.h3]].map(([k, l], i) => {
    const n = gnode(g); const card = A.card(n, 560, 190, { fill: 'rgba(255,200,87,.1)', stroke: 'rgba(255,200,87,.6)' });
    const ic = gnode(n); if (k === 'piggy') A.piggy(ic, {}); if (k === 'bag') A.bag(ic, { color: '#FF5A5F', color2: '#E5384F' }); if (k === 'wallet') A.wallet(ic, {}); T(ic, { x: -190, s: .52 });
    txt(n, l, { size: 44, fill: '#fff', x: 40, y: 15, anchor: 'start' }); T(n, { x: 480, y: rowsY[i], o: 0 }); return n;
  });
  const mems = [['🌧️', '#7FA8FF', tx.m1], ['💸', '#FFD66B', tx.m2], ['🏫', '#FF9AA2', tx.m3]].map(([e, bg, cap], i) => {
    const n = gnode(g); const card = A.card(n, 560, 190, { fill: 'rgba(255,255,255,.1)', stroke: 'rgba(255,255,255,.4)' });
    txt(n, e, { size: 90, font: 'en', x: -190, y: 30 }); txt(n, cap, { size: 44, fill: '#fff', x: -110, y: 15, anchor: 'start' }); T(n, { x: 1440, y: rowsY[i], o: 0 }); return n;
  });
  const links = rowsY.map(y => { const p = P(g, `M 770 ${y} L 1150 ${y}`, 'none', { stroke: '#FFC857', 'stroke-width': 6, 'stroke-dasharray': '14 12', 'stroke-linecap': 'round' }); p.setAttribute('opacity', 0); return p; });
  const arrows = rowsY.map(y => { const a = gnode(g); A.arrow(a, { len: 60, color: '#FFC857', w: 10 }); T(a, { x: 960, y, o: 0, r: 180 }); return a; });
  const t0 = [.1, dur * .33, dur * .62];
  habits.forEach((n, i) => { c.cue(t0[i], 'pop'); c.cue(t0[i] + .5, 'tick'); });
  return lt => {
    fade(hl, lt, .05); fade(hr, lt, .3); T(hl, { x: 480, y: 130 }); T(hr, { x: 1440, y: 130 });
    habits.forEach((n, i) => { pop(n, lt, t0[i], { x: 480, y: rowsY[i], d: .45 }); pop(mems[i], lt, t0[i] + .45, { x: 1440, y: rowsY[i], d: .45 });
      const p = seg(lt, t0[i] + .3, t0[i] + .8); links[i].setAttribute('opacity', p); links[i].setAttribute('stroke-dashoffset', -lt * 40);
      pop(arrows[i], lt, t0[i] + .3, { x: 960, y: rowsY[i], r: 180, d: .35 }); });
  };
};

// ============================================================== 7.4 why fear / why spend
V.fearOrSpend = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = A.person(g, { skin: 'brown', hair: 'short', shirt: '#8B5CF6', shirt2: '#6C3BE8', mood: 'think' }); T(me, { x: 960, y: 880, s: 1.2 });
  const q = txt(g, tx.q, { size: 150, fill: '#FFC857', stroke: '#2a1450', sw: 16, x: 960, y: 260 }); q.setAttribute('opacity', 0);
  const mk = (x, col, ic, label, shake) => {
    const n = gnode(g); const th = gnode(n); A.thought(th, { w: 560, h: 330, fill: '#fff' });
    const i = gnode(th); if (ic === 'lock') { A.wallet(i, {}); const lk = gnode(i); R(lk, -30, -10, 60, 52, '#FFC857', 8); P(lk, 'M -18 -10 Q -18 -46 0 -46 Q 18 -46 18 -10', 'none', { stroke: '#E9A02A', 'stroke-width': 9 }); T(lk, { x: 60, y: 10 }); } else A.bag(i, { color: '#FF5A5F', color2: '#E5384F' });
    T(i, { x: 0, y: -30, s: .82 });
    const p = pill(th, label, { size: 50, bg: col, fill: '#fff' }); T(p, { y: 115 });
    T(n, { x: x, y: 520, o: 0 }); n.__i = i; return n;
  };
  const a = mk(500, '#4C6FFF', 'lock', tx.a), b = mk(1420, '#FF5A5F', 'bag', tx.b);
  c.cue(.1, 'pop'); c.cue(dur * .2, 'pop'); c.cue(dur * .55, 'pop'); c.cue(dur * .55 + .05, 'ping');
  return lt => {
    me.idle(lt); const e = E.out3(seg(lt, 0, .5)); T(me, { x: 960, y: lerp(960, 880, e), s: 1.2, o: e });
    pop(q, lt, .15, { x: 960, y: 250, big: true }); q.setAttribute('opacity', seg(lt, .15, .3)); q.setAttribute('transform', `translate(0 ${bob(lt, 8, .8)})`);
    pop(a, lt, dur * .15, { x: 500, y: 520 + bob(lt, 6, .6), big: true }); pop(b, lt, dur * .5, { x: 1420, y: 520 + bob(lt, 6, .6, 1), big: true });
    T(a.__i, { x: Math.sin(lt * 25) * 3 * (lt > dur * .15 && lt < dur * .15 + .6 ? 1 : 0), y: -30, s: .82 });
  };
};

// ============================================================== 8.x numbered steps
function badge(c, n, x, y, col = '#FFC857') { const b = gnode(c.g); C(b, 0, 0, 62, col, { stroke: '#fff', 'stroke-width': 7 }); txt(b, String(n), { size: 84, font: 'en', fill: '#2a1b00', y: 29 }); T(b, { x, y, o: 0 }); return b; }

V.threeSteps = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = fitRow(g, tx.top, { size: 100, fill: '#fff', stroke: '#1d0f4a', sw: 14, maxW: 1400 }); T(top, { x: 960, y: 240 });
  const items = [tx.s1, tx.s2, tx.s3].map((l, i) => {
    const n = gnode(g); const card = A.card(n, 460, 330, { fill: 'rgba(255,255,255,.1)', stroke: 'rgba(255,200,87,.6)', sw: 4, shadow: true });
    const b = gnode(n); C(b, 0, -70, 70, '#FFC857', { stroke: '#fff', 'stroke-width': 8 }); txt(b, String(i + 1), { size: 96, font: 'en', fill: '#2a1b00', y: -37 });
    txt(n, l, { size: 52, fill: '#fff', y: 80 }); T(n, { x: 400 + i * 560 + (i === 0 ? 0 : 0), y: 640, o: 0 }); return n;
  });
  const t0 = [dur * .3, dur * .5, dur * .72];
  c.cue(.1, 'whoosh'); t0.forEach(t => c.cue(t, 'pop'));
  return lt => {
    top.__row.__words.forEach((w, i) => pop(w, lt, .05 + i * .12, { x: w.__x, y: 0, d: .45 }));
    items.forEach((n, i) => pop(n, lt, t0[i], { x: 400 + i * 560, y: 640 + bob(lt, 6, .5, i), big: true }));
  };
};

V.stepLook = c => { // 8.2: think about their situation
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 120, size: 52, bg: 'rgba(255,255,255,.14)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 });
  const bd = badge(c, 1, 160, 130);
  const me = A.person(g, Object.assign({ mood: 'think' }, YOUTH)); T(me, { x: 380, y: 860, s: 1.3 });
  const dad = A.person(g, Object.assign({ mood: 'flat' }, DAD)); T(dad, { x: 1500, y: 860, s: 1.3 });
  const mg = gnode(g); A.magnifier(mg, { r: 110 }); T(mg, { x: 760, y: 520, s: 1.3, o: 0 });
  const th = gnode(g); A.thought(th, { w: 560, h: 260, fill: '#fff' }); const cl = gnode(th); A.cloud(cl, { color: '#9AA6D6' }); T(cl, { x: -130, y: -10, s: .8 }); const bk = gnode(th); A.bank(bk, {}); T(bk, { x: 120, y: -10, s: .52 }); T(th, { x: 1250, y: 330, o: 0 });
  const lab = pill(g, tx.lab, { size: 48, bg: '#FFC857', fill: '#2a1b00' }); T(lab, { x: 960, y: 560, o: 0 });
  c.cue(.1, 'pop'); c.cue(dur * .3, 'whoosh'); c.cue(dur * .55, 'pop'); c.cue(dur * .7, 'ding');
  return lt => {
    rise(top, lt, .05, { x: 960, y: 120, dy: -30 }); pop(bd, lt, .1, { x: 160, y: 130, big: true });
    me.idle(lt); dad.idle(lt, 1);
    pop(mg, lt, dur * .25, { x: 780 + Math.sin(lt * 1.6) * 120, y: 540 + Math.cos(lt * 2.1) * 20, s: 1.3, big: true });
    pop(th, lt, dur * .5, { x: 1250, y: 330 + bob(lt, 6, .6), big: true });
    rise(lab, lt, dur * .65, { x: 960, y: 570, dy: 30 });
  };
};

V.stepMirror = c => { // 8.3: question own beliefs
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 120, size: 52, bg: 'rgba(255,255,255,.14)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 });
  const bd = badge(c, 2, 160, 130);
  const me = A.person(g, { skin: 'tan', hair: 'short', shirt: '#4C6FFF', shirt2: '#3652D6', mood: 'think' }); T(me, { x: 500, y: 860, s: 1.45 });
  const mir = gnode(g); const frame = el('ellipse', { cx: 0, cy: 0, rx: 230, ry: 310, fill: 'url(#gSky)', stroke: '#FFE08A', 'stroke-width': 18 }, mir); el('ellipse', { cx: 0, cy: 0, rx: 205, ry: 285, fill: '#BFE3FF' }, mir);
  const rf = gnode(mir); const rp = A.person(rf, { skin: 'tan', hair: 'short', shirt: '#4C6FFF', shirt2: '#3652D6', mood: 'think' }); T(rf, { x: 0, y: 250, s: 1.05 });
  P(mir, 'M -150 -180 L -60 -250 L -20 -240 L -120 -150 Z', 'rgba(255,255,255,.55)'); T(mir, { x: 1300, y: 500, o: 0 });
  const qs = [0, 1, 2].map(i => { const q = txt(g, '?', { size: 120, font: 'en', fill: i % 2 ? '#4CC9F0' : '#FFC857', stroke: '#2a1450', sw: 12, y: 40 }); const w = gnode(g); w.appendChild(q); T(w, { o: 0 }); return w; });
  const qp = [[1000, 250], [1620, 260], [1650, 620]];
  const lab = pill(g, tx.lab, { size: 48, bg: '#FFC857', fill: '#2a1b00' }); T(lab, { x: 1300, y: 880, o: 0 });
  c.cue(.1, 'pop'); c.cue(dur * .3, 'whoosh'); qs.forEach((q, i) => c.cue(dur * (.5 + i * .1), 'pop', .6));
  return lt => {
    rise(top, lt, .05, { x: 960, y: 120, dy: -30 }); pop(bd, lt, .1, { x: 160, y: 130, big: true });
    me.idle(lt); rp.idle(lt, .2);
    pop(mir, lt, dur * .25, { x: 1300, y: 500 + bob(lt, 6, .4), big: true });
    qs.forEach((q, i) => pop(q, lt, dur * (.5 + i * .1), { x: qp[i][0], y: qp[i][1] + bob(lt, 8, .8, i), r: (i - 1) * 12, big: true }));
    rise(lab, lt, dur * .7, { x: 1300, y: 880, dy: 30 });
  };
};

V.stepLearn = c => { // 8.4: learn from others
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 120, size: 52, bg: 'rgba(255,255,255,.14)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 });
  const bd = badge(c, 3, 160, 130);
  spot(c, 960, 560, 420, 'url(#gGlowGold)', .25);
  const me = A.person(g, { skin: 'tan', hair: 'short', shirt: '#FFC857', shirt2: '#E9A02A', mood: 'grin' }); T(me, { x: 960, y: 860, s: 1.25 });
  const others = [
    [{ skin: 'light', hair: 'bun', hairColor: '#5b3a29', shirt: '#FF8A8A', shirt2: '#E5384F', bindi: true }, 360, 400],
    [{ skin: 'dark', hair: 'curly', shirt: '#4CC9F0', shirt2: '#2F7BFF' }, 1560, 400],
    [DAD, 330, 760], [YOUTH, 1590, 760],
  ].map(([o, x, y]) => { const p = A.person(g, Object.assign({ mood: 'smile' }, o)); T(p, { x, y: y + 130, s: .6, o: 0 }); p.__p = [x, y + 130]; return p; });
  const items = others.map((p, i) => { const n = gnode(g); const ic = gnode(n); if (i % 2) A.bulb(ic, {}).setOn(1); else A.book(ic, { title: false }); T(ic, { s: .22 }); T(n, { o: 0 }); n.__from = [p.__p[0], p.__p[1] - 100]; return n; });
  const lab = pill(g, tx.lab, { size: 50, bg: '#3DDC97', fill: '#04281b' }); T(lab, { x: 960, y: 180, o: 0 });
  const t0 = [dur * .12, dur * .3, dur * .48, dur * .64];
  t0.forEach(t => { c.cue(t, 'pop'); c.cue(t + .5, 'whoosh', .5); }); c.cue(dur * .85, 'ding');
  return lt => {
    rise(top, lt, .05, { x: 960, y: 120, dy: -30 }); pop(bd, lt, .1, { x: 160, y: 130, big: true });
    me.idle(lt);
    others.forEach((p, i) => { pop(p, lt, t0[i], { x: p.__p[0], y: p.__p[1], s: .6, d: .45 }); p.idle(lt, i);
      const k = E.inOut(seg(lt, t0[i] + .4, t0[i] + 1.3)), n = items[i];
      T(n, { x: lerp(n.__from[0], 960, k), y: lerp(n.__from[1], 640, k) - Math.sin(k * Math.PI) * 60, s: 1 + .2 * Math.sin(k * Math.PI), o: (lt > t0[i] + .4 && k < 1) ? 1 : 0 }); });
    rise(lab, lt, dur * .75, { x: 960, y: 190, dy: -20 });
  };
};

// ============================================================== 9.x outro
V.notMath = c => {
  const { g, S, dur } = c, tx = S.txt;
  const board = gnode(g); A.card(board, 1100, 400, { fill: 'rgba(255,255,255,.08)', shadow: true }); T(board, { x: 960, y: 440, o: 0 });
  const eq = ['2', '+', '2', '=', '4'].map((ch, i) => { const n = gnode(board); txt(n, ch, { size: 190, font: 'en', fill: '#fff', y: 66 }); T(n, { x: -400 + i * 200, y: 0 }); n.__a = (i - 2) * 0.35; return n; });
  const sl = L(g, 460, 600, 1460, 280, '#FF5A5F', 22); sl.setAttribute('opacity', 0);
  const pl = pill(g, tx.main, { size: 62, bg: '#FFC857', fill: '#2a1b00' }); T(pl, { x: 960, y: 800, o: 0 });
  const hr = gnode(g); A.heart(hr, {}); T(hr, { x: 700, y: 440, s: .9, o: 0 });
  const gr = gnode(g); A.gear(gr, { r: 60, n: 9, color: '#9AA6D6', hole: '#2a1c70' }); T(gr, { x: 1220, y: 440, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .4, 'scratch'); c.cue(dur * .65, 'pop'); c.cue(dur * .65 + .1, 'ding');
  return lt => {
    rise(board, lt, .05, { x: 960, y: 440, dy: 60 });
    const p = seg(lt, dur * .4, dur * .4 + .4); sl.setAttribute('x2', lerp(460, 1460, p)); sl.setAttribute('y2', lerp(600, 280, p)); sl.setAttribute('opacity', p > 0 ? 1 : 0);
    const f = E.in2(seg(lt, dur * .55, dur * .55 + .6));
    eq.forEach((n, i) => T(n, { x: -400 + i * 200 + f * (i - 2) * 80, y: f * (i % 2 ? -80 : 80), r: f * n.__a * 40, o: 1 - f }));
    pop(hr, lt, dur * .6, { x: 700, y: 440 + bob(lt, 6, 1), s: .9 + .08 * Math.sin(lt * 6), big: true }); pop(gr, lt, dur * .66, { x: 1220, y: 440, r: lt * 50, big: true });
    rise(pl, lt, dur * .3, { x: 960, y: 800, dy: 30 });
  };
};

V.mindExperience = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 520, 520, 'url(#gGlowGold)', .28);
  const wal = gnode(g); A.wallet(wal, {}); T(wal, { x: 960, y: 520, s: 1.5, o: 0 });
  const hr = gnode(g); const hh = gnode(hr); A.heart(hh, {}); T(hh, { s: 1.25 }); const hp = pill(hr, tx.l, { size: 46, bg: '#FF4D6D', fill: '#fff' }); T(hp, { y: 150 }); T(hr, { x: 360, y: 420, o: 0 });
  const ex = gnode(g); const pol = gnode(ex); A.polaroid(pol, { emoji: '🌍', bg: '#7FA8FF' }); T(pol, { s: 1.15, r: -6 }); const ep = pill(ex, tx.r, { size: 46, bg: '#4CC9F0', fill: '#02283a' }); T(ep, { y: 170 }); T(ex, { x: 1560, y: 420, o: 0 });
  const a1 = gnode(g); A.arrow(a1, { len: 150, color: '#FFC857' }); T(a1, { x: 660, y: 470, o: 0 }); const a2 = gnode(g); A.arrow(a2, { len: 150, color: '#FFC857' }); T(a2, { x: 1260, y: 470, r: 180, o: 0 });
  const t = pill(g, tx.main, { size: 56, bg: '#fff', fill: '#1d0f4a', h: 110 }); T(t, { x: 960, y: 800, o: 0 });
  c.cue(.1, 'pop'); c.cue(dur * .25, 'pop'); c.cue(dur * .5, 'pop'); c.cue(dur * .55, 'whoosh'); c.cue(dur * .75, 'ding');
  return lt => {
    pop(hr, lt, .15, { x: 360, y: 420 + bob(lt, 6, .5), big: true }); pop(ex, lt, dur * .25, { x: 1560, y: 420 + bob(lt, 6, .5, 1), big: true });
    pop(wal, lt, dur * .45, { x: 960, y: 520 + bob(lt, 6, .6), s: 1.5, big: true });
    pop(a1, lt, dur * .5, { x: 660, y: 470, d: .35 }); pop(a2, lt, dur * .5, { x: 1260, y: 470, r: 180, d: .35 });
    rise(t, lt, dur * .65, { x: 960, y: 800, dy: 30 });
  };
};

V.likeBtn = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 480, 480, 'url(#gGlowGold)', .3);
  const th = gnode(g); const ic = gnode(th); A.thumb(ic, {}); T(ic, { s: 2 }); T(th, { x: 960, y: 480, o: 0 });
  const cnt = pill(g, tx.cnt, { size: 56, bg: '#fff', fill: '#1d0f4a', font: 'en' }); T(cnt, { x: 1300, y: 330, o: 0 });
  const pl = pill(g, tx.main, { size: 62, bg: '#4C6FFF', fill: '#fff' }); T(pl, { x: 960, y: 820, o: 0 });
  const hearts = Array.from({ length: 8 }, (_, i) => { const n = gnode(g); A.heart(n, { color: i % 2 ? '#FF4D6D' : '#FFC857' }); n.__a = i / 8 * Math.PI * 2; return n; });
  const tk = dur * .45;
  c.cue(.1, 'pop'); c.cue(tk, 'click'); c.cue(tk + .1, 'pop'); c.cue(tk + .2, 'sparkle');
  return lt => {
    const press = seg(lt, tk, tk + .12), rel = seg(lt, tk + .12, tk + .5);
    const s = 1 - .15 * press * (1 - rel) + .1 * E.elastic(rel) * (rel > 0 ? 1 : 0);
    pop(th, lt, .05, { x: 960, y: 480 + bob(lt, 6, .5) * (lt < tk ? 1 : 0), big: true }); if (lt >= .6) T(th, { s: s, x: 960, y: 480, r: -8 * (1 - E.out3(rel)) * (lt >= tk ? 1 : 0) });
    pop(cnt, lt, tk + .1, { x: 1300, y: 330, big: true });
    hearts.forEach((n, i) => { const p = seg(lt, tk + .1, tk + 1); const r = 120 + 360 * E.out3(p); T(n, { x: 960 + Math.cos(n.__a) * r, y: 480 + Math.sin(n.__a) * r * .8, s: (1 - p) * .55 * (p > 0 ? 1 : 0), o: p > 0 && p < 1 ? 1 : 0 }); });
    rise(pl, lt, .3, { x: 960, y: 820, dy: 30 });
  };
};

V.commentBtn = c => {
  const { g, S, dur } = c, tx = S.txt;
  const items = [[tx.c1, 420, 330, 'left', '#6C3BE8'], [tx.c2, 1420, 470, 'right', '#E5384F'], [tx.c3, 560, 640, 'left', '#2FB8A6']].map(([text, x, y, side, col], i) => {
    const n = gnode(g); const w = tw(text, 44, 600) + 80; const b = gnode(n); A.bubble(b, { w, h: 120, fill: '#fff', tail: side === 'left' ? 'bl' : 'br' });
    txt(b, text, { size: 44, fill: '#1d0f4a', y: 15, weight: 600 }); const av = gnode(n); A.avatar(av, { r: 44, bg: col }); T(av, { x: side === 'left' ? -w / 2 - 30 : w / 2 + 30, y: 10 });
    T(n, { x, y, o: 0 }); n.__p = [x, y]; return n;
  });
  const typing = gnode(g); A.bubble(typing, { w: 190, h: 100, fill: '#fff', tail: 'bl' }); [-44, 0, 44].forEach(x => { const d = C(typing, x, 0, 12, '#9AA3C7'); d.__x = x; typing.appendChild(d); }); T(typing, { x: 1400, y: 720, o: 0 });
  const pl = pill(g, tx.main, { size: 62, bg: '#FFC857', fill: '#2a1b00' }); T(pl, { x: 960, y: 880, o: 0 });
  const t0 = [.1, dur * .3, dur * .55];
  t0.forEach(t => c.cue(t, 'pop')); c.cue(dur * .75, 'tick');
  return lt => {
    items.forEach((n, i) => pop(n, lt, t0[i], { x: n.__p[0], y: n.__p[1] + bob(lt, 5, .5, i), big: true }));
    pop(typing, lt, dur * .72, { x: 1400, y: 720, big: true }); const ds = typing.querySelectorAll('circle'); ds.forEach((d, i) => d.setAttribute('cy', Math.sin(lt * 8 - i) * 8));
    rise(pl, lt, .2, { x: 960, y: 880, dy: 30 });
  };
};

V.subscribeBtn = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 480, 520, 'url(#gGlowCoral)', .3);
  const btn = gnode(g); const bg = R(btn, -330, -90, 660, 180, '#E5232B', 90, { filter: 'url(#fShadow)' }); const lab = txt(btn, 'SUBSCRIBE', { size: 84, font: 'en', fill: '#fff', y: 30, ls: 3 }); T(btn, { x: 880, y: 480, o: 0 });
  const bell = gnode(g); const bl = A.bell(bell, {}); T(bell, { x: 1380, y: 470, s: 1.2, o: 0 });
  const ring = gnode(g); [0, 1].forEach(i => { C(ring, 0, 0, 80 + i * 30, 'none', { stroke: '#FFC857', 'stroke-width': 6, opacity: .0 }); }); T(ring, { x: 1380, y: 470 });
  const cur = gnode(g); A.hand(cur, {}); T(cur, { x: 1500, y: 800, s: 1.1, o: 0 });
  const pl = pill(g, tx.main, { size: 62, bg: '#fff', fill: '#1d0f4a' }); T(pl, { x: 960, y: 800, o: 0 });
  const tk = dur * .5;
  c.cue(.1, 'pop'); c.cue(.4, 'pop'); c.cue(tk, 'click'); c.cue(tk + .15, 'ding'); c.cue(tk + .3, 'bell'); c.cue(tk + .8, 'bell', .7);
  return lt => {
    pop(btn, lt, .1, { x: 880, y: 480, big: true });
    pop(bell, lt, .4, { x: 1380, y: 470, s: 1.2, big: true });
    const mv = E.inOut(seg(lt, dur * .2, tk)); const px = lerp(1500, 920, mv), py = lerp(840, 540, mv); const press = seg(lt, tk, tk + .1) * (1 - seg(lt, tk + .1, tk + .3));
    pop(cur, lt, dur * .2, { x: px, y: py, s: 1.1 - .12 * press, d: .3 }); if (lt > dur * .2 + .3) T(cur, { x: px, y: py, s: 1.1 - .12 * press });
    const done = lt >= tk + .05;
    bg.setAttribute('fill', done ? '#5B6591' : '#E5232B'); lab.textContent = done ? 'SUBSCRIBED ✓' : 'SUBSCRIBE'; lab.setAttribute('font-size', done ? 70 : 84);
    const rg = seg(lt, tk + .25, tk + 1.6); T(bl.parts.b, { r: rg > 0 && rg < 1 ? Math.sin(rg * 24) * 22 * (1 - rg) : 0, x: 0, y: 0 });
    rise(pl, lt, .2, { x: 960, y: 800, dy: 30 });
  };
};

V.endCard = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 24, fill: 'rgba(255,214,107,.1)' }); T(rays, { x: 960, y: 460 });
  spot(c, 960, 460, 620, 'url(#gGlowGold)', .4);
  const nm = txt(g, '🙏', { size: 250, font: 'en', x: 960, y: 330 }); nm.setAttribute('opacity', 0);
  const t = fitRow(g, tx.main, { size: 150, fill: '#FFD66B', stroke: '#2a1450', sw: 18, maxW: 1400 }); T(t, { x: 960, y: 560 });
  const bt = gnode(g); A.card(bt, 1240, 190, { fill: 'rgba(255,255,255,.1)', shadow: true });
  const bk = gnode(bt); A.book(bk, { title: false }); T(bk, { x: -520, y: 0, s: .44 });
  txt(bt, tx.src1, { size: 38, fill: '#FFD66B', font: 'en', y: -22, x: -440, anchor: 'start', weight: 600 });
  txt(bt, tx.src2, { size: 46, fill: '#fff', font: 'en', y: 32, x: -440, anchor: 'start', weight: 700 });
  txt(bt, tx.src3, { size: 34, fill: '#C9CFE8', font: 'en', y: 76, x: -440, anchor: 'start', weight: 400 });
  T(bt, { x: 960, y: 800, o: 0 });
  c.cue(.05, 'tada'); c.cue(.2, 'sparkle'); c.flash(.02, .3, '#fff', .4);
  return lt => {
    T(rays, { x: 960, y: 460, r: lt * 6 });
    pop(nm, lt, .05, { x: 0, y: 0, big: true }); nm.setAttribute('opacity', seg(lt, .05, .2)); nm.setAttribute('transform', `translate(0 ${bob(lt, 8, .6)})`);
    t.__row.__words.forEach((w, i) => pop(w, lt, .3 + i * .22, { x: w.__x, y: 0, d: .55, big: true }));
    rise(bt, lt, 1.0, { x: 960, y: 800, dy: 40 });
  };
};
