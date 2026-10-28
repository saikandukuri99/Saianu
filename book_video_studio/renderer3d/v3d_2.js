// Scenes 3-5 as 3D shots: your world is small, history shapes money habits, the other side.
import * as THREE from 'three';
import { V, clamp, lerp, seg, E, bob, rng, FLOOR_Y } from './core3d.js';
import { P, M, person, PEOPLE, label, text3d, words3d, fitW, at, pop, rise, popWords, group, mesh, glow, halo, lightCone, rbox, col } from './kit3d.js';
import { pillL, place, FY, coinRain } from './v3d_1.js';

const stage = (r, color, y = FY + .05) => { const m = mesh(new THREE.CylinderGeometry(r, r * 1.04, .22, 64), M(color, { rough: .35, metal: .2 }), { receive: true }); m.position.y = y - .11; return m; };

// ============================================================ 3.1 not just maths
V.calcNo = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125 }); place(top, 0, 2.65, .5); g.add(top);
  const calc = P.calculator('5 × 12'); place(calc, -3.2, .1, 0, 1.35); g.add(calc);
  const x = P.cross(.9); place(x, -2.2, 1.2, 1.2); g.add(x);
  const items = [[P.heart(), tx.p1, 2.2, 1.55, .8], [P.polaroid('🧒', '#7FA8FF'), tx.p2, 4.9, .2, .8], [P.house(), tx.p3, 1.9, -.9, .8]].map(([o, l, px, py, s], i) => { const gr = new THREE.Group(); o.scale.setScalar(s); gr.add(o); const p = pillL(l, { bg: '#fff', fill: '#1d0f4a', h: .62, size: 100 }); p.position.set(0, -1.15, .3); gr.add(p); place(gr, px, py, 0); g.add(gr); gr.userData.o = o; return gr; });
  c.cue(.2, 'whoosh'); c.cue(dur * .3, 'stamp'); c.shake(dur * .3, .12, .3); items.forEach((n, i) => c.cue(dur * (.5 + i * .13), 'pop'));
  c.camera([{ t: 0, p: [-5, 1, 12], l: [-2, .3, 0], f: 33 }, { t: .5, p: [-1, .8, 11], l: [0, .2, 0], f: 32 }, { t: 1, p: [3, .5, 12], l: [1, .2, 0], f: 33 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 }); pop(calc, lt, .15, { d: .5 }); calc.rotation.y = .25 + bob(lt, .12, .2);
    const k = seg(lt, dur * .3 - .25, dur * .3); x.visible = lt > dur * .3 - .25; x.scale.setScalar(lerp(3.2, 1, E.in2(k)) * (lt > dur * .3 ? 1 + .12 * Math.exp(-(lt - dur * .3) * 8) : 1));
    items.forEach((n, i) => { pop(n, lt, dur * (.5 + i * .13), { big: true }); n.position.y = n.userData.base.y + bob(lt, .1, .5, i); n.userData.o.rotation.y = lt * .8 + i; });
  };
};

// ============================================================ 3.2 where / home / what we saw
V.lifeTimeline = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125, bg: 'rgba(255,255,255,.16)', fill: '#fff', bgStroke: 'rgba(255,255,255,.4)' }); place(top, 0, 2.7, .5); g.add(top);
  const xs = [-5.2, -1.9, 1.4], T0 = [.02, .24, .46], ics = [P.pin(), P.house(), P.eye()], labs = [tx.n1, tx.n2, tx.n3];
  const nodes = xs.map((x, i) => { const gr = new THREE.Group(); const ped = mesh(new THREE.CylinderGeometry(1.1, 1.2, .3, 40), M('#ffffff', { opacity: .22, rough: .1 }), { receive: true }); ped.position.y = -.9; gr.add(ped); const ic = ics[i]; ic.position.y = .35; ic.scale.setScalar(i === 1 ? .8 : .85); gr.add(ic); const p = pillL(labs[i], { bg: '#fff', fill: '#1d0f4a', h: .62, size: 100 }); p.position.set(0, -1.65, .4); gr.add(p); place(gr, x, 0, 0); g.add(gr); gr.userData.ic = ic; return gr; });
  const arr = [0, 1, 2].map(i => { const a = P.arrow(1.3); place(a, xs[i] + 1.65, .2, 0, .8); g.add(a); return a; });
  const wal = new THREE.Group(); const w = P.wallet(); w.scale.setScalar(.95); wal.add(w); wal.add(halo('#FFD66B', 6, .5)); const wp = pillL(tx.n4, { h: .7, size: 105 }); wp.position.set(0, -1.65, .4); wal.add(wp); place(wal, 5.0, .1, 0); g.add(wal);
  nodes.forEach((n, i) => c.cue(dur * T0[i], 'pop')); c.cue(dur * .72, 'whoosh'); c.cue(dur * .8, 'ding');
  c.camera([{ t: 0, p: [-5.5, 1.3, 12], l: [-3, .2, 0], f: 33 }, { t: 1, p: [3.5, 1, 11], l: [2.5, .2, 0], f: 33 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 });
    nodes.forEach((n, i) => { pop(n, lt, dur * T0[i], { big: true }); n.userData.ic.rotation.y = lt * .9; if (i === 2) n.userData.ic.userData.iris.position.x = Math.sin(lt * 2) * .3; });
    arr.forEach((a, i) => { pop(a, lt, dur * (i < 2 ? T0[i + 1] - .08 : .68), { d: .4 }); a.position.x = a.userData.base.x + bob(lt, .12, 1.1); });
    pop(wal, lt, dur * .74, { big: true }); w.rotation.y = lt * .8;
  };
};

// ============================================================ 3.3 the whole world
V.globeAll = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125 }); place(top, 0, 2.7, .5); g.add(top);
  const gl = P.globe(1.9); place(gl, 0, .2, 0); g.add(gl);
  const tok = [P.coin(.45), P.bolt(), P.flame(), P.tag('₹99'), P.heart('#FF4D6D'), P.star(.5)].map((o, i) => { o.scale.setScalar(i === 3 ? .55 : .62); o.userData.a = i / 6 * 6.28 + .4; g.add(o); return o; });
  const eyeN = P.eye(); place(eyeN, 4.8, -1.0, .6, .7); g.add(eyeN); const xx = P.cross(.4); place(xx, 5.7, -0.55, 1.0); g.add(xx);
  const bp = pillL(tx.bottom, { bg: '#fff', fill: '#1d0f4a', h: .72, size: 110 }); place(bp, 0, -1.3, .6); g.add(bp);
  c.cue(.1, 'whoosh'); tok.forEach((n, i) => c.cue(.4 + i * .18, 'pop', .6)); c.cue(dur * .6, 'error');
  c.camera([{ t: 0, p: [-3, 1.2, 14], l: [0, .2, 0], f: 33 }, { t: 1, p: [2.5, .6, 11.5], l: [.4, .2, 0], f: 32 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 }); pop(gl, lt, .05, { d: .7 }); gl.spin(lt);
    tok.forEach((n, i) => { const a = n.userData.a + lt * .45; const k = seg(lt, .4 + i * .18, .9 + i * .18); n.visible = k > 0; n.scale.setScalar(Math.max(.001, (i === 3 ? .55 : .62) * E.backBig(k))); n.position.set(Math.cos(a) * 4.0, Math.sin(a) * 1.55 + .2, Math.sin(a) * 2.4); n.rotation.y = lt * 1.3 + i; });
    pop(eyeN, lt, dur * .5, { s: .7, big: true }); eyeN.userData.base && (eyeN.children[0] && 0); pop(xx, lt, dur * .6, { big: true }); rise(bp, lt, dur * .55, { dy: -.4 });
  };
};

// ============================================================ 3.4 only a small slice
V.spotlightWorld = c => {
  const { g, S, dur } = c, tx = S.txt;
  const gl = P.globe(2.3); place(gl, 0, .3, -1); g.add(gl);
  const shell = mesh(new THREE.SphereGeometry(2.36, 48, 32), new THREE.MeshBasicMaterial({ color: 0x05061a, transparent: true, opacity: 0 }), { shadow: false }); shell.position.copy(gl.position); g.add(shell);
  const dio = new THREE.Group(); const st = stage(1.2, '#3a8f5c', 0); st.position.y = -.25; dio.add(st); const h = P.house(); h.scale.setScalar(.5); h.position.set(-.35, .45, 0); dio.add(h); const me = person(Object.assign({ mood: 'smile' }, PEOPLE.me)); me.scale.setScalar(.34); me.position.set(.5, -.1, .15); dio.add(me);
  const tree = group(mesh(new THREE.CylinderGeometry(.06, .08, .4, 8), M('#8a5a2b')), mesh(new THREE.ConeGeometry(.28, .7, 12), M('#2fa05f'))); tree.children[1].position.y = .5; tree.position.set(.1, .0, -.6); dio.add(tree);
  const ring = mesh(new THREE.TorusGeometry(1.32, .06, 16, 64), glow('#FFD66B', 1.6)); ring.position.y = .1; ring.rotation.x = Math.PI / 2 - .35; dio.add(ring); dio.add(halo('#FFD66B', 6, .35));
  place(dio, 0, .1, 2.2, 1); g.add(dio);
  const cap = pillL(tx.small, { h: .72, size: 110 }); place(cap, 0, -1.3, .8); g.add(cap);
  const eq = words3d(tx.eq, { h: 1.0, size: 150, fill: '#fff', outline: '#1d0f4a', depth: '#5a4a9a', layers: 8 }); fitW(eq, 11); place(eq, 0, 2.75, .6); g.add(eq);
  c.cue(.2, 'whoosh'); c.cue(dur * .38, 'zoom'); c.cue(dur * .6, 'ding');
  c.camera([{ t: 0, p: [3.5, 1.5, 14], l: [0, .3, -1], f: 33 }, { t: .45, p: [1.4, .8, 10.5], l: [0, .2, 0], f: 31 }, { t: 1, p: [-.4, .4, 8.6], l: [0, .1, 1], f: 29 }]);
  return lt => {
    gl.spin(lt); const p = E.inOut(seg(lt, dur * .35, dur * .75)); shell.material.opacity = .62 * p;
    const k = E.back(seg(lt, dur * .3, dur * .6)); dio.visible = lt > dur * .3; dio.scale.setScalar(Math.max(.001, k)); dio.rotation.y = bob(lt, .2, .2); ring.rotation.z = lt * .6; me.idle(lt);
    pop(cap, lt, dur * .5, { d: .5 }); popWords(eq, lt, dur * .6, .15, .5);
  };
};

// ============================================================ 4.1 inflation
V.inflation = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = words3d(tx.top, { h: 1.0, size: 150, fill: '#fff', outline: '#2a0b16', depth: '#8a2145', layers: 8 }); fitW(top, 9.5); place(top, 0, 2.7, .6); g.add(top);
  const steps = [['₹10', '#4CC9F0'], ['₹50', '#3DDC97'], ['₹200', '#FFC857'], ['₹1000', '#FF5A5F']].map(([l, cc], i) => { const gr = new THREE.Group(); const b = mesh(rbox(1.9, .9 + i * .9, 1.4, .12), M(cc, { rough: .35 }), { receive: true }); b.position.y = (.9 + i * .9) / 2 - .9; gr.add(b); const tg = P.tag(l, '#ffffff'); tg.children.forEach(ch => { if (ch.material && ch.material.color && ch.type === 'Mesh' && ch.geometry.type === 'ExtrudeGeometry') ch.material.color.set(cc); }); tg.scale.setScalar(.62); tg.position.set(0, (.9 + i * .9) - .45 + .55, .5); tg.rotation.z = .12; gr.add(tg); place(gr, -5.2 + i * 2.15, FY + .9 + .0, 0); gr.position.y = FY + .9; g.add(gr); return gr; });
  const fl = P.flame(); place(fl, 3.4, 2.0, 0, 1.0); g.add(fl);
  const coin = P.coin(1.15); place(coin, 5.0, .2, 0); g.add(coin);
  const dn = P.arrow(1.2, '#FF5A5F'); place(dn, 5.0, -1.25, 0, .8); dn.rotation.z = -Math.PI / 2; g.add(dn);
  const lab = pillL(tx.coin, { bg: '#FF5A5F', fill: '#fff', h: .62, size: 100 }); place(lab, 4.4, -1.3, .6); g.add(lab);
  steps.forEach((n, i) => c.cue(.25 + i * dur * .13, 'pop')); c.cue(dur * .6, 'melt');
  c.camera([{ t: 0, p: [-6, -.2, 12.5], l: [-3, .2, 0], f: 33 }, { t: .6, p: [-1, 1.2, 12], l: [1, .6, 0], f: 33 }, { t: 1, p: [3, 1.0, 11.5], l: [2.5, .2, 0], f: 32 }]);
  return lt => {
    popWords(top, lt, .05, .1, .45);
    steps.forEach((n, i) => { pop(n, lt, .25 + i * dur * .13, { big: true }); });
    pop(fl, lt, dur * .5, { big: true }); fl.userData.o.scale.y = 1 + .12 * Math.sin(lt * 18);
    const k = 1 - .45 * E.inOut(seg(lt, dur * .55, dur * .9)); pop(coin, lt, .3, { s: k, d: .5 }); coin.rotation.y = lt * 1.6;
    pop(dn, lt, dur * .6, { d: .4 }); pop(lab, lt, dur * .65, { d: .5 });
  };
};

// ============================================================ 4.2 great depression
V.depression = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = words3d(tx.top, { h: 1.15, size: 150, fill: '#F3DDB8', outline: '#150f08', depth: '#7a5a2a', layers: 9 }); fitW(top, 9.5); place(top, 0, 2.55, .5); g.add(top);
  const yr = label(tx.year, { h: .5, size: 100, fill: '#E9C58B', font: 'en', weight: 600, gain: 1.1 }); place(yr, 0, 1.55, .5); g.add(yr);
  const mkPanel = x => { const p = P.glassCard(4.1, 3.5, { color: '#e9c58b', opacity: .1, edge: '#E9C58B', edgeOp: .55 }); place(p, x, -.2, -.3); g.add(p); return p; };
  const A_ = mkPanel(-4.4), B_ = mkPanel(0), C_ = mkPanel(4.4);
  const ch = P.chart({ color: '#FF6B6B', w: 3.0, h: 1.4, pts: [.1, .16, .08, .3, .5, .46, .8, .95] }); ch.position.set(0, .35, .2); A_.add(ch);
  const p1 = pillL(tx.p1, { bg: '#E9C58B', fill: '#2a1b00', h: .55, size: 95 }); p1.position.set(0, -1.15, .3); A_.add(p1);
  const bk = P.bank(); bk.scale.setScalar(.36); bk.position.set(0, .3, .3); B_.add(bk);
  const shut = mesh(rbox(1.75, .01, .3, .02), M('#6B7592', { metal: .6 })); shut.position.set(0, .83, .55); B_.add(shut);
  const sign = group(mesh(rbox(1.5, .42, .08, .06), M('#FF5A5F')), label('CLOSED', { h: .3, size: 100, fill: '#fff', font: 'en', gain: 1 })); sign.children[1].position.z = .06; sign.position.set(0, .15, .7); sign.rotation.z = -.1; B_.add(sign);
  const p2 = pillL(tx.p2, { bg: '#E9C58B', fill: '#2a1b00', h: .55, size: 95 }); p2.position.set(0, -1.15, .3); B_.add(p2);
  const pp = person(Object.assign({ mood: 'worry' }, { skin: 'tan', hair: 'short', shirt: '#8D7B5B', pants: '#4a4033' })); pp.scale.setScalar(.55); pp.position.set(0, -1.3, .2); C_.add(pp);
  const slip = group(mesh(rbox(1.5, .8, .05, .05), M('#ffffff')), label('JOB LOSS', { h: .3, size: 100, fill: '#B3262F', font: 'en', gain: 1 })); slip.children[1].position.z = .04; slip.position.set(0, 1.0, .5); slip.rotation.z = -.15; C_.add(slip);
  const p3 = pillL(tx.p3, { bg: '#E9C58B', fill: '#2a1b00', h: .55, size: 95 }); p3.position.set(0, -1.15, .3); C_.add(p3);
  const t2 = dur * .3, t3 = dur * .6;
  c.cue(.1, 'whoosh'); c.cue(.6, 'crash'); c.cue(t2 + .5, 'whoosh'); c.cue(t2 + 1.2, 'thud'); c.shake(t2 + 1.2, .14, .35); c.cue(t3 + .4, 'whoosh'); c.cue(t3 + 1.1, 'stamp');
  c.camera([{ t: 0, p: [-5, .8, 12], l: [-3.5, .1, 0], f: 33 }, { t: .5, p: [0, .6, 11.5], l: [0, .1, 0], f: 33 }, { t: 1, p: [4.5, .8, 11], l: [3.5, .1, 0], f: 32 }]);
  return lt => {
    popWords(top, lt, .05, .12, .45); yr.visible = lt > .4;
    rise(A_, lt, .2, { dy: -.8 }); ch.setProgress(E.inOut(seg(lt, .5, 1.6)));
    rise(B_, lt, t2, { dy: -.8 }); const s = E.inOut(seg(lt, t2 + .5, t2 + 1.3)); shut.scale.y = Math.max(.01, 1 + s * 160); shut.position.y = .83 - s * 0.84; shut.scale.y = Math.max(.01, s * 168); sign.visible = lt > t2 + 1.2; sign.scale.setScalar(Math.max(.001, E.backBig(seg(lt, t2 + 1.2, t2 + 1.6))));
    rise(C_, lt, t3, { dy: -.8 }); pp.idle(lt); slip.visible = lt > t3 + .5; slip.scale.setScalar(Math.max(.001, E.backBig(seg(lt, t3 + .5, t3 + .9)))); slip.position.y = 1.0 + bob(lt, .06, .6);
  };
};

// ============================================================ 4.3 market = danger
V.fearMarket = c => {
  const { g, S, dur } = c, tx = S.txt;
  const lab = pillL(tx.label, { bg: '#fff', fill: '#1d0f4a', h: .72, size: 110 }); place(lab, 0, 2.65, .6); g.add(lab);
  const card = new THREE.Group(); place(card, 0, -0.1, 0); g.add(card);
  const f1 = new THREE.Group(), f2 = new THREE.Group(); card.add(f1, f2); f2.rotation.y = Math.PI;
  f1.add(P.glassCard(8.4, 4.0, { color: '#3DDC97', opacity: .14, edge: '#3DDC97', edgeOp: .8 })); const rk = P.rocket(); rk.scale.setScalar(.95); rk.position.set(-2.5, .3, .4); rk.rotation.z = -.4; f1.add(rk);
  const c1 = P.chart({ color: '#3DDC97', w: 3.4, h: 1.7, pts: [.9, .78, .7, .5, .56, .3, .2, .06] }); c1.setProgress(1); c1.position.set(1.7, .3, .2); f1.add(c1);
  const l1 = pillL(tx.good, { bg: '#3DDC97', fill: '#04281b', h: .9, size: 130 }); l1.position.set(0, -1.45, .5); f1.add(l1);
  f2.add(P.glassCard(8.4, 4.0, { color: '#FF5A5F', opacity: .16, edge: '#FF5A5F', edgeOp: .8 })); const wr = P.warning(); wr.scale.setScalar(1.15); wr.position.set(-2.5, .3, .4); f2.add(wr);
  const c2 = P.chart({ color: '#FF5A5F', w: 3.4, h: 1.7, pts: [.1, .2, .16, .4, .36, .62, .7, .94] }); c2.setProgress(1); c2.position.set(1.7, .3, .2); f2.add(c2);
  const l2 = pillL(tx.bad, { bg: '#FF5A5F', fill: '#fff', h: .9, size: 130 }); l2.position.set(0, -1.45, .5); f2.add(l2);
  const xx = P.cross(.8); place(xx, 3.4, 1.4, 1.2); card.add(xx);
  const fl = dur * .5; c.cue(.1, 'whoosh'); c.cue(fl - .2, 'stamp'); c.cue(fl + .2, 'flip'); c.cue(fl + .7, 'alarm'); c.shake(fl + .7, .1, .3);
  c.camera([{ t: 0, p: [0, 1.6, 15], l: [0, 0, 0], f: 34, r: 1 }, { t: .55, p: [-1.5, .6, 12], l: [0, 0, 0], f: 33 }, { t: 1, p: [1.5, -.4, 11.5], l: [0, 0, 0], f: 32, r: -1.2 }]);
  return lt => {
    rise(lab, lt, .1, { dy: .5 }); pop(card, lt, .05, { d: .5 });
    const p = E.inOut(seg(lt, fl, fl + .6)); card.rotation.y = p * Math.PI; xx.visible = lt > fl - .35 && p < .5; xx.rotation.y = 0; if (xx.visible) xx.scale.setScalar(Math.max(.001, E.backBig(seg(lt, fl - .35, fl - .05))));
    rk.position.y = .3 + bob(lt, .1, .8); wr.rotation.z = p > .6 ? Math.sin(lt * 26) * .08 : 0;
  };
};

// ============================================================ 5.1 the other side (coin flip)
V.otherSide = c => {
  const { g, S, dur } = c, tx = S.txt;
  const rays = new THREE.Group(); for (let i = 0; i < 16; i++) { const m = lightCone('#fff1c0', 20, .9, .09); const pv = new THREE.Group(); pv.rotation.z = i / 16 * 6.28; m.rotation.z = Math.PI / 2; m.position.x = 10; pv.add(m); rays.add(pv); } place(rays, 0, .6, -3); g.add(rays);
  const coin = new THREE.Group(); const disc = mesh(new THREE.CylinderGeometry(2.0, 2.0, .35, 64), M('#F2B63C', { metal: 1, rough: .22, env: 1.4 })); disc.rotation.x = Math.PI / 2; coin.add(disc);
  const rim = mesh(new THREE.TorusGeometry(1.95, .12, 16, 64), M('#FFD66B', { metal: 1, rough: .2 })); rim.position.z = .17; coin.add(rim); const rim2 = rim.clone(); rim2.position.z = -.17; coin.add(rim2);
  const fA = new THREE.Group(); const dA = mesh(new THREE.CircleGeometry(1.72, 48), new THREE.MeshStandardMaterial({ color: col('#2f3350'), roughness: .5 })); fA.add(dA); const cl = P.cloud('#8A90B5'); cl.scale.setScalar(.85); cl.position.y = .2; fA.add(cl); const bl = P.bolt(); bl.scale.setScalar(.5); bl.position.set(.2, -.7, .1); fA.add(bl); fA.position.z = .19; coin.add(fA);
  const fB = new THREE.Group(); const dB = mesh(new THREE.CircleGeometry(1.72, 48), new THREE.MeshStandardMaterial({ color: col('#4cb8ff'), roughness: .4 })); fB.add(dB); const sn = P.sun(.6); fB.add(sn); fB.rotation.y = Math.PI; fB.position.z = -.19; coin.add(fB);
  place(coin, 0, .9, 0, .8); g.add(coin);
  const t = words3d(tx.main, { h: 1.5, size: 170, fill: '#ffffff', outline: '#1b2a6b', depth: '#5a6ab0', layers: 10 }); fitW(t, 9); place(t, 0, -1.3, .8); g.add(t);
  const fl = dur * .3; c.cue(.2, 'whoosh'); c.cue(.45, 'coinflip'); c.cue(dur * .55, 'sparkle');
  c.camera([{ t: 0, p: [0, -1.5, 13], l: [0, .6, 0], f: 36 }, { t: 1, p: [0, .6, 10.5], l: [0, .3, 0], f: 31 }]);
  return lt => {
    rays.rotation.z = lt * .2; const p = seg(lt, .15, fl + .9), ang = E.out3(p) * Math.PI * 5; coin.rotation.x = 0; coin.rotation.y = ang; coin.position.y = .9 + Math.sin(clamp(p) * Math.PI) * 1.2; sn.userData.rays.rotation.z = lt * .5;
    popWords(t, lt, fl + .5, .2, .55);
  };
};

// ============================================================ 5.2 youth + bull market
V.youthBull = c => {
  const { g, S, dur } = c, tx = S.txt;
  const me = person(Object.assign({ mood: 'grin' }, PEOPLE.youth, { headphones: true, earphones: false })); place(me, -4.6, FY, 0, 1.05); me.rotation.y = .4; g.add(me);
  const nm = pillL(tx.name, { bg: '#4CC9F0', fill: '#02283a' }); place(nm, -4.6, 1.65, .3); g.add(nm);
  const card = P.glassCard(6.4, 3.8, { color: '#3DDC97', opacity: .12, edge: '#3DDC97', edgeOp: .8 }); place(card, 2.4, 1.0, -.5); g.add(card);
  const chart = P.chart({ color: '#3DDC97', w: 4.6, h: 2.2, pts: [.9, .8, .84, .66, .7, .5, .52, .3, .34, .1] }); chart.position.set(0, -.05, .2); card.add(chart);
  const up = label('▲ +24%', { h: .6, size: 110, fill: '#3DDC97', font: 'en', gain: 1.3 }); up.position.set(-1.6, 1.55, .3); card.add(up);
  const rk = P.rocket(); place(rk, 5.4, -1.0, .6, .75); rk.rotation.z = -.35; g.add(rk);
  const bub = P.thought(5.0, 2.2); place(bub, 1.2, -1.2, 1.1, .8); g.add(bub);
  const b1 = label(tx.b1, { h: .5, size: 100, fill: '#1d0f4a', gain: 1 }); b1.position.set(0, .22, .45); bub.add(b1); const b2 = label(tx.b2, { h: .62, size: 120, fill: '#E5384F', gain: 1 }); b2.position.set(0, -.42, .45); bub.add(b2);
  c.cue(.15, 'whoosh'); c.cue(.6, 'riser', .6); c.cue(dur * .55, 'pop'); c.cue(dur * .6, 'whoosh');
  c.camera([{ t: 0, p: [-3, .6, 13.5], l: [-.5, .3, 0], f: 33 }, { t: 1, p: [1.2, 1.0, 11.2], l: [1, .4, 0], f: 32, r: -1 }]);
  return lt => {
    me.idle(lt, .5); pop(me, lt, .05, { d: .5 }); rise(nm, lt, .2, { dy: .5 }); rise(card, lt, .3, { dx: 1.5, dy: 0 }); chart.setProgress(E.inOut(seg(lt, .6, dur * .7)));
    pop(rk, lt, dur * .4, { big: true }); rk.position.y = -1.0 + 3.4 * E.in2(seg(lt, dur * .45, dur)); rk.userData.fire.scale.y = 1 + Math.sin(lt * 40) * .15;
    pop(bub, lt, dur * .55, { big: true }); bub.position.y = -1.2 + bob(lt, .08, .6);
  };
};

// ============================================================ 5.3 two different worlds
V.twoWorlds = c => {
  const { g, S, dur } = c, tx = S.txt;
  const L_ = new THREE.Group(), R_ = new THREE.Group(); place(L_, -3.6, 0, 0); place(R_, 3.6, 0, 0); g.add(L_, R_);
  L_.add(stage(3.2, '#262040')); R_.add(stage(3.2, '#2fa4d6'));
  const cl = P.cloud('#59608A'); cl.position.set(0, 2.1, -1.2); cl.scale.setScalar(1.1); L_.add(cl); const bolt = P.bolt(); bolt.position.set(.2, 1.1, -.9); bolt.scale.setScalar(.7); L_.add(bolt);
  const sn = P.sun(.7); sn.position.set(-1.4, 2.3, -1.2); R_.add(sn); const cl2 = P.cloud('#ffffff'); cl2.position.set(1.4, 2.0, -1.4); cl2.scale.setScalar(.7); R_.add(cl2);
  const dad = person(Object.assign({ mood: 'worry' }, PEOPLE.dad)); dad.position.set(0, FY, .2); dad.scale.setScalar(1.0); L_.add(dad); const fr = person(Object.assign({ mood: 'grin' }, PEOPLE.youth)); fr.position.set(0, FY, .2); fr.scale.setScalar(1.0); R_.add(fr);
  const lp = pillL(tx.l, { bg: '#E9C58B', fill: '#2a1b00', h: .66, size: 100 }); lp.position.set(0, -1.9, 1.3); L_.add(lp); const rp = pillL(tx.r, { bg: '#FFE08A', fill: '#2a1b00', h: .66, size: 100 }); rp.position.set(0, -1.9, 1.3); R_.add(rp);
  const neq = group(mesh(new THREE.CylinderGeometry(.75, .75, .3, 40), M('#FFC857', { metal: .4 })), label('≠', { h: 1.0, size: 190, fill: '#2a1b00', font: 'en', gain: 1 })); neq.children[0].rotation.x = Math.PI / 2; neq.children[1].position.z = .17; place(neq, 0, .6, 1.2); g.add(neq);
  c.cue(.1, 'whoosh'); c.cue(dur * .3, 'whoosh'); c.cue(dur * .6, 'pop'); c.cue(dur * .6 + .05, 'ding', .7);
  c.camera([{ t: 0, p: [-5, 1.2, 14], l: [-2, .4, 0], f: 34 }, { t: .5, p: [0, 1.0, 12.5], l: [0, .4, 0], f: 33 }, { t: 1, p: [5, 1.2, 14], l: [2, .4, 0], f: 34 }]);
  return lt => {
    rise(L_, lt, .05, { dx: -2.5, dy: 0, d: .6 }); rise(R_, lt, dur * .3, { dx: 2.5, dy: 0, d: .6 }); dad.idle(lt); fr.idle(lt, 1); bolt.visible = Math.sin(lt * 9) > -.4; sn.userData.rays.rotation.z = lt * .5; pop(neq, lt, dur * .6, { big: true }); neq.rotation.y = bob(lt, .25, .3);
  };
};

// ============================================================ 5.4 both feel right
V.bothRight = c => {
  const { g, S, dur } = c, tx = S.txt;
  const top = pillL(tx.top, { h: .85, size: 125, bg: '#3DDC97', fill: '#04281b' }); place(top, 0, 2.65, .6); g.add(top);
  const mk = (x, lines, who, dly) => { const gr = new THREE.Group(); const p = person(Object.assign({ mood: 'smile' }, who)); p.position.set(0, FY, 0); p.scale.setScalar(.95); gr.add(p); const th = P.thought(5.0, 2.1); th.position.set(0, .35, .6); gr.add(th); const a = label(lines[0], { h: .5, size: 100, fill: '#1d0f4a', gain: 1 }); a.position.set(0, .22, .45); th.add(a); const b = label(lines[1], { h: .62, size: 120, fill: '#0E8F5E', gain: 1 }); b.position.set(0, -.38, .45); th.add(b); const ck = P.check(.55); ck.position.set(2.4, .9, .6); gr.add(ck); place(gr, x, 0, 0); g.add(gr); gr.userData = Object.assign(gr.userData, { p, th, ck }); return gr; };
  const A_ = mk(-3.7, tx.a, PEOPLE.dad), B_ = mk(3.7, tx.b, PEOPLE.youth);
  c.cue(.1, 'pop'); c.cue(.8, 'ding'); c.cue(dur * .5, 'pop'); c.cue(dur * .5 + .7, 'ding');
  c.camera([{ t: 0, p: [-2.5, .9, 13], l: [-1.5, .2, 0], f: 33 }, { t: 1, p: [2.5, .9, 13], l: [1.5, .2, 0], f: 33 }]);
  return lt => {
    rise(top, lt, .05, { dy: .5 }); [A_, B_].forEach((o, i) => { const t0 = i ? dur * .45 : .15; pop(o, lt, t0, { big: true }); o.userData.p.idle(lt, i); pop(o.userData.ck, lt, t0 + .6, { big: true }); o.userData.th.position.y = .35 + bob(lt, .08, .5, i); });
  };
};

// ============================================================ 5.5 their logic
V.logicGears = c => {
  const { g, S, dur } = c, tx = S.txt;
  const gs = [[P.gear(1.1, 12, '#8B9BE0', .5), -2.4, .5, 1], [P.gear(.8, 9, '#FFC857', .5), -.15, 1.5, -1.33], [P.gear(.62, 7, '#4CC9F0', .5), 1.1, -.1, 1.7]].map(([o, x, y, sp]) => { place(o, x, y, 0); g.add(o); o.userData.sp = sp; return o; });
  const bulb = P.bulb(); place(bulb, 4.4, .6, 0, 1.0); g.add(bulb);
  const t = words3d(tx.main, { h: 1.4, size: 170, fill: '#FFD66B', outline: '#2a1450', depth: '#a86a08', layers: 10 }); fitW(t, 10); place(t, 0, -1.3, .6); g.add(t);
  c.cue(.1, 'gear', .7); c.cue(dur * .5, 'switch'); c.cue(dur * .5 + .1, 'ding');
  c.camera([{ t: 0, p: [-2, 1.2, 12.5], l: [0, .3, 0], f: 33 }, { t: 1, p: [1.5, .6, 10.5], l: [.8, .3, 0], f: 31 }]);
  return lt => {
    gs.forEach((o, i) => { pop(o, lt, .1 + i * .2, { big: true }); o.rotation.z = lt * .8 * o.userData.sp; });
    pop(bulb, lt, dur * .45, { d: .5 }); bulb.setOn(E.out3(seg(lt, dur * .5, dur * .5 + .4))); popWords(t, lt, dur * .4, .2, .55);
  };
};
