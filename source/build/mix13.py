# v12 mix: voice (with a touch of room), music ducked under it, and light sound design on the transitions
import json, os, numpy as np, soundfile as sf
from scipy.signal import resample_poly, fftconvolve, butter, sosfilt
from scipy.ndimage import uniform_filter1d
B = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(f"{B}/timeline12.json")); SR = 44100
rng = np.random.default_rng(3)
m, _ = sf.read(f"{B}/music12.wav"); N = len(m)
vo = np.zeros(N)
for i, L in enumerate(tl["lines"]):
    a, sr = sf.read(f"{B}/vo3/{i:02d}.wav"); a = a if sr == 44100 else resample_poly(a, 147, 80)
    a = a / np.abs(a).max() * 0.95
    j = int(L["start"] * SR); vo[j:j + len(a)] += a[:N - j]
# subtle room: exponentially decaying noise impulse response, ~9 % wet
n_ir = int(0.42 * SR); ir = rng.normal(0, 1, n_ir) * np.exp(-np.arange(n_ir) / (0.09 * SR))
ir = sosfilt(butter(2, 5200, "low", fs=SR, output="sos"), ir); ir /= np.abs(ir).sum() * 0.35
wet = fftconvolve(vo, ir)[:N]
vo = vo * 0.93 + wet * 0.09
act = uniform_filter1d((np.abs(vo) > 0.02).astype(float), int(0.6 * SR))
act = np.clip(act * 4, 0, 1); act = uniform_filter1d(act, int(0.35 * SR))
gain = 0.36 * (1 - 0.55 * act)
mix = m * gain[:, None] + vo[:, None]


def whoosh(dur=0.9, f0=300, f1=5200, amp=0.20):
    n = int(dur * SR); x = rng.normal(0, 1, n)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2.2
    out = np.zeros(n); seg = 12
    for k in range(seg):
        a0, a1 = k * n // seg, (k + 1) * n // seg
        fc = f0 * (f1 / f0) ** (k / (seg - 1))
        sos = butter(2, [fc * 0.7, min(fc * 1.4, SR / 2 - 100)], "band", fs=SR, output="sos")
        out[a0:a1] = sosfilt(sos, x[a0:a1])
    out = out / np.abs(out).max() * env * amp
    return out


def thump(amp=0.30):
    n = int(0.55 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (52 * np.exp(-tt * 5) + 34) * tt) * np.exp(-tt * 6.5) * amp


def add(sig, at):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    e = min(N, i + len(sig)); mix[i:e] += (sig[:e - i])[:, None]


for s in tl["segs"][1:]:
    b = s["start"]
    w = whoosh()
    add(w, b - 0.62); add(thump(), b - 0.04)
# logo reveal shimmer + final riser into the lock-up
sh = whoosh(1.6, 900, 9000, 0.10); add(sh, 0.9); add(thump(0.34), 1.9)
add(whoosh(2.0, 200, 7000, 0.16), tl["lines"][32]["start"] - 1.6)
mix /= np.abs(mix).max() / 0.97
sf.write(f"{B}/mix13.wav", mix, SR); print("ok", N / SR)
