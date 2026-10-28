// Scene 1 (hook) and scene 2 (the lesson) as 3D shots.
import * as THREE from 'three';
import { V, clamp, lerp, seg, E, bob, rng, FLOOR_Y } from './core3d.js';
import { P, M, person, PEOPLE, label, text3d, words3d, fitW, at, pop, rise, popWords, group, mesh, glow, halo, lightCone, setOpacity, rbox, col } from './kit3d.js';

export const pillL = (s, o = {}) => label(s, Object.assign({ h: .72, size: 110, fill: '#2a1b00', bg: '#FFC857', padX: 36 }, o));
export const FY = FLOOR_Y;
export const place = (o, x, y, z, s = 1) => at(o, x, y, z, s);

// falling coins that land and bounce on the floor
export function coinRain(g, n, seed) {
  const r = rng(seed), items = [];
  for (let i = 0; i < n; i++) { const c = P.coin(.28 + r() * .12); c.visible = false; g.add(c); items.push({ c, x: (r() - .5) * 12, z: (r() - .5) * 5 - 1, t0: r() * 1.4, sp: 1.4 + r(), rx: r() * 4, ry: r() * 5 }); }
  return lt => items.forEach(o => { const k = lt - o.t0; if (k < 0) { o.c.visible = false; return; } o.c.visible = true; const top = 6, v = Math.min(top - (FY + .3), .5 * 9 * k * k * o.sp); let y = top - v; if (y <= FY + .3) { const b = k - Math.sqrt(2 * (top - FY - .3) / (9 * o.sp)); y = FY + .3 + Math.abs(Math.sin(b * 6)) * Math.exp(-b * 2.2) * .9; } o.c.position.set(o.x, y, o.z); o.c.rotation.set(k * o.rx * (y > FY + .4 ? 1 : .0) + 1.2, k * o.ry, 0); });
}

// ============================================================ 1.1 dad + bank
V.dadBank = c => {
  const { g, S, dur } = c, tx = S.txt;
  const dad = person(Object.assign({ mood: 'smile' }, PEOPLE.dad)); place(dad, -3.9, FY, 0, 1.05); dad.rotation.y = .25; g.add(dad);
  const nm = pillL(tx.name); place(nm, -3.9, 1.65, .3); g.add(nm);
  const cA = P.glassCard(5.8, 2.9, { color: '#3DDC97', opacity: .12, edge: '#3DDC97' }); place(cA, 3.2, 1.35, -.5); g.add(cA);
  const bank = P.bank(); place(bank, 2.0, 1.3, -.3, .38); const pig = P.piggy(); place(pig, 4.3, 1.1, -.2, .42); pig.rotation.y = .6; cA.add(bank, pig);
  bank.position.set(-1.2, -.05, .3); pig.position.set(1.15, -.25, .3); bank.scale.setScalar(.38); pig.scale.setScalar(.42);
  const okp = pillL(tx.ok, { bg: '#3DDC97', fill: '#04281b', h: .62, size: 100 }); place(okp, 3.2, -0.35, .2); g.add(okp);
  const ok = P.check(.42); place(ok, 5.7, 2.55, .3); g.add(ok);
  const cB = P.glassCard(5.8, 2.9, { color: '#FF5A5F', opacity: .12, edge: '#FF5A5F' }); place(cB, 3.2, -0.95, -.5); g.add(cB);
  const chart = P.chart({ color: '#FF5A5F', w: 4.0, h: 1.5, pts: [.1, .22, .16, .42, .38, .62, .6, .9] }); chart.position.set(0, .12, .2); cB.add(chart);
  const badp = pillL(tx.bad, { bg: '#FF5A5F', fill: '#fff', h: .62, size: 100 }); place(badp, 3.2, -1.5, .2); g.add(badp);
  const xx = P.cross(.4); place(xx, 5.7, .55, .3); g.add(xx);
  const t1 = Math.min(.5, dur * .12), t2 = dur * .5;
  c.cue(t1 + .05, 'whoosh'); c.cue(t1 + .5, 'ding'); c.cue(t2, 'whoosh'); c.cue(t2 + .9, 'error');
  c.camera([{ t: 0, p: [-1.8, .9, 14.5], l: [-.6, .3, 0], f: 32 }, { t: 1, p: [.9, .6, 11.8], l: [.3, .1, 0], f: 32, r: -1 }]);
  return lt => {
    dad.idle(lt); dad.setMood(lt > t2 ? 'worry' : 'smile'); pop(dad, lt, .05, { d: .5 }); rise(nm, lt, .2, { dy: .5 });
    rise(cA, lt, t1, { dx: 1.6, dy: 0, d: .6 }); pop(ok, lt, t1 + .5, { big: true }); rise(okp, lt, t1 + .35, { dy: -.3, d: .4 });
    bank.rotation.y = bob(lt, .35, .15); pig.rotation.y = .6 + bob(lt, .2, .2); pig.userData.coin.position.y = 1.7 + bob(lt, .15, .8);
    rise(cB, lt, t2, { dx: 1.6, dy: 0, d: .6 }); chart.setProgress(E.inOut(seg(lt, t2 + .2, t2 + 1.4))); pop(xx, lt, t2 + .9, { big: true }); rise(badp, lt, t2 + .4, { dy: -.3, d: .4 });
  };
};

// ============================================================ 1.2 friend + EMI
V.friendEMI = c => {
  const { g, S, dur } = c, tx = S.txt;
  const fr = person(Object.assign({ mood: 'grin' }, PEOPLE.youth)); place(fr, 4.0, FY, 0, 1.05); fr.rotation.y = -.3; g.add(fr);
  const nm = pillL(tx.name, { bg: '#4CC9F0', fill: '#02283a' }); place(nm, 4.0, 1.65, .3); g.add(nm);
  const bags = [['#FF5A5F', '#E5384F', 2.3, .45, .3, 1.5], ['#8B5CF6', '#6C3BE8', 5.8, -.1, .6, 1.2], ['#FFC857', '#E9A02A', 5.3, -1.4, .0, .9]].map(([a, b, x, y, z, s], i) => { const bg = P.bag(a, b, ['%', '₹', '%'][i]); place(bg, x, FY + .85 * s, z, s * .8); g.add(bg); bg.rotation.y = -.4 + i * .3; return bg; });
  const cals = ['JAN', 'FEB', 'MAR'].map((m, i) => { const k = P.calendar('EMI', '₹ ' + m); place(k, -5.0 + i * 2.5, .4, -.5 - i * .3, .95); g.add(k); k.rotation.y = .35; return k; });
  const lab = pillL(tx.chip, { h: .9, size: 130 }); place(lab, -2.4, -1.3, .5); g.add(lab);
  const rain = coinRain(g, 9, 11);
  const t0 = [dur * .36, dur * .52, dur * .68]; cals.forEach((n, i) => c.cue(t0[i], 'pop')); c.cue(.2, 'whoosh'); c.cue(dur * .8, 'coins');
  c.camera([{ t: 0, p: [2.8, 1.2, 13.5], l: [.4, .1, 0], f: 32 }, { t: 1, p: [-.8, .5, 11.4], l: [-.3, .1, 0], f: 32, r: 1.2 }]);
  return lt => {
    fr.idle(lt, 1); pop(fr, lt, .05, { d: .5 }); rise(nm, lt, .2, { dy: .5 });
    bags.forEach((b, i) => { pop(b, lt, .3 + i * .18, { big: true }); b.position.y = (b.userData.base.y) + bob(lt, .06, .5, i); });
    cals.forEach((k, i) => { pop(k, lt, t0[i], { big: true }); k.rotation.y = .35 - E.out3(seg(lt, t0[i], t0[i] + .8)) * .35 + bob(lt, .05, .3, i); k.position.y = .4 + bob(lt, .08, .45, i); });
    rise(lab, lt, dur * .35, { dy: -.4, d: .5 }); if (lt > dur * .6) rain(lt - dur * .6); else rain(-1);
  };
};

// ============================================================ 1.3 are both wrong?
V.bothQuestion = c => {
  const { g, S, dur } = c, tx = S.txt;
  const dad = person(Object.assign({ mood: 'flat' }, PEOPLE.dad)); place(dad, -4.2, FY, 0, 1.0); dad.rotation.y = .5; g.add(dad);
  const fr = person(Object.assign({ mood: 'grin' }, PEOPLE.youth)); place(fr, 4.2, FY, 0, 1.0); fr.rotation.y = -.5; g.add(fr);
  const big = text3d(tx.big, { h: 1.7, size: 160, fill: '#FFD66B', outline: '#2a1450', depth: '#a86a08' }); fitW(big, 8.2); place(big, 0, .9, 0); g.add(big);
  const qs = [[-4.9, 2.1], [-3.5, 2.6], [3.5, 2.6], [4.9, 2.1]].map(([x, y], i) => { const q = text3d('?', { h: 1.1, size: 160, font: 'en', fill: i % 2 ? '#4CC9F0' : '#FFC857', outline: '#2a1450', depth: i % 2 ? '#1a6a88' : '#a86a08' }); place(q, x, y, .4); g.add(q); return q; });
  const wr = pillL(tx.wrong, { bg: '#FF5A5F', fill: '#fff', h: .9, size: 130 }); place(wr, 0, -0.9, .6); g.add(wr);
  c.cue(.15, 'pop'); c.cue(.45, 'pop'); c.cue(.75, 'pop'); c.cue(dur * .42, 'whoosh'); c.cue(dur * .75, 'error');
  c.camera([{ t: 0, p: [0, 1.4, 16.5], l: [0, .5, 0], f: 34, r: 1.5 }, { t: 1, p: [0, .5, 11.8], l: [0, .6, 0], f: 31, r: -1 }]);
  return lt => {
    dad.idle(lt); fr.idle(lt, 1.3); pop(dad, lt, 0, { d: .5 }); pop(fr, lt, .1, { d: .5 });
    qs.forEach((q, i) => { pop(q, lt, .15 + i * .3, { big: true }); q.position.y = q.userData.base.y + bob(lt, .12, .7, i); q.rotation.z = bob(lt, .12, .8, i); });
    const s0 = dur * .4; pop(big, lt, s0, { big: true, d: .6, s: big.scale.x }); if (lt > s0 && lt < s0 + .5) big.position.x = Math.sin(lt * 50) * .06; else big.position.x = 0;
    pop(wr, lt, dur * .72, { big: true });
  };
};

// ============================================================ 1.4 one truth ...
V.truth = c => {
  const { g, S, dur } = c, tx = S.txt;
  const cone = lightCone('#ffe1a8', 12, 4.2, .07); place(cone, 0, 3.4, -.8); g.add(cone);
  const hl = halo('#FFC857', 12, .45); place(hl, 0, .5, -1.2); g.add(hl);
  const t = words3d(tx.main, { h: 2.1, size: 170, fill: '#ffffff', outline: '#2a1450', depth: '#6a5a9a', layers: 11, step: .02 }); fitW(t, 9.5); place(t, 0, .6, 0); g.add(t);
  const dots = [0, 1, 2].map(i => { const d = mesh(new THREE.SphereGeometry(.16, 16, 12), glow('#FFC857', 1.5)); place(d, -.5 + i * .5, -1.2, .3); g.add(d); return d; });
  const sp = Array.from({ length: 10 }, (_, i) => { const s = P.spark(.22, i % 2 ? '#FFE08A' : '#ffffff'); s.userData.a = i / 10 * 6.28; g.add(s); return s; });
  c.cue(.05, 'riser', .9); c.cue(dur * .55, 'impact'); c.flash(dur * .55, .35, '#fff', .5);
  c.camera([{ t: 0, p: [0, -.6, 14], l: [0, .8, 0], f: 36 }, { t: .55, p: [0, .3, 11], l: [0, .6, 0], f: 32 }, { t: 1, p: [0, .5, 9.6], l: [0, .6, 0], f: 29 }]);
  return lt => {
    popWords(t, lt, .1, .3, .6); t.rotation.y = bob(lt, .06, .2); hl.material.opacity = .25 + .35 * seg(lt, 0, dur * .55);
    dots.forEach((d, i) => { pop(d, lt, dur * .5 + i * .12, { big: true }); });
    sp.forEach(s => { const p = seg(lt, dur * .55, dur * .55 + .9), r = 1.5 + 5 * E.out3(p); s.position.set(Math.cos(s.userData.a) * r, .6 + Math.sin(s.userData.a) * r * .55, .4); s.scale.setScalar(Math.sin(p * Math.PI) * 1.4 + .001); s.visible = p > 0 && p < 1; });
  };
};

// ============================================================ 1.5 title
V.titleReveal = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = new THREE.Group(); for (let i = 0; i < 14; i++) { const m = lightCone('#ffd9a0', 22, 1.1, .08); m.rotation.z = Math.PI / 2; m.position.set(0, 0, 0); const pv = new THREE.Group(); pv.rotation.z = i / 14 * 6.28; pv.add(m); m.position.x = 11; rays.add(pv); } place(rays, 0, .5, -4); g.add(rays);
  const hl = halo('#FFD66B', 16, .5); place(hl, 0, .5, -2); g.add(hl);
  const l1 = words3d(tx.l1, { h: 1.0, size: 150, fill: '#fff', outline: '#1d0f4a', depth: '#5a4a9a', layers: 8 }); fitW(l1, 8.6); place(l1, 0, 2.3, 0); g.add(l1);
  const l2 = words3d(tx.l2, { h: 1.7, size: 150, fill: '#FFD66B', outline: '#2a1450', depth: '#a86a08', layers: 12, step: .02 }); fitW(l2, 11); place(l2, 0, .55, 0); g.add(l2);
  const l3 = words3d(tx.l3, { h: 2.4, size: 170, fill: '#FF5A6E', outline: '#ffffff', depth: '#8a1230', layers: 14, step: .024 }); fitW(l3, 6); place(l3, 0, -1.3, 0); g.add(l3);
  const rain = coinRain(g, 18, 5);
  c.cue(0, 'impact'); c.flash(0, .3, '#fff', .6); c.cue(.9, 'sparkle'); c.cue(1.7, 'tada'); c.cue(.4, 'coins');
  c.camera([{ t: 0, p: [-2.5, -1.2, 13], l: [0, .3, 0], f: 36, r: -2 }, { t: 1, p: [2.2, 1.0, 11.4], l: [0, .2, 0], f: 30, r: 1 }]);
  return lt => {
    rays.rotation.z = lt * .12; hl.material.opacity = .4 + .15 * Math.sin(lt * 4);
    popWords(l1, lt, .15, .2, .5); popWords(l2, lt, .55, .25, .6); popWords(l3, lt, 1.3, .25, .7);
    const k = 1 + .03 * Math.sin(lt * 3.2); l3.scale.setScalar(Math.min(1, 6 / l3.userData.w) * k); rain(Math.max(0, lt - .3));
  };
};

// ============================================================ 2.1 the lesson (idea)
V.lessonBulb = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = new THREE.Group(); for (let i = 0; i < 12; i++) { const m = lightCone('#fff1c0', 18, .9, .07); const pv = new THREE.Group(); pv.rotation.z = i / 12 * 6.28; m.rotation.z = Math.PI / 2; m.position.x = 9; pv.add(m); rays.add(pv); } place(rays, 0, .6, -3); g.add(rays);
  const b = P.bulb(); place(b, 0, .1, 0, 1.3); g.add(b);
  const ring = new THREE.Group(); g.add(ring); const mk = [P.coin(.5), P.heart('#FF4D6D'), P.gear(.4, 9, '#9AA6D6'), P.star(.5, 5, .45, '#FFC857'), P.wallet('#8B5CF6')];
  mk.forEach((o, i) => { o.scale.setScalar(i === 4 ? .5 : i === 1 ? .55 : 1); o.userData.a = i / 5 * 6.28; ring.add(o); });
  const pl = pillL(tx.pill, { h: .85, size: 130 }); place(pl, 0, 2.7, .4); g.add(pl);
  const sb = pillL(tx.sub, { bg: 'rgba(255,255,255,.16)', fill: '#fff', h: .66, size: 100, bgStroke: 'rgba(255,255,255,.4)' }); place(sb, 0, -1.3, .6); g.add(sb);
  c.cue(.2, 'pop'); c.cue(dur * .35, 'switch'); c.cue(dur * .35 + .1, 'ding'); c.cue(dur * .6, 'sparkle');
  c.camera([{ t: 0, p: [-3.2, 1.1, 12.5], l: [0, .5, 0], f: 33 }, { t: 1, p: [3.0, .6, 11.2], l: [0, .5, 0], f: 31 }]);
  return lt => {
    rays.rotation.z = lt * .15; b.setOn(E.out3(seg(lt, dur * .3, dur * .3 + .4))); rays.visible = lt > dur * .3; b.rotation.y = bob(lt, .25, .15);
    pop(b, lt, .05, { d: .6, big: true }); ring.position.set(0, .5, 0);
    mk.forEach((o, i) => { const a = o.userData.a + lt * .7, r = 3.5 * E.out3(seg(lt, dur * .35 + i * .06, dur * .35 + .7 + i * .06)); o.position.set(Math.cos(a) * r, Math.sin(a) * r * .55, Math.sin(a) * 1.2); o.rotation.y = lt * 1.1; o.visible = r > .05; });
    rise(pl, lt, .15, { dy: .5 }); rise(sb, lt, dur * .45, { dy: -.4 });
  };
};

// ============================================================ 2.2 the lesson title
V.lessonTitle = c => {
  const { g, S, dur } = c, tx = S.txt;
  const plaque = P.glassCard(11.2, 3.3, { color: '#c9a8ff', opacity: .14, edge: '#FFD66B', edgeOp: .7 }); place(plaque, 0, .6, -.3); g.add(plaque);
  const cone = lightCone('#ffe1a8', 12, 3.0, .12); place(cone, -3, 4, -.5); cone.rotation.z = -.25; g.add(cone);
  const t = words3d(tx.l1, { h: 1.55, size: 150, fill: '#FFD66B', outline: '#2a1450', depth: '#a86a08', layers: 11, step: .02 }); fitW(t, 10.2); place(t, 0, .6, .1); g.add(t);
  const tag = pillL(tx.tag, { bg: '#fff', fill: '#1d0f4a', h: .75, size: 110 }); place(tag, 0, 2.7, .5); g.add(tag);
  const sw = mesh(new THREE.PlaneGeometry(1.4, 4), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .25, blending: THREE.AdditiveBlending, depthWrite: false })); sw.rotation.z = .5; place(sw, -6, .6, .3); g.add(sw);
  c.cue(.1, 'whoosh'); c.cue(.6, 'ding'); c.cue(dur * .75, 'sparkle');
  c.camera([{ t: 0, p: [-3.5, .2, 13], l: [0, .6, 0], f: 32, r: -1.5 }, { t: 1, p: [3.2, 1.1, 11.8], l: [0, .6, 0], f: 31, r: 1 }]);
  return lt => {
    pop(plaque, lt, .05, { d: .6, big: true }); popWords(t, lt, .45, .3, .6); rise(tag, lt, .25, { dy: .5 });
    sw.position.x = lerp(-6.5, 6.5, E.inOut(seg(lt, dur * .55, dur * .95))); sw.visible = lt > dur * .55;
  };
};

// ============================================================ 2.3 every decision has a reason
const TRIO = [[PEOPLE.dad, -4.0, 'flat'], [PEOPLE.youth, 0, 'grin'], [PEOPLE.girl, 4.0, 'smile']];
V.reasonOrbs = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125, bg: '#FFC857' }); place(top, 0, 2.6, .5); g.add(top);
  const ppl = TRIO.map(([o, x, m], i) => { const p = person(Object.assign({ mood: m }, o)); place(p, x, FY, 0, .95); p.rotation.y = (i - 1) * -.25; g.add(p); return p; });
  const colors = ['#4CC9F0', '#FF5A5F', '#3DDC97'], orbs = TRIO.map(([o, x], i) => { const grp = new THREE.Group(); const s = mesh(new THREE.SphereGeometry(.55, 32, 24), new THREE.MeshPhysicalMaterial({ color: col(colors[i]), emissive: col(colors[i]), emissiveIntensity: 1.1, roughness: .1, clearcoat: 1, transparent: true, opacity: .92 })); grp.add(s); grp.add(halo(colors[i], 3.4, .6)); const k = label(['కారణం', 'కారణం', 'కారణం'][i], { h: .46, size: 100, fill: '#fff', font: 'te', gain: 1.4 }); k.position.set(0, -.95, 0); grp.add(k); place(grp, x, 1.55, .3); g.add(grp); return grp; });
  const t0 = [.35, dur * .35, dur * .62]; t0.forEach(t => { c.cue(t, 'pop'); c.cue(t + .3, 'ding', .6); });
  c.camera([{ t: 0, p: [-6, .6, 11], l: [-2, .4, 0], f: 33 }, { t: 1, p: [5.5, .8, 11], l: [2, .4, 0], f: 33 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 });
    ppl.forEach((p, i) => { p.idle(lt, i); pop(p, lt, i * .12, { d: .5 }); });
    orbs.forEach((o, i) => { pop(o, lt, t0[i], { big: true }); o.position.y = 1.55 + bob(lt, .12, .6, i); });
  };
};

// ============================================================ 2.4 we just can't see it
V.hiddenReason = c => {
  const { g, S, dur } = c, tx = S.txt;
  const ppl = TRIO.map(([o, x, m], i) => { const p = person(Object.assign({ mood: m }, o)); place(p, x, FY, 0, .95); p.rotation.y = (i - 1) * -.25; g.add(p); return p; });
  const colors = ['#4CC9F0', '#FF5A5F', '#3DDC97'];
  const orbs = TRIO.map(([o, x], i) => { const grp = new THREE.Group(); grp.add(mesh(new THREE.SphereGeometry(.55, 24, 18), new THREE.MeshPhysicalMaterial({ color: col(colors[i]), emissive: col(colors[i]), emissiveIntensity: 1.1 }))); grp.add(halo(colors[i], 3, .5)); place(grp, x, 1.55, .3); g.add(grp); return grp; });
  const clouds = TRIO.map(([o, x], i) => { const cl = P.cloud('#B9C0E8'); place(cl, x, 1.55, 1.1, .85); g.add(cl); return cl; });
  const mg = P.magnifier(.9); place(mg, -4, 1.0, 1.6, 1); g.add(mg);
  const t = pillL(tx.main, { bg: '#fff', fill: '#1d0f4a', h: .95, size: 135 }); place(t, 0, 2.6, .6); g.add(t);
  const eyeN = P.eye(); place(eyeN, 0, -1.1, 1.0, .7); g.add(eyeN); const xx = P.cross(.45); place(xx, 1.1, -0.75, 1.3); g.add(xx);
  c.cue(.2, 'whoosh'); c.cue(dur * .3, 'pop'); c.cue(dur * .6, 'error');
  c.camera([{ t: 0, p: [0, .8, 12.5], l: [0, .6, 0], f: 33 }, { t: 1, p: [0, .8, 10.5], l: [0, .8, 0], f: 30, r: 1 }]);
  return lt => {
    ppl.forEach((p, i) => { p.idle(lt, i); });
    clouds.forEach((cl, i) => { const k = E.out3(seg(lt, .05 + i * .1, .6 + i * .1)); cl.scale.setScalar(Math.max(.001, .85 * k)); cl.position.y = 1.55 + bob(lt, .1, .4, i); });
    const sweep = E.inOut(seg(lt, dur * .1, dur * .8)); mg.position.set(lerp(-4.5, 4.5, sweep), 1.2 + bob(lt, .15, .8), 1.6); mg.rotation.z = bob(lt, .15, .6);
    rise(t, lt, .1, { dy: .5 }); pop(eyeN, lt, dur * .45, { big: true, s: .7 }); pop(xx, lt, dur * .6, { big: true });
  };
};

// ============================================================ 2.5 your thinking changes
V.mindsetShift = c => {
  const { g, S, dur } = c, tx = S.txt;
  const pl = pillL(tx.pill, { h: .85, size: 125 }); place(pl, 0, 2.65, .6); g.add(pl);
  const me = person(Object.assign({ mood: 'think' }, PEOPLE.me)); place(me, 0, FY, 0, .95); g.add(me);
  const th = P.thought(3.4, 1.9); place(th, 0, 2.0, .2, .75); g.add(th); const bulb = P.bulb(); bulb.scale.setScalar(.5); bulb.position.set(0, .0, .4); th.add(bulb);
  const mkCard = (x, c1, a, b, edge, fill) => { const cd = P.glassCard(3.7, 2.2, { color: fill, opacity: .13, edge, edgeOp: .7 }); const t1 = label(a, { h: .45, size: 100, fill: edge, gain: 1.2 }); t1.position.set(0, .5, .12); const t2 = label(b, { h: .62, size: 120, fill: '#fff', gain: 1.2 }); t2.position.set(0, -.2, .12); cd.add(t1, t2); place(cd, x, .5, -.2); g.add(cd); return cd; };
  const L1 = mkCard(-4.7, 0, tx.before1, tx.before2, '#FFB3B6', '#FF5A5F'), R1 = mkCard(4.7, 0, tx.after1, tx.after2, '#8CF0C4', '#3DDC97');
  c.cue(.2, 'pop'); c.cue(dur * .5, 'switch'); c.cue(dur * .5 + .1, 'ding', .8);
  c.camera([{ t: 0, p: [0, -.8, 14], l: [0, .8, 0], f: 34 }, { t: 1, p: [0, 1.6, 11], l: [0, .9, 0], f: 31, r: -1 }]);
  return lt => {
    me.idle(lt); me.setMood(lt > dur * .5 ? 'grin' : 'think'); rise(pl, lt, .05, { dy: .5 });
    pop(th, lt, .3, { d: .6 }); bulb.setOn(E.out3(seg(lt, dur * .5, dur * .5 + .35)));
    pop(L1, lt, .4, { d: .5 }); pop(R1, lt, dur * .45, { big: true }); R1.position.y = .5 + bob(lt, .08, .5);
  };
};
