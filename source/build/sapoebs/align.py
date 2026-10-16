# Snap script punctuation to the real pauses in the placed voice-over track -> vo_align.json
import sys, json, itertools, numpy as np, soundfile as sf
from cues import VO, weights, OFF
a, sr = sf.read(sys.argv[1]); a = a[:, 0] if a.ndim > 1 else a
hop = int(.01 * sr); env = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)]); quiet = env < .012
out = []
for v in VO:
    txt = v["text"]; s, e = v["start"], v["end"]; i0, j0 = int(s * 100), int(e * 100)
    cands = []; k = i0 + 12
    while k < j0 - 12:
        if quiet[k]:
            m = k
            while m < j0 and quiet[m]: m += 1
            if m - k >= 7 and m < j0 - 10: cands.append((k / 100, m / 100))
            k = m
        else: k += 1
    cuts = [i + 1 for i, ch in enumerate(txt[:-1]) if ch in ",.?"]            # char index just after punctuation
    segs = []; prev = 0
    for c in cuts + [len(txt)]: segs.append((prev, c)); prev = c
    cum = np.cumsum([0] + weights(txt)); tot = cum[-1]
    pred = [s + .06 + (e - s - .16) * cum[c] / tot for c in cuts]            # predicted pause centres
    K = len(cuts); from functools import lru_cache
    @lru_cache(None)
    def solve(n, last):
        if n == K: return 0.0, ()
        best = (0.7 + solve(n + 1, last)[0], (None,) + solve(n + 1, last)[1])          # leave this comma unmatched
        for ci in range(last + 1, len(cands)):
            c0, c1 = cands[ci]; d = abs((c0 + c1) / 2 - pred[n])
            if d > 1.1: continue
            sub = solve(n + 1, ci); cost = d - .4 * (c1 - c0) + sub[0]
            if cost < best[0]: best = (cost, (ci,) + sub[1])
        return best
    sel = solve(0, -1)[1] if K else ()
    bounds = []; lastt = s + .06
    for n in range(K):
        if sel[n] is not None: bounds.append(cands[sel[n]])
        else: bounds.append((max(pred[n] - .04, lastt + .25), max(pred[n] + .04, lastt + .33)))
        lastt = bounds[-1][1]
    t_prev = s + .06; spans = []
    for n, (c0, c1) in enumerate(segs):
        t_end = bounds[n][0] if n < K else e - .08
        spans.append(dict(c0=c0, c1=c1, t0=round(t_prev, 3), t1=round(t_end, 3)))
        if n < K: t_prev = bounds[n][1]
    out.append(spans); print(v["i"], [(sp["t0"], sp["t1"]) for sp in spans])
for l in out:                               # stored unshifted: cues.py adds OFF back when it loads
    for sp in l: sp["t0"] = round(float(sp["t0"]) - OFF, 3); sp["t1"] = round(float(sp["t1"]) - OFF, 3)
json.dump(out, open("vo_align.json", "w"))
