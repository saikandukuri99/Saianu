# Female narration for the Solix Academy promo: Kokoro af_heart, one sentence per file,
# then a broadcast voice chain (EQ, de-ess, gentle compression, light room).
# usage: python3 make_vo.py <kokoro-model-dir>
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
LINES = [  # (id, section, text, speed)
    ("l01", 1, "The world is entering a new era.", 1.0),
    ("l02", 1, "An era where every enterprise, every business function, and every employee, can be reimagined through Artificial Intelligence.", 1.06),
    ("l03", 1, "But how do organizations make this transformation a reality?", 1.04),
    ("l04", 2, "It starts with three essential pillars.", 1.05),
    ("l05", 2, "First: AI-Ready Data. Because AI is only as powerful as the structured, governed information behind it.", 1.1),
    ("l06", 2, "Second: AI-Ready People. Equipping your workforce to lead AI transformation across the organization.", 1.1),
    ("l07", 2, "And third: AI-Ready Governance. Building the trusted foundation needed to deliver secure, scalable business value.", 1.1),
    ("l08", 3, "Introducing Solix Academy.", 1.02),
    ("l09", 3, "A premier learning platform, designed to help enterprises embrace AI faster, and with confidence.", 1.16),
    ("l10", 3, "Built by distinguished professors, leading AI practitioners, and industry experts,", 1.16),
    ("l11", 3, "we deliver hands-on labs and real-world projects, from AI fundamentals to production-grade engineering,", 1.18),
    ("l12", 3, "in flexible self-paced and instructor-led formats.", 1.14),
    ("l13", 4, "Our mission is simple: to transform everyone into AI-ready innovators.", 1.08),
    ("l14", 4, "The future belongs to organizations that learn, adapt, and innovate faster than ever.", 1.1),
    ("l15", 4, "Welcome to Solix Academy.", 1.0),
    ("l16", 4, "Learn.", 0.95),
    ("l17", 4, "Innovate.", 0.95),
    ("l18", 4, "Transform.", 0.92),
    ("l19", 4, "Your AI journey starts today.", 1.0),
]
TEMPO = {"l02": 1.05, "l05": 1.06, "l06": 1.06, "l07": 1.06, "l09": 1.06, "l10": 1.06, "l11": 1.07, "l12": 1.05, "l13": 1.04, "l14": 1.05}
CHAIN = ("highpass=f=80,equalizer=f=220:t=q:w=1.0:g=-2.0,equalizer=f=3200:t=q:w=1.2:g=2.0,"
         "equalizer=f=9500:t=h:w=1:g=1.5,deesser=i=0.35,"
         "acompressor=threshold=-21dB:ratio=2.4:attack=6:release=140:makeup=2.0,"
         "aecho=0.92:0.9:19|37:0.06|0.04,aresample=48000")

def tighten(a, sr, longest=0.30):
    """Shorten any silence inside a sentence that runs longer than `longest` seconds (crossfaded)."""
    w = int(0.01 * sr)
    e = np.array([np.sqrt(np.mean(a[i:i + w] ** 2)) for i in range(0, len(a) - w, w)])
    quiet = e < 0.006
    cuts, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if (j - i) * 0.01 > longest:
                mid = (i + j) // 2
                drop = int(((j - i) * 0.01 - longest) * sr)
                cuts.append((mid * w - drop // 2, mid * w + drop // 2))
            i = j
        else:
            i += 1
    for c0, c1 in reversed(cuts):
        x = int(0.01 * sr)
        tail = a[c1:c1 + x] * np.linspace(0, 1, len(a[c1:c1 + x]))
        a = np.concatenate([a[:c0], a[c0:c0 + x] * np.linspace(1, 0, len(a[c0:c0 + x])) + np.pad(tail, (0, max(0, len(a[c0:c0 + x]) - len(tail))))[:len(a[c0:c0 + x])], a[c1 + x:]])
    return a

def main(model_dir):
    k = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))
    os.makedirs(os.path.join(HERE, "raw"), exist_ok=True)
    meta = []
    for lid, sec, text, speed in LINES:
        a, sr = k.create(text, voice="af_heart", speed=speed, lang="en-us")
        a = np.asarray(a, dtype=np.float32)
        idx = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, idx[0] - int(0.04 * sr)): min(len(a), idx[-1] + int(0.12 * sr))]
        a = tighten(a, sr)
        f = int(0.015 * sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        raw = os.path.join(HERE, "raw", lid + ".wav"); sf.write(raw, a, sr)
        out = os.path.join(HERE, lid + ".wav")
        tempo = TEMPO.get(lid, 1.0)  # a light pitch-preserving tighten on the long lines, to land the 75 s slot
        chain = (f"atempo={tempo}," if tempo != 1.0 else "") + CHAIN
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-af", chain, out], check=True)
        d = sf.info(out).duration
        meta.append(dict(id=lid, section=sec, text=text, dur=round(d, 3)))
        print(lid, round(d, 2), text)
    json.dump(meta, open(os.path.join(HERE, "lines.json"), "w"), indent=1)
    # the same table as a script, so score.js can read it in the browser too
    with open(os.path.join(HERE, "lines.js"), "w") as f:
        f.write("globalThis.VO_LINES = " + json.dumps(meta) + ";\n")

if __name__ == "__main__":
    main(sys.argv[1])
