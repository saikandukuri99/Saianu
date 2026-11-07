'use strict';
// Episode 3, "maths vs mindset". Black theme flat 2D. Uses helpers from ep2 (head, bill, mini, scale, GOLD...).
const W5 = 'rgba(255,255,255,.12)';
const bigLine = (c, s, y, o = {}) => { const r = fitRow(c.g, s, Object.assign({ size: 110, fill: '#fff', stroke: '#000', sw: 14, maxW: 1500 }, o)); T(r, { x: 960, y }); return r; };
const wp = (r, lt, t0, step = .16, big = false) => r.__row.__words.forEach((w, i) => pop(w, lt, t0 + i * step, { x: w.__x, y: 0, d: .5, big }));
const tagp = (c, s, y, o = {}) => { const p = pill(c.g, s, Object.assign({ size: 48, bg: W5, fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }, o)); T(p, { x: o.x == null ? 960 : o.x, y, o: 0 }); p.__y = y; p.__x = o.x == null ? 960 : o.x; return p; };
const tagIn = (p, lt, t0 = .1) => rise(p, lt, t0, { x: p.__x, y: p.__y, dy: -24 });
function sheet(parent, w = 420, h = 540) { const g = gnode(parent); R(g, -w / 2, -h / 2, w, h, '#F3F1EA', 14, { filter: 'url(#fShadow)' }); for (let i = 0; i < 6; i++) R(g, -w / 2 + 34, -h / 2 + 150 + i * 48, w - 68, 8, 'rgba(0,0,0,.12)', 4); return g; }
function brain(parent, col = '#FF8AD0') { const g = gnode(parent); [[-34, -20, 48], [34, -20, 48], [-48, 24, 40], [48, 24, 40], [0, 34, 44], [0, -34, 44]].forEach(([x, y, r]) => C(g, x, y, r, col)); P(g, 'M 0 -70 Q -12 -20 0 20 Q 12 60 0 78', 'none', { stroke: 'rgba(0,0,0,.28)', 'stroke-width': 6, 'stroke-linecap': 'round' }); P(g, 'M -60 -20 Q -30 -10 -10 -30 M 60 -20 Q 30 -10 10 -30 M -50 28 Q -26 20 -8 32 M 50 28 Q 26 20 8 32', 'none', { stroke: 'rgba(0,0,0,.22)', 'stroke-width': 5, 'stroke-linecap': 'round' }); return g; }

// 1.1
V.calcLogic = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tag = tagp(c, tx.tag, 130, { size: 52 });
  const calc = gnode(g); A.calculator(calc, { display: '12,50,000' }); T(calc, { x: 560, y: 560, s: 2.3, o: 0 });
  const ch = gnode(g); const chart = A.chart(ch, { color: GREEN, w: 520, h: 260, pts: [.9, .78, .7, .52, .5, .3, .2, .06] }); T(ch, { x: 1400, y: 440, o: 0 });
  const ok = A.check(g, { r: 60 }); T(ok, { x: 1700, y: 270, o: 0 });
  const p = pill(g, tx.ok, { size: 56, bg: GREEN, fill: '#04281b' }); T(p, { x: 1400, y: 780, o: 0 });
  const nums = ['+8%', '₹ 5L', '÷ 12', '= ✓'].map((t, i) => { const n = gnode(g); txt(n, t, { size: 70, font: 'en', fill: 'rgba(255,200,87,.8)' }); T(n, { o: 0 }); return n; });
  c.cue(.2, 'pop'); c.cue(dur * .3, 'whoosh'); c.cue(dur * .6, 'ding'); c.cue(dur * .7, 'sparkle');
  return lt => {
    tagIn(tag, lt); pop(calc, lt, .1, { x: 560, y: 560 + bob(lt, 6, .6), s: 2.3, big: true });
    nums.forEach((n, i) => { const k = lt - (.5 + i * .35); T(n, { x: 380 + i * 130, y: 280 - Math.max(0, k) * 40 + Math.sin(lt * 2 + i) * 8, o: k > 0 ? Math.min(1, k * 3) * (1 - clamp((k - 1.6) / .6)) : 0 }); });
    rise(ch, lt, dur * .3, { x: 1400, y: 440, dx: 160, dy: 0 }); chart.setProgress(E.inOut(seg(lt, dur * .35, dur * .7)));
    pop(ok, lt, dur * .68, { x: 1700, y: 270, big: true }); rise(p, lt, dur * .62, { x: 1400, y: 780, dy: 30 });
  };
};
// 1.2
V.perfectPlan = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tag = tagp(c, tx.top, 130, { size: 56, bg: GOLD, fill: '#1b1100', stroke: 'none' });
  const sh = gnode(g); const s0 = sheet(sh, 760, 700); T(sh, { x: 520, y: 560, o: 0, r: -3 });
  const rows = [[tx.a, 'piggy'], [tx.b, 'chart']].map(([t, k], i) => { const r = gnode(sh); C(r, -270, -100 + i * 190, 38, 'none', { stroke: '#2a2a2a', 'stroke-width': 6 }); const ck = A.check(r, { r: 36 }); T(ck, { x: -270, y: -100 + i * 190, o: 0 }); const tt = txt(r, t, { size: 52, fill: '#17171f', x: -210, y: -82 + i * 190, anchor: 'start' }); r.__ck = ck; return r; });
  const pig = gnode(g); A.piggy(pig, {}); T(pig, { x: 1380, y: 380, s: 1.3, o: 0 });
  const bars = gnode(g); const chart = A.chart(bars, { color: GOLD, w: 420, h: 200, pts: [.9, .8, .72, .5, .4, .3, .12] }); T(bars, { x: 1380, y: 760, o: 0 });
  c.cue(.2, 'whoosh'); c.cue(dur * .3, 'tick'); c.cue(dur * .65, 'tick');
  return lt => {
    tagIn(tag, lt); pop(sh, lt, .1, { x: 520, y: 560, r: -3, d: .5 });
    rows.forEach((r, i) => pop(r.__ck, lt, dur * (.3 + i * .35), { x: -270, y: -100 + i * 190, big: true }));
    pop(pig, lt, dur * .28, { x: 1380, y: 380 + bob(lt, 6, .6), s: 1.3, big: true }); pop(bars, lt, dur * .62, { x: 1380, y: 760, big: true }); chart.setProgress(E.inOut(seg(lt, dur * .65, dur * .95)));
  };
};
// 1.3
V.plansFail = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sheets = [0, 1, 2].map(i => { const sh = gnode(g); sheet(sh, 340, 440); T(sh, { x: 460 + i * 340, y: 600, r: (i - 1) * 6, o: 0 }); return sh; });
  const xs = sheets.map((_, i) => { const x = A.cross(g, { r: 54 }); T(x, { o: 0 }); return x; });
  const mt = bigLine(c, tx.main, 190, { size: 110, maxW: 1500 });
  const st = gnode(g); R(st, -190, -70, 380, 140, 'none', 18, { stroke: RED, 'stroke-width': 14 }); txt(st, tx.stamp, { size: 100, font: 'en', fill: RED, y: 36, weight: 700 }); T(st, { x: 1500, y: 880, o: 0, r: -12 });
  c.cue(.2, 'pop'); [0, 1, 2].forEach(i => c.cue(dur * (.3 + i * .15), 'error', .6)); c.cue(dur * .75, 'stamp'); c.shake(dur * .75, 8, .3);
  return lt => {
    wp(mt, lt, .1, .2);
    sheets.forEach((sh, i) => { pop(sh, lt, .2 + i * .2, { x: 460 + i * 340, y: 600 + bob(lt, 5, .6, i), r: (i - 1) * 6, d: .5 }); const f = E.in2(seg(lt, dur * (.4 + i * .12), dur * (.4 + i * .12) + .7)); if (f > 0) T(sh, { x: 460 + i * 340 + f * (i - 1) * 40, y: 600 + f * 160, r: (i - 1) * 6 + f * (i - 1) * 25, o: 1 - f * .6 }); pop(xs[i], lt, dur * (.3 + i * .15), { x: 460 + i * 340, y: 560, big: true }); });
    pop(st, lt, dur * .72, { x: 1500, y: 880, r: -12, big: true });
  };
};
// 1.4
V.cantHandle = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = head(g, { mood: 'worry' }); T(me, { x: 560, y: 900, s: 1.8 });
  const qs = [0, 1, 2].map(i => { const q = gnode(g); txt(q, '?', { size: 120 + i * 20, font: 'en', fill: i % 2 ? GOLD : '#fff', y: 40 }); T(q, { o: 0 }); return q; });
  const coins = Array.from({ length: 9 }, () => { const k = gnode(g); A.coin(k, { r: 30 }); T(k, { o: 0 }); return k; });
  const w = gnode(g); A.wallet(w, { color: GOLD }); T(w, { x: 1280, y: 700, s: 1.6, o: 0 });
  const mt = bigLine(c, tx.main, 170, { size: 92, maxW: 1700 });
  c.cue(.3, 'pop'); c.cue(dur * .4, 'coins'); c.cue(dur * .6, 'error');
  return lt => {
    me.idle(lt, 1); const e = E.out3(seg(lt, 0, .5)); T(me, { x: lerp(380, 560, e), y: 900, s: 1.8, o: e }); wp(mt, lt, .1, .14);
    qs.forEach((q, i) => pop(q, lt, .5 + i * .25, { x: [400, 700, 840][i], y: [500, 420, 560][i] + bob(lt, 8, .8, i), r: (i - 1) * 12, big: true }));
    pop(w, lt, dur * .25, { x: 1280, y: 700 + bob(lt, 5, .6), s: 1.6, big: true });
    coins.forEach((k, i) => { const t = lt - (dur * .4 + i * .15); if (t < 0) { T(k, { o: 0 }); return; } T(k, { x: 1280 + (i % 2 ? 1 : -1) * t * (120 + i * 18), y: 640 - 160 * t + 320 * t * t, r: t * 300, o: 1 - clamp((t - 1.2) / .6) }); });
  };
};
// 1.5
V.eyesOpen = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 22, fill: 'rgba(255,200,87,.1)' }); T(rays, { x: 960, y: 520 });
  C(g, 960, 520, 480, 'url(#gGlowGold)', { opacity: .35 });
  const eye = gnode(g); const ea = A.eye(eye, {}); T(eye, { x: 960, y: 520, s: 2.6 });
  const lid = gnode(eye); P(lid, 'M -118 0 Q 0 -100 118 0 L 118 -120 L -118 -120 Z', '#0c0c12'); P(lid, 'M -118 0 Q 0 90 118 0 L 118 120 L -118 120 Z', '#0c0c12');
  const sp = Array.from({ length: 8 }, (_, i) => { const s = gnode(g); A.sparkle(s, { r: 26, fill: i % 2 ? GOLD : '#fff' }); T(s, { o: 0 }); return s; });
  const mt = bigLine(c, tx.main, 850, { size: 120, fill: GOLD, maxW: 1500 });
  c.cue(.2, 'whoosh'); c.cue(dur * .35, 'riser', .7); c.cue(dur * .55, 'ding'); c.cue(dur * .6, 'sparkle'); c.flash(dur * .55, .3, '#fff', .35);
  return lt => {
    T(rays, { x: 960, y: 520, r: lt * 6 }); const o = E.out3(seg(lt, dur * .3, dur * .6)); lid.setAttribute('transform', `scale(1 ${(1 - o).toFixed(3)})`); lid.setAttribute('opacity', o < .99 ? 1 : 0);
    ea.parts.pupil.setAttribute('transform', `translate(${Math.sin(lt * 1.4) * 22} ${Math.cos(lt) * 8})`); T(eye, { x: 960, y: 520, s: 2.6 * (1 + .05 * o) });
    sp.forEach((s, i) => { const k = seg(lt, dur * .55 + i * .03, dur * .55 + 1), a = i / 8 * 6.28; T(s, { x: 960 + Math.cos(a) * (300 + 160 * k), y: 520 + Math.sin(a) * (200 + 100 * k), s: Math.sin(k * Math.PI) * 1.4, o: k > 0 && k < 1 ? 1 : 0 }); });
    wp(mt, lt, dur * .5, .16, true);
  };
};
// 1.6
V.titleMath = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 22, fill: 'rgba(255,200,87,.08)' }); T(rays, { x: 960, y: 520 });
  const calc = gnode(g); A.calculator(calc, { display: '2 + 2' }); T(calc, { x: 960, y: 480, s: 2.2 });
  const x = A.cross(g, { r: 110 }); T(x, { x: 1060, y: 380, o: 0 });
  const br = gnode(g); brain(br); const hr = gnode(g); A.heart(hr, { color: RED }); T(br, { x: 960, y: 480, s: 0.01, o: 0 }); T(hr, { x: 1160, y: 560, s: 0.01, o: 0 });
  const l1 = bigLine(c, tx.l1, 170, { size: 120, maxW: 1400 }); const l2 = bigLine(c, tx.l2, 900, { size: 150, fill: GOLD, maxW: 1700 });
  const bs = rain(c, 14, 4, it => A.coin(it, { r: 26 }));
  c.cue(.05, 'impact'); c.flash(.02, .3, '#fff', .45); c.cue(dur * .3, 'stamp'); c.cue(dur * .5, 'switch'); c.cue(dur * .55, 'tada');
  return lt => {
    T(rays, { x: 960, y: 520, r: lt * 6 }); const m = E.inOut(seg(lt, dur * .35, dur * .6)); T(calc, { x: 960, y: 480 + bob(lt, 5, .7), s: 2.2 * (1 - m * .8), o: 1 - m, r: -m * 30 });
    pop(x, lt, dur * .25, { x: 1060, y: 380, big: true }); if (m > 0) T(x, { o: 1 - m });
    T(br, { x: 800, y: 480 + bob(lt, 6, .8), s: Math.max(.001, m * 2.2), o: m }); T(hr, { x: 1160, y: 500 + bob(lt, 6, .8, 1), s: Math.max(.001, m * 2.2 * (1 + .06 * Math.sin(lt * 7))), o: m });
    wp(l1, lt, .2, .3); wp(l2, lt, dur * .5, .3, true); bs(Math.max(0, lt - dur * .5));
  };
};
// 2.1
V.notJustMath = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tag = tagp(c, tx.tag, 130, { size: 52, bg: GOLD, fill: '#1b1100', stroke: 'none' });
  const me = head(g, { mood: 'think' }); T(me, { x: 460, y: 900, s: 1.9 });
  const cl = gnode(g); A.thought(cl, { w: 820, h: 440, fill: 'rgba(255,255,255,.07)' }); cl.querySelectorAll('ellipse,circle').forEach(n => { n.setAttribute('stroke', 'rgba(255,255,255,.35)'); n.setAttribute('stroke-width', 3); }); T(cl, { x: 1280, y: 400, o: 0 });
  const it = [['🧮', -240, -50], ['❤️', 0, -90], ['😰', 240, -40], ['🏠', -110, 80], ['🎯', 120, 90]].map(([e, x, y], i) => { const t = gnode(cl); txt(t, e, { size: 90, font: 'en', y: 30 }); T(t, { x, y, o: 0 }); t.__p = [x, y]; return t; });
  const mt = bigLine(c, tx.main, 800, { size: 100, maxW: 1100 }); T(mt, { x: 1280, y: 800 });
  c.cue(.2, 'pop'); it.forEach((_, i) => c.cue(dur * (.2 + i * .12), 'pop', .5)); c.cue(dur * .7, 'ping');
  return lt => {
    tagIn(tag, lt); me.idle(lt); const e = E.out3(seg(lt, 0, .5)); T(me, { x: lerp(300, 460, e), y: 900, s: 1.9, o: e }); pop(cl, lt, .2, { x: 1280, y: 400 + bob(lt, 6, .5), big: true });
    it.forEach((t, i) => pop(t, lt, dur * (.2 + i * .12), { x: t.__p[0], y: t.__p[1] + bob(lt, 6, .6, i), big: true })); wp(mt, lt, dur * .45, .16);
  };
};
// 2.2
V.rationalPaper = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sh = gnode(g); sheet(sh, 700, 720); T(sh, { x: 560, y: 560, o: 0, r: -2 });
  const ch = gnode(sh); const chart = A.chart(ch, { color: '#1f9d62', w: 460, h: 220, pts: [.9, .8, .66, .55, .4, .3, .12] }); T(ch, { x: 0, y: 40 }); ch.querySelectorAll('rect').forEach(r => r.setAttribute('fill', 'rgba(0,0,0,.06)'));
  const ck = A.check(g, { r: 70 }); T(ck, { x: 880, y: 300, o: 0 });
  const lab = pill(g, tx.main, { size: 110, bg: GOLD, fill: '#1b1100', padX: 60 }); T(lab, { x: 1380, y: 440, o: 0 });
  const sub = pill(g, tx.sub, { size: 52, bg: W5, fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }); T(sub, { x: 1380, y: 640, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .45, 'ding'); c.cue(dur * .5, 'stamp');
  return lt => { pop(sh, lt, .1, { x: 560, y: 560 + bob(lt, 4, .6), r: -2, d: .5 }); chart.setProgress(E.inOut(seg(lt, .4, dur * .5))); pop(ck, lt, dur * .5, { x: 880, y: 300, big: true }); pop(lab, lt, dur * .45, { x: 1380, y: 440, big: true }); rise(sub, lt, dur * .6, { x: 1380, y: 640, dy: 30 }); };
};
// 2.3
V.hardToDo = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tag = tagp(c, tx.tag, 130, { size: 52 });
  const m = P(g, 'M 100 900 L 560 380 L 760 620 L 980 300 L 1300 700 L 1520 520 L 1820 900 Z', 'rgba(255,255,255,.07)', { stroke: 'rgba(255,255,255,.25)', 'stroke-width': 4 });
  const mt = P(g, 'M 980 300 L 880 420 L 980 380 L 1060 430 Z', '#EAF6FF');
  const man = gnode(g); mini(man, '#8CD8FF', 1.5);
  const path = P(g, 'M 200 900 Q 500 880 700 700 T 1000 520 T 1300 360', 'none', { stroke: GOLD, 'stroke-width': 6, 'stroke-dasharray': '2 18', 'stroke-linecap': 'round' });
  const rocks = [[560, 780], [820, 640], [1080, 500]].map(([x, y]) => { const r = P(g, 'M -40 30 L -30 -20 L 10 -40 L 44 -10 L 40 30 Z', '#6b6f85'); T(r, { x, y, o: 0 }); r.__p = [x, y]; return r; });
  const flag = gnode(g); L(flag, 0, 0, 0, -120, '#fff', 8); P(flag, 'M 0 -120 L 80 -96 L 0 -72 Z', RED); T(flag, { x: 1300, y: 330, o: 0 });
  const mtl = bigLine(c, tx.main, 215, { size: 92, fill: GOLD, maxW: 1400 });
  c.cue(.2, 'whoosh'); c.cue(dur * .5, 'thud'); c.cue(dur * .75, 'error');
  return lt => {
    tagIn(tag, lt); const p = E.inOut(seg(lt, .3, dur * .85)); const pt = pathPt(path, p); T(man, { x: pt.x, y: pt.y - 60 + Math.sin(lt * 7) * 4, r: bob(lt, 5, 2) + 8 });
    rocks.forEach((r, i) => pop(r, lt, .4 + i * .3, { x: r.__p[0], y: r.__p[1], d: .4 })); pop(flag, lt, .6, { x: 1300, y: 330, d: .4 }); wp(mtl, lt, dur * .5, .16, true);
  };
};
// 2.4
V.threeInputs = c => {
  const { g, S, dur } = c, tx = S.txt;
  const items = [[tx.a, '❤️', '#FF4D6D'], [tx.b, '📖', '#6EC8FF'], [tx.c, '🌍', '#3DDC97']];
  const cards = items.map(([lab, em, col], i) => { const gr = gnode(g); A.card(gr, 440, 220, { fill: 'rgba(255,255,255,.06)', stroke: col, sw: 3, shadow: true }); txt(gr, em, { size: 84, font: 'en', x: -140, y: 28 }); txt(gr, lab, { size: 46, fill: '#fff', x: 40, y: 16 }); T(gr, { x: 420, y: 260 + i * 270, o: 0 }); return gr; });
  const lines = [0, 1, 2].map(i => P(g, `M 650 ${260 + i * 270} C 900 ${260 + i * 270} 900 540 1180 540`, 'none', { stroke: items[i][2], 'stroke-width': 6, 'stroke-linecap': 'round' }));
  const out = gnode(g); C(out, 0, 0, 150, GOLD); txt(out, tx.out, { size: 62, fill: '#1b1100', y: 20 }); C(out, 0, 0, 190, 'url(#gGlowGold)', { opacity: .4 }); T(out, { x: 1500, y: 540, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .2, 'pop'); c.cue(dur * .4, 'pop'); c.cue(dur * .65, 'ding');
  return lt => { cards.forEach((gr, i) => pop(gr, lt, dur * (.05 + i * .2), { x: 420, y: 260 + i * 270 + bob(lt, 5, .6, i), big: true })); lines.forEach((l, i) => draw(l, seg(lt, dur * (.12 + i * .2), dur * (.3 + i * .2)))); pop(out, lt, dur * .65, { x: 1500, y: 540 + bob(lt, 6, .8), s: 1 + .04 * Math.sin(lt * 6), big: true }); };
};
// 2.5
V.realisticWord = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 24, fill: 'rgba(61,220,151,.09)' }); T(rays, { x: 960, y: 520 }); C(g, 960, 520, 520, 'url(#gGlowMint)', { opacity: .3 });
  const tg = tagp(c, tx.tag, 170, { size: 56, font: 'en', bg: GREEN, fill: '#04281b', stroke: 'none' });
  const big = bigLine(c, tx.main, 600, { size: 230, fill: '#fff', maxW: 1650 });
  const ul = L(g, 260, 700, 1660, 700, GREEN, 14); const sp = Array.from({ length: 6 }, (_, i) => { const s = gnode(g); A.sparkle(s, { r: 26, fill: i % 2 ? GOLD : '#fff' }); T(s, { o: 0 }); return s; });
  const ck = A.check(g, { r: 80 }); T(ck, { x: 960, y: 880, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .35, 'stamp'); c.cue(dur * .6, 'ding'); c.cue(dur * .62, 'sparkle');
  return lt => { T(rays, { x: 960, y: 520, r: lt * 6 }); tagIn(tg, lt); wp(big, lt, .15, .3, true); ul.setAttribute('x2', 260 + 1400 * E.out3(seg(lt, dur * .35, dur * .6))); pop(ck, lt, dur * .6, { x: 960, y: 880, big: true }); sp.forEach((s, i) => { const k = seg(lt, dur * .6 + i * .04, dur * .6 + .9), a = i / 6 * 6.28; T(s, { x: 960 + Math.cos(a) * (500 + 80 * k), y: 600 + Math.sin(a) * (200 + 60 * k), s: Math.sin(k * Math.PI) * 1.4, o: k > 0 && k < 1 ? 1 : 0 }); }); };
};
// 2.6
V.vsCompare = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mk = (title, sub, col, em, x) => { const gr = gnode(g); A.card(gr, 760, 700, { fill: 'rgba(255,255,255,.05)', stroke: col, sw: 4, shadow: true }); txt(gr, em, { size: 190, font: 'en', y: -50 }); const p = pill(gr, title, { size: 70, bg: col, fill: '#0a0a10' }); T(p, { y: 130 }); txt(gr, sub, { size: 46, fill: '#fff', y: 250 }); T(gr, { x, y: 540, o: 0 }); return gr; };
  const L_ = mk(tx.a, tx.a2, SKY, '🧮', 500), R_ = mk(tx.b, tx.b2, GREEN, '🌱', 1420);
  const vs = gnode(g); C(vs, 0, 0, 62, GOLD); txt(vs, 'VS', { size: 50, font: 'en', fill: '#1b1100', y: 17, weight: 700 }); T(vs, { x: 960, y: 540, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .5, 'whoosh'); c.cue(dur * .8, 'pop');
  return lt => { pop(L_, lt, .1, { x: 500, y: 540 + bob(lt, 5, .5), d: .5 }); pop(R_, lt, dur * .45, { x: 1420, y: 540 + bob(lt, 5, .5, 1), d: .5 }); pop(vs, lt, dur * .8, { x: 960, y: 540, big: true }); };
};
// 2.7
V.winPlan = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 24, fill: 'rgba(255,200,87,.09)' }); T(rays, { x: 960, y: 480 }); C(g, 960, 480, 460, 'url(#gGlowGold)', { opacity: .35 });
  const tr = gnode(g); P(tr, 'M -110 -140 L 110 -140 Q 110 40 0 80 Q -110 40 -110 -140 Z', GOLD); P(tr, 'M -110 -110 Q -190 -110 -170 -40 Q -150 10 -100 20', 'none', { stroke: GOLD, 'stroke-width': 14 }); P(tr, 'M 110 -110 Q 190 -110 170 -40 Q 150 10 100 20', 'none', { stroke: GOLD, 'stroke-width': 14 }); R(tr, -20, 80, 40, 70, '#E9A02A'); R(tr, -90, 150, 180, 36, '#B07A10', 10); A.star(tr, { r: 40 }); T(tr, { x: 960, y: 440, s: 0.01 });
  const mt = bigLine(c, tx.main, 850, { size: 112, fill: '#fff', maxW: 1700 });
  const bs = rain(c, 16, 6, it => A.coin(it, { r: 26 }));
  c.cue(.2, 'whoosh'); c.cue(dur * .3, 'tada', .9); c.cue(dur * .35, 'sparkle');
  return lt => { T(rays, { x: 960, y: 480, r: lt * 6 }); const k = E.backBig(seg(lt, .15, .8)); T(tr, { x: 960, y: 440 + bob(lt, 6, .8), s: Math.max(.001, k * 2.2), o: k > 0 ? 1 : 0 }); wp(mt, lt, dur * .3, .2, true); bs(Math.max(0, lt - dur * .3)); };
};
// 3.1
V.stockLong = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tp = tagp(c, tx.top, 120, { size: 50 });
  const me = head(g, { mood: 'smile' }); T(me, { x: 400, y: 900, s: 1.7 });
  const card = gnode(g); A.card(card, 1000, 560, { fill: 'rgba(255,255,255,.05)', stroke: 'rgba(61,220,151,.5)', sw: 3, shadow: true }); T(card, { x: 1320, y: 480, o: 0 });
  const ch = gnode(card); const chart = A.chart(ch, { color: GREEN, w: 760, h: 300, pts: [.9, .84, .8, .86, .7, .6, .66, .42, .34, .2, .06] }); T(ch, { y: 10 });
  const tg = pill(card, tx.tag, { size: 44, bg: GREEN, fill: '#04281b' }); T(tg, { y: -230 });
  const gl = pill(g, tx.gain, { size: 56, bg: GOLD, fill: '#1b1100' }); T(gl, { x: 1320, y: 810, o: 0 });
  c.cue(.2, 'whoosh'); c.cue(dur * .6, 'ding'); c.cue(dur * .65, 'coins');
  return lt => { tagIn(tp, lt); me.idle(lt); const e = E.out3(seg(lt, 0, .5)); T(me, { x: lerp(260, 400, e), y: 900, s: 1.7, o: e }); pop(card, lt, .2, { x: 1320, y: 480, d: .5 }); chart.setProgress(E.inOut(seg(lt, .6, dur * .85))); rise(gl, lt, dur * .6, { x: 1320, y: 810, dy: 30 }); };
};
// 3.2
V.pureLogic = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 22, fill: 'rgba(110,200,255,.08)' }); T(rays, { x: 960, y: 480 });
  const big = gnode(g); txt(big, tx.big, { size: 380, font: 'en', fill: SKY, weight: 700, stroke: '#000', sw: 18, y: 130 }); T(big, { x: 880, y: 440, s: .01 });
  const ck = A.check(g, { r: 100 }); T(ck, { x: 1560, y: 380, o: 0 });
  const mt = bigLine(c, tx.main, 860, { size: 120, fill: GOLD, maxW: 1400 });
  c.cue(.1, 'impact'); c.cue(dur * .5, 'ding'); c.flash(.05, .25, '#bfe6ff', .3);
  return lt => { T(rays, { x: 960, y: 480, r: lt * 6 }); const k = E.backBig(seg(lt, .05, .6)); T(big, { x: 880, y: 440, s: Math.max(.001, k), o: k > 0 ? 1 : 0 }); pop(ck, lt, dur * .5, { x: 1560, y: 380, big: true }); wp(mt, lt, dur * .35, .2, true); };
};
// 3.3
V.marketDrop = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tp = tagp(c, tx.tag, 120, { size: 52, bg: RED, fill: '#fff', stroke: 'none' });
  const card = gnode(g); A.card(card, 1000, 560, { fill: 'rgba(255,90,95,.06)', stroke: 'rgba(255,90,95,.55)', sw: 3, shadow: true }); T(card, { x: 1320, y: 460, o: 0 });
  const ch = gnode(card); const chart = A.chart(ch, { color: RED, w: 760, h: 300, pts: [.1, .16, .1, .22, .18, .3, .5, .7, .94] }); T(ch, { y: 20 });
  const me = head(g, { mood: 'worry' }); T(me, { x: 420, y: 900, s: 1.8 });
  const fear = pill(g, tx.fear, { size: 90, bg: '#fff', fill: RED, padX: 50 }); T(fear, { x: 420, y: 340, o: 0 });
  const sw = [0, 1, 2].map(() => { const d = P(g, 'M 0 -12 Q 10 4 0 12 Q -10 4 0 -12 Z', '#6EC8FF'); T(d, { o: 0 }); return d; });
  c.cue(.2, 'whoosh'); c.cue(dur * .45, 'thud'); c.cue(dur * .55, 'error'); c.shake(dur * .5, 8, .4);
  return lt => { tagIn(tp, lt); me.idle(lt, 2); me.setMood(lt > dur * .5 ? 'worry' : 'smile'); T(me, { x: 420, y: 900, s: 1.8 }); pop(card, lt, .2, { x: 1320, y: 460, d: .5 }); chart.setProgress(E.in2(seg(lt, .5, dur * .6))); pop(fear, lt, dur * .55, { x: 420, y: 340 + bob(lt, 6, 1), big: true }); sw.forEach((d, i) => { const k = ((lt - dur * .55) * 1.2 + i / 3) % 1; T(d, { x: 330 + i * 60, y: 560 + k * 80, s: 1.6, o: lt > dur * .55 ? 1 - k : 0 }); }); };
};
// 3.4
V.sellAll = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tp = tagp(c, tx.tag, 120, { size: 52, bg: RED, fill: '#fff', stroke: 'none' });
  const door = gnode(g); R(door, -150, -260, 300, 520, 'rgba(255,255,255,.07)', 14, { stroke: 'rgba(255,255,255,.4)', 'stroke-width': 5 }); txt(door, 'EXIT', { size: 70, font: 'en', fill: GREEN, y: -190 }); A.arrow(door, { len: 160, color: GREEN }); T(door, { x: 1560, y: 600 });
  const man = gnode(g); mini(man, '#FF8A94', 2.0); T(man, { x: 300, y: 700 });
  const sh = Array.from({ length: 8 }, (_, i) => { const n = gnode(g); R(n, -70, -40, 140, 80, '#18202c', 10, { stroke: RED, 'stroke-width': 4 }); txt(n, 'SELL', { size: 36, font: 'en', fill: RED, y: 12 }); T(n, { o: 0 }); return n; });
  const mt = bigLine(c, tx.main, 830, { size: 100, maxW: 1500 });
  c.cue(.2, 'whoosh'); c.cue(dur * .5, 'coins'); c.cue(dur * .8, 'thud');
  return lt => { tagIn(tp, lt); const p = E.in2(seg(lt, .3, dur * .85)); T(man, { x: lerp(300, 1500, p), y: 700 + Math.abs(Math.sin(lt * 9)) * -24, r: 6 }); sh.forEach((n, i) => { const k = lt - (.4 + i * .18); if (k < 0) { T(n, { o: 0 }); return; } T(n, { x: lerp(300, 1560, E.in2(clamp(k / 1.6))) + i * 6, y: 640 - i * 36 + Math.sin(k * 6 + i) * 20, r: k * 40, o: 1 - clamp((k - 1.2) / .5) }); }); T(door, { x: 1560, y: 600 }); wp(mt, lt, dur * .45, .15); };
};
// 3.5
V.mathWrong = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tp = tagp(c, tx.tag, 130, { size: 56, font: 'en', bg: SKY, fill: '#02283a', stroke: 'none' });
  const calc = gnode(g); A.calculator(calc, { display: '-₹ 2,40,000' }); T(calc, { x: 640, y: 540, s: 2.4, o: 0 });
  const x = A.cross(g, { r: 120 }); T(x, { x: 1360, y: 460, o: 0 });
  const ch = gnode(g); const chart = A.chart(ch, { color: RED, w: 420, h: 180, pts: [.1, .3, .2, .5, .6, .9] }); T(ch, { x: 1360, y: 760, o: 0 });
  const mt = bigLine(c, tx.main, 260, { size: 100, maxW: 1500 });
  c.cue(.2, 'pop'); c.cue(dur * .45, 'error'); c.cue(dur * .5, 'stamp');
  return lt => { tagIn(tp, lt); wp(mt, lt, .15, .16); pop(calc, lt, .2, { x: 640, y: 540 + bob(lt, 5, .6), s: 2.4, big: true }); pop(x, lt, dur * .45, { x: 1360, y: 460, big: true }); pop(ch, lt, dur * .55, { x: 1360, y: 760 }); chart.setProgress(seg(lt, dur * .6, dur * .95)); };
};
// 3.6
V.mentalPeace = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tp = tagp(c, tx.tag, 100, { size: 52, bg: GREEN, fill: '#04281b', stroke: 'none' });
  C(g, 960, 540, 520, 'url(#gGlowMint)', { opacity: .35 });
  const me = head(g, { mood: 'grin', skin: 'brown' }); T(me, { x: 700, y: 900, s: 2.0 });
  const lot = gnode(g); [[-90, 40, -30], [90, 40, 30], [0, 0, 0]].forEach(([x, y, r]) => { const p = P(lot, 'M 0 0 Q -50 -60 0 -110 Q 50 -60 0 0 Z', '#FF8AD0'); T(p, { x, y, r }); }); T(lot, { x: 1380, y: 520, s: 1.9, o: 0 });
  const ht = gnode(g); A.heart(ht, { color: GREEN }); T(ht, { x: 1380, y: 350, s: .01, o: 0 });
  const mt = bigLine(c, tx.main, 250, { size: 108, fill: GOLD, maxW: 1600 }); const ok = pill(g, 'అందుకే అది కరెక్ట్', { size: 50, bg: '#fff', fill: '#10101a' }); T(ok, { x: 1380, y: 800, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .4, 'ping'); c.cue(dur * .55, 'sparkle');
  return lt => { tagIn(tp, lt); me.idle(lt, 1); const e = E.out3(seg(lt, 0, .5)); T(me, { x: lerp(500, 700, e), y: 900, s: 2.0, o: e }); wp(mt, lt, .15, .16); pop(lot, lt, dur * .3, { x: 1380, y: 540 + bob(lt, 7, .5), s: 1.9, big: true }); T(ht, { x: 1380, y: 330 + bob(lt, 5, .7), s: seg(lt, dur * .45, dur * .6) * 1.1 * (1 + .07 * Math.sin(lt * 5)), o: seg(lt, dur * .45, dur * .55) }); rise(ok, lt, dur * .6, { x: 1380, y: 800, dy: 30 }); };
};
// 3.7
V.mindDecides = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sc = scale(g); T(sc, { x: 960, y: 350, s: 1.0 }); sc.tilt(0);
  const calc = gnode(sc.parts.L); A.calculator(calc, {}); T(calc, { y: 90, s: .55 });
  const br = gnode(sc.parts.R); brain(br); T(br, { y: 110, s: .9 });
  const l = pill(g, tx.l, { size: 50, bg: W5, fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }); T(l, { x: 620, y: 140, o: 0 }); const r = pill(g, tx.r, { size: 50, bg: GOLD, fill: '#1b1100' }); T(r, { x: 1300, y: 140, o: 0 });
  const mt = bigLine(c, tx.main, 840, { size: 110, fill: '#fff', maxW: 1500 });
  c.cue(.1, 'whoosh'); c.cue(dur * .5, 'thud'); c.cue(dur * .6, 'ding');
  return lt => { pop(sc, lt, .1, { x: 960, y: 350, d: .5 }); sc.tilt(lerp(-6, 15, E.back(seg(lt, dur * .25, dur * .6))) + bob(lt, .6, .6)); rise(l, lt, dur * .1, { x: 620, y: 140, dy: -20 }); rise(r, lt, dur * .3, { x: 1300, y: 140, dy: -20 }); wp(mt, lt, dur * .5, .14, true); };
};
// 4.1
V.balancePlan = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mt = bigLine(c, tx.main, 170, { size: 100, fill: GOLD, maxW: 1700 });
  const calc = gnode(g); A.calculator(calc, {}); T(calc, { x: 480, y: 600, s: 1.8, o: 0 }); const ht = gnode(g); A.heart(ht, { color: RED }); T(ht, { x: 1440, y: 600, s: .01, o: 0 });
  const plus = gnode(g); C(plus, 0, 0, 64, GOLD); txt(plus, '+', { size: 100, font: 'en', fill: '#1b1100', y: 32 }); T(plus, { x: 960, y: 600, o: 0 });
  const l = pill(g, tx.l, { size: 50, bg: SKY, fill: '#02283a' }); T(l, { x: 480, y: 830, o: 0 }); const r = pill(g, tx.r, { size: 50, bg: RED, fill: '#fff' }); T(r, { x: 1440, y: 830, o: 0 });
  const bs = rain(c, 12, 8, it => A.coin(it, { r: 24 }));
  c.cue(.2, 'pop'); c.cue(dur * .35, 'pop'); c.cue(dur * .55, 'ding'); c.cue(dur * .6, 'tada', .8);
  return lt => { wp(mt, lt, .1, .14); pop(calc, lt, .3, { x: 480, y: 600 + bob(lt, 5, .6), s: 1.8, big: true }); pop(ht, lt, dur * .3, { x: 1440, y: 600 + bob(lt, 5, .6, 1), s: 2.1 * (1 + .05 * Math.sin(lt * 6)), big: true }); pop(plus, lt, dur * .5, { x: 960, y: 600, big: true }); rise(l, lt, .6, { x: 480, y: 830, dy: 30 }); rise(r, lt, dur * .4, { x: 1440, y: 830, dy: 30 }); bs(Math.max(0, lt - dur * .6)); };
};

// 4.5 thanks
V.thanksEnd = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 24, fill: 'rgba(255,200,87,.09)' }); T(rays, { x: 960, y: 480 }); C(g, 960, 480, 500, 'url(#gGlowGold)', { opacity: .3 });
  const ht = gnode(g); A.heart(ht, { color: RED }); T(ht, { x: 960, y: 400, s: .01 });
  const th = bigLine(c, tx.main, 760, { size: 150, fill: GOLD, maxW: 1700 });
  const bs = rain(c, 16, 3, it => A.heart(it, { color: '#FF6B81' }));
  c.cue(.1, 'tada', .8); c.cue(.2, 'sparkle');
  return lt => { T(rays, { x: 960, y: 480, r: lt * 6 }); const k = E.backBig(seg(lt, .05, .6)); T(ht, { x: 960, y: 400 + bob(lt, 6, .9), s: Math.max(.001, k * 2.2 * (1 + .06 * Math.sin(lt * 6))), o: k > 0 ? 1 : 0 }); wp(th, lt, .3, .25, true); bs(Math.max(0, lt - .3)); };
};
