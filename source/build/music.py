# Procedural energetic corporate-event track (original, royalty-free).
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

B = os.path.dirname(os.path.abspath(__file__))
SR = 44100
tl = json.load(open(f"{B}/timeline.json"))
T = tl["total"]
N = int(T * SR) + SR
BPM = 124.0
beat = 60 / BPM
rng = np.random.default_rng(7)
bounds = [s["start"] for s in tl["segs"][1:]]
final = tl["segs"][7]["start"]


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)


def add(buf, sig, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def env(n, a, d):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / (d * SR))
    return e


def saw(f, n, detune=(0,), phase_rand=True):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in detune:
        ff = f * 2 ** (d / 1200)
        ph = rng.random() if phase_rand else 0
        out += 2 * ((t * ff + ph) % 1) - 1
    return out / len(detune)


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


# intensity curve per time (0..1)
def intensity(t):
    if t < 3.0:
        return 0.35
    if t < bounds[0]:
        return 0.75
    if bounds[4] <= t < bounds[4] + 4:
        return 0.7  # small lift into industries
    if t >= final:
        return 1.0
    return 0.9


drums = np.zeros(N); bass = np.zeros(N); pad = np.zeros(N); arp = np.zeros(N); fx = np.zeros(N)

# --- one-shots
kn = int(0.45 * SR); kt = np.arange(kn) / SR
kfreq = 48 + 110 * np.exp(-kt * 28)
kick = np.sin(2 * np.pi * np.cumsum(kfreq) / SR) * np.exp(-kt * 7.5)
kick += 0.25 * np.exp(-kt * 300) * rng.standard_normal(kn) * 0.3
kick = np.tanh(kick * 1.6)
cn = int(0.3 * SR)
clap = bp(rng.standard_normal(cn), 900, 4000) * env(cn, 0.001, 0.07)
hn = int(0.06 * SR)
hat = hp(rng.standard_normal(hn), 7000) * env(hn, 0.0005, 0.015)
on = int(0.22 * SR)
ohat = hp(rng.standard_normal(on), 6500) * env(on, 0.001, 0.07)

# chord progression (Am F C G) -> roots midi
prog = [(57, [57, 60, 64, 69]), (53, [53, 57, 60, 65]), (48, [52, 55, 60, 64]), (55, [55, 59, 62, 67])]
bar = beat * 4

t = 0.0; step = 0
sidechain = np.ones(N)
while t < T + 1:
    I = intensity(t)
    b_in_bar = step % 4
    bar_idx = int(step // 4)
    root, chord = prog[(bar_idx // 2) % 4]
    full = t >= 3.0
    fill_zone = any(0 < bd - t <= bar for bd in bounds)
    # kick
    if full and not (t >= final + bar * 4):
        add(drums, kick * 0.95, t)
        i = int(t * SR); n = int(0.28 * SR)
        if i < N:
            m = min(n, N - i)
            sidechain[i:i + m] = np.minimum(sidechain[i:i + m], 0.35 + 0.65 * (np.arange(m) / n) ** 0.7)
    elif not full and b_in_bar == 0:
        add(drums, kick * 0.6, t)
    # clap on 2 & 4
    if full and b_in_bar in (1, 3):
        add(drums, clap * 0.45, t)
    # hats
    if full:
        add(drums, ohat * 0.22 * I, t + beat / 2)
        for k in (0.25, 0.75):
            add(drums, hat * 0.16 * I, t + beat * k)
        if fill_zone:
            for k in range(4):
                add(drums, clap * 0.18 * (k + 1) / 4, t + beat * k / 4)
    # bass: offbeat 8ths + rolling 16ths
    if full:
        f = midi(root - 24)
        for k, (pos, ln) in enumerate([(0.5, 0.22), (0.75, 0.2)]):
            n = int(ln * SR)
            s = saw(f, n, (-6, 6)) * env(n, 0.003, 0.09)
            s = lp(s, 900) + 0.6 * np.sin(2 * np.pi * f * np.arange(n) / SR) * env(n, 0.003, 0.12)
            add(bass, s * 0.5 * I, t + beat * pos)
    # arp: 16th plucks over chord
    if t >= 1.5:
        for k in range(4):
            note = chord[(step * 4 + k) % 4] + 12 + (12 if (step // 8) % 2 else 0)
            n = int(0.18 * SR)
            s = saw(midi(note), n, (-8, 8)) * env(n, 0.002, 0.06)
            add(arp, lp(s, 3500) * 0.16 * (0.6 if t < 3 else I), t + beat * k / 4)
    # pad per bar
    if b_in_bar == 0:
        n = int(bar * SR) + int(0.3 * SR)
        s = np.zeros(n)
        for m in chord:
            s += saw(midi(m), n, (-12, -4, 4, 12))
        s = lp(s, 2200 if full else 1200) * env(n, 0.05, 2.5)
        add(pad, s * 0.11, t)
    t += beat; step += 1

# --- risers + impacts at section boundaries
for bd in bounds:
    rl = 2.0 if bd != final else 3.0
    n = int(rl * SR)
    noise = rng.standard_normal(n)
    sweep = np.zeros(n)
    # sweep band by blocks
    blk = 2048
    for i in range(0, n, blk):
        fc = 400 + 7000 * (i / n) ** 2
        seg = noise[i:i + blk]
        sweep[i:i + blk] = bp(seg, fc * 0.7, min(fc * 1.4, 20000))
    sweep *= np.linspace(0, 1, n) ** 2
    add(fx, sweep * 0.30, bd - rl)
    # impact boom
    n = int(2.5 * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (40 + 60 * np.exp(-tt * 12)) * tt) * np.exp(-tt * 2.2)
    boom += lp(rng.standard_normal(n), 2500) * np.exp(-tt * 6) * 0.35
    add(fx, boom * (0.55 if bd != final else 0.8), bd)

# final hit tail chord
n = int(4 * SR)
s = np.zeros(n)
for m in [45, 57, 60, 64, 69, 76]:
    s += saw(midi(m), n, (-10, 0, 10))
s = lp(s, 3000) * env(n, 0.01, 1.6)
add(fx, s * 0.12, T - 3.6)

# mix
music = drums * 1.0 + bass * sidechain + pad * sidechain * 1.0 + arp * (0.5 + 0.5 * sidechain) + fx
# simple reverb on pad/arp/fx
ir_n = int(1.8 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / (0.45 * SR)); ir /= np.sqrt((ir ** 2).sum())
wet = fftconvolve(pad + arp * 0.6 + fx * 0.4, ir)[:N] * 0.35
music = music + wet
music = hp(music, 30)
# fade in/out
fi = int(0.3 * SR); music[:fi] *= np.linspace(0, 1, fi)
end = int(T * SR); fo = int(2.5 * SR)
music[end - fo:end] *= np.linspace(1, 0, fo) ** 1.5
music[end:] = 0
music = music[:end]
music = np.tanh(music / np.abs(music).max() * 1.4) * 0.89
st = np.stack([music, np.roll(music, 220) * 0.98], 1)  # slight width
sf.write(f"{B}/music.wav", st, SR)
print("music", len(music) / SR)
