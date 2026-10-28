// 3D asset kit: text, materials, props and toy-style characters. Units: 1 unit ~ 1/6 of the frame height.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { clamp, lerp, seg, E, bob, rng } from './core3d.js';

await Promise.all(['700 40px TeSans', '400 40px TeSans', '700 40px TeSerif', '600 40px Pop', '700 40px Pop', '400 40px Pop'].map(f => document.fonts.load(f, 'అఆఇ ₹ABC')));
await document.fonts.ready;

export const col = c => new THREE.Color(c);
// ------------------------------------------------------------------ materials
export function M(color, o = {}) {
  return new THREE.MeshPhysicalMaterial({
    color: col(color), roughness: o.rough ?? .38, metalness: o.metal ?? 0, clearcoat: o.coat ?? .55, clearcoatRoughness: o.coatRough ?? .18,
    emissive: col(o.emissive ?? '#000'), emissiveIntensity: o.ei ?? 1, transparent: o.opacity != null && o.opacity < 1, opacity: o.opacity ?? 1,
    envMapIntensity: o.env ?? 1, side: o.side ?? THREE.FrontSide, flatShading: !!o.flat,
  });
}
export const glow = (color, k = 1.6) => new THREE.MeshBasicMaterial({ color: col(color).multiplyScalar(k), toneMapped: true });
export function mesh(geo, mat, o = {}) { const m = new THREE.Mesh(geo, mat); m.castShadow = o.shadow !== false; m.receiveShadow = !!o.receive; return m; }
export const group = (...kids) => { const g = new THREE.Group(); kids.forEach(k => k && g.add(k)); return g; };
export function at(o, x = 0, y = 0, z = 0, s = 1) { o.position.set(x, y, z); o.scale.setScalar(s); o.userData.base = { x, y, z, s }; return o; }
export const xyz = (o, x, y, z) => { o.position.set(x, y, z); return o; };

// ------------------------------------------------------------------ canvas text / labels
const FONTS = { te: "'TeSans','Pop','Noto Color Emoji',sans-serif", serif: "'TeSerif','TeSans','Pop',serif", en: "'Pop','TeSans','Noto Color Emoji',sans-serif" };
function roundRect(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
function drawText(str, o) {
  const size = o.size || 140, padX = o.padX ?? 28, padY = o.padY ?? 18, font = FONTS[o.font || 'te'], weight = o.weight || 700;
  const lines = Array.isArray(str) ? str : [str];
  const meas = document.createElement('canvas').getContext('2d'); meas.font = `${weight} ${size}px ${font}`;
  const lh = size * (o.lh || 1.55), tw = Math.max(...lines.map(l => meas.measureText(l).width));
  const sw = o.stroke ? (o.sw || size * .1) : 0;
  const w = Math.ceil(tw + padX * 2 + sw * 2), h = Math.ceil(lh * lines.length + padY * 2 + sw);
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  if (o.bg) { g.fillStyle = o.bg; roundRect(g, 0, 0, w, h, o.rx ?? h / 2); g.fill(); if (o.bgStroke) { g.strokeStyle = o.bgStroke; g.lineWidth = o.bgSw || 4; g.stroke(); } }
  g.font = `${weight} ${size}px ${font}`; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.lineJoin = 'round';
  lines.forEach((l, i) => {
    const y = padY + sw / 2 + lh * i + size * 1.12;
    if (o.glow) { g.shadowColor = o.glow; g.shadowBlur = size * .22; }
    if (o.stroke) { g.strokeStyle = o.stroke; g.lineWidth = sw; g.strokeText(l, w / 2, y); }
    g.shadowBlur = 0;
    g.fillStyle = o.fill || '#fff'; g.fillText(l, w / 2, y);
  });
  return c;
}
function texOf(canvas) { const t = new THREE.CanvasTexture(canvas); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; return t; }
// flat label / text quad; h = world height of the whole quad
export function label(str, o = {}) {
  const c = drawText(str, o), h = o.h || .6, w = h * c.width / c.height;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: texOf(c), transparent: true, depthWrite: false, toneMapped: o.tone ?? false }));
  m.material.color.setScalar(o.gain ?? 1.25); m.userData.w = w; m.userData.h = h; m.renderOrder = o.order ?? 5; return m;
}
// chunky pseudo-extruded 3D text: stacked silhouette layers behind a bright front face
export function text3d(str, o = {}) {
  const g = new THREE.Group(), h = o.h || .8, layers = o.layers ?? 9, step = o.step ?? .018;
  const front = drawText(str, Object.assign({ stroke: o.outline || '#1b0f4a' }, o));
  const back = drawText(str, Object.assign({}, o, { fill: o.depth || '#8a5a00', stroke: o.depth || '#8a5a00', sw: o.sw || (o.size || 140) * .1, glow: null }));
  const w = h * front.width / front.height;
  const tf = texOf(front), tb = texOf(back);
  for (let i = layers; i >= 1; i--) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tb, transparent: true, depthWrite: false, toneMapped: false }));
    m.material.color.setScalar(1 - i / layers * .5); m.position.z = -i * step; m.renderOrder = 4; g.add(m);
  }
  const f = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tf, transparent: true, depthWrite: false, toneMapped: false }));
  f.material.color.setScalar(o.gain ?? 1.3); f.renderOrder = 6; g.add(f); g.userData.w = w; g.userData.h = h; g.userData.front = f; return g;
}
// row of separately animatable words (each word a 3D text group)
export function words3d(str, o = {}) {
  const g = new THREE.Group(), ws = str.split(' ').filter(Boolean), h = o.h || .8, items = [];
  ws.forEach(w => items.push(text3d(w, Object.assign({}, o, { h }))));
  const gap = (o.gap ?? .22) * h, total = items.reduce((a, b) => a + b.userData.w, 0) + gap * (items.length - 1);
  let x = -total / 2; items.forEach(it => { it.position.x = x + it.userData.w / 2; it.userData.bx = it.position.x; g.add(it); x += it.userData.w + gap; });
  g.userData.items = items; g.userData.w = total; return g;
}
// fit a group to a max world width
export function fitW(g, maxW) { const k = Math.min(1, maxW / g.userData.w); g.scale.setScalar(k); return g; }

// ------------------------------------------------------------------ animation helpers (3D)
export function pop(o, lt, t0, p = {}) {
  const b = o.userData.base || { x: o.position.x, y: o.position.y, z: o.position.z, s: o.scale.x }; o.userData.base = b;
  const d = p.d || .55, k = seg(lt, t0, t0 + d);
  if (k <= 0) { o.visible = false; return o; }
  o.visible = true; const s = (p.s ?? b.s) * (p.big ? E.backBig(k) : E.back(k));
  o.scale.setScalar(Math.max(1e-3, s)); if (p.x != null) o.position.x = p.x; if (p.y != null) o.position.y = p.y; if (p.z != null) o.position.z = p.z;
  if (p.ry != null) o.rotation.y = p.ry; return o;
}
export function rise(o, lt, t0, p = {}) {
  const b = o.userData.base || { x: o.position.x, y: o.position.y, z: o.position.z, s: o.scale.x }; o.userData.base = b;
  const d = p.d || .6, k = seg(lt, t0, t0 + d), e = E.out3(k);
  if (k <= 0) { o.visible = false; return o; }
  o.visible = true; o.position.set(b.x + (p.dx || 0) * (1 - e), b.y + (p.dy ?? -.8) * (1 - e), b.z + (p.dz || 0) * (1 - e)); return o;
}
export function showAt(o, lt, t0) { o.visible = lt >= t0; return o; }
export function setOpacity(o, a) { o.traverse(n => { if (n.material) { const ms = Array.isArray(n.material) ? n.material : [n.material]; ms.forEach(m => { if (m.userData.o0 == null) m.userData.o0 = m.opacity; m.transparent = true; m.opacity = m.userData.o0 * a; }); } }); }
export function popWords(wg, lt, t0, stagger = .18, d = .55) { wg.userData.items.forEach((it, i) => { const k = seg(lt, t0 + i * stagger, t0 + i * stagger + d); it.visible = k > 0; const s = E.backBig(k); it.scale.setScalar(Math.max(1e-3, s)); it.position.y = (1 - E.out3(k)) * -.35; }); }

// ------------------------------------------------------------------ geometry helpers
function shapeGeo(shape, depth = .28, bevel = .05) { const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 4, curveSegments: 16 }); g.center(); return g; }
const poly = (pts) => { const s = new THREE.Shape(); pts.forEach(([x, y], i) => i ? s.lineTo(x, y) : s.moveTo(x, y)); s.closePath(); return s; };
export const rbox = (w, h, d, r = .08, seg_ = 4) => new RoundedBoxGeometry(w, h, d, seg_, Math.min(r, Math.min(w, h, d) / 2 - 1e-3));

// ------------------------------------------------------------------ props
export const P = {};
P.coin = (r = .5, sym = '₹') => {
  const g = new THREE.Group(); const gold = M('#F2B63C', { metal: 1, rough: .22, coat: .4, env: 1.4 });
  const body = mesh(new THREE.CylinderGeometry(r, r, r * .16, 56), gold); body.rotation.x = Math.PI / 2; g.add(body);
  const rim = mesh(new THREE.TorusGeometry(r * .96, r * .06, 12, 56), M('#FFD66B', { metal: 1, rough: .18 })); rim.position.z = r * .08; g.add(rim); const rim2 = rim.clone(); rim2.position.z = -r * .08; g.add(rim2);
  const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d'); x.fillStyle = '#F2B63C'; x.fillRect(0, 0, 256, 256); x.fillStyle = '#7a4a00'; x.font = `700 150px ${FONTS.en}`; x.textAlign = 'center'; x.fillText(sym, 128, 175); x.strokeStyle = '#a76a08'; x.lineWidth = 6; x.beginPath(); x.arc(128, 128, 98, 0, 7); x.stroke();
  const t = texOf(c); const face = new THREE.Mesh(new THREE.CircleGeometry(r * .9, 48), new THREE.MeshStandardMaterial({ map: t, metalness: .85, roughness: .3, envMapIntensity: 1.3 })); face.position.z = r * .085; g.add(face);
  const f2 = face.clone(); f2.position.z = -r * .085; f2.rotation.y = Math.PI; g.add(f2); return g;
};
P.bank = () => {
  const g = new THREE.Group(), stone = M('#F2F0FF', { rough: .45, coat: .3 }), gold = M('#F2B63C', { metal: .9, rough: .25 });
  const roof = mesh(shapeGeo(poly([[-2.1, 0], [0, 1.2], [2.1, 0]]), .9, .04), gold); roof.position.y = 1.65; g.add(roof);
  g.add(at(mesh(rbox(4.5, .22, 1.15, .05), stone), 0, 1.0, 0));
  for (let i = -2; i <= 2; i++) { const c = mesh(new THREE.CylinderGeometry(.2, .23, 1.55, 24), stone); c.position.set(i * .85, .12, 0); g.add(c); }
  g.add(at(mesh(rbox(4.7, .24, 1.3, .05), stone), 0, -.78, 0)); g.add(at(mesh(rbox(5.1, .24, 1.5, .05), M('#c9cfee')), 0, -1.0, 0));
  const c = P.coin(.3); c.position.set(0, 1.62, .55); g.add(c); g.userData.coin = c; return g;
};
P.piggy = () => {
  const g = new THREE.Group(), pink = M('#FF9DB8', { rough: .35 }), dark = M('#C8456A');
  const body = mesh(new THREE.SphereGeometry(1, 40, 28), pink); body.scale.set(1.25, 1, .95); g.add(body);
  const snout = mesh(new THREE.CylinderGeometry(.34, .38, .34, 24), M('#F58AA5')); snout.rotation.z = Math.PI / 2; snout.position.set(-1.25, -.08, 0); g.add(snout);
  [-.14, .14].forEach(z => { const n = mesh(new THREE.SphereGeometry(.05, 12, 8), dark); n.position.set(-1.42, -.08, z); g.add(n); });
  [-.38, .38].forEach(z => { const e = mesh(new THREE.ConeGeometry(.24, .4, 4), M('#F58AA5')); e.position.set(-.6, .92, z); e.rotation.z = .35; g.add(e); const eye = mesh(new THREE.SphereGeometry(.09, 12, 8), M('#241633')); eye.position.set(-.82, .32, z * .95 * 1.25); g.add(eye); });
  [[-.65, .42], [-.65, -.42], [.6, .42], [.6, -.42]].forEach(([x, z]) => { const l = mesh(new THREE.CylinderGeometry(.2, .22, .55, 14), M('#F58AA5')); l.position.set(x, -.95, z); g.add(l); });
  const tail = mesh(new THREE.TorusGeometry(.2, .05, 8, 20, 4.4), pink); tail.position.set(1.28, .15, 0); g.add(tail);
  const slot = mesh(new THREE.BoxGeometry(.7, .06, .12), dark); slot.position.set(0, .98, 0); g.add(slot);
  const c = P.coin(.3); c.position.set(0, 1.7, 0); c.rotation.y = Math.PI / 2; g.add(c); g.userData.coin = c; return g;
};
P.calendar = (label1 = 'EMI', label2 = '₹ JAN', color = '#E5384F') => {
  const g = new THREE.Group(); g.add(mesh(rbox(2.0, 2.2, .24, .14), M('#FFFFFF', { rough: .5 })));
  const head = mesh(rbox(2.0, .6, .26, .14), M(color)); head.position.y = .8; g.add(head);
  [-.55, .55].forEach(x => { const r = mesh(new THREE.CylinderGeometry(.07, .07, .4, 12), M('#333')); r.position.set(x, 1.12, 0); g.add(r); });
  const t = label(label1, { h: .8, size: 130, fill: color, font: 'en', gain: 1, tone: false }); t.position.set(0, -.05, .13); g.add(t);
  const t2 = label(label2, { h: .38, size: 100, fill: '#8A93BE', font: 'en', weight: 600, gain: 1 }); t2.position.set(0, -.72, .13); g.add(t2); return g;
};
P.bag = (c1 = '#FF5A5F', c2 = '#E5384F', mark = '%') => {
  const g = new THREE.Group(); const b = mesh(rbox(1.35, 1.6, .7, .12), M(c1)); g.add(b);
  const top = mesh(rbox(1.38, .36, .72, .1), M(c2)); top.position.y = .62; g.add(top);
  [-.3, .3].forEach(x => { const h = mesh(new THREE.TorusGeometry(.32, .055, 10, 24, Math.PI), M(c2)); h.position.set(x * .8, .8, 0); h.rotation.x = 0; g.add(h); });
  const t = label(mark, { h: .75, size: 160, fill: '#fff', font: 'en', gain: 1 }); t.position.set(0, -.15, .36); g.add(t); return g;
};
P.phone = () => { const g = new THREE.Group(); g.add(mesh(rbox(1.0, 2.0, .14, .14), M('#1c2038', { rough: .25 }))); const s = mesh(new THREE.PlaneGeometry(.86, 1.82), new THREE.MeshBasicMaterial({ color: col('#4a62c8') })); s.position.z = .075; g.add(s); return g; };
P.chart = (o = {}) => {
  const g = new THREE.Group(), w = o.w || 4.2, h = o.h || 2.4, c = o.color || '#3DDC97', pts = o.pts || [.9, .78, .84, .6, .66, .4, .46, .18, .1];
  const panel = mesh(rbox(w + .5, h + .5, .12, .12), M('#ffffff', { opacity: .1, rough: .2, coat: 1 }), { shadow: false }); panel.material.transparent = true; g.add(panel);
  const frame = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w + .5, h + .5, .12)), new THREE.LineBasicMaterial({ color: col('#ffffff'), transparent: true, opacity: .35 })); g.add(frame);
  for (let i = 1; i < 4; i++) { const l = mesh(new THREE.BoxGeometry(w, .01, .01), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .16 }), { shadow: false }); l.position.set(0, -h / 2 + h * i / 4, .07); g.add(l); }
  const P3 = pts.map((y, i) => new THREE.Vector3(-w / 2 + w * i / (pts.length - 1), -h / 2 + h * (1 - y), .12));
  const curve = new THREE.CatmullRomCurve3(P3, false, 'catmullrom', .35);
  const tube = new THREE.TubeGeometry(curve, 160, .065, 10, false); const line = new THREE.Mesh(tube, glow(c, 1.7)); g.add(line);
  const tip = mesh(new THREE.SphereGeometry(.15, 20, 14), glow('#ffffff', 1.4)); g.add(tip);
  const tl = new THREE.PointLight(col(c), 6, 4, 2); tip.add(tl);
  const idxCount = tube.index.count;
  g.setProgress = k => { k = clamp(k); line.geometry.setDrawRange(0, Math.floor(idxCount * k / 3) * 3); const p = curve.getPoint(clamp(k, 0, .999)); tip.position.copy(p); tip.visible = k > .01; };
  g.setProgress(0); g.userData.curve = curve; return g;
};
P.globe = (r = 1.5) => {
  const g = new THREE.Group(); const c = document.createElement('canvas'); c.width = 1024; c.height = 512; const x = c.getContext('2d');
  const gr = x.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, '#2b7cf0'); gr.addColorStop(1, '#1346b8'); x.fillStyle = gr; x.fillRect(0, 0, 1024, 512);
  x.strokeStyle = 'rgba(255,255,255,.14)'; x.lineWidth = 2; for (let i = 0; i < 24; i++) { x.beginPath(); x.moveTo(i * 43, 0); x.lineTo(i * 43, 512); x.stroke(); } for (let i = 0; i < 12; i++) { x.beginPath(); x.moveTo(0, i * 43); x.lineTo(1024, i * 43); x.stroke(); }
  x.fillStyle = '#4CCB86'; const rr = rng(4);
  const blob = (cx, cy, rx, ry, n = 7) => { x.beginPath(); for (let i = 0; i <= n; i++) { const a = i / n * 6.28, k = .72 + rr() * .5; const px = cx + Math.cos(a) * rx * k, py = cy + Math.sin(a) * ry * k; i ? x.lineTo(px, py) : x.moveTo(px, py); } x.closePath(); x.fill(); };
  [[250, 190, 110, 90], [330, 330, 60, 90], [560, 170, 90, 70], [600, 300, 80, 100], [780, 190, 120, 80], [860, 360, 60, 40], [130, 380, 50, 30], [520, 450, 160, 30]].forEach(a => { blob(...a); blob(a[0] + 30, a[1] - 20, a[2] * .6, a[3] * .6); });
  const tex = texOf(c); tex.wrapS = THREE.RepeatWrapping;
  const s = mesh(new THREE.SphereGeometry(r, 64, 40), new THREE.MeshPhysicalMaterial({ map: tex, roughness: .5, clearcoat: 1, clearcoatRoughness: .15, metalness: .05 })); g.add(s); g.userData.sphere = s;
  const atm = new THREE.Mesh(new THREE.SphereGeometry(r * 1.12, 48, 32), new THREE.ShaderMaterial({ transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: {}, vertexShader: 'varying vec3 vN; void main(){ vN = normalize(normalMatrix*normal); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }', fragmentShader: 'varying vec3 vN; void main(){ float i = pow(.72 - dot(vN, vec3(0.,0.,1.)), 3.); gl_FragColor = vec4(.35,.7,1.,1.)*i*1.4; }' })); g.add(atm);
  g.spin = lt => { s.rotation.y = lt * .35; }; return g;
};
P.magnifier = (r = .8) => {
  const g = new THREE.Group(); const ring = mesh(new THREE.TorusGeometry(r, r * .11, 20, 56), M('#F2F6FF', { metal: .6, rough: .2 })); g.add(ring);
  const glass = new THREE.Mesh(new THREE.CircleGeometry(r * .96, 48), new THREE.MeshPhysicalMaterial({ color: col('#bfe6ff'), transparent: true, opacity: .22, roughness: .05, clearcoat: 1 })); glass.position.z = .0; g.add(glass);
  const h = mesh(new THREE.CylinderGeometry(r * .11, r * .14, r * 1.1, 16), M('#C98412', { metal: .5 })); h.position.set(r * .98, -r * .98, 0); h.rotation.z = Math.PI / 4; g.add(h);
  const sh = new THREE.Mesh(new THREE.TorusGeometry(r * .66, r * .03, 8, 24, 1.4), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .7 })); sh.rotation.z = 1.9; sh.position.z = .02; g.add(sh); return g;
};
P.gear = (r = .8, n = 10, color = '#9AA6D6', depth = .35) => {
  const s = new THREE.Shape(); const ro = r * 1.2, ri = r;
  for (let i = 0; i < n * 4; i++) { const a = i / (n * 4) * Math.PI * 2, rr = (i % 4 < 2) ? ro : ri; const px = Math.cos(a) * rr, py = Math.sin(a) * rr; i ? s.lineTo(px, py) : s.moveTo(px, py); }
  s.closePath(); const hole = new THREE.Path(); hole.absarc(0, 0, r * .42, 0, Math.PI * 2, true); s.holes.push(hole);
  return mesh(shapeGeo(s, depth, .04), M(color, { metal: .75, rough: .3, env: 1.3 }));
};
P.puzzle = (color = '#FF8A3D', sides = [0, 1, 0, 0], s = 1) => { // sides: top,right,bottom,left : 1 knob out, -1 notch in
  const a = 1, k = .3, sh = new THREE.Shape(); sh.moveTo(-a, -a);
  const edge = (x0, y0, x1, y1, d) => { if (!d) { sh.lineTo(x1, y1); return; } const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy), nx = dy / L * d, ny = -dx / L * d, ux = dx / L, uy = dy / L; sh.lineTo(mx - ux * .2, my - uy * .2); sh.bezierCurveTo(mx - ux * .2 + nx * k, my - uy * .2 + ny * k, mx - ux * .42 + nx * k * 1.9, my - uy * .42 + ny * k * 1.9, mx + nx * k * 1.9, my + ny * k * 1.9); sh.bezierCurveTo(mx + ux * .42 + nx * k * 1.9, my + uy * .42 + ny * k * 1.9, mx + ux * .2 + nx * k, my + uy * .2 + ny * k, mx + ux * .2, my + uy * .2); sh.lineTo(x1, y1); };
  edge(-a, -a, a, -a, -sides[2] || 0); edge(a, -a, a, a, -sides[1] || 0); edge(a, a, -a, a, -sides[0] || 0); edge(-a, a, -a, -a, -sides[3] || 0);
  const m = mesh(shapeGeo(sh, .5, .06), M(color, { rough: .3 })); m.scale.setScalar(s); return m;
};
P.heart = (color = '#FF4D6D') => { const s = new THREE.Shape(); s.moveTo(0, -.9); s.bezierCurveTo(-1.5, .1, -.9, 1.1, 0, .5); s.bezierCurveTo(.9, 1.1, 1.5, .1, 0, -.9); const m = mesh(shapeGeo(s, .35, .1), M(color, { rough: .22, coat: 1 })); m.scale.setScalar(.8); return m; };
P.star = (r = .8, n = 5, inner = .45, color = '#FFC857') => { const pts = []; for (let i = 0; i < n * 2; i++) { const a = -Math.PI / 2 + i / (n * 2) * Math.PI * 2, rr = i % 2 ? r * inner : r; pts.push([Math.cos(a) * rr, Math.sin(a) * rr]); } return mesh(shapeGeo(poly(pts), .3, .06), M(color, { metal: .5, rough: .25 })); };
P.bolt = (color = '#FFD66B') => mesh(shapeGeo(poly([[.3, 1], [-.55, -.1], [-.08, -.1], [-.3, -1], [.6, .2], [.1, .2]]), .25, .05), glow(color, 1.3));
P.arrow = (len = 1.6, color = '#FFC857') => mesh(shapeGeo(poly([[-len / 2, -.18], [len / 2 - .5, -.18], [len / 2 - .5, -.5], [len / 2, 0], [len / 2 - .5, .5], [len / 2 - .5, .18], [-len / 2, .18]]), .22, .05), M(color, { metal: .3, rough: .3 }));
P.check = (r = .55) => { const g = new THREE.Group(); g.add(mesh(new THREE.CylinderGeometry(r, r, .22, 40), M('#2FD08A', { rough: .25 }), {})); g.children[0].rotation.x = Math.PI / 2; const a = mesh(rbox(r * .38, r * 1.0, .14, .06), M('#fff')); a.position.set(r * .22, -r * .02, .14); a.rotation.z = -.78; const b = mesh(rbox(r * .38, r * .6, .14, .06), M('#fff')); b.position.set(-r * .28, -r * .14, .14); b.rotation.z = .78; g.add(a, b); return g; };
P.cross = (r = .55) => { const g = new THREE.Group(); const d = mesh(new THREE.CylinderGeometry(r, r, .22, 40), M('#F0455A', { rough: .25 })); d.rotation.x = Math.PI / 2; g.add(d); [.785, -.785].forEach(a => { const b = mesh(rbox(r * 1.15, r * .26, .14, .06), M('#fff')); b.position.z = .14; b.rotation.z = a; g.add(b); }); return g; };
P.warning = () => { const g = new THREE.Group(); const t = mesh(shapeGeo(poly([[0, 1], [1.05, -.8], [-1.05, -.8]]), .3, .09), M('#FFC857')); g.add(t); const e = label('!', { h: 1, size: 200, fill: '#7A4A00', font: 'en', gain: 1 }); e.position.set(0, -.12, .26); g.add(e); return g; };
P.wallet = (color = '#8B5CF6') => { const g = new THREE.Group(); g.add(mesh(rbox(2.2, 1.5, .5, .16), M(color))); const f = mesh(rbox(2.2, .5, .54, .16), M('#6C3BE8')); f.position.y = .5; g.add(f); const c = mesh(rbox(.7, .5, .56, .16), M('#B79CFF')); c.position.set(.8, -.15, 0); g.add(c); const b = mesh(new THREE.SphereGeometry(.1, 16, 12), M('#fff')); b.position.set(.8, -.15, .3); g.add(b); return g; };
P.lock = () => { const g = new THREE.Group(); g.add(mesh(rbox(.9, .75, .35, .1), M('#FFC857', { metal: .6 }))); const sh = mesh(new THREE.TorusGeometry(.26, .07, 12, 24, Math.PI), M('#E9A02A', { metal: .8 })); sh.position.y = .38; g.add(sh); return g; };
P.cloud = (color = '#C9CFE8') => { const g = new THREE.Group(), m = M(color, { rough: .7, coat: .1 }); [[-.8, -.05, .55], [-.15, .3, .75], [.6, .05, .62], [1.15, -.12, .42], [-1.3, -.2, .38]].forEach(([x, y, r]) => { const s = mesh(new THREE.SphereGeometry(r, 24, 18), m); s.position.set(x, y, 0); s.scale.z = .8; g.add(s); }); const b = mesh(rbox(2.9, .5, .8, .24), m); b.position.set(0, -.35, 0); g.add(b); return g; };
P.sun = (r = .7) => { const g = new THREE.Group(), core = mesh(new THREE.SphereGeometry(r, 32, 24), glow('#FFD66B', 1.4)); g.add(core); const rays = new THREE.Group(); for (let i = 0; i < 12; i++) { const c = mesh(new THREE.ConeGeometry(.09, .5, 8), glow('#FFD66B', 1.2)); const a = i / 12 * 6.28; c.position.set(Math.cos(a) * (r + .45), Math.sin(a) * (r + .45), 0); c.rotation.z = a - Math.PI / 2; rays.add(c); } g.add(rays); g.userData.rays = rays; return g; };
P.flame = () => { const g = new THREE.Group(); const o = mesh(new THREE.ConeGeometry(.5, 1.5, 24), glow('#FF7A33', 1.2)); const i = mesh(new THREE.ConeGeometry(.28, .95, 24), glow('#FFE066', 1.4)); i.position.y = -.2; g.add(o, i); g.userData.o = o; return g; };
P.rocket = () => {
  const g = new THREE.Group(); const body = mesh(new THREE.CapsuleGeometry(.42, 1.3, 12, 24), M('#F2F4FF', { rough: .25, coat: 1 })); g.add(body);
  const nose = mesh(new THREE.ConeGeometry(.42, .75, 24), M('#FF5A5F')); nose.position.y = 1.35; g.add(nose);
  const w = mesh(new THREE.SphereGeometry(.2, 20, 14), M('#4C6FFF', { rough: .1 })); w.position.set(0, .25, .36); g.add(w);
  [-1, 1].forEach(s => { const f = mesh(shapeGeo(poly([[0, 0], [.5 * s, -.4], [0, -.9]]), .12, .03), M('#FF5A5F')); f.position.set(.46 * s, -.65, 0); g.add(f); });
  const fl = mesh(new THREE.ConeGeometry(.3, 1.0, 20), glow('#FF9A33', 1.4)); fl.rotation.x = Math.PI; fl.position.y = -1.55; g.add(fl); g.userData.fire = fl; return g;
};
P.tag = (text = '₹100', color = '#FF5A5F') => { const g = new THREE.Group(); const s = poly([[-1.2, -.5], [.55, -.5], [1.15, 0], [.55, .5], [-1.2, .5]]); g.add(mesh(shapeGeo(s, .18, .05), M(color))); const h = mesh(new THREE.CylinderGeometry(.09, .09, .22, 14), M('#222')); h.rotation.x = Math.PI / 2; h.position.set(.78, 0, 0); g.add(h); const t = label(text, { h: .62, size: 140, fill: '#fff', font: 'en', gain: 1 }); t.position.set(-.2, 0, .16); g.add(t); return g; };
P.bulb = () => {
  const g = new THREE.Group(); const glass = mesh(new THREE.SphereGeometry(.8, 40, 28), new THREE.MeshPhysicalMaterial({ color: col('#7a85a8'), roughness: .1, clearcoat: 1, transparent: true, opacity: .92 })); glass.position.y = .3; g.add(glass);
  const neck = mesh(new THREE.CylinderGeometry(.42, .3, .45, 24), M('#AAB4D0', { metal: .8, rough: .3 })); neck.position.y = -.5; g.add(neck);
  [-.82, -1.0].forEach((y, i) => { const b = mesh(new THREE.CylinderGeometry(.36 - i * .07, .36 - i * .07, .16, 24), M('#8791AD', { metal: .8 })); b.position.y = y; g.add(b); });
  const fil = mesh(new THREE.TorusGeometry(.2, .025, 8, 24), new THREE.MeshBasicMaterial({ color: col('#ffe9a0') })); fil.position.y = .15; g.add(fil);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex(), color: col('#FFD66B'), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); halo.scale.setScalar(6); halo.position.y = .3; g.add(halo);
  const pl = new THREE.PointLight(col('#FFD66B'), 0, 12, 2); pl.position.y = .3; g.add(pl);
  g.setOn = k => { glass.material.color.set('#7a85a8').lerp(col('#FFE066'), k); glass.material.emissive.set('#FFD23F'); glass.material.emissiveIntensity = k * 1.6; halo.material.opacity = k * .9; pl.intensity = k * 40; };
  g.setOn(0); return g;
};
P.thumb = (color = '#FFC857') => {
  const g = new THREE.Group(), m = M(color, { rough: .35 });
  const palm = mesh(rbox(1.5, 1.3, .8, .26), m); palm.position.set(.25, -.2, 0); g.add(palm);
  const th = mesh(new THREE.CapsuleGeometry(.24, .9, 8, 16), m); th.position.set(-.25, .75, 0); th.rotation.z = .28; g.add(th);
  [0, 1, 2].forEach(i => { const f = mesh(new THREE.CapsuleGeometry(.14, .5, 6, 12), m); f.rotation.z = Math.PI / 2; f.position.set(1.0, .12 - i * .3, .12 * (i % 2)); g.add(f); });
  const cuff = mesh(rbox(.55, 1.5, .9, .14), M('#4C6FFF')); cuff.position.set(-.85, -.3, 0); g.add(cuff); return g;
};
P.bell = (color = '#FFC857') => { const g = new THREE.Group(); const pr = [[.95, -.62], [.9, -.5], [.78, -.15], [.6, .25], [.42, .6], [.24, .88], [.1, 1.02], [0, 1.06]].map(([r, y]) => new THREE.Vector2(r, y)); const b = mesh(new THREE.LatheGeometry(pr, 40), M(color, { metal: .85, rough: .25, env: 1.3, side: THREE.DoubleSide })); g.add(b); const c = mesh(new THREE.SphereGeometry(.2, 16, 12), M('#E9A02A', { metal: .7 })); c.position.y = -.68; g.add(c); const t = mesh(new THREE.TorusGeometry(.12, .035, 8, 16), M(color, { metal: .8 })); t.position.y = 1.12; g.add(t); g.userData.pivot = b; return g; };
P.house = (roof = '#FF5A5F', wall = '#FFE8C2') => { const g = new THREE.Group(); g.add(at(mesh(rbox(2.2, 1.3, 1.6, .06), M(wall, { rough: .6 })), 0, 0, 0)); const r = mesh(shapeGeo(poly([[-1.5, 0], [0, 1], [1.5, 0]]), 1.8, .04), M(roof)); r.position.y = 1.15; g.add(r); const d = mesh(rbox(.45, .8, .1, .04), M('#B8764A')); d.position.set(0, -.25, .84); g.add(d); [-.7, .7].forEach(x => { const w = mesh(rbox(.45, .45, .08, .04), M('#8EC9FF', { rough: .1 })); w.position.set(x, .12, .83); g.add(w); }); return g; };
P.pin = (color = '#FF5A5F') => { const g = new THREE.Group(); const c = mesh(new THREE.ConeGeometry(.55, 1.3, 32), M(color)); c.rotation.x = Math.PI; c.position.y = -.45; g.add(c); const s = mesh(new THREE.SphereGeometry(.62, 32, 24), M(color)); s.position.y = .3; g.add(s); const h = mesh(new THREE.SphereGeometry(.24, 16, 12), M('#fff')); h.position.set(0, .3, .5); g.add(h); return g; };
P.eye = () => { const g = new THREE.Group(); const w = mesh(new THREE.SphereGeometry(.95, 40, 28), M('#ffffff', { rough: .2, coat: 1 })); w.scale.set(1.25, .8, .7); g.add(w); const ir = new THREE.Group(); const i = mesh(new THREE.CircleGeometry(.4, 32), M('#3F7BFF', { rough: .2 })); const p = mesh(new THREE.CircleGeometry(.18, 24), new THREE.MeshBasicMaterial({ color: 0x08081a })); p.position.z = .01; const h = mesh(new THREE.CircleGeometry(.07, 12), new THREE.MeshBasicMaterial({ color: 0xffffff })); h.position.set(.1, .12, .02); ir.add(i, p, h); ir.position.z = .66; g.add(ir); g.userData.iris = ir; return g; };
P.calculator = (display = '5 × 12') => { const g = new THREE.Group(); g.add(mesh(rbox(1.8, 2.5, .32, .16), M('#2A3050'))); const s = mesh(rbox(1.5, .6, .06, .06), M('#B9F3D6')); s.position.set(0, .8, .17); g.add(s); const t = label(display, { h: .5, size: 120, fill: '#0B6B4B', font: 'en', gain: 1 }); t.position.set(0, .8, .22); g.add(t); for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) { const b = mesh(rbox(.42, .32, .1, .06), M(c === 2 && r < 3 ? '#FFB84D' : '#5B6591')); b.position.set(-.5 + c * .5, .18 - r * .4, .18); g.add(b); } return g; };
P.polaroid = (emoji = '📷', bg = '#7FA8FF') => { const g = new THREE.Group(); g.add(mesh(rbox(1.7, 2.0, .06, .05), M('#ffffff', { rough: .6 }))); const f = mesh(new THREE.PlaneGeometry(1.4, 1.4), new THREE.MeshBasicMaterial({ color: col(bg) })); f.position.set(0, .15, .035); g.add(f); const e = label(emoji, { h: 1.0, size: 150, font: 'en', gain: 1 }); e.position.set(0, .15, .05); g.add(e); return g; };
P.docs = () => { const g = new THREE.Group(); [0, 1, 2].forEach(i => { const d = mesh(rbox(1.8, 1.2, .06, .06), M('#ffffff', { rough: .5 })); d.position.set(-.3 + i * .3, .1 - i * .15, i * .12); d.rotation.z = -.08 + i * .08; g.add(d); const l = mesh(new THREE.BoxGeometry(1.0, .09, .02), new THREE.MeshBasicMaterial({ color: col('#4CC9F0') })); l.position.set(-.25, .32, .035); d.add(l); [0, 1, 2].forEach(k => { const t = mesh(new THREE.BoxGeometry(1.4 - k * .3, .06, .02), new THREE.MeshBasicMaterial({ color: col('#C8D0EE') })); t.position.set(-.1 - k * .15, .1 - k * .2, .035); d.add(t); }); }); return g; };
P.glassCard = (w, h, o = {}) => { const g = new THREE.Group(); const m = new THREE.Mesh(rbox(w, h, .14, .22, 5), new THREE.MeshPhysicalMaterial({ color: col(o.color || '#ffffff'), transparent: true, opacity: o.opacity ?? .13, roughness: .1, metalness: 0, clearcoat: 1, envMapIntensity: 1.2 })); m.castShadow = false; g.add(m); const e = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, .14)), new THREE.LineBasicMaterial({ color: col(o.edge || '#ffffff'), transparent: true, opacity: o.edgeOp ?? .4 })); g.add(e); return g; };
P.bubble = (w = 3, h = 1.4, color = '#ffffff') => { const g = new THREE.Group(); g.add(mesh(rbox(w, h, .22, .5, 6), M(color, { rough: .4, coat: .6 }))); const t = mesh(new THREE.ConeGeometry(.28, .6, 4), M(color)); t.position.set(-w / 2 + .6, -h / 2 - .22, 0); t.rotation.z = Math.PI + .3; g.add(t); return g; };
P.thought = (w = 3.4, h = 1.8, color = '#ffffff') => { const g = new THREE.Group(), m = M(color, { rough: .5, coat: .5 }); const e = mesh(new THREE.SphereGeometry(1, 36, 24), m); e.scale.set(w / 2, h / 2, .35); g.add(e); [[-.38, .42, .38], [-.12, .5, .44], [.18, .5, .42], [.4, .38, .36], [.44, -.3, .34], [-.4, -.32, .34], [0, -.5, .38]].forEach(([x, y, r]) => { const s = mesh(new THREE.SphereGeometry(r * h * .6, 24, 16), m); s.position.set(x * w, y * h, 0); s.scale.z = .5; g.add(s); }); const d1 = mesh(new THREE.SphereGeometry(.2, 16, 12), m); d1.position.set(-w / 2 + .15, -h / 2 - .35, 0); const d2 = mesh(new THREE.SphereGeometry(.12, 16, 12), m); d2.position.set(-w / 2 - .15, -h / 2 - .75, 0); g.add(d1, d2); return g; };
P.hand = () => { const g = new THREE.Group(); const t = label('👆', { h: 1.6, size: 200, font: 'en', gain: 1.0 }); g.add(t); return g; };
P.avatar = (c = '#6C3BE8') => { const g = new THREE.Group(); g.add(mesh(new THREE.SphereGeometry(.42, 24, 18), M(c))); const h = mesh(new THREE.SphereGeometry(.14, 16, 12), M('#fff')); h.position.set(0, .1, .36); g.add(h); const b = mesh(new THREE.SphereGeometry(.22, 16, 12), M('#fff')); b.scale.set(1.3, .8, .5); b.position.set(0, -.2, .34); g.add(b); return g; };
P.spark = (r = .22, color = '#ffffff') => { const g = new THREE.Group(); const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex(), color: col(color), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); sp.scale.setScalar(r * 8); g.add(sp); return g; };

let _gt = null;
export function glowTex() { if (_gt) return _gt; const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'); const g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.3, 'rgba(255,255,255,.35)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); _gt = new THREE.CanvasTexture(c); return _gt; }
export function lightCone(color = '#ffd9a0', h = 9, r = 3, op = .13) { return new THREE.Mesh(new THREE.ConeGeometry(r, h, 40, 1, true), new THREE.MeshBasicMaterial({ color: col(color), transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide })); }
export function halo(color = '#FFD66B', s = 6, op = .6) { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex(), color: col(color), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: op })); sp.scale.setScalar(s); return sp; }

// ------------------------------------------------------------------ toy-style person
const SKIN = { light: '#F4C9A8', tan: '#E0A678', brown: '#B9774A', dark: '#8A5530' };
export function person(o = {}) {
  const g = new THREE.Group(), parts = g.parts = {}, skin = M(SKIN[o.skin || 'tan'], { rough: .55, coat: .15 }), shirt = M(o.shirt || '#4C6FFF', { rough: .5 }), pants = M(o.pants || '#2b2f55', { rough: .6 });
  const hairM = M(o.hairColor || '#1d1b24', { rough: .45 });
  const legs = group(); [-.2, .2].forEach(x => { const l = mesh(new THREE.CapsuleGeometry(.15, .62, 6, 12), pants); l.position.set(x, .52, 0); legs.add(l); const s = mesh(new THREE.SphereGeometry(.2, 16, 12), M(o.shoes || '#eee', { rough: .4 })); s.scale.set(1, .6, 1.4); s.position.set(x, .14, .08); legs.add(s); }); g.add(legs);
  const torso = mesh(new THREE.CapsuleGeometry(.46, .62, 8, 20), shirt); torso.scale.set(1.05, 1, .78); torso.position.y = 1.52; g.add(torso); parts.torso = torso;
  if (o.hoodie) { const h = mesh(new THREE.TorusGeometry(.3, .09, 10, 24), shirt); h.position.set(0, 1.98, -.05); h.rotation.x = 1.2; g.add(h); [-.12, .12].forEach(x => { const c = mesh(new THREE.CylinderGeometry(.015, .015, .4, 6), M('#fff')); c.position.set(x, 1.65, .36); g.add(c); }); }
  if (o.kurta) [0, 1, 2].forEach(i => { const b = mesh(new THREE.SphereGeometry(.035, 8, 6), M('#fff')); b.position.set(0, 1.9 - i * .17, .36); g.add(b); });
  if (o.tie) { const t = mesh(shapeGeo(poly([[-.07, 0], [.07, 0], [.1, -.5], [0, -.62], [-.1, -.5]]), .04, .01), M(o.tie)); t.position.set(0, 1.78, .38); g.add(t); }
  const mkArm = sgn => { const a = new THREE.Group(); a.position.set(sgn * .56, 1.88, 0); const s = mesh(new THREE.SphereGeometry(.17, 16, 12), shirt); a.add(s); const u = mesh(new THREE.CapsuleGeometry(.12, .52, 6, 12), shirt); u.position.y = -.38; a.add(u); const h = mesh(new THREE.SphereGeometry(.14, 16, 12), skin); h.position.y = -.8; a.add(h); g.add(a); return a; };
  parts.armL = mkArm(-1); parts.armR = mkArm(1);
  const neck = mesh(new THREE.CylinderGeometry(.13, .15, .2, 16), skin); neck.position.y = 2.17; g.add(neck);
  const head = new THREE.Group(); head.position.y = 2.62; g.add(head); parts.head = head;
  const sk = mesh(new THREE.SphereGeometry(.52, 40, 30), skin); sk.scale.set(1, 1.05, .98); head.add(sk);
  [-1, 1].forEach(s => { const e = mesh(new THREE.SphereGeometry(.1, 12, 10), skin); e.position.set(s * .5, -.02, 0); e.scale.z = .6; head.add(e); });
  const nose = mesh(new THREE.SphereGeometry(.07, 12, 10), M(SKIN[o.skin || 'tan'], { rough: .5 })); nose.position.set(0, -.06, .52); head.add(nose);
  const eyes = group(); [-.19, .19].forEach(x => { const w = mesh(new THREE.SphereGeometry(.105, 16, 12), M('#fff', { rough: .2, coat: 1 })); w.position.set(x, .06, .43); w.scale.z = .6; const p = mesh(new THREE.SphereGeometry(.058, 12, 10), new THREE.MeshBasicMaterial({ color: 0x120c1d })); p.position.set(0, 0, .05); w.add(p); const hl = mesh(new THREE.SphereGeometry(.02, 6, 6), new THREE.MeshBasicMaterial({ color: 0xffffff })); hl.position.set(.02, .025, .095); w.add(hl); eyes.add(w); }); head.add(eyes); parts.eyes = eyes;
  const browM = M(o.hairColor || '#2a2233'); const brows = group(); parts.brows = brows;
  [-1, 1].forEach(s => { const b = mesh(new THREE.CapsuleGeometry(.025, .16, 4, 8), browM); b.rotation.z = Math.PI / 2; b.position.set(s * .19, .2, .46); b.userData.s = s; brows.add(b); }); head.add(brows);
  [-1, 1].forEach(s => { const c = mesh(new THREE.SphereGeometry(.09, 12, 10), new THREE.MeshBasicMaterial({ color: col('#ff8e8e'), transparent: true, opacity: .35 }), { shadow: false }); c.position.set(s * .3, -.12, .42); c.scale.set(1, .7, .3); head.add(c); });
  const mouth = mesh(new THREE.TorusGeometry(.13, .026, 8, 20, Math.PI), M('#5a2a2a', { rough: .6 }), { shadow: false }); mouth.position.set(0, -.2, .47); mouth.rotation.z = Math.PI; head.add(mouth); parts.mouth = mouth;
  const hs = o.hair || 'short';
  const hairTop = (c, th = .42, y = .14) => { const h = mesh(new THREE.SphereGeometry(.555, 40, 24, 0, Math.PI * 2, 0, Math.PI * th), c); h.position.set(0, y, -.02); head.add(h); };
  const hairBack = (c, th = .62) => { const h = mesh(new THREE.SphereGeometry(.56, 40, 24, Math.PI, Math.PI, 0, Math.PI * th), c); h.position.set(0, .1, -.02); h.scale.set(1, 1.05, .98); head.add(h); };
  if (hs === 'short') { hairTop(hairM); hairBack(hairM); }
  if (hs === 'grey') { const gm = M('#D8D8E0'); hairTop(gm); hairBack(gm, .58); }
  if (hs === 'bald') { [-1, 1].forEach(s => { const h = mesh(new THREE.SphereGeometry(.12, 10, 8), M('#B9B9C6')); h.position.set(s * .5, .1, -.05); head.add(h); }); }
  if (hs === 'cap') { const cm = M(o.capColor || '#FF5A5F', { coat: .8 }); hairTop(cm, .44, .12); hairBack(cm, .6); const br = mesh(new THREE.CylinderGeometry(.5, .5, .045, 32, 1, false, 0, Math.PI), M(o.capColor2 || '#E5384F')); br.position.set(0, .3, .1); br.scale.set(1.0, 1, 1.25); br.rotation.y = -Math.PI / 2; head.add(br); }
  if (hs === 'long') { hairTop(hairM); hairBack(hairM, .8); const b = mesh(new THREE.SphereGeometry(.56, 24, 16), hairM); b.scale.set(1, 1.2, .6); b.position.set(0, -.3, -.28); head.add(b); }
  if (hs === 'bun') { hairTop(hairM); hairBack(hairM); const b = mesh(new THREE.SphereGeometry(.22, 16, 12), hairM); b.position.set(0, .66, -.12); head.add(b); }
  if (hs === 'curly') { for (let i = 0; i < 14; i++) { const a = i / 14 * Math.PI * 2, b = mesh(new THREE.SphereGeometry(.2, 12, 10), hairM); b.position.set(Math.cos(a) * .44, .32 + Math.sin(a * 2) * .05, Math.sin(a) * .44 - .05); head.add(b); } hairTop(hairM, .4, .16); }
  if (o.glasses) { [-.19, .19].forEach(x => { const t = mesh(new THREE.TorusGeometry(.14, .02, 8, 24), M('#1f2235', { metal: .5 })); t.position.set(x, .06, .5); head.add(t); }); const br = mesh(new THREE.CylinderGeometry(.015, .015, .1, 6), M('#1f2235')); br.rotation.z = Math.PI / 2; br.position.set(0, .08, .5); head.add(br); }
  if (o.mustache) { [-1, 1].forEach(s => { const m = mesh(new THREE.CapsuleGeometry(.035, .17, 4, 8), M(o.mustacheColor || '#2a2233')); m.rotation.z = Math.PI / 2 + s * .25; m.position.set(s * .1, -.12, .5); head.add(m); }); }
  if (o.headphones) { const t = mesh(new THREE.TorusGeometry(.55, .035, 8, 32, Math.PI), M('#222')); t.rotation.z = 0; t.position.y = .05; head.add(t); [-1, 1].forEach(s => { const c = mesh(new THREE.CylinderGeometry(.14, .14, .1, 16), M('#222')); c.rotation.z = Math.PI / 2; c.position.set(s * .56, 0, 0); head.add(c); }); }
  if (o.earphones) [-1, 1].forEach(s => { const c = mesh(new THREE.SphereGeometry(.05, 8, 6), M('#fff')); c.position.set(s * .52, -.04, .02); head.add(c); });
  if (o.bindi) { const b = mesh(new THREE.SphereGeometry(.03, 8, 6), M('#E5384F')); b.position.set(0, .2, .5); head.add(b); }
  g.setMood = m => {
    const cfg = { smile: [.13, 1, 0], grin: [.16, 1.15, 0], worry: [.1, -1, .12], flat: [.12, 0, 0], o: [.06, 1, .06], angry: [.1, -1, -.2], think: [.1, 0, .1] }[m] || [.13, 1, 0];
    const mo = parts.mouth; mo.scale.set(cfg[0] / .13, Math.abs(cfg[1]) < .05 ? .05 : cfg[1] > 0 ? cfg[1] : 1, 1); mo.rotation.z = cfg[1] >= 0 ? Math.PI : 0; mo.position.y = cfg[1] >= 0 ? -.2 : -.27;
    parts.brows.children.forEach(b => { b.rotation.z = Math.PI / 2 + b.userData.s * (cfg[2] === 0 ? .0 : cfg[2] > 0 ? .0 : .0) + (cfg[2] > 0 ? -b.userData.s * -.35 * (m === 'worry' ? 1 : 0) : 0) + (m === 'angry' ? b.userData.s * .5 : 0); b.position.y = .2 + (m === 'worry' ? .05 : m === 'o' ? .09 : 0); });
  };
  g.idle = (lt, ph = 0) => { parts.head.rotation.z = bob(lt, .03, .35, ph); parts.head.rotation.y = bob(lt, .08, .22, ph + 1); parts.head.position.y = 2.62 + bob(lt, .025, .6, ph); parts.torso.scale.y = 1 + bob(lt, .012, .6, ph); parts.armL.rotation.z = .1 + bob(lt, .03, .5, ph); parts.armR.rotation.z = -.1 - bob(lt, .03, .5, ph); const bl = (lt + ph) % 3.4; parts.eyes.scale.y = bl > 3.28 ? .12 : 1; };
  g.setMood(o.mood || 'smile'); g.traverse(n => { if (n.isMesh) n.castShadow = true; }); return g;
}
export const PEOPLE = {
  dad: { skin: 'tan', hair: 'grey', glasses: true, mustache: true, shirt: '#7C8DB5', kurta: true, pants: '#d9d4c8' },
  youth: { skin: 'brown', hair: 'cap', capColor: '#FF5A5F', capColor2: '#E5384F', shirt: '#2FB8A6', hoodie: true, earphones: true, pants: '#2b2f55' },
  me: { skin: 'tan', hair: 'short', shirt: '#4C6FFF', pants: '#2b2f55' },
  girl: { skin: 'light', hair: 'bun', hairColor: '#5b3a29', shirt: '#FF8A8A', bindi: true, pants: '#3b2f55' },
  curly: { skin: 'dark', hair: 'curly', shirt: '#4CC9F0', pants: '#2b2f55' },
};
