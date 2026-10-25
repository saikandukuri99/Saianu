// THE SOUNDTRACK: renders music, SFX and the voiceover from score.js into out/music.wav.
//   node song.js            (STEMS=1 also writes out/stem-*.wav, LUFS=-14 masters to a loudness target)
// Arc: ambient pad + sub pulse  ->  electronic beat on the pillars  ->  uplifting synth lead for the academy
//      ->  strings, timpani and brass swell to "Transform", then one clean F chord rings out.
const path = require('path');
const { SR, Bus, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { T, BEAT, BAR, B, DURATION, m, ev, S, chords, vo } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), bass = bus(), pad = bus(), keys = bus(), lead = bus(), orch = bus(), fx = bus(), voice = bus();
const verb = bus(), dly = bus(), hall = bus();
const inSec = (t, name) => t >= S[name][0] && t < S[name][1];

// ---------- voiceover ----------
// narration lines, and the three pillar presenters in their own voices (loudness-matched by media/prep.sh)
for (const l of vo) {
  const file = l.avatar ? path.join(__dirname, 'media', `avatar_${l.avatar.name}.wav`) : path.join(__dirname, 'vo', l.id + '.wav');
  const b = MIX.loadAudio(file, { at: l.t, length: DURATION });
  if (l.avatar) b.applyGain((t) => (t < l.end + 0.05 ? 1 : 0)); // the governance clip ends on black: stop with it
  b.mixInto(voice, l.avatar ? 0.68 : 1);
}
// "That's where we can make a difference" lands in a held breath: no drums from here to the logo
const HOLD = [ev.difference - 0.15, ev.logo];

// ---------- pads: every chord, opening up section by section ----------
for (const c of chords) {
  const opts = c.sec === 'intro' ? { cutoff: 850, attack: 1.2, release: 1.8 }
    : c.sec === 'pillars' ? { cutoff: 1500, attack: 0.25, release: 0.8 }
    : c.sec === 'academy' ? { cutoff: 2600, attack: 0.08, release: 0.6 }
    : c.sec === 'finale' ? { cutoff: 2000, attack: 0.4, release: 0.9 }
    : { cutoff: 2400, attack: 0.03, release: 2.2 };
  const t0 = Math.max(0, c.t0), dur = c.t1 - t0;
  if (dur <= 0.05) continue;
  const g = c.sec === 'intro' ? 0.11 : c.sec === 'end' ? 0.1 : 0.075;
  for (const n of c.notes) { const { L, R } = I.padNote(n, dur, opts); pad.addStereo(L, R, t0, g); if (c.sec === 'intro') hall.addStereo(L, R, t0, 0.05); }
}

// ---------- intro: the sub-bass pulse (a slow heartbeat on every half bar) + glints ----------
for (let t = T(B.first); t < ev.beatIn - 0.01; t += BAR / 2) {
  if (t < 0.3) continue;
  const c = sc.chordAt(t);
  bass.addMono(I.bass(c.bass + 12, BAR / 2 * 0.7, { bright: 0.05, sub: 1.2 }), t, 0.32 * Math.min(1, t / 4));
}
const glint = [m('A5'), m('E6'), m('D6'), m('F6'), m('C6'), m('A5'), m('E6'), m('D6')];
for (let i = 0; i < 8; i++) {
  const t = 3.2 + i * BAR * 0.75;
  if (t > ev.beatIn - 1.2) break;
  const x = I.musicBox(glint[i] - 12, { decay: 1.2 });
  keys.addMono(x, t, 0.05, i % 2 ? 0.4 : -0.4); hall.addMono(x, t, 0.09); dly.addMono(x, t, 0.05);
}

// ---------- the beat (pillars) and the four-on-the-floor (academy) ----------
const K = I.kick({ punch: 1.1 }), CL = I.clap(), SN = I.snare({ snap: 1.2 }), HC = [I.hat(false, 11), I.hat(false, 12)], HO = I.hat(true, 14);
const SH = [I.shaker(1, 15), I.shaker(0.6, 16)];
const kicks = [];
clock16(B.beat, B.finale, (t, b, s) => {
  const acad = b >= B.academy;
  if (acad ? s % 4 === 0 : (s === 0 || s === 8 || s === 11)) { drums.addMono(K, t, 0.9); kicks.push(t); }
  if (s === 4 || s === 12) { drums.addMono(CL, t, 0.45, 0.05); verb.addMono(CL, t, 0.18); if (acad) drums.addMono(SN, t, 0.18); }
  if (s % 4 === 2) drums.addMono(acad ? HO : HC[0], t, acad ? 0.1 : 0.16, 0.3);
  else if (s % 2 === 1) drums.addMono(SH[s % 4 === 1 ? 0 : 1], t, 0.09, -0.35);
});
function clock16(b0, b1, fn) { sc.clock.eachStep(b0, b1, 16, (t, b, s) => { if (t >= HOLD[0] && t < HOLD[1]) return; fn(t, b, s); }); }

// ---------- bassline: rhythmic 8ths on the pillars, driving 8ths with octave hops for the academy ----------
sc.clock.eachStep(B.beat, B.finale, 8, (t, b, s) => {
  if (t >= HOLD[0] && t < HOLD[1]) return;
  const c = sc.chordAt(t); if (!c) return;
  const R = c.bass + 12;
  if (b >= B.academy) bass.addMono(I.bass(s % 2 ? R + 12 : R, BEAT / 2 * 0.8, { sub: 0.8, bright: 0.7 }), t, 0.42);
  else if (s !== 3 && s !== 7) bass.addMono(I.bass(s === 6 ? R + 7 : R, BEAT / 2 * 0.75, { bright: 0.55 }), t, 0.42);
});

// ---------- pillars: a pulsing pluck arp ----------
sc.clock.eachStep(B.beat, B.academy, 16, (t, b, s) => {
  if (s % 2 || t >= HOLD[0]) return;
  const c = sc.chordAt(t); if (!c) return;
  const n = c.notes[[0, 2, 1, 3, 2, 1, 3, 2][(s / 2) % 8]] + 12;
  const x = I.pluck(n, { decay: 0.12, cutoff: 2200 + 1400 * ((b - B.beat) / (B.academy - B.beat)) });
  keys.addMono(x, t, 0.07, s % 4 ? 0.35 : -0.35); dly.addMono(x, t, 0.04);
});

// ---------- academy: the uplifting synth lead + bright arps ----------
const HOOK = [ // one 4-bar phrase on F C Dm Bb: [bar, beat, midi, beats]
  [0, 0, 'C5', 1.5], [0, 1.5, 'A4', 0.5], [0, 2, 'C5', 1], [0, 3, 'F5', 1],
  [1, 0, 'E5', 1.5], [1, 1.5, 'D5', 0.5], [1, 2, 'C5', 2],
  [2, 0, 'D5', 1.5], [2, 1.5, 'E5', 0.5], [2, 2, 'F5', 1], [2, 3, 'A5', 1],
  [3, 0, 'G5', 2.5], [3, 2.5, 'F5', 0.5], [3, 3, 'D5', 1],
];
for (let rep = 0; rep < Math.ceil((B.finale - B.academy) / 4); rep++) {
  for (const [bb, beat, note, beats] of HOOK) {
    const t = T(B.academy + rep * 4 + bb, beat);
    if (t >= S.academy[1] - 0.2) continue;
    if (t < ev.platform - 0.05) continue; // the lead enters once the logo has spoken
    const s = I.supersaw(m(note), beats * BEAT * 0.9, { detune: 18, cutoff: 4200, attack: 0.02, release: 0.25, seed: 3 });
    lead.addStereo(s.L, s.R, t, 0.11); verb.addStereo(s.L, s.R, t, 0.05); dly.addStereo(s.L, s.R, t, 0.04);
  }
}
sc.clock.eachStep(B.academy, B.finale, 16, (t, b, s) => {
  if (t < ev.logo) return;
  const c = sc.chordAt(t); if (!c) return;
  const n = c.notes[[0, 1, 2, 3, 2, 1][s % 6]] + 24;
  const x = I.pluck(n, { decay: 0.09, cutoff: 4200 });
  keys.addMono(x, t, 0.035, (s % 2 ? 0.5 : -0.5)); dly.addMono(x, t, 0.025);
});

// ---------- finale: strings + timpani + brass swelling to "Transform" ----------
for (const c of chords.filter((c) => c.sec === 'finale')) {
  const k = (c.t0 - S.finale[0]) / (ev.transform - S.finale[0]); // 0 -> 1 across the finale
  for (const n of [...c.notes, c.notes[0] + 12]) {
    const st = I.strings(n + 12, c.t1 - c.t0 + 0.05, { attack: 0.35, release: 0.6, bright: 0.6 + 0.6 * k, seed: n });
    orch.addStereo(st.L, st.R, c.t0, 0.06 + 0.07 * k); hall.addStereo(st.L, st.R, c.t0, 0.05);
  }
  const lo = I.strings(c.bass + 12, c.t1 - c.t0, { attack: 0.3, bright: 0.5, seed: 77 });
  orch.addStereo(lo.L, lo.R, c.t0, 0.09 + 0.06 * k);
}
// driving half-time pulse: kick + tom on 1 and 3, timpani rolls growing into the hit
sc.clock.eachStep(B.finale, sc.barOf(ev.transform) + 1, 8, (t, b, s) => {
  if (t >= ev.learn - 0.25) return;
  const k = (t - S.finale[0]) / (ev.learn - S.finale[0]);
  if (s === 0 || s === 4) { drums.addMono(K, t, 0.7 + 0.25 * k); kicks.push(t); drums.addMono(I.tom(90, 0.4), t, 0.2 + 0.2 * k); }
  if (s === 4) { drums.addMono(SN, t, 0.12 + 0.12 * k); hall.addMono(SN, t, 0.06); }
  if (s % 2 === 1) drums.addMono(HC[1], t, 0.06 + 0.06 * k, 0.3);
});
for (let t = ev.future; t < ev.endcard - 0.1; t += BEAT / 4) {
  const k = (t - ev.future) / (ev.endcard - ev.future);
  const c = sc.chordAt(t);
  orch.addMono(I.timpani(c.bass + 12, { decay: 0.5, seed: Math.round(t * 50) }), t, 0.04 + 0.12 * k * k);
}
// brass pad over the welcome
for (const c of chords.filter((c) => c.t0 >= ev.endcard - BAR && c.t0 < ev.transform && c.sec === 'finale')) {
  for (const n of c.notes) { const b = I.brassNote(n, c.t1 - c.t0, { bright: 0.6, seed: n }); orch.addStereo(b.L, b.R, c.t0, 0.05); hall.addStereo(b.L, b.R, c.t0, 0.03); }
}

// "Learn." and "Innovate.": two big taiko/timpani hits; then a breath; "Transform." is the climax
for (const [t, note, g] of [[ev.learn, 'D2', 0.6], [ev.innovate, 'A2', 0.7]]) {
  orch.addMono(I.timpani(m(note), { decay: 1.0, seed: 4 }), t, g);
  drums.addMono(I.tom(70, 0.5), t, 0.45); hall.addMono(I.tom(70, 0.5), t, 0.2);
  const st = I.brassNote(m(note) + 24, 0.5, { bright: 0.9, stab: true, seed: 8 }); orch.addStereo(st.L, st.R, t, 0.12);
}
fx.addMono(I.noiseSweep(ev.transform - ev.innovate - 0.08, 300, 7000, { q: 0.9, shape: (x) => x * x * x, pink: true }), ev.innovate + 0.0, 0.18);
// the hit: deep boom + crash + timpani + brass + strings on F, ringing out to the end
fx.addMono(I.subBoom(3.2, 70, 26), ev.transform, 0.95);
drums.addMono(K, ev.transform, 1.0); drums.addMono(I.crash(18), ev.transform, 0.42, -0.2); drums.addMono(I.crash(21), ev.transform, 0.3, 0.25);
orch.addMono(I.timpani(m('F2'), { decay: 1.6, seed: 9 }), ev.transform, 0.8);
const ring = DURATION - ev.transform;
for (const n of ['F3', 'C4', 'A4', 'F4', 'C5']) {
  const b = I.brassNote(m(n), 1.6, { bright: 0.9, seed: m(n) }); orch.addStereo(b.L, b.R, ev.transform, 0.1); hall.addStereo(b.L, b.R, ev.transform, 0.08);
  const st = I.strings(m(n) + 12, ring, { attack: 0.05, release: 1.0, bright: 1.1, seed: m(n) + 3 }); orch.addStereo(st.L, st.R, ev.transform, 0.09); hall.addStereo(st.L, st.R, ev.transform, 0.07);
}

// ---------- SFX (each tied to a score event) ----------
// 0:02 soft digital frequency sweep as the title resolves
{
  const sw = I.noiseSweep(1.6, 250, 7000, { q: 5, shape: (x) => Math.sin(Math.PI * x), seed: 3 });
  fx.addMono(sw, ev.sweep - 0.5, 0.22, -0.3); hall.addMono(sw, ev.sweep - 0.5, 0.1);
  const chirp = new Float32Array(Math.round(1.4 * SR));
  let ph = 0;
  for (let i = 0; i < chirp.length; i++) { const t = i / SR; ph += (400 * Math.pow(12, t / 1.4)) / SR; chirp[i] = Math.sin(2 * Math.PI * ph) * Math.sin(Math.PI * t / 1.4) * 0.25; }
  fx.addMono(chirp, ev.sweep - 0.4, 0.12, 0.3); dly.addMono(chirp, ev.sweep - 0.4, 0.08);
}
// riser into the beat
fx.addMono(I.noiseSweep(2.4, 200, 6000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.beatIn - 2.4, 0.22);
fx.addMono(I.subBoom(1.6, 60, 30), ev.beatIn, 0.45);
// three metallic chime impacts, one per pillar, rising
ev.pillar.forEach((t0, i) => {
  const t = t0 - 0.3; // just ahead of the presenter's first word
  const f = [587.33, 698.46, 880][i];
  const a = I.bell(f, 0.9, 3.2, 3.5), b = I.bell(f * 2.01, 0.5, 2.0, 1.41), c = I.bell(f * 0.5, 1.1, 1.2, 2.76);
  fx.addMono(a, t, 0.22, -0.3 + 0.3 * i); fx.addMono(b, t, 0.09); fx.addMono(c, t, 0.12);
  hall.addMono(a, t, 0.18); dly.addMono(b, t, 0.06);
  fx.addMono(I.thud(70, 0.12), t, 0.5);
  fx.addMono(I.noiseSweep(0.35, 5000, 900, { q: 1.5, pink: true }), t, 0.06);
});
// the logo: whoosh in, a clean impact on "Solix"
fx.addMono(I.noiseSweep(0.9, 400, 6000, { q: 0.8, shape: (x) => x * x, pink: true }), ev.logo - 0.9, 0.22);
fx.addMono(I.subBoom(2.0, 64, 28), ev.logo, 0.7);
drums.addMono(I.crash(6), ev.logo, 0.3, 0.1);
{ const sh = I.bell(1318.5, 0.8, 1.6, 2.0); fx.addMono(sh, ev.logo, 0.12); hall.addMono(sh, ev.logo, 0.2); }
// UI whooshes as the course cards and lab windows glide in
const whooshes = ev.whooshes;
whooshes.forEach((t, i) => {
  fx.addMono(I.noiseSweep(0.5, 900, 5200, { q: 1.4, shape: (x) => Math.sin(Math.PI * x) ** 2, seed: 30 + i, pink: true }), t - 0.22, 0.13, i % 2 ? 0.45 : -0.45);
  fx.addMono(I.pop(1.6 + 0.1 * i), t + 0.05, 0.05);
});
// the statement: a soft low impact and a high bell under "make a difference"
fx.addMono(I.subBoom(1.8, 58, 30), ev.difference, 0.4);
{ const b = I.bell(1046.5, 1.2, 1.4, 2.0); fx.addMono(b, ev.difference + 0.05, 0.08); hall.addMono(b, ev.difference + 0.05, 0.16); }
// glass shimmer tone on the web address
[m('F6'), m('A6'), m('C7'), m('G7'), m('A7')].forEach((n, i) => {
  const t = ev.url + i * 0.055;
  const x = I.bell(440 * Math.pow(2, (n - 69) / 12), 0.9, 1.1, 3.01);
  fx.addMono(x, t, 0.05, -0.5 + i * 0.25); hall.addMono(x, t, 0.1); dly.addMono(x, t, 0.04);
});

// ---------- mix ----------
MIX.sidechain([pad, bass], kicks.filter((t) => t >= ev.beatIn && t < ev.learn), { depth: 0.45, release: 0.18 });
const music = [drums, bass, pad, keys, lead, orch];
const stems = {
  voice, drums, bass, pad, keys, lead, orch, fx,
  verb: reverb(verb, { room: 0.78, damp: 0.35 }),
  hall: reverb(hall, { room: 0.93, damp: 0.25, predelay: 0.03 }),
  dly: pingpong(dly, BEAT * 0.75, 0.35, 3800),
};
// sit the music further back while the presenters speak
for (const b of [...music, stems.verb, stems.hall, stems.dly]) b.applyGain((t) => (sc.AVATARS.some((a) => t > a.t - 0.4 && t < a.end + 0.4) ? 0.6 : 1));
MIX.duck([...music, stems.verb, stems.hall, stems.dly], voice, { depth: 0.42, attack: 0.03, release: 0.45, threshold: 0.05 });
const GAIN = { voice: 2.2, drums: 0.3, bass: 0.5, pad: 1.6, keys: 1.1, lead: 3.2, orch: 0.9, fx: 0.6, verb: 1, hall: 0.9, dly: 0.9 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 24);
MIX.fadeOut(mix, DURATION - 1.4, DURATION);
const M = MIX.master(mix, parseFloat(process.env.DRIVE || '0.8'), undefined, { lufs: process.env.LUFS ? parseFloat(process.env.LUFS) : -14 });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s${M.lufs !== undefined ? `, ${M.lufs.toFixed(1)} LUFS at drive ${M.drive.toFixed(2)}` : ''})`);
