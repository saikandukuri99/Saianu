// Minimal stroke icon set (24x24 viewBox)
const IC = {
  db: '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
  app: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M8 4v5"/>',
  doc: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
  chat: '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
  layers: '<path d="M12 3 2 8l10 5 10-5z"/><path d="m2 13 10 5 10-5"/><path d="m2 17.5 10 5 10-5" opacity=".6"/>',
  bolt: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
  sense: '<path d="M12 2 22 12 12 22 2 12z"/><circle cx="12" cy="12" r="3"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
  lock: '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
  link: '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/>',
  cloud: '<path d="M7 18a5 5 0 1 1 1-9.9A6 6 0 0 1 19.5 10 4 4 0 0 1 18 18z"/>',
  graph: '<circle cx="5" cy="6" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M7.3 7 10.7 16M16.7 7l-3.4 9M7.5 6h9"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
  truck: '<path d="M2 6h12v10H2zM14 10h4l3 3v3h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
  factory: '<path d="M2 21V10l6 4V10l6 4V6h8v15z"/>',
  coin: '<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1-1.6-1.5-3-1.5-1.8 0-3 .9-3 2s1.2 1.7 3 2 3 .9 3 2-1.2 2-3 2c-1.4 0-2.5-.5-3-1.5M12 6v2M12 16v2"/>',
  users: '<circle cx="9" cy="8" r="3.5"/><path d="M2 20c1-3.5 3.6-5 7-5s6 1.5 7 5"/><circle cx="17" cy="7" r="2.5"/><path d="M17 12.5c2.5 0 4.3 1.3 5 4"/>',
  lake: '<path d="M2 15c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 19c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M6 10 12 4l6 6"/>',
  folder: '<path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  cpu: '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
  play: '<path d="M7 4v16l13-8z"/>',
  flask: '<path d="M9 3h6M10 3v6L4 19a2 2 0 0 0 1.7 3h12.6A2 2 0 0 0 20 19l-6-10V3"/>',
  refresh: '<path d="M20 11a8 8 0 0 0-14.8-4M4 4v4h4M4 13a8 8 0 0 0 14.8 4M20 20v-4h-4"/>',
  hand: '<path d="M8 13V5.5a1.5 1.5 0 0 1 3 0V12M11 11V4.5a1.5 1.5 0 0 1 3 0V12M14 11.5V6a1.5 1.5 0 0 1 3 0v8a7 7 0 0 1-7 7h-.5a6 6 0 0 1-5-2.7L2 14.5a1.5 1.5 0 0 1 2.4-1.8L8 16"/>',
  send: '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15v3M11 11v7M15 7v11M19 12v6"/>',
  shield: '<path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
  tag: '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
};
function ico(name, size = 40, color = '#33a9ff', bg = 'rgba(51,169,255,.14)', extra = '') {
  return `<span class="ico" style="width:${size}px;height:${size}px;color:${color};background:${bg};${extra}"><svg viewBox="0 0 24 24">${IC[name]}</svg></span>`;
}
// 4-point AI sparkle (gradient filled)
let _spk = 0;
function sparkle(size = 120, glow = true) {
  const id = 'spk' + (_spk++);
  return `<svg width="${size}" height="${size}" viewBox="-60 -60 120 120" style="overflow:visible">
  <defs><linearGradient id="${id}" x1="0" y1="-1" x2="0" y2="1"><stop offset="0" stop-color="#9fe8ff"/><stop offset=".5" stop-color="#33a9ff"/><stop offset="1" stop-color="#0088cf"/></linearGradient>
  <radialGradient id="${id}g"><stop offset="0" stop-color="#33a9ff" stop-opacity=".55"/><stop offset="1" stop-color="#33a9ff" stop-opacity="0"/></radialGradient></defs>
  ${glow ? `<circle r="58" fill="url(#${id}g)"/>` : ''}
  <path d="M0-44C4-14 14-4 44 0 14 4 4 14 0 44-4 14-14 4-44 0-14-4-4-14 0-44z" fill="url(#${id})"/>
  <path d="M30-38C31.5-31 33-29.5 40-28 33-26.5 31.5-25 30-18 28.5-25 27-26.5 20-28 27-29.5 28.5-31 30-38z" fill="#c9f2ff"/>
  </svg>`;
}

// AI processor chip: glowing rounded die with pins and an "AI" label
let _chip = 0;
function aiChip(size = 112) {
  const id = 'chip' + (_chip++);
  const pins = [-24, -8, 8, 24].map(p => `<rect x="${p - 3}" y="-50" width="6" height="12" rx="2"/><rect x="${p - 3}" y="38" width="6" height="12" rx="2"/><rect x="-50" y="${p - 3}" width="12" height="6" rx="2"/><rect x="38" y="${p - 3}" width="12" height="6" rx="2"/>`).join('');
  return `<svg width="${size}" height="${size}" viewBox="-60 -60 120 120" style="overflow:visible">
  <defs><linearGradient id="${id}" x1="0" y1="-1" x2="0" y2="1"><stop offset="0" stop-color="#33a9ff"/><stop offset="1" stop-color="#0060b0"/></linearGradient>
  <radialGradient id="${id}g"><stop offset="0" stop-color="#33a9ff" stop-opacity=".5"/><stop offset="1" stop-color="#33a9ff" stop-opacity="0"/></radialGradient></defs>
  <circle r="60" fill="url(#${id}g)"/>
  <g fill="#7fd0ff">${pins}</g>
  <rect x="-38" y="-38" width="76" height="76" rx="14" fill="url(#${id})" stroke="#9fe8ff" stroke-width="2"/>
  <rect x="-28" y="-28" width="56" height="56" rx="9" fill="none" stroke="rgba(255,255,255,.45)" stroke-width="1.5"/>
  <text x="0" y="11" text-anchor="middle" font-family="Inter Display,Inter" font-weight="800" font-size="30" fill="#fff">AI</text>
  </svg>`;
}
