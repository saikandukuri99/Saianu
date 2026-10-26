// White-background variant (?light): swap the dark UI palette for a light one.
'use strict';
if (LIGHT) {
  document.body.classList.add('light');
  $('#logo').src = 'assets/logo_dark.png';
  $$('img').forEach(i => { if (i.getAttribute('src') === 'assets/logo_white.png') i.src = 'assets/logo_dark.png'; });
  const hex = h => { h = h.replace('#', ''); if (h.length === 3) h = [...h].map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
  const parse = s => { s = s.trim(); if (s[0] === '#') return [...hex(s), 1]; const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return [p[0], p[1], p[2], p[3] ?? 1]; };
  const rgb2hsl = ([r, g, b]) => { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2; let h = 0, s = 0; if (mx !== mn) { const d = mx - mn; s = l > .5 ? d / (2 - mx - mn) : d / (mx + mn); h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h /= 6; } return [h, s, l]; };
  const hsl2rgb = ([h, s, l]) => { const f = n => { const k = (n + h * 12) % 12, a = s * Math.min(l, 1 - l); return Math.round(255 * (l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)))); }; return [f(0), f(8), f(4)]; };
  // text: light neutrals -> dark navy tones; light accents -> deeper accents
  const fg = s => {
    const c = parse(s); if (!c) return s;
    const [h, sat, l] = rgb2hsl(c);
    if (l < (sat > .5 ? .45 : .55)) return s;
    let out;
    if (sat < .55 || l > .88) out = hsl2rgb([.68, .45, Math.max(.12, 1.02 - l)]);        // neutral text
    else out = hsl2rgb([h, Math.min(1, sat), Math.min(l * .62, .38)]);                                    // accent text
    return `rgba(${out.join(',')},${c[3]})`;
  };
  // fills: white-ish washes -> navy washes; dark navy panels -> light panels
  const bg = s => s.replace(/rgba?\([^)]+\)|#[0-9a-fA-F]{6}\b/g, m => {
    const c = parse(m); if (!c) return m;
    const [h, sat, l] = rgb2hsl(c);
    if (l > .9 && sat < .2) return `rgba(30,28,90,${Math.min(1, c[3] * 1.6)})`;
    if (l < .3) return `rgba(${hsl2rgb([h, .5, .975]).join(',')},${Math.max(.9, c[3])})`;
    return m;
  });
  $$('[style]').forEach(e => {
    if (e.closest('.keep')) return;
    const st = e.style;
    if (['bar', 'qb', 'sql', 'av'].some(c => e.classList.contains(c))) return;
    // text sitting on its own saturated fill (badges, icon chips) keeps its colour
    const own = parse((st.background.match(/rgba?\([^)]+\)|#[0-9a-fA-F]{6}\b/) || [''])[0] || '');
    const onColour = own && own[3] > .6 && rgb2hsl(own)[1] > .35 && rgb2hsl(own)[2] < .8;
    if (st.color && !onColour) st.color = fg(st.color);
    if (st.background && !st.background.includes('url') && !onColour) st.background = bg(st.background);
  });
  $$('svg [stroke]').forEach(e => { const c = parse(e.getAttribute('stroke')); if (c) { const [h, s, l] = rgb2hsl(c); if (l > .7 && s < .9 && !e.closest('.keep')) e.setAttribute('stroke', `rgba(${hsl2rgb([h, Math.min(1, s), .45]).join(',')},${Math.min(1, c[3] * 1.4)})`); } });
  $$('svg [fill]').forEach(e => { const c = parse(e.getAttribute('fill')); if (c && rgb2hsl(c)[2] < .3 && !e.closest('.keep')) e.setAttribute('fill', `rgba(232,234,248,${Math.min(1, c[3] + .3)})`); });
  $$('svg text').forEach(e => { if ((e.getAttribute('fill') || '').toLowerCase() === '#e6e9ff') e.setAttribute('fill', '#1b1848'); });
}
