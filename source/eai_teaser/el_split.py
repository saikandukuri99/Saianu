# Cut the ElevenLabs narration into the 37 script lines (one clip per line) so
# vo_track.py can place each line on its storyboard cue.
import sys, os, re, subprocess, numpy as np, soundfile as sf
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
a, sr = sf.read(src)
log = subprocess.run(['ffmpeg', '-nostdin', '-i', src, '-af', 'silencedetect=noise=-40dB:d=0.25', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr.replace('\r', '\n')
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
starts = [0.0] + en
segs = [(s, e) for s, e in zip(starts, st + [len(a) / sr]) if e - s > .1]
assert len(segs) == 36, len(segs)
def split(s, e, frac):
    # quietest 20 ms point within +-0.6 s of the expected boundary
    guess = s + (e - s) * frac
    lo, hi = int((guess - .6) * sr), int((guess + .6) * sr)
    w = int(.02 * sr)
    rms = [np.sqrt(np.mean(a[i:i + w] ** 2)) for i in range(lo, hi - w, w // 2)]
    cut = (lo + int(np.argmin(rms)) * (w // 2) + w // 2) / sr
    # widen to the whole quiet stretch around the cut so each half stops/starts in silence
    thr = np.sqrt(np.mean(a[int(s * sr):int(e * sr)] ** 2)) * .03
    i0 = i1 = int(cut * sr)
    while i0 > int(s * sr) and np.sqrt(np.mean(a[i0 - w:i0] ** 2)) < thr: i0 -= w // 4
    while i1 < int(e * sr) and np.sqrt(np.mean(a[i1:i1 + w] ** 2)) < thr: i1 += w // 4
    return [(s, i0 / sr), (i1 / sr, e)]
# segment index -> script lines: 'split' (two lines), 'merge' (with next segment)
plan = []
i = 0
splits = {7: .566, 10: .71, 19: .545, 23: .36}       # segment -> line-1 share
merges = {11, 16, 25}                                # segment joins the following one
while i < len(segs):
    s, e = segs[i]
    if i in splits: plan += split(s, e, splits[i])
    elif i in merges: plan.append((s, segs[i + 1][1])); i += 1
    else: plan.append((s, e))
    i += 1
assert len(plan) == 37, len(plan)
for k, (s, e) in enumerate(plan):
    # pad into the surrounding pauses, but never past the middle of the gap to the
    # neighbouring clip, so no syllable is copied into two clips
    prev_e = plan[k - 1][1] if k else -1
    next_s = plan[k + 1][0] if k + 1 < len(plan) else 1e9
    s0 = max(s - .04, (prev_e + s) / 2) if k else max(0, s - .04)
    e0 = min(e + .12, (e + next_s) / 2)
    c = a[max(0, int(s0 * sr)): int(e0 * sr)].copy()
    f = int(.015 * sr); c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
    sf.write(f'{out}/{k:02d}.wav', c, sr)
    print(k, round(s, 2), round(e, 2))
