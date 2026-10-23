# Music bed + SFX (whooshes at cuts, soft pops at highlights), ducked under the voice-over, mixed with the VO.
import sys, numpy as np, soundfile as sf, subprocess
from scipy.signal import butter, sosfilt, fftconvolve
sys.path.insert(0, ".")
from cues import cue, VO, OFF
from scenes import SC
SR = 48000; T = SC['J'][1]; N = int(T * SR); rs = np.random.RandomState(3)
t = np.arange(N) / SR
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def env(x, a, b): return np.interp(t, x, [0] * len(x)) if False else None
# ---- pad: slow chord loop (Dm9 - Bbmaj7 - Fmaj7 - Cadd9), 4 bars of 4 s ... fades in/out
chords = [[146.8, 220.0, 261.6, 329.6], [116.5, 174.6, 233.1, 293.7], [174.6, 220.0, 261.6, 329.6], [130.8, 196.0, 261.6, 329.6]]
pad = np.zeros(N)
for k in range(int(T // 4) + 1):
    a, b = int(k * 4 * SR), min(N, int((k + 1) * 4 * SR + 1.2 * SR)); seg = np.zeros(b - a); tt = np.arange(b - a) / SR
    for f in chords[k % 4]:
        for d in (-.6, 0, .6):
            seg += np.sin(2 * np.pi * (f + d * .25) * tt + rs.rand() * 6) * (.5 if d else 1)
    g = np.clip(tt / 1.2, 0, 1) * np.clip((b - a) / SR - tt, 0, 1.2) / 1.2
    pad[a:b] += seg * np.minimum(1, tt / 1.2) * np.minimum(1, (tt[-1] - tt) / 1.2 + 0) * .05
pad = lp(pad, 1800)
# ---- pulse / arpeggio (16ths at 112 bpm, soft pluck)
arp = np.zeros(N); step = 60 / 112 / 2; notes = [[293.7, 349.2, 440.0, 523.3], [233.1, 293.7, 349.2, 440.0], [349.2, 440.0, 523.3, 659.3], [261.6, 329.6, 392.0, 523.3]]
for i in range(int(T / step)):
    ch = notes[int(i * step // 4) % 4]; f = ch[[0, 1, 2, 3, 2, 1, 3, 2][i % 8]]; a = int(i * step * SR)
    L = int(.45 * SR); tt = np.arange(L) / SR; pl = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7) + .3 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 11)
    arp[a:a + L] += pl[:max(0, min(L, N - a))] * (.03 if i % 2 == 0 else .018)
d = np.zeros(N); dl = int(.375 * SR); d[dl:] = arp[:-dl]; arp = arp + .5 * d      # echo
sub = np.zeros(N)                                                                    # soft sub on chord roots
for k in range(int(T // 4) + 1):
    f = [73.4, 58.3, 87.3, 65.4][k % 4]; a = int(k * 4 * SR); L = min(N - a, int(4 * SR)); tt = np.arange(L) / SR
    if L > 0: sub[a:a + L] += np.sin(2 * np.pi * f * tt) * np.minimum(1, tt / .3) * np.minimum(1, (4 - tt) / .5) * .06
music = pad + arp + sub

# ---- alternative bed: warm "corporate" track (100 bpm, C - G - Am - F, piano plucks + soft strings + light drums)
def corporate():
    """smooth corporate bed matched to the reference (Solix_AR_Update): C major, 120 bpm, warm pad, soft pulse, gentle piano, chime tail"""
    r = np.random.RandomState(9); out = np.zeros(N); beat = .5; bar = 4 * beat
    CH = [([130.8, 164.8, 196.0, 261.6, 329.6], 65.4), ([98.0, 146.8, 196.0, 246.9, 293.7], 49.0), ([110.0, 164.8, 220.0, 261.6, 329.6], 55.0), ([87.3, 130.8, 174.6, 220.0, 261.6], 43.7)]
    def put(x, at, g=1.0):
        a = int(at * SR)
        if 0 <= a < N: x = x[:N - a]; out[a:a + len(x)] += x * g
    nb = int(T / bar) + 1; END = T - 3.4                               # last chord = C major, held under the chime
    for b in range(nb):
        notes, root = CH[b % 4]
        if b * bar >= END - bar: notes, root = CH[0]
        L = int((bar + 1.2) * SR); tt = np.arange(L) / SR; seg = np.zeros(L)
        for f in notes:
            for d in (-.0035, 0, .0035): seg += np.sin(2 * np.pi * f * (1 + d) * tt + r.rand() * 6.28 + .15 * np.sin(2 * np.pi * .3 * tt)) * .5
        env_ = np.minimum(1, tt / .9) * np.minimum(1, (tt[-1] - tt) / 1.1)
        put(lp(seg, 1800) * env_ * .075, b * bar)                         # warm pad
        bt = np.arange(int(beat * 3 * SR)) / SR
        put(np.sin(2 * np.pi * root * 2 * bt) * np.minimum(1, bt / .05) * np.exp(-bt * 1.6), b * bar, .075 if b * bar > 3 else 0)   # soft bass on the bar
    pulse_from = 6.0
    for i in range(int((T - 3.4) / beat)):                                  # soft pulse on every beat from the first phrase
        at = i * beat
        if at < pulse_from: continue
        g = min(1, (at - pulse_from) / 4.0)
        tt = np.arange(int(.28 * SR)) / SR; put(np.sin(2 * np.pi * (50 + 55 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 10), at, .07 * g)
        if i % 2 == 1:
            tt = np.arange(int(.05 * SR)) / SR; put(sosfilt(butter(2, 7500, "high", fs=SR, output="sos"), r.randn(len(tt))) * np.exp(-tt * 70), at + .25, .008 * g)
    step = beat / 2
    for i in range(int((T - 3.4) / step)):                                  # gentle piano figure
        at = i * step
        if at < pulse_from - 1: continue
        b = int(at // bar); notes = CH[b % 4][0]; f = notes[[0, 2, 3, 4, 3, 2, 4, 3][i % 8]] * 2
        L = int(1.0 * SR); tt = np.arange(L) / SR
        pl = (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 5) + .15 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt * 9)) * np.exp(-tt * 3.6)
        put(pl, at, .034 * (1.0 if i % 2 == 0 else .7) * min(1, (at - pulse_from + 1) / 5.0))
    tt = np.arange(int(3.2 * SR)) / SR                                       # closing chime: C major shimmer
    for f, g in ((523.3, 1.0), (659.3, .8), (784.0, .7), (1046.5, .5)): put(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.3) * np.minimum(1, tt / .02), END, .045 * g)
    return out
def upbeat():
    """upbeat corporate bed: 124 bpm, C major (C - G - Am - F), four-on-the-floor kick, claps, off-beat hats, bass, chord stabs, bright plucked arpeggio"""
    r = np.random.RandomState(13); out = np.zeros(N); bpm = 124.0; beat = 60 / bpm; bar = 4 * beat; END = T - 4.3; G0 = OFF   # full groove starts with the story
    TRI = [[261.6, 329.6, 392.0], [246.9, 293.7, 392.0], [220.0, 261.6, 329.6], [220.0, 261.6, 349.2]]; ROOT = [65.4, 98.0, 110.0, 87.3]
    def put(x, at, g=1.0):
        a_ = int(at * SR)
        if 0 <= a_ < N: x = x[:N - a_]; out[a_:a_ + len(x)] += x * g
    def saw(f, L, n=7): tt = np.arange(L) / SR; return sum(np.sin(2 * np.pi * f * k_ * tt) / k_ for k_ in range(1, n + 1))
    nb = int(T / bar) + 1
    for b in range(nb):
        t_b = b * bar
        if t_b >= END: break
        ch = 0 if t_b >= END - bar else b % 4
        L = int((bar + .8) * SR); tt = np.arange(L) / SR; pad = np.zeros(L)                      # pad
        for f in TRI[ch] + [TRI[ch][0] / 2]:
            for d in (-.003, 0, .003): pad += np.sin(2 * np.pi * f * (1 + d) * tt + r.rand() * 6.28) * .5
        put(lp(pad, 2200) * np.minimum(1, tt / .5) * np.minimum(1, (tt[-1] - tt) / .7) * .05, t_b)
        for bt_, gB in ((0, 1), (.75, .8), (1.5, .9), (2.5, 1), (3.0, .8), (3.5, .9)):               # bass
            at = t_b + bt_ * beat
            if at < G0 - bar or at >= END: continue
            L2 = int(.3 * SR); put(lp(saw(ROOT[ch] * (2 if bt_ in (.75, 3.0) else 1), L2, 8), 380) * np.exp(-np.arange(L2) / SR * 8) * np.minimum(1, np.arange(L2) / SR / .005), at, .16 * gB * (1 if at >= G0 else .0))
        for bt_ in (.5, 1.5, 2.5, 3.5):                                                           # off-beat chord stabs
            at = t_b + bt_ * beat
            if at < G0 or at >= END: continue
            L2 = int(.22 * SR); seg = sum(saw(f, L2, 6) for f in TRI[ch]); put(lp(seg, 3200) * np.exp(-np.arange(L2) / SR * 14), at, .028)
    for i in range(int(END / (beat / 4))):                                                       # 16th grid: arp, hats
        at = i * beat / 4; b = int(at // bar); ch = 0 if at >= END - bar else b % 4; k16 = i % 16
        if at >= G0 - 2 * bar:                                                                    # bright plucked arpeggio (also lightly through the title)
            f = TRI[ch][[0, 1, 2, 1][i % 4]] * 2; L2 = int(.3 * SR); tt = np.arange(L2) / SR
            pl = (np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt * 9)
            g = .026 * (1.35 if i % 4 == 0 else 1.0) * (1 if at >= G0 else .6); put(pl, at, g); put(pl, at + beat * .75, g * .35)
        if k16 % 2 == 0 and k16 % 4 != 0 or (at < G0 and k16 % 4 == 2):                            # off-beat hats
            tt = np.arange(int(.06 * SR)) / SR; put(sosfilt(butter(2, 7000, "high", fs=SR, output="sos"), r.randn(len(tt))) * np.exp(-tt * 55), at, .028)
        elif k16 % 2 == 1 and at >= G0:
            tt = np.arange(int(.03 * SR)) / SR; put(sosfilt(butter(2, 8000, "high", fs=SR, output="sos"), r.randn(len(tt))) * np.exp(-tt * 90), at, .009)
        if at >= G0 and k16 % 4 == 0:                                                              # kick on every beat
            tt = np.arange(int(.3 * SR)) / SR; put(np.sin(2 * np.pi * (46 + 85 * np.exp(-tt * 32)) * tt) * np.exp(-tt * 9), at, .16)
        if at >= G0 and k16 in (4, 12):                                                            # clap on 2 and 4
            tt = np.arange(int(.16 * SR)) / SR; put(bp(r.randn(len(tt)), 1200, 5500) * np.exp(-tt * 26), at, .06)
    rs_ = np.arange(int(1.9 * SR)) / SR; put(bp(r.randn(len(rs_)), 1500, 9000, 2) * (rs_ / rs_[-1]) ** 2.2, G0 - 1.9, .06)   # riser into the story
    tt = np.arange(int(3.4 * SR)) / SR                                                             # final hit: C major chord + crash
    for f, g in ((130.8, 1.0), (261.6, 1.0), (329.6, .8), (392.0, .8), (523.3, .6), (1046.5, .35)): put(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.1) * np.minimum(1, tt / .01), END, .06 * g)
    put(sosfilt(butter(2, 3500, "high", fs=SR, output="sos"), r.randn(len(tt))) * np.exp(-tt * 1.6), END, .05)
    return out

STYLE = sys.argv[3] if len(sys.argv) > 3 else "ambient"
if STYLE in ("corporate", "upbeat"):
    ref = np.sqrt(np.mean(music ** 2)); music = (corporate() if STYLE == "corporate" else upbeat()); music *= ref / np.sqrt(np.mean(music ** 2)) * (1.15 if STYLE == "upbeat" else 1.0)
music *= np.clip(t / 1.2, 0, 1) * np.clip((T - t) / 3.0, 0, 1)
if STYLE in ("corporate", "upbeat") and len(sys.argv) > 4: sf.write(sys.argv[4], music / np.abs(music).max() * .8, SR, subtype="PCM_24")   # music-only file
sfx = np.zeros(N)                    # sound effects removed: music bed + voice-over only
# ---- duck music + sfx under the voice, then mix
voL, _ = sf.read(sys.argv[1]); vo = voL[:, 0] if voL.ndim > 1 else voL; vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
e = lp(np.abs(vo), 6, 2); e = np.clip(e / (np.percentile(e, 95) + 1e-9), 0, 1)
duck = 1 - .62 * e
music_d = music * duck * 1.0; sfx_d = sfx * (1 - .35 * e)
def wide(x): d = int(.013 * SR); y = np.zeros_like(x); y[d:] = x[:-d]; return np.stack([x + .35 * y, y + .35 * x], 1)
mix = np.stack([vo, vo], 1) * 1.0 + wide(music_d) * 0.55 + np.stack([sfx_d, sfx_d], 1) * 0.6
mix = np.tanh(mix * .9) / .9
sf.write(sys.argv[2], mix, SR, subtype="PCM_24")
print("mix peak", np.abs(mix).max())
