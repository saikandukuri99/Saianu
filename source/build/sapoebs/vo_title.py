# Title-card voice-over ("SAP and Oracle. ERP archiving and application retirement."): same voice, tone chain and level as the narration.
#   python3 vo_title.py KOKORO_DIR WORK_DIR OUT_TITLE_WAV   -> also writes vo_title.json (card length + start of the 2nd sentence)
import sys, os, re, json, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
K, WORK, OUT = sys.argv[1:4]; os.makedirs(WORK, exist_ok=True); SR = 48000
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vo_v8.py")).read()
CHAIN = None; ns = {}
exec(src[src.index("CHAIN = ("):src.index("k = Kokoro(")], ns); CHAIN = ns["CHAIN"]
TARGET_RMS = 10 ** (-20 / 20)
k = Kokoro(K + "/kokoro-v1.0.onnx", K + "/voices-v1.0.bin")
def take(text, n):
    a, sr = k.create(text, voice="af_heart", speed=1.0, lang="en-us")
    ix = np.where(np.abs(a) > .012)[0]; a = a[max(0, ix[0] - int(.05 * sr)): min(len(a), ix[-1] + int(.16 * sr))].astype(np.float64)
    f = int(.012 * sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    raw = f"{WORK}/t{n}_raw.wav"; out = f"{WORK}/t{n}.wav"; sf.write(raw, a, sr)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-af", CHAIN, "-ac", "1", out], check=True)
    y, _ = sf.read(out); act = np.abs(y) > .02; return y * (TARGET_RMS / np.sqrt(np.mean(y[act] ** 2)))
# letters spoken as letters (the engine would say "S-uh-P" for "S A P"): exact sounds, as in vo_v8.py
s1 = k.tokenizer.phonemize("and Oracle Applications.", "en-us"); p1 = "ˌɛsˌeɪpˈiː " + s1
y1 = None
a, sr = k.create(p1, voice="af_heart", speed=1.0, lang="en-us", is_phonemes=True)
ix = np.where(np.abs(a) > .012)[0]; a = a[max(0, ix[0] - int(.05 * sr)): min(len(a), ix[-1] + int(.16 * sr))].astype(np.float64)
f = int(.012 * sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f); sf.write(f"{WORK}/t0_raw.wav", a, sr)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{WORK}/t0_raw.wav", "-af", CHAIN, "-ac", "1", f"{WORK}/t0.wav"], check=True)
y1, _ = sf.read(f"{WORK}/t0.wav"); act = np.abs(y1) > .02; y1 = y1 * (TARGET_RMS / np.sqrt(np.mean(y1[act] ** 2)))
p2 = k.tokenizer.phonemize("PeopleSoft, J D Edwards, Siebel, and O E B S.", "en-us")
a, sr = k.create(p2, voice="af_heart", speed=1.0, lang="en-us", is_phonemes=True)
ix = np.where(np.abs(a) > .012)[0]; a = a[max(0, ix[0] - int(.05 * sr)): min(len(a), ix[-1] + int(.16 * sr))].astype(np.float64)
f = int(.012 * sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f); sf.write(f"{WORK}/t1_raw.wav", a, sr)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{WORK}/t1_raw.wav", "-af", CHAIN, "-ac", "1", f"{WORK}/t1.wav"], check=True)
y2, _ = sf.read(f"{WORK}/t1.wav"); act = np.abs(y2) > .02; y2 = y2 * (TARGET_RMS / np.sqrt(np.mean(y2[act] ** 2)))
T0, GAP = .45, .30
y = np.concatenate([np.zeros(int(T0 * SR)), y1, np.zeros(int(GAP * SR)), y2])
s2 = T0 + len(y1) / SR + GAP; end = len(y) / SR
sf.write(OUT, y, SR, subtype="PCM_24")
off = round(max(3.0, end + .75), 2)
json.dump(dict(off=off, s1=T0, s2=round(s2, 3), end=round(end, 3)), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vo_title.json"), "w"))
print("title voice: sentence 1", round(len(y1) / SR, 2), "s, sentence 2", round(len(y2) / SR, 2), "s -> card length", off, "s")
