// THE FILM: Solix Academy executive promo. Every frame is a pure function of t, timed from score.js.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev, V, C, BEAT } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const TAU = Math.PI * 2;
  const FONT = 'Inter, system-ui, sans-serif';
  const IMG = {};
  const LAYERS = {};

  // ---------------------------------------------------------------- helpers
  const fade = (t, t0, d = 0.5) => clamp((t - t0) / d);
  const win = (t, a, b, fi = 0.5, fo = 0.5) => Math.min(fade(t, a, fi), 1 - fade(t, b - fo, fo));
  const rgba = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };
  const hash = (...xs) => U.hash(...xs);

  function font(ctx, size, weight = 700) { ctx.font = `${weight} ${size}px ${FONT}`; }
  function text(ctx, str, x, y, { size = 48, weight = 700, color = '#fff', align = 'left', alpha = 1, spacing = 0, glow = 0, glowColor = null, baseline = 'alphabetic' } = {}) {
    if (alpha <= 0.003) return 0;
    ctx.save();
    font(ctx, size, weight);
    ctx.letterSpacing = spacing + 'px';
    ctx.textAlign = align; ctx.textBaseline = baseline;
    ctx.globalAlpha *= alpha;
    if (glow) { ctx.shadowColor = glowColor || color; ctx.shadowBlur = glow; }
    ctx.fillStyle = color;
    ctx.fillText(str, x, y);
    const w = ctx.measureText(str).width;
    ctx.restore();
    return w;
  }
  function measure(ctx, str, size, weight = 700, spacing = 0) { ctx.save(); font(ctx, size, weight); ctx.letterSpacing = spacing + 'px'; const w = ctx.measureText(str).width; ctx.restore(); return w; }

  // a line made of segments {s, c, hl, t}; each segment rises in at its own time (t), highlight segments get colour + optional pill
  function rich(ctx, segs, x, y, { size = 64, weight = 800, align = 'left', alpha = 1, t = 0, rise = 26, spacing = -1 } = {}) {
    const ws = segs.map((g) => measure(ctx, g.s, size, g.weight || weight, spacing));
    const total = ws.reduce((a, b) => a + b, 0);
    let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
    segs.forEach((g, i) => {
      const k = g.t === undefined ? 1 : ease.outCubic(fade(t, g.t, 0.45));
      const a = alpha * k;
      if (a > 0.003) {
        const yy = y + (1 - k) * rise;
        if (g.pill) {
          const pw = ws[i] - measure(ctx, ' ', size, weight) * (g.s.endsWith(' ') ? 1 : 0);
          ctx.save(); ctx.globalAlpha = a;
          rrect(ctx, cx - size * 0.18, yy - size * 0.86, pw + size * 0.36, size * 1.12, size * 0.2);
          ctx.fillStyle = g.pill; ctx.fill(); ctx.restore();
        }
        // After-Effects style "blur in" animator: each segment arrives defocused and slightly over-tracked
        if (k < 1) ctx.filter = `blur(${((1 - k) * 12 * (G.scale || 1)).toFixed(2)}px)`;
        text(ctx, g.s, cx, yy, { size, weight: g.weight || weight, color: g.c || '#fff', alpha: a, spacing: spacing + (1 - k) * size * 0.12, glow: g.glow || 0, glowColor: g.c });
        ctx.filter = 'none';
      }
      cx += ws[i];
    });
    return total;
  }
  function rrect(ctx, x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }
  function glowDot(ctx, x, y, r, color, a = 1) {
    if (a <= 0.003 || r <= 0) return;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(color, a)); g.addColorStop(0.35, rgba(color, a * 0.35)); g.addColorStop(1, rgba(color, 0));
    ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2);
  }
  function kicker(ctx, str, x, y, a, color = C.blueHi, align = 'left') {
    if (a <= 0) return;
    const w = measure(ctx, str, 24, 700, 6);
    const x0 = align === 'center' ? x - w / 2 : x;
    ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = C.red; ctx.fillRect(x0 - 2, y + 14, 46 * a, 4); ctx.restore();
    text(ctx, str, x0, y, { size: 24, weight: 700, color, alpha: a, spacing: 6 });
  }

  // deep indigo backdrop with brand glows
  function backdrop(ctx, t, { glowX = W * 0.5, glowY = H * 0.45, blue = 0.35, red = 0.12, top = '#06051a', bottom = '#1a1450' } = {}) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, top); g.addColorStop(1, bottom);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    glowDot(ctx, glowX + Math.sin(t * 0.21) * 80, glowY + Math.cos(t * 0.17) * 40, 900, C.blue, blue * 0.5);
    glowDot(ctx, W * 0.86 + Math.cos(t * 0.13) * 60, H * 0.12, 700, C.red, red * 0.5);
    glowDot(ctx, W * 0.1, H * 0.95, 800, '#5a46d6', 0.1);
    ctx.restore();
  }
  // soft out-of-focus particles drifting up
  function bokeh(ctx, t, n = 40, a = 0.5, seed = 1) {
    a *= 0.45; // kept quiet so the foreground reads
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < n; i++) {
      const sp = 8 + hash(i, seed, 1) * 26;
      const x = hash(i, seed, 2) * W + Math.sin(t * 0.3 + i) * 30;
      const y = ((hash(i, seed, 3) * (H + 200) - t * sp) % (H + 200) + H + 200) % (H + 200) - 100;
      const r = 6 + hash(i, seed, 4) * 22;
      const col = hash(i, seed, 5) < 0.7 ? C.blue : hash(i, seed, 6) < 0.5 ? C.red : '#8f7dff';
      glowDot(ctx, x, y, r * 2.2, col, a * (0.25 + 0.5 * hash(i, seed, 7)) * (0.6 + 0.4 * Math.sin(t * 1.3 + i * 2)));
    }
    ctx.restore();
  }
  // perspective floor grid
  function floorGrid(ctx, t, horizon, a = 0.4, speed = 40, color = C.blue) {
    a *= 0.55;
    if (a <= 0) return;
    ctx.save();
    ctx.globalAlpha = a;
    const vx = W / 2;
    ctx.strokeStyle = rgba(color, 0.55); ctx.lineWidth = 1.4;
    for (let i = -14; i <= 14; i++) { ctx.beginPath(); ctx.moveTo(vx + i * 30, horizon); ctx.lineTo(vx + i * 330, H + 40); ctx.stroke(); }
    const off = (t * speed) % 60;
    for (let k = 0; k < 18; k++) {
      const d = k * 60 + off; // distance
      const y = horizon + (H - horizon) * Math.pow(d / 1080, 1.8);
      if (y > H + 10) continue;
      ctx.globalAlpha = a * clamp((y - horizon) / 120);
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    ctx.restore();
    const g = ctx.createLinearGradient(0, horizon - 2, 0, horizon + 160);
    g.addColorStop(0, rgba('#0a0826', 1)); g.addColorStop(1, rgba('#0a0826', 0));
    ctx.fillStyle = g; ctx.fillRect(0, horizon - 2, W, 162);
  }
  // a slowly turning 3D network of light (nodes + links), depth-faded: the "data" backdrop
  const PLEX = Array.from({ length: 90 }, (_, i) => [hash(i, 501) * 2 - 1, hash(i, 502) * 2 - 1, hash(i, 503) * 2 - 1]);
  function plexus(ctx, t, { a = 1, cx = W / 2, cy = H * 0.45, scale = 1150, speed = 0.05, seed = 0 } = {}) {
    if (a <= 0) return;
    const ry = t * speed + seed, rx = 0.35 + Math.sin(t * 0.07 + seed) * 0.08;
    const cyr = Math.cos(ry), syr = Math.sin(ry), cxr = Math.cos(rx), sxr = Math.sin(rx);
    const P = PLEX.map(([x, y, z]) => {
      const x1 = x * cyr + z * syr, z1 = -x * syr + z * cyr;
      const y1 = y * cxr - z1 * sxr, z2 = y * sxr + z1 * cxr;
      const d = 2.6 + z2, f = scale / d;
      return [cx + x1 * f * 1.25, cy + y1 * f * 0.75, z2, x, y, z];
    });
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    ctx.lineWidth = 1.1;
    for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) {
      const dx = PLEX[i][0] - PLEX[j][0], dy = PLEX[i][1] - PLEX[j][1], dz = PLEX[i][2] - PLEX[j][2];
      const d2 = dx * dx + dy * dy + dz * dz;
      if (d2 > 0.16) continue;
      const depth = clamp(0.75 - (P[i][2] + P[j][2]) * 0.3);
      ctx.strokeStyle = rgba((i + j) % 7 ? C.blueHi : '#8d7bff', a * 0.5 * (1 - d2 / 0.16) * depth);
      ctx.beginPath(); ctx.moveTo(P[i][0], P[i][1]); ctx.lineTo(P[j][0], P[j][1]); ctx.stroke();
    }
    P.forEach(([x, y, z], i) => {
      const depth = clamp(0.8 - z * 0.35);
      const tw = 0.6 + 0.4 * Math.sin(t * 1.7 + i * 2.3);
      glowDot(ctx, x, y, (7 + 9 * depth), i % 9 ? C.blueHi : C.red, a * 0.75 * depth * tw);
    });
    ctx.restore();
  }
  // soft light pooling on an unseen floor (no grid)
  function floorLight(ctx, t, y, a = 1, color = C.blue) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    ctx.translate(W / 2, y); ctx.scale(1, 0.22);
    glowDot(ctx, 0, 0, 1100, color, 0.28 * a);
    ctx.restore();
  }

  // a flash / light-leak at a cut
  function flash(ctx, t, t0, { color = '#ffffff', a = 0.8, d = 0.5 } = {}) {
    const k = t - t0;
    if (k < -0.08 || k > d) return;
    const v = k < 0 ? (k + 0.08) / 0.08 : Math.exp(-k * 7);
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = v * a;
    const g = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, W * 0.7);
    g.addColorStop(0, color); g.addColorStop(1, rgba(C.blue, 0.2));
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
  }
  function shockRing(ctx, x, y, t, t0, { color = C.blue, r1 = 700, d = 0.9, lw = 6 } = {}) {
    const k = (t - t0) / d;
    if (k < 0 || k > 1) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    ctx.strokeStyle = rgba(color, (1 - k) * 0.9); ctx.lineWidth = lw * (1 - k) + 1;
    ctx.shadowColor = color; ctx.shadowBlur = 30;
    ctx.beginPath(); ctx.arc(x, y, 40 + r1 * ease.outCubic(k), 0, TAU); ctx.stroke();
    ctx.restore();
  }

  // anamorphic lens flare: a horizontal streak, a hot core and ghosts mirrored through the frame centre
  function lensFlare(ctx, x, y, t, t0, { color = C.blueHi, dur = 1.3, size = 1 } = {}) {
    const k = (t - t0) / dur;
    if (k < -0.05 || k > 1) return;
    const v = k < 0 ? (k + 0.05) / 0.05 : Math.pow(1 - k, 1.6);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const sw = W * 1.1 * size * (0.6 + 0.4 * v);
    const g = ctx.createLinearGradient(x - sw / 2, 0, x + sw / 2, 0);
    g.addColorStop(0, rgba(color, 0)); g.addColorStop(0.5, rgba('#ffffff', 0.9 * v)); g.addColorStop(1, rgba(color, 0));
    ctx.fillStyle = g; ctx.fillRect(x - sw / 2, y - 3 * size, sw, 6 * size);
    ctx.globalAlpha = 0.6; ctx.fillRect(x - sw / 2, y - 12 * size, sw, 24 * size);
    ctx.globalAlpha = 1;
    glowDot(ctx, x, y, 220 * size * v, '#ffffff', 0.7 * v);
    glowDot(ctx, x, y, 520 * size, color, 0.35 * v);
    const dx = W / 2 - x, dy = H / 2 - y;
    [[0.6, 40, C.blue], [1.15, 70, '#8d7bff'], [1.5, 26, C.red], [1.85, 110, C.blue]].forEach(([p, r, c]) => {
      const gx = x + dx * p * 2 * (0.9 + 0.1 * v), gy = y + dy * p * 2 * (0.9 + 0.1 * v);
      ctx.fillStyle = rgba(c, 0.12 * v); ctx.beginPath(); ctx.arc(gx, gy, r * size, 0, TAU); ctx.fill();
      ctx.strokeStyle = rgba(c, 0.18 * v); ctx.lineWidth = 2; ctx.stroke();
    });
    ctx.restore();
  }
  // camera shake on the impacts (decaying, smooth noise)
  const IMPACTS = [[ev.beatIn, 6], ...ev.pillar.map((p) => [p, 7]), [ev.logo, 12], [ev.learn, 5], [ev.innovate, 6], [ev.transform, 16]];
  function shake(t) {
    let x = 0, y = 0, r = 0;
    for (const [t0, amp] of IMPACTS) {
      const k = t - t0;
      if (k < 0 || k > 0.7) continue;
      const e = amp * Math.exp(-k * 7);
      x += U.noise1(k * 30, t0) * e; y += U.noise1(k * 30, t0 + 9) * e; r += U.noise1(k * 24, t0 + 3) * e * 0.0009;
    }
    return { x, y, r };
  }
  // offscreen buffers for the comp passes (sized to the real canvas, so 4K stays 4K)
  const BUF = {};
  function buffer(name, w, h) {
    let c = BUF[name];
    if (!c || c.width !== w || c.height !== h) { c = BUF[name] = G.makeCanvas(w, h); }
    return c;
  }
  // draw a scene through a layer: opacity + scale about the centre + gaussian blur (zoom-blur transitions)
  function layer(ctx, fn, t, { alpha = 1, scale = 1, blur = 0 }) {
    if (alpha <= 0.003) return;
    if (blur < 0.2 && Math.abs(scale - 1) < 1e-4) { ctx.save(); ctx.globalAlpha = alpha; fn(ctx, t); ctx.restore(); return; }
    const cv = ctx.canvas, s = G.scale || 1;
    const c = buffer('layer', cv.width, cv.height), x = c.getContext('2d');
    x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, c.width, c.height);
    x.setTransform(s, 0, 0, s, 0, 0);
    x.translate(W / 2, H / 2); x.scale(scale, scale); x.translate(-W / 2, -H / 2);
    fn(x, t);
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = alpha;
    ctx.filter = `blur(${(blur * s).toFixed(2)}px)`;
    ctx.drawImage(c, 0, 0);
    ctx.restore();
  }
  // "Deep Glow": threshold the bright parts, blur them small, add them back
  function bloom(ctx, amount = 0.32) {
    const cv = ctx.canvas, sw = Math.round(cv.width / 4), sh = Math.round(cv.height / 4);
    const c = buffer('bloom', sw, sh), x = c.getContext('2d');
    x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'copy';
    x.filter = `brightness(0.85) contrast(2.4) blur(${Math.max(3, sw / 160).toFixed(1)}px)`;
    x.drawImage(cv, 0, 0, sw, sh);
    x.filter = 'none'; x.globalCompositeOperation = 'source-over';
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = amount;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(c, 0, 0, cv.width, cv.height);
    ctx.restore();
  }

  // ---------------------------------------------------------------- icons (line icons, centred at 0,0, size ~ s)
  const ICON = {
    database(ctx, s) { const w = s * 0.62, h = s * 0.2; for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.ellipse(0, -s * 0.34 + i * s * 0.3, w, h, 0, 0, TAU); ctx.stroke(); } ctx.beginPath(); ctx.moveTo(-w, -s * 0.34); ctx.lineTo(-w, s * 0.26); ctx.moveTo(w, -s * 0.34); ctx.lineTo(w, s * 0.26); ctx.stroke(); },
    people(ctx, s) { const p = (x, sc) => { ctx.beginPath(); ctx.arc(x, -s * 0.22 * sc, s * 0.17 * sc, 0, TAU); ctx.stroke(); ctx.beginPath(); ctx.arc(x, s * 0.42 * sc, s * 0.34 * sc, Math.PI * 1.08, Math.PI * 1.92); ctx.stroke(); }; p(-s * 0.36, 0.8); p(s * 0.36, 0.8); p(0, 1.05); },
    shield(ctx, s) { ctx.beginPath(); ctx.moveTo(0, -s * 0.55); ctx.lineTo(s * 0.48, -s * 0.36); ctx.lineTo(s * 0.42, s * 0.1); ctx.quadraticCurveTo(s * 0.3, s * 0.42, 0, s * 0.6); ctx.quadraticCurveTo(-s * 0.3, s * 0.42, -s * 0.42, s * 0.1); ctx.lineTo(-s * 0.48, -s * 0.36); ctx.closePath(); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-s * 0.2, 0); ctx.lineTo(-s * 0.04, s * 0.17); ctx.lineTo(s * 0.24, -s * 0.16); ctx.stroke(); },
    building(ctx, s) { ctx.strokeRect(-s * 0.32, -s * 0.5, s * 0.64, s); for (let r = 0; r < 4; r++) for (let c = 0; c < 2; c++) ctx.strokeRect(-s * 0.2 + c * s * 0.24, -s * 0.38 + r * s * 0.2, s * 0.14, s * 0.1); },
    gear(ctx, s) { ctx.beginPath(); for (let i = 0; i < 16; i++) { const a = (i / 16) * TAU, r = i % 2 ? s * 0.42 : s * 0.54; ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); } ctx.closePath(); ctx.stroke(); ctx.beginPath(); ctx.arc(0, 0, s * 0.18, 0, TAU); ctx.stroke(); },
    person(ctx, s) { ctx.beginPath(); ctx.arc(0, -s * 0.24, s * 0.2, 0, TAU); ctx.stroke(); ctx.beginPath(); ctx.arc(0, s * 0.5, s * 0.4, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); },
    cap(ctx, s) { ctx.beginPath(); ctx.moveTo(-s * 0.6, -s * 0.1); ctx.lineTo(0, -s * 0.38); ctx.lineTo(s * 0.6, -s * 0.1); ctx.lineTo(0, s * 0.16); ctx.closePath(); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-s * 0.32, s * 0.04); ctx.lineTo(-s * 0.32, s * 0.32); ctx.quadraticCurveTo(0, s * 0.5, s * 0.32, s * 0.32); ctx.lineTo(s * 0.32, s * 0.04); ctx.stroke(); ctx.beginPath(); ctx.moveTo(s * 0.5, -s * 0.06); ctx.lineTo(s * 0.5, s * 0.3); ctx.stroke(); },
    chip(ctx, s) { ctx.strokeRect(-s * 0.32, -s * 0.32, s * 0.64, s * 0.64); ctx.strokeRect(-s * 0.14, -s * 0.14, s * 0.28, s * 0.28); for (let i = -1; i <= 1; i++) { ctx.beginPath(); ctx.moveTo(i * s * 0.18, -s * 0.32); ctx.lineTo(i * s * 0.18, -s * 0.5); ctx.moveTo(i * s * 0.18, s * 0.32); ctx.lineTo(i * s * 0.18, s * 0.5); ctx.moveTo(-s * 0.32, i * s * 0.18); ctx.lineTo(-s * 0.5, i * s * 0.18); ctx.moveTo(s * 0.32, i * s * 0.18); ctx.lineTo(s * 0.5, i * s * 0.18); ctx.stroke(); } },
    briefcase(ctx, s) { rrect(ctx, -s * 0.5, -s * 0.24, s, s * 0.66, s * 0.08); ctx.stroke(); ctx.strokeRect(-s * 0.18, -s * 0.42, s * 0.36, s * 0.18); ctx.beginPath(); ctx.moveTo(-s * 0.5, s * 0.04); ctx.lineTo(s * 0.5, s * 0.04); ctx.stroke(); },
  };
  function icon(ctx, name, x, y, s, color, a = 1, lw = 3) {
    if (a <= 0) return;
    ctx.save(); ctx.translate(x, y); ctx.globalAlpha *= a; ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.shadowColor = color; ctx.shadowBlur = 12;
    ICON[name](ctx, s); ctx.restore();
  }

  // ---------------------------------------------------------------- the Solix Academy logo
  // The official artwork, cut into its parts so each can animate: icon, SOLIX, then "Academy" beside it,
  // then the tagline. Geometry is in the logo's own 2000 x 362 units; `width` is the on-screen width.
  const ACAD = { icon: [0, 0, 366, 362], solix: [404, 26, 737, 204], academy: [1149, 26, 849, 204], tag: [408, 238, 1584, 104] };
  function acadLogo(ctx, cx, cy, width, t, { tIcon = -99, tSolix = -99, tAcad = -99, tTag = -99, alpha = 1, tagline = true } = {}) {
    if (alpha <= 0) return { iconX: cx, iconY: cy };
    const u = width / 2000, x0 = cx - width / 2, y0 = cy - (tagline ? 181 : 128) * u;
    const P = (k) => { const [x, y, w, h] = ACAD[k]; return [x0 + x * u, y0 + y * u, w * u, h * u]; };
    ctx.save(); ctx.globalAlpha *= alpha;
    // icon: pops in with a small turn
    const ki = clamp((t - tIcon) / 0.5);
    if (ki > 0) {
      const [x, y, w, h] = P('icon'), s = ease.outBack(ki, 1.8), rot = (1 - ease.outCubic(ki)) * -0.8;
      ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(rot); ctx.scale(s, s); ctx.globalAlpha *= clamp(ki * 2);
      ctx.drawImage(IMG.acadIcon, -w / 2, -h / 2, w, h); ctx.restore();
    }
    // SOLIX wipes in left -> right
    const ks = ease.outCubic(clamp((t - tSolix) / 0.55));
    if (ks > 0) {
      const [x, y, w, h] = P('solix');
      ctx.save(); ctx.beginPath(); ctx.rect(x - 4, y - 10, (w + 8) * ks, h + 20); ctx.clip();
      ctx.drawImage(IMG.acadSolix, x - (1 - ks) * 40 * u * 10, y, w, h); ctx.restore();
    }
    // "Academy" arrives beside it, sliding in from the right
    const ka = ease.outCubic(clamp((t - tAcad) / 0.55));
    if (ka > 0) {
      const [x, y, w, h] = P('academy');
      ctx.save(); ctx.globalAlpha *= ka; ctx.drawImage(IMG.acadAcademy, x + (1 - ka) * 90 * u * 5, y, w, h); ctx.restore();
    }
    // tagline fades up
    const kt = ease.outCubic(clamp((t - tTag) / 0.6));
    if (tagline && kt > 0) {
      const [x, y, w, h] = P('tag');
      ctx.save(); ctx.globalAlpha *= kt; ctx.drawImage(IMG.acadTag, x, y + (1 - kt) * 20 * u * 5, w, h); ctx.restore();
    }
    ctx.restore();
    const [ix, iy, iw, ih] = P('icon');
    return { iconX: ix + iw / 2, iconY: iy + ih / 2 };
  }

  // the corporate Solix logo, top-right corner, for the whole film
  function cornerLogo(ctx, t) {
    const a = fade(t, 0.5, 0.8) * 0.95;
    if (a <= 0) return;
    const w = 300, h = w * 427 / 2000;
    ctx.save(); ctx.globalAlpha = a;
    ctx.drawImage(IMG.solixLogo, W - 56 - w, 42, w, h);
    ctx.restore();
  }

  // running captions of the narration (lower third), brand words in brand colours
  const CAPS = [];
  for (const l of S.vo) {
    let chunk = [];
    const flush = () => { if (chunk.length) CAPS.push({ words: chunk, t: chunk[0].t - 0.12 }); chunk = []; };
    l.words.forEach((w) => {
      const len = chunk.reduce((a, x) => a + x.w.length + 1, 0);
      if (len + w.w.length > 52) flush();
      chunk.push(w);
      if (/[.?:]$/.test(w.w) && len > 18) flush();
    });
    flush();
    CAPS[CAPS.length - 1].lineEnd = l.end;
  }
  CAPS.forEach((c, i) => { c.end = c.lineEnd !== undefined ? c.lineEnd + 0.25 : CAPS[i + 1].t; if (CAPS[i + 1] && c.end > CAPS[i + 1].t) c.end = CAPS[i + 1].t; });
  const KEY = /^(ai|ai-ready|artificial|intelligence|solix|academy|data|people|governance|enterprise|enterprises|transform|transformation|innovate|innovators|learn|hands-on|labs)$/i;
  function captions(ctx, t) {
    if (t >= ev.endcard - 0.3) return;
    const c = CAPS.find((c) => t >= c.t && t < c.end);
    if (!c) return;
    const a = Math.min(clamp((t - c.t) / 0.18), clamp((c.end - t) / 0.18));
    const size = 34, y = H - 66;
    const parts = c.words.map((w) => ({ s: w.w, key: KEY.test(w.w.replace(/[^A-Za-z-]/g, '')) }));
    const sp = measure(ctx, ' ', size, 600);
    const ws = parts.map((p) => measure(ctx, p.s, size, p.key ? 800 : 600));
    const total = ws.reduce((x, y2) => x + y2, 0) + sp * (parts.length - 1);
    ctx.save(); ctx.globalAlpha = a * 0.62;
    rrect(ctx, W / 2 - total / 2 - 28, y - 40, total + 56, 56, 28); ctx.fillStyle = '#05041a'; ctx.fill();
    ctx.restore();
    let x = W / 2 - total / 2;
    parts.forEach((p, i) => {
      text(ctx, p.s, x, y - 2, { size, weight: p.key ? 800 : 600, color: p.key ? (/^(innovate|innovators|transform|transformation)/i.test(p.s) ? '#ff5a5a' : C.blueHi) : '#ffffff', alpha: a });
      x += ws[i] + sp;
    });
  }

  // ================================================================ SCENE 1: city -> data streams -> boardroom
  function buildCity() {
    const mk = (seed, n, hMin, hMax, base, col, winA) => {
      const c = G.makeCanvas(W + 400, H), x = c.getContext('2d');
      let px = -20, i = 0;
      while (px < W + 400) {
        const bw = 60 + hash(seed, i, 1) * 120, bh = hMin + hash(seed, i, 2) * (hMax - hMin);
        const g = x.createLinearGradient(0, base - bh, 0, base);
        g.addColorStop(0, G.tint(col, 0.12)); g.addColorStop(1, col);
        x.fillStyle = g; x.fillRect(px, base - bh, bw, bh + 400);
        if (hash(seed, i, 3) < 0.35) { x.fillRect(px + bw * 0.4, base - bh - 40, 4, 40); }
        for (let wy = base - bh + 14; wy < base - 8; wy += 16) for (let wx = px + 8; wx < px + bw - 10; wx += 13) {
          const r = hash(seed, i, wx | 0, wy | 0);
          if (r < winA) { x.fillStyle = r < winA * 0.25 ? 'rgba(120,200,255,0.85)' : r < winA * 0.32 ? 'rgba(255,120,120,0.6)' : 'rgba(255,214,150,0.65)'; x.fillRect(wx, wy, 6, 8); }
        }
        px += bw + 6 + hash(seed, i, 4) * 20; i++;
      }
      return c;
    };
    LAYERS.city3 = mk(3, 0, 220, 520, H * 0.78, '#1a1650', 0.18);
    LAYERS.city2 = mk(2, 0, 260, 640, H * 0.86, '#120f3a', 0.24);
    LAYERS.city1 = mk(1, 0, 180, 460, H * 0.98, '#08071f', 0.3);
  }

  function city(ctx, t, a) {
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a;
    // sky
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#05041a'); g.addColorStop(0.55, '#16124a'); g.addColorStop(0.8, '#2a3a8a'); g.addColorStop(1, '#0c0a2a');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';
    glowDot(ctx, W * 0.5, H * 0.74, 1100, C.blue, 0.4);
    glowDot(ctx, W * 0.78, H * 0.7, 600, C.red, 0.14);
    ctx.globalCompositeOperation = 'source-over';
    // stars
    for (let i = 0; i < 90; i++) { ctx.fillStyle = `rgba(255,255,255,${0.15 + 0.4 * hash(i, 9) * (0.6 + 0.4 * Math.sin(t * 2 + i))})`; ctx.fillRect(hash(i, 7) * W, hash(i, 8) * H * 0.5, 2, 2); }
    // parallax push-in
    const z = 1 + 0.12 * ease.inOutQuad(clamp(t / 7));
    for (const [L, par] of [['city3', 0.3], ['city2', 0.6], ['city1', 1]]) {
      const zz = 1 + (z - 1) * par * 1.6;
      ctx.save(); ctx.translate(W / 2, H * 0.9); ctx.scale(zz, zz); ctx.translate(-W / 2 - 200 - t * 6 * par, -H * 0.9);
      ctx.drawImage(LAYERS[L], 0, 0); ctx.restore();
    }
    ctx.restore();
  }

  // vertical data streams rising out of the city
  function streams(ctx, t, a, t0) {
    if (a <= 0) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const n = 46;
    for (let i = 0; i < n; i++) {
      const x = (hash(i, 31) * 1.1 - 0.05) * W;
      const start = t0 + hash(i, 32) * 2.5;
      if (t < start) continue;
      const sp = 260 + hash(i, 33) * 420;
      const len = 120 + hash(i, 34) * 260;
      const col = hash(i, 35) < 0.78 ? C.blue : hash(i, 36) < 0.6 ? C.red : '#9d8cff';
      if (i % 2) continue; // half as many streams
      for (let k = 0; k < 3; k++) {
        const y = H - (((t - start) * sp + k * 520) % (H + len + 300));
        const gr = ctx.createLinearGradient(0, y, 0, y + len);
        gr.addColorStop(0, rgba(col, 0.95 * a)); gr.addColorStop(0.15, rgba(col, 0.5 * a)); gr.addColorStop(1, rgba(col, 0));
        ctx.fillStyle = gr; ctx.fillRect(x - 1.5, y, 3, len);
        glowDot(ctx, x, y, 18, col, 0.8 * a);
        // binary glyphs trailing
        if (i % 4 === 0) { ctx.fillStyle = rgba(col, 0.45 * a); font(ctx, 14, 700); for (let q = 1; q < 6; q++) ctx.fillText(hash(i, k, q, Math.floor(t * 6)) < 0.5 ? '0' : '1', x + 6, y + q * 20); }
      }
    }
    ctx.restore();
  }

  function boardroom(ctx, t, a) {
    if (a <= 0) return;
    const k = clamp((t - ev.boardroom + 1.2) / 8);
    ctx.save(); ctx.globalAlpha = a;
    const z = 1.06 - 0.06 * ease.inOutQuad(k);
    ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
    // room
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#07061c'); g.addColorStop(0.6, '#121040'); g.addColorStop(1, '#05041a');
    ctx.fillStyle = g; ctx.fillRect(-100, -100, W + 200, H + 200);
    const hz = H * 0.46, vx = W / 2;
    // window wall with the city beyond (the skyline, dimmed)
    ctx.save();
    ctx.beginPath(); ctx.rect(W * 0.18, H * 0.12, W * 0.64, hz - H * 0.12 + 120); ctx.clip();
    ctx.globalAlpha *= 0.7;
    ctx.drawImage(LAYERS.city2, -200 - t * 4, -H * 0.36, W + 400, H);
    ctx.drawImage(LAYERS.city1, -260 - t * 6, -H * 0.4, W + 400, H);
    ctx.restore();
    ctx.strokeStyle = 'rgba(160,190,255,0.25)'; ctx.lineWidth = 3;
    for (let i = 0; i <= 6; i++) { const x = W * 0.18 + (W * 0.64 * i) / 6; ctx.beginPath(); ctx.moveTo(x, H * 0.12); ctx.lineTo(x, hz + 120); ctx.stroke(); }
    // side walls + ceiling light strips converging
    ctx.fillStyle = '#0b0a26';
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(W * 0.18, H * 0.12); ctx.lineTo(W * 0.18, hz + 120); ctx.lineTo(0, H); ctx.fill();
    ctx.beginPath(); ctx.moveTo(W, 0); ctx.lineTo(W * 0.82, H * 0.12); ctx.lineTo(W * 0.82, hz + 120); ctx.lineTo(W, H); ctx.fill();
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (const s of [-1, 1]) { ctx.strokeStyle = rgba(C.blue, 0.55); ctx.lineWidth = 5; ctx.shadowColor = C.blue; ctx.shadowBlur = 20; ctx.beginPath(); ctx.moveTo(vx + s * 300, H * 0.12); ctx.lineTo(vx + s * 700, -20); ctx.stroke(); }
    ctx.restore();
    // floor
    ctx.fillStyle = '#070617'; ctx.fillRect(0, hz + 120, W, H);
    // the table: a long glossy trapezoid in perspective
    const ty = hz + 150;
    ctx.beginPath(); ctx.moveTo(vx - 170, ty); ctx.lineTo(vx + 170, ty); ctx.lineTo(vx + 620, H + 40); ctx.lineTo(vx - 620, H + 40); ctx.closePath();
    const tg = ctx.createLinearGradient(0, ty, 0, H);
    tg.addColorStop(0, '#2b2a5e'); tg.addColorStop(1, '#0f0e2c');
    ctx.fillStyle = tg; ctx.fill();
    ctx.strokeStyle = rgba(C.blue, 0.7); ctx.lineWidth = 2; ctx.stroke();
    // reflection of the hologram on the table
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(ctx, vx, ty + 120, 360, C.blue, 0.35 * a); ctx.restore();
    // chairs (silhouettes) along both sides
    for (let i = 0; i < 4; i++) for (const s of [-1, 1]) {
      const d = i / 3; const y = ty + 30 + d * (H - ty - 60); const x = vx + s * (230 + d * 470);
      const sz = 40 + d * 70;
      ctx.fillStyle = '#050414'; rrect(ctx, x - sz * 0.5 + s * sz * 0.25, y - sz * 1.3, sz, sz * 1.5, sz * 0.25); ctx.fill();
      ctx.strokeStyle = rgba(C.blue, 0.25); ctx.lineWidth = 1.5; ctx.stroke();
    }
    ctx.restore();
    hologram(ctx, t, a * (0.28 + 0.72 * fade(t, ev.question - 0.6, 0.8)), vx, hz + 20);
  }

  // floating holographic dashboard over the boardroom table
  function hologram(ctx, t, a, cx, cy) {
    const k = ease.outCubic(clamp((t - ev.boardroom) / 1.2));
    if (k <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha = a * k; ctx.globalCompositeOperation = 'lighter';
    const w = 520 * (0.6 + 0.4 * k), h = 250 * (0.6 + 0.4 * k);
    const x = cx - w / 2, y = cy - h - 10 + Math.sin(t * 1.4) * 6;
    // projection beam
    const bg = ctx.createLinearGradient(0, y + h, 0, cy + 110);
    bg.addColorStop(0, rgba(C.blue, 0.0)); bg.addColorStop(1, rgba(C.blue, 0.25));
    ctx.fillStyle = bg; ctx.beginPath(); ctx.moveTo(x + 40, y + h); ctx.lineTo(x + w - 40, y + h); ctx.lineTo(cx + 40, cy + 110); ctx.lineTo(cx - 40, cy + 110); ctx.fill();
    rrect(ctx, x, y, w, h, 14); ctx.fillStyle = rgba(C.blue, 0.12); ctx.fill(); ctx.strokeStyle = rgba(C.blueHi, 0.8); ctx.lineWidth = 2; ctx.stroke();
    // bars
    for (let i = 0; i < 7; i++) { const bh = (40 + 120 * hash(i, 61)) * clamp((t - ev.boardroom - 0.3 - i * 0.08) / 0.6) * (0.85 + 0.15 * Math.sin(t * 2 + i)); ctx.fillStyle = i === 4 ? rgba(C.red, 0.8) : rgba(C.blueHi, 0.7); ctx.fillRect(x + 30 + i * 32, y + h - 26 - bh, 20, bh); }
    // line chart
    ctx.strokeStyle = rgba('#ffffff', 0.9); ctx.lineWidth = 2.5; ctx.beginPath();
    for (let i = 0; i <= 20; i++) { const px = x + 280 + i * 11, py = y + h - 50 - i * 6 - 18 * Math.sin(i * 0.7 + t); if (i / 20 > clamp((t - ev.boardroom - 0.5) / 1.5)) break; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
    ctx.stroke();
    // network nodes
    for (let i = 0; i < 6; i++) { const nx = x + 300 + hash(i, 62) * 190, ny = y + 26 + hash(i, 63) * 70; ctx.fillStyle = rgba(C.blueHi, 0.9); ctx.beginPath(); ctx.arc(nx, ny, 4, 0, TAU); ctx.fill(); if (i) { ctx.strokeStyle = rgba(C.blueHi, 0.35); ctx.beginPath(); ctx.moveTo(nx, ny); ctx.lineTo(x + 300 + hash(i - 1, 62) * 190, y + 26 + hash(i - 1, 63) * 70); ctx.stroke(); } }
    ctx.restore();
  }

  // flowing data lines across the boardroom (the "overlay")
  function dataFlow(ctx, t, a) {
    if (a <= 0) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 9; i++) {
      const y0 = H * (0.2 + 0.07 * i), amp = 40 + 50 * hash(i, 71), ph = hash(i, 72) * TAU;
      const col = i % 4 === 1 ? C.red : C.blue;
      ctx.strokeStyle = rgba(col, 0.22 * a); ctx.lineWidth = 1.5; ctx.beginPath();
      for (let x = -20; x <= W + 20; x += 24) { const y = y0 + Math.sin(x / 260 + ph + t * 0.4) * amp; x < 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
      ctx.stroke();
      for (let p = 0; p < 4; p++) { const x = ((t * (180 + 80 * hash(i, p)) + hash(i, p, 3) * W) % (W + 200)) - 100; const y = y0 + Math.sin(x / 260 + ph + t * 0.4) * amp; glowDot(ctx, x, y, 16, col, 0.8 * a); }
    }
    ctx.restore();
  }

  function scene1(ctx, t) {
    const cityA = 1 - fade(t, ev.boardroom - 1.6, 1.6);
    const roomA = fade(t, ev.boardroom - 1.6, 1.6);
    if (roomA < 1) city(ctx, t, 1);
    if (roomA > 0) boardroom(ctx, t, roomA);
    streams(ctx, t, cityA * fade(t, 1.2, 1.5), 1.2);
    dataFlow(ctx, t, roomA * 0.9);
    // dim the whole background layer, then a vignette top/bottom for type
    ctx.fillStyle = 'rgba(4,3,18,0.38)'; ctx.fillRect(0, 0, W, H);
    const v = ctx.createLinearGradient(0, 0, 0, H);
    v.addColorStop(0, 'rgba(4,3,18,0.55)'); v.addColorStop(0.35, 'rgba(4,3,18,0)'); v.addColorStop(0.7, 'rgba(4,3,18,0)'); v.addColorStop(1, 'rgba(4,3,18,0.6)');
    ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);

    // --- opening heading: "Solix Academy presents / The world is entering a new era"
    const oA = win(t, 0.15, ev.title + 0.15, 0.6, 0.45);
    if (oA > 0) {
      kicker(ctx, 'SOLIX ACADEMY PRESENTS', W / 2, H * 0.4, oA, C.blueHi, 'center');
      rich(ctx, [{ s: 'The world is entering ', c: '#ffffff', weight: 300, t: 0.35 }, { s: 'a new era', c: C.blueHi, glow: 18, t: wordT('l01', 'new') - 0.1 }], W / 2, H * 0.4 + 96, { size: 72, weight: 800, align: 'center', alpha: oA, t });
    }
    // --- title: "Reimagining Enterprise AI" (0:02), then it rises to a header
    const up = ease.inOutCubic(fade(t, V.l02.words[3].t - 0.5, 0.8)); // moves up as "every enterprise" begins
    const tA = win(t, ev.title, ev.question - 0.1, 0.6, 0.5);
    if (tA > 0) {
      const ty = lerp(H * 0.47, H * 0.2, up), sz = lerp(104, 64, up);
      // sweep reveal (clip widening from the centre)
      const kr = ease.outCubic(fade(t, ev.title, 1.1));
      ctx.save(); ctx.beginPath(); const hw = (W / 2) * kr; ctx.rect(W / 2 - hw, 0, hw * 2, H); ctx.clip();
      rich(ctx, [{ s: 'Reimagining ', c: '#ffffff', weight: 300 }, { s: 'Enterprise AI', c: C.blueHi, glow: 26 }], W / 2, ty, { size: sz, weight: 800, align: 'center', alpha: tA });
      ctx.restore();
      // the sweep line itself
      if (kr < 1) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; for (const s of [-1, 1]) { const x = W / 2 + s * hw; const lg = ctx.createLinearGradient(0, ty - 120, 0, ty + 60); lg.addColorStop(0, rgba(C.blueHi, 0)); lg.addColorStop(0.5, rgba(C.blueHi, 0.45)); lg.addColorStop(1, rgba(C.blueHi, 0)); ctx.fillStyle = lg; ctx.fillRect(x - 2, ty - 120, 4, 180); glowDot(ctx, x, ty - 30, 40, C.blueHi, 0.3); } ctx.restore(); }

    }
    // --- "every enterprise / every business function / every employee" chips
    const chipA = win(t, V.l02.words[3].t, ev.question - 0.1, 0.4, 0.5);
    if (chipA > 0) {
      const items = [['building', 'Every enterprise', V.l02.words[3].t], ['gear', 'Every business function', V.l02.words[5].t], ['person', 'Every employee', V.l02.words[9].t]];
      const cw = 530, gap = 30, x0 = W / 2 - (cw * 3 + gap * 2) / 2, y = H * 0.36;
      items.forEach(([ic, label, t0], i) => {
        const k = ease.outBack(clamp((t - t0) / 0.5), 1.6);
        const a = chipA * clamp((t - t0) / 0.3);
        if (a <= 0) return;
        const x = x0 + i * (cw + gap), yy = y + (1 - k) * 40;
        ctx.save(); ctx.globalAlpha = a;
        rrect(ctx, x, yy, cw, 110, 18); ctx.fillStyle = 'rgba(16,14,52,0.72)'; ctx.fill();
        ctx.strokeStyle = rgba(C.blue, 0.85); ctx.lineWidth = 2; ctx.stroke();
        ctx.fillStyle = C.blue; ctx.fillRect(x, yy + 24, 5, 62);
        ctx.restore();
        icon(ctx, ic, x + 62, yy + 55, 46, C.blueHi, a);
        text(ctx, label, x + 108, yy + 67, { size: 33, weight: 700, color: '#fff', alpha: a });
      });
      // "reimagined through Artificial Intelligence"
      const r0 = wordT('l02', 'reimagined');
      rich(ctx, [{ s: 'can be ', c: '#dfe6ff', weight: 400, t: r0 - 0.35 }, { s: 'reimagined', c: C.red, glow: 18, t: r0 }, { s: ' through ', c: '#dfe6ff', weight: 400, t: r0 + 0.4 }, { s: 'Artificial Intelligence', c: C.blueHi, t: wordT('l02', 'artificial'), glow: 16 }],
        W / 2, H * 0.36 + 230, { size: 52, weight: 800, align: 'center', alpha: chipA, t });
    }
    // --- the question
    const qA = win(t, ev.question, S.S.intro[1] + 0.1, 0.5, 0.5);
    if (qA > 0) {
      kicker(ctx, 'THE QUESTION', W / 2, H * 0.68 - 104, qA, C.blueHi, 'center');
      const q0 = ev.question;
      rich(ctx, [{ s: 'How do organizations make this', c: '#ffffff', weight: 700, t: q0 }], W / 2, H * 0.68, { size: 60, align: 'center', alpha: qA, t });
      rich(ctx, [{ s: 'transformation ', c: C.blueHi, weight: 800, t: wordT('l03', 'transformation'), glow: 18 }, { s: 'a ', c: '#fff', t: wordT('l03', 'reality') - 0.2 }, { s: 'reality?', c: '#fff', pill: C.red, t: wordT('l03', 'reality') }], W / 2, H * 0.68 + 86, { size: 68, weight: 800, align: 'center', alpha: qA, t });
    }
  }
  const wordT = S.wordT;

  // ================================================================ SCENE 2: the three pillars
  const PILLARS = [
    { name: 'Data', icon: 'database', col: C.blue, hi: C.blueHi, sub: ['Structured, governed', 'information behind AI'], t: ev.pillar[0] },
    { name: 'People', icon: 'people', col: C.red, hi: '#ff5a5a', sub: ['A workforce that leads', 'AI transformation'], t: ev.pillar[1] },
    { name: 'Governance', icon: 'shield', col: C.indigo, hi: '#8d7bff', sub: ['A trusted foundation for', 'secure, scalable value'], t: ev.pillar[2] },
  ];
  // an isometric metallic prism (base centre bx, by), width w, height h
  function prism(ctx, bx, by, w, h, col, hi, glow, active) {
    const dx = w / 2, dy = w / 4;
    const top = by - h;
    // left face
    let g = ctx.createLinearGradient(bx - dx, 0, bx, 0);
    g.addColorStop(0, G.tint(col, -0.35)); g.addColorStop(1, G.tint(col, 0.05));
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(bx - dx, top); ctx.lineTo(bx, top + dy); ctx.lineTo(bx, by + dy); ctx.lineTo(bx - dx, by); ctx.closePath(); ctx.fill();
    // right face
    g = ctx.createLinearGradient(bx, 0, bx + dx, 0);
    g.addColorStop(0, G.tint(col, -0.45)); g.addColorStop(1, G.tint(col, -0.7));
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(bx, top + dy); ctx.lineTo(bx + dx, top); ctx.lineTo(bx + dx, by); ctx.lineTo(bx, by + dy); ctx.closePath(); ctx.fill();
    // metallic sheen bands
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const sh = ctx.createLinearGradient(0, top, 0, by);
    sh.addColorStop(0, 'rgba(255,255,255,0.22)'); sh.addColorStop(0.4, 'rgba(255,255,255,0.02)'); sh.addColorStop(0.75, 'rgba(255,255,255,0.08)'); sh.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = sh; ctx.beginPath(); ctx.moveTo(bx - dx, top); ctx.lineTo(bx, top + dy); ctx.lineTo(bx, by + dy); ctx.lineTo(bx - dx, by); ctx.closePath(); ctx.fill();
    ctx.restore();
    // top face
    g = ctx.createLinearGradient(bx - dx, top - dy, bx + dx, top + dy);
    g.addColorStop(0, G.tint(hi, 0.35)); g.addColorStop(1, G.tint(col, 0.1));
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(bx, top - dy); ctx.lineTo(bx + dx, top); ctx.lineTo(bx, top + dy); ctx.lineTo(bx - dx, top); ctx.closePath(); ctx.fill();
    // glowing edges
    ctx.save(); ctx.strokeStyle = rgba(hi, 0.5 + 0.5 * glow); ctx.lineWidth = active ? 2.5 : 1.5; ctx.shadowColor = hi; ctx.shadowBlur = 16 * glow;
    ctx.beginPath(); ctx.moveTo(bx, top - dy); ctx.lineTo(bx + dx, top); ctx.lineTo(bx, top + dy); ctx.lineTo(bx - dx, top); ctx.closePath();
    ctx.moveTo(bx, top + dy); ctx.lineTo(bx, by + dy); ctx.moveTo(bx - dx, top); ctx.lineTo(bx - dx, by); ctx.moveTo(bx + dx, top); ctx.lineTo(bx + dx, by);
    ctx.stroke(); ctx.restore();
  }

  function scene2(ctx, t) {
    const t0 = S.S.pillars[0];
    backdrop(ctx, t, { glowY: H * 0.62, blue: 0.3 });
    plexus(ctx, t, { a: fade(t, t0, 0.8), cy: H * 0.4, seed: 1.3 });
    floorLight(ctx, t, H * 0.68, fade(t, t0, 0.8));
    bokeh(ctx, t, 26, 0.35, 2);
    ctx.fillStyle = 'rgba(4,3,18,0.25)'; ctx.fillRect(0, 0, W, H);
    // which pillar is speaking
    // gentle camera drift toward the speaking pillar, eased between targets (never a jump)
    let focus = 0;
    for (const [tk, v] of [[ev.pillar[0] - 0.2, -70], [ev.pillar[1] - 0.2, 0], [ev.pillar[2] - 0.2, 70], [ev.pillarsTag - 0.3, 0]]) focus = lerp(focus, v, ease.inOutCubic(clamp((t - tk) / 1.0)));
    const camX = 0;
    // how much each pillar is emphasised (0..1), cross-faded instead of switched
    const allK = ease.inOutQuad(fade(t, ev.pillarsTag - 0.3, 0.8));
    const emph = (i) => Math.max(allK, win(t, ev.pillar[i] - 0.05, i < 2 ? ev.pillar[i + 1] + 0.25 : 1e9, 0.5, 0.6));
    ctx.save();
    const zoom = 1 + 0.04 * Math.sin((t - t0) * 0.2);
    ctx.translate(W / 2, H * 0.6); ctx.scale(zoom, zoom); ctx.translate(-W / 2 - focus * 0.6 + camX, -H * 0.6);

    const baseY = H * 0.655, xs = [W / 2 - 470, W / 2, W / 2 + 470], pw = 230;
    // the foundation slab ("trusted foundation") under all three
    const fk = ease.outCubic(fade(t, ev.pillarsTag, 0.8));
    if (fk > 0) {
      ctx.save(); ctx.globalAlpha = fk;
      const sw = 1260, sd = sw / 4 * 0.32;
      ctx.fillStyle = 'rgba(30,26,90,0.9)';
      ctx.beginPath(); ctx.moveTo(W / 2 - sw / 2, baseY + 40); ctx.lineTo(W / 2, baseY + 40 + sd); ctx.lineTo(W / 2 + sw / 2, baseY + 40); ctx.lineTo(W / 2, baseY + 40 - sd); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = rgba(C.blueHi, 0.9); ctx.lineWidth = 2; ctx.shadowColor = C.blue; ctx.shadowBlur = 24; ctx.stroke();
      ctx.restore();
    }
    // platforms
    PILLARS.forEach((p, i) => {
      const k = clamp((t - p.t) / 0.9);
      const x = xs[i], dx = pw / 2 + 30, dy = dx / 2;
      ctx.save(); ctx.globalAlpha = 0.35 + 0.65 * clamp((t - t0 - i * 0.2) / 0.6);
      ctx.strokeStyle = rgba(p.hi, 0.5 + 0.5 * k); ctx.lineWidth = 2; ctx.shadowColor = p.hi; ctx.shadowBlur = 20 * k;
      ctx.beginPath(); ctx.moveTo(x, baseY - dy); ctx.lineTo(x + dx, baseY); ctx.lineTo(x, baseY + dy); ctx.lineTo(x - dx, baseY); ctx.closePath(); ctx.stroke();
      ctx.fillStyle = rgba(p.col, 0.12 + 0.12 * k); ctx.fill();
      ctx.restore();
      if (k > 0) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(ctx, x, baseY, 260, p.hi, 0.35 * k); ctx.restore(); }
    });
    // the pillars rise
    PILLARS.forEach((p, i) => {
      const k = clamp((t - p.t) / 0.9);
      if (k <= 0) return;
      const h = 330 * ease.outBack(k, 1.3);
      const e = emph(i);
      ctx.save(); ctx.globalAlpha = 0.8 + 0.2 * e;
      prism(ctx, xs[i], baseY, pw, h, p.col, p.hi, 0.35 + 0.6 * e, e > 0.5);
      ctx.restore();
      // impact ring at the base + a flare off the top edge
      shockRing(ctx, xs[i], baseY, t, p.t, { color: p.hi, r1: 260, d: 0.8, lw: 4 });

      // the icon floats above
      const ik = ease.outBack(clamp((t - p.t - 0.35) / 0.5), 2);
      const iy = baseY - h - 125 + Math.sin(t * 1.6 + i) * 6;
      if (ik > 0) {
        ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(ctx, xs[i], iy, 120, p.hi, 0.5 * ik); ctx.restore();
        ctx.save(); ctx.translate(xs[i], iy); ctx.scale(ik, ik); icon(ctx, p.icon, 0, 0, 74, '#ffffff', 1, 4); ctx.restore();
      }
    });
    ctx.restore();

    // labels under each pillar (screen space so they stay crisp)
    PILLARS.forEach((p, i) => {
      const k = ease.outCubic(clamp((t - p.t - 0.25) / 0.5));
      if (k <= 0) return;
      const x = xs[i] - focus * 0.6, y = baseY + 160;
      text(ctx, '0' + (i + 1), x, y - 50 + (1 - k) * 18, { size: 26, weight: 800, color: p.hi === '#8d7bff' ? '#a99bff' : p.hi, align: 'center', alpha: k, spacing: 4 });
      rich(ctx, [{ s: 'AI-Ready ', c: '#ffffff', weight: 700 }, { s: p.name, c: '#ffffff', pill: p.col, weight: 800 }], x, y + (1 - k) * 18, { size: 44, align: 'center', alpha: k });
      const sk = clamp((t - p.t - 1.2) / 0.5) * (0.55 + 0.45 * emph(i));
      p.sub.forEach((ln, j) => text(ctx, ln, x, y + 52 + j * 34, { size: 27, weight: 600, color: '#e3e9ff', align: 'center', alpha: sk * k }));
    });

    // header kicker
    const hk = win(t, V.l04.t - 0.1, S.S.pillars[1] + 0.2, 0.5, 0.4);
    kicker(ctx, 'THREE ESSENTIAL PILLARS', W / 2, 118, hk, C.blueHi, 'center');
    const tagA = ease.outCubic(fade(t, ev.pillarsTag + 0.3, 0.6));
    const big = 1 - fade(t, ev.pillar[0] - 0.3, 0.5);
    if (big > 0) rich(ctx, [{ s: 'It starts with ', c: '#fff', weight: 300 }, { s: 'three essential pillars', c: C.blueHi, glow: 20 }], W / 2, H * 0.36, { size: 70, align: 'center', alpha: big * fade(t, V.l04.t, 0.5) });
    if (tagA > 0) {
      rich(ctx, [{ s: 'Data', c: C.blueHi }, { s: '  •  ', c: '#8090c0', weight: 400 }, { s: 'People', c: '#ff5a5a' }, { s: '  •  ', c: '#8090c0', weight: 400 }, { s: 'Governance', c: '#a99bff' }], W / 2, 196, { size: 54, weight: 800, align: 'center', alpha: tagA * win(t, 0, S.S.pillars[1] + 0.2, 0, 0.4) });
    }
    flash(ctx, t, t0, { a: 0.1, color: '#9fd8ff' });
  }

  // ================================================================ SCENE 3: Solix Academy
  const COURSES = [
    ['AI Fundamentals', 'Foundations', C.blue], ['Generative AI', 'Intermediate', C.red], ['Data Engineering for AI', 'Intermediate', C.indigo],
    ['MLOps in Production', 'Advanced', C.blue], ['Agentic AI Systems', 'Advanced', C.red], ['RAG & Knowledge Graphs', 'Advanced', C.indigo],
  ];
  function courseCard(ctx, x, y, w, h, c, a, t, i) {
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a;
    ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 12;
    rrect(ctx, x, y, w, h, 16); ctx.fillStyle = '#ffffff'; ctx.fill();
    ctx.shadowColor = 'transparent';
    // header band
    ctx.save(); rrect(ctx, x, y, w, h, 16); ctx.clip();
    const g = ctx.createLinearGradient(x, y, x + w, y + 70);
    g.addColorStop(0, c[2]); g.addColorStop(1, G.tint(c[2], 0.25));
    ctx.fillStyle = g; ctx.fillRect(x, y, w, 64);
    ctx.restore();
    text(ctx, c[1].toUpperCase(), x + 22, y + 40, { size: 17, weight: 700, color: '#ffffff', spacing: 3 });
    text(ctx, c[0], x + 22, y + 108, { size: 27, weight: 800, color: C.indigo });
    // progress bar
    ctx.fillStyle = '#e6e9f5'; rrect(ctx, x + 22, y + h - 40, w - 44, 10, 5); ctx.fill();
    ctx.fillStyle = c[2]; rrect(ctx, x + 22, y + h - 40, (w - 44) * (0.25 + 0.6 * hash(i, 81)) * clamp((t - 0.3) / 1.2), 10, 5); ctx.fill();
    ctx.restore();
  }

  // lab window chrome
  function labWindow(ctx, x, y, w, h, title, tag, a, draw) {
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a;
    ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 20;
    rrect(ctx, x, y, w, h, 18); ctx.fillStyle = '#0e0c2e'; ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.strokeStyle = rgba(C.blue, 0.8); ctx.lineWidth = 2; ctx.stroke();
    // title bar
    ctx.save(); rrect(ctx, x, y, w, h, 18); ctx.clip(); ctx.fillStyle = '#ffffff'; ctx.fillRect(x, y, w, 56); ctx.restore();
    ['#ee2424', '#f5b400', '#2bb673'].forEach((c, i) => { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(x + 26 + i * 22, y + 28, 7, 0, TAU); ctx.fill(); });
    text(ctx, title, x + 104, y + 37, { size: 22, weight: 800, color: C.indigo });
    const tw = measure(ctx, tag, 16, 700, 2) + 28;
    rrect(ctx, x + w - tw - 18, y + 14, tw, 28, 14); ctx.fillStyle = C.red; ctx.fill();
    text(ctx, tag, x + w - tw / 2 - 18, y + 34, { size: 16, weight: 700, color: '#fff', align: 'center', spacing: 2 });
    ctx.save(); ctx.translate(x, y + 56); draw(ctx, w, h - 56); ctx.restore();
    ctx.restore();
  }
  function node(ctx, x, y, w, h, label, on, col = C.blue) {
    rrect(ctx, x, y, w, h, 12); ctx.fillStyle = on ? rgba(col, 0.25) : 'rgba(255,255,255,0.05)'; ctx.fill();
    ctx.strokeStyle = on ? rgba(col === C.indigo ? '#8d7bff' : col, 1) : 'rgba(255,255,255,0.2)'; ctx.lineWidth = 2; ctx.stroke();
    text(ctx, label, x + w / 2, y + h / 2 + 8, { size: 21, weight: 700, color: on ? '#fff' : '#9aa6cc', align: 'center' });
  }
  function arrow(ctx, x1, y1, x2, y2, k, col = C.blueHi) {
    if (k <= 0) return;
    const x = lerp(x1, x2, k), y = lerp(y1, y2, k);
    ctx.strokeStyle = rgba(col, 0.9); ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x, y); ctx.stroke();
    if (k >= 1) { const an = Math.atan2(y2 - y1, x2 - x1); ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x2 - 12 * Math.cos(an - 0.45), y2 - 12 * Math.sin(an - 0.45)); ctx.lineTo(x2 - 12 * Math.cos(an + 0.45), y2 - 12 * Math.sin(an + 0.45)); ctx.fill(); }
  }
  function check(ctx, x, y, k) {
    if (k <= 0) return;
    ctx.fillStyle = '#2bb673'; ctx.beginPath(); ctx.arc(x, y, 11 * ease.outBack(k, 2), 0, TAU); ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(x - 5, y); ctx.lineTo(x - 1, y + 4); ctx.lineTo(x + 6, y - 4); ctx.stroke();
  }
  const LABS = [
    { title: 'MLOps Pipeline Lab', tag: 'HANDS-ON LAB', draw(ctx, w, h, u) {
      const steps = ['Data', 'Train', 'Evaluate', 'Deploy', 'Monitor'];
      const nw = 132, gap = (w - 60 - nw * 5) / 4;
      steps.forEach((s, i) => {
        const on = u > i * 0.17, x = 30 + i * (nw + gap), y = 70;
        node(ctx, x, y, nw, 60, s, on, i === 3 ? C.red : C.blue);
        if (i < 4) arrow(ctx, x + nw + 4, y + 30, x + nw + gap - 4, y + 30, clamp((u - i * 0.17) / 0.12));
        check(ctx, x + nw - 6, y + 4, clamp((u - i * 0.17 - 0.1) / 0.08));
      });
      // metrics chart
      ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 1; for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(30, 190 + i * 40); ctx.lineTo(w - 30, 190 + i * 40); ctx.stroke(); }
      ctx.strokeStyle = C.blueHi; ctx.lineWidth = 3; ctx.beginPath();
      for (let i = 0; i <= 40 * clamp(u * 1.2); i++) { const x = 30 + (i / 40) * (w - 60), y = 300 - 100 * (1 - Math.exp(-i / 10)) - 6 * Math.sin(i); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
      ctx.stroke();
      text(ctx, 'model accuracy  ' + (80 + 14.6 * clamp(u * 1.2)).toFixed(1) + '%', 30, 360, { size: 20, weight: 700, color: '#c9d3f5' });
    } },
    { title: 'Agentic AI Lab', tag: 'HANDS-ON LAB', draw(ctx, w, h, u) {
      const rows = [['Goal', 'Reconcile Q3 vendor invoices', C.indigo], ['Plan', 'Split into 3 sub-tasks', C.blue], ['Tool call', 'query_erp(vendor, quarter=Q3)', C.red], ['Observe', '1,284 records - 6 mismatches', C.blue], ['Answer', 'Report drafted, approvals routed', '#2bb673']];
      rows.forEach(([k, v, col], i) => {
        const a = clamp((u - i * 0.16) / 0.12);
        if (a <= 0) return;
        const y = 28 + i * 66;
        ctx.save(); ctx.globalAlpha *= a;
        rrect(ctx, 30, y + (1 - a) * 12, w - 60, 54, 12); ctx.fillStyle = 'rgba(255,255,255,0.06)'; ctx.fill();
        ctx.fillStyle = col; ctx.fillRect(30, y + (1 - a) * 12 + 10, 5, 34);
        text(ctx, k.toUpperCase(), 52, y + 34 + (1 - a) * 12, { size: 17, weight: 800, color: col === C.indigo ? '#a99bff' : col, spacing: 2 });
        text(ctx, v, 200, y + 35 + (1 - a) * 12, { size: 22, weight: 700, color: '#ffffff' });
        ctx.restore();
      });
    } },
    { title: 'RAG Systems Lab', tag: 'HANDS-ON LAB', draw(ctx, w, h, u) {
      node(ctx, 30, 40, 170, 60, 'Query', u > 0.02);
      node(ctx, 30, 160, 170, 60, 'Retriever', u > 0.2, C.red);
      node(ctx, 30, 280, 170, 60, 'LLM', u > 0.55, C.indigo);
      arrow(ctx, 115, 104, 115, 156, clamp((u - 0.08) / 0.1));
      arrow(ctx, 115, 224, 115, 276, clamp((u - 0.45) / 0.1));
      ['policy_handbook.pdf  0.92', 'contract_2025.docx  0.88', 'kb/returns.md  0.81'].forEach((d, i) => {
        const a = clamp((u - 0.25 - i * 0.08) / 0.1);
        if (a <= 0) return;
        const y = 150 + i * 46;
        ctx.save(); ctx.globalAlpha *= a; rrect(ctx, 250, y, w - 280, 38, 8); ctx.fillStyle = 'rgba(0,136,207,0.16)'; ctx.fill(); ctx.restore();
        text(ctx, d, 266, y + 26, { size: 19, weight: 700, color: '#dfe6ff', alpha: a });
      });
      const ak = clamp((u - 0.62) / 0.3);
      if (ak > 0) {
        rrect(ctx, 250, 40, w - 280, 76, 10); ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fill();
        const ans = 'Refunds are processed within 14 days [1][3]';
        text(ctx, ans.slice(0, Math.round(ans.length * ak)), 266, 86, { size: 21, weight: 700, color: '#ffffff' });
      }
    } },
  ];

  function scene3(ctx, t) {
    const t0 = S.S.academy[0];
    backdrop(ctx, t, { glowX: W * 0.5, glowY: H * 0.48, blue: 0.4, red: 0.16, bottom: '#1d1658' });
    // rotating rings behind the logo
    const ringA = 1 - fade(t, ev.platform, 0.8);
    if (ringA > 0) {
      ctx.save(); ctx.translate(W / 2, H / 2); ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 4; i++) { ctx.rotate(t * 0.12 * (i % 2 ? -1 : 1)); ctx.strokeStyle = rgba(i % 2 ? C.red : C.blue, 0.22 * ringA); ctx.lineWidth = 2; ctx.setLineDash([40 + i * 20, 18]); ctx.beginPath(); ctx.arc(0, 0, 300 + i * 90, 0, TAU); ctx.stroke(); }
      ctx.setLineDash([]); ctx.restore();
    }
    bokeh(ctx, t, 30, 0.4, 3);
    plexus(ctx, t, { a: 0.85, cy: H * 0.5, seed: 4.1, speed: 0.04 });
    ctx.fillStyle = 'rgba(4,3,18,0.3)'; ctx.fillRect(0, 0, W, H);
    { const sa = fade(t, ev.platform, 0.6); if (sa > 0) { const g = ctx.createLinearGradient(0, 0, W * 0.55, 0); g.addColorStop(0, `rgba(5,4,22,${0.75 * sa})`); g.addColorStop(1, 'rgba(5,4,22,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W * 0.55, H); } }

    // --- logo: full-screen reveal, then it docks top-left
    const dock = ease.inOutCubic(fade(t, ev.platform - 0.1, 0.8));
    const lw = lerp(1320, 420, dock), lx = lerp(W / 2, 64 + 210, dock), ly = lerp(H * 0.46, 82, dock);
    if (t < ev.logo + 0.2) {
      // gathering light before the hit
      const g = clamp((t - (ev.logo - 0.9)) / 0.9);
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(ctx, W / 2, H * 0.46, 500 * g, C.blueHi, 0.6 * g * g); ctx.restore();
    }
    kicker(ctx, 'INTRODUCING', W / 2, H * 0.46 - 160, win(t, V.l08.t - 0.1, ev.logo + 0.6, 0.35, 0.4), C.blueHi, 'center');
    const L = acadLogo(ctx, lx, ly, lw, t, { tIcon: ev.logo - 0.12, tSolix: ev.logo + 0.02, tAcad: ev.academyWord, tTag: ev.academyWord + 0.45 });
    shockRing(ctx, L.iconX, L.iconY, t, ev.logo, { color: C.red, r1: 700, d: 0.9, lw: 4 });
    flash(ctx, t, ev.logo, { a: 0.18 });
    lensFlare(ctx, L.iconX, L.iconY, t, ev.logo, { color: C.red, dur: 0.9, size: 0.45 });

    // --- the platform: headline + floating course cards
    const platA = win(t, ev.platform + 0.2, ev.experts + 0.1, 0.5, 0.45);
    if (platA > 0) {
      kicker(ctx, 'A PREMIER LEARNING PLATFORM', 140, 330, platA);
      rich(ctx, [{ s: 'Embrace AI ', c: '#fff', t: ev.platform + 0.3 }, { s: 'faster', c: C.red, glow: 16, t: wordT('l09', 'faster') }], 140, 430, { size: 76, alpha: platA, t });
      rich(ctx, [{ s: 'and with ', c: '#fff', weight: 300, t: wordT('l09', 'and') }, { s: 'confidence.', c: C.blueHi, glow: 16, t: wordT('l09', 'confidence') }], 140, 520, { size: 76, alpha: platA, t });
      text(ctx, 'Built for enterprises adopting AI at scale', 142, 590, { size: 28, weight: 400, color: '#c9d3f5', alpha: platA * fade(t, ev.platform + 1.5, 0.6) });
    }
    const cardsA = win(t, ev.platform + 0.2, ev.labs[0] + 0.3, 0.5, 0.6);
    if (cardsA > 0) {
      COURSES.forEach((c, i) => {
        const ti = ev.platform + 0.25 + i * 0.22;
        const k = ease.outCubic(clamp((t - ti) / 0.7));
        const col = i % 2, row = Math.floor(i / 2);
        const bx = 1080 + col * 380 + (row % 2) * 40, by = 250 + row * 230;
        const fl = Math.sin(t * 0.9 + i) * 8;
        courseCard(ctx, bx + (1 - k) * 500, by + fl, 350, 200, c, cardsA * k, t - ti, i);
      });
    }
    // --- the experts
    const exA = win(t, ev.experts - 0.1, ev.labs[0] + 0.1, 0.4, 0.4);
    if (exA > 0) {
      kicker(ctx, 'BUILT BY', 140, 330, exA);
      const ex = [['cap', 'Distinguished', 'Professors', C.blue, wordT('l10', 'distinguished')], ['chip', 'Leading AI', 'Practitioners', C.red, wordT('l10', 'leading')], ['briefcase', 'Industry', 'Experts', '#8d7bff', wordT('l10', 'industry')]];
      ex.forEach(([ic, a1, a2, col, ti], i) => {
        const k = ease.outBack(clamp((t - ti + 0.15) / 0.5), 1.5);
        const a = exA * clamp((t - ti + 0.15) / 0.3);
        if (a <= 0) return;
        const y = 380 + i * 150 + (1 - k) * 30;
        ctx.save(); ctx.globalAlpha = a;
        rrect(ctx, 140, y, 760, 124, 20); ctx.fillStyle = 'rgba(16,14,52,0.78)'; ctx.fill(); ctx.strokeStyle = rgba(col, 0.9); ctx.lineWidth = 2; ctx.stroke();
        ctx.restore();
        ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(ctx, 214, y + 62, 70, col, 0.5 * a); ctx.restore();
        icon(ctx, ic, 214, y + 62, 56, '#ffffff', a, 3.5);
        text(ctx, a1, 290, y + 56, { size: 28, weight: 400, color: '#c9d3f5', alpha: a });
        text(ctx, a2, 290, y + 96, { size: 38, weight: 800, color: col === '#8d7bff' ? '#b4a8ff' : col === C.blue ? C.blueHi : '#ff5a5a', alpha: a });
      });
    }
    // --- hands-on labs: three lab windows glide in, one after another
    const labsA = win(t, ev.labs[0] - 0.4, ev.paths + 0.3, 0.4, 0.5);
    if (labsA > 0) {
      kicker(ctx, 'LEARN BY DOING', 140, 300, labsA);
      rich(ctx, [{ s: 'Hands-on labs', c: C.blueHi, glow: 14 }], 140, 384, { size: 64, alpha: labsA });
      rich(ctx, [{ s: '& real-world projects', c: '#ffffff', weight: 700 }], 140, 456, { size: 50, alpha: labsA * fade(t, wordT('l11', 'real-world') - 0.1, 0.4) });
      // path: AI Fundamentals -> Production-grade Engineering
      const pk = clamp((t - wordT('l11', 'from')) / 2.0);
      if (pk > 0) {
        const x0 = 150, x1 = 760, y = 600;
        ctx.save(); ctx.globalAlpha = labsA;
        ctx.strokeStyle = 'rgba(255,255,255,0.18)'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke();
        const g = ctx.createLinearGradient(x0, 0, x1, 0); g.addColorStop(0, C.blue); g.addColorStop(1, C.red);
        ctx.strokeStyle = g; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(lerp(x0, x1, ease.inOutQuad(pk)), y); ctx.stroke();
        ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(lerp(x0, x1, ease.inOutQuad(pk)), y, 10, 0, TAU); ctx.fill();
        ctx.restore();
        text(ctx, 'AI Fundamentals', x0 - 8, y + 50, { size: 24, weight: 700, color: C.blueHi, alpha: labsA });
        text(ctx, 'Production-grade Engineering', x1 + 8, y + 50, { size: 24, weight: 700, color: '#ff5a5a', align: 'right', alpha: labsA * clamp(pk * 1.6 - 0.4) });
      }
      LABS.forEach((L, i) => {
        const ti = ev.labs[i];
        const kin = ease.outCubic(clamp((t - ti + 0.25) / 0.7));
        if (kin <= 0) return;
        const nxt = i < 2 ? ease.inOutCubic(clamp((t - ev.labs[i + 1] + 0.25) / 0.7)) : 0;
        // the current window sits front-right; the previous one steps back and up
        const x = 990 + (1 - kin) * 900 - nxt * 60, y = 300 - nxt * 150, s = 1 - nxt * 0.16;
        const a = labsA * kin * (1 - nxt * 0.55);
        ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
        labWindow(ctx, 0, 0, 800, 470, L.title, L.tag, a, (c, w, h) => L.draw(c, w, h, clamp((t - ti) / 1.8)));
        ctx.restore();
      });
    }
    // --- 150+ learning paths, self-paced & instructor-led
    const pA = win(t, ev.paths - 0.2, S.S.academy[1] + 0.3, 0.4, 0.5);
    if (pA > 0) {
      const n = Math.round(150 * ease.outCubic(clamp((t - ev.paths) / 1.2)));
      const x = W / 2;
      ctx.save(); ctx.globalAlpha = pA; ctx.fillStyle = 'rgba(8,7,30,0.55)'; ctx.fillRect(0, 0, W, H); ctx.restore();
      text(ctx, n + '+', x, H * 0.47, { size: 220, weight: 800, color: C.blueHi, align: 'center', alpha: pA, glow: 40, glowColor: C.blue });
      text(ctx, 'LEARNING PATHS', x, H * 0.47 + 76, { size: 44, weight: 800, color: '#ffffff', align: 'center', alpha: pA, spacing: 10 });
      const pk = ease.outBack(clamp((t - wordT('l12', 'self-paced')) / 0.45), 1.6), ik = ease.outBack(clamp((t - wordT('l12', 'instructor-led')) / 0.45), 1.6);
      const py = H * 0.47 + 150;
      for (const [label, col, k, dx] of [['Self-Paced', C.blue, pk, -190], ['Instructor-Led', C.red, ik, 190]]) {
        if (k <= 0) continue;
        const w = measure(ctx, label, 36, 800) + 70;
        ctx.save(); ctx.globalAlpha = pA * clamp(k); ctx.translate(x + dx, py); ctx.scale(k, k);
        rrect(ctx, -w / 2, -34, w, 68, 34); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 30; ctx.fill(); ctx.restore();
        ctx.save(); ctx.translate(x + dx, py); ctx.scale(k, k); text(ctx, label, 0, 13, { size: 36, weight: 800, color: '#fff', align: 'center', alpha: pA * clamp(k) }); ctx.restore();
      }
    }
    flash(ctx, t, t0, { a: 0.1, color: '#ffd7d7' });
  }

  // ================================================================ SCENE 4: mission, teams, end card
  // a stylised team around a glowing table, connected by light
  function team(ctx, t, a) {
    if (a <= 0) return;
    const k = clamp((t - ev.finale) / (ev.endcard - ev.finale));
    ctx.save(); ctx.globalAlpha = a;
    const z = 1 + 0.08 * ease.inOutQuad(k);
    ctx.translate(W * 0.68, H * 0.62); ctx.scale(z, z); ctx.translate(-W * 0.68, -H * 0.62);
    const cx = W * 0.68, cy = H * 0.66;
    // table glow
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(ctx, cx, cy, 520, C.blue, 0.45); glowDot(ctx, cx, cy - 120, 260, C.blueHi, 0.25); ctx.restore();
    ctx.beginPath(); ctx.ellipse(cx, cy, 380, 110, 0, 0, TAU);
    const tg = ctx.createRadialGradient(cx, cy, 20, cx, cy, 380); tg.addColorStop(0, '#3a4fb8'); tg.addColorStop(1, '#141244');
    ctx.fillStyle = tg; ctx.fill(); ctx.strokeStyle = rgba(C.blueHi, 0.9); ctx.lineWidth = 3; ctx.shadowColor = C.blue; ctx.shadowBlur = 30; ctx.stroke(); ctx.shadowBlur = 0;
    // a hologram over the table: a rotating network globe
    const gy = cy - 190;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const pts = [];
    for (let i = 0; i < 26; i++) { const th = hash(i, 91) * TAU + t * 0.4, ph = Math.acos(2 * hash(i, 92) - 1); const x = Math.sin(ph) * Math.cos(th), y = Math.cos(ph), zz = Math.sin(ph) * Math.sin(th); pts.push([cx + x * 120, gy + y * 120, zz]); }
    ctx.strokeStyle = rgba(C.blueHi, 0.25); ctx.lineWidth = 1.2;
    for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) { const d = Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]); if (d < 80) { ctx.beginPath(); ctx.moveTo(pts[i][0], pts[i][1]); ctx.lineTo(pts[j][0], pts[j][1]); ctx.stroke(); } }
    for (const [x, y, zz] of pts) glowDot(ctx, x, y, 10 + 6 * zz, zz > 0.3 ? C.red : C.blueHi, 0.6 + 0.4 * zz);
    ctx.restore();
    // people: silhouettes with rim light, seated around the far side and standing at the ends
    const seats = [[-300, -40, 1.0], [-160, -78, 0.92], [0, -92, 0.9], [160, -78, 0.92], [300, -40, 1.0], [-470, 30, 1.18], [470, 30, 1.18]];
    // connections between them (collaboration)
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    seats.forEach(([sx, sy], i) => { const nx = seats[(i + 2) % seats.length]; const pk = (t * 0.6 + i * 0.3) % 1; ctx.strokeStyle = rgba(i % 3 ? C.blueHi : C.red, 0.28); ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(cx + sx, cy + sy - 120); ctx.quadraticCurveTo(cx, gy - 60, cx + nx[0], cy + nx[1] - 120); ctx.stroke(); const bx = (1 - pk) * (1 - pk) * (cx + sx) + 2 * pk * (1 - pk) * cx + pk * pk * (cx + nx[0]); const by = (1 - pk) * (1 - pk) * (cy + sy - 120) + 2 * pk * (1 - pk) * (gy - 60) + pk * pk * (cy + nx[1] - 120); glowDot(ctx, bx, by, 14, i % 3 ? C.blueHi : C.red, 0.9); });
    ctx.restore();
    seats.forEach(([sx, sy, s], i) => {
      const x = cx + sx, y = cy + sy;
      const bob = Math.sin(t * 1.2 + i * 1.7) * 3;
      const gest = Math.max(0, Math.sin(t * 0.9 + i * 2.1)); // someone leans in to talk
      ctx.save(); ctx.translate(x, y + bob); ctx.scale(s, s); ctx.rotate((sx > 0 ? -1 : 1) * gest * 0.05);
      ctx.fillStyle = '#0a0920';
      // shoulders/torso
      ctx.beginPath(); ctx.moveTo(-62, 10); ctx.quadraticCurveTo(-60, -84, 0, -88); ctx.quadraticCurveTo(60, -84, 62, 10); ctx.closePath(); ctx.fill();
      // head
      ctx.beginPath(); ctx.ellipse(0, -126, 30, 36, 0, 0, TAU); ctx.fill();
      // rim light toward the table hologram
      ctx.strokeStyle = rgba(i % 3 === 1 ? '#ff7a7a' : C.blueHi, 0.85); ctx.lineWidth = 3; ctx.shadowColor = C.blueHi; ctx.shadowBlur = 14;
      ctx.beginPath(); ctx.ellipse(0, -126, 30, 36, 0, Math.PI * 0.9, Math.PI * 2.1); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-58, -30); ctx.quadraticCurveTo(-58, -84, 0, -88); ctx.quadraticCurveTo(58, -84, 58, -30); ctx.stroke();
      ctx.restore();
      // a laptop/tablet glow in front of some
      if (i % 2 === 0) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(ctx, x, y + 10, 50 * s, C.blueHi, 0.5); ctx.restore(); }
    });
    ctx.restore();
  }

  function scene4(ctx, t) {
    const endA = fade(t, ev.endcard - 0.2, 0.9);
    // --- mission + teams
    if (endA < 1) {
      ctx.save(); ctx.globalAlpha = 1 - endA;
      backdrop(ctx, t, { glowX: W * 0.68, glowY: H * 0.6, blue: 0.45, red: 0.18 });
      bokeh(ctx, t, 30, 0.45, 4);
      team(ctx, t, 1);
      const lv = ctx.createLinearGradient(0, 0, W * 0.6, 0);
      lv.addColorStop(0, 'rgba(6,5,24,0.85)'); lv.addColorStop(1, 'rgba(6,5,24,0)');
      ctx.fillStyle = lv; ctx.fillRect(0, 0, W * 0.6, H);
      const mA = win(t, ev.finale + 0.2, ev.future + 0.05, 0.5, 0.4);
      if (mA > 0) {
        kicker(ctx, 'OUR MISSION', 140, 360, mA);
        rich(ctx, [{ s: 'Transform ', c: '#fff', t: wordT('l13', 'transform') - 0.1 }, { s: 'everyone', c: '#fff', t: wordT('l13', 'everyone') }], 140, 460, { size: 76, alpha: mA, t });
        rich(ctx, [{ s: 'into ', c: '#fff', weight: 300, t: wordT('l13', 'into') }, { s: 'AI-ready', c: C.blueHi, glow: 18, t: wordT('l13', 'ai-ready') }], 140, 552, { size: 76, alpha: mA, t });
        rich(ctx, [{ s: 'innovators.', c: '#ffffff', pill: C.red, t: wordT('l13', 'innovators') }], 152, 652, { size: 76, alpha: mA, t });
      }
      const fA = win(t, ev.future, ev.endcard + 0.4, 0.5, 0.5);
      if (fA > 0) {
        kicker(ctx, 'THE FUTURE BELONGS TO ORGANIZATIONS THAT', 140, 330, fA);
        const ws = [['Learn', C.blueHi, wordT('l14', 'learn')], ['Adapt', '#ffffff', wordT('l14', 'adapt')], ['Innovate', '#ff5a5a', wordT('l14', 'innovate')]];
        ws.forEach(([w, col, ti], i) => {
          const k = ease.outBack(clamp((t - ti + 0.1) / 0.4), 2);
          text(ctx, w + '.', 140, 450 + i * 100 + (1 - k) * 20, { size: 90, weight: 800, color: col, alpha: fA * clamp((t - ti + 0.1) / 0.25), glow: col === '#ffffff' ? 0 : 20 });
        });
        const fk = clamp((t - wordT('l14', 'faster') + 0.1) / 0.4);
        // speed lines on "faster than ever"
        if (fk > 0) {
          rich(ctx, [{ s: 'faster than ever', c: C.blueHi }], 146, 790, { size: 40, weight: 700, alpha: fA * fk });
          ctx.save(); ctx.globalAlpha = fA * fk * 0.8; ctx.globalCompositeOperation = 'lighter';
          for (let i = 0; i < 5; i++) { const y = 776 - 30 + i * 14, x = 470 + ((t * 900 + i * 170) % 300); const g = ctx.createLinearGradient(x, 0, x + 140, 0); g.addColorStop(0, rgba(C.blue, 0)); g.addColorStop(1, rgba(C.blueHi, 0.8)); ctx.fillStyle = g; ctx.fillRect(x, y, 140, 2.5); }
          ctx.restore();
        }
      }
      flash(ctx, t, S.S.finale[0], { a: 0.1, color: '#cfe8ff' });
      ctx.restore();
    }
    // --- end card
    if (endA > 0) {
      ctx.save(); ctx.globalAlpha = endA;
      backdrop(ctx, t, { glowX: W / 2, glowY: H * 0.42, blue: 0.45, red: 0.18, bottom: '#241b6e' });
      // light rays
      ctx.save(); ctx.translate(W / 2, H * 0.36); ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 14; i++) { ctx.rotate(TAU / 14); const a0 = t * 0.05; ctx.fillStyle = rgba(i % 3 ? C.blue : C.indigo, 0.03); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a0) * 1800, Math.sin(a0) * 1800); ctx.lineTo(Math.cos(a0 + 0.09) * 1800, Math.sin(a0 + 0.09) * 1800); ctx.fill(); }
      ctx.restore();
      bokeh(ctx, t, 34, 0.45, 5);
      ctx.fillStyle = 'rgba(4,3,18,0.25)'; ctx.fillRect(0, 0, W, H);
      ctx.restore();
      const z = 1 + 0.025 * clamp((t - ev.endcard) / 8);
      ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
      acadLogo(ctx, W / 2, H * 0.3, 1240, t, { tIcon: ev.endcard + 0.1, tSolix: ev.endcard + 0.3, tAcad: ev.endcard + 0.75, alpha: endA, tagline: false });
      // Learn. Innovate. Transform.
      const words = [['Learn.', C.blueHi, ev.learn], ['Innovate.', '#ff4a4a', ev.innovate], ['Transform.', '#ffffff', ev.transform]];
      const sz = 92, gap = 46;
      const widths = words.map(([w]) => measure(ctx, w, sz, 800));
      let x = W / 2 - (widths.reduce((a, b) => a + b, 0) + gap * 2) / 2;
      const y = H * 0.62;
      words.forEach(([w, col, ti], i) => {
        const k = clamp((t - ti) / 0.35);
        const s = i === 2 ? 1 + 0.6 * (1 - ease.outCubic(k)) : 1 + 0.25 * (1 - ease.outBack(k, 2));
        if (k > 0) {
          ctx.save(); ctx.translate(x + widths[i] / 2, y - sz * 0.35); ctx.scale(s, s);
          if (i === 2) { rrect(ctx, -widths[i] / 2 - 26, -sz * 0.72, widths[i] + 52, sz * 1.2, 22); const g = ctx.createLinearGradient(-widths[i] / 2, 0, widths[i] / 2, 0); g.addColorStop(0, C.indigo); g.addColorStop(1, '#4a3bb0'); ctx.fillStyle = g; ctx.globalAlpha = k; ctx.fill(); ctx.strokeStyle = rgba(C.blueHi, 0.9); ctx.lineWidth = 2.5; ctx.shadowColor = C.blue; ctx.shadowBlur = 30; ctx.stroke(); ctx.globalAlpha = 1; }
          text(ctx, w, 0, sz * 0.35, { size: sz, weight: 800, color: col, align: 'center', alpha: k, glow: i === 2 ? 30 : 18, glowColor: i === 2 ? C.blueHi : col });
          ctx.restore();
        }
        x += widths[i] + gap;
      });
      ctx.restore();
      shockRing(ctx, W / 2, y - sz * 0.35, t, ev.transform, { color: C.blueHi, r1: 900, d: 0.9, lw: 4 });
      flash(ctx, t, ev.transform, { a: 0.22, d: 0.5 });
      // web address with a glass shimmer
      const uk = ease.outCubic(clamp((t - ev.url) / 0.6));
      if (uk > 0) {
        const uw = 560, uh = 84, ux = W / 2 - uw / 2, uy = H * 0.76;
        ctx.save(); ctx.globalAlpha = uk;
        rrect(ctx, ux, uy + (1 - uk) * 20, uw, uh, 42); ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.55)'; ctx.lineWidth = 2; ctx.stroke();
        ctx.clip();
        const sx = ux - 200 + (uw + 400) * clamp((t - ev.url) / 1.0);
        const sg = ctx.createLinearGradient(sx - 120, 0, sx + 120, 0); sg.addColorStop(0, 'rgba(255,255,255,0)'); sg.addColorStop(0.5, 'rgba(255,255,255,0.25)'); sg.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = sg; ctx.fillRect(sx - 120, uy - 10, 240, uh + 40);
        ctx.restore();
        rich(ctx, [{ s: 'solix', c: '#ffffff' }, { s: 'academy', c: C.blueHi }, { s: '.com', c: '#ffffff' }], W / 2, uy + 56 + (1 - uk) * 20, { size: 46, weight: 800, align: 'center', alpha: uk });
        text(ctx, 'Your AI journey starts today.', W / 2, uy + 150, { size: 32, weight: 400, color: '#dfe6ff', align: 'center', alpha: fade(t, ev.url + 0.35, 0.5), spacing: 1 });
      }
    }
  }

  // ---------------------------------------------------------------- draw
  Studio.film({
    async init() {
      IMG.acadIcon = await Studio.loadImage('assets/acad_icon.png');
      IMG.acadSolix = await Studio.loadImage('assets/acad_solix.png');
      IMG.acadAcademy = await Studio.loadImage('assets/acad_academy.png');
      IMG.acadTag = await Studio.loadImage('assets/acad_tagline.png');
      IMG.solixLogo = await Studio.loadImage('assets/solix_logo_white.png');
      buildCity();
    },
    post: { paper: 0, vignette: 0.35, grain: 0.03 },
    fadeOut: 0.6,
    draw(ctx, t) {
      const a0 = S.S.academy[0], f0 = S.S.finale[0], p0 = S.S.pillars[0];
      const sh = shake(t);
      ctx.save(); ctx.translate(W / 2 + sh.x, H / 2 + sh.y); ctx.rotate(sh.r); ctx.translate(-W / 2, -H / 2);
      // zoom-blur cuts: the outgoing scene pushes past camera and defocuses, the incoming one settles in from a soft focus
      const TR = 0.6;
      const out = (t0) => { const k = ease.inCubic(clamp((t - t0) / TR)); return { alpha: 1, scale: 1 + 0.12 * k, blur: 16 * k }; };
      const inn = (t0) => { const k = ease.outCubic(clamp((t - t0) / TR)); return { alpha: k, scale: 1.08 - 0.08 * k, blur: 14 * (1 - k) }; };
      const scenes = [[scene1, 0, p0], [scene2, p0, a0], [scene3, a0, f0], [scene4, f0, 1e9]];
      for (const [fn, s0, s1] of scenes) {
        if (t < s0 - 0.01 || t >= s1 + TR) continue;
        const o = t >= s1 ? out(s1) : s0 > 0 && t < s0 + TR ? inn(s0) : { alpha: 1, scale: 1, blur: 0 };
        layer(ctx, fn, t, o);
      }
      ctx.restore();
      bloom(ctx, 0.1);
      captions(ctx, t);
      cornerLogo(ctx, t);
    },
  });
})();
