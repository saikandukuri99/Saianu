# v8 voice-over: updated script ("SAP-Updated_Video_Script"), natural pacing, one take per sentence,
# per-take level matching, warmth/air chain, real pauses, light room tone.
#   python3 vo_v8.py KOKORO_DIR WORK_DIR OUT_VO.wav OUT_TIMING.json
import sys, os, re, json, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
K, WORK, OUT_WAV, OUT_JSON = sys.argv[1:5]
os.makedirs(WORK, exist_ok=True)
SR = 48000
# (sentences) per line; spelled letters / numbers written the way they are spoken
LINES = [
 ["Enterprise applications run the business: Oracle applications, S A P, and mainframes."],
 ["But years of inactive data keep bloating databases, slowing performance, and driving up costs, right when you're planning a move to the cloud."],
 ["Solix C D P brings more than twenty years of E R P archiving expertise, to all of them."],
 ["For Oracle E Business Suite, Solix is validated by Oracle, and covers both archiving and full application retirement."],
 ["For S A P, Solix C D P works natively through S A P's Archive Development Kit, with pre-built support for standard archive objects across Finance, Materials, Sales, and more."],
 ["Inactive data moves out on policy, and stays searchable, accessible, and reportable, for as long as you need it."],
 ["Solix includes pre-built Application Knowledge Graphs, or A K Gs, for these applications."],
 ["Ask your archive in plain language, with Data Ask."],
 ["Every answer cites its source.", "And every question is permission checked, and audit logged."],
 ["The result?"],
 ["Leaner production systems, cleaner migrations, and legacy databases, up to thirty to sixty percent smaller."],
 ["Your E R P history becomes A I activated data, not dead weight."],
 ["Solix C D P. Built for enterprise applications."],
]
# silence after each line before the next one (s). Line 0 -> 1 leaves room for chips + underline; 8 -> 9 is set by the 2 s hold.
GAP = {0: .90, 1: .38, 2: .36, 3: .36, 4: .40, 5: .46, 6: .42, 7: .32, 8: .55, 10: .40, 11: .46}   # tighter, continuous flow like the reference
HOLD_NEXT = 2.14                        # "The result?" stays on screen 2.0 s; next line starts this long after it begins
SENT_GAP = .28
TARGET_RMS = 10 ** (-20 / 20)
# tone matched to the reference voice (Solix_AR_Update): warmer, less upper-mid presence, less top-end sparkle
CHAIN = ("aresample=48000:resampler=soxr,highpass=f=70,equalizer=f=240:t=q:w=1.0:g=-3,lowshelf=f=130:g=1.6,"
         "equalizer=f=1500:t=q:w=1.0:g=-1.4,equalizer=f=3100:t=q:w=1.1:g=1.2,equalizer=f=6000:t=q:w=0.9:g=-2.0,highshelf=f=8500:g=1.8,"
         "deesser=i=0.4,acompressor=threshold=-22dB:ratio=2.4:attack=8:release=170:makeup=2,aecho=0.9:0.9:23|47:0.05|0.035")
VOICE = os.environ.get("VOICE", "am_michael"); SPD = float(os.environ.get("SPD", "1.12"))
k = Kokoro(K + "/kokoro-v1.0.onnx", K + "/voices-v1.0.bin")
rs = np.random.RandomState(21)
# "S A P" / "A I" must be spoken as letters: the engine would read "S A P" as "S-uh-P" and "A I" as "uh-eye".
# So those tokens are given as exact sounds (ess-ay-pee, ay-eye); everything else is phonemized normally.
PAT = re.compile(r"S A P(?:'s)?|A I|A K Gs?|C D P")
def ph(text):
    out = ""; pos = 0
    def add(p):
        nonlocal out
        out += (p if (not out or p[0] in ",.?!;:") else " " + p)
    for m in PAT.finditer(text):
        seg = text[pos:m.start()].strip()
        if seg: add(k.tokenizer.phonemize(seg, "en-us"))
        tok = m.group(0)
        add("ˌɛsˌeɪpˈiːz" if tok.endswith("'s") else "ˌɛsˌeɪpˈiː" if tok.startswith("S A P") else "ˌsiːdˌiːpˈiː" if tok == "C D P" else "ˌeɪˈaɪ" if tok == "A I" else "ˌeɪkˌeɪdʒˈiːz" if tok.endswith("s") else "ˌeɪkˌeɪdʒˈiː"); pos = m.end()
    seg = text[pos:].strip()
    if seg: add(k.tokenizer.phonemize(seg, "en-us"))
    return out

def take(text, n):
    sp = float(np.clip(SPD + rs.uniform(-.025, .025), SPD - .03, SPD + .03))            # calm, slightly varied pace
    if PAT.search(text): a, sr = k.create(ph(text), voice=VOICE, speed=sp, lang="en-us", is_phonemes=True)
    else: a, sr = k.create(text, voice=VOICE, speed=sp, lang="en-us")
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
    t = starts[i] + HOLD_NEXT if i == 9 else (end + GAP[i] if i in GAP else end)
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
