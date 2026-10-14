# SAP + OEBS voice-over: one Kokoro af_heart take per script line, fitted to the script timecodes.
import sys, os, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
D, out = sys.argv[1], sys.argv[2]
FPS = 30
def tc(s):
    h, m, sec, f = map(int, s.split(":")); return h*3600+m*60+sec+f/FPS
# (start, end, tts text, caption)  -- tts spells things the way they should be said
L = [
 ("00:00:00:18","00:00:03:07","S A P and Oracle E Business Suite run the business."),
 ("00:00:03:17","00:00:12:18","But years of inactive data keep bloating databases, slowing performance, and driving up costs, right when you're planning a move to S four HANA, or the cloud."),
 ("00:00:13:01","00:00:17:29","Solix Cloud brings more than twenty years of ERP archiving expertise, to both."),
 ("00:00:18:13","00:00:28:18","For S A P, Solix Cloud works natively through SAP's Archive Development Kit, with pre-built support for standard archive objects across Finance, Materials, Sales, and more."),
 ("00:00:29:02","00:00:36:07","For Oracle E Business Suite, Solix is certified by Oracle, and covers both archiving and full application retirement."),
 ("00:00:36:20","00:00:43:04","Inactive data moves out on policy, and stays searchable, reportable, and under legal hold, for as long as you need it."),
 ("00:00:44:01","00:00:44:24","The result?"),
 ("00:00:45:08","00:00:51:29","Leaner production systems, cleaner migrations, and S A P databases, up to thirty to sixty percent smaller."),
 ("00:00:52:12","00:00:56:06","Your ERP history becomes AI-ready data, not dead weight."),
 ("00:00:57:00","00:01:01:06","Solix Cloud. Built for S A P. Built for Oracle."),
]
k = Kokoro(D + "/kokoro-v1.0.onnx", D + "/voices-v1.0.bin")
os.makedirs(out, exist_ok=True); meta = []
for i, (a, b, t) in enumerate(L):
    slot = tc(b) - tc(a)
    best = None
    for sp in (1.0, 1.05, 1.1, 1.15, 1.2):
        au, sr = k.create(t, voice="af_heart", speed=sp, lang="en-us")
        dur = len(au)/sr
        best = (au, sr, sp, dur)
        if dur <= slot + 0.35: break
    au, sr, sp, dur = best
    sf.write(f"{out}/{i:02d}.wav", au, sr)
    meta.append(dict(i=i, start=tc(a), slot=slot, speed=sp, dur=round(dur, 2), text=t))
    print(i, round(slot, 2), sp, round(dur, 2))
json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
