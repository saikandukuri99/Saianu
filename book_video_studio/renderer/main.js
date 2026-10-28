'use strict';
(async function () {
  await Promise.all(['700 40px TeSans', '400 40px TeSans', '700 40px TeSerif', '400 40px Pop', '600 40px Pop', '700 40px Pop'].map(f => document.fonts.load(f, 'అఆఇ ₹ABCabc')));
  await document.fonts.ready;

  const CUES = [], FLASHES = [], SHAKES = [];
  const layersRoot = $('layers');
  const LAY = TL.sentences.map(S => {
    const g = gnode(layersRoot); g.style.display = 'none';
    const wrap = gnode(g);
    const ctx = {
      g: wrap, S, dur: S.dur,
      cue: (t, n, v) => CUES.push({ t: +(S.start + t).toFixed(3), n, v: v == null ? 1 : v }),
      flash: (t, d, col, a) => FLASHES.push({ t: S.start + t, d, col, a }),
      shake: (t, amp, d) => SHAKES.push({ t: S.start + t, amp, d }),
    };
    let upd;
    try { upd = V[S.visual](ctx); }
    catch (e) { console.error('visual build failed', S.id, S.visual, e); upd = () => { }; }
    return { S, g, wrap, upd };
  });

  // ---- captions (karaoke style subtitles)
  const capRoot = $('cap');
  const CAP = [];
  const SIZE = 44, LH = 68, MAXW = 1480;
  TL.sentences.forEach(S => {
    S.chunks.forEach((ch, ci) => {
      ch.last = ci === S.chunks.length - 1;
      const grp = gnode(capRoot); grp.style.display = 'none';
      const words = ch.text.split(' ').filter(Boolean);
      const gap = SIZE * .27, ws = words.map(w => tw(w, SIZE, 700, 'te'));
      // wrap into lines
      const lines = []; let cur = [], cw = 0;
      words.forEach((w, i) => { const add = (cur.length ? gap : 0) + ws[i]; if (cw + add > MAXW && cur.length) { lines.push({ idx: cur, w: cw }); cur = []; cw = 0; } cur.push(i); cw += (cur.length > 1 ? gap : 0) + ws[i]; });
      if (cur.length) lines.push({ idx: cur, w: cw });
      const maxw = Math.max(...lines.map(l => l.w)), h = lines.length * LH + 34, top = 1042 - h;
      el('rect', { x: 960 - maxw / 2 - 44, y: top, width: maxw + 88, height: h, rx: 34, fill: 'rgba(7,9,34,.66)', stroke: 'rgba(255,255,255,.16)', 'stroke-width': 2 }, grp);
      const nodes = new Array(words.length), tot = words.reduce((a, w) => a + w.length, 0); let acc = 0; const fr = [];
      words.forEach(w => { fr.push(acc / tot); acc += w.length; });
      lines.forEach((ln, li) => {
        let x = 960 - ln.w / 2;
        ln.idx.forEach(i => { nodes[i] = txt(grp, words[i], { size: SIZE, weight: 700, x: x + ws[i] / 2, y: top + 17 + li * LH + LH * .68, fill: '#fff' }); x += ws[i] + gap; });
      });
      CAP.push({ ch, grp, nodes, fr });
    });
  });

  // ---- fx
  const fxRoot = $('fx');
  el('rect', { x: 0, y: 0, width: W, height: H, fill: 'url(#gVig)', 'pointer-events': 'none' }, fxRoot);
  const flash = el('rect', { x: 0, y: 0, width: W, height: H, fill: '#fff', opacity: 0 }, fxRoot);
  if (TL.brand) { const b = txt(fxRoot, TL.brand, { size: 34, font: 'en', fill: 'rgba(255,255,255,.7)', x: 1860, y: 70, anchor: 'end', weight: 600, ls: 3 }); }

  const camOf = (s, dx = 0, dy = 0) => `translate(${(960 * (1 - s) + dx).toFixed(2)} ${(540 * (1 - s) + dy).toFixed(2)}) scale(${s.toFixed(4)})`;

  window.seek = function (t) {
    // background theme blend
    let idx = 0; for (let i = 0; i < LAY.length; i++) if (t >= LAY[i].S.start - .001) idx = i;
    const cur = LAY[idx].S, prev = idx > 0 ? LAY[idx - 1].S : cur;
    updateBg(t, prev.theme, cur.theme, idx > 0 ? E.inOut(seg(t, cur.start - .2, cur.start + .7)) : 1);
    // shake
    let sx = 0, sy = 0; SHAKES.forEach(s => { const p = (t - s.t) / s.d; if (p >= 0 && p <= 1) { const a = s.amp * (1 - p); sx += Math.sin(t * 61) * a; sy += Math.cos(t * 53) * a; } });
    layersRoot.setAttribute('transform', `translate(${sx.toFixed(2)} ${sy.toFixed(2)})`);
    LAY.forEach((L, i) => {
      const S = L.S, first = i === 0, last = i === LAY.length - 1;
      const pin = first ? 1 : seg(t, S.start - .16, S.start + .16), pout = last ? 0 : seg(t, S.end - .16, S.end + .16);
      const op = Math.min(pin, 1 - pout);
      if (op <= 0.001 || t < S.start - .17 || t > S.end + .17) { L.g.style.display = 'none'; return; }
      L.g.style.display = 'inline';
      const lt = clamp(t - S.start, 0, S.dur + .3);
      try { L.upd(lt); } catch (e) { console.error('update failed', S.id, e); }
      let dx = 0, dy = 0, sc = 1 + .03 * seg(lt, 0, S.dur);
      const tr = S.trans || 'fade';
      if (tr === 'slide') { dx = (1 - E.out3(pin)) * 220 - E.in2(pout) * 220; }
      if (tr === 'zoom') { sc *= lerp(1.12, 1, E.out3(pin)) * lerp(1, .92, E.in2(pout)); }
      if (tr === 'up') { dy = (1 - E.out3(pin)) * 120 - E.in2(pout) * 120; }
      L.g.setAttribute('transform', camOf(sc, dx, dy)); L.g.setAttribute('opacity', op.toFixed(3));
    });
    // captions
    CAP.forEach(C_ => {
      const c = C_.ch, a = seg(t, c.t0 - .02, c.t0 + .12), b = c.last ? 1 - seg(t, c.t1 + .1, c.t1 + .3) : 1 - seg(t, c.t1 - .08, c.t1);
      const o = Math.min(a, b);
      if (o <= 0.001) { C_.grp.style.display = 'none'; return; }
      C_.grp.style.display = 'inline'; C_.grp.setAttribute('opacity', o.toFixed(3));
      C_.grp.setAttribute('transform', `translate(0 ${((1 - E.out3(a)) * 18).toFixed(2)})`);
      const prog = clamp((t - c.t0) / Math.max(.2, (c.t1 - c.t0) * .94));
      C_.nodes.forEach((n, i) => n.setAttribute('fill', prog >= C_.fr[i] ? '#FFD66B' : '#FFFFFF'));
    });
    // flashes
    let fa = 0; FLASHES.forEach(f => { const p = (t - f.t) / f.d; if (p >= 0 && p <= 1) fa = Math.max(fa, f.a * (1 - p)); });
    flash.setAttribute('opacity', fa.toFixed(3));
  };
  window.getCues = () => CUES.slice().sort((a, b) => a.t - b.t);
  window.READY = true;
  if (location.hash.startsWith('#t=')) window.seek(parseFloat(location.hash.slice(3)));
})();
