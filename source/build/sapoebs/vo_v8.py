# v8 voice-over: updated script ("SAP-Updated_Video_Script"), natural pacing, one take per sentence,
# per-take level matching, warmth/air chain, real pauses, light room tone.
#   python3 vo_v8.py KOKORO_DIR WORK_DIR OUT_VO.wav OUT_TIMING.json
import sys, os, json, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
K, WORK, OUT_WAV, OUT_JSON = sys.argv[1:5]
os.makedirs(WORK, exist_ok=True)
SR = 48000
# (sentences) per line; spelled letters / numbers written the way they are spoken
LINES = [
 ["S A P and Oracle Applications run the business."],
 ["But years of inactive data keep bloating databases, slowing performance, and driving up costs, right when you're planning a move to the cloud."],
 ["Solix Common Data Platform brings more than twenty years of E R P archiving expertise, to both."],
 ["For Oracle E Business Suite, Solix is certified by Oracle, and covers both archiving and full application retirement."],
 ["For S A P, Solix works natively through S A P's Archiving Development Kit, with pre-built support for standard archive objects across Finance, Materials, Sales, and more."],
 ["Inactive data moves out on policy, and stays searchable, reportable, and under legal hold, for as long as you need it."],
 ["Ask your archive in plain language, with Data Ask."],
 ["Every answer cites its source.", "And every question is permission checked, and audit logged."],
 ["The result?"],
 ["Leaner production systems, cleaner migrations, and legacy databases, up to thirty to sixty percent smaller."],
 ["Your E R P history becomes A I activated data, not dead weight."],
 ["Solix. Built for S A P. Built for Oracle."],
]
# silence after each line before the next one (s). Line 0 -> 1 leaves room for chips + underline; 8 -> 9 is set by the 2 s hold.
GAP = {0: 1.05, 1: .50, 2: .45, 3: .45, 4: .50, 5: .55, 6: .40, 7: .80, 9: .50, 10: .55}
HOLD_NEXT = 2.14                        # "The result?" stays on screen 2.0 s; next line starts this long after it begins
SENT_GAP = .34
TARGET_RMS = 10 ** (-20 / 20)
CHAIN = ("aresample=48000:resampler=soxr,highpass=f=80,equalizer=f=240:t=q:w=1.0:g=-2.2,equalizer=f=3100:t=q:w=1.1:g=2.4,"
         "equalizer=f=5800:t=q:w=1.0:g=1.2,aexciter=level_in=1:level_out=1:amount=0.3:drive=6:blend=0:freq=7000:ceil=16000,"
         "deesser=i=0.35,acompressor=threshold=-22dB:ratio=2.2:attack=8:release=170:makeup=2,aecho=0.9:0.9:23|47:0.05|0.035")
k = Kokoro(K + "/kokoro-v1.0.onnx", K + "/voices-v1.0.bin")
rs = np.random.RandomState(21)

def take(text, n):
    sp = float(np.clip(1.01 + rs.uniform(-.025, .025), .98, 1.04))            # calm, slightly varied pace
    a, sr = k.create(text, voice="af_heart", speed=sp, lang="en-us")
    env = np.abs(a) > .012; ix = np.where(env)[0]
    a = a[max(0, ix[0] - int(.05 * sr)): min(len(a), ix[-1] + int(.16 * sr))].astype(np.float64)
    f = int(.012 * sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    raw = f"{WORK}/s{n:02d}_raw.wav"; out = f"{WORK}/s{n:02d}.wav"
    sf.write(raw, a, sr)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-af", CHAIN, "-ac", "1", out], check=True)
    y, _ = sf.read(out)
    act = np.abs(y) > .02; rms = np.sqrt(np.mean(y[act] ** 2)) if act.any() else 1
    y = y * (TARGET_RMS / rms)                                               # every sentence at the same loudness
    return y, sp

pieces = []; n = 0
for i, sents in enumerate(LINES):
    ys = []
    for s in sents:
        y, sp = take(s, n); n += 1; ys.append(y); print(i, round(sp, 3), round(len(y) / SR, 2), s[:50])
    parts = []
    for j, y in enumerate(ys):
        parts.append(y)
        if j < len(ys) - 1: parts.append(np.zeros(int(SENT_GAP * SR)))
    pieces.append(np.concatenate(parts))
# place on the timeline
starts = []; t = .25
for i, y in enumerate(pieces):
    starts.append(t); end = t + len(y) / SR
    t = starts[i] + HOLD_NEXT if i == 8 else (end + GAP[i] if i in GAP else end)
T = starts[-1] + len(pieces[-1]) / SR + 3.6
buf = np.zeros(int(T * SR))
for st, y in zip(starts, pieces): i0 = int(st * SR); buf[i0:i0 + len(y)] += y
# room tone: very quiet pink-ish noise under the whole track (no dead digital silence between sentences)
nz = rs.randn(len(buf)); b = np.cumsum(nz); b -= np.convolve(b, np.ones(2000) / 2000, "same"); b = b / np.abs(b).max()
buf += b * 10 ** (-62 / 20)
buf = np.tanh(buf * 1.1) / 1.1                                               # gentle safety saturation
buf = buf / np.abs(buf).max() * .89
sf.write(OUT_WAV, np.stack([buf, buf], 1), SR, subtype="PCM_24")
tm = []
for i, (st, y) in enumerate(zip(starts, pieces)):
    tm.append(dict(i=i, start=round(st, 3), end=round(st + len(y) / SR, 3), text=" ".join(LINES[i])))
json.dump(tm, open(OUT_JSON, "w"), indent=1)
for t_ in tm: print(t_["i"], t_["start"], t_["end"], t_["text"][:50])
words = sum(len(" ".join(l).split()) for l in LINES); print("words", words, "voiced+pauses", round(starts[-1] + len(pieces[-1]) / SR, 1), "s; unshifted film length", round(T, 2))
