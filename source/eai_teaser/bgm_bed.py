# Loop a short music clip into a full-length bed with crossfaded seams,
# fade-in at the top and a gentle fade-out over the end card.
import sys, json, numpy as np, soundfile as sf
src, dst = sys.argv[1], sys.argv[2]
T = json.load(open("timeline.json"))["total"]
a, sr = sf.read(src)
xf = int(.35 * sr)
ramp = np.linspace(0, 1, xf)[:, None]
bed = a.copy()
while len(bed) < (T + 1) * sr:
    tail, head = bed[-xf:], a[:xf]
    bed = np.concatenate([bed[:-xf], tail * (1 - ramp) + head * ramp, a[xf:]])
bed = bed[:int(T * sr)]
t = np.arange(len(bed)) / sr
env = np.clip(t / 1.2, 0, 1) * np.clip((T - t) / 3.5, 0, 1)
sf.write(dst, (bed * env[:, None]).astype(np.float32), sr)
print(round(len(bed) / sr, 2))
