# Music bed + SFX (whooshes at cuts, soft pops at highlights), ducked under the voice-over, mixed with the VO.
import sys, numpy as np, soundfile as sf, subprocess
from scipy.signal import butter, sosfilt, fftconvolve
sys.path.insert(0, ".")
from cues import cue, VO
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
STYLE = sys.argv[3] if len(sys.argv) > 3 else "ambient"
if STYLE == "corporate":
    ref = np.sqrt(np.mean(music ** 2)); music = corporate(); music *= ref / np.sqrt(np.mean(music ** 2))
music *= np.clip(t / 1.2, 0, 1) * np.clip((T - t) / 3.0, 0, 1)
if STYLE == "corporate" and len(sys.argv) > 4: sf.write(sys.argv[4], music / np.abs(music).max() * .8, SR, subtype="PCM_24")   # music-only file
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
