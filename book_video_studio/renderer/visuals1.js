'use strict';
// Scene 1 (hook) and scene 2 (the book). Each visual: V.name = ctx => update(localTime)
const V = {};

// shared small helpers -------------------------------------------------------
function topPill(c, text, o = {}) {
  const p = pill(c.g, text, Object.assign({ size: 46, bg: 'rgba(255,255,255,.14)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 }, o));
  T(p, { x: o.x == null ? 960 : o.x, y: o.y == null ? 130 : o.y, o: 0 });
  p.__bx = o.x == null ? 960 : o.x; p.__by = o.y == null ? 130 : o.y;
  return p;
}
function spot(c, x, y, r = 360, fill = 'url(#gGlow)', op = .3) { const n = C(c.g, x, y, r, fill, { opacity: op }); return n; }
function rain(c, n, seed, mk) { // falling items; returns update fn
  const r = rng(seed), items = [];
  for (let i = 0; i < n; i++) { const it = gnode(c.g); mk(it, i); items.push({ it, x: 100 + r() * 1720, t0: r() * .8, sp: 380 + r() * 360, rot: (r() - .5) * 400, s: .5 + r() * .7, ph: r() * 6 }); }
  return lt => items.forEach(o => { const k = lt - o.t0; if (k < 0) { T(o.it, { o: 0 }); return; } T(o.it, { x: o.x + Math.sin(k * 2 + o.ph) * 30, y: -80 + k * o.sp, r: k * o.rot * .3, s: o.s, o: 1 }); });
}
function fitRow(parent, str, o) { // word row scaled to max width, wrapped in outer group
  const outer = gnode(parent), row = wordRow(outer, str, o);
  const k = Math.min(1, (o.maxW || 1500) / row.__w); T(row, { s: k }); outer.__row = row; outer.__k = k; return outer;
}

// ============================================================== 1.1 dad + bank
V.dadBank = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sp = spot(c, 600, 640, 420, 'url(#gGlowGold)', .22);
  const dad = A.person(g, { skin: 'tan', hair: 'grey', glasses: true, mustache: true, shirt: '#7C8DB5', shirt2: '#5E6E96', kurta: true, mood: 'smile' });
  T(dad, { x: 600, y: 840, s: 1.6 });
  const nm = topPill(c, tx.name, { x: 600, y: 215, size: 44, bg: '#FFC857', fill: '#2a1b00', stroke: 'none' });
  const CW = 640, CH = 300, XA = 1370, YA = 290, YB = 640;
  const cardA = gnode(g), cardB = gnode(g);
  A.card(cardA, CW, CH, { fill: 'rgba(61,220,151,.12)', stroke: 'rgba(61,220,151,.65)', shadow: true });
  const bank = gnode(cardA); A.bank(bank, {}); T(bank, { x: -150, y: -34, s: .62 });
  const pig = gnode(cardA); A.piggy(pig, {}); T(pig, { x: 140, y: -14, s: .72 });
  const okp = pill(cardA, tx.ok, { size: 38, bg: '#3DDC97', fill: '#04281b' }); T(okp, { x: -10, y: 106 });
  const ok = A.check(cardA, { r: 38 }); T(ok, { x: CW / 2 - 30, y: -CH / 2 + 30 });
  T(cardA, { x: XA, y: YA, o: 0 });
  A.card(cardB, CW, CH, { fill: 'rgba(255,90,95,.12)', stroke: 'rgba(255,90,95,.65)', shadow: true });
  const ch = gnode(cardB); const chart = A.chart(ch, { color: '#FF5A5F', w: 360, h: 120, pts: [.1, .22, .16, .42, .38, .62, .6, .9] }); T(ch, { x: -10, y: -34 });
  const badp = pill(cardB, tx.bad, { size: 38, bg: '#FF5A5F', fill: '#fff' }); T(badp, { x: -10, y: 106 });
  const xx = A.cross(cardB, { r: 38 }); T(xx, { x: CW / 2 - 30, y: -CH / 2 + 30 });
  T(cardB, { x: XA, y: YB, o: 0 });
  const t1 = Math.min(.45, dur * .12), t2 = dur * .5;
  c.cue(t1 + .05, 'whoosh'); c.cue(t1 + .5, 'ding'); c.cue(t2, 'whoosh'); c.cue(t2 + .9, 'error');
  return lt => {
    dad.idle(lt); rise(nm, lt, .1, { x: 600, y: 215, dy: -30 });
    if (lt > t2) dad.setMood('worry'); else dad.setMood('smile');
    const e = E.out3(seg(lt, .05, .55)); T(dad, { x: lerp(430, 600, e), y: 840, s: 1.6, o: e });
    rise(cardA, lt, t1, { x: XA, y: YA, dx: 200, dy: 0, d: .6 });
    pop(ok, lt, t1 + .5, { x: CW / 2 - 30, y: -CH / 2 + 30, big: true }); fade(okp, lt, t1 + .35); T(okp, { x: -10, y: 106 });
    T(bank, { x: -150, y: -34 + bob(lt, 5, .5), s: .62 }); T(pig, { x: 140, y: -14 + bob(lt, 4, .6, 1), s: .72 });
    rise(cardB, lt, t2, { x: XA, y: YB, dx: 200, dy: 0, d: .6 });
    chart.setProgress(E.inOut(seg(lt, t2 + .2, t2 + 1.4)));
    pop(xx, lt, t2 + .9, { x: CW / 2 - 30, y: -CH / 2 + 30, big: true }); fade(badp, lt, t2 + .4);
  };
};

// ============================================================== 1.2 friend + EMI
V.friendEMI = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 1380, 640, 420, 'url(#gGlowCoral)', .2);
  const fr = A.person(g, { skin: 'brown', hair: 'cap', capColor: '#FF5A5F', capColor2: '#E5384F', shirt: '#2FB8A6', shirt2: '#1E8E7F', hoodie: true, earphones: true, mood: 'grin' });
  T(fr, { x: 1380, y: 840, s: 1.6 });
  const nm = topPill(c, tx.name, { x: 1380, y: 215, size: 44, bg: '#4CC9F0', fill: '#02283a', stroke: 'none' });
  const bags = [['#FF5A5F', '#E5384F', 1150, 690, -10, .82], ['#8B5CF6', '#6C3BE8', 1620, 700, 10, .9], ['#FFC857', '#E9A02A', 1520, 770, -4, .7]].map(([a, b, x, y, r, s]) => { const n = gnode(g); A.bag(n, { color: a, color2: b }); n.__b = { x, y, r, s }; return n; });
  const cals = ['JAN', 'FEB', 'MAR'].map((m, i) => { const n = gnode(g); A.calendar(n, { label: 'EMI', sub: '₹ ' + m, w: 190, h: 210 }); n.__x = 330 + i * 230; return n; });
  const lab = pill(g, tx.chip, { size: 52, bg: '#FFC857', fill: '#2a1b00' }); T(lab, { x: 580, y: 790, o: 0 });
  const stream = rain(c, 7, 11, (it) => A.coin(it, { r: 30 }));
  const t0 = [dur * .38, dur * .55, dur * .72];
  cals.forEach((n, i) => c.cue(t0[i], 'pop')); c.cue(.2, 'whoosh'); c.cue(dur * .8, 'coins');
  return lt => {
    fr.idle(lt, 1); rise(nm, lt, .1, { x: 1380, y: 215, dy: -30 });
    const e = E.out3(seg(lt, .05, .55)); T(fr, { x: lerp(1560, 1380, e), y: 840, s: 1.6, o: e });
    bags.forEach((n, i) => { const p = n.__b; pop(n, lt, .3 + i * .18, { x: p.x, y: p.y + bob(lt, 6, .5, i), r: p.r + bob(lt, 3, .6, i), s: p.s }); });
    cals.forEach((n, i) => { pop(n, lt, t0[i], { x: n.__x, y: 440 + bob(lt, 8, .5, i), big: true, r: (i - 1) * 4 }); });
    fade(lab, lt, dur * .35, .5); T(lab, { x: 580, y: 790 + bob(lt, 5, .6) });
    if (lt > dur * .6) stream(lt - dur * .6); else stream(-1);
  };
};

// ============================================================== 1.3 both look wrong?
V.bothQuestion = c => {
  const { g, S, dur } = c, tx = S.txt;
  const dad = A.person(g, { skin: 'tan', hair: 'grey', glasses: true, mustache: true, shirt: '#7C8DB5', shirt2: '#5E6E96', kurta: true, mood: 'flat' });
  const fr = A.person(g, { skin: 'brown', hair: 'cap', capColor: '#FF5A5F', capColor2: '#E5384F', shirt: '#2FB8A6', shirt2: '#1E8E7F', hoodie: true, earphones: true, mood: 'grin' });
  T(dad, { x: 430, y: 850, s: 1.5 }); T(fr, { x: 1490, y: 850, s: 1.5 });
  const big = fitRow(g, tx.big, { size: 130, fill: '#FFC857', stroke: '#2a1450', sw: 14, maxW: 960 }); T(big, { x: 960, y: 560 });
  const q = [0, 1, 2, 3].map(i => { const n = gnode(g); txt(n, '?', { size: 150, fill: i % 2 ? '#4CC9F0' : '#FFC857', font: 'en', stroke: '#2a1450', sw: 12, y: 50 }); return n; });
  const qp = [[330, 330, -12], [540, 250, 10], [1380, 250, -10], [1590, 330, 12]];
  const wr = pill(g, tx.wrong, { size: 58, bg: '#FF5A5F', fill: '#fff' }); T(wr, { x: 960, y: 760, o: 0 });
  c.cue(.15, 'pop'); c.cue(.45, 'pop'); c.cue(.75, 'pop'); c.cue(dur * .45, 'whoosh'); c.cue(dur * .75, 'error');
  return lt => {
    dad.idle(lt); fr.idle(lt, 1.3);
    const e = E.out3(seg(lt, 0, .5)); T(dad, { x: lerp(300, 430, e), y: 850, s: 1.5, o: e }); T(fr, { x: lerp(1620, 1490, e), y: 850, s: 1.5, o: e });
    q.forEach((n, i) => { pop(n, lt, .15 + i * .3, { x: qp[i][0], y: qp[i][1] + bob(lt, 10, .7, i), r: qp[i][2] + bob(lt, 4, .8, i), big: true }); });
    pop(big, lt, dur * .4, { x: 960 + Math.sin(lt * 40) * (lt > dur * .4 && lt < dur * .4 + .5 ? 6 : 0), y: 560, big: true, d: .6 });
    pop(wr, lt, dur * .72, { x: 960, y: 760, big: true });
  };
};

// ============================================================== 1.4 "one truth..."
V.truth = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 18, fill: 'rgba(255,214,107,.10)' }); T(rays, { x: 960, y: 520 });
  const core = spot(c, 960, 520, 520, 'url(#gGlowGold)', .5);
  const t = fitRow(g, tx.main, { size: 190, fill: '#fff', stroke: '#2a1450', sw: 18, maxW: 1500 }); T(t, { x: 960, y: 560 });
  const dots = [0, 1, 2].map(i => { const n = gnode(g); C(n, 0, 0, 14, '#FFC857'); return n; });
  const sp = [0, 1, 2, 3, 4, 5].map(i => { const n = gnode(g); A.sparkle(n, { r: 26 + (i % 3) * 8, fill: i % 2 ? '#FFE08A' : '#fff' }); n.__a = i / 6 * Math.PI * 2; return n; });
  c.cue(.05, 'riser', .9); c.cue(dur * .55, 'impact'); c.flash(dur * .55, .35, '#fff', .55);
  return lt => {
    T(rays, { x: 960, y: 520, r: lt * 8, o: seg(lt, 0, .5) });
    core.setAttribute('opacity', .25 + .25 * seg(lt, 0, dur * .55));
    const row = t.__row; row.__words.forEach((w, i) => pop(w, lt, .1 + i * .28, { x: w.__x, y: 0, d: .6, big: true }));
    const k = 1 + .06 * seg(lt, 0, dur); T(t, { x: 960, y: 560, s: k });
    dots.forEach((n, i) => pop(n, lt, dur * .5 + i * .12, { x: 880 + i * 80, y: 740, big: true }));
    sp.forEach((n, i) => { const p = seg(lt, dur * .55, dur * .55 + .8); const r = 330 + 160 * E.out3(p); T(n, { x: 960 + Math.cos(n.__a) * r, y: 540 + Math.sin(n.__a) * r * .55, s: Math.sin(p * Math.PI) * 1.2, o: p > 0 && p < 1 ? 1 : 0, r: lt * 90 }); });
  };
};

// ============================================================== 1.5 big title
V.titleReveal = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 24, fill: 'rgba(255,214,107,.13)' }); T(rays, { x: 960, y: 500 });
  spot(c, 960, 500, 640, 'url(#gGlowGold)', .45);
  const coins = rain(c, 16, 5, it => A.coin(it, { r: 34 }));
  const l1 = fitRow(g, tx.l1, { size: 96, fill: '#fff', stroke: '#1d0f4a', sw: 14, maxW: 1400 }); T(l1, { x: 960, y: 270 });
  const l2 = fitRow(g, tx.l2, { size: 150, fill: '#FFD66B', stroke: '#2a1450', sw: 18, maxW: 1560 }); T(l2, { x: 960, y: 500 });
  const l3 = fitRow(g, tx.l3, { size: 230, fill: '#FF5A6E', stroke: '#fff', sw: 20, maxW: 900 }); T(l3, { x: 960, y: 740 });
  c.cue(.0, 'impact'); c.flash(0, .3, '#fff', .6); c.cue(.9, 'sparkle'); c.cue(1.7, 'tada'); c.cue(.4, 'coins');
  return lt => {
    T(rays, { x: 960, y: 500, r: lt * 6 });
    l1.__row.__words.forEach((w, i) => pop(w, lt, .15 + i * .2, { x: w.__x, y: 0, d: .5 }));
    l2.__row.__words.forEach((w, i) => pop(w, lt, .55 + i * .25, { x: w.__x, y: 0, d: .6, big: true }));
    l3.__row.__words.forEach((w, i) => pop(w, lt, 1.35 + i * .25, { x: w.__x, y: 0, d: .7, big: true }));
    const s = 1 + .035 * Math.sin(lt * 3); T(l3, { x: 960, y: 740, s });
    coins(Math.max(0, lt - .3));
  };
};

// ============================================================== 2.1 the book
V.bookIntro = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 20, fill: 'rgba(255,255,255,.08)' }); T(rays, { x: 960, y: 520 });
  spot(c, 960, 500, 560, 'url(#gGlowSky)', .45);
  const bk = gnode(g); const book = gnode(bk); A.book(book, {}); T(book, { s: 1.75 });
  const pl = topPill(c, tx.pill, { y: 120, size: 50, bg: '#FFC857', fill: '#2a1b00', stroke: 'none' });
  const sp = [0, 1, 2, 3, 4].map(i => { const n = gnode(g); A.sparkle(n, { r: 22 }); return n; });
  const sparkPos = [[640, 330], [1290, 360], [700, 760], [1250, 720], [960, 210]];
  const en = txt(g, 'THE PSYCHOLOGY OF MONEY', { size: 40, font: 'en', fill: '#fff', x: 960, y: 880, weight: 600, ls: 6 }); en.setAttribute('opacity', 0);
  c.cue(.05, 'whoosh'); c.cue(.55, 'impact', .7); c.cue(1.0, 'sparkle');
  return lt => {
    T(rays, { x: 960, y: 520, r: -lt * 5 });
    const p = seg(lt, 0, .8), e = E.out3(p);
    T(bk, { x: lerp(1500, 960, e), y: 520 + bob(lt, 12, .45), r: lerp(25, 0, e) + bob(lt, 2.5, .4), sx: Math.max(.02, Math.abs(Math.cos((1 - e) * Math.PI * .5 * 3))) * 1, sy: 1, s: 1, o: Math.min(1, p * 3) });
    rise(pl, lt, .2, { x: 960, y: 120, dy: -30 });
    sp.forEach((n, i) => { const k = (lt * .8 + i * .37) % 1; T(n, { x: sparkPos[i][0], y: sparkPos[i][1] + bob(lt, 10, .5, i), s: Math.sin(k * Math.PI) * 1.2, o: lt > .9 ? 1 : 0, r: lt * 60 }); });
    en.setAttribute('opacity', seg(lt, .9, 1.4) * .85);
  };
};

// ============================================================== 2.2 author
V.authorCard = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 620, 520, 480, 'url(#gGlowGold)', .3);
  const ring = gnode(g); C(ring, 0, 0, 230, 'rgba(255,255,255,.08)', { stroke: '#FFC857', 'stroke-width': 10 });
  const av = gnode(ring); const cp = el('clipPath', { id: 'avclip' + Math.floor(Math.random() * 1e6) }, DEFS); C(cp, 0, 0, 222, '#000');
  const inner = gnode(ring, { 'clip-path': `url(#${cp.id})` });
  R(inner, -230, -230, 460, 460, '#2b3a8c'); C(inner, 0, -40, 78, '#E6E9FF'); P(inner, 'M -170 230 Q -170 60 0 50 Q 170 60 170 230 Z', '#E6E9FF');
  T(ring, { x: 620, y: 500, o: 0 });
  const pen = gnode(g); L(pen, -60, 60, 60, -60, '#FFC857', 26); P(pen, 'M -60 60 L -78 78 L -42 72 Z', '#2a1b00'); T(pen, { x: 820, y: 700, r: 0, o: 0 });
  const lab = pill(g, tx.role, { size: 40, bg: '#FFC857', fill: '#2a1b00' }); T(lab, { x: 1250, y: 330, o: 0 });
  const name = fitRow(g, tx.name, { size: 112, fill: '#fff', stroke: '#1d0f4a', sw: 12, maxW: 880 }); T(name, { x: 1250, y: 500 });
  const en = txt(g, tx.en, { size: 60, font: 'en', fill: '#FFD66B', weight: 600, x: 1250, y: 610 }); en.setAttribute('opacity', 0);
  const ul = R(g, 810, 650, 0, 8, '#FFC857', 4);
  c.cue(.1, 'whoosh'); c.cue(.9, 'pop'); c.cue(1.5, 'ding');
  return lt => {
    pop(ring, lt, .05, { x: 620, y: 500 + bob(lt, 8, .45), d: .7 });
    pop(pen, lt, 1.5, { x: 820, y: 700, r: -20 + bob(lt, 8, 1), d: .5 });
    rise(lab, lt, .6, { x: 1250, y: 330, dy: 30 });
    name.__row.__words.forEach((w, i) => pop(w, lt, .9 + i * .25, { x: w.__x, y: 0, d: .55 }));
    en.setAttribute('opacity', seg(lt, 1.7, 2.2)); ul.setAttribute('width', 880 * E.out3(seg(lt, 1.6, 2.4)));
  };
};

// ============================================================== 2.3 chapter 1
V.chapterCard = c => {
  const { g, S, dur } = c, tx = S.txt;
  const big = txt(g, '01', { size: 620, font: 'en', fill: 'rgba(255,255,255,.06)', x: 1500, y: 760, weight: 700 });
  const card = gnode(g); A.card(card, 1300, 520, { fill: 'rgba(255,255,255,.08)', shadow: true });
  const ch = txt(card, 'CHAPTER 1', { size: 54, font: 'en', fill: '#FFC857', weight: 600, ls: 14, y: -120 });
  const tt = txt(card, '', { size: 120, font: 'en', fill: '#fff', weight: 700, y: 70 });
  const cur = R(card, 0, -30, 8, 120, '#FFC857', 3);
  T(card, { x: 960, y: 500, o: 0 });
  c.cue(.2, 'whoosh');
  const full = tx.chapter, cps = Math.max(8, full.length / Math.max(1, dur * .55));
  for (let i = 0; i < full.length; i++) c.cue(.45 + i / cps, 'key', .5);
  return lt => {
    rise(card, lt, .05, { x: 960, y: 500, dy: 50 });
    const n = typeText(tt, full, lt, .45, cps);
    const w = tw(tt.textContent, 120, 700, 'en'); cur.setAttribute('x', w / 2 + 14); cur.setAttribute('opacity', (Math.floor(lt * 2.2) % 2 === 0 || n < full.length) ? 1 : 0);
    T(big, { x: 0, y: 0 }); big.setAttribute('x', 1500 - lt * 14);
  };
};

// ============================================================== 2.4 translate
V.translateCard = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 520, 560, 'url(#gGlowGold)', .3);
  const card = gnode(g);
  const face1 = gnode(card), face2 = gnode(card);
  A.card(face1, 1200, 360, { fill: 'rgba(255,255,255,.12)', shadow: true }); txt(face1, 'No One’s Crazy', { size: 120, font: 'en', fill: '#fff', y: 40 });
  A.card(face2, 1400, 360, { fill: 'rgba(255,200,87,.18)', stroke: '#FFC857', sw: 6, shadow: true });
  const f2 = fitRow(face2, tx.te, { size: 104, fill: '#FFD66B', stroke: '#2a1450', sw: 12, maxW: 1260 }); T(f2, { y: 36 });
  const ar = gnode(g); A.arrow(ar, { len: 140, color: '#fff' }); T(ar, { x: 960, y: 820, r: 90, o: 0 });
  const tl = pill(g, tx.tag, { size: 44, bg: '#3DDC97', fill: '#04281b' }); T(tl, { x: 960, y: 220, o: 0 });
  const ok = A.check(g, { r: 54 }); T(ok, { x: 1590, y: 360, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .42, 'flip'); c.cue(dur * .42 + .45, 'ding');
  const fl = dur * .42;
  return lt => {
    rise(card, lt, .05, { x: 960, y: 500, dy: 60 });
    const p = seg(lt, fl, fl + .5), sx = Math.abs(Math.cos(p * Math.PI));
    const first = p < .5; face1.setAttribute('display', first ? 'inline' : 'none'); face2.setAttribute('display', first ? 'none' : 'inline');
    T(face1, { sx: sx, sy: 1 }); T(face2, { sx: sx, sy: 1 });
    pop(ar, lt, fl - .3, { x: 960, y: 820 + bob(lt, 6, 1), r: 90, d: .4 });
    rise(tl, lt, fl + .5, { x: 960, y: 220, dy: -20 }); pop(ok, lt, fl + .7, { x: 1590, y: 360, big: true });
  };
};

// ============================================================== 2.5 mindset shift
V.mindsetShift = c => {
  const { g, S, dur } = c, tx = S.txt;
  spot(c, 960, 560, 560, 'url(#gGlowGold)', .22);
  const pl = topPill(c, tx.pill, { y: 120, size: 50, bg: '#FFC857', fill: '#2a1b00', stroke: 'none' });
  const me = A.person(g, { skin: 'tan', hair: 'short', shirt: '#4C6FFF', shirt2: '#3652D6', mood: 'think' }); T(me, { x: 960, y: 830, s: 1.2 });
  const th = gnode(g); A.thought(th, { w: 360, h: 190, fill: '#fff' }); const bulb = gnode(th); const bb = A.bulb(bulb, {}); T(bulb, { x: 0, y: 0, s: .5 }); T(th, { x: 960, y: 330, o: 0 });
  const left = gnode(g); A.card(left, 440, 250, { fill: 'rgba(255,90,95,.12)', stroke: 'rgba(255,90,95,.55)' }); txt(left, tx.before1, { size: 38, fill: '#FFB3B6', y: -50, weight: 600 }); txt(left, tx.before2, { size: 54, fill: '#fff', y: 40 }); T(left, { x: 330, y: 620, o: 0 });
  const right = gnode(g); A.card(right, 440, 250, { fill: 'rgba(61,220,151,.14)', stroke: 'rgba(61,220,151,.7)', shadow: true }); txt(right, tx.after1, { size: 38, fill: '#8CF0C4', y: -50, weight: 600 }); txt(right, tx.after2, { size: 54, fill: '#fff', y: 40 }); T(right, { x: 1590, y: 620, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .5, 'switch'); c.cue(dur * .5 + .1, 'ding', .8);
  return lt => {
    me.idle(lt); rise(pl, lt, .05, { x: 960, y: 120, dy: -30 });
    pop(th, lt, .3, { x: 960, y: 320 + bob(lt, 6, .5), d: .6 });
    pop(left, lt, .4, { x: 330, y: 640, d: .5 }); pop(right, lt, dur * .45, { x: 1590, y: 640, d: .6, big: true });
    bb.setOn(E.out3(seg(lt, dur * .5, dur * .5 + .35))); me.setMood(lt > dur * .5 ? 'grin' : 'think');
  };
};
