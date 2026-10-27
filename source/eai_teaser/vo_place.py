# Place line clips at the start times already in timeline.json (picture unchanged),
# e.g. after re-cutting clips. Fails if any clip would run into the next line.
import sys, json, numpy as np, soundfile as sf
src, out = sys.argv[1], sys.argv[2]
T = json.load(open("timeline.json")); L = T["lines"]
sr = sf.info(f"{src}/00.wav").samplerate
buf = np.zeros(int(T["total"] * sr))
for i, l in enumerate(L):
    a, r = sf.read(f"{src}/{i:02d}.wav"); assert r == sr
    s = int(l["start"] * sr)
    nxt = L[i + 1]["start"] if i + 1 < len(L) else T["total"]
    assert l["start"] + len(a) / sr <= nxt + 1e-3, (i, l["start"] + len(a) / sr, nxt)
    buf[s:s + len(a)] += a
sf.write(out, buf.astype(np.float32), sr, subtype="PCM_24")
print("ok", T["total"])
