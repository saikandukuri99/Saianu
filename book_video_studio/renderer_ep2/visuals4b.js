'use strict';
// Episode 2, black theme. Act 3 (the car example) and act 4 (conclusion + calls to action).
function mini(parent, col = '#8CD8FF', s = 1) { // tiny flat person
  const g = gnode(parent); C(g, 0, -62 * s, 22 * s, '#E0A678'); R(g, -22 * s, -38 * s, 44 * s, 70 * s, col, 18 * s); L(g, -22 * s, -26 * s, -34 * s, 20 * s, col, 12 * s); L(g, 22 * s, -26 * s, 34 * s, 20 * s, col, 12 * s); L(g, -10 * s, 30 * s, -12 * s, 78 * s, '#2a2f48', 14 * s); L(g, 10 * s, 30 * s, 12 * s, 78 * s, '#2a2f48', 14 * s); return g;
}
function pathPt(p, k) { const L_ = p.getTotalLength(); return p.getPointAtLength(clamp(k) * L_); }

// ============================================================== 3.1 hard-earned money becomes a car
V.buyCar = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = topPill(c, tx.top, { y: 120, size: 56, bg: GOLD, fill: '#1b1100', stroke: 'none' });
  const me = head(g, { mood: 'grin' }); T(me, { x: 400, y: 880, s: 1.6 });
  const drops = [0, 1, 2].map(i => { const d = P(g, 'M 0 -12 Q 10 4 0 12 Q -10 4 0 -12 Z', '#6EC8FF'); T(d, { o: 0 }); return d; });
  const stack = gnode(g); [0, 1, 2, 3].forEach(i => { const b = bill(stack, 1); T(b, { x: (i % 2) * 14, y: -i * 22, r: (i - 1.5) * 4 }); }); T(stack, { x: 900, y: 760, o: 0 });
  const bills = Array.from({ length: 8 }, () => { const b = bill(g, .8); T(b, { o: 0 }); return b; });
  const car = gnode(g); const cr = A.car(car, { color: RED }); T(car, { x: 1500, y: 640, s: 1.3, o: 0 });
  const tg = pill(g, tx.tag, { size: 52, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }); T(tg, { x: 1360, y: 880, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .3, 'coins'); c.cue(dur * .55, 'whoosh'); c.cue(dur * .75, 'ding');
  return lt => {
    me.idle(lt); rise(top, lt, .05, { x: 960, y: 120, dy: -20 }); T(me, { x: 400, y: 880, s: 1.6 });
    drops.forEach((d, i) => { const k = (lt * .8 + i / 3) % 1; T(d, { x: 330 + i * 70, y: 450 + k * 120, o: lt > .6 ? 1 - k : 0 }); });
    pop(stack, lt, dur * .22, { x: 900, y: 760, big: true });
    bills.forEach((b, i) => { const k = (lt - (dur * .4 + i * .12)) / .9; if (k < 0 || k > 1) { T(b, { o: 0 }); return; } const e = E.inOut(k); T(b, { x: lerp(900, 1420, e), y: lerp(740, 640, e) - Math.sin(e * Math.PI) * 160, r: e * 220, s: 1 - e * .4, o: 1 }); });
    pop(car, lt, dur * .55, { x: 1500, y: 640 + bob(lt, 5, .8), s: 1.3, d: .6 }); cr.spin(lt, 30); rise(tg, lt, dur * .7, { x: 1360, y: 880, dy: 20 });
  };
};

// ============================================================== 3.2 "what a fool! he could have bought a house"
V.foolHouse = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = head(g, { mood: 'angry' }); T(me, { x: 380, y: 880, s: 1.6 });
  const sb = gnode(g); A.bubble(sb, { w: 640, h: 190, fill: '#fff', tail: 'bl' }); txt(sb, tx.say, { size: 76, fill: '#12121a', y: 26 }); T(sb, { x: 760, y: 300, o: 0 });
  const house = gnode(g); A.house(house, {}); T(house, { x: 1450, y: 520, s: 1.9, o: 0 });
  const ar = P(g, 'M 760 640 Q 1100 360 1280 500', 'none', { stroke: GOLD, 'stroke-width': 8, 'stroke-dasharray': '4 18', 'stroke-linecap': 'round', opacity: 0 });
  const ht = pill(g, tx.house, { size: 48, bg: 'rgba(255,255,255,.12)', fill: '#fff', stroke: 'rgba(255,255,255,.4)', sw: 3 }); T(ht, { x: 1450, y: 780, o: 0 });
  const cr = gnode(g); A.car(cr, { color: RED, beam: false }); T(cr, { x: 1000, y: 780, s: .55, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .45, 'whoosh'); c.cue(dur * .6, 'pop'); c.cue(dur * .8, 'error');
  return lt => {
    me.idle(lt, 1); pop(sb, lt, .2, { x: 760, y: 300 + bob(lt, 6, .6), big: true }); pop(cr, lt, dur * .3, { x: 1000, y: 780, s: .55 });
    ar.setAttribute('opacity', seg(lt, dur * .45, dur * .55)); ar.setAttribute('stroke-dashoffset', -lt * 30); pop(house, lt, dur * .55, { x: 1450, y: 520 + bob(lt, 6, .6), s: 1.9, big: true }); rise(ht, lt, dur * .7, { x: 1450, y: 780, dy: 20 });
  };
};

// ============================================================== 3.3 it is not just a vehicle
V.notJustVehicle = c => {
  const { g, S, dur } = c, tx = S.txt;
  dust(c, 14, 9);
  const car = gnode(g); const cr = A.car(car, { color: RED, beam: false }); T(car, { x: 960, y: 560, s: 1.7 });
  const old = gnode(g); const ot = txt(old, tx.old, { size: 120, fill: '#fff', stroke: '#000', sw: 12, y: 40 }); const ln = L(old, -170, 20, 170, 20, RED, 12); T(old, { x: 960, y: 220, o: 0 });
  const heart = gnode(g); A.heart(heart, { color: '#FFC857' }); heart.appendChild(el('circle', { r: 150, fill: 'url(#gGlowGold)', opacity: .8 })); T(heart, { x: 960, y: 560, s: 0.01, o: 0 });
  const mt = fitRow(g, tx.main, { size: 100, fill: GOLD, stroke: '#000', sw: 14, maxW: 1400 }); T(mt, { x: 960, y: 880 });
  c.cue(.2, 'pop'); c.cue(dur * .35, 'stamp'); c.cue(dur * .55, 'switch'); c.cue(dur * .6, 'sparkle');
  return lt => {
    pop(old, lt, .15, { x: 960, y: 220, d: .4 }); ln.setAttribute('opacity', seg(lt, dur * .3, dur * .4)); ln.setAttribute('x2', -170 + 340 * E.out3(seg(lt, dur * .3, dur * .42)));
    const m = E.inOut(seg(lt, dur * .5, dur * .75)); T(car, { x: 960, y: 560 + bob(lt, 5, .8), s: 1.7 * (1 - m * .6), o: 1 - m }); cr.spin(lt, 0);
    T(heart, { x: 960, y: 560 + bob(lt, 6, .8), s: m * 1.9 * (1 + .06 * Math.sin(lt * 8)), o: m }); mt.__row.__words.forEach((w, i) => pop(w, lt, dur * .62 + i * .15, { x: w.__x, y: 0, d: .5, big: true }));
  };
};

// ============================================================== 3.4 a gift for years of hard work
V.giftBox = c => {
  const { g, S, dur } = c, tx = S.txt;
  const kid = gnode(g); mini(kid, '#FFB36B', 1.5); T(kid, { x: 380, y: 640, o: 0 }); const kd = [0, 1, 2].map(i => { const d = P(g, 'M 0 -10 Q 8 3 0 10 Q -8 3 0 -10 Z', '#6EC8FF'); T(d, { o: 0 }); return d; });
  const kl = pill(g, tx.kid, { size: 44, bg: 'rgba(255,255,255,.14)', fill: '#fff' }); T(kl, { x: 380, y: 820, o: 0 });
  const ar = gnode(g); A.arrow(ar, { len: 220, color: GOLD }); T(ar, { x: 760, y: 560, o: 0 });
  const box = gnode(g); R(box, -150, -60, 300, 220, '#C23B4E', 14); R(box, -20, -60, 40, 220, GOLD); const lid = gnode(box); R(lid, -170, -110, 340, 60, '#E5384F', 12); R(lid, -20, -110, 40, 60, GOLD); const bow = P(lid, 'M 0 -110 Q -80 -190 -90 -120 Q -60 -90 0 -110 Q 60 -90 90 -120 Q 80 -190 0 -110 Z', GOLD); T(box, { x: 1300, y: 640, o: 0 });
  const car = gnode(g); A.car(car, { color: RED, beam: false }); T(car, { x: 1300, y: 600, s: .0, o: 0 });
  const nl = pill(g, tx.now, { size: 44, bg: GOLD, fill: '#1b1100' }); T(nl, { x: 1300, y: 860, o: 0 });
  const mt = fitRow(g, tx.main, { size: 80, fill: '#fff', stroke: '#000', sw: 12, maxW: 1500 }); T(mt, { x: 960, y: 180 });
  const sp = Array.from({ length: 8 }, (_, i) => { const s = gnode(g); A.sparkle(s, { r: 20, fill: i % 2 ? GOLD : '#fff' }); T(s, { o: 0 }); return s; });
  c.cue(.2, 'pop'); c.cue(dur * .4, 'whoosh'); c.cue(dur * .6, 'pop'); c.cue(dur * .72, 'sparkle');
  return lt => {
    pop(kid, lt, .15, { x: 380, y: 640 + bob(lt, 4, 1.4), big: true }); kd.forEach((d, i) => { const k = (lt * .9 + i / 3) % 1; T(d, { x: 330 + i * 45, y: 480 + k * 90, o: lt > .4 ? 1 - k : 0 }); }); rise(kl, lt, .3, { x: 380, y: 820, dy: 20 });
    pop(ar, lt, dur * .35, { x: 760 + Math.sin(lt * 4) * 10, y: 560, d: .4 }); pop(box, lt, dur * .5, { x: 1300, y: 640, big: true });
    const o = E.out3(seg(lt, dur * .65, dur * .8)); T(lid, { x: o * 150, y: -o * 90, r: o * 40 }); const cs = seg(lt, dur * .68, dur * .85); pop(car, lt, dur * .68, { x: 1300, y: 560 - cs * 60, s: .75, d: .5 }); rise(nl, lt, dur * .7, { x: 1300, y: 860, dy: 20 });
    mt.__row.__words.forEach((w, i) => pop(w, lt, .1 + i * .12, { x: w.__x, y: 0, d: .4 })); sp.forEach((s, i) => { const k = seg(lt, dur * .72 + i * .03, dur * .72 + .9); const a = i / 8 * 6.28, r = 90 + 220 * E.out3(k); T(s, { x: 1300 + Math.cos(a) * r, y: 560 + Math.sin(a) * r * .6, s: Math.sin(k * Math.PI) * 1.4, o: k > 0 && k < 1 ? 1 : 0 }); });
  };
};

// ============================================================== 3.5 self-respect: how far he has come
V.pride = c => {
  const { g, S, dur } = c, tx = S.txt;
  const stairs = gnode(g); const N_ = 6; for (let i = 0; i < N_; i++) { R(stairs, 360 + i * 220, 800 - i * 100, 220, 400, i === N_ - 1 ? GOLD : `rgba(255,255,255,${.08 + i * .03})`, 6, { stroke: 'rgba(255,255,255,.25)', 'stroke-width': 2 }); }
  const man = gnode(g); mini(man, '#8CD8FF', 1.3); T(man, { x: 400, y: 640 });
  const flag = gnode(g); L(flag, 0, 0, 0, -150, '#fff', 8); P(flag, 'M 0 -150 L 100 -120 L 0 -90 Z', RED); T(flag, { x: 1560, y: 330, o: 0 });
  const crown = gnode(g); P(crown, 'M -70 40 L -70 -20 L -35 10 L 0 -40 L 35 10 L 70 -20 L 70 40 Z', GOLD); T(crown, { x: 1560, y: 170, o: 0, s: 1.3 });
  const lowl = pill(g, tx.low, { size: 40, bg: 'rgba(255,255,255,.14)', fill: '#fff' }); T(lowl, { x: 470, y: 900, o: 0 }); const highl = pill(g, tx.high, { size: 40, bg: GOLD, fill: '#1b1100' }); T(highl, { x: 1560, y: 460, o: 0 });
  const mt = fitRow(g, tx.main, { size: 130, fill: '#fff', stroke: '#000', sw: 14, maxW: 1100 }); T(mt, { x: 700, y: 250 });
  const sp = Array.from({ length: 6 }, () => { const s = gnode(g); A.sparkle(s, { r: 22, fill: '#fff' }); T(s, { o: 0 }); return s; });
  c.cue(.2, 'whoosh'); c.cue(dur * .75, 'tada', .8); c.cue(dur * .8, 'sparkle');
  return lt => {
    rise(stairs, lt, 0, { dy: 60, d: .6 }); const p = E.inOut(seg(lt, .4, dur * .8)); const i = Math.min(N_ - 1, p * (N_ - 1)); const fl = Math.floor(i), fr = i - fl;
    const x = 400 + p * (N_ - 1) * 220, y = 640 - p * (N_ - 1) * 100 - Math.abs(Math.sin(fr * Math.PI)) * 30; T(man, { x, y, r: bob(lt, 3, 3) });
    pop(lowl, lt, .5, { x: 470, y: 900, d: .4 }); pop(flag, lt, dur * .8, { x: 1560, y: 330, big: true }); pop(crown, lt, dur * .82, { x: 1560, y: 170 + bob(lt, 6, 1), s: 1.3, big: true }); pop(highl, lt, dur * .85, { x: 1560, y: 460, d: .4 });
    mt.__row.__words.forEach((w, k) => pop(w, lt, dur * .15 + k * .2, { x: w.__x, y: 0, d: .5, big: true })); sp.forEach((s, k) => { const q = seg(lt, dur * .8 + k * .04, dur * .8 + .8), a = k / 6 * 6.28; T(s, { x: 1560 + Math.cos(a) * (60 + 160 * q), y: 280 + Math.sin(a) * (60 + 100 * q), s: Math.sin(q * Math.PI) * 1.3, o: q > 0 && q < 1 ? 1 : 0 }); });
  };
};

// ============================================================== 3.6 the childhood dream car
V.childDream = c => {
  const { g, S, dur } = c, tx = S.txt;
  const stars = Array.from({ length: 22 }, (_, i) => { const r = rng(i + 3); const s = C(g, r() * 1920, r() * 560, 2 + r() * 3, '#fff'); s.__ph = r() * 6; return s; });
  const kid = gnode(g); mini(kid, '#FFB36B', 2.0); T(kid, { x: 460, y: 740 });
  const cloud = gnode(g); A.thought(cloud, { w: 900, h: 480, fill: 'rgba(255,255,255,.08)' }); cloud.querySelectorAll('ellipse,circle').forEach(n => { n.setAttribute('stroke', 'rgba(255,200,87,.55)'); n.setAttribute('stroke-width', 3); }); const dc = gnode(cloud); const cr = A.car(dc, { color: GOLD, color2: '#B07A10', beam: false }); T(dc, { x: 0, y: 10, s: 1.3 }); T(cloud, { x: 1220, y: 400, o: 0 });
  const mt = fitRow(g, tx.main, { size: 120, fill: GOLD, stroke: '#000', sw: 14, maxW: 1300 }); T(mt, { x: 1100, y: 840 });
  c.cue(.2, 'pop'); c.cue(dur * .35, 'sparkle'); c.cue(dur * .6, 'ding');
  return lt => {
    stars.forEach(s => s.setAttribute('opacity', .3 + .6 * Math.abs(Math.sin(lt * 2 + s.__ph)))); T(kid, { x: 460, y: 740 + bob(lt, 4, 1) });
    pop(cloud, lt, dur * .15, { x: 1220, y: 400 + bob(lt, 8, .5), big: true }); cr.spin(lt, 60); mt.__row.__words.forEach((w, i) => pop(w, lt, dur * .5 + i * .25, { x: w.__x, y: 0, d: .5, big: true }));
  };
};

// ============================================================== 3.7 / 3.8 balance scale: outsider vs insider
function scale(parent) {
  const g = gnode(parent), parts = g.parts = {};
  R(g, -12, -40, 24, 320, '#C9CFE8', 8); R(g, -140, 270, 280, 24, '#9AA6D6', 10); const beam = gnode(g); R(beam, -360, -12, 720, 24, GOLD, 12); C(beam, 0, 0, 22, '#fff'); parts.beam = beam; T(beam, { y: -40 });
  const mkPan = x => { const p = gnode(beam); L(p, 0, 0, -90, 150, 'rgba(255,255,255,.6)', 4); L(p, 0, 0, 90, 150, 'rgba(255,255,255,.6)', 4); P(p, 'M -110 150 L 110 150 Q 90 200 0 200 Q -90 200 -110 150 Z', '#E8ECFA'); T(p, { x, y: 0 }); return p; };
  parts.L = mkPan(-340); parts.R = mkPan(340);
  g.tilt = (deg) => { T(parts.beam, { y: -40, r: deg }); const a = deg * Math.PI / 180; T(parts.L, { x: -340, y: 0, r: -deg }); T(parts.R, { x: 340, y: 0, r: -deg }); parts.L.setAttribute('transform', `translate(${-340 * Math.cos(a)} ${-340 * Math.sin(a)}) rotate(${-deg})`); parts.R.setAttribute('transform', `translate(${340 * Math.cos(a)} ${340 * Math.sin(a)}) rotate(${-deg})`); };
  return g;
}
V.outsider = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sc = scale(g); T(sc, { x: 1100, y: 330, s: 1.0 }); sc.tilt(0);
  const out = head(g, { glasses: true, hair: 'bald', skin: 'light', mood: 'flat' }); T(out, { x: 330, y: 890, s: 1.5 });
  const wasteBox = gnode(sc.parts.L); const b1 = bill(wasteBox, 1.1); T(b1, { y: 100 }); txt(wasteBox, '🔥', { size: 80, font: 'en', y: 70, x: 40 }); T(wasteBox, { y: -10 });
  const cr = gnode(sc.parts.R); A.car(cr, { color: RED, beam: false }); T(cr, { x: 0, y: 120, s: .4 });
  const l = pill(g, tx.l, { size: 48, bg: 'rgba(255,255,255,.14)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 }); T(l, { x: 330, y: 330, o: 0 });
  const r = pill(g, tx.r, { size: 76, bg: RED, fill: '#fff' }); T(r, { x: 1100, y: 840, o: 0 });
  c.cue(.2, 'pop'); c.cue(dur * .35, 'thud'); c.cue(dur * .55, 'error');
  return lt => {
    out.idle(lt); rise(l, lt, .1, { x: 330, y: 330, dy: -20 }); pop(sc, lt, .2, { x: 1100, y: 330 + 0, s: 1.0, d: .5 }); sc.tilt(-14 * E.back(seg(lt, dur * .3, dur * .6)) + bob(lt, .8, .6)); pop(r, lt, dur * .5, { x: 1100, y: 840, big: true });
  };
};
V.insider = c => {
  const { g, S, dur } = c, tx = S.txt;
  const sc = scale(g); T(sc, { x: 1100, y: 330 }); sc.tilt(-14);
  const me = head(g, { mood: 'grin', skin: 'brown' }); T(me, { x: 330, y: 890, s: 1.5 });
  const heart = gnode(sc.parts.R); A.heart(heart, { color: GOLD }); T(heart, { x: 0, y: 110, s: .75 }); heart.appendChild(el('circle', { r: 120, fill: 'url(#gGlowGold)', opacity: .8, cy: 0 }));
  const wasteBox = gnode(sc.parts.L); const b1 = bill(wasteBox, .8); T(b1, { y: 120 });
  const l = pill(g, tx.l, { size: 48, bg: 'rgba(255,255,255,.14)', fill: '#fff', stroke: 'rgba(255,255,255,.35)', sw: 3 }); T(l, { x: 330, y: 330, o: 0 });
  const r = pill(g, tx.r, { size: 76, bg: GOLD, fill: '#1b1100' }); T(r, { x: 1100, y: 840, o: 0 });
  const sp = Array.from({ length: 8 }, (_, i) => { const s = gnode(g); A.sparkle(s, { r: 22, fill: i % 2 ? GOLD : '#fff' }); T(s, { o: 0 }); return s; });
  c.cue(.1, 'whoosh'); c.cue(dur * .35, 'thud'); c.cue(dur * .5, 'tada', .8); c.cue(dur * .55, 'sparkle'); c.flash(dur * .5, .25, '#ffe9b0', .2);
  return lt => {
    me.idle(lt, 1); rise(l, lt, .05, { x: 330, y: 330, dy: -20 }); const t = E.back(seg(lt, .2, dur * .55)); sc.tilt(lerp(-14, 16, t) + bob(lt, .7, .6)); heart.setAttribute('transform', heart.getAttribute('transform'));
    T(heart, { x: 0, y: 110, s: .75 * (1 + .08 * Math.sin(lt * 7)) }); pop(r, lt, dur * .5, { x: 1100, y: 840, big: true });
    sp.forEach((s, i) => { const k = seg(lt, dur * .5 + i * .03, dur * .5 + .9), a = i / 8 * 6.28; T(s, { x: 1440 + Math.cos(a) * (60 + 200 * k), y: 420 + Math.sin(a) * (40 + 140 * k), s: Math.sin(k * Math.PI) * 1.4, o: k > 0 && k < 1 ? 1 : 0 }); });
  };
};

// ============================================================== 4.1 stop judging others
V.stopJudge = c => {
  const { g, S, dur } = c, tx = S.txt;
  const texts = ['ఎంత ఖర్చు!', 'ఇది వృధా!', 'ఎందుకు ఇలా?'];
  const bubs = texts.map((t, i) => { const b = gnode(g); A.bubble(b, { w: 360, h: 120, fill: '#fff', tail: i % 2 ? 'br' : 'bl' }); txt(b, t, { size: 46, fill: '#12121a', y: 16 }); T(b, { o: 0 }); return b; });
  const bp = [[420, 330, -6], [1500, 300, 6], [1420, 700, -4]];
  const sign = gnode(g); const oct = P(sign, 'M -90 -218 L 90 -218 L 218 -90 L 218 90 L 90 218 L -90 218 L -218 90 L -218 -90 Z', RED, { stroke: '#fff', 'stroke-width': 14, 'stroke-linejoin': 'round' }); txt(sign, tx.stop, { size: 120, font: 'en', fill: '#fff', y: 42, weight: 700 }); T(sign, { x: 960, y: 480, o: 0 });
  const mt = fitRow(g, tx.main, { size: 96, fill: '#fff', stroke: '#000', sw: 14, maxW: 1500 }); T(mt, { x: 960, y: 900 });
  c.cue(.2, 'pop'); c.cue(.5, 'pop'); c.cue(.8, 'pop'); c.cue(dur * .45, 'stamp'); c.shake(dur * .45, 8, .3);
  return lt => {
    bubs.forEach((b, i) => { const t0 = .2 + i * .3, k = seg(lt, dur * .45, dur * .6); pop(b, lt, t0, { x: bp[i][0], y: bp[i][1] + bob(lt, 6, .6, i), r: bp[i][2], big: true }); if (k > 0) T(b, { s: 1 - k, o: 1 - k }); });
    const k = E.backBig(seg(lt, dur * .42, dur * .6)); T(sign, { x: 960, y: 480, s: Math.max(.001, k * (1 + .03 * Math.sin(lt * 6))), o: k > 0 ? 1 : 0, r: (1 - k) * -20 });
    mt.__row.__words.forEach((w, i) => pop(w, lt, dur * .5 + i * .18, { x: w.__x, y: 0, d: .5 }));
  };
};

// ============================================================== 4.2 everyone has their own journey
V.ownPaths = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = fitRow(g, tx.main, { size: 100, fill: '#fff', stroke: '#000', sw: 14, maxW: 1500 }); T(top, { x: 960, y: 150 });
  const paths = [['M 960 900 C 960 700 500 700 420 420', GREEN, tx.a, 420, 330], ['M 960 900 C 960 700 960 520 960 400', GOLD, tx.b, 960, 300], ['M 960 900 C 960 700 1420 700 1500 420', SKY, tx.c, 1500, 330]];
  const els = paths.map(([d, col, lab, x, y]) => { const base = P(g, d, 'none', { stroke: 'rgba(255,255,255,.12)', 'stroke-width': 26, 'stroke-linecap': 'round' }); const line = P(g, d, 'none', { stroke: col, 'stroke-width': 8, 'stroke-linecap': 'round' }); const dot = C(g, 0, 0, 20, col, { stroke: '#fff', 'stroke-width': 5 }); const p = pill(g, lab, { size: 48, bg: col, fill: '#06130f' }); T(p, { x, y, o: 0 }); return { line, dot, p, col }; });
  const st = gnode(g); C(st, 0, 0, 42, '#fff'); txt(st, '▶', { size: 36, fill: '#000', y: 12 }); T(st, { x: 960, y: 900 });
  c.cue(.1, 'whoosh'); c.cue(dur * .3, 'pop'); c.cue(dur * .5, 'pop'); c.cue(dur * .7, 'pop');
  return lt => {
    top.__row.__words.forEach((w, i) => pop(w, lt, .1 + i * .15, { x: w.__x, y: 0, d: .5 }));
    els.forEach((o, i) => { const k = E.inOut(seg(lt, .3 + i * .3, dur * .75 + i * .1)); draw(o.line, seg(lt, .2 + i * .25, .9 + i * .25)); const pt = pathPt(o.line, k); o.dot.setAttribute('cx', pt.x); o.dot.setAttribute('cy', pt.y); o.dot.setAttribute('opacity', lt > .3 + i * .3 ? 1 : 0); pop(o.p, lt, dur * (.3 + i * .2), { x: [420, 960, 1500][i], y: [330, 300, 330][i], big: true }); });
  };
};

// ============================================================== 4.3 not maths, emotions
V.moreThanMath = c => {
  const { g, S, dur } = c, tx = S.txt;
  const nums = ['1,25,000', '+ 8%', '× 12', '= ?', '₹ 40L', '÷ 3'].map((t, i) => { const n = gnode(g); txt(n, t, { size: 76 + (i % 3) * 14, font: 'en', fill: 'rgba(255,255,255,.75)', weight: 600 }); const r = rng(i + 20); n.__p = [200 + (i % 3) * 640 + r() * 80, 220 + Math.floor(i / 3) * 280 + r() * 40]; T(n, { x: n.__p[0], y: n.__p[1] }); return n; });
  const heart = gnode(g); A.heart(heart, { color: RED }); heart.appendChild(el('circle', { r: 240, fill: 'url(#gGlowCoral)', opacity: .7 })); T(heart, { x: 960, y: 400, s: .01, o: 0 });
  const mt = fitRow(g, tx.main, { size: 100, fill: '#fff', stroke: '#000', sw: 14, maxW: 1600 }); T(mt, { x: 960, y: 800 });
  c.cue(.2, 'pop'); c.cue(dur * .3, 'scratch'); c.cue(dur * .5, 'pop'); c.cue(dur * .5 + .1, 'ding'); c.cue(dur * .7, 'sparkle');
  return lt => {
    const f = E.in2(seg(lt, dur * .28, dur * .5)); nums.forEach((n, i) => { T(n, { x: n.__p[0], y: n.__p[1] + f * 500, r: f * (i - 2.5) * 20, o: seg(lt, i * .08, i * .08 + .4) * (1 - f) }); });
    const m = E.backBig(seg(lt, dur * .5, dur * .72)); T(heart, { x: 960, y: 400 + bob(lt, 6, .8), s: Math.max(.001, m * 2.1 * (1 + .07 * Math.sin(lt * 7))), o: m > 0 ? 1 : 0 });
    mt.__row.__words.forEach((w, i) => pop(w, lt, dur * .45 + i * .18, { x: w.__x, y: 0, d: .5, big: true }));
  };
};

// ============================================================== 4.4 comment
V.commentCta = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mk = (text, x, y, side, col) => { const n = gnode(g); const w = tw(text, 48, 600) + 100; const b = gnode(n); A.bubble(b, { w, h: 130, fill: '#fff', tail: side < 0 ? 'bl' : 'br' }); txt(b, text, { size: 48, fill: '#12121a', y: 17, weight: 600 }); const av = gnode(n); A.avatar(av, { r: 48, bg: col }); T(av, { x: side * (w / 2 + 56), y: 12 }); T(n, { x, y, o: 0 }); n.__p = [x, y]; return n; };
  const items = [mk(tx.c1, 560, 330, -1, '#6C3BE8'), mk(tx.c2, 1350, 500, 1, RED), mk(tx.c3, 640, 690, -1, '#1FA88F')];
  const typing = gnode(g); A.bubble(typing, { w: 200, h: 110, fill: '#fff', tail: 'bl' }); [-48, 0, 48].forEach(x => C(typing, x, 0, 13, '#9AA3C7')); T(typing, { x: 1460, y: 800, o: 0 });
  const pl = pill(g, tx.main, { size: 74, bg: GOLD, fill: '#1b1100' }); T(pl, { x: 960, y: 150, o: 0 });
  const t0 = [.3, dur * .22, dur * .42]; t0.forEach(t => c.cue(t, 'pop')); c.cue(dur * .65, 'tick');
  return lt => { items.forEach((n, i) => pop(n, lt, t0[i], { x: n.__p[0], y: n.__p[1] + bob(lt, 5, .5, i), big: true })); pop(typing, lt, dur * .6, { x: 1460, y: 800, big: true }); typing.querySelectorAll('circle').forEach((d, i) => d.setAttribute('cy', Math.sin(lt * 8 - i) * 9)); rise(pl, lt, .1, { x: 960, y: 150, dy: -20 }); };
};

// ============================================================== 4.5 subscribe + thank you
V.subscribeEnd = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = A.rays(g, { n: 24, fill: 'rgba(255,200,87,.07)' }); T(rays, { x: 960, y: 480 });
  C(g, 960, 480, 480, 'url(#gGlowCoral)', { opacity: .25 });
  const btn = gnode(g); const bg = R(btn, -330, -90, 660, 180, '#E5232B', 90); const lab = txt(btn, 'SUBSCRIBE', { size: 84, font: 'en', fill: '#fff', y: 30, ls: 3 }); T(btn, { x: 860, y: 440, o: 0 });
  const bell = gnode(g); const bl = A.bell(bell, {}); T(bell, { x: 1380, y: 430, s: 1.2, o: 0 });
  const cur = gnode(g); A.hand(cur, {}); T(cur, { x: 1500, y: 800, s: 1.1, o: 0 });
  const pl = pill(g, tx.main, { size: 70, bg: '#fff', fill: '#10101a' }); T(pl, { x: 960, y: 150, o: 0 });
  const th = fitRow(g, tx.thanks, { size: 110, fill: GOLD, stroke: '#000', sw: 14, maxW: 1400 }); T(th, { x: 960, y: 860 });
  const tk = dur * .38; c.cue(.1, 'pop'); c.cue(.4, 'pop'); c.cue(tk, 'click'); c.cue(tk + .15, 'ding'); c.cue(tk + .3, 'bell'); c.cue(dur * .62, 'tada', .8); c.cue(dur * .64, 'sparkle');
  return lt => {
    T(rays, { x: 960, y: 480, r: lt * 6 }); pop(btn, lt, .1, { x: 860, y: 440, big: true }); pop(bell, lt, .4, { x: 1380, y: 430, s: 1.2, big: true }); rise(pl, lt, .1, { x: 960, y: 150, dy: -20 });
    const mv = E.inOut(seg(lt, dur * .15, tk)); const px = lerp(1500, 920, mv), py = lerp(800, 500, mv), press = seg(lt, tk, tk + .1) * (1 - seg(lt, tk + .1, tk + .3));
    pop(cur, lt, dur * .15, { x: px, y: py, s: 1.1 - .12 * press, d: .3 }); if (lt > dur * .15 + .3) T(cur, { x: px, y: py, s: 1.1 - .12 * press });
    const done = lt >= tk + .05; bg.setAttribute('fill', done ? '#3b3b48' : '#E5232B'); lab.textContent = done ? 'SUBSCRIBED ✓' : 'SUBSCRIBE'; lab.setAttribute('font-size', done ? 70 : 84);
    const rg = seg(lt, tk + .25, tk + 1.6); T(bl.parts.b, { r: rg > 0 && rg < 1 ? Math.sin(rg * 24) * 22 * (1 - rg) : 0 });
    th.__row.__words.forEach((w, i) => pop(w, lt, dur * .6 + i * .2, { x: w.__x, y: 0, d: .6, big: true }));
  };
};
