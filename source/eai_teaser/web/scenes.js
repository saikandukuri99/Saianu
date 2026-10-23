// Solix Enterprise AI teaser - Storyline A. All scenes are keyed to the narration timeline.
'use strict';
const TLD = window.TIMELINE, L = TLD.lines.map(l => l.start), LE = TLD.lines.map(l => l.end), TOTAL = TLD.total;
const stage = $('#stage');
const SC = [];
function scene(tin, tout, build) {
  const root = el('<section class="scene"></section>');
  stage.appendChild(root);
  const update = build(root);
  SC.push({ root, tin, tout, update });
}
function svgLayer(root, extra = '') {
  const s = el(`<svg class="a" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">${extra}</svg>`);
  root.appendChild(s); return s;
}
const NS = 'http://www.w3.org/2000/svg';
function path(svg, d, color = 'rgba(51,169,255,.6)', w = 2, dash = false) {
  const p = document.createElementNS(NS, 'path');
  p.setAttribute('d', d); p.setAttribute('fill', 'none'); p.setAttribute('stroke', color); p.setAttribute('stroke-width', w);
  p.setAttribute('stroke-linecap', 'round');
  if (dash) p.setAttribute('stroke-dasharray', '6 8'); else { p.setAttribute('pathLength', '1'); p.style.strokeDasharray = '1'; p.style.strokeDashoffset = '1'; }
  svg.appendChild(p);
  return p;
}
function dot(svg, color = '#9fe8ff', r = 4.5) {
  const c = document.createElementNS(NS, 'circle'); c.setAttribute('r', r); c.setAttribute('fill', color);
  c.style.filter = `drop-shadow(0 0 6px ${color}) drop-shadow(0 0 14px ${color})`; c.style.opacity = 0;
  svg.appendChild(c); return c;
}
function glowAt(e, t, at, rgb = '51,169,255', out) {
  let p = prog(t, at, .5, Ease.out2);
  if (out !== undefined) p *= 1 - prog(t, out, .5);
  e.style.boxShadow = p > 0.001
    ? `0 0 0 1.5px rgba(${rgb},${(.9 * p).toFixed(3)}),0 0 ${Math.round(50 * p)}px rgba(${rgb},${(.5 * p).toFixed(3)}),0 24px 70px rgba(0,0,0,.5)`
    : '';
}
function headline(root, kick, l1, l2, opt = {}) {
  const h = el(`<div class="head"${opt.style ? ` style="${opt.style}"` : ''}><div class="kick">${kick}</div><div class="h1">${l1}</div>${l2 ? `<div class="pill"><div class="bar"></div><div class="tx">${l2}</div></div>` : ''}</div>`);
  root.appendChild(h);
  const k = $('.kick', h), words = splitWords($('.h1', h)), p = $('.pill', h);
  return (t, at, pAt = at + .45) => {
    fx(k, t, { at, dur: .6, from: { o: 0, x: -24 } });
    if (opt.wordAt) words.forEach((w, i) => fx(w, t, { at: opt.wordAt[i] ?? at, dur: .6, ease: Ease.out4, from: { o: 0, y: 30, blur: 10 } }));
    else wordsIn(words, t, at + .15);
    if (p) pillIn(p, t, pAt);
  };
}
function card(root, x, y, w, h, html, cls = '') {
  const c = el(`<div class="card ${cls}" style="left:${x}px;top:${y}px;width:${w}px;${h ? `height:${h}px;` : ''}">${html}</div>`);
  root.appendChild(c); return c;
}
function check(size = 22, color = '#2fd18a') {
  return `<span class="ico ck" style="width:${size}px;height:${size}px;border-radius:50%;background:${color};color:#06120c"><svg viewBox="0 0 24 24" style="stroke-width:3.2">${IC.check}</svg></span>`;
}
function pop(e, t, at, d = .5) { fx(e, t, { at, dur: d, ease: Ease.outBack, from: { o: 0, s: .3 } }); }

// ============================================================ S0 TITLE
scene(0, 5.15, root => {
  const logo = el(`<img class="a" src="assets/logo_white.png" style="left:${960 - 260}px;top:300px;height:118px;transform-origin:56px 50%">`);
  root.appendChild(logo);
  const svg = svgLayer(root);
  const rings = [0, 1, 2].map(i => { const c = document.createElementNS(NS, 'circle'); c.setAttribute('cx', 960); c.setAttribute('cy', 359); c.setAttribute('fill', 'none'); c.setAttribute('stroke', i === 1 ? '#ee2424' : '#33a9ff'); svg.appendChild(c); return c; });
  const kick = el(`<div class="a center mono" style="top:236px;font-size:16px;letter-spacing:.5em;color:#aeb8ee">SOLIX EMPOWER 2026</div>`);
  const title = el(`<div class="a center disp" style="top:462px;font-size:134px;font-weight:800;line-height:1;letter-spacing:-.01em"></div>`);
  const T = 'Enterprise AI';
  title.innerHTML = [...T].map(c => `<span class="w" style="background:linear-gradient(180deg,#ffffff 30%,#9fd8ff);-webkit-background-clip:text;color:transparent">${c === ' ' ? '&nbsp;' : c}</span>`).join('');
  const sweep = el(`<div class="a center disp" style="top:462px;font-size:134px;font-weight:800;line-height:1;letter-spacing:-.01em;background:linear-gradient(100deg,transparent 42%,rgba(255,255,255,.95) 50%,transparent 58%);background-size:300% 100%;-webkit-background-clip:text;color:transparent">${T}</div>`);
  const line = el(`<div class="a" style="left:700px;top:640px;width:520px;height:3px;background:linear-gradient(90deg,transparent,#0088cf 20%,#ee2424 80%,transparent);transform-origin:50% 50%"></div>`);
  const sub = el(`<div class="a center" style="top:674px;font-size:32px;font-weight:500;color:#d3d9ff">Get your data ready for AI. Then put it to work.</div>`);
  [kick, title, sweep, line, sub].forEach(e => root.appendChild(e));
  const letters = $$('.w', title), sw = splitWords(sub);
  return t => {
    BG.state.black = 1 - prog(t, 0, 1.2, Ease.out2);
    // icon pops, then logo slides open to reveal the wordmark
    const slide = prog(t, 1.05, 1.0, Ease.inOut5);
    const iconFrac = 376 / 1797;
    logo.style.clipPath = `inset(0 ${((1 - iconFrac) * (1 - slide) * 100).toFixed(2)}% 0 0)`;
    const sIn = prog(t, .3, .7, Ease.outBack);
    logo.style.opacity = prog(t, .3, .25);
    const dx = (260 - 56) * (1 - slide);
    logo.style.transform = `translateX(${dx}px) scale(${.2 + .8 * sIn})`;
    rings.forEach((c, i) => {
      const p = prog(t, .42 + i * .14, 1.6, Ease.out3);
      c.setAttribute('cx', 960 - 0 * dx); c.setAttribute('r', 50 + p * (380 + i * 90));
      c.setAttribute('stroke-width', 2.5 * (1 - p) + .3); c.style.opacity = (p > 0 ? 1 - p : 0) * .8;
    });
    fx(kick, t, { at: 1.5, dur: .9, from: { o: 0, y: 12, blur: 6 } });
    kick.style.letterSpacing = (0.9 - .4 * prog(t, 1.5, 1.6, Ease.out3)) + 'em';
    letters.forEach((l, i) => fx(l, t, { at: 1.75 + i * .045, dur: .8, ease: Ease.out4, from: { o: 0, y: 60, blur: 16, s: 1.2 } }));
    title.style.letterSpacing = (0.16 - .17 * prog(t, 1.75, 1.6, Ease.out3)) + 'em';
    sweep.style.letterSpacing = title.style.letterSpacing;
    sweep.style.backgroundPosition = `${100 - 100 * prog(t, 3.0, 1.3, Ease.inOut3)}% 0`;
    sweep.style.opacity = t > 3 && t < 4.4 ? 1 : 0;
    fx(line, t, { at: 2.55, dur: .9, ease: Ease.outExpo, from: { o: 0, sx: 0 } });
    wordsIn(sw, t, 2.75, { stagger: .06 });
    BG.state.net = 1.2;
  };
});

// ============================================================ S1 AGENTIC AI / ENTERPRISE DATA
scene(5.55, L[2] - .75, root => {
  const svg = svgLayer(root);
  const hub = el(`<div class="a" style="left:${960 - 140}px;top:${300 - 140}px;width:280px;height:280px"></div>`);
  hub.innerHTML = `<svg width="280" height="280" viewBox="-140 -140 280 280">
    <circle r="88" fill="rgba(20,18,60,.6)" stroke="rgba(51,169,255,.55)" stroke-width="2" pathLength="1" class="ring" style="stroke-dasharray:1;stroke-dashoffset:1"/>
    <g class="orb"><circle r="122" fill="none" stroke="rgba(160,175,255,.28)" stroke-width="1.5" stroke-dasharray="3 9"/></g></svg>`;
  root.appendChild(hub);
  const spk = el(`<div class="a" style="left:${960 - 70}px;top:${300 - 70}px;width:140px;height:140px">${sparkle(140)}</div>`); root.appendChild(spk);
  const orbitIcons = [['db', -90], ['chat', 30], ['bolt', 150]].map(([n, a]) => {
    const r = 88, x = 960 + r * Math.cos(a * Math.PI / 180), y = 300 + r * Math.sin(a * Math.PI / 180);
    const e = el(`<div class="a" style="left:${x - 19}px;top:${y - 19}px">${ico(n, 38, '#9fe8ff', '#16144a', 'border:1.5px solid rgba(51,169,255,.7);border-radius:50%')}</div>`);
    root.appendChild(e); return e;
  });
  const lab = el(`<div class="a center lbl" style="top:448px;letter-spacing:.45em">Enterprise AI</div>`); root.appendChild(lab);
  // workflows
  const LW = [['Purchase order', 'Awaiting approval', 'doc'], ['Customer request', 'New ticket', 'chat'], ['Shipment delay', 'Carrier update', 'truck']];
  const RW = [['Order approved', 'Done by agent', 'check'], ['Reply sent', 'Done by agent', 'send'], ['Supplier notified', 'Done by agent', 'mail']];
  const ys = [180, 270, 360];
  const lc = LW.map(([a, b, i], k) => card(root, 230, ys[k], 330, 70, `<div style="display:flex;align-items:center;gap:14px;padding:13px 16px">${ico(i, 40, '#a9b6ff', 'rgba(125,107,255,.16)')}<div><div style="font-size:18px;font-weight:600">${a}</div><div style="font-size:14px;color:#8f99cc;margin-top:3px">${b}</div></div></div>`));
  const rc = RW.map(([a, b, i], k) => card(root, 1360, ys[k], 330, 70, `<div style="display:flex;align-items:center;gap:14px;padding:13px 16px">${ico(i, 40, '#5fe3a6', 'rgba(47,209,138,.14)')}<div style="flex:1"><div style="font-size:18px;font-weight:600">${a}</div><div style="font-size:14px;color:#8f99cc;margin-top:3px">${b}</div></div><span class="okc">${check(24)}</span></div>`));
  const lp = ys.map(y => path(svg, `M560 ${y + 35} C 700 ${y + 35}, 760 300, 872 300`, 'rgba(125,140,255,.45)', 1.6));
  const rp = ys.map(y => path(svg, `M1048 300 C 1160 300, 1220 ${y + 35}, 1360 ${y + 35}`, 'rgba(47,209,138,.45)', 1.6));
  const ld = lp.map(() => dot(svg, '#b7a9ff', 4)), rd = rp.map(() => dot(svg, '#5fe3a6', 4));
  const outs = ['Faster cycle times', 'Higher productivity', 'Always-on operations', 'Better, faster decisions'];
  const orow = el(`<div class="a center" style="top:478px;display:flex;justify-content:center;gap:14px">${outs.map(o => `<span class="chip" style="font-size:15px;color:#c9d0ff;background:rgba(30,28,80,.6)">${o}</span>`).join('')}</div>`);
  root.appendChild(orow); const ochips = $$('.chip', orow);
  const h1 = el(`<div class="a center disp" style="top:568px;font-size:62px;font-weight:700;line-height:1.14">AI is transforming<br>how enterprises run and grow.</div>`);
  const h2 = el(`<div class="a center disp" style="top:568px;font-size:62px;font-weight:700;line-height:1.14">But your AI is only as ready<br>as <span style="color:#43b4ff">your enterprise data</span> is.</div>`);
  root.appendChild(h1); root.appendChild(h2);
  const w1 = splitWords(h1), w2 = splitWords(h2);
  const dlab = el(`<div class="a center lbl" style="top:800px;letter-spacing:.4em;color:#7f8ac4">Your enterprise data</div>`); root.appendChild(dlab);
  const data = ['GL_JE_LINES', 'MTL_SYS_ITEMS', 'PO_LINES_ALL', 'AP_INV_HDR', 'CUST_ACCT_B', 'Contract_2214.pdf', 'Policy_v7.docx'];
  const drow = el(`<div class="a center" style="top:834px;display:flex;justify-content:center;gap:12px">${data.map(d => `<span class="chip mono" style="font-size:14px;font-weight:500;color:#aab4e8;background:rgba(20,18,60,.7)">${d}</span>`).join('')}</div>`);
  root.appendChild(drow); const dchips = $$('.chip', drow);
  return t => {
    BG.state.net = lerp(1.2, .9, prog(t, 5.5, 2));
    const a0 = 5.75;
    $('.ring', hub).style.strokeDashoffset = 1 - prog(t, a0, 1.1, Ease.inOut3);
    fx(spk, t, { at: a0 + .2, dur: .9, ease: Ease.outBack, from: { o: 0, s: 0, r: -90 } });
    spk.style.transform += ` rotate(${Math.sin(t * .8) * 4}deg) scale(${1 + Math.sin(t * 2.1) * .03})`;
    $('.orb', hub).setAttribute('transform', `rotate(${t * 12})`);
    fx($('.orb', hub), t, { at: a0 + .4, dur: 1 });
    orbitIcons.forEach((e, i) => pop(e, t, a0 + .6 + i * .12));
    fx(lab, t, { at: a0 + .8, dur: .7, from: { o: 0, y: 10 } });
    wordsIn(w1, t, L[0] - .05, { out: L[1] - .55, stagger: .06 });
    const dim = 1 - .62 * prog(t, L[1] - .2, .8);
    lc.forEach((c, i) => fx(c, t, { at: L[0] + .9 + i * .15, dur: .8, from: { o: 0, x: -40, blur: 8 }, max: dim }));
    rc.forEach((c, i) => {
      fx(c, t, { at: L[0] + 1.5 + i * .15, dur: .8, from: { o: 0, x: 40, blur: 8 }, max: dim });
      pop($('.okc', c), t, L[0] + 2.2 + i * .25, .45);
    });
    lp.forEach((p, i) => { draw(p, t, L[0] + 1.1 + i * .15, .8); p.style.opacity *= dim; pulse(ld[i], p, t, L[0] + 1.7, 1.6, i * .3, dim); });
    rp.forEach((p, i) => { draw(p, t, L[0] + 1.6 + i * .15, .8); p.style.opacity *= dim; pulse(rd[i], p, t, L[0] + 2.1, 1.6, i * .3 + .5, dim); });
    ochips.forEach((c, i) => fx(c, t, { at: L[0] + 2.6 + i * .12, dur: .6, from: { o: 0, y: 14, blur: 6 }, max: dim }));
    wordsIn(w2, t, L[1] - .1, { stagger: .055 });
    fx(dlab, t, { at: L[1] + .8, dur: .6, from: { o: 0, y: 10 } });
    dchips.forEach((c, i) => fx(c, t, { at: L[1] + 1.0 + i * .08, dur: .7, ease: Ease.out4, from: { o: 0, y: 26, blur: 8 } }));
  };
});

// ============================================================ S2 THE PROBLEM
scene(L[2] - .6, L[6] - .8, root => {
  const svg = svgLayer(root);
  const ai = el(`<div class="a" style="left:${960 - 46}px;top:104px;width:92px;height:92px">${sparkle(92)}</div>`); root.appendChild(ai);
  const ail = el(`<div class="a center lbl" style="top:206px">AI</div>`); root.appendChild(ail);
  const colX = [150, 720, 1290], heads = ['Cryptic tables', 'Disconnected systems', 'Unindexed documents'];
  const hd = heads.map((h, i) => { const e = el(`<div class="a" style="left:${colX[i]}px;top:292px;font-size:21px;font-weight:700;display:flex;align-items:center;gap:12px"><span style="width:22px;height:2px;background:#ee2424"></span>${h}</div>`); root.appendChild(e); return e; });
  const tables = [['GL_JE_LINES', ['SEG2_ATTR14', 'CCID_X07', 'PRD_FLG', 'AMT_ENT_DR']], ['MTL_ENTITIES', ['ORG_CLS_CD', 'UOM_X', 'ATTR_9', 'REV_FL']], ['PO_LINES_ALL', ['VNDR_SITE_ID', 'LN_TP_C', 'BLK_FLG_3', 'ITM_REV']]];
  const tc = tables.map(([n, f], i) => {
    const c = card(root, 150, 340 + i * 128, 480, 112, `<div style="padding:14px 20px"><div class="mono tn" style="font-size:16px;font-weight:600;color:#43b4ff;margin-bottom:12px"></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:9px 20px">${f.map(x => `<div class="mono" style="font-size:14.5px;color:#b9c0ea;display:flex;align-items:center;gap:8px"><span class="fn"></span><span class="q" style="color:#ee2424;font-weight:700">?</span></div>`).join('')}</div></div>`);
    c._n = n; c._f = f; return c;
  });
  const sys = [['Finance application', 'coin', 720, 345], ['Manufacturing application', 'factory', 1010, 345], ['Supply chain app', 'truck', 865, 560]];
  const sc = sys.map(([n, i, x, y]) => card(root, x, y, 240, 104, `<div style="padding:16px;display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center">${ico(i, 40, '#43b4ff')}<div style="font-size:16px;font-weight:600">${n}</div></div>`));
  const broken = [[960, 397, 1010, 397], [840, 449, 940, 560], [1130, 449, 1050, 560]].map(([x1, y1, x2, y2]) => {
    const p = path(svg, `M${x1} ${y1} L${x2} ${y2}`, 'rgba(238,36,36,.75)', 2, true);
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const xm = el(`<div class="a" style="left:${mx - 13}px;top:${my - 13}px">${ico('x', 26, '#fff', '#ee2424', 'border-radius:50%')}</div>`); root.appendChild(xm);
    return { p, xm };
  });
  const docs = ['Contract_2214.pdf', 'Policy_v7.docx', 'Manual_rev3.pdf'];
  const dc = docs.map((d, i) => card(root, 1290, 345 + i * 120, 480, 100, `<div style="padding:16px 18px;display:flex;gap:16px;align-items:center">${ico('doc', 46, '#a9b6ff', 'rgba(125,107,255,.16)')}<div style="flex:1"><div class="mono" style="font-size:16px;font-weight:600;margin-bottom:10px">${d}</div><div style="height:6px;border-radius:3px;background:rgba(150,160,220,.18);width:88%;margin-bottom:6px"></div><div style="height:6px;border-radius:3px;background:rgba(150,160,220,.12);width:62%"></div></div><span class="tag un" style="background:rgba(238,36,36,.16);color:#ff6b6b;border:1px solid rgba(238,36,36,.5)">Unindexed</span></div>`));
  const beam = el(`<div class="a" style="left:1290px;top:330px;width:6px;height:390px;background:linear-gradient(180deg,transparent,#43b4ff,transparent);box-shadow:0 0 30px #43b4ff"></div>`); root.appendChild(beam);
  const barrier = path(svg, 'M960 252 L150 252 M960 252 L1770 252', 'rgba(238,36,36,.8)', 2, true);
  const lock = el(`<div class="a" style="left:${960 - 24}px;top:${252 - 24}px">${ico('lock', 48, '#fff', '#ee2424', 'border-radius:50%;box-shadow:0 0 40px rgba(238,36,36,.8)')}</div>`); root.appendChild(lock);
  const big = el(`<div class="a center disp" style="top:806px;font-size:66px;font-weight:800">Your data <span style="color:#ff3b3b">isn't usable by AI.</span></div>`); root.appendChild(big);
  const bw = splitWords(big);
  return t => {
    BG.state.net = .85;
    const a0 = L[2] - .45;
    fx(ai, t, { at: a0, dur: .8, ease: Ease.outBack, from: { o: 0, s: .4 } });
    ai.style.filter = `grayscale(${prog(t, L[5], .6)}) brightness(${1 - .4 * prog(t, L[5], .6)})`;
    fx(ail, t, { at: a0 + .2, dur: .6 });
    const dim = 1 - .45 * prog(t, L[5] + .2, .7);
    // tables
    fx(hd[0], t, { at: L[2] - .2, dur: .6, from: { o: 0, x: -20 }, max: dim });
    tc.forEach((c, i) => {
      const at = L[2] + i * .32;
      fx(c, t, { at, dur: .7, ease: Ease.out4, from: { o: 0, y: 30, blur: 8 }, max: dim });
      scramble($('.tn', c), t, at + .1, .7, c._n);
      $$('.fn', c).forEach((f, j) => scramble(f, t, at + .25 + j * .06, .8, c._f[j]));
      $$('.q', c).forEach((q, j) => pop(q, t, at + .9 + j * .08, .4));
    });
    // systems
    fx(hd[1], t, { at: L[3] - .2, dur: .6, from: { o: 0, x: -20 }, max: dim });
    sc.forEach((c, i) => fx(c, t, { at: L[3] + i * .2, dur: .7, ease: Ease.out4, from: { o: 0, s: .85, blur: 8 }, max: dim }));
    broken.forEach(({ p, xm }, i) => {
      const o = prog(t, L[3] + .7 + i * .15, .4) * (0.65 + .35 * Math.abs(Math.sin(t * 9 + i)));
      p.style.opacity = o * dim; pop(xm, t, L[3] + .9 + i * .15, .45); xm.style.opacity *= dim;
    });
    // documents
    fx(hd[2], t, { at: L[4] - .2, dur: .6, from: { o: 0, x: -20 }, max: dim });
    dc.forEach((c, i) => { fx(c, t, { at: L[4] + i * .2, dur: .7, ease: Ease.out4, from: { o: 0, y: 30, blur: 8 }, max: dim }); pop($('.un', c), t, L[4] + 1.15 + i * .12, .45); });
    const bp = prog(t, L[4] + .6, .9, Ease.inOut3);
    beam.style.opacity = bp > 0 && bp < 1 ? .9 : 0; beam.style.transform = `translateX(${bp * 474}px)`;
    // AI blocked
    barrier.style.opacity = prog(t, L[5] - .1, .5);
    const shake = t > L[5] + .25 && t < L[5] + .55 ? Math.sin(t * 90) * 4 * (1 - (t - L[5] - .25) / .3) : 0;
    fx(lock, t, { at: L[5] + .05, dur: .55, ease: Ease.outBack, from: { o: 0, s: 2.2, blur: 6 } });
    lock.style.transform += ` translateX(${shake}px)`;
    wordsIn(bw, t, L[5] + .15, { stagger: .07, y: 40 });
  };
});

// ============================================================ S3 FRAMEWORK
scene(L[6] - .65, L[9] - .8, root => {
  const svg = svgLayer(root);
  const t1 = el(`<div class="a center disp" style="top:92px;font-size:46px;font-weight:800;letter-spacing:.06em">AI-ACTIVATED DATA</div>`); root.appendChild(t1);
  const pw = el(`<div class="a center" style="top:152px"><div class="pill"><div class="bar"></div><div class="tx">UNLOCKS ENTERPRISE AI</div></div></div>`); root.appendChild(pw);
  const raw = ['TBL_0437', 'COL_3922', 'ATTR_14'].map((r, i) => { const e = el(`<div class="a chip mono" style="left:${700 + i * 190}px;top:330px;font-size:16px;color:#aab4e8">${r}</div>`); root.appendChild(e); return e; });
  const scan = el(`<div class="a" style="left:640px;top:300px;width:4px;height:110px;background:linear-gradient(180deg,transparent,#5fe3d0,transparent);box-shadow:0 0 26px #26c6b0"></div>`); root.appendChild(scan);
  const tagRow = (n, k, c) => `<div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;font-size:15px;color:#cfd5ff">${n}<span class="tag" style="width:122px;text-align:center;background:${c}22;color:${c};border:1px solid ${c}66">${k}</span></div>`;
  const ds = card(root, 500, 276, 920, 150, `<div style="display:flex;align-items:center;height:100%;padding:0 30px;gap:22px">${ico('sense', 70, '#5fe3d0', 'rgba(38,198,176,.15)', 'border-radius:16px')}<div style="flex:1"><div class="mono" style="font-size:13px;letter-spacing:.2em;color:#5fe3d0">01 · UNDERSTAND</div><div style="display:flex;align-items:center;gap:12px;margin:6px 0"><span class="disp" style="font-size:34px;font-weight:800">Data Sense</span><span class="ck1">${check(26, '#26c6b0')}</span></div><div style="font-size:17px;color:#9aa3cf">Makes enterprise data AI-activated.</div></div><div style="display:flex;flex-direction:column;gap:9px">${tagRow('Application Knowledge Graph', 'Structured', '#43b4ff')}${tagRow('Content Intelligence', 'Unstructured', '#a99bff')}${tagRow('Intelligent Classification', 'Unstructured', '#a99bff')}</div></div>`);
  const cx = [560, 960, 1360];
  const P = [path(svg, 'M960 426 V476 H560 V522', 'rgba(51,169,255,.6)', 2), path(svg, 'M960 426 V522', 'rgba(245,165,36,.6)', 2), path(svg, 'M960 426 V476 H1360 V522', 'rgba(169,155,255,.65)', 2)];
  const D = [dot(svg, '#43b4ff'), dot(svg, '#f5a524'), dot(svg, '#a99bff')];
  const defs = [['chat', '02 · ANSWER', 'Data Ask', 'Plain-language answers across your data.', 'Grounded in the Application Knowledge Graph. Cited.', '#43b4ff', '51,169,255'],
    ['layers', '03 · BUILD', 'AI Warehouse', 'Domain experts build AI applications on governed data.', 'No data engineering project needed.', '#f5a524', '245,165,36'],
    ['bolt', '04 · ACTIVATE', 'Agentic', 'Describe it. Build it. Run it.', 'Agentic AI builds, tests and runs.', '#a99bff', '169,155,255']];
  const cards = defs.map(([i, k, n, d, s, c], j) => card(root, cx[j] - 185, 522, 370, 252, `<div style="padding:24px 24px"><div style="display:flex;justify-content:space-between;align-items:flex-start">${ico(i, 50, c, c + '22', 'border-radius:12px')}<span class="ck">${check(26, c)}</span></div><div class="mono" style="font-size:12.5px;letter-spacing:.2em;color:${c};margin:16px 0 6px">${k}</div><div class="disp" style="font-size:28px;font-weight:800;margin-bottom:8px">${n}</div><div style="font-size:16.5px;color:#cfd5ff;line-height:1.35;margin-bottom:8px">${d}</div><div style="font-size:13.5px;color:#8f99cc;line-height:1.35">${s}</div></div>`));
  return t => {
    BG.state.net = .8;
    const a0 = L[6] - .5;
    fx(t1, t, { at: a0 + .1, dur: .8, from: { o: 0, y: 20, blur: 10 } });
    t1.style.letterSpacing = (.25 - .19 * prog(t, a0 + .1, 1.4, Ease.out3)) + 'em';
    pillIn($('.pill', pw), t, L[6] + .5);
    raw.forEach((r, i) => {
      fx(r, t, { at: a0 + .25 + i * .1, dur: .6, from: { o: 0, y: 16 }, out: L[6] + 1.1, outDur: .45, to: { o: 0, s: .6, blur: 10, y: -10 } });
      r.style.color = t > L[6] + .55 + i * .12 ? '#5fe3d0' : '#aab4e8';
    });
    const sp = prog(t, L[6] + .45, .7, Ease.inOut3); scan.style.opacity = sp > 0 && sp < 1 ? 1 : 0; scan.style.transform = `translateX(${sp * 640}px)`;
    fx(ds, t, { at: L[6] + 1.25, dur: .9, ease: Ease.out4, from: { o: 0, s: .86, blur: 14 } });
    P.forEach((p, i) => { draw(p, t, L[6] + 1.9 + i * .1, .8); pulse(D[i], p, t, L[6] + 2.5, 1.5, i * .33); });
    cards.forEach((c, i) => fx(c, t, { at: L[6] + 2.25 + i * .15, dur: .8, ease: Ease.out4, from: { o: 0, y: 40, blur: 10 } }));
    // highlights follow the narration: understand / ask / build / put to work
    glowAt(ds, t, L[7], '38,198,176'); pop($('.ck1', ds), t, L[7] + .1);
    const hl = [L[7] + 1.05, L[8], L[8] + .95];
    cards.forEach((c, i) => { glowAt(c, t, hl[i], defs[i][6]); pop($('.ck', c), t, hl[i] + .1); fx(c, t, { at: L[6] + 2.25 + i * .15, dur: .8, ease: Ease.out4, from: { o: 0, y: 40, blur: 10 } }); c.style.transform += ` translateY(${-8 * prog(t, hl[i], .5, Ease.outBack)}px)`; });
  };
});

// ============================================================ S4 DATA SENSE
scene(L[9] - .65, L[14] - .75, root => {
  const head = headline(root, 'Data Sense', 'Understand your data.', 'Structured and unstructured.');
  // (a) flow
  const fa = el('<div class="a" style="inset:0"></div>'); root.appendChild(fa);
  const svg = svgLayer(fa);
  const hub = card(fa, 830, 520, 260, 160, `<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:10px">${ico('sense', 58, '#5fe3d0', 'rgba(38,198,176,.16)', 'border-radius:14px')}<div class="disp" style="font-size:25px;font-weight:800">Data Sense</div><div style="font-size:14px;color:#8f99cc;margin-top:-6px">Understands both</div></div>`);
  const ll = el(`<div class="a lbl" style="left:230px;top:398px;color:#43b4ff">Structured</div>`), rl = el(`<div class="a lbl" style="left:1360px;top:398px;color:#a99bff">Unstructured</div>`);
  fa.appendChild(ll); fa.appendChild(rl);
  const Ls = [['Finance application', 'coin'], ['Manufacturing application', 'factory'], ['Cloud data platform', 'cloud']];
  const Rs = [['Contracts', 'doc'], ['Policies', 'shield'], ['Emails', 'mail']];
  const sy = [430, 530, 630];
  const lcs = Ls.map(([n, i], k) => card(fa, 230, sy[k], 330, 70, `<div style="display:flex;align-items:center;gap:14px;padding:13px 16px">${ico(i, 42, '#43b4ff')}<span style="font-size:18px;font-weight:600">${n}</span></div>`));
  const rcs = Rs.map(([n, i], k) => card(fa, 1360, sy[k], 330, 70, `<div style="display:flex;align-items:center;gap:14px;padding:13px 16px">${ico(i, 42, '#a99bff', 'rgba(125,107,255,.16)')}<span style="font-size:18px;font-weight:600">${n}</span></div>`));
  const lps = sy.map(y => path(svg, `M560 ${y + 35} C 700 ${y + 35}, 700 600, 830 600`, 'rgba(51,169,255,.55)', 2));
  const rps = sy.map(y => path(svg, `M1360 ${y + 35} C 1220 ${y + 35}, 1220 600, 1090 600`, 'rgba(169,155,255,.55)', 2));
  const lds = lps.map(() => dot(svg, '#43b4ff')), rds = rps.map(() => dot(svg, '#a99bff'));
  const outs = el(`<div class="a center" style="top:742px;display:flex;justify-content:center;gap:14px">${['Business meaning', 'Relationships', 'Classifications'].map(o => `<span class="chip" style="color:#5fe3d0;border-color:rgba(38,198,176,.45);background:rgba(38,198,176,.10)">${o}</span>`).join('')}</div>`);
  fa.appendChild(outs); const oc = $$('.chip', outs);
  // (b..d) app window
  const win = el(`<div class="win"><div class="tb"><span class="dots"><i></i><i></i><i></i></span>${ico('sense', 22, '#5fe3d0', 'transparent')}Solix Data Sense<span style="margin-left:auto;font-size:13px;color:#8f99cc;font-weight:500">Finance · Manufacturing · Supply chain</span></div>
    <div class="side"><div class="hl" style="position:absolute;left:12px;width:208px;height:36px;border-radius:8px;background:rgba(51,169,255,.16);border:1px solid rgba(51,169,255,.35)"></div>${['Dashboard', 'Workflow', 'Graph Builder', 'Applications', 'Knowledge Graph', 'Curation', 'Synonyms', 'Certified Measures', 'Semantic Packs', 'Quality', 'Usage Console'].map(s => `<div class="it" style="position:relative"><b></b>${s}</div>`).join('')}</div><div class="main"></div></div>`);
  root.appendChild(win);
  const main = $('.main', win), hl = $('.hl', win), items = $$('.it', win);
  // view b: Knowledge Graph Builder
  const rows = [['SEG2_ATTR14', 'Cost center', '96%'], ['CCID_X07', 'GL account combination', '93%'], ['AMT_ENT_DR', 'Debit amount, entered currency', '98%'], ['PRD_FLG', 'Period-close flag', '88%'], ['VNDR_SITE_ID', 'Supplier site', '95%']];
  const steps = ['Connect', 'Profile', 'Discover', 'Draft meaning', 'Expert review', 'Publish'];
  const vb = el(`<div class="view"><div class="vt">Knowledge Graph Builder</div><div class="vs">Finance application · GL_JE_LINES · 214 columns</div>
    <div style="display:flex;gap:10px;margin-bottom:22px">${steps.map((s, i) => `<span class="chip stp" style="font-size:14px;padding:7px 12px"><span class="sd" style="width:9px;height:9px;border-radius:50%;background:#5c6399"></span>${s}</span>`).join('')}</div>
    <table class="t"><tr><th>Technical name</th><th>Business meaning</th><th>Confidence</th><th>Status</th></tr>${rows.map(r => `<tr><td class="mono" style="color:#43b4ff">${r[0]}</td><td class="bm" style="width:380px"></td><td class="cf mono" style="color:#cfd5ff">${r[2]}</td><td class="sts" style="width:230px"><span class="st draft">AI draft</span><span class="st ok" style="display:none">${check(16)} Reviewed</span></td></tr>`).join('')}</table>
    <div class="rev card" style="left:auto;right:32px;bottom:26px;width:330px;padding:14px 16px;display:flex;align-items:center;gap:12px"><span class="av" style="width:38px;height:38px">FE</span><div><div style="font-weight:700;font-size:16px">Finance data expert</div><div style="font-size:13.5px;color:#8f99cc">Reviewing AI-drafted meanings</div></div></div></div>`);
  main.appendChild(vb);
  // view c1: applications
  const apps = [['Finance application', 'coin', '1,284 tables'], ['Manufacturing application', 'factory', '2,113 tables'], ['Supply chain application', 'truck', '1,760 tables'], ['CRM', 'users', '942 tables'], ['Cloud data platform', 'cloud', '2,402 tables'], ['HR application', 'user', '611 tables']];
  const vc = el(`<div class="view"><div class="vt">Applications</div><div class="vs">Knowledge graphs for your applications and cloud platforms</div>
    <div style="display:flex;gap:14px;margin-bottom:20px">${[['Applications', 6], ['Tables', 9112], ['Relationships', 18420], ['Business terms', 14010]].map(([k, v]) => `<div class="card" style="position:relative;flex:1;padding:14px 18px"><div style="font-size:13px;color:#8f99cc">${k}</div><div class="disp cnt" data-v="${v}" style="font-size:28px;font-weight:800;margin-top:4px">0</div></div>`).join('')}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px">${apps.map(([n, i, s]) => `<div class="card apc" style="position:relative;padding:16px 18px"><div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">${ico(i, 38)}<div><div style="font-weight:700;font-size:16.5px">${n}</div><div style="font-size:13px;color:#8f99cc">${s}</div></div></div><div style="display:flex;align-items:center;justify-content:space-between"><span class="tag" style="background:rgba(38,198,176,.12);color:#5fe3d0;border:1px solid rgba(38,198,176,.4)">Application Knowledge Graph</span><span class="rdy st ok">${check(14)} Ready</span></div><div style="height:4px;border-radius:2px;background:rgba(255,255,255,.08);margin-top:12px"><div class="pb" style="height:100%;border-radius:2px;background:linear-gradient(90deg,#0088cf,#26c6b0);width:0"></div></div></div>`).join('')}</div></div>`);
  main.appendChild(vc);
  // view c2: knowledge graph
  const vg = el(`<div class="view"><div class="vt">Knowledge Graph</div><div class="vs">Finance · Manufacturing · Supply chain — entities and relationships</div><svg class="kg" width="1124" height="560" viewBox="0 0 1124 560" style="position:absolute;left:32px;top:96px"></svg>
    <div class="card tim" style="left:auto;right:32px;top:26px;padding:10px 16px;display:flex;align-items:center;gap:10px;font-weight:700;font-size:16px"><span style="width:10px;height:10px;border-radius:50%;background:#2fd18a;box-shadow:0 0 12px #2fd18a"></span>Ready in minutes</div></div>`);
  main.appendChild(vg);
  const kg = $('.kg', vg), r = rng(42);
  const clusters = [[230, 200, '#43b4ff', 'Supplier'], [560, 140, '#a99bff', 'Purchase order'], [880, 230, '#5fe3d0', 'Invoice'], [380, 420, '#f5a524', 'Item'], [760, 430, '#ff6b8a', 'GL account']];
  const nodes = [], edges = [];
  clusters.forEach(([cx0, cy0, c, name], ci) => {
    const hubI = nodes.length; nodes.push({ x: cx0, y: cy0, c, r: 15, name, ci, ord: ci * .06 });
    for (let k = 0; k < 13; k++) {
      const a = r() * 6.283, d = 55 + r() * 95;
      nodes.push({ x: cx0 + Math.cos(a) * d, y: cy0 + Math.sin(a) * d * .8, c, r: 4 + r() * 4, ci, ord: .3 + r() * .9 });
      edges.push([hubI, nodes.length - 1]);
    }
  });
  [[0, 14], [14, 28], [28, 56], [0, 42], [42, 56], [14, 42], [0, 28]].forEach(e => edges.push(e));
  for (let k = 0; k < 16; k++) { const a = Math.floor(r() * nodes.length), b = Math.floor(r() * nodes.length); if (nodes[a].ci !== nodes[b].ci) edges.push([a, b]); }
  const eEls = edges.map(([a, b]) => { const p = document.createElementNS(NS, 'line'); p.setAttribute('x1', nodes[a].x); p.setAttribute('y1', nodes[a].y); p.setAttribute('x2', nodes[b].x); p.setAttribute('y2', nodes[b].y); p.setAttribute('stroke', 'rgba(170,180,255,.28)'); p.setAttribute('stroke-width', nodes[a].r > 10 && nodes[b].r > 10 ? 2 : 1); kg.appendChild(p); return p; });
  const nEls = nodes.map(n => { const g = document.createElementNS(NS, 'g'); g.innerHTML = `<circle r="${n.r * 2.2}" fill="${n.c}" opacity=".18"/><circle r="${n.r}" fill="${n.c}"/>${n.name ? `<text y="${n.r + 22}" text-anchor="middle" fill="#e6e9ff" font-size="15" font-weight="700" font-family="Inter">${n.name}</text>` : ''}`; kg.appendChild(g); return g; });
  // view d: curation workspace
  const wl = [['Supplier', 'Finance application', .96, 'High'], ['Net revenue', 'Finance application', .91, 'High'], ['Item cost', 'Manufacturing application', .74, 'Medium'], ['Ship-to site', 'Supply chain application', .58, 'Medium'], ['Contract renewal date', 'Contracts', .41, 'Low']];
  const pc = { High: ['#ff6b6b', '238,36,36'], Medium: ['#ffc35c', '245,165,36'], Low: ['#43b4ff', '51,169,255'] };
  const vd = el(`<div class="view"><div class="vt">Curation Workspace</div><div class="vs">Steward's worklist · ranked by business impact</div>
    <div style="display:flex;gap:14px;margin-bottom:22px">${[['Total terms', 14010, '#fff'], ['Auto-approved', 8992, '#5fe3a6'], ['Needs review', 4713, '#ffc35c'], ['Approved today', 305, '#43b4ff']].map(([k, v, c]) => `<div class="card" style="position:relative;flex:1;padding:14px 18px"><div style="font-size:13px;color:#8f99cc">${k}</div><div class="disp cnt" data-v="${v}" style="font-size:28px;font-weight:800;margin-top:4px;color:${c}">0</div></div>`).join('')}</div>
    <div style="display:grid;grid-template-columns:60px 1.3fr 1.5fr 1.4fr 120px;padding:0 16px 10px" class="mono"><span style="font-size:12px;color:#7f89bb;letter-spacing:.14em">RANK</span><span style="font-size:12px;color:#7f89bb;letter-spacing:.14em">TERM</span><span style="font-size:12px;color:#7f89bb;letter-spacing:.14em">APPLICATION</span><span style="font-size:12px;color:#7f89bb;letter-spacing:.14em">BUSINESS IMPACT</span><span style="font-size:12px;color:#7f89bb;letter-spacing:.14em">PRIORITY</span></div>
    <div class="wl" style="position:relative;height:330px">${wl.map(([n, a, v, p], i) => `<div class="card wr" style="left:0;right:0;height:56px;display:grid;grid-template-columns:60px 1.3fr 1.5fr 1.4fr 120px;align-items:center;padding:0 16px"><span class="mono rk" style="color:#8f99cc;font-size:15px"></span><span style="font-weight:700;font-size:17px">${n}</span><span style="color:#b9c0ea;font-size:15px">${a}</span><span style="display:flex;align-items:center;gap:10px"><span style="flex:1;max-width:210px;height:8px;border-radius:4px;background:rgba(255,255,255,.08)"><span style="display:block;height:100%;width:${v * 100}%;border-radius:4px;background:${pc[p][0]}"></span></span><span class="mono" style="font-size:13px;color:#cfd5ff">${Math.round(v * 100)}</span></span><span class="tag" style="justify-self:start;background:rgba(${pc[p][1]},.16);color:${pc[p][0]};border:1px solid rgba(${pc[p][1]},.5)">${p}</span></div>`).join('')}</div>
    <div class="card" style="left:auto;right:32px;top:24px;padding:10px 16px;display:flex;align-items:center;gap:10px;font-size:15px;font-weight:600"><span class="av">DS</span>Data steward · in the loop</div></div>`);
  main.appendChild(vd);
  const wr = $$('.wr', vd), start = [2, 4, 0, 3, 1]; // initial slot of each row; ranked => slot i
  const views = [vb, vc, vg, vd];
  return t => {
    BG.state.net = .7;
    const a0 = L[9] - .5;
    head(t, a0 + .1);
    // (a) flow, before the window
    const outA = L[10] - .45;
    fx(hub, t, { at: a0 + .4, dur: .8, ease: Ease.outBack, from: { o: 0, s: .6 } }); glowAt(hub, t, L[9] + .8, '38,198,176');
    fx(ll, t, { at: L[9] + .1, dur: .6 }); fx(rl, t, { at: L[9] + 1.2, dur: .6 });
    lcs.forEach((c, i) => fx(c, t, { at: L[9] + .2 + i * .14, dur: .7, from: { o: 0, x: -40, blur: 8 } }));
    rcs.forEach((c, i) => fx(c, t, { at: L[9] + 1.3 + i * .14, dur: .7, from: { o: 0, x: 40, blur: 8 } }));
    lps.forEach((p, i) => { draw(p, t, L[9] + .5 + i * .12, .8); pulse(lds[i], p, t, L[9] + 1, 1.3, i * .3); });
    rps.forEach((p, i) => { draw(p, t, L[9] + 1.6 + i * .12, .8); pulse(rds[i], p, t, L[9] + 2.1, 1.3, i * .3); });
    oc.forEach((c, i) => fx(c, t, { at: L[9] + 2.5 + i * .12, dur: .6, from: { o: 0, y: 14 } }));
    fx(fa, t, { out: outA, outDur: .5, to: { o: 0, s: .94, blur: 10 } });
    fa.style.display = t > outA + .5 ? 'none' : 'block';
    // window
    fx(win, t, { at: L[10] - .3, dur: .9, ease: Ease.out4, from: { o: 0, y: 60, s: .96, blur: 12 } });
    const vt = [L[10] - .3, L[11] - .15, L[12] - .1, L[13] - .15, 999];
    views.forEach((v, i) => fx(v, t, { at: vt[i], dur: .55, from: { o: 0, x: 40, blur: 6 }, out: vt[i + 1] - .05, outDur: .3, to: { o: 0, x: -30, blur: 6 } }));
    const act = [2, 3, 4, 5], idx = t < vt[1] ? 0 : t < vt[2] ? 1 : t < vt[3] ? 2 : 3;
    const prevIdx = Math.max(0, idx - 1), mp = prog(t, vt[idx], .45, Ease.inOut3);
    const ip = items[act[idx]], pp = items[act[prevIdx]];
    hl.style.top = lerp(pp.offsetTop, ip.offsetTop, idx === 0 ? 1 : mp) + 'px';
    items.forEach((it, i) => it.style.color = i === act[idx] ? '#fff' : '');
    // b: AI drafts meaning, experts review
    $$('.stp', vb).forEach((s, i) => {
      const on = [L[10] - .2, L[10] - .05, L[10] + .1, L[10] + .3, L[10] + 1.7, L[10] + 2.6][i];
      $('.sd', s).style.background = t > on ? (i === 3 ? '#a99bff' : i >= 4 ? '#2fd18a' : '#43b4ff') : '#5c6399';
      s.style.borderColor = t > on && i < 6 ? 'rgba(130,150,255,.5)' : '';
    });
    $$('tr', vb).slice(1).forEach((tr, i) => {
      const at = L[10] + .3 + i * .22;
      type($('.bm', tr), t, at, 55, rows[i][1], false);
      fx($('.cf', tr), t, { at: at + .3, dur: .4 });
      fx($('.st.draft', tr), t, { at: at + .2, dur: .4, from: { o: 0, x: -10 } });
      const rv = L[10] + 1.75 + i * .2;
      $('.st.draft', tr).style.display = t < rv ? '' : 'none';
      const ok = $('.st.ok', tr); ok.style.display = t < rv ? 'none' : 'inline-flex'; pop(ok, t, rv, .4);
    });
    fx($('.rev', vb), t, { at: L[10] + 1.5, dur: .6, from: { o: 0, y: 20 } });
    // c1: applications
    $$('.cnt', vc).forEach((c, i) => count(c, t, L[11] + .1, 1.4, +c.dataset.v));
    $$('.apc', vc).forEach((c, i) => {
      fx(c, t, { at: L[11] + .15 + i * .12, dur: .6, ease: Ease.out4, from: { o: 0, y: 24, blur: 6 } });
      const pb = prog(t, L[11] + .4 + i * .15, 1.0, Ease.inOut3);
      $('.pb', c).style.width = pb * 100 + '%'; pop($('.rdy', c), t, L[11] + 1.4 + i * .15, .4);
    });
    // c2: graph built in minutes
    nEls.forEach((g, i) => {
      const n = nodes[i], p = prog(t, L[12] - .1 + n.ord * 1.1, .5, Ease.outBack);
      const dx = Math.sin(t * .6 + i) * 3, dy = Math.cos(t * .5 + i * 1.3) * 3;
      g.setAttribute('transform', `translate(${n.x + dx},${n.y + dy}) scale(${p})`); g.style.opacity = clamp(p);
    });
    eEls.forEach((e, i) => { const [a, b] = edges[i]; e.style.opacity = prog(t, L[12] + .2 + Math.max(nodes[a].ord, nodes[b].ord) * 1.1, .6); });
    // d: ranked worklist
    $$('.cnt', vd).forEach(c => count(c, t, L[13] + .05, 1.5, +c.dataset.v));
    const rp = prog(t, L[13] + 2.3, .9, Ease.inOut3);
    wr.forEach((w, i) => {
      const y = lerp(start[i], i, rp) * 66;
      fx(w, t, { at: L[13] + .2 + start[i] * .1, dur: .5, from: { o: 0, x: 30 } });
      w.style.top = y + 'px';
      $('.rk', w).textContent = rp > .5 ? '#' + (i + 1) : '—';
      if (i < 2) glowAt(w, t, L[13] + 3.0, '238,36,36');
    });
  };
});

// ============================================================ S5 CROSS-APPLICATION KNOWLEDGE GRAPH
scene(L[14] - .6, L[19] - .8, root => {
  const intro = el(`<div class="a center disp" style="top:440px;font-size:84px;font-weight:800">What sets <span style="color:#ff3b3b">Solix</span> apart</div>`); root.appendChild(intro);
  const iu = el(`<div class="a" style="left:760px;top:560px;width:400px;height:4px;background:linear-gradient(90deg,#0088cf,#ee2424);transform-origin:0 50%"></div>`); root.appendChild(iu);
  const iw = splitWords(intro);
  const head = headline(root, 'XKG · Cross-application knowledge graph', 'One shared meaning', 'across every application.');
  const A = el('<div class="a" style="inset:0"></div>'); root.appendChild(A);
  const svg = svgLayer(A);
  const P = [['Finance application', 'coin', 'AP_SUPPLIERS', [['VENDOR_ID', '10482'], ['VENDOR_NAME', 'ZENTRA COMP INC'], ['PAY_SITE', 'SAN JOSE']]],
    ['Manufacturing application', 'factory', 'MFG_VENDOR', [['SUPP_NO', 'S-7731'], ['SUPP_DESC', 'Zentra Components'], ['PLANT_CD', 'P-04']]],
    ['Supply chain application', 'truck', 'PARTNER', [['PARTNER_REF', 'ZC-0091'], ['PARTNER_NM', 'Zentra Comp.'], ['REGION', 'US-W']]]];
  const px = [200, 735, 1270];
  const panels = P.map(([n, i, tb, kv], k) => card(A, px[k], 268, 450, 236, `<div style="padding:18px 22px"><div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">${ico(i, 40)}<div><div style="font-weight:700;font-size:18px">${n}</div><div class="mono" style="font-size:13px;color:#43b4ff">${tb}</div></div></div>${kv.map(([a, b], j) => `<div class="kv${j === 1 ? ' hit' : ''}" style="display:flex;justify-content:space-between;padding:9px 12px;border-radius:8px;margin-bottom:4px;font-size:15px" class="mono"><span class="mono" style="color:#8f99cc">${a}</span><span class="mono" style="color:#e6e9ff;font-weight:600">${b}</span></div>`).join('')}</div>`));
  const layer = card(A, 200, 568, 1520, 64, `<div style="display:flex;align-items:center;height:100%;padding:0 24px;gap:16px"><span class="lbl" style="color:#43b4ff;margin-right:auto">Cross-application semantic layer</span>${['Golden records', 'Business terms', 'Lineage', 'Governance'].map(s => `<span class="chip" style="font-size:14px;padding:6px 12px">${s}</span>`).join('')}</div>`);
  const drops = px.map(x => path(svg, `M${x + 225} 504 V568`, 'rgba(51,169,255,.6)', 2));
  const dd = drops.map(() => dot(svg, '#43b4ff'));
  const conv = px.map(x => path(svg, `M${x + 225} 504 C ${x + 225} 640, 960 600, 960 690`, 'rgba(245,165,36,.85)', 2.5));
  const cd = conv.map(() => dot(svg, '#ffc35c', 5));
  const gold = card(A, 600, 690, 720, 150, `<div style="padding:20px 26px"><div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">${check(30)}<span class="disp" style="font-size:30px;font-weight:800">Supplier · Zentra Components</span><span class="tag" style="margin-left:auto;background:rgba(47,209,138,.14);color:#5fe3a6;border:1px solid rgba(47,209,138,.45)">One trusted record</span></div><div style="display:flex;gap:10px">${['Finance · 10482', 'Manufacturing · S-7731', 'Supply chain · ZC-0091'].map(s => `<span class="chip mono" style="font-size:13.5px;font-weight:500">${s}</span>`).join('')}</div></div>`);
  // B: one shared meaning / no migration
  const B = el('<div class="a" style="inset:0"></div>'); root.appendChild(B);
  const svgB = svgLayer(B);
  const st1 = el(`<div class="a center disp" style="top:290px;font-size:72px;font-weight:800">One shared <span style="color:#43b4ff">meaning</span>, everywhere.</div>`); B.appendChild(st1);
  const s1w = splitWords(st1);
  const nm = el(`<div class="a center" style="top:262px"><div class="mono" style="font-size:18px;letter-spacing:.2em;color:#ff6b6b;position:relative;display:inline-block">DATA MIGRATION<span class="strike" style="position:absolute;left:-6px;right:-6px;top:50%;height:2px;background:#ff6b6b;transform-origin:0 50%"></span></div><div class="disp" style="font-size:80px;font-weight:800;color:#2fd18a;display:flex;align-items:center;justify-content:center;gap:20px;margin-top:8px"><span class="nck">${check(64)}</span>No migration</div><div class="nsub" style="font-size:28px;color:#d3d9ff;margin-top:6px">Your records stay where they are.</div></div>`); B.appendChild(nm);
  const bar = el(`<div class="a" style="left:560px;top:480px;width:800px;height:62px;border-radius:14px;border:1.5px solid rgba(51,169,255,.7);background:rgba(0,136,207,.12);box-shadow:0 0 40px rgba(0,136,207,.3);display:flex;align-items:center;justify-content:center;gap:12px;font-size:19px;font-weight:600">${ico('link', 30, '#43b4ff', 'transparent')}Each application answers in its own schema · no joins, no copies</div>`); B.appendChild(bar);
  const ax = [610, 960, 1310];
  const an = [['Finance application', 'coin'], ['Manufacturing application', 'factory'], ['Supply chain application', 'truck']].map(([n, i], k) => card(B, ax[k] - 160, 630, 320, 96, `<div style="display:flex;align-items:center;gap:14px;padding:14px 18px">${ico(i, 44)}<div><div style="font-weight:700;font-size:17px">${n}</div><div class="stay" style="font-size:14px;color:#5fe3a6;display:flex;align-items:center;gap:6px;margin-top:4px">${check(14)} Records stay in place</div></div></div>`));
  const bl = ax.map(x => path(svgB, `M${x} 542 V630`, 'rgba(51,169,255,.6)', 2)), bd = bl.map(() => dot(svgB, '#43b4ff'));
  return t => {
    BG.state.net = .8;
    const a0 = L[14] - .45;
    wordsIn(iw, t, a0 + .1, { stagger: .08, y: 40, out: L[15] - .55 });
    fx(iu, t, { at: a0 + .6, dur: .8, ease: Ease.outExpo, from: { o: 0, sx: 0 }, out: L[15] - .55, outDur: .4 });
    head(t, L[15] - .3);
    const outA = L[17] - .4;
    panels.forEach((p, i) => fx(p, t, { at: L[15] + .1 + i * .18, dur: .8, ease: Ease.out4, from: { o: 0, y: 40, blur: 10 } }));
    fx(layer, t, { at: L[15] + 1.4, dur: .8, from: { o: 0, y: 20, blur: 8 } });
    drops.forEach((p, i) => { draw(p, t, L[15] + 1.2 + i * .1, .5); pulse(dd[i], p, t, L[15] + 1.7, 1.1, i * .3); });
    // the same supplier, three systems -> one record
    panels.forEach((p, i) => { const h = $('.hit', p), q = prog(t, L[16] + .1 + i * .2, .5); h.style.background = `rgba(245,165,36,${.18 * q})`; h.style.boxShadow = `inset 0 0 0 1.5px rgba(245,165,36,${.8 * q})`; });
    conv.forEach((p, i) => { draw(p, t, L[16] + .8 + i * .1, .9); pulse(cd[i], p, t, L[16] + 1.6, 1.0, i * .3); });
    fx(gold, t, { at: L[16] + 1.6, dur: .8, ease: Ease.outBack, from: { o: 0, s: .8, blur: 10 } }); glowAt(gold, t, L[16] + 2.1, '47,209,138');
    fx(A, t, { out: outA, outDur: .55, to: { o: 0, s: 1.05, blur: 12 } });
    A.style.display = t > outA + .55 ? 'none' : 'block';
    // B
    wordsIn(s1w, t, L[17] - .05, { stagger: .08, out: L[18] - .45 });
    fx(bar, t, { at: L[17] + .5, dur: .8, ease: Ease.out4, from: { o: 0, sx: .6, blur: 8 } });
    an.forEach((c, i) => fx(c, t, { at: L[17] + .8 + i * .15, dur: .7, from: { o: 0, y: 30, blur: 8 } }));
    bl.forEach((p, i) => { draw(p, t, L[17] + 1.0 + i * .1, .5); pulse(bd[i], p, t, L[17] + 1.5, 1.1, i * .3); });
    fx(nm, t, { at: L[18] - .2, dur: .6, from: { o: 0, y: 16 } });
    $('.strike', nm).style.transform = `scaleX(${prog(t, L[18] + .05, .4, Ease.out3)})`;
    pop($('.nck', nm), t, L[18] + .2, .5);
    fx($('.nsub', nm), t, { at: L[18] + .7, dur: .6, from: { o: 0, y: 12 } });
    an.forEach((c, i) => { pop($('.stay', c), t, L[18] + 1.1 + i * .15, .45); glowAt(c, t, L[18] + 1.1 + i * .15, '47,209,138'); });
  };
});

// ============================================================ S6 DATA ASK
scene(L[19] - .65, L[23] - .8, root => {
  const head = headline(root, 'Data Ask', 'Plain-language answers', 'across all your data.');
  const Q = 'What did we spend with Zentra Components last quarter?';
  const win = el(`<div class="win"><div class="tb"><span class="dots"><i></i><i></i><i></i></span>${ico('chat', 22, '#43b4ff', 'transparent')}Solix Data Ask</div>
    <div class="side"><div class="lbl" style="padding:6px 12px 12px">Recent questions</div>${['Top suppliers by spend', 'Late orders this week', 'Contracts expiring in Q4', 'Revenue by region', 'Open invoices over 90 days', 'Plant downtime last month'].map(s => `<div class="it" style="font-size:14px">${s}</div>`).join('')}</div>
    <div class="main">
      <div class="qb a" style="right:32px;top:24px;max-width:640px;padding:14px 20px;border-radius:16px 16px 4px 16px;background:linear-gradient(135deg,#5b4bdc,#30267b);font-size:18px;font-weight:600;box-shadow:0 10px 30px rgba(48,38,123,.6)">${Q}</div>
      <div class="think a" style="left:32px;top:100px;display:flex;align-items:center;gap:10px;font-size:16px;color:#9aa3cf"><span class="dts mono" style="color:#43b4ff;font-size:22px;letter-spacing:.1em"></span>Searching structured and unstructured data…</div>
      <div class="srcs a" style="left:32px;right:32px;top:96px;display:grid;grid-template-columns:1fr 1fr;gap:12px">${[['db', 'AP_INVOICES', 'Finance application', 'Structured', '#43b4ff'], ['db', 'PO_LINES_ALL', 'Supply chain application', 'Structured', '#43b4ff'], ['doc', 'Contract_2214.pdf', 'Contracts library', 'Unstructured', '#a99bff'], ['mail', 'Zentra renewal thread', 'Email archive', 'Unstructured', '#a99bff']].map(([i, n, s, k, c]) => `<div class="card src" style="position:relative;padding:11px 16px;display:flex;align-items:center;gap:12px">${ico(i, 34, c, c + '22')}<div style="flex:1"><div class="mono" style="font-size:14.5px;font-weight:600">${n}</div><div style="font-size:12.5px;color:#8f99cc">${s}</div></div><span class="tag" style="background:${c}1f;color:${c};border:1px solid ${c}55">${k}</span><span class="sck">${check(20)}</span></div>`).join('')}</div>
      <div class="ans a card" style="left:32px;right:32px;top:250px;padding:20px 24px">
        <div class="def" style="display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:10px;background:rgba(47,209,138,.10);border:1px solid rgba(47,209,138,.45);font-size:15.5px;color:#c9f5df;margin-bottom:16px">${check(22)}<span><b style="color:#5fe3a6">Certified definition applied:</b> vendor spend = invoiced amount, net of credits · from your Knowledge Graph</span></div>
        <table class="t"><tr><th>Supplier</th><th>Period</th><th>Currency</th><th style="text-align:right">Total spend</th></tr><tr><td style="font-weight:700">Zentra Components</td><td>Q3 2026</td><td>USD</td><td class="amt mono" style="text-align:right;font-size:22px;font-weight:700;color:#5fe3a6">$0.00</td></tr></table>
        <div style="display:flex;gap:14px;margin-top:16px;align-items:flex-start"><div style="flex:1"><div class="lbl" style="margin-bottom:10px">Sources</div><div style="display:flex;flex-wrap:wrap;gap:8px">${['[1] AP_INVOICES · 42 rows', '[2] Contract_2214.pdf · p. 4', '[3] Certified measure · Vendor spend'].map(s => `<span class="chip cit mono" style="font-size:13.5px;font-weight:500;border-color:rgba(51,169,255,.55)">${s}</span>`).join('')}</div></div>
        <div class="sql mono" style="width:420px;height:118px;padding:12px 14px;border-radius:10px;background:#07061a;border:1px solid rgba(130,150,255,.2);font-size:12.5px;line-height:1.55;color:#9fb0ff;white-space:pre"></div></div>
      </div>
      <div class="a" style="left:32px;right:32px;bottom:22px;height:54px;border-radius:12px;border:1px solid rgba(130,150,255,.3);background:rgba(255,255,255,.03);display:flex;align-items:center;padding:0 18px;gap:12px">${ico('search', 26, '#8f99cc', 'transparent')}<span class="inp" style="flex:1;font-size:17px;color:#e6e9ff"></span>${ico('send', 36, '#fff', '#5b4bdc')}</div>
    </div></div>`);
  root.appendChild(win);
  const SQL = "SELECT s.name, SUM(i.amount - i.credits)\n  FROM ap_invoices i\n  JOIN suppliers s ON s.id = i.vendor_id\n WHERE s.golden_id = 'SUP-ZENTRA'\n   AND i.period = '2026-Q3';";
  return t => {
    BG.state.net = .7;
    head(t, L[19] - .5);
    fx(win, t, { at: L[19] - .45, dur: .9, ease: Ease.out4, from: { o: 0, y: 60, s: .96, blur: 12 } });
    const sent = L[19] + 1.35;
    if (t < sent) type($('.inp', win), t, L[19] - .1, 38, Q); else $('.inp', win).textContent = '';
    fx($('.qb', win), t, { at: sent, dur: .5, ease: Ease.out4, from: { o: 0, y: 40, s: .95 } });
    fx($('.think', win), t, { at: sent + .3, dur: .3, out: L[20] - .1, outDur: .25 });
    $('.dts', win).textContent = '•••'.slice(0, 1 + Math.floor(t * 4) % 3);
    $$('.src', win).forEach((s, i) => { fx(s, t, { at: L[20] + i * .18, dur: .5, from: { o: 0, y: 14, blur: 6 } }); pop($('.sck', s), t, L[20] + .9 + i * .2, .4); });
    fx($('.ans', win), t, { at: L[21] - .1, dur: .7, ease: Ease.out4, from: { o: 0, y: 30, blur: 8 } });
    glowAt($('.def', win), t, L[21] + .5, '47,209,138');
    count($('.amt', win), t, L[21] + .3, 1.3, 248500, v => '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
    $$('.cit', win).forEach((c, i) => { pop(c, t, L[22] + i * .2, .45); glowAt(c, t, L[22] + .3 + i * .2, '51,169,255', L[22] + 1.6 + i * .2); });
    type($('.sql', win), t, L[22] + .1, 95, SQL, false);
    fx($('.sql', win), t, { at: L[22] - .1, dur: .4 });
  };
});

// ============================================================ S7 AI WAREHOUSE
scene(L[23] - .65, L[27] - .8, root => {
  const head = headline(root, 'AI Warehouse', 'Your people build', 'their own AI applications.');
  const svg = svgLayer(root);
  const ex = card(root, 150, 300, 470, 92, `<div style="display:flex;align-items:center;gap:16px;padding:16px 20px">${ico('user', 54, '#fff', 'linear-gradient(135deg,#0088cf,#30267b)', 'border-radius:50%')}<div><div style="font-weight:700;font-size:20px">Domain expert</div><div style="font-size:15px;color:#8f99cc">Describes it, in plain language</div></div></div>`);
  const roles = el(`<div class="a" style="left:150px;top:404px;display:flex;gap:10px">${['Finance', 'Supply chain', 'Operations', 'Compliance'].map(r => `<span class="chip" style="font-size:14px">${r}</span>`).join('')}</div>`); root.appendChild(roles);
  const rch = $$('.chip', roles);
  const PR = 'Build a supplier-risk app: late deliveries, open spend and contract terms.';
  const pb = card(root, 150, 470, 520, 118, `<div style="padding:16px 20px"><div class="lbl" style="color:#43b4ff;margin-bottom:10px">You describe</div><div class="pt" style="font-size:18px;line-height:1.4;color:#e6e9ff"></div></div>`);
  const S = [['1', 'chat', 'Describe', 'In natural language', '#43b4ff', '51,169,255'], ['2', 'sense', 'Data Sense', 'Surfaces tables and documents', '#5fe3d0', '38,198,176'], ['3', 'layers', 'AI Warehouse', 'Builds and versions it, governed', '#f5a524', '245,165,36'], ['4', 'app', 'Your AI application', 'Owned by your analyst', '#2fd18a', '47,209,138']];
  const sy = [270, 368, 466, 564];
  const st = S.map(([n, i, a, b, c], k) => card(root, 1110, sy[k], 640, 80, `<div style="display:flex;align-items:center;gap:16px;padding:0 20px;height:100%"><span class="mono" style="width:30px;height:30px;border-radius:50%;border:1.5px solid ${c};color:${c};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700">${n}</span>${ico(i, 42, c, c + '22')}<div style="flex:1"><div style="font-weight:700;font-size:19px">${a}</div><div style="font-size:14.5px;color:#8f99cc">${b}</div></div><span class="sk">${check(24, c)}</span></div>`));
  const link = path(svg, 'M670 529 C 860 529, 900 310, 1110 310', 'rgba(51,169,255,.6)', 2), ld = dot(svg, '#43b4ff');
  const vline = path(svg, 'M1135 350 V564', 'rgba(170,180,255,.45)', 2), vd = dot(svg, '#ffc35c');
  // isometric governed data stack
  const stack = el(`<div class="a" style="left:180px;top:610px;width:420px;height:300px;perspective:1400px"></div>`); root.appendChild(stack);
  const SL = [['#7d6bff', '#4b3bbd', 'Version-tracked'], ['#3b6dff', '#2443b8', 'Quality-checked'], ['#33a9ff', '#0a6fb0', 'Governed']];
  const slabs = SL.map(([c1, c2], i) => { const e = el(`<div class="a" style="left:60px;top:${150 - i * 58}px;width:200px;height:200px;transform-style:preserve-3d"><div style="position:absolute;inset:0;transform:rotateX(60deg) rotateZ(45deg);border-radius:18px;background:linear-gradient(135deg,${c1},${c2});box-shadow:0 0 0 1.5px rgba(255,255,255,.35) inset,0 30px 50px rgba(0,0,0,.45)"></div></div>`); stack.appendChild(e); return e; });
  const tags = SL.map(([c, , n], i) => { const e = el(`<div class="a chip" style="left:300px;top:${232 - i * 58}px;font-size:14px;color:#5fe3a6;border-color:rgba(47,209,138,.45);background:rgba(47,209,138,.10)">${check(16)} ${n}</div>`); stack.appendChild(e); return e; });
  const ver = el(`<div class="a mono chip" style="left:58px;top:-10px;font-size:14px;color:#ffc35c;border-color:rgba(245,165,36,.5)">v1.<span class="vn">0</span></div>`); stack.appendChild(ver);
  const appv = card(root, 1110, 676, 640, 220, `<div style="padding:16px 20px"><div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">${ico('chart', 30, '#2fd18a', 'rgba(47,209,138,.14)')}<span style="font-weight:700;font-size:17px">Supplier Risk</span><span class="tag" style="margin-left:auto;background:rgba(47,209,138,.14);color:#5fe3a6;border:1px solid rgba(47,209,138,.45)">Live · your data</span></div><div style="display:flex;gap:16px;align-items:flex-end;height:120px">${[.55, .8, .42, .95, .66, .74, .5, .88].map((v, i) => `<div style="flex:1;display:flex;flex-direction:column;justify-content:flex-end;height:100%"><div class="bb" data-v="${v}" style="border-radius:5px 5px 2px 2px;background:linear-gradient(180deg,${i === 3 ? '#ff6b6b,#ee2424' : '#43b4ff,#0088cf'});height:0"></div></div>`).join('')}</div></div>`);
  return t => {
    BG.state.net = .75;
    head(t, L[23] - .5);
    fx(ex, t, { at: L[23] + .1, dur: .7, from: { o: 0, x: -40, blur: 8 } });
    rch.forEach((c, i) => fx(c, t, { at: L[23] + .9 + i * .12, dur: .5, from: { o: 0, y: 12 } }));
    fx(pb, t, { at: L[24] - .2, dur: .6, from: { o: 0, y: 20, blur: 6 } });
    type($('.pt', pb), t, L[24] + .15, 42, PR);
    draw(link, t, L[24] + .5, .8); pulse(ld, link, t, L[24] + 1.2, 1.4);
    const sOn = [L[24] + .6, L[24] + 1.5, L[25] + .2, L[26] - .3];
    st.forEach((c, i) => { fx(c, t, { at: sOn[i] - .2, dur: .6, from: { o: 0, x: 40, blur: 8 } }); pop($('.sk', c), t, sOn[i] + .4, .4); });
    glowAt(st[2], t, L[25] + .4, '245,165,36', L[26] - .2); glowAt(st[3], t, L[26] - .1, '47,209,138');
    draw(vline, t, L[24] + 1.4, 1.6, Ease.lin); pulse(vd, vline, t, L[25], 1.2);
    slabs.forEach((s, i) => fx(s, t, { at: L[25] + .1 + (2 - i) * .25, dur: .7, ease: Ease.outBack, from: { o: 0, y: -80 } }));
    tags.forEach((g, i) => fx(g, t, { at: L[25] + .9 + (2 - i) * .3, dur: .5, from: { o: 0, x: -16 } }));
    fx(ver, t, { at: L[25] + 1.0, dur: .5, from: { o: 0, y: 10 } });
    count($('.vn', ver), t, L[25] + 1.2, 1.6, 4);
    fx(appv, t, { at: L[26] - .1, dur: .7, ease: Ease.out4, from: { o: 0, y: 30, blur: 8 } });
    $$('.bb', appv).forEach((b, i) => b.style.height = (+b.dataset.v * 100 * prog(t, L[26] + .2 + i * .06, .7, Ease.outBack)) + '%');
  };
});

// ============================================================ S8 AGENTIC
scene(L[27] - .65, L[30] - .8, root => {
  const head = headline(root, 'Agentic', 'Describe it. Build it.', 'Run it.');
  const svg = svgLayer(root);
  const ex = card(root, 130, 300, 470, 92, `<div style="display:flex;align-items:center;gap:16px;padding:16px 20px">${ico('user', 54, '#fff', 'linear-gradient(135deg,#0088cf,#30267b)', 'border-radius:50%')}<div><div style="font-weight:700;font-size:20px">Domain expert</div><div style="font-size:15px;color:#8f99cc">Describes the work, in plain language</div></div></div>`);
  const PR = 'Follow up on late supplier orders and draft replies.';
  const pb = card(root, 130, 412, 470, 128, `<div style="padding:16px 20px"><div class="lbl" style="color:#a99bff;margin-bottom:10px">You describe</div><div class="pt" style="font-size:19px;line-height:1.4;color:#e6e9ff"></div></div>`);
  const pchip = el(`<div class="a chip" style="left:130px;top:556px;font-size:14px;color:#c9c0ff;border-color:rgba(169,155,255,.5)">Describe it in plain language</div>`); root.appendChild(pchip);
  const C = [930, 560], R = 160;
  const orb = el(`<div class="a" style="left:${C[0] - 220}px;top:${C[1] - 220}px;width:440px;height:440px"><svg width="440" height="440" viewBox="-220 -220 440 440"><circle r="${R}" fill="rgba(20,18,60,.35)" stroke="rgba(169,155,255,.35)" stroke-width="1.5" stroke-dasharray="4 8"/><g class="cm"><path d="M${R} 0 A ${R} ${R} 0 0 0 ${R * Math.cos(-.9)} ${R * Math.sin(-.9)}" stroke="url(#cmg)" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="${R}" cy="0" r="6" fill="#d9f4ff" style="filter:drop-shadow(0 0 8px #43b4ff)"/></g><defs><linearGradient id="cmg" x1="0" y1="0" x2="0" y2="-1"><stop offset="0" stop-color="#43b4ff"/><stop offset="1" stop-color="#43b4ff" stop-opacity="0"/></linearGradient></defs></svg></div>`); root.appendChild(orb);
  const spk = el(`<div class="a" style="left:${C[0] - 75}px;top:${C[1] - 75}px;width:150px;height:150px">${sparkle(150)}</div>`); root.appendChild(spk);
  const NN = [['Build', 'gear', -90], ['Test', 'flask', 30], ['Run', 'play', 150]].map(([n, i, a]) => {
    const x = C[0] + R * Math.cos(a * Math.PI / 180), y = C[1] + R * Math.sin(a * Math.PI / 180);
    const e = el(`<div class="a" style="left:${x - 34}px;top:${y - 34}px;width:68px;text-align:center"><div class="nb" style="width:68px;height:68px;border-radius:50%;background:#15134a;border:1.5px solid rgba(169,155,255,.55);display:flex;align-items:center;justify-content:center;color:#c9c0ff"><svg viewBox="0 0 24 24" width="30" height="30" style="fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round">${IC[i]}</svg></div><div style="font-weight:700;font-size:16px;margin-top:8px">${n}</div></div>`);
    root.appendChild(e); return e;
  });
  const cap = el(`<div class="a lbl" style="left:${C[0] - 300}px;width:600px;text-align:center;top:${C[1] + R + 70}px;letter-spacing:.32em">Agentic AI builds, tests and runs it</div>`); root.appendChild(cap);
  const l1 = path(svg, `M600 476 C 680 476, 700 ${C[1]}, ${C[0] - R - 6} ${C[1]}`, 'rgba(169,155,255,.6)', 2), d1 = dot(svg, '#a99bff');
  const l2 = path(svg, `M${C[0] + R + 6} ${C[1]} C 1180 ${C[1]}, 1190 470, 1270 470`, 'rgba(47,209,138,.6)', 2), d2 = dot(svg, '#5fe3a6');
  const steps = [['search', 'Find late orders', '14 found'], ['doc', 'Check contract terms', 'Terms matched'], ['mail', 'Draft supplier messages', '14 drafts'], ['hand', 'Human in the loop', 'Approved'], ['send', 'Messages sent', 'Done']];
  const panel = card(root, 1270, 286, 500, 420, `<div style="padding:20px 22px"><div style="display:flex;align-items:center;margin-bottom:6px"><span class="disp" style="font-size:22px;font-weight:800">Supplier follow-up</span><span class="tag" style="margin-left:auto;background:rgba(47,209,138,.14);color:#5fe3a6;border:1px solid rgba(47,209,138,.45)">● Running</span></div><div style="font-size:14px;color:#8f99cc;margin-bottom:16px">Built, tested and deployed by Agentic AI</div>${steps.map(([i, n, r], k) => `<div class="sr" style="display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:10px;margin-bottom:6px;background:rgba(255,255,255,.03)">${ico(i, 32, k === 3 ? '#c9c0ff' : '#43b4ff', k === 3 ? 'rgba(125,107,255,.18)' : 'rgba(51,169,255,.14)')}<span style="flex:1;font-size:16px;font-weight:600">${n}</span><span class="rs" style="font-size:13.5px;color:${k === 3 ? '#c9c0ff' : '#5fe3a6'};margin-right:8px">${r}</span><span class="sk">${check(22, k === 3 ? '#a99bff' : '#2fd18a')}</span></div>`).join('')}</div>`);
  const days = el(`<div class="a" style="left:1270px;top:726px;width:500px;display:flex;gap:10px">${['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].map(d => `<div class="card dy" style="position:relative;flex:1;padding:10px 0;text-align:center"><div style="font-size:13px;color:#8f99cc;margin-bottom:6px">${d}</div><span class="dk">${check(22)}</span></div>`).join('')}</div>`); root.appendChild(days);
  const dlab = el(`<div class="a lbl" style="left:1270px;top:820px;width:500px;text-align:center">Runs every day</div>`); root.appendChild(dlab);
  return t => {
    BG.state.net = .8;
    head(t, L[27] - .5, L[28] + 1.9);
    // reveal headline words with the narration rhythm
    fx(ex, t, { at: L[27] + .1, dur: .7, from: { o: 0, x: -40, blur: 8 } });
    fx(pb, t, { at: L[27] + 1.0, dur: .6, from: { o: 0, y: 20, blur: 6 } });
    type($('.pt', pb), t, L[27] + 1.3, 30, PR);
    fx(pchip, t, { at: L[27] + 2.6, dur: .5, from: { o: 0, y: 10 } });
    fx(orb, t, { at: L[28] - .5, dur: .8, ease: Ease.out4, from: { o: 0, s: .7, blur: 10 } });
    $('.cm', orb).setAttribute('transform', `rotate(${(t - L[28]) * 150 - 90})`);
    $('.cm', orb).style.opacity = prog(t, L[28], .4);
    fx(spk, t, { at: L[28] - .3, dur: .9, ease: Ease.outBack, from: { o: 0, s: 0, r: -120 } });
    spk.style.transform += ` rotate(${Math.sin(t) * 5}deg) scale(${1 + Math.sin(t * 2.4) * .04})`;
    const on = [L[28] + .05, L[28] + 1.0, L[28] + 1.95];
    NN.forEach((n, i) => {
      pop(n, t, L[28] - .2 + i * .12);
      const q = prog(t, on[i], .4), nb = $('.nb', n);
      nb.style.background = `rgba(${Math.round(lerp(21, 125, q))},${Math.round(lerp(19, 107, q))},${Math.round(lerp(74, 255, q))},${lerp(1, .9, q)})`;
      nb.style.boxShadow = q > 0 ? `0 0 ${40 * q}px rgba(125,107,255,${.8 * q})` : ''; nb.style.color = q > .5 ? '#fff' : '#c9c0ff';
    });
    fx(cap, t, { at: L[28] + .3, dur: .6 });
    draw(l1, t, L[28] - .4, .7); pulse(d1, l1, t, L[28], 1.3);
    draw(l2, t, L[28] + 2.0, .6); pulse(d2, l2, t, L[28] + 2.5, 1.3);
    fx(panel, t, { at: L[28] + 2.2, dur: .7, ease: Ease.out4, from: { o: 0, x: 40, blur: 10 } });
    $$('.sr', panel).forEach((r, i) => {
      const at = L[28] + 2.6 + i * .42;
      fx(r, t, { at: L[28] + 2.35 + i * .06, dur: .4, from: { o: 0, y: 10 }, max: t > at ? 1 : .45 });
      pop($('.sk', r), t, at, .4); fx($('.rs', r), t, { at: at + .1, dur: .4 });
      r.style.background = t > at && t < at + .5 ? 'rgba(51,169,255,.14)' : 'rgba(255,255,255,.03)';
    });
    $$('.dy', days).forEach((d, i) => { fx(d, t, { at: L[29] + .1 + i * .1, dur: .5, from: { o: 0, y: 16 } }); pop($('.dk', d), t, L[29] + .6 + i * .22, .4); });
    fx(dlab, t, { at: L[29] + 1.0, dur: .5 });
  };
});

// ============================================================ S9 OPEN BY DESIGN
scene(L[30] - .65, L[35] - .8, root => {
  const head = headline(root, 'Open by design', 'Any LLM. Any application.', 'Any data platform.', { wordAt: [L[31] - .1, L[31] + .05, L[32] - .1, L[32] + .05] });
  const svg = svgLayer(root);
  const core = card(root, 750, 470, 420, 176, `<div style="padding:20px 22px"><div style="display:flex;align-items:center;gap:12px;margin-bottom:16px"><img src="assets/icon.png" style="width:40px;height:40px"><div><div class="disp" style="font-weight:800;font-size:22px">Solix Enterprise AI</div><div class="lbl" style="font-size:11px;margin-top:4px">EAI platform</div></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">${['Data Sense', 'Data Ask', 'AI Warehouse', 'Agentic'].map(s => `<span class="chip" style="justify-content:center;font-size:14px;padding:7px">${s}</span>`).join('')}</div></div>`);
  const tl = el(`<div class="a center lbl" style="top:318px">Any LLM</div>`); root.appendChild(tl);
  const llm = [['cloud', 'Hosted LLM', 700], ['cpu', 'Open-source LLM', 960], ['shield', 'Your own model', 1220]].map(([i, n, x]) => { const e = el(`<div class="a chip" style="left:${x - 110}px;width:220px;top:350px;height:50px;justify-content:center">${ico(i, 26, '#43b4ff', 'transparent')}${n}</div>`); root.appendChild(e); return e; });
  const lp = [700, 960, 1220].map((x, i) => path(svg, `M${x} 400 C ${x} 440, ${860 + i * 100} 430, ${860 + i * 100} 470`, 'rgba(51,169,255,.6)', 2));
  const ld = lp.map(() => dot(svg, '#43b4ff'));
  const ay = [440, 510, 580, 650];
  const al = el(`<div class="a lbl" style="left:190px;top:408px">Any application</div>`), dl = el(`<div class="a lbl" style="left:1410px;top:408px">Any data platform</div>`); root.appendChild(al); root.appendChild(dl);
  const apps = [['coin', 'Finance application'], ['factory', 'Manufacturing application'], ['users', 'CRM'], ['truck', 'Supply chain app']].map(([i, n], k) => card(root, 190, ay[k], 320, 54, `<div style="display:flex;align-items:center;gap:12px;padding:0 14px;height:100%">${ico(i, 32)}<span style="font-size:16px;font-weight:600">${n}</span></div>`));
  const plats = [['lake', 'Data lakehouse'], ['cloud', 'Cloud warehouse'], ['db', 'Databases'], ['folder', 'File stores']].map(([i, n], k) => card(root, 1410, ay[k], 320, 54, `<div style="display:flex;align-items:center;gap:12px;padding:0 14px;height:100%">${ico(i, 32, '#5fe3d0', 'rgba(38,198,176,.14)')}<span style="font-size:16px;font-weight:600">${n}</span></div>`));
  const ap = ay.map(y => path(svg, `M510 ${y + 27} C 640 ${y + 27}, 620 558, 750 558`, 'rgba(51,169,255,.55)', 2));
  const pp = ay.map(y => path(svg, `M1170 558 C 1300 558, 1280 ${y + 27}, 1410 ${y + 27}`, 'rgba(38,198,176,.6)', 2));
  const ad = ap.map(() => dot(svg, '#43b4ff')), pd = pp.map(() => dot(svg, '#5fe3d0'));
  const fit = el(`<div class="a" style="left:610px;top:752px;width:700px;height:62px;border-radius:14px;border:1.5px solid rgba(47,209,138,.6);background:rgba(47,209,138,.08);display:flex;align-items:center;justify-content:center;gap:12px;font-size:20px;font-weight:600">${ico('link', 30, '#5fe3a6', 'transparent')}Works alongside what you already run.</div>`); root.appendChild(fit);
  return t => {
    BG.state.net = .85;
    head(t, L[30] - .3, L[33] - .05);
    fx(core, t, { at: L[30] + .1, dur: .9, ease: Ease.outBack, from: { o: 0, s: .7, blur: 10 } }); glowAt(core, t, L[30] + .6, '238,36,36');
    fx(tl, t, { at: L[31] - .1, dur: .5 });
    llm.forEach((c, i) => fx(c, t, { at: L[31] - .05 + i * .12, dur: .6, ease: Ease.out4, from: { o: 0, y: -24, blur: 6 } }));
    lp.forEach((p, i) => { draw(p, t, L[31] + .3 + i * .1, .5); pulse(ld[i], p, t, L[31] + .7, 1.1, i * .3); });
    fx(al, t, { at: L[32] - .1, dur: .5 });
    apps.forEach((c, i) => fx(c, t, { at: L[32] - .05 + i * .1, dur: .6, ease: Ease.out4, from: { o: 0, x: -40, blur: 6 } }));
    ap.forEach((p, i) => { draw(p, t, L[32] + .3 + i * .08, .6); pulse(ad[i], p, t, L[32] + .8, 1.2, i * .25); });
    fx(dl, t, { at: L[33] - .1, dur: .5 });
    plats.forEach((c, i) => fx(c, t, { at: L[33] - .05 + i * .1, dur: .6, ease: Ease.out4, from: { o: 0, x: 40, blur: 6 } }));
    pp.forEach((p, i) => { draw(p, t, L[33] + .3 + i * .08, .6); pulse(pd[i], p, t, L[33] + .8, 1.2, i * .25); });
    fx(fit, t, { at: L[34] + .2, dur: .7, ease: Ease.out4, from: { o: 0, y: 20, sx: .8, blur: 8 } });
    fit.style.boxShadow = `0 0 ${50 * prog(t, L[34] + .6, .6)}px rgba(47,209,138,.35)`;
  };
});

// ============================================================ S10 END CARD
scene(L[35] - .65, TOTAL + 1, root => {
  const logo = el(`<img class="a" src="assets/logo_white.png" style="left:${960 - 300}px;top:330px;height:137px;transform-origin:65px 50%">`); root.appendChild(logo);
  const eai = el(`<div class="a center disp" style="top:540px;font-size:30px;font-weight:700;letter-spacing:.6em;padding-left:.6em">ENTERPRISE AI</div>`); root.appendChild(eai);
  const line = el(`<div class="a" style="left:810px;top:600px;width:300px;height:3px;background:linear-gradient(90deg,transparent,#ee2424,transparent)"></div>`); root.appendChild(line);
  const tg = el(`<div class="a center disp" style="top:630px;font-size:40px;font-weight:600">Put AI in the hands of your business.</div>`); root.appendChild(tg);
  const tw = splitWords(tg);
  const ev = el(`<div class="a center mono" style="top:760px;font-size:15px;letter-spacing:.5em;color:#9aa3cf">SOLIX EMPOWER 2026</div>`); root.appendChild(ev);
  const svg = svgLayer(root);
  const rings = [0, 1].map(i => { const c = document.createElementNS(NS, 'circle'); c.setAttribute('cy', 398); c.setAttribute('fill', 'none'); c.setAttribute('stroke', i ? '#ee2424' : '#33a9ff'); svg.appendChild(c); return c; });
  return t => {
    BG.state.net = lerp(.85, 1.2, prog(t, L[35] - .5, 2));
    const a0 = L[35] - .45;
    const iconFrac = 376 / 1797, slide = prog(t, a0 + .55, 1.0, Ease.inOut5);
    logo.style.clipPath = `inset(0 ${((1 - iconFrac) * (1 - slide) * 100).toFixed(2)}% 0 0)`;
    const sIn = prog(t, a0, .7, Ease.outBack); logo.style.opacity = prog(t, a0, .25);
    const dx = (300 - 65) * (1 - slide);
    logo.style.transform = `translateX(${dx}px) scale(${.2 + .8 * sIn})`;
    rings.forEach((c, i) => { const p = prog(t, a0 + .1 + i * .15, 1.6); c.setAttribute('cx', 960); c.setAttribute('r', 60 + p * 460); c.setAttribute('stroke-width', 2.5 * (1 - p) + .3); c.style.opacity = (p > 0 ? 1 - p : 0) * .7; });
    fx(eai, t, { at: L[35] + .1, dur: 1, from: { o: 0, y: 14, blur: 10 } });
    eai.style.letterSpacing = (1.1 - .5 * prog(t, L[35] + .1, 1.6, Ease.out3)) + 'em';
    fx(line, t, { at: L[35] + .6, dur: .9, ease: Ease.outExpo, from: { o: 0, sx: 0 } });
    wordsIn(tw, t, L[36] - .05, { stagger: .08 });
    fx(ev, t, { at: L[36] + 2.2, dur: .9, from: { o: 0, y: 10 } });
    BG.state.black = prog(t, TOTAL - 1.4, 1.4, Ease.inOut3);
  };
});

// ============================================================ master clock
const logo = $('#logo'), cap = $('#cap'), capt = $('#capt'), flash = $('#flash'), corners = $$('.corner');
function seek(t) {
  BG.state.black = 0;
  // hard cuts: each scene is shown in full until the next one starts (no transitions)
  SC.forEach((s, i) => {
    const next = SC[i + 1] ? SC[i + 1].tin : 1e9;
    const vis = t >= s.tin - .01 && t < next;
    s.root.style.display = vis ? 'block' : 'none';
    if (!vis) return;
    s.update(t);
    const push = .022 * clamp((t - s.tin) / (next - s.tin));
    s.root.style.opacity = 1;
    s.root.style.transform = `scale(${(1 + push).toFixed(5)})`;
    s.root.style.filter = '';
  });
  flash.style.opacity = 0;
  // chrome
  const lo = prog(t, 5.9, .8) * (1 - prog(t, L[35] - .8, .5));
  logo.style.opacity = lo; logo.style.visibility = lo > 0 ? 'visible' : 'hidden';
  corners.forEach(c => c.style.opacity = prog(t, .6, 1.2) * (1 - BG.state.black));
  let line = null;
  TLD.lines.forEach((l, i) => { const nx = TLD.lines[i + 1]; const end = Math.min(l.end + .45, nx ? nx.start - .1 : 1e9); if (t >= l.start - .15 && t < end) line = { l, end }; });
  if (line) {
    capt.textContent = line.l.cap;
    cap.style.opacity = Math.min(prog(t, line.l.start - .15, .25), 1 - prog(t, line.end - .2, .2)) * (1 - BG.state.black);
  } else cap.style.opacity = 0;
  BG.render(t);
}
window.seek = seek;
window.TOTAL = TOTAL;
window.ready = Promise.all([document.fonts.ready, ...$$('img').map(i => i.complete ? 1 : new Promise(r => { i.onload = r; i.onerror = r; }))]);
