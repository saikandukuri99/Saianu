// Scenes 6-9 as 3D shots: it's not about intelligence, it applies to you, three actions, outro.
import * as THREE from 'three';
import { V, clamp, lerp, seg, E, bob, rng, FLOOR_Y } from './core3d.js';
import { P, M, person, PEOPLE, label, text3d, words3d, fitW, at, pop, rise, popWords, group, mesh, glow, halo, lightCone, rbox, col, glowTex } from './kit3d.js';
import { pillL, place, FY, coinRain } from './v3d_1.js';

const burst = (n, color, r = 1) => { const gr = new THREE.Group(); for (let i = 0; i < n; i++) { const s = P.spark(.2, color); s.userData.a = i / n * 6.28; s.userData.k = .6 + (i % 3) * .25; gr.add(s); } gr.userData.r = r; return gr; };
const runBurst = (gr, p, cx = 0, cy = 0) => gr.children.forEach(s => { const r = (1 + 4.5 * E.out3(p)) * gr.userData.r * s.userData.k; s.position.set(cx + Math.cos(s.userData.a) * r, cy + Math.sin(s.userData.a) * r * .6, .4); s.scale.setScalar(Math.max(.001, Math.sin(clamp(p) * Math.PI) * 1.5)); s.visible = p > 0 && p < 1; });
const rayFan = (n, color, op = .08, len = 22) => { const rays = new THREE.Group(); for (let i = 0; i < n; i++) { const m = lightCone(color, len, .9, op); const pv = new THREE.Group(); pv.rotation.z = i / n * 6.28; m.rotation.z = Math.PI / 2; m.position.x = len / 2; pv.add(m); rays.add(pv); } return rays; };

// ============================================================ 6.1 notice
V.notice = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = rayFan(16, '#ffe9b0', .09); place(rays, 0, .6, -3); g.add(rays);
  const mg = P.magnifier(1.5); place(mg, -2.3, .7, .6); g.add(mg);
  const st = P.star(1.5, 12, .78, '#FF5A5F'); place(st, 3.0, 1.0, .3); g.add(st); const ex = label('!', { h: 2.0, size: 220, fill: '#fff', font: 'en', gain: 1.2 }); ex.position.z = .35; st.add(ex);
  const t = pillL(tx.main, { h: 1.3, size: 165, padX: 60 }); place(t, 0, -1.4, .8); g.add(t);
  c.cue(.05, 'whoosh'); c.cue(.25, 'ping'); c.cue(.4, 'pop');
  c.camera([{ t: 0, p: [0, .2, 15], l: [0, .3, 0], f: 36 }, { t: 1, p: [0, .5, 10.5], l: [0, .3, 0], f: 30, r: 2 }]);
  return lt => {
    rays.rotation.z = lt * .25; pop(mg, lt, .05, { big: true }); mg.position.x = -2.3 + Math.sin(lt * 3) * 1.1; mg.position.y = .7 + Math.cos(lt * 3.4) * .45;
    pop(st, lt, .25, { big: true }); st.rotation.z = lt * .6; ex.rotation.z = -lt * .6; pop(t, lt, .3, { big: true });
  };
};

// ============================================================ 6.2 not smart vs not smart
V.notSmart = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mk = (x, on, l, bg, fg) => { const gr = new THREE.Group(); gr.add(P.glassCard(4.6, 4.2, { color: on ? '#FFD66B' : '#ffffff', opacity: .12, edge: on ? '#FFD66B' : '#ffffff', edgeOp: .6 })); const b = P.bulb(); b.scale.setScalar(1.0); b.position.set(0, .3, .3); b.setOn(on ? 1 : 0); gr.add(b); const p = pillL(l, { bg, fill: fg, h: .7, size: 105 }); p.position.set(0, -1.6, .5); gr.add(p); place(gr, x, .3, 0); g.add(gr); gr.userData.b = b; return gr; };
  const a = mk(-3.4, true, tx.a, '#FFC857', '#2a1b00'), b = mk(3.4, false, tx.b, '#5B6591', '#fff');
  const slash = mesh(new THREE.BoxGeometry(14, .45, .3), M('#FF3B4E', { rough: .25 })); place(slash, 0, .3, 1.0); slash.rotation.z = -.38; g.add(slash);
  const no = P.cross(.8); place(no, 0, .3, 1.4); g.add(no);
  const nt = pillL(tx.no, { bg: '#FF5A5F', fill: '#fff', h: .85, size: 125 }); place(nt, 0, 2.7, .6); g.add(nt);
  c.cue(.1, 'pop'); c.cue(dur * .3, 'pop'); c.cue(dur * .6, 'stamp'); c.shake(dur * .6, .12, .3);
  c.camera([{ t: 0, p: [0, 1, 14.5], l: [0, .3, 0], f: 33, r: 1.5 }, { t: 1, p: [0, .5, 11.5], l: [0, .3, 0], f: 31, r: -1 }]);
  return lt => {
    pop(a, lt, .1, { big: true }); pop(b, lt, dur * .3, { big: true }); a.userData.b.rotation.y = bob(lt, .25, .3);
    const k = E.out3(seg(lt, dur * .6, dur * .6 + .3)); slash.visible = k > 0; slash.scale.x = Math.max(.001, k); pop(no, lt, dur * .6 + .2, { big: true }); rise(nt, lt, dur * .55, { dy: .5 });
  };
};

// ============================================================ 6.3 different info / experience
V.differentData = c => {
  const { g, S, dur } = c, tx = S.txt;
  const L_ = new THREE.Group(), R_ = new THREE.Group(); place(L_, -3.7, .2, 0); place(R_, 3.7, .2, 0); g.add(L_, R_);
  L_.add(P.glassCard(5.4, 4.4, { color: '#4CC9F0', opacity: .12, edge: '#4CC9F0', edgeOp: .7 })); R_.add(P.glassCard(5.4, 4.4, { color: '#FF8A3D', opacity: .12, edge: '#FF8A3D', edgeOp: .7 }));
  const docs = P.docs(); docs.scale.setScalar(1.15); docs.position.set(0, .4, .3); L_.add(docs);
  const pols = [['🌧️', '#7FA8FF'], ['🏦', '#FFD66B'], ['👨‍👩‍👧', '#FF9AA2']].map(([e, bg], i) => { const p = P.polaroid(e, bg); p.scale.setScalar(.82); p.position.set(-1.35 + i * 1.35, .5 - (i % 2) * .3, .3 + i * .1); p.rotation.z = -.15 + i * .15; R_.add(p); return p; });
  const lp = pillL(tx.l, { bg: '#4CC9F0', fill: '#02283a', h: .7, size: 105 }); lp.position.set(0, -1.65, .5); L_.add(lp); const rp = pillL(tx.r, { bg: '#FF8A3D', fill: '#2a1200', h: .7, size: 105 }); rp.position.set(0, -1.65, .5); R_.add(rp);
  const ne = group(mesh(new THREE.CylinderGeometry(.7, .7, .3, 40), M('#FFC857', { metal: .4 })), label('≠', { h: 1.0, size: 190, fill: '#2a1b00', font: 'en', gain: 1 })); ne.children[0].rotation.x = Math.PI / 2; ne.children[1].position.z = .17; place(ne, 0, .4, 1); g.add(ne);
  c.cue(.1, 'whoosh'); c.cue(dur * .45, 'whoosh'); pols.forEach((p, i) => c.cue(dur * .5 + i * .15, 'pop', .6)); c.cue(dur * .8, 'ding');
  c.camera([{ t: 0, p: [-3, .9, 13.5], l: [-1.5, .2, 0], f: 33 }, { t: 1, p: [3, .9, 13], l: [1.5, .2, 0], f: 33 }]);
  return lt => {
    rise(L_, lt, .05, { dx: -2, dy: 0 }); rise(R_, lt, dur * .42, { dx: 2, dy: 0 }); docs.rotation.y = bob(lt, .2, .25); pols.forEach((p, i) => pop(p, lt, dur * .5 + i * .15, { big: true })); pop(ne, lt, dur * .78, { big: true });
  };
};

// ============================================================ 6.4 that's all
V.thatsAll = c => {
  const { g, S, dur } = c, tx = S.txt;
  const hl = halo('#FFC857', 14, .5); place(hl, 0, .5, -1); g.add(hl);
  const t = words3d(tx.main, { h: 3.0, size: 220, fill: '#ffffff', outline: '#1d0f4a', depth: '#6a5a9a', layers: 14, step: .03 }); fitW(t, 9); place(t, 0, .3, 0); g.add(t);
  c.cue(.05, 'thud'); c.shake(.05, .2, .3);
  c.camera([{ t: 0, p: [0, 0, 6.5], l: [0, .3, 0], f: 30 }, { t: 1, p: [0, .2, 10.5], l: [0, .3, 0], f: 30 }]);
  return lt => { popWords(t, lt, .02, .1, .4); t.rotation.y = bob(lt, .15, .3); };
};

// ============================================================ 6.5 puzzle
V.puzzle = c => {
  const { g, S, dur } = c, tx = S.txt;
  const hl = halo('#FFD66B', 14, .35); place(hl, 0, .5, -1); g.add(hl);
  const a = P.puzzle('#FF8A3D', [0, 1, 0, 0], 1.25), b = P.puzzle('#4C8DFF', [0, 0, 0, -1], 1.25); place(a, -6, .6, 0); place(b, 6, .6, 0); g.add(a, b);
  const gl = P.globe(1.2); place(gl, 0, .6, -.8); g.add(gl);
  const la = pillL(tx.l, { bg: '#FF8A3D', fill: '#2a1200', h: .66, size: 100 }); place(la, -3.3, 2.5, .5); g.add(la); const lb = pillL(tx.r, { bg: '#4C8DFF', fill: '#fff', h: .66, size: 100 }); place(lb, 3.3, 2.5, .5); g.add(lb);
  const fin = pillL(tx.fin, { bg: '#3DDC97', fill: '#04281b', h: .9, size: 130 }); place(fin, 0, -1.3, .6); g.add(fin);
  const bs = burst(12, '#FFE08A', 1);
  g.add(bs); const tA = .05, tB = dur * .38, tS = dur * .7;
  c.cue(tA, 'whoosh'); c.cue(tB, 'whoosh'); c.cue(tS, 'snap'); c.cue(tS + .1, 'ding'); c.cue(tS + .25, 'sparkle', .7); c.flash(tS, .25, '#fff', .3);
  c.camera([{ t: 0, p: [0, 1.2, 13.5], l: [0, .5, 0], f: 33 }, { t: .7, p: [0, .5, 12], l: [0, .5, 0], f: 33 }, { t: 1, p: [0, .6, 8.6], l: [0, .6, 0], f: 30, r: 1 }]);
  return lt => {
    const sa = E.out3(seg(lt, tA, tA + .7)), sb = E.out3(seg(lt, tB, tB + .7)), sn = E.back(seg(lt, tS - .05, tS + .3));
    a.visible = sa > 0; b.visible = sb > 0; a.position.x = lt >= tS ? lerp(-3.0, -1.12, sn) : lerp(-7, -3.0, sa); b.position.x = lt >= tS ? lerp(3.0, 1.12, sn) : lerp(7, 3.0, sb);
    a.rotation.z = lt >= tS ? 0 : (1 - sa) * -.6 + bob(lt, .05, .5); b.rotation.z = lt >= tS ? 0 : (1 - sb) * .6 + bob(lt, .05, .5, 1); a.position.y = b.position.y = .6 + bob(lt, .1, .5);
    const gg = seg(lt, tS, tS + .6); gl.visible = gg > 0; gl.scale.setScalar(Math.max(.001, gg * 1.35)); gl.spin(lt); a.position.z = b.position.z = lt >= tS ? .9 : 0;
    pop(la, lt, tA + .3, { d: .4 }); pop(lb, lt, tB + .3, { d: .4 }); la.visible = lb.visible = lt < tS; rise(fin, lt, tS + .3, { dy: -.4 }); runBurst(bs, seg(lt, tS, tS + .9), 0, .6);
  };
};

// ============================================================ 7.1 important
V.important = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = rayFan(22, '#ffcf70', .1); place(rays, 0, .6, -3); g.add(rays);
  const st = P.star(2.3, 14, .8, '#FFC857'); place(st, 0, .7, 0); g.add(st); const ex = label('!', { h: 3.0, size: 260, fill: '#B8730A', font: 'en', gain: 1 }); ex.position.z = .4; st.add(ex);
  const t = pillL(tx.main, { bg: '#fff', fill: '#1d0f4a', h: 1.05, size: 140, padX: 54 }); place(t, 0, -1.3, .8); g.add(t);
  c.cue(.05, 'impact', .8); c.cue(.4, 'ping');
  c.camera([{ t: 0, p: [0, -.5, 15], l: [0, .5, 0], f: 36 }, { t: 1, p: [0, .6, 10.8], l: [0, .5, 0], f: 31 }]);
  return lt => { rays.rotation.z = lt * .3; pop(st, lt, .05, { big: true, d: .6 }); st.rotation.z = lt * .35; ex.rotation.z = -lt * .35; ex.position.y = bob(lt, .1, 1.2); pop(t, lt, .35, { big: true }); };
};

// ============================================================ 7.2 applies to you
V.appliesYou = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = person(Object.assign({ mood: 'grin' }, PEOPLE.me, { shirt: '#FFC857' })); place(me, 0, FY, 0, 1.05); g.add(me);
  const rings = [0, 1, 2].map(() => { const r = mesh(new THREE.TorusGeometry(1, .05, 12, 64), glow('#4CC9F0', 1.5), { shadow: false }); r.rotation.x = Math.PI / 2; r.position.set(0, FY + .05, 0); g.add(r); return r; });
  const you = text3d(tx.you, { h: 1.7, size: 200, font: 'en', fill: '#FFC857', outline: '#2a1450', depth: '#a86a08', layers: 12, step: .024 }); place(you, 0, 2.2, .5); g.add(you);
  const hand = P.hand(); place(hand, 3.4, .6, .8, 1.5); g.add(hand);
  const pt = pillL(tx.main, { bg: '#4CC9F0', fill: '#02283a', h: .85, size: 125 }); place(pt, 0, -1.3, .8); g.add(pt);
  c.cue(.1, 'whoosh'); c.cue(.4, 'pop'); c.cue(dur * .45, 'ding');
  c.camera([{ t: 0, p: [-3, .2, 12], l: [0, .8, 0], f: 33 }, { t: 1, p: [2.5, .8, 10.2], l: [0, .8, 0], f: 31 }]);
  return lt => {
    me.idle(lt); pop(me, lt, 0, { d: .5 }); rings.forEach((r, i) => { const k = ((lt * .55 + i / 3) % 1); r.scale.setScalar(.8 + k * 6); r.material.color.setRGB(.3 * (1 - k) * 2, .79 * (1 - k) * 2, .94 * (1 - k) * 2); });
    popWords({ userData: { items: [you] } }, lt, .3, .1, .5); you.position.y = 2.2 + bob(lt, .08, .6); pop(hand, lt, .6, { big: true }); hand.position.x = 3.4 - Math.abs(bob(lt, .35, .9)); hand.rotation.z = Math.PI / 2 * -1 + 0; rise(pt, lt, dur * .35, { dy: -.4 });
  };
};

// ============================================================ 7.3 habits <- memories
V.habitsMemories = c => {
  const { g, S, dur } = c, tx = S.txt;
  const hl = pillL(tx.hl, { h: .7, size: 105 }); place(hl, -3.9, 2.7, .5); g.add(hl); const hr = pillL(tx.hr, { bg: '#fff', fill: '#1d0f4a', h: .7, size: 105 }); place(hr, 3.9, 2.7, .5); g.add(hr);
  const ys = [1.35, -.3, -1.95 + .35], t0 = [.1, dur * .33, dur * .62];
  const ho = [P.piggy(), P.bag('#FF5A5F', '#E5384F', '%'), P.wallet()], hs = [.55, .6, .8], hlabels = [tx.h1, tx.h2, tx.h3], mems = [['🌧️', '#7FA8FF', tx.m1], ['💸', '#FFD66B', tx.m2], ['🏫', '#FF9AA2', tx.m3]];
  const rows = ys.map((y, i) => { const L_ = new THREE.Group(); L_.add(P.glassCard(5.6, 1.5, { color: '#FFC857', opacity: .1, edge: '#FFC857', edgeOp: .6 })); const o = ho[i]; o.scale.setScalar(hs[i]); o.position.set(-1.8, 0, .3); L_.add(o); const t = label(hlabels[i], { h: .5, size: 100, fill: '#fff', gain: 1.2 }); t.position.set(1.0, 0, .2); L_.add(t); place(L_, -3.9, y, 0); g.add(L_);
    const R_ = new THREE.Group(); R_.add(P.glassCard(5.6, 1.5, { color: '#ffffff', opacity: .1, edge: '#ffffff', edgeOp: .5 })); const e = label(mems[i][0], { h: 1.0, size: 150, font: 'en', gain: 1 }); e.position.set(-1.9, 0, .3); R_.add(e); const mt = label(mems[i][2], { h: .5, size: 100, fill: '#fff', gain: 1.2 }); mt.position.set(.75, 0, .2); R_.add(mt); place(R_, 3.9, y, 0); g.add(R_);
    const ln = mesh(new THREE.BoxGeometry(2.4, .07, .07), glow('#FFC857', 1.5), { shadow: false }); place(ln, 0, y, .2); g.add(ln); const ar = P.arrow(.7, '#FFC857'); place(ar, 0, y, .3, .5); ar.rotation.y = Math.PI; g.add(ar); return { L_, R_, ln, ar, o }; });
  rows.forEach((r, i) => { c.cue(t0[i], 'pop'); c.cue(t0[i] + .5, 'tick'); });
  c.camera([{ t: 0, p: [-2, .8, 14], l: [0, .3, 0], f: 33 }, { t: 1, p: [2, .5, 12.5], l: [0, .3, 0], f: 33 }]);
  return lt => {
    pop(hl, lt, .05, { d: .4 }); pop(hr, lt, .3, { d: .4 });
    rows.forEach((r, i) => { pop(r.L_, lt, t0[i], { d: .45 }); pop(r.R_, lt, t0[i] + .45, { d: .45 }); const k = seg(lt, t0[i] + .3, t0[i] + .8); r.ln.visible = k > 0; r.ln.scale.x = Math.max(.001, k); r.ar.visible = k > 0; r.o.rotation.y = lt * .8 + i; });
  };
};

// ============================================================ 7.4 fear or spend
V.fearOrSpend = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = person(Object.assign({ mood: 'think' }, { skin: 'brown', hair: 'short', shirt: '#8B5CF6', pants: '#2b2f55' })); place(me, 0, FY, 0, 1.0); g.add(me);
  const q = text3d(tx.q, { h: 1.7, size: 190, fill: '#FFC857', outline: '#2a1450', depth: '#a86a08', layers: 12, step: .024 }); place(q, 0, 2.5, .4); g.add(q);
  const mk = (x, bg, ic, l) => { const gr = new THREE.Group(); const th = P.thought(4.4, 2.6); gr.add(th); const o = ic; o.position.set(0, .35, .5); o.scale.setScalar(.8); th.add(o); const p = pillL(l, { bg, fill: '#fff', h: .62, size: 100 }); p.position.set(0, -.75, .5); th.add(p); place(gr, x, .5, .4); g.add(gr); gr.userData.o = o; return gr; };
  const wal = new THREE.Group(); wal.add(P.wallet()); const lk = P.lock(); lk.position.set(.7, 0, .35); wal.add(lk); wal.scale.setScalar(.8);
  const a = mk(-4.3, '#4C6FFF', wal, tx.a), b = mk(4.3, '#FF5A5F', P.bag('#FF5A5F', '#E5384F', '%'), tx.b);
  c.cue(.1, 'pop'); c.cue(dur * .2, 'pop'); c.cue(dur * .55, 'pop'); c.cue(dur * .55 + .05, 'ping');
  c.camera([{ t: 0, p: [0, .2, 14.5], l: [0, .8, 0], f: 33 }, { t: 1, p: [0, 1.4, 11], l: [0, .9, 0], f: 31, r: -1 }]);
  return lt => {
    me.idle(lt); pop(me, lt, 0, { d: .5 }); pop(q, lt, .15, { big: true }); q.position.y = 2.5 + bob(lt, .1, .7);
    pop(a, lt, dur * .15, { big: true }); pop(b, lt, dur * .5, { big: true }); a.position.y = .5 + bob(lt, .1, .6); b.position.y = .5 + bob(lt, .1, .6, 1); a.userData.o.rotation.y = bob(lt, .3, .5); b.userData.o.rotation.y = lt * .8;
  };
};

// ============================================================ 8.x steps
const medal = (n, x, y) => { const g = group(mesh(new THREE.CylinderGeometry(.62, .62, .22, 40), M('#FFC857', { metal: .8, rough: .25, env: 1.3 })), label(String(n), { h: .85, size: 190, fill: '#2a1b00', font: 'en', gain: 1 })); g.children[0].rotation.x = Math.PI / 2; g.children[1].position.z = .13; place(g, x, y, .6); return g; };

V.threeSteps = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = words3d(tx.top, { h: 1.5, size: 190, fill: '#ffffff', outline: '#1d0f4a', depth: '#5a4a9a', layers: 10 }); fitW(top, 8); place(top, 0, 2.4, .5); g.add(top);
  const items = [tx.s1, tx.s2, tx.s3].map((l, i) => { const gr = new THREE.Group(); gr.add(P.glassCard(3.5, 3.2, { color: '#FFC857', opacity: .12, edge: '#FFC857', edgeOp: .7 })); const m = medal(i + 1, 0, .55); m.scale.setScalar(1.2); gr.add(m); const t = label(l, { h: .62, size: 120, fill: '#fff', gain: 1.3 }); t.position.set(0, -.85, .3); gr.add(t); place(gr, -4.0 + i * 4.0, -.4, 0); g.add(gr); gr.userData.m = m; return gr; });
  const t0 = [dur * .3, dur * .5, dur * .72]; c.cue(.1, 'whoosh'); t0.forEach(t => c.cue(t, 'pop'));
  c.camera([{ t: 0, p: [0, .5, 15], l: [0, .3, 0], f: 33 }, { t: 1, p: [0, .8, 11.8], l: [0, .3, 0], f: 32 }]);
  return lt => { popWords(top, lt, .05, .12, .45); items.forEach((n, i) => { pop(n, lt, t0[i], { big: true }); n.userData.m.rotation.y = Math.sin(lt * 1.4 + i) * .5; n.position.y = -.4 + bob(lt, .08, .5, i); }); };
};

V.stepLook = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125, bg: 'rgba(255,255,255,.16)', fill: '#fff', bgStroke: 'rgba(255,255,255,.4)' }); place(top, 0, 2.65, .6); g.add(top); const bd = medal(1, -5.2, 2.55); g.add(bd);
  const me = person(Object.assign({ mood: 'think' }, PEOPLE.youth)); place(me, -4.3, FY, 0, 1.0); me.rotation.y = .5; g.add(me);
  const dad = person(Object.assign({ mood: 'flat' }, PEOPLE.dad)); place(dad, 4.3, FY, 0, 1.0); dad.rotation.y = -.5; g.add(dad);
  const mg = P.magnifier(1.2); place(mg, -1.2, .5, 1.2); g.add(mg);
  const th = P.thought(4.4, 2.3); place(th, 3.0, 2.0, .8, .85); g.add(th); const cl = P.cloud('#9AA6D6'); cl.scale.setScalar(.5); cl.position.set(-.9, 0, .4); th.add(cl); const bk = P.bank(); bk.scale.setScalar(.3); bk.position.set(.9, -.1, .4); th.add(bk);
  const lab = pillL(tx.lab, { h: .75, size: 112 }); place(lab, 0, -1.3, .8); g.add(lab);
  c.cue(.1, 'pop'); c.cue(dur * .3, 'whoosh'); c.cue(dur * .55, 'pop'); c.cue(dur * .7, 'ding');
  c.camera([{ t: 0, p: [-3, .6, 14], l: [-.8, .4, 0], f: 33 }, { t: 1, p: [2.2, .8, 11.8], l: [.8, .5, 0], f: 31 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 }); pop(bd, lt, .1, { big: true }); me.idle(lt); dad.idle(lt, 1); pop(me, lt, 0, { d: .5 }); pop(dad, lt, .1, { d: .5 });
    pop(mg, lt, dur * .25, { big: true }); mg.position.x = -1.2 + Math.sin(lt * 1.6) * 2.2; mg.position.y = .5 + Math.cos(lt * 2.1) * .25; pop(th, lt, dur * .5, { big: true }); th.position.y = 2.0 + bob(lt, .08, .6); rise(lab, lt, dur * .65, { dy: -.4 });
  };
};

V.stepMirror = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125, bg: 'rgba(255,255,255,.16)', fill: '#fff', bgStroke: 'rgba(255,255,255,.4)' }); place(top, 0, 2.65, .6); g.add(top); const bd = medal(2, -5.2, 2.55); g.add(bd);
  const me = person(Object.assign({ mood: 'think' }, PEOPLE.me)); place(me, -3.0, FY, 0, 1.1); me.rotation.y = .6; g.add(me);
  const mir = new THREE.Group(); const fr = mesh(new THREE.TorusGeometry(1.0, .09, 16, 64), M('#FFD66B', { metal: 1, rough: .2, env: 1.5 })); fr.scale.set(1.35, 1.9, 1); mir.add(fr); const gl = mesh(new THREE.CircleGeometry(1, 48), new THREE.MeshPhysicalMaterial({ color: col('#bfe3ff'), roughness: .05, metalness: .2, clearcoat: 1, transparent: true, opacity: .55 }), { shadow: false }); gl.scale.set(1.3, 1.85, 1); gl.position.z = -.02; mir.add(gl);
  const rf = person(Object.assign({ mood: 'think' }, PEOPLE.me)); rf.scale.setScalar(.58); rf.position.set(0, -1.7, .05); mir.add(rf); place(mir, 3.2, .3, 0); mir.rotation.y = -.3; g.add(mir);
  const qs = [0, 1, 2].map(i => { const q = text3d('?', { h: 1.0, size: 170, font: 'en', fill: i % 2 ? '#4CC9F0' : '#FFC857', outline: '#2a1450', depth: '#a86a08', layers: 8 }); place(q, 1.0 + i * 1.8, 2.1 - (i % 2) * .6, .6); g.add(q); return q; });
  const lab = pillL(tx.lab, { h: .75, size: 112 }); place(lab, 0, -1.3, .8); g.add(lab);
  c.cue(.1, 'pop'); c.cue(dur * .3, 'whoosh'); qs.forEach((q, i) => c.cue(dur * (.5 + i * .1), 'pop', .6));
  c.camera([{ t: 0, p: [-2, .6, 14], l: [0, .4, 0], f: 33 }, { t: 1, p: [2.2, .9, 11.4], l: [.8, .5, 0], f: 31 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 }); pop(bd, lt, .1, { big: true }); me.idle(lt); rf.idle(lt, .2); pop(me, lt, 0, { d: .5 }); pop(mir, lt, dur * .25, { big: true }); mir.rotation.y = -.3 + bob(lt, .12, .25);
    qs.forEach((q, i) => { pop(q, lt, dur * (.5 + i * .1), { big: true }); q.position.y = q.userData.base.y + bob(lt, .12, .8, i); }); rise(lab, lt, dur * .7, { dy: -.4 });
  };
};

V.stepLearn = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125, bg: 'rgba(255,255,255,.16)', fill: '#fff', bgStroke: 'rgba(255,255,255,.4)' }); place(top, 0, 2.65, .6); g.add(top); const bd = medal(3, -5.2, 2.55); g.add(bd);
  const hl = halo('#FFD66B', 9, .35); place(hl, 0, .3, -.5); g.add(hl);
  const me = person(Object.assign({ mood: 'grin' }, PEOPLE.me, { shirt: '#FFC857' })); place(me, 0, FY, .4, 1.15); g.add(me);
  const others = [[PEOPLE.girl, -5.0, -.4], [PEOPLE.curly, 5.0, -.4], [PEOPLE.dad, -3.0, -1.6], [PEOPLE.youth, 3.0, -1.6]].map(([o, x, z]) => { const p = person(Object.assign({ mood: 'smile' }, o)); place(p, x, FY, z, .8); p.rotation.y = x < 0 ? .5 : -.5; g.add(p); return p; });
  const items = others.map((p, i) => { const it = i % 2 ? P.bulb() : P.book ? P.docs() : P.docs(); it.scale.setScalar(.34); g.add(it); return it; });
  const lab = pillL(tx.lab, { bg: '#3DDC97', fill: '#04281b', h: .75, size: 112 }); place(lab, 0, -1.3, .8); g.add(lab);
  const t0 = [dur * .12, dur * .3, dur * .48, dur * .64]; t0.forEach(t => { c.cue(t, 'pop'); c.cue(t + .5, 'whoosh', .5); }); c.cue(dur * .85, 'ding');
  c.camera([{ t: 0, p: [0, 1.0, 15], l: [0, .3, 0], f: 33 }, { t: 1, p: [0, .8, 11], l: [0, .5, 0], f: 31, r: 1 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 }); pop(bd, lt, .1, { big: true }); me.idle(lt);
    others.forEach((p, i) => { p.idle(lt, i); pop(p, lt, t0[i], { d: .45 }); const k = E.inOut(seg(lt, t0[i] + .4, t0[i] + 1.3)), it = items[i]; const from = [p.position.x, 1.9, p.position.z], to = [0, 2.7, .8]; it.position.set(lerp(from[0], to[0], k), lerp(from[1], to[1], k) + Math.sin(k * Math.PI) * 1.4, lerp(from[2], to[2], k)); it.visible = lt > t0[i] + .4 && k < 1; it.scale.setScalar(.34 + .15 * Math.sin(k * Math.PI)); it.rotation.y = lt * 3; });
    rise(lab, lt, dur * .75, { dy: -.4 });
  };
};

// ============================================================ 9.x outro
V.notMath = c => {
  const { g, S, dur } = c, tx = S.txt;
  const board = P.glassCard(11, 3.8, { color: '#ffffff', opacity: .1, edge: '#ffffff', edgeOp: .5 }); place(board, 0, .9, -.2); g.add(board);
  const eq = ['2', '+', '2', '=', '4'].map((ch, i) => { const t = text3d(ch, { h: 2.0, size: 220, font: 'en', fill: '#ffffff', outline: '#1d0f4a', depth: '#5a4a9a', layers: 12, step: .03 }); place(t, -3.8 + i * 1.9, .9, .3); g.add(t); t.userData.a = (i - 2) * .35; return t; });
  const sl = mesh(new THREE.BoxGeometry(11.5, .4, .3), M('#FF3B4E', { rough: .25 })); place(sl, 0, .9, 1.0); sl.rotation.z = -.28; g.add(sl);
  const pl = pillL(tx.main, { h: .9, size: 130 }); place(pl, 0, -1.3, .8); g.add(pl);
  const hr = P.heart(); place(hr, -2.6, .9, .5, 1.1); g.add(hr); const gr = P.gear(.8, 9, '#9AA6D6'); place(gr, 2.6, .9, .5, 1.0); g.add(gr);
  c.cue(.1, 'whoosh'); c.cue(dur * .4, 'scratch'); c.cue(dur * .65, 'pop'); c.cue(dur * .65 + .1, 'ding');
  c.camera([{ t: 0, p: [0, .8, 14], l: [0, .8, 0], f: 33 }, { t: 1, p: [0, 1.0, 10.6], l: [0, .8, 0], f: 30 }]);
  return lt => {
    pop(board, lt, .05, { d: .5 }); const k = E.out3(seg(lt, dur * .4, dur * .4 + .35)); sl.visible = k > 0; sl.scale.x = Math.max(.001, k);
    const f = E.in2(seg(lt, dur * .55, dur * .55 + .6)); eq.forEach((t, i) => { t.position.x = -3.8 + i * 1.9 + f * (i - 2) * 1.2; t.position.y = .9 + f * (i % 2 ? 1.6 : -1.6); t.rotation.z = f * t.userData.a * 4; t.visible = f < .98; });
    sl.visible = sl.visible && f < .98; pop(hr, lt, dur * .6, { big: true }); hr.scale.setScalar(1.1 + .08 * Math.sin(lt * 6)); pop(gr, lt, dur * .66, { big: true }); gr.rotation.z = lt * .9; rise(pl, lt, dur * .3, { dy: -.4 });
  };
};

V.mindExperience = c => {
  const { g, S, dur } = c, tx = S.txt;
  const hl = halo('#FFD66B', 12, .3); place(hl, 0, .6, -1); g.add(hl);
  const wal = P.wallet(); place(wal, 0, .4, 0, 1.4); g.add(wal);
  const hr = new THREE.Group(); const h = P.heart(); h.scale.setScalar(1.3); hr.add(h); const hp = pillL(tx.l, { bg: '#FF4D6D', fill: '#fff', h: .66, size: 100 }); hp.position.set(0, -1.5, .4); hr.add(hp); place(hr, -4.6, 1.0, 0); g.add(hr);
  const ex = new THREE.Group(); const pol = P.polaroid('🌍', '#7FA8FF'); pol.scale.setScalar(1.0); pol.rotation.z = -.1; ex.add(pol); const ep = pillL(tx.r, { bg: '#4CC9F0', fill: '#02283a', h: .66, size: 100 }); ep.position.set(0, -1.6, .4); ex.add(ep); place(ex, 4.6, 1.0, 0); g.add(ex);
  const a1 = P.arrow(1.4); place(a1, -2.5, .8, 0, .8); g.add(a1); const a2 = P.arrow(1.4); place(a2, 2.5, .8, 0, .8); a2.rotation.y = Math.PI; g.add(a2);
  const t = pillL(tx.main, { bg: '#fff', fill: '#1d0f4a', h: .85, size: 125 }); place(t, 0, -1.3, .8); g.add(t);
  c.cue(.1, 'pop'); c.cue(dur * .25, 'pop'); c.cue(dur * .5, 'pop'); c.cue(dur * .55, 'whoosh'); c.cue(dur * .75, 'ding');
  c.camera([{ t: 0, p: [0, 1.2, 14.5], l: [0, .5, 0], f: 33 }, { t: 1, p: [0, .6, 11.5], l: [0, .5, 0], f: 31 }]);
  return lt => {
    pop(hr, lt, .15, { big: true }); h.rotation.y = lt * .9; pop(ex, lt, dur * .25, { big: true }); pol.rotation.y = bob(lt, .3, .3);
    pop(wal, lt, dur * .45, { big: true }); wal.rotation.y = bob(lt, .3, .25); pop(a1, lt, dur * .5, { d: .35 }); pop(a2, lt, dur * .5, { d: .35 }); rise(t, lt, dur * .65, { dy: -.4 });
  };
};

V.likeBtn = c => {
  const { g, S, dur } = c, tx = S.txt;
  const hl = halo('#FFD66B', 12, .35); place(hl, 0, .6, -1); g.add(hl);
  const th = P.thumb(); place(th, 0, .4, 0, 1.45); g.add(th);
  const cnt = pillL(tx.cnt, { bg: '#fff', fill: '#1d0f4a', font: 'en', h: .8, size: 125 }); place(cnt, 3.6, 2.3, .8); g.add(cnt);
  const pl = pillL(tx.main, { bg: '#4C6FFF', fill: '#fff', h: .9, size: 130 }); place(pl, 0, -1.3, .8); g.add(pl);
  const hearts = Array.from({ length: 10 }, (_, i) => { const h = P.heart(i % 2 ? '#FF4D6D' : '#FFC857'); h.scale.setScalar(.38); h.userData.a = i / 10 * 6.28; g.add(h); return h; });
  const tk = dur * .45; c.cue(.1, 'pop'); c.cue(tk, 'click'); c.cue(tk + .1, 'pop'); c.cue(tk + .2, 'sparkle');
  c.camera([{ t: 0, p: [-2.5, 1, 13], l: [0, .5, 0], f: 33 }, { t: 1, p: [2, .6, 10.5], l: [0, .5, 0], f: 31 }]);
  return lt => {
    const press = seg(lt, tk, tk + .12), rel = seg(lt, tk + .12, tk + .5); const s = 1.45 * (1 - .16 * press * (1 - rel) + .1 * E.elastic(rel) * (rel > 0 ? 1 : 0));
    pop(th, lt, .05, { big: true, s: 1.45 }); if (lt >= .6) { th.scale.setScalar(s); th.rotation.z = -.1 * (1 - E.out3(rel)) * (lt >= tk ? 1 : 0); } th.position.y = .4 + (lt < tk ? bob(lt, .1, .5) : 0); th.rotation.y = bob(lt, .25, .3);
    pop(cnt, lt, tk + .1, { big: true }); const p = seg(lt, tk + .1, tk + 1); hearts.forEach(h => { const r = 1.6 + 5 * E.out3(p); h.position.set(Math.cos(h.userData.a) * r, .5 + Math.sin(h.userData.a) * r * .7, .8); h.visible = p > 0 && p < 1; h.scale.setScalar(.38 * (1 - p) + .001); h.rotation.y = lt * 4; }); rise(pl, lt, .3, { dy: -.4 });
  };
};

V.commentBtn = c => {
  const { g, S, dur } = c, tx = S.txt;
  const mkB = (text, x, y, side, colr) => { const gr = new THREE.Group(); const w = Math.max(3.2, text.length * .21 + 1.2); const b = P.bubble(w, 1.1); gr.add(b); const t = label(text, { h: .56, size: 100, fill: '#1d0f4a', gain: 1 }); t.position.set(0, 0, .2); gr.add(t); const av = P.avatar(colr); av.position.set(side * (w / 2 + .6), 0, 0); gr.add(av); place(gr, x, y, 0); g.add(gr); return gr; };
  const items = [mkB(tx.c1, -3.2, 1.6, -1, '#6C3BE8'), mkB(tx.c2, 3.7, .4, 1, '#E5384F'), mkB(tx.c3, -2.6, -.9, -1, '#2FB8A6')];
  const typing = group(P.bubble(1.8, .9), ...[-.45, 0, .45].map(x => { const d = mesh(new THREE.SphereGeometry(.1, 12, 8), M('#9AA3C7')); d.position.set(x, 0, .2); return d; })); place(typing, 4.2, -1.1, 0); g.add(typing);
  const pl = pillL(tx.main, { h: .9, size: 130 }); place(pl, 0, 2.7, .8); g.add(pl);
  const t0 = [.1, dur * .3, dur * .55]; t0.forEach(t => c.cue(t, 'pop')); c.cue(dur * .75, 'tick');
  c.camera([{ t: 0, p: [-2, .6, 13.5], l: [0, .3, 0], f: 33 }, { t: 1, p: [2, .8, 11.5], l: [0, .3, 0], f: 32 }]);
  return lt => {
    items.forEach((n, i) => { pop(n, lt, t0[i], { big: true }); n.position.y = n.userData.base.y + bob(lt, .08, .5, i); }); pop(typing, lt, dur * .72, { big: true }); typing.children.slice(1).forEach((d, i) => d.position.y = Math.sin(lt * 8 - i) * .12); rise(pl, lt, .2, { dy: .5 });
  };
};

V.subscribeBtn = c => {
  const { g, S, dur } = c, tx = S.txt;
  const hl = halo('#FF5A6E', 12, .3); place(hl, 0, .6, -1); g.add(hl);
  const btn = new THREE.Group(); const bg = mesh(rbox(5.6, 1.7, .5, .8, 8), M('#E5232B', { rough: .25, coat: 1 })); btn.add(bg);
  const l1 = label('SUBSCRIBE', { h: .9, size: 150, fill: '#fff', font: 'en', gain: 1.1 }); l1.position.z = .3; btn.add(l1); const l2 = label('SUBSCRIBED ✓', { h: .8, size: 135, fill: '#fff', font: 'en', gain: 1.1 }); l2.position.z = .3; btn.add(l2); place(btn, -1.2, .6, 0); g.add(btn);
  const bell = P.bell(); place(bell, 3.9, .7, 0, 1.2); g.add(bell);
  const cur = P.hand(); place(cur, 4.6, -1.3, 1.2, 1.4); g.add(cur);
  const pl = pillL(tx.main, { bg: '#fff', fill: '#1d0f4a', h: .9, size: 130 }); place(pl, 0, 2.7, .8); g.add(pl);
  const tk = dur * .5; c.cue(.1, 'pop'); c.cue(.4, 'pop'); c.cue(tk, 'click'); c.cue(tk + .15, 'ding'); c.cue(tk + .3, 'bell'); c.cue(tk + .8, 'bell', .7);
  c.camera([{ t: 0, p: [-2, .6, 13.5], l: [0, .5, 0], f: 33 }, { t: 1, p: [1.5, .8, 10.8], l: [.4, .5, 0], f: 31 }]);
  return lt => {
    pop(btn, lt, .1, { big: true }); pop(bell, lt, .4, { big: true });
    const mv = E.inOut(seg(lt, dur * .2, tk)); const px = lerp(4.6, -1.0, mv), py = lerp(-1.8, .1, mv), press = seg(lt, tk, tk + .1) * (1 - seg(lt, tk + .1, tk + .3));
    pop(cur, lt, dur * .2, { d: .3 }); if (lt > dur * .2 + .3) { cur.position.set(px, py, 1.2); cur.scale.setScalar(1.4 - .15 * press); }
    const done = lt >= tk + .05; l1.visible = !done; l2.visible = done; bg.material.color.set(done ? '#5B6591' : '#E5232B'); btn.scale.setScalar(btn.userData.base.s * (1 - .05 * press));
    const rg = seg(lt, tk + .25, tk + 1.6); bell.rotation.z = rg > 0 && rg < 1 ? Math.sin(rg * 24) * .4 * (1 - rg) : 0; rise(pl, lt, .2, { dy: .5 });
  };
};

V.endCard = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = rayFan(24, '#ffd9a0', .08); place(rays, 0, .6, -3); g.add(rays); const hl = halo('#FFD66B', 14, .45); place(hl, 0, .6, -1.5); g.add(hl);
  const nm = label('🙏', { h: 2.4, size: 260, font: 'en', gain: 1 }); place(nm, 0, 2.0, 0); g.add(nm);
  const t = words3d(tx.main, { h: 1.7, size: 170, fill: '#FFD66B', outline: '#2a1450', depth: '#a86a08', layers: 12, step: .024 }); fitW(t, 9); place(t, 0, -0.4, 0); g.add(t);
  const sb = pillL(tx.sub, { bg: 'rgba(255,255,255,.18)', fill: '#fff', bgStroke: 'rgba(255,255,255,.45)', h: .85, size: 125 }); place(sb, 0, -1.3, .6); g.add(sb);
  const rain = coinRain(g, 14, 9); c.cue(.05, 'tada'); c.cue(.2, 'sparkle'); c.flash(.02, .3, '#fff', .35);
  c.camera([{ t: 0, p: [0, -.8, 13], l: [0, .5, 0], f: 36 }, { t: 1, p: [0, .8, 10.5], l: [0, .5, 0], f: 31 }]);
  return lt => { rays.rotation.z = lt * .15; pop(nm, lt, .05, { big: true }); nm.position.y = 2.0 + bob(lt, .1, .5); popWords(t, lt, .3, .22, .55); rise(sb, lt, 1.0, { dy: -.4 }); rain(Math.max(0, lt - .2)); };
};
