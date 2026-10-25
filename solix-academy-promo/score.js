// THE SCORE: Solix Academy promo.
// The voiceover is the spine: every line is placed here from its measured length (vo/lines.json),
// and the sections, music bars, SFX and on-screen text all hang off those times.
(function () {
  const node = typeof require !== 'undefined';
  const U = node ? require('./engine/util') : globalThis.U;
  const MU = node ? require('./engine/music') : globalThis.MUSIC;
  const VO_LINES = node ? require('./vo/lines.json') : globalThis.VO_LINES;
  const { m, makeClock } = MU;

  const FPS = 30;
  const FORMAT = U.pickFormat('16:9');
  const [W, H] = U.formatSize(FORMAT);
  const SAFE = U.safeArea(W, H);
  const STYLE = 'flat';

  // brand
  const C = { blue: '#0088cf', red: '#ee2424', indigo: '#30267b', ink: '#07061a', night: '#0c0a2a', white: '#ffffff', blueHi: '#2fb0f0', mist: '#b9c6e6' };

  // ---------- the three pillar presenters (HeyGen avatar clips, their own voices) ----------
  const AVATARS = [
    { id: 'av1', name: 'data', dur: 7.56, frames: 189, fps: 25, color: C.blue, hi: C.blueHi, icon: 'database' },
    { id: 'av2', name: 'people', dur: 7.6, frames: 190, fps: 25, color: C.red, hi: '#ff5a5a', icon: 'people' },
    { id: 'av3', name: 'governance', dur: 5.5, frames: 144, fps: 25, color: C.indigo, hi: '#8d7bff', icon: 'shield' }, // the clip's last 0.26 s is black
  ];

  // ---------- timeline: narration lines + avatar clips (gap = silence BEFORE the item) ----------
  const LEAD = 2.4; // a calm opening before the first line
  const GAP = { a02: 1.5, a03: 0.25, a04: 0.25, a05: 0.3, a06: 0.45, a07: 0.5, av1: 0.7, av2: 0.6, av3: 0.6, a08: 0.6,
    a09: 1.3, a10: 0.3, a11: 0.7, a12: 0.7, a13: 0.7, a14: 0.6, a15: 0.6, a16: 0.9, a17: 0.2, a18: 0.35, a19: 0.35,
    a20: 0.6, a21: 0.5, a22: 0.45, a23: 0.3, a24: 0.32, a25: 0.45 };
  const ORDER = [...VO_LINES.filter((l) => l.id <= 'a07'), ...AVATARS.map((a) => ({ id: a.id, avatar: a, dur: a.dur, text: '' })), ...VO_LINES.filter((l) => l.id > 'a07')];
  const vo = [];
  let cur = LEAD;
  for (const L of ORDER) {
    cur += GAP[L.id] || 0;
    vo.push({ ...L, t: +cur.toFixed(3), end: +(cur + L.dur).toFixed(3), words: [] });
    cur += L.dur;
  }
  const V = Object.fromEntries(vo.map((l) => [l.id, l]));
  AVATARS.forEach((a) => { a.t = V[a.id].t; a.end = V[a.id].end; });
  // estimated word times (proportional to letters, with room for punctuation pauses)
  for (const l of vo) {
    if (!l.text) continue;
    const ws = l.text.split(/\s+/);
    const wt = ws.map((w) => w.replace(/[^A-Za-z0-9]/g, '').length + 2 + (/[,:]$/.test(w) ? 3 : /[.?]$/.test(w) ? 5 : 0));
    const sum = wt.reduce((a, b) => a + b, 0);
    let acc = 0;
    const span = l.dur - 0.12;
    l.words = ws.map((w, i) => { const t0 = l.t + 0.04 + (acc / sum) * span; acc += wt[i]; return { w, t: +t0.toFixed(3), end: +(l.t + 0.04 + (acc / sum) * span).toFixed(3) }; });
  }
  const wordT = (id, word, n = 0) => { const hits = V[id].words.filter((x) => x.w.toLowerCase().replace(/[^a-z0-9-]/g, '').startsWith(word.toLowerCase())); return (hits[n] || hits[0]).t; };

  const DURATION = +(V.a25.end + 1.6).toFixed(2);

  // ---------- scenes (what is on screen) ----------
  const SC = {
    intro: [0, V.a07.t - 0.3],
    pillars: [V.a07.t - 0.3, V.a08.t - 0.4],
    bridge: [V.a08.t - 0.4, V.a09.t - 1.1],
    reveal: [V.a09.t - 1.1, V.a11.t - 0.4],
    s01: [V.a11.t - 0.4, V.a12.t - 0.4],
    s02: [V.a12.t - 0.4, V.a13.t - 0.35],
    s03: [V.a13.t - 0.35, V.a14.t - 0.35],
    s04: [V.a14.t - 0.35, V.a15.t - 0.35],
    s05: [V.a15.t - 0.35, V.a16.t - 0.5],
    mission: [V.a16.t - 0.5, V.a21.t - 0.15],
    end: [V.a21.t - 0.15, DURATION],
  };
  // music sections (also used by engine/tools/levels.js)
  const S = {
    intro: [0, SC.pillars[0]],
    pillars: [SC.pillars[0], SC.reveal[0]],
    academy: [SC.reveal[0], SC.mission[0]],
    finale: [SC.mission[0], DURATION],
  };

  // ---------- music clock: the beat kicks in on a downbeat at the pillars section ----------
  const BPM = 112, BAR = (60 / BPM) * 4;
  const beatIn = S.pillars[0];
  const k0 = Math.ceil(beatIn / BAR);
  const clock = makeClock({ bpm: BPM, offset: beatIn - k0 * BAR });
  const { T, BEAT } = clock;
  const barOf = (t) => Math.round((t - clock.OFFSET) / BAR);
  const B = { first: barOf(0) - 1, beat: k0, academy: barOf(S.academy[0]), finale: barOf(S.finale[0]) };

  // ---------- key events ----------
  const ev = {
    sweep: V.a01.end + 0.15, // soft digital frequency sweep + title, once the first line has landed
    title: V.a01.end + 0.15,
    chips: [V.a02.t + 0.35, V.a03.t, V.a04.t],
    boardroom: V.a04.t + 1.2, // the city dissolves into the boardroom
    question: V.a06.t,
    beatIn,
    pillar: AVATARS.map((a) => a.t),
    pillarsTag: V.av3.end + 0.15,
    difference: V.a08.t,
    logo: 0,
    academyWord: 0,
    platform: V.a10.t,
    experts: V.a11.t,
    immersive: V.a12.t,
    journey: V.a13.t,
    tracks: V.a14.t,
    formats: V.a15.t,
    finale: S.finale[0],
    future: V.a20.t,
    endcard: V.a21.t - 0.15,
    learn: V.a22.t,
    innovate: V.a23.t,
    transform: V.a24.t,
    url: V.a25.t - 0.05,
  };
  ev.logo = wordT('a09', 'solix');
  ev.academyWord = wordT('a09', 'academy');
  // a soft whoosh wherever a card or panel glides in
  ev.whooshes = [ev.platform + 0.2, SC.s01[0] + 0.3, SC.s02[0] + 0.3, SC.s03[0] + 0.25, SC.s04[0] + 0.25, SC.s05[0] + 0.25];

  // ---------- harmony (F major / D minor), one chord per bar ----------
  const CH = {
    Dm9: { notes: ['D3', 'A3', 'E4', 'F4'], bass: 'D2' },
    Bbmaj7: { notes: ['Bb2', 'F3', 'A3', 'D4'], bass: 'Bb1' },
    Dm: { notes: ['D3', 'F3', 'A3', 'D4'], bass: 'D2' },
    Bb: { notes: ['Bb2', 'F3', 'Bb3', 'D4'], bass: 'Bb1' },
    F: { notes: ['F3', 'A3', 'C4', 'F4'], bass: 'F1' },
    C: { notes: ['C3', 'G3', 'C4', 'E4'], bass: 'C2' },
    Fadd9: { notes: ['F3', 'C4', 'G4', 'A4'], bass: 'F1' },
  };
  const progs = { intro: ['Dm9', 'Dm9', 'Bbmaj7', 'Bbmaj7'], pillars: ['Dm', 'Bb', 'F', 'C'], academy: ['F', 'C', 'Dm', 'Bb'], finale: ['Bb', 'C', 'Dm', 'C'] };
  const lastBar = barOf(DURATION) + 1;
  const chords = [];
  for (let b = B.first; b <= lastBar; b++) {
    const t0 = T(b), t1 = T(b + 1);
    if (t0 >= ev.transform) break;
    const sec = b < B.beat ? 'intro' : b < B.academy ? 'pillars' : b < B.finale ? 'academy' : 'finale';
    const base = sec === 'intro' ? B.first : B[sec === 'pillars' ? 'beat' : sec];
    const name = progs[sec][(((b - base) % 4) + 4) % 4];
    chords.push({ bar: b, sec, name, t0, t1: Math.min(t1, ev.transform), ...CH[name], notes: CH[name].notes.map(m), bass: m(CH[name].bass) });
  }
  // the resolution: everything lands on F on "Transform" and rings out
  chords.push({ bar: null, sec: 'end', name: 'Fadd9', t0: ev.transform, t1: DURATION, notes: CH.Fadd9.notes.map(m), bass: m(CH.Fadd9.bass) });
  const chordAt = (t) => chords.find((c) => t >= c.t0 && t < c.t1) || null;

  // ---------- named moments (render.js stills @pillar1, verify...) ----------
  const markers = {
    title: { t: ev.title },
    beat: { t: ev.beatIn, sync: 'a' },
    pillar1: { t: ev.pillar[0], sync: 'av' },
    pillar2: { t: ev.pillar[1], sync: 'av' },
    pillar3: { t: ev.pillar[2], sync: 'av' },
    logo: { t: ev.logo, sync: 'av' },
    difference: { t: ev.difference },
    s01: { t: SC.s01[0] + 1 }, s02: { t: SC.s02[0] + 2 }, s03: { t: SC.s03[0] + 1.5 }, s04: { t: SC.s04[0] + 2.5 }, s05: { t: SC.s05[0] + 3 },
    finale: { t: ev.finale },
    endcard: { t: ev.endcard },
    transform: { t: ev.transform, sync: 'av' },
    url: { t: ev.url },
  };

  // subtitles straight from the voiceover lines (srt / soft subtitle track)
  const subtitles = vo.filter((l) => l.text).map((l) => ({ t: l.t, end: l.end, text: l.text }));

  const SCORE = { FPS, FORMAT, W, H, SAFE, STYLE, DURATION, C, vo, V, wordT, S, SC, AVATARS, clock, T, BEAT, BAR, B, barOf, ev, chords, chordAt, markers, subtitles, m };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
