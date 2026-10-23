# Lay polished VO lines on the timeline: each line starts at its storyboard cue
# (+ title intro offset), or just after the previous line if that runs long.
import json, sys, numpy as np, soundfile as sf
src, out = sys.argv[1], sys.argv[2]
INTRO, SR, TAIL = 6.0, 44100, 4.5
SCENES = {2, 6, 9, 14, 19, 23, 27, 30, 35}  # first line of each storyboard scene
L = json.load(open("lines.json"))
buf = np.zeros(int(200 * SR))
tl = []
for i, l in enumerate(L):
    a, sr = sf.read(f"{src}/{i:02d}.wav"); assert sr == SR
    if a.ndim > 1: a = a.mean(1)
    gap = (1.0 if i in SCENES else 0.2 if L[i - 1]["cap"].endswith(",") else 0.5) if tl else 0
    st = max(INTRO + l["cue"], tl[-1]["end"] + gap if tl else 0)
    s = int(st * SR)
    buf[s:s + len(a)] += a
    tl.append(dict(i=i, start=round(st, 3), end=round(st + len(a) / SR, 3), cap=l["cap"]))
TOTAL = round(tl[-1]["end"] + TAIL, 2)
buf = buf[:int(TOTAL * SR)]
sf.write(out, buf.astype(np.float32), SR, subtype="PCM_24")
json.dump(dict(intro=INTRO, total=TOTAL, lines=tl), open("timeline.json", "w"), indent=1)
print("total", TOTAL, "peak", round(np.abs(buf).max(), 3))
