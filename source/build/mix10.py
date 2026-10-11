import json, os, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from scipy.ndimage import uniform_filter1d
B = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(f"{B}/timeline10.json")); SR = 44100
m, _ = sf.read(f"{B}/music10.wav"); N = len(m)
vo = np.zeros(N)
for i, L in enumerate(tl["lines"]):
    a, sr = sf.read(f"{B}/vo3/{i:02d}.wav"); a = a if sr == 44100 else resample_poly(a, 147, 80)
    a = a / np.abs(a).max() * 0.95
    j = int(L["start"] * SR); vo[j:j + len(a)] += a[:N - j]
act = uniform_filter1d((np.abs(vo) > 0.02).astype(float), int(0.6 * SR))
act = np.clip(act * 4, 0, 1); act = uniform_filter1d(act, int(0.35 * SR))
gain = 0.34 * (1 - 0.55 * act)          # music well under the voice
mix = m * gain[:, None] + vo[:, None]
mix /= np.abs(mix).max() / 0.97
sf.write(f"{B}/mix10.wav", mix, SR); print("ok", N / SR)
