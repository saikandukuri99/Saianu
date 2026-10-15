# v2: Data Ask insert (2 new lines, same Kokoro af_heart voice) + full timeline (+0.9 s hold after "The result?")
import sys, os, json, numpy as np, soundfile as sf, subprocess
from kokoro_onnx import Kokoro
K, RAW, POL, OLD_POL, OLD_META, OUT_WAV, OUT_JSON = sys.argv[1:8]
FPS = 30; SR = 48000; HOLD = 0.9
def tc(s): h, m, sec, f = map(int, s.split(":")); return h*3600+m*60+sec+f/FPS
NEW = [("00:00:43:21", "00:00:47:10", "Ask your archive in plain language, with Data Ask."),
       ("00:00:47:22", "00:00:52:17", "Every answer cites its source, and every question is permission checked, and audit logged.")]
k = Kokoro(K + "/kokoro-v1.0.onnx", K + "/voices-v1.0.bin"); os.makedirs(RAW, exist_ok=True)
for i, (a, b, t) in enumerate(NEW):
    slot = tc(b) - tc(a)
    for sp in (1.0, 1.05, 1.1, 1.15, 1.2):
        au, sr = k.create(t, voice="af_heart", speed=sp, lang="en-us")
        if len(au) / sr <= slot + .3: break
    sf.write(f"{RAW}/n{i}.wav", au, sr); print("new", i, slot, sp, round(len(au)/sr, 2))
subprocess.run(["python3", "../polish.py", RAW, POL], check=True)
old = json.load(open(OLD_META))                       # lines 0..9 of v1
entries = []                                          # (wav, start, text)
for m in old[:6]: entries.append((f"{OLD_POL}/{m['i']:02d}.wav", m["start"], m["text"]))
for i, (a, b, t) in enumerate(NEW): entries.append((f"{POL}/n{i}.wav", tc(a), t))
for m in old[6:]:
    st = m["start"] + 10.0 + (HOLD if m["i"] > 6 else 0.0)        # +10:00 insert, then +0.9 s so "The result?" holds 2 s
    entries.append((f"{OLD_POL}/{m['i']:02d}.wav", st, m["text"]))
T = 63.87 + 10.0 + HOLD; buf = np.zeros(int(T * SR) + SR); timing = []
for n, (p, st, text) in enumerate(entries):
    tmp = p + ".48.wav"; subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", p, "-ar", str(SR), "-ac", "1", tmp], check=True)
    a, _ = sf.read(tmp); s0 = st - (0.35 if n == 0 else 0.05); i0 = int(s0 * SR); buf[i0:i0 + len(a)] += a
    timing.append(dict(i=n, start=round(s0, 3), end=round(s0 + len(a) / SR, 3), text=text))
buf = buf[:int(T * SR)]; buf = buf / np.abs(buf).max() * .89
sf.write(OUT_WAV, np.stack([buf, buf], 1), SR, subtype="PCM_24"); json.dump(timing, open(OUT_JSON, "w"), indent=1)
for t in timing: print(t["i"], t["start"], t["end"], t["text"][:40])
print("T", T)
