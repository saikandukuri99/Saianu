// Sentence sequencer: builds one 3D group per sentence, drives camera / theme / transitions / captions from time t.
import * as THREE from 'three';
import { V, scene, camera, composer, fx, renderer, applyTheme, evalCam, setCamera, clamp, lerp, seg, E, W, H } from './core3d.js';
import './kit3d.js';
import './v3d_1.js'; import './v3d_2.js'; import './v3d_3.js';

const TLs = window.TL.sentences;
const CUES = [], FLASHES = [], SHAKES = [];
const root = new THREE.Group(); scene.add(root);

const LAY = TLs.map(S => {
  const g = new THREE.Group(); g.visible = false; root.add(g);
  const ctx = {
    g, S, dur: S.dur, cam: null,
    camera: keys => { ctx.cam = keys; },
    cue: (t, n, v) => CUES.push({ t: +(S.start + t).toFixed(3), n, v: v == null ? 1 : v }),
    flash: (t, d, c, a) => FLASHES.push({ t: S.start + t, d, a }),
    shake: (t, amp, d) => SHAKES.push({ t: S.start + t, amp, d }),
  };
  let upd = () => { };
  try { upd = V[S.visual](ctx) || upd; } catch (e) { console.error('visual build failed', S.id, S.visual, e); }
  if (!ctx.cam) ctx.cam = [{ t: 0, p: [0, .4, 12], l: [0, 0, 0], f: 32 }, { t: 1, p: [0, .4, 11], l: [0, 0, 0], f: 32 }];
  return { S, g, ctx, upd };
});

// ---------------------------------------------------------------- captions (karaoke subtitles drawn on a 2D canvas, composited on export)
const capCanvas = document.createElement('canvas'); capCanvas.width = W; capCanvas.height = H; const cx = capCanvas.getContext('2d');
const out2d = document.createElement('canvas'); out2d.width = W; out2d.height = H; const ox = out2d.getContext('2d');
const SIZE = 44, LH = 68, MAXW = 1480, CAPFONT = `700 ${SIZE}px 'TeSans','Pop',sans-serif`;
cx.font = CAPFONT;
const CAP = [];
TLs.forEach(S => S.chunks.forEach((ch, ci) => {
  ch.last = ci === S.chunks.length - 1;
  const words = ch.text.split(' ').filter(Boolean), gap = SIZE * .27, ws = words.map(w => cx.measureText(w).width);
  const lines = []; let cur = [], cw = 0;
  words.forEach((w, i) => { const add = (cur.length ? gap : 0) + ws[i]; if (cw + add > MAXW && cur.length) { lines.push({ idx: cur, w: cw }); cur = []; cw = 0; } cur.push(i); cw += (cur.length > 1 ? gap : 0) + ws[i]; });
  if (cur.length) lines.push({ idx: cur, w: cw });
  const maxw = Math.max(...lines.map(l => l.w)), h = lines.length * LH + 34, top = 1042 - h;
  const tot = words.reduce((a, w) => a + w.length, 0); let acc = 0; const fr = []; words.forEach(w => { fr.push(acc / tot); acc += w.length; });
  const pos = []; lines.forEach((ln, li) => { let x = 960 - ln.w / 2; ln.idx.forEach(i => { pos[i] = [x + ws[i] / 2, top + 17 + li * LH + LH * .68]; x += ws[i] + gap; }); });
  CAP.push({ ch, words, pos, fr, box: [960 - maxw / 2 - 44, top, maxw + 88, h] });
}));
function rr(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
function drawCaptions(t) {
  cx.clearRect(0, 0, W, H); cx.font = CAPFONT; cx.textAlign = 'center'; cx.textBaseline = 'alphabetic';
  CAP.forEach(C_ => {
    const ch = C_.ch, a = seg(t, ch.t0 - .02, ch.t0 + .12), b = ch.last ? 1 - seg(t, ch.t1 + .1, ch.t1 + .3) : 1 - seg(t, ch.t1 - .08, ch.t1), o = Math.min(a, b);
    if (o <= .001) return;
    const dy = (1 - E.out3(a)) * 18, prog = clamp((t - ch.t0) / Math.max(.2, (ch.t1 - ch.t0) * .94));
    cx.save(); cx.globalAlpha = o; cx.translate(0, dy);
    const [bx, by, bw, bh] = C_.box; rr(cx, bx, by, bw, bh, 34); cx.fillStyle = 'rgba(7,9,34,.62)'; cx.fill(); cx.strokeStyle = 'rgba(255,255,255,.16)'; cx.lineWidth = 2; cx.stroke();
    C_.words.forEach((w, i) => { cx.fillStyle = prog >= C_.fr[i] ? '#FFD66B' : '#FFFFFF'; cx.fillText(w, C_.pos[i][0], C_.pos[i][1]); });
    cx.restore();
  });
}

// ---------------------------------------------------------------- seek
const TRANS = { slide: { dir: [1, 0], blur: 1.0, radial: 0, flash: 0 }, up: { dir: [0, 1], blur: .9, radial: 0, flash: 0 }, zoom: { dir: [1, 0], blur: 0, radial: 1.0, flash: .12 }, fade: { dir: [1, 0], blur: .25, radial: .35, flash: .22 } };
window.seek = function (t) {
  let idx = 0; for (let i = 0; i < LAY.length; i++) if (t >= LAY[i].S.start - 1e-4) idx = i;
  const L = LAY[idx], S = L.S, prev = idx > 0 ? LAY[idx - 1].S : S;
  LAY.forEach((o, i) => { o.g.visible = i === idx; });
  const lt = clamp(t - S.start, 0, S.dur + .5), f = clamp(lt / S.dur);
  applyTheme(prev.theme, S.theme, idx > 0 ? E.inOut(seg(t, S.start - .2, S.start + .7)) : 1, t);
  try { L.upd(lt); } catch (e) { console.error('update failed', S.id, e); }
  // camera
  const c = evalCam(L.ctx.cam, f);
  let sx = 0, sy = 0; SHAKES.forEach(s => { const p = (t - s.t) / s.d; if (p >= 0 && p <= 1) { const a = s.amp * (1 - p); sx += Math.sin(t * 61) * a; sy += Math.cos(t * 53) * a; } });
  setCamera(c, t); camera.position.x += sx; camera.position.y += sy;
  // transition between sentences: whip blur / zoom blur peaking exactly at the cut
  let blur = 0, rad = 0, flash = 0; const dir = fx.uniforms.uDir.value;
  const bounds = [S.start, idx + 1 < LAY.length ? LAY[idx + 1].S.start : 1e9];
  const near = bounds.map(b => b - t).reduce((a, b) => Math.abs(b) < Math.abs(a) ? b : a, 1e9);
  const kk = Math.pow(clamp(1 - Math.abs(near) / .2), 1.4);
  const tr = TRANS[(Math.abs(near) === Math.abs(bounds[0] - t) ? S.trans : (LAY[idx + 1] ? LAY[idx + 1].S.trans : 'fade'))] || TRANS.fade;
  if (kk > 0 && !(idx === 0 && Math.abs(bounds[0] - t) < 1e-3)) { blur = kk * tr.blur; rad = kk * tr.radial; flash = kk * tr.flash; dir.set(tr.dir[0], tr.dir[1]); }
  FLASHES.forEach(fl => { const p = (t - fl.t) / fl.d; if (p >= 0 && p <= 1) flash = Math.max(flash, fl.a * (1 - p)); });
  if (idx === 0) { flash = Math.max(flash, .6 * (1 - seg(t, 0, .35))); }
  fx.uniforms.uBlur.value = blur; fx.uniforms.uRadial.value = rad; fx.uniforms.uFlash.value = flash; fx.uniforms.uT.value = t;
  composer.render();
  window.__t = t;
};
window.grab = (t, q = .93) => { window.seek(t); drawCaptions(t); ox.imageSmoothingEnabled = true; ox.imageSmoothingQuality = 'high'; ox.drawImage(renderer.domElement, 0, 0, W, H); ox.drawImage(capCanvas, 0, 0); return out2d.toDataURL('image/jpeg', q).slice(23); };
window.getCues = () => CUES.slice().sort((a, b) => a.t - b.t);
window.READY = true;
const h = location.hash.match(/t=([\d.]+)/); if (h) window.seek(parseFloat(h[1]));
