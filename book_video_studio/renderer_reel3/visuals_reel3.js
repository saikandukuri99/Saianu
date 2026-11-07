'use strict';
// Portrait 1080x1920 redesign of episode 3 highlights (headline 230-520, hero 560-1300, captions 1370+).
// 1.3
V.plansFail = c => {
  const { g, S, dur } = c, tx = S.txt;
  const a = hl(c, 'ప్లాన్స్ ఎందుకు', 300, 120), b = hl(c, 'ఫెయిల్?', 450, 150, RED);
  const sheets = [0, 1, 2].map(i => { const sh = gnode(g); sheet(sh, 300, 400); T(sh, { x: 200 + i * 340, y: 900 + (i % 2) * 80, r: (i - 1) * 7, o: 0 }); return sh; });
  const xs = sheets.map(() => { const x = A.cross(g, { r: 50 }); T(x, { o: 0 }); return x; });
  const st = gnode(g); R(st, -180, -70, 360, 140, 'none', 18, { stroke: RED, 'stroke-width': 14 }); txt(st, tx.stamp, { size: 100, font: 'en', fill: RED, y: 36, weight: 700 }); T(st, { x: CX, y: 1230, o: 0, r: -10 });
  c.cue(.2, 'pop'); [0, 1, 2].forEach(i => c.cue(dur * (.3 + i * .15), 'error', .6)); c.cue(dur * .75, 'stamp'); c.shake(dur * .75, 8, .3);
  return lt => {
    hlPop(a, lt, .1, .15); hlPop(b, lt, .4, .2, true);
    sheets.forEach((sh, i) => { pop(sh, lt, .2 + i * .2, { x: 200 + i * 340, y: 900 + (i % 2) * 80 + bob(lt, 5, .6, i), r: (i - 1) * 7, d: .5 }); const f = E.in2(seg(lt, dur * (.45 + i * .1), dur * (.45 + i * .1) + .7)); if (f > 0) T(sh, { y: 900 + (i % 2) * 80 + f * 140, r: (i - 1) * 7 + f * (i - 1) * 25, o: 1 - f * .5 }); pop(xs[i], lt, dur * (.3 + i * .15), { x: 200 + i * 340, y: 860 + (i % 2) * 80, big: true }); });
    pop(st, lt, dur * .72, { x: CX, y: 1230, r: -10, big: true });
  };
};
// 1.4
V.cantHandle = c => {
  const { g, S, dur } = c;
  const a = hl(c, 'అనుకున్నట్లు', 280, 120), b = hl(c, 'హ్యాండ్ చేయలేకపోతున్నాం?', 420, 84, GOLD);
  const me = head(g, { mood: 'worry' }); T(me, { x: 330, y: 1250, s: 2.1 });
  const qs = [0, 1, 2].map(i => { const q = gnode(g); txt(q, '?', { size: 150 + i * 20, font: 'en', fill: i % 2 ? GOLD : '#fff', y: 50 }); T(q, { o: 0 }); return q; });
  const w = gnode(g); A.wallet(w, { color: GOLD }); T(w, { x: 790, y: 1050, s: 1.7, o: 0 });
  const coins = Array.from({ length: 9 }, () => { const k = gnode(g); A.coin(k, { r: 30 }); T(k, { o: 0 }); return k; });
  c.cue(.3, 'pop'); c.cue(dur * .4, 'coins'); c.cue(dur * .6, 'error');
  return lt => {
    me.idle(lt, 1); hlPop(a, lt, .1, .2); hlPop(b, lt, .4, .15);
    qs.forEach((q, i) => pop(q, lt, .5 + i * .25, { x: [180, 520, 640][i], y: [760, 700, 880][i] + bob(lt, 8, .8, i), r: (i - 1) * 12, big: true }));
    pop(w, lt, dur * .25, { x: 790, y: 1050 + bob(lt, 5, .6), s: 1.7, big: true });
    coins.forEach((k, i) => { const t = lt - (dur * .4 + i * .15); if (t < 0) { T(k, { o: 0 }); return; } T(k, { x: 790 + (i % 2 ? 1 : -1) * t * (90 + i * 14), y: 960 - 200 * t + 380 * t * t, r: t * 300, o: 1 - clamp((t - 1.2) / .6) }); });
  };
};
// 1.6 title
V.titleMath = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 22, fill: 'rgba(255,200,87,.08)' }); T(rays, { x: CX, y: 860 });
  const calc = gnode(g); A.calculator(calc, { display: '2 + 2' }); T(calc, { x: CX, y: 860, s: 2.2 });
  const x = A.cross(g, { r: 100 }); T(x, { x: 640, y: 740, o: 0 });
  const br = gnode(g); brain(br); const hr = gnode(g); A.heart(hr, { color: RED }); T(br, { x: 340, y: 860, s: .01, o: 0 }); T(hr, { x: 760, y: 900, s: .01, o: 0 });
  const l1 = hl(c, tx.l1, 300, 140), l2 = hl(c, 'మనస్తత్వం', 1170, 165, GOLD), l3 = hl(c, 'ముఖ్యం!', 1330, 165, GOLD);
  c.cue(.05, 'impact'); c.flash(.02, .3, '#fff', .45); c.cue(dur * .4, 'switch'); c.cue(dur * .5, 'tada');
  return lt => {
    T(rays, { x: CX, y: 860, r: lt * 6 }); const m = E.inOut(seg(lt, dur * .35, dur * .65)); T(calc, { x: CX, y: 860 + bob(lt, 5, .7), s: 2.2 * (1 - m * .8), o: 1 - m, r: -m * 30 });
    pop(x, lt, dur * .2, { x: 640, y: 740, big: true }); if (m > 0) T(x, { o: 1 - m });
    T(br, { x: 330, y: 860 + bob(lt, 6, .8), s: Math.max(.001, m * 2.0), o: m }); T(hr, { x: 760, y: 880 + bob(lt, 6, .8, 1), s: Math.max(.001, m * 2.1 * (1 + .06 * Math.sin(lt * 7))), o: m });
    hlPop(l1, lt, .1, .25); hlPop(l2, lt, dur * .5, .2, true); hlPop(l3, lt, dur * .6, .2, true);
  };
};
// 2.2
V.rationalPaper = c => {
  const { g, S, dur } = c, tx = S.txt;
  const lab = pill(g, tx.main, { size: 140, bg: GOLD, fill: '#1b1100', padX: 70 }); T(lab, { x: CX, y: 330, o: 0 });
  const sub = chip(c, tx.sub, 480, { size: 52 });
  const sh = gnode(g); sheet(sh, 640, 640); T(sh, { x: CX, y: 920, o: 0, r: -2 });
  const ch = gnode(sh); const chart = A.chart(ch, { color: '#1f9d62', w: 420, h: 200, pts: [.9, .8, .66, .55, .4, .3, .12] }); T(ch, { x: 0, y: 70 }); ch.querySelectorAll('rect').forEach(r => r.setAttribute('fill', 'rgba(0,0,0,.06)'));
  const ck = A.check(g, { r: 70 }); T(ck, { x: 820, y: 640, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .45, 'ding'); c.cue(dur * .5, 'stamp');
  return lt => { pop(lab, lt, .1, { x: CX, y: 330, big: true }); rise(sub, lt, .3, { x: CX, y: 480, dy: 20 }); pop(sh, lt, .2, { x: CX, y: 920 + bob(lt, 4, .6), r: -2, d: .5 }); chart.setProgress(E.inOut(seg(lt, .5, dur * .6))); pop(ck, lt, dur * .6, { x: 820, y: 640, big: true }); };
};
// 2.3
V.hardToDo = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tg = chip(c, tx.tag, 250, { size: 52 });
  const a = hl(c, 'ఆచరించడం', 400, 130), b = hl(c, 'కష్టం', 560, 150, GOLD);
  P(g, 'M 0 1250 L 330 800 L 480 960 L 640 700 L 860 1000 L 1000 880 L 1100 1250 Z', 'rgba(255,255,255,.07)', { stroke: 'rgba(255,255,255,.25)', 'stroke-width': 4 });
  P(g, 'M 640 700 L 570 790 L 640 760 L 700 800 Z', '#EAF6FF');
  const man = gnode(g); mini(man, '#8CD8FF', 1.5);
  const path = P(g, 'M 60 1240 Q 240 1200 330 1080 T 520 940 T 660 760', 'none', { stroke: GOLD, 'stroke-width': 6, 'stroke-dasharray': '2 18', 'stroke-linecap': 'round' });
  const rocks = [[250, 1120], [420, 1000], [560, 880]].map(([x, y]) => { const r = P(g, 'M -40 30 L -30 -20 L 10 -40 L 44 -10 L 40 30 Z', '#6b6f85'); T(r, { x, y, o: 0 }); r.__p = [x, y]; return r; });
  const flag = gnode(g); L(flag, 0, 0, 0, -120, '#fff', 8); P(flag, 'M 0 -120 L 80 -96 L 0 -72 Z', RED); T(flag, { x: 700, y: 730, o: 0 });
  c.cue(.2, 'whoosh'); c.cue(dur * .5, 'thud'); c.cue(dur * .75, 'error');
  return lt => { rise(tg, lt, .05, { x: CX, y: 250, dy: -20 }); hlPop(a, lt, .1, .2); hlPop(b, lt, .4, .2, true); const p = E.inOut(seg(lt, .3, dur * .85)); const pt = pathPt(path, p); T(man, { x: pt.x, y: pt.y - 60 + Math.sin(lt * 7) * 4, r: bob(lt, 5, 2) + 8 }); rocks.forEach((r, i) => pop(r, lt, .4 + i * .3, { x: r.__p[0], y: r.__p[1], d: .4 })); pop(flag, lt, .6, { x: 700, y: 730, d: .4 }); };
};
// 2.6
V.vsCompare = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mk = (title, sub, col, em, y) => { const gr = gnode(g); A.card(gr, 900, 360, { fill: 'rgba(255,255,255,.05)', stroke: col, sw: 4, shadow: true }); txt(gr, em, { size: 150, font: 'en', x: -270, y: 40 }); const p = pill(gr, title, { size: 64, bg: col, fill: '#0a0a10' }); T(p, { x: 130, y: -50 }); txt(gr, sub, { size: 44, fill: '#fff', x: 130, y: 70 }); T(gr, { x: CX, y, o: 0 }); return gr; };
  const A_ = mk(tx.a, tx.a2, SKY, '🧮', 520), B_ = mk(tx.b, tx.b2, GREEN, '🌱', 1000);
  const vs = gnode(g); C(vs, 0, 0, 56, GOLD); txt(vs, 'VS', { size: 44, font: 'en', fill: '#1b1100', y: 15, weight: 700 }); T(vs, { x: CX, y: 760, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .5, 'whoosh'); c.cue(dur * .8, 'pop');
  return lt => { pop(A_, lt, .1, { x: CX, y: 520 + bob(lt, 5, .5), d: .5 }); pop(B_, lt, dur * .45, { x: CX, y: 1000 + bob(lt, 5, .5, 1), d: .5 }); pop(vs, lt, dur * .8, { x: CX, y: 760, big: true }); };
};
// 3.3
V.marketDrop = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tg = chip(c, tx.tag, 260, { size: 54, bg: RED, fill: '#fff', stroke: 'none' });
  const card = gnode(g); A.card(card, 920, 520, { fill: 'rgba(255,90,95,.06)', stroke: 'rgba(255,90,95,.55)', sw: 3, shadow: true }); T(card, { x: CX, y: 640, o: 0 });
  const ch = gnode(card); const chart = A.chart(ch, { color: RED, w: 700, h: 280, pts: [.1, .16, .1, .22, .18, .3, .5, .7, .94] }); T(ch, { y: 10 });
  const me = head(g, { mood: 'worry' }); T(me, { x: 340, y: 1290, s: 2.0 });
  const fear = pill(g, tx.fear, { size: 100, bg: '#fff', fill: RED, padX: 56 }); T(fear, { x: 700, y: 1060, o: 0 });
  c.cue(.2, 'whoosh'); c.cue(dur * .45, 'thud'); c.cue(dur * .55, 'error'); c.shake(dur * .5, 8, .4);
  return lt => { rise(tg, lt, .05, { x: CX, y: 260, dy: -20 }); me.idle(lt, 2); me.setMood(lt > dur * .5 ? 'worry' : 'smile'); T(me, { x: 340, y: 1290, s: 2.0 }); pop(card, lt, .2, { x: CX, y: 640, d: .5 }); chart.setProgress(E.in2(seg(lt, .5, dur * .6))); pop(fear, lt, dur * .55, { x: 700, y: 1060 + bob(lt, 6, 1), big: true }); };
};
// 3.4
V.sellAll = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tg = chip(c, tx.tag, 260, { size: 54, bg: RED, fill: '#fff', stroke: 'none' });
  const a = hl(c, 'షేర్లన్నీ', 420, 130), b = hl(c, 'అమ్మేశాడు', 580, 140, GOLD);
  const door = gnode(g); R(door, -150, -260, 300, 520, 'rgba(255,255,255,.07)', 14, { stroke: 'rgba(255,255,255,.4)', 'stroke-width': 5 }); txt(door, 'EXIT', { size: 70, font: 'en', fill: GREEN, y: -190 }); A.arrow(door, { len: 160, color: GREEN }); T(door, { x: 850, y: 1000 });
  const man = gnode(g); mini(man, '#FF8A94', 2.2); T(man, { x: 160, y: 1060 });
  const sh = Array.from({ length: 8 }, () => { const n = gnode(g); R(n, -70, -40, 140, 80, '#18202c', 10, { stroke: RED, 'stroke-width': 4 }); txt(n, 'SELL', { size: 36, font: 'en', fill: RED, y: 12 }); T(n, { o: 0 }); return n; });
  c.cue(.2, 'whoosh'); c.cue(dur * .5, 'coins'); c.cue(dur * .8, 'thud');
  return lt => { rise(tg, lt, .05, { x: CX, y: 260, dy: -20 }); hlPop(a, lt, .1, .2); hlPop(b, lt, .4, .2, true); const p = E.in2(seg(lt, .3, dur * .85)); T(man, { x: lerp(160, 780, p), y: 1060 + Math.abs(Math.sin(lt * 9)) * -24, r: 6 }); sh.forEach((n, i) => { const k = lt - (.4 + i * .18); if (k < 0) { T(n, { o: 0 }); return; } T(n, { x: lerp(160, 850, E.in2(clamp(k / 1.5))) + i * 6, y: 940 - i * 30 + Math.sin(k * 6 + i) * 20, r: k * 40, o: 1 - clamp((k - 1.0) / .5) }); }); T(door, { x: 850, y: 1000 }); };
};
// 3.6
V.mentalPeace = c => {
  const { g, S, dur } = c, tx = S.txt;
  C(g, CX, 900, 560, 'url(#gGlowMint)', { opacity: .35 });
  const tg = chip(c, tx.tag, 260, { size: 54, bg: GREEN, fill: '#04281b', stroke: 'none' });
  const a = hl(c, 'మానసిక', 430, 150, GOLD), b = hl(c, 'ప్రశాంతత', 600, 150, GOLD);
  const me = head(g, { mood: 'grin', skin: 'brown' }); T(me, { x: 330, y: 1280, s: 2.2 });
  const lot = gnode(g); [[-90, 40, -30], [90, 40, 30], [0, 0, 0]].forEach(([x, y, r]) => { const p = P(lot, 'M 0 0 Q -50 -60 0 -110 Q 50 -60 0 0 Z', '#FF8AD0'); T(p, { x, y, r }); }); T(lot, { x: 780, y: 1000, s: 1.9, o: 0 });
  const ht = gnode(g); A.heart(ht, { color: GREEN }); T(ht, { x: 780, y: 780, s: .01, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .4, 'ping'); c.cue(dur * .55, 'sparkle');
  return lt => { rise(tg, lt, .05, { x: CX, y: 260, dy: -20 }); hlPop(a, lt, .1, .2, true); hlPop(b, lt, .4, .2, true); me.idle(lt, 1); const e = E.out3(seg(lt, 0, .5)); T(me, { x: lerp(160, 330, e), y: 1280, s: 2.2, o: e }); pop(lot, lt, dur * .3, { x: 780, y: 1000 + bob(lt, 7, .5), s: 1.9, big: true }); T(ht, { x: 780, y: 780 + bob(lt, 5, .7), s: seg(lt, dur * .45, dur * .6) * 1.1 * (1 + .07 * Math.sin(lt * 5)), o: seg(lt, dur * .45, dur * .55) }); };
};
// 3.7
V.mindDecides = c => {
  const { g, S, dur } = c, tx = S.txt;
  const a = hl(c, 'నిర్ణయాన్ని', 280, 120), b = hl(c, 'శాసించేది?', 420, 130, GOLD);
  const sc = scale(g); T(sc, { x: CX, y: 800, s: .95 }); sc.tilt(0);
  const calc = gnode(sc.parts.L); A.calculator(calc, {}); T(calc, { y: 90, s: .55 });
  const br = gnode(sc.parts.R); brain(br); T(br, { y: 110, s: .9 });
  const l = pill(g, tx.l, { size: 50, bg: W5, fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }); T(l, { x: 260, y: 1180, o: 0 }); const r = pill(g, 'మానసిక పరిస్థితి', { size: 50, bg: GOLD, fill: '#1b1100' }); T(r, { x: 760, y: 1180, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .5, 'thud'); c.cue(dur * .6, 'ding');
  return lt => { hlPop(a, lt, .1, .2); hlPop(b, lt, .4, .2, true); pop(sc, lt, .1, { x: CX, y: 800, s: .95, d: .5 }); sc.tilt(lerp(-6, 15, E.back(seg(lt, dur * .25, dur * .6))) + bob(lt, .6, .6)); rise(l, lt, dur * .1, { x: 260, y: 1180, dy: 20 }); rise(r, lt, dur * .3, { x: 760, y: 1180, dy: 20 }); };
};
// 4.1
V.balancePlan = c => {
  const { g, S, dur } = c, tx = S.txt;
  const a = hl(c, 'మీ మనస్తత్వానికి', 280, 110), b = hl(c, 'తగిన ప్లాన్', 420, 140, GOLD);
  const calc = gnode(g); A.calculator(calc, {}); T(calc, { x: 290, y: 880, s: 1.9, o: 0 }); const ht = gnode(g); A.heart(ht, { color: RED }); T(ht, { x: 790, y: 880, s: .01 });
  const plus = gnode(g); C(plus, 0, 0, 56, GOLD); txt(plus, '+', { size: 90, font: 'en', fill: '#1b1100', y: 28 }); T(plus, { x: CX, y: 880, o: 0 });
  const l = pill(g, tx.l, { size: 48, bg: SKY, fill: '#02283a' }); T(l, { x: 290, y: 1180, o: 0 }); const r = pill(g, tx.r, { size: 48, bg: RED, fill: '#fff' }); T(r, { x: 790, y: 1180, o: 0 });
  const bs = rain(c, 12, 8, it => A.coin(it, { r: 24 }));
  c.cue(.2, 'pop'); c.cue(dur * .35, 'pop'); c.cue(dur * .55, 'ding'); c.cue(dur * .6, 'tada', .8);
  return lt => { hlPop(a, lt, .1, .15); hlPop(b, lt, dur * .1, .2, true); pop(calc, lt, .3, { x: 290, y: 880 + bob(lt, 5, .6), s: 1.9, big: true }); pop(ht, lt, dur * .3, { x: 790, y: 880 + bob(lt, 5, .6, 1), s: 2.2 * (1 + .05 * Math.sin(lt * 6)), big: true }); pop(plus, lt, dur * .5, { x: CX, y: 880, big: true }); rise(l, lt, .6, { x: 290, y: 1180, dy: 30 }); rise(r, lt, dur * .4, { x: 790, y: 1180, dy: 30 }); bs(Math.max(0, lt - dur * .6)); };
};
// 4.5
V.thanksEnd = c => {
  const { g, S, dur } = c;
  const rays = A.rays(g, { n: 24, fill: 'rgba(255,200,87,.09)' }); T(rays, { x: CX, y: 760 }); C(g, CX, 760, 500, 'url(#gGlowGold)', { opacity: .3 });
  const ht = gnode(g); A.heart(ht, { color: RED }); T(ht, { x: CX, y: 760, s: .01 });
  const a = hl(c, 'థాంక్యూ', 1130, 160, GOLD), b = hl(c, 'సో మచ్!', 1290, 160, GOLD);
  c.cue(.1, 'tada', .8); c.cue(.2, 'sparkle');
  return lt => { T(rays, { x: CX, y: 760, r: lt * 6 }); const k = E.backBig(seg(lt, .05, .6)); T(ht, { x: CX, y: 760 + bob(lt, 6, .9), s: Math.max(.001, k * 3 * (1 + .06 * Math.sin(lt * 6))), o: k > 0 ? 1 : 0 }); hlPop(a, lt, .2, .2, true); hlPop(b, lt, .5, .2, true); };
};
