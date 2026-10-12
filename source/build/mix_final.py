import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from scipy.ndimage import uniform_filter1d
SR = 44100
m, _ = sf.read("music_final.wav"); v, _ = sf.read("vo_final_full.wav"); v = resample_poly(v, 147, 160)
N = len(m); v = np.pad(v, (0, max(0, N - len(v))))[:N]
v = v / np.abs(v).max() * 0.95
act = uniform_filter1d((np.abs(v) > 0.02).astype(float), int(0.6 * SR)); act = np.clip(act * 4, 0, 1); act = uniform_filter1d(act, int(0.35 * SR))
mix = m * (0.34 * (1 - 0.55 * act))[:, None] + v[:, None]
mix /= np.abs(mix).max() / 0.97
sf.write("mix_final.wav", mix, SR); print("ok", N / SR)
