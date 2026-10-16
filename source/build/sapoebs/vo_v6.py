# v4 voice timeline: (1) "planning a move to the cloud" (S/4HANA removed), (2) Oracle portion first, then SAP portion. Everything else unchanged.
import sys, os, json, numpy as np, soundfile as sf, subprocess
from kokoro_onnx import Kokoro
K, RAW, POL, OLD_POL, POL2, TIMING_IN, OUT_WAV, OUT_JSON = sys.argv[1:9]
SR = 48000; T = 74.77
old = json.load(open(TIMING_IN))                                     # v3 timeline (12 lines)
LINE1 = "But years of inactive data keep bloating databases, slowing performance, and driving up costs, right when you're planning a move to the cloud."
k = Kokoro(K + "/kokoro-v1.0.onnx", K + "/voices-v1.0.bin"); os.makedirs(RAW, exist_ok=True)
for sp in (1.0, 1.05, 1.1):
    au, sr = k.create(LINE1, voice="af_heart", speed=sp, lang="en-us")
    if len(au) / sr <= 9.2: break
sf.write(f"{RAW}/l1.wav", au, sr); print("line1 speed", sp, round(len(au) / sr, 2))
LINE11 = "Solix. Built for S A P. Built for Oracle."                  # end line: "Solix" only (no "Cloud")
for sp in (1.0, 1.05):
    au, sr = k.create(LINE11, voice="af_heart", speed=sp, lang="en-us")
    if len(au) / sr <= 4.4: break
sf.write(f"{RAW}/l11.wav", au, sr); print("line11 speed", sp, round(len(au) / sr, 2))
subprocess.run(["python3", "../polish.py", RAW, POL], check=True)
def dur(p): return sf.info(p).duration
SAPT = old[3]["text"]; ORAT = old[4]["text"]                         # v3: index 3 = SAP line, 4 = Oracle line
assert SAPT.startswith("For S A P") and ORAT.startswith("For Oracle")
sap_wav, ora_wav = f"{OLD_POL}/03.wav", f"{OLD_POL}/04.wav"
sap_start = old[3]["start"] + dur(ora_wav) + 0.17        # SAP portion follows the Oracle portion, ends just before the policy line
E_ = [(f"{OLD_POL}/00.wav", old[0]["start"], old[0]["text"]), (f"{POL}/l1.wav", old[1]["start"], LINE1), (f"{OLD_POL}/02.wav", old[2]["start"], old[2]["text"]),
      (ora_wav, old[3]["start"], ORAT), (sap_wav, sap_start, SAPT), (f"{OLD_POL}/05.wav", old[5]["start"], old[5]["text"]),
      (f"{POL2}/n0.wav", old[6]["start"], old[6]["text"]), (f"{POL2}/n1.wav", old[7]["start"], old[7]["text"])]
for j in range(8, 11): E_.append((f"{OLD_POL}/{j - 2:02d}.wav", old[j]["start"], old[j]["text"]))
E_.append((f"{POL}/l11.wav", old[11]["start"], LINE11))
buf = np.zeros(int(T * SR) + SR); timing = []
for n, (p, st, text) in enumerate(E_):
    tmp = f"{RAW}/_t{n}.wav"; subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", p, "-ar", str(SR), "-ac", "1", tmp], check=True)
    a, _ = sf.read(tmp); i0 = int(st * SR); buf[i0:i0 + len(a)] += a
    timing.append(dict(i=n, start=round(st, 3), end=round(st + len(a) / SR, 3), text=text))
buf = buf[:int(T * SR)]; buf = buf / np.abs(buf).max() * .89
sf.write(OUT_WAV, np.stack([buf, buf], 1), SR, subtype="PCM_24"); json.dump(timing, open(OUT_JSON, "w"), indent=1)
for t in timing: print(t["i"], t["start"], t["end"], t["text"][:48])
