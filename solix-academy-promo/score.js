// THE SCORE: Solix Academy executive promo (75 s).
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

  // ---------- voiceover placement (gap = silence BEFORE the line) ----------
  const LEAD = 0.45;
  const GAP = { l02: 0.3, l03: 0.35, l04: 0.5, l05: 0.3, l06: 0.4, l07: 0.4, l08: 0.5, l09: 0.25, l10: 0.25, l11: 0.2, l12: 0.18,
    l13: 0.5, l14: 0.3, l15: 0.35, l16: 0.45, l17: 0.3, l18: 0.32, l19: 0.45 };
  const vo = [];
  let cur = LEAD;
  for (const L of VO_LINES) {
    cur += GAP[L.id] || 0;
    vo.push({ ...L, t: +cur.toFixed(3), end: +(cur + L.dur).toFixed(3), words: [] });
    cur += L.dur;
  }
  const V = Object.fromEntries(vo.map((l) => [l.id, l]));
  // estimated word times (proportional to letters, with room for punctuation pauses)
  for (const l of vo) {
    const ws = l.text.split(/\s+/);
    const wt = ws.map((w) => w.replace(/[^A-Za-z0-9]/g, '').length + 2 + (/[,:]$/.test(w) ? 3 : /[.?]$/.test(w) ? 5 : 0));
    const sum = wt.reduce((a, b) => a + b, 0);
    let acc = 0;
    const span = l.dur - 0.12;
    l.words = ws.map((w, i) => { const t0 = l.t + 0.04 + (acc / sum) * span; acc += wt[i]; return { w, t: +t0.toFixed(3), end: +(l.t + 0.04 + (acc / sum) * span).toFixed(3) }; });
  }
  const wordT = (id, word, n = 0) => { const hits = V[id].words.filter((x) => x.w.toLowerCase().replace(/[^a-z0-9-]/g, '').startsWith(word.toLowerCase())); return (hits[n] || hits[0]).t; };

  const DURATION = +(V.l19.end + 1.2).toFixed(2);

  // ---------- sections ----------
  const S = {
    intro: [0, V.l04.t - 0.3],
    pillars: [V.l04.t - 0.3, V.l08.t - 0.35],
    academy: [V.l08.t - 0.35, V.l13.t - 0.35],
    finale: [V.l13.t - 0.35, DURATION],
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
    sweep: 2.0, // soft digital frequency sweep + title
    title: 2.0,
    streams: V.l02.t - 0.4, // city dissolves into data streams over a boardroom
    boardroom: V.l02.t + 2.2,
    question: V.l03.t,
    beatIn,
    pillar: [wordT('l05', 'first'), wordT('l06', 'second'), wordT('l07', 'and')],
    pillarsTag: 0, // set below: the foundation appears on "Building the trusted foundation"
    logo: V.l08.t + wordT('l08', 'solix') - V.l08.t - 0.05, // the bolt lands on "Solix"
    academyWord: wordT('l08', 'academy'),
    platform: V.l09.t,
    experts: V.l10.t,
    labs: [V.l11.t + 0.1, V.l11.t + 2.05, V.l11.t + 4.0],
    paths: V.l12.t,
    finale: S.finale[0],
    future: V.l14.t,
    endcard: V.l15.t - 0.15,
    learn: V.l16.t,
    innovate: V.l17.t,
    transform: V.l18.t,
    url: V.l19.t - 0.05,
  };
  ev.logo = wordT('l08', 'solix');
  ev.pillarsTag = wordT('l07', 'trusted');

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
    labs: { t: ev.labs[0] },
    paths: { t: ev.paths },
    finale: { t: ev.finale },
    endcard: { t: ev.endcard },
    transform: { t: ev.transform, sync: 'av' },
    url: { t: ev.url },
  };

  // subtitles straight from the voiceover lines (srt / soft subtitle track)
  const subtitles = vo.map((l) => ({ t: l.t, end: l.end, text: l.text }));

  const SCORE = { FPS, FORMAT, W, H, SAFE, STYLE, DURATION, C, vo, V, wordT, S, clock, T, BEAT, BAR, B, barOf, ev, chords, chordAt, markers, subtitles, m };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
