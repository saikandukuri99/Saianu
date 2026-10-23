# Original procedural score for the EAI teaser (royalty-free): warm pads, pluck
# arpeggio, sub bass and a light beat that builds; impacts on the title and logo.
import json, sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR = 44100
TL = json.load(open("timeline.json")); T = TL["total"]; L = [l["start"] for l in TL["lines"]]
N = int((T + 1) * SR); BPM = 96; beat = 60 / BPM; bar = 4 * beat
rng = np.random.default_rng(3)
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def add(buf, sig, t):
    i = int(t * SR)
    if i < 0 or i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i]
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a, r):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e
def saw(f, n, det=(-7, 0, 7)):
    t = np.arange(n) / SR; o = np.zeros(n)
    for d in det: ph = rng.random(); o += 2 * ((t * f * 2 ** (d / 1200) + ph) % 1) - 1
    return o / len(det)
# chords (D major-ish, uplifting): Bm  G  D  A
CH = [[59, 62, 66], [55, 59, 62], [50, 54, 57], [57, 61, 64]]
BASS = [35, 31, 38, 33]
pad = np.zeros(N); arp = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N); fx = np.zeros(N)
start = 0.0
nb = int(T / bar) + 2
S3, S10 = L[6] - .6, L[35] - .6
for b in range(nb):
    t0 = start + b * bar; c = CH[b % 4]
    n = int(bar * SR * 1.15)
    p = sum(saw(hz(m), n) for m in c + [c[0] + 12]) * env(n, .6, .7)
    add(pad, lp(p, 1400) * .09, t0)
    if t0 >= 5.5:
        nn = int(bar * SR)
        add(bass, np.sin(2 * np.pi * hz(BASS[b % 4]) * np.arange(nn) / SR) * env(nn, .02, .3) * .22, t0)
    # pluck arpeggio 8ths from the first narration onward
    if t0 >= 5.5 and t0 < T - 4:
        seq = [c[0] + 12, c[1] + 12, c[2] + 12, c[1] + 12, c[0] + 24, c[2] + 12, c[1] + 12, c[2] + 12]
        for k, m in enumerate(seq):
            nn = int(.45 * SR); tt = np.arange(nn) / SR
            s = (np.sin(2 * np.pi * hz(m) * tt) + .3 * np.sin(4 * np.pi * hz(m) * tt)) * np.exp(-tt * 9)
            add(arp, s * .06, t0 + k * beat / 2)
    # light beat once the solution starts
    if S3 <= t0 < S10 - .5:
        for k in range(4):
            tb = t0 + k * beat; nn = int(.35 * SR); tt = np.arange(nn) / SR
            if k in (0, 2):
                add(drums, np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * .32, tb)
            else:
                nz = hp(rng.standard_normal(int(.18 * SR)), 1500) * np.exp(-np.arange(int(.18 * SR)) / SR * 22)
                add(drums, nz * .07, tb)
            for h in range(2):
                nh = int(.05 * SR); add(drums, hp(rng.standard_normal(nh), 7000) * np.exp(-np.arange(nh) / SR * 80) * .05, tb + h * beat / 2 + beat / 4)
def impact(t, g=1):
    n = int(3 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * (40 + 60 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 2.2) * .5
    s += lp(rng.standard_normal(n), 900) * np.exp(-tt * 3) * .25
    add(fx, s * g, t)
def riser(t_end, d=1.6, g=.15):
    n = int(d * SR); tt = np.arange(n) / SR
    s = hp(rng.standard_normal(n), 2000) * (tt / d) ** 2 * g
    add(fx, s, t_end - d)
impact(.35, .9); impact(1.1, .5)
cuts = [L[2], L[6], L[9], L[14], L[19], L[23], L[27], L[30]]
for c in cuts: riser(c - .5, 1.2, .08)
riser(S10 + .1, 2.0, .16); impact(S10 + .15, 1.0)
mix = pad + arp + bass + drums + fx
# global arc: soft intro, fuller middle, resolve and fade at the end
t = np.arange(N) / SR
arc = np.interp(t, [0, 5, 6, S3, S3 + 2, S10, T - 3, T + 1], [.8, .8, .65, .7, 1, 1, .9, 0])
mix *= arc
mix = np.tanh(mix * 1.4) / 1.4
sf.write(sys.argv[1], np.stack([mix, np.roll(mix, 300)], 1).astype(np.float32), SR)
print("music", round(len(mix) / SR, 2), round(np.abs(mix).max(), 3))
