'use strict';
// Portrait 1080x1920 redesign of episode 2 highlights. Layout: headline y 230-520, hero 560-1300, captions 1370-1640.
const CX = 540;
const hl = (c, str, y, size, fill = '#fff', maxW = 960) => { const o = fitRow(c.g, str, { size, fill, stroke: '#000', sw: 14, maxW }); T(o, { x: CX, y }); return o; };
const hlPop = (o, lt, t0, step = .18, big = false) => o.__row.__words.forEach((w, i) => pop(w, lt, t0 + i * step, { x: w.__x, y: 0, d: .5, big }));
const chip = (c, s, y, o = {}) => { const p = pill(c.g, s, Object.assign({ size: 46, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }, o)); T(p, { x: o.x == null ? CX : o.x, y, o: 0 }); return p; };
function dustR(c, n, seed) {
  const r = rng(seed), it = []; for (let i = 0; i < n; i++) { const d = C(c.g, 0, 0, 3 + r() * 4, '#fff', { opacity: 0 }); it.push({ d, x: r() * 1080, y: 500 + r() * 800, ph: r() * 6, t0: r() * 1.2 }); }
  return lt => it.forEach(o => { const k = lt - o.t0; o.d.setAttribute('cx', o.x + Math.sin(k + o.ph) * 30); o.d.setAttribute('cy', o.y - k * 25); o.d.setAttribute('opacity', k > 0 ? .5 * Math.min(1, k) : 0); });
}

// 1.1 expensive car passes
V.carPass = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sk2 = skyline(g, 9, '#0c0d14', 200, 520, 1180), sk1 = skyline(g, 3, '#161824', 150, 380, 1180);
  R(g, -100, 1180, 1300, 260, '#050507'); R(g, -100, 1176, 1300, 5, 'rgba(255,200,87,.6)');
  const dash = gnode(g); for (let i = 0; i < 12; i++) R(dash, i * 160, 1330, 90, 10, 'rgba(255,255,255,.45)', 4);
  const car = gnode(g); const cr = A.car(car, { color: RED }); T(car, { x: -700, y: 1100, s: 1.5 });
  const lines = Array.from({ length: 6 }, () => L(g, 0, 0, 0, 0, 'rgba(255,255,255,.35)', 4));
  const price = fitRow(g, tx.price, { size: 130, font: 'en', fill: GOLD, stroke: '#000', sw: 14, maxW: 960 }); T(price, { x: CX, y: 520 });
  const tag = chip(c, tx.tag, 330, { size: 56 });
  const cx = p => p < .5 ? lerp(-300, 540, E.out3(p / .5)) : lerp(540, 1700, E.in3((p - .5) / .5));
  c.cue(.05, 'whoosh'); c.cue(dur * .45, 'ding'); c.cue(dur * .55, 'whoosh');
  return lt => {
    const p = clamp(lt / dur), x = cx(p), v = (cx(clamp(p + .01)) - x) / (dur * .01) / 30;
    T(sk2, { x: -lt * 14 }); T(sk1, { x: -lt * 40 }); dash.setAttribute('transform', `translate(${-(lt * 420 * (.2 + Math.abs(v) / 30)) % 160} 0)`);
    T(car, { x, y: 1090 + bob(lt, 3, 3), s: 1.5 }); cr.spin(lt, Math.abs(v) * 40 + 40);
    lines.forEach((l, i) => { const len = Math.min(380, Math.abs(v) * 14); l.setAttribute('x1', x - 360 - i * 18); l.setAttribute('x2', x - 360 - len - i * 18); l.setAttribute('y1', 1030 + i * 22); l.setAttribute('y2', 1030 + i * 22); l.setAttribute('opacity', len > 20 ? .5 : 0); });
    hlPop(price, lt, dur * .4, 0, true); rise(tag, lt, .2, { x: CX, y: 330, dy: -30 });
  };
};

// 1.3 "he has too much money"
V.judgeBubble = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = head(g, { mood: 'angry', skin: 'brown' }); T(me, { x: 330, y: 1280, s: 2.0 });
  const sb = gnode(g); A.bubble(sb, { w: 900, h: 330, fill: '#fff', tail: 'bl' }); const parts = tx.say.replace('!', '').split(' '); txt(sb, parts.slice(0, 2).join(' '), { size: 96, fill: '#12121a', y: -20 }); txt(sb, parts.slice(2).join(' ') + '!', { size: 96, fill: '#c1121f', y: 90 }); T(sb, { x: CX, y: 560, o: 0 });
  const bills = Array.from({ length: 7 }, () => { const b = bill(g, 1.1); T(b, { o: 0 }); return b; });
  const tg = pill(g, tx.tag, { size: 66, bg: RED, fill: '#fff' }); T(tg, { x: 700, y: 1080, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .35, 'whoosh'); c.cue(dur * .6, 'error');
  return lt => {
    me.idle(lt, 2); T(me, { x: 330, y: 1280, s: 2.0 }); pop(sb, lt, .2, { x: CX, y: 560, big: true });
    bills.forEach((b, i) => { const k = lt - (dur * .3 + i * .18); if (k < 0) { T(b, { o: 0 }); return; } T(b, { x: 560 + k * 220 + i * 20, y: 1000 - k * 200 - Math.sin(k * 3 + i) * 40, r: k * 120 + i * 20, o: 1 - clamp(k / 1.8) }); });
    rise(tg, lt, dur * .55, { x: 700, y: 1080, dy: 30 });
  };
};

// 1.4 is it really a waste?
V.wasteQ = c => {
  const { g, S, dur } = c, tx = S.txt;
  const d_ = dustR(c, 18, 5);
  const car = gnode(g); const cr = A.car(car, { color: RED, beam: false }); T(car, { x: CX, y: 1120, s: 1.5 });
  const a = hl(c, 'డబ్బు', 300, 190), b = hl(c, 'వృధానేనా?', 480, 190, GOLD);
  const w = gnode(g); txt(w, tx.a, { size: 120, fill: RED, y: 40, stroke: '#000', sw: 12 }); const ln = L(w, -190, 10, 190, 10, RED, 14); T(w, { x: 300, y: 800, o: 0, r: -8 });
  const qm = gnode(g); txt(qm, tx.b, { size: 340, font: 'en', fill: GOLD, y: 120, weight: 700, stroke: '#000', sw: 14 }); T(qm, { x: 860, y: 800, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .45, 'stamp'); c.cue(dur * .7, 'riser', .6);
  return lt => {
    d_(lt); hlPop(a, lt, .1, .25, true); hlPop(b, lt, .5, .25, true);
    pop(car, lt, 0, { x: CX, y: 1120 + bob(lt, 4, 1), s: 1.5, d: .5 }); cr.spin(lt, 0);
    pop(w, lt, dur * .4, { x: 300, y: 800, r: -8, big: true }); ln.setAttribute('opacity', seg(lt, dur * .5, dur * .6)); pop(qm, lt, dur * .65, { x: 860, y: 800 + bob(lt, 10, .8), big: true, r: bob(lt, 6, .5) });
  };
};

// 2.1 no two people alike
V.noTwoAlike = c => {
  const { g, S, dur } = c, tx = S.txt;
  const tag = chip(c, tx.tag, 250, { size: 52 });
  const defs = [[{ skin: 'tan', hair: 'grey', glasses: true, shirt: '#3a4466' }, 190, '#4CC9F0', '🏠'], [{ skin: 'brown', hair: 'cap', capColor: RED, capColor2: '#a31b30', shirt: '#1d4d44' }, 540, GOLD, '🚗'], [{ skin: 'light', hair: 'bun', hairColor: '#4a2a1c', shirt: '#5b2f4c' }, 890, '#FF8AD0', '✈️']];
  const ps = defs.map(([o, x, col, em]) => { const gr = gnode(g); const p = head(gr, o); T(p, { y: 330, s: 1.0 }); const w = gnode(gr); A.wallet(w, { color: col }); T(w, { x: 0, y: 360, s: .42 }); const th = gnode(gr); A.thought(th, { w: 190, h: 150, fill: '#17171f' }); th.querySelectorAll('ellipse,circle').forEach(n => { n.setAttribute('stroke', col); n.setAttribute('stroke-width', 3); }); txt(th, em, { size: 66, font: 'en', y: 24 }); T(th, { x: 0, y: -20 }); T(gr, { x, y: 800, o: 0 }); gr.__p = p; return gr; });
  const mk = x => { const n = gnode(g); C(n, 0, 0, 44, GOLD); txt(n, '≠', { size: 70, font: 'en', fill: '#1b1100', y: 22 }); T(n, { x, y: 1000, o: 0 }); return n; };
  const ne = mk(365), ne2 = mk(715);
  const a = hl(c, 'ఏ ఇద్దరూ', 440, 130), b = hl(c, 'ఒకేలా కాదు', 580, 130, GOLD); T(a, { x: CX, y: 1250 }); T(b, { x: CX, y: 1250 }); T(a, { y: 480 }); T(b, { y: 1225 });
  T(b, { y: 1225 });
  c.cue(.1, 'pop'); c.cue(.4, 'pop'); c.cue(.7, 'pop'); c.cue(dur * .6, 'stamp');
  return lt => {
    rise(tag, lt, .05, { x: CX, y: 250, dy: -20 }); ps.forEach((gr, i) => { pop(gr, lt, .1 + i * .3, { x: [190, 540, 890][i], y: 800 + bob(lt, 6, .5, i), big: true }); gr.__p.idle(lt, i); });
    pop(ne, lt, dur * .55, { x: 365, y: 1000, big: true }); pop(ne2, lt, dur * .62, { x: 715, y: 1000, big: true }); hlPop(a, lt, dur * .1, .2); hlPop(b, lt, dur * .5, .2, true);
  };
};

// 2.4 iceberg
V.iceberg = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = chip(c, tx.top, 260, { size: 56 });
  R(g, 0, 760, 1080, 560, 'rgba(20,70,120,.55)'); const wave = P(g, 'M -60 760 Q 60 740 180 760 T 420 760 T 660 760 T 900 760 T 1140 760 L 1140 800 L -60 800 Z', 'rgba(110,200,255,.5)');
  const ice = gnode(g); P(ice, 'M 760 380 L 860 250 L 930 300 L 1010 190 L 1110 330 L 1170 380 Z', '#EAF6FF'); P(ice, 'M 1010 190 L 1110 330 L 1050 330 Z', '#C2E3FA'); P(ice, 'M 740 380 L 700 560 L 780 760 L 940 900 L 1120 860 L 1230 700 L 1200 520 L 1190 380 Z', 'rgba(150,200,240,.55)');
  const IX = 540 - 965 * .85, IY = 760 - 380 * .85;
  const car = gnode(g); A.car(car, { color: RED, beam: false });
  const tipl = pill(g, tx.tip, { size: 46, bg: '#fff', fill: '#10202e' }); T(tipl, { x: CX, y: 500, o: 0 });
  const icons = [['🏠', 'కలలు'], ['💔', 'కష్టాలు'], ['🎯', 'లక్ష్యాలు']].map(([e, l], i) => { const gr = gnode(g); txt(gr, e, { size: 90, font: 'en', y: 20 }); const p = pill(gr, l, { size: 38, bg: 'rgba(255,255,255,.14)', fill: '#fff' }); T(p, { y: 80 }); T(gr, { x: 540 + (i - 1) * 270, y: 960 + (i % 2) * 70, o: 0 }); return gr; });
  const deepl = pill(g, tx.deep, { size: 44, bg: GOLD, fill: '#1b1100' }); T(deepl, { x: CX, y: 1255, o: 0 });
  const mg = gnode(g); A.magnifier(mg, { r: 56 }); T(mg, { x: 200, y: 600, o: 0 });
  c.cue(.1, 'whoosh'); c.cue(dur * .25, 'pop'); icons.forEach((_, i) => c.cue(dur * (.45 + i * .12), 'pop', .6)); c.cue(dur * .8, 'ding');
  return lt => {
    rise(top, lt, .05, { x: CX, y: 260, dy: -20 }); T(wave, { x: Math.sin(lt * 1.2) * 20 }); rise(ice, lt, .1, { x: IX, y: IY, s: .85, dy: 80, d: .7 }); T(ice, { x: IX, y: IY + (1 - E.out3(seg(lt, .1, .8))) * 80, s: .85 });
    pop(car, lt, dur * .1, { x: 536, y: 640, s: .36, d: .5 });
    pop(mg, lt, dur * .2, { x: 300 + Math.sin(lt * 2) * 80, y: 620 + Math.cos(lt * 2) * 20, s: 1.2, big: true }); rise(tipl, lt, dur * .3, { x: CX, y: 500, dy: -30 });
    icons.forEach((gr, i) => pop(gr, lt, dur * (.45 + i * .12), { x: 540 + (i - 1) * 270, y: 960 + (i % 2) * 70 + bob(lt, 6, .5, i), big: true })); rise(deepl, lt, dur * .72, { x: CX, y: 1255, dy: 30 });
  };
};

// 3.3 not just a vehicle
V.notJustVehicle = c => {
  const { g, S, dur } = c, tx = S.txt;
  const d_ = dustR(c, 14, 9);
  const car = gnode(g); const cr = A.car(car, { color: RED, beam: false }); T(car, { x: CX, y: 900, s: 1.7 });
  const old = gnode(g); txt(old, tx.old, { size: 150, fill: '#fff', stroke: '#000', sw: 14, y: 50 }); const ln = L(old, -220, 20, 220, 20, RED, 14); T(old, { x: CX, y: 340, o: 0 });
  const heart = gnode(g); A.heart(heart, { color: GOLD }); heart.appendChild(el('circle', { r: 150, fill: 'url(#gGlowGold)', opacity: .8 })); T(heart, { x: CX, y: 900, s: .01, o: 0 });
  const mt = hl(c, tx.main, 1230, 104, GOLD);
  c.cue(.2, 'pop'); c.cue(dur * .35, 'stamp'); c.cue(dur * .55, 'switch'); c.cue(dur * .6, 'sparkle');
  return lt => {
    d_(lt); pop(old, lt, .15, { x: CX, y: 340, d: .4 }); ln.setAttribute('opacity', seg(lt, dur * .3, dur * .4)); ln.setAttribute('x2', -220 + 440 * E.out3(seg(lt, dur * .3, dur * .42)));
    const m = E.inOut(seg(lt, dur * .5, dur * .75)); T(car, { x: CX, y: 900 + bob(lt, 5, .8), s: 1.7 * (1 - m * .6), o: 1 - m }); cr.spin(lt, 0);
    T(heart, { x: CX, y: 900 + bob(lt, 6, .8), s: m * 2.4 * (1 + .06 * Math.sin(lt * 8)), o: m }); hlPop(mt, lt, dur * .62, .15, true);
  };
};

// 3.4 gift box
V.giftBox = c => {
  const { g, S, dur } = c, tx = S.txt;
  const a = hl(c, 'కష్టానికి తను', 300, 100), b = hl(c, 'ఇచ్చుకున్న బహుమతి', 430, 100, GOLD);
  const kid = gnode(g); mini(kid, '#FFB36B', 1.8); T(kid, { x: 200, y: 960, o: 0 }); const kd = [0, 1, 2].map(() => { const d = P(g, 'M 0 -10 Q 8 3 0 10 Q -8 3 0 -10 Z', '#6EC8FF'); T(d, { o: 0 }); return d; });
  const kl = pill(g, tx.kid, { size: 42, bg: 'rgba(255,255,255,.14)', fill: '#fff' }); T(kl, { x: 200, y: 1160, o: 0 });
  const ar = gnode(g); A.arrow(ar, { len: 180, color: GOLD }); T(ar, { x: 450, y: 900, o: 0 });
  const BX = 790, BY = 960;
  const box = gnode(g); R(box, -150, -60, 300, 220, '#C23B4E', 14); R(box, -20, -60, 40, 220, GOLD); const lid = gnode(box); R(lid, -170, -110, 340, 60, '#E5384F', 12); R(lid, -20, -110, 40, 60, GOLD); P(lid, 'M 0 -110 Q -80 -190 -90 -120 Q -60 -90 0 -110 Q 60 -90 90 -120 Q 80 -190 0 -110 Z', GOLD); T(box, { x: BX, y: BY, o: 0 });
  const car = gnode(g); A.car(car, { color: RED, beam: false }); T(car, { x: BX, y: BY, s: 0, o: 0 });
  const nl = pill(g, tx.now, { size: 44, bg: GOLD, fill: '#1b1100' }); T(nl, { x: BX, y: 1160, o: 0 });
  const sp = Array.from({ length: 8 }, (_, i) => { const s = gnode(g); A.sparkle(s, { r: 20, fill: i % 2 ? GOLD : '#fff' }); T(s, { o: 0 }); return s; });
  c.cue(.2, 'pop'); c.cue(dur * .4, 'whoosh'); c.cue(dur * .6, 'pop'); c.cue(dur * .72, 'sparkle');
  return lt => {
    hlPop(a, lt, .1, .12); hlPop(b, lt, .4, .12);
    pop(kid, lt, .15, { x: 200, y: 960 + bob(lt, 4, 1.4), big: true }); kd.forEach((d, i) => { const k = (lt * .9 + i / 3) % 1; T(d, { x: 150 + i * 50, y: 780 + k * 90, o: lt > .4 ? 1 - k : 0 }); }); rise(kl, lt, .3, { x: 200, y: 1160, dy: 20 });
    pop(ar, lt, dur * .35, { x: 450 + Math.sin(lt * 4) * 10, y: 900, d: .4 }); pop(box, lt, dur * .5, { x: BX, y: BY, s: .9, big: true });
    const o = E.out3(seg(lt, dur * .65, dur * .8)); T(lid, { x: o * 150, y: -o * 90, r: o * 40 }); const cs = seg(lt, dur * .68, dur * .85); pop(car, lt, dur * .68, { x: BX, y: BY - 20 - cs * 140, s: .5, d: .5 }); rise(nl, lt, dur * .7, { x: BX, y: 1160, dy: 20 });
    sp.forEach((s, i) => { const k = seg(lt, dur * .72 + i * .03, dur * .72 + .9); const an = i / 8 * 6.28, r = 90 + 200 * E.out3(k); T(s, { x: BX + Math.cos(an) * r, y: BY - 40 + Math.sin(an) * r * .7, s: Math.sin(k * Math.PI) * 1.4, o: k > 0 && k < 1 ? 1 : 0 }); });
  };
};

// 3.5 self respect, climbing
V.pride = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mt = hl(c, tx.main, 330, 150);
  const N_ = 6, SW = 150, X0 = 100, YB = 1230;
  const stairs = gnode(g); for (let i = 0; i < N_; i++) R(stairs, X0 + i * SW, YB - i * 90, SW, 500, i === N_ - 1 ? GOLD : `rgba(255,255,255,${.08 + i * .03})`, 6, { stroke: 'rgba(255,255,255,.25)', 'stroke-width': 2 });
  const man = gnode(g); mini(man, '#8CD8FF', 1.3);
  const crown = gnode(g); P(crown, 'M -70 40 L -70 -20 L -35 10 L 0 -40 L 35 10 L 70 -20 L 70 40 Z', GOLD);
  const lowl = pill(g, tx.low, { size: 42, bg: 'rgba(255,255,255,.14)', fill: '#fff' }); T(lowl, { x: 220, y: 1320, o: 0 }); const highl = pill(g, tx.high, { size: 46, bg: GOLD, fill: '#1b1100' }); T(highl, { x: 700, y: 640, o: 0 });
  const sp = Array.from({ length: 6 }, () => { const s = gnode(g); A.sparkle(s, { r: 22, fill: '#fff' }); T(s, { o: 0 }); return s; });
  const ex = X0 + (N_ - 1) * SW + SW / 2, ey = YB - (N_ - 1) * 90;
  c.cue(.2, 'whoosh'); c.cue(dur * .75, 'tada', .8); c.cue(dur * .8, 'sparkle');
  return lt => {
    rise(stairs, lt, 0, { dy: 60, d: .6 }); const p = E.inOut(seg(lt, .4, dur * .8)); const i = p * (N_ - 1), fr = i - Math.floor(i);
    T(man, { x: X0 + SW / 2 + p * (N_ - 1) * SW, y: YB - p * (N_ - 1) * 90 - 110 - Math.abs(Math.sin(fr * Math.PI)) * 30, r: bob(lt, 3, 3) });
    pop(lowl, lt, .5, { x: 220, y: 1320, d: .4 }); pop(crown, lt, dur * .82, { x: ex, y: ey - 330 + bob(lt, 6, 1), s: 1.3, big: true }); pop(highl, lt, dur * .85, { x: 700, y: 640, d: .4 });
    hlPop(mt, lt, dur * .1, .2, true); sp.forEach((s, k) => { const q = seg(lt, dur * .8 + k * .04, dur * .8 + .8), a = k / 6 * 6.28; T(s, { x: ex + Math.cos(a) * (60 + 140 * q), y: ey - 280 + Math.sin(a) * (60 + 100 * q), s: Math.sin(q * Math.PI) * 1.3, o: q > 0 && q < 1 ? 1 : 0 }); });
  };
};

// 3.8 insider: tip the scale to the heart
V.insider = c => {
  const { g, S, dur } = c, tx = S.txt;
  const l = chip(c, tx.l, 300, { size: 56 });
  const sc = scale(g); T(sc, { x: CX, y: 640, s: .95 }); sc.tilt(-14);
  const heart = gnode(sc.parts.R); A.heart(heart, { color: GOLD }); T(heart, { x: 0, y: 110, s: .75 }); heart.appendChild(el('circle', { r: 120, fill: 'url(#gGlowGold)', opacity: .8 }));
  const wb = gnode(sc.parts.L); const b1 = bill(wb, .8); T(b1, { y: 120 });
  const r = hl(c, tx.r, 1180, 120, GOLD);
  const sp = Array.from({ length: 8 }, (_, i) => { const s = gnode(g); A.sparkle(s, { r: 22, fill: i % 2 ? GOLD : '#fff' }); T(s, { o: 0 }); return s; });
  c.cue(.1, 'whoosh'); c.cue(dur * .35, 'thud'); c.cue(dur * .5, 'tada', .8); c.cue(dur * .55, 'sparkle'); c.flash(dur * .5, .25, '#ffe9b0', .2);
  return lt => {
    rise(l, lt, .05, { x: CX, y: 300, dy: -20 }); const t = E.back(seg(lt, .2, dur * .55)); sc.tilt(lerp(-14, 16, t) + bob(lt, .7, .6));
    T(heart, { x: 0, y: 110, s: .75 * (1 + .08 * Math.sin(lt * 7)) }); hlPop(r, lt, dur * .5, .2, true);
    sp.forEach((s, i) => { const k = seg(lt, dur * .5 + i * .03, dur * .5 + .9), a = i / 8 * 6.28; T(s, { x: 800 + Math.cos(a) * (60 + 160 * k), y: 780 + Math.sin(a) * (40 + 120 * k), s: Math.sin(k * Math.PI) * 1.4, o: k > 0 && k < 1 ? 1 : 0 }); });
  };
};

// 4.1 stop judging
V.stopJudge = c => {
  const { g, S, dur } = c, tx = S.txt;
  const a = hl(c, 'జడ్జ్ చేయడం', 290, 125), b = hl(c, 'మానేయండి', 430, 125, GOLD);
  const texts = ['ఎంత ఖర్చు!', 'ఇది వృధా!', 'ఎందుకు ఇలా?'];
  const bubs = texts.map((t, i) => { const bb = gnode(g); A.bubble(bb, { w: 380, h: 130, fill: '#fff', tail: i % 2 ? 'br' : 'bl' }); txt(bb, t, { size: 50, fill: '#12121a', y: 17 }); T(bb, { o: 0 }); return bb; });
  const bp = [[280, 640, -6], [800, 760, 6], [330, 1180, -4]];
  const sign = gnode(g); P(sign, 'M -90 -218 L 90 -218 L 218 -90 L 218 90 L 90 218 L -90 218 L -218 90 L -218 -90 Z', RED, { stroke: '#fff', 'stroke-width': 14, 'stroke-linejoin': 'round' }); txt(sign, tx.stop, { size: 120, font: 'en', fill: '#fff', y: 42, weight: 700 }); T(sign, { x: CX, y: 950, o: 0 });
  c.cue(.2, 'pop'); c.cue(.5, 'pop'); c.cue(.8, 'pop'); c.cue(dur * .45, 'stamp'); c.shake(dur * .45, 8, .3);
  return lt => {
    hlPop(a, lt, .1, .15); hlPop(b, lt, dur * .5, .18, true);
    bubs.forEach((bb, i) => { const t0 = .2 + i * .3, k = seg(lt, dur * .45, dur * .6); pop(bb, lt, t0, { x: bp[i][0], y: bp[i][1] + bob(lt, 6, .6, i), r: bp[i][2], big: true }); if (k > 0) T(bb, { s: 1 - k, o: 1 - k }); });
    const k = E.backBig(seg(lt, dur * .42, dur * .6)); T(sign, { x: CX, y: 950, s: Math.max(.001, k * (1 + .03 * Math.sin(lt * 6))), o: k > 0 ? 1 : 0, r: (1 - k) * -20 });
  };
};

// 4.3 maths vs emotions
V.moreThanMath = c => {
  const { g, S, dur } = c, tx = S.txt;
  const nums = ['1,25,000', '+ 8%', '× 12', '= ?', '₹ 40L', '÷ 3'].map((t, i) => { const n = gnode(g); txt(n, t, { size: 76 + (i % 3) * 12, font: 'en', fill: 'rgba(255,255,255,.75)', weight: 600 }); const r = rng(i + 20); n.__p = [270 + (i % 2) * 540 + r() * 40, 640 + Math.floor(i / 2) * 190 + r() * 30]; T(n, { x: n.__p[0], y: n.__p[1] }); return n; });
  const heart = gnode(g); A.heart(heart, { color: RED }); heart.appendChild(el('circle', { r: 240, fill: 'url(#gGlowCoral)', opacity: .7 })); T(heart, { x: CX, y: 900, s: .01, o: 0 });
  const a = hl(c, 'లెక్కలు కాదు…', 290, 120), b = hl(c, 'భావోద్వేగాలు', 440, 125, GOLD);
  c.cue(.2, 'pop'); c.cue(dur * .3, 'scratch'); c.cue(dur * .5, 'pop'); c.cue(dur * .5 + .1, 'ding'); c.cue(dur * .7, 'sparkle');
  return lt => {
    const f = E.in2(seg(lt, dur * .28, dur * .5)); nums.forEach((n, i) => T(n, { x: n.__p[0], y: n.__p[1] + f * 500, r: f * (i - 2.5) * 20, o: seg(lt, i * .08, i * .08 + .4) * (1 - f) }));
    const m = E.backBig(seg(lt, dur * .5, dur * .72)); T(heart, { x: CX, y: 920 + bob(lt, 6, .8), s: Math.max(.001, m * 2.5 * (1 + .07 * Math.sin(lt * 7))), o: m > 0 ? 1 : 0 });
    hlPop(a, lt, .1, .2); hlPop(b, lt, dur * .45, .18, true);
  };
};

// 4.5 subscribe + thanks
V.subscribeEnd = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 24, fill: 'rgba(255,200,87,.07)' }); T(rays, { x: CX, y: 800 });
  C(g, CX, 800, 480, 'url(#gGlowCoral)', { opacity: .25 });
  const pl = pill(g, tx.main, { size: 72, bg: '#fff', fill: '#10101a' }); T(pl, { x: CX, y: 290, o: 0 });
  const btn = gnode(g); const bg = R(btn, -330, -90, 660, 180, '#E5232B', 90); const lab = txt(btn, 'SUBSCRIBE', { size: 84, font: 'en', fill: '#fff', y: 30, ls: 3 }); T(btn, { x: CX, y: 620, o: 0 });
  const bell = gnode(g); const bl = A.bell(bell, {}); T(bell, { x: CX, y: 920, s: 1.5, o: 0 });
  const cur = gnode(g); A.hand(cur, {}); T(cur, { x: 860, y: 1180, s: 1.1, o: 0 });
  const th = hl(c, tx.thanks, 1180, 125, GOLD); T(th, { x: CX, y: 1210 });
  const tk = dur * .38; c.cue(.1, 'pop'); c.cue(.4, 'pop'); c.cue(tk, 'click'); c.cue(tk + .15, 'ding'); c.cue(tk + .3, 'bell'); c.cue(dur * .62, 'tada', .8); c.cue(dur * .64, 'sparkle');
  return lt => {
    T(rays, { x: CX, y: 800, r: lt * 6 }); pop(btn, lt, .1, { x: CX, y: 620, s: .95, big: true }); pop(bell, lt, .4, { x: CX, y: 920, s: 1.5, big: true }); rise(pl, lt, .1, { x: CX, y: 290, dy: -20 });
    const mv = E.inOut(seg(lt, dur * .15, tk)); const px = lerp(860, 600, mv), py = lerp(1180, 680, mv), press = seg(lt, tk, tk + .1) * (1 - seg(lt, tk + .1, tk + .3));
    pop(cur, lt, dur * .15, { x: px, y: py, s: 1.1 - .12 * press, d: .3 }); if (lt > dur * .15 + .3) T(cur, { x: px, y: py, s: 1.1 - .12 * press });
    const done = lt >= tk + .05; bg.setAttribute('fill', done ? '#3b3b48' : '#E5232B'); lab.textContent = done ? 'SUBSCRIBED ✓' : 'SUBSCRIBE'; lab.setAttribute('font-size', done ? 70 : 84);
    const rg = seg(lt, tk + .25, tk + 1.6); T(bl.parts.b, { r: rg > 0 && rg < 1 ? Math.sin(rg * 24) * 22 * (1 - rg) : 0 });
    hlPop(th, lt, dur * .6, .2, true);
  };
};
