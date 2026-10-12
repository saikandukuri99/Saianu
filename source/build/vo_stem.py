# Build a voice-only track for a timeline: place each line's wav at its start time.
import json, sys, numpy as np, soundfile as sf
tl, vodir, out = sys.argv[1], sys.argv[2], sys.argv[3]
T = json.load(open(tl)); SR = 48000
N = int((T["total"] + 1) * SR)
buf = np.zeros(N)
from scipy.signal import resample_poly
for i, L in enumerate(T["lines"]):
    a, sr = sf.read(f"{vodir}/{i:02d}.wav")
    if a.ndim > 1: a = a.mean(1)
    if sr != SR: a = resample_poly(a, SR, sr)
    a = a / max(1e-6, np.abs(a).max()) * 0.89
    j = int(L["start"] * SR); buf[j:j + len(a)] += a[:N - j]
sf.write(out, buf, SR, subtype="PCM_24")
print(out, round(N / SR, 1))
