# Female narration for the Solix Academy promo: Kokoro af_heart, one sentence per file,
# then a broadcast voice chain (EQ, de-ess, gentle compression, light room).
# usage: python3 make_vo.py <kokoro-model-dir>
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
LINES = [  # (id, section, text, speed); the three pillar lines are spoken by the HeyGen avatars (avatars/)
    ("a01", 1, "The world is entering a new era.", 0.92),
    ("a02", 1, "An era where every enterprise...", 0.95),
    ("a03", 1, "Every business function...", 0.95),
    ("a04", 1, "And every employee...", 0.95),
    ("a05", 1, "Can be reimagined through the power of Artificial Intelligence.", 0.97),
    ("a06", 1, "But how do organizations make this transformation a reality?", 0.97),
    ("a07", 2, "It starts with three essential pillars.", 0.97),
    ("a08", 2, "That's where we can make a difference.", 0.95),
    ("a09", 3, "Introducing Solix Academy.", 0.98),
    ("a10", 3, "A premier learning platform designed to help aspiring individuals, professionals, teams, and enterprises embrace AI: faster, smarter, and with confidence.", 1.02),
    ("a11", 3, "At Solix Academy, we combine the learning from distinguished professors, leading AI practitioners, enterprise technology experts, and business innovators.", 1.02),
    ("a12", 3, "Experience immersive learning through real-world use cases, hands-on labs, practical exercises, and enterprise-focused projects.", 1.0),
    ("a13", 3, "From absolute beginner to enterprise expert.", 0.97),
    ("a14", 3, "Structured tracks take you from fundamentals to production-grade Enterprise AI.", 1.0),
    ("a15", 3, "Every format: self-paced and instructor-led, with many free courses to start today.", 1.0),
    ("a16", 4, "Our mission is simple:", 0.95),
    ("a17", 4, "To transform everyone into AI-Ready innovators.", 0.97),
    ("a18", 4, "To help teams discover new possibilities.", 0.97),
    ("a19", 4, "To empower enterprises to unlock the full potential of AI.", 0.97),
    ("a20", 4, "The future belongs to organizations that learn, adapt, and innovate faster than ever before.", 1.0),
    ("a21", 4, "Welcome to Solix Academy.", 0.95),
    ("a22", 4, "Learn.", 0.95),
    ("a23", 4, "Innovate.", 0.95),
    ("a24", 4, "Transform.", 0.92),
    ("a25", 4, "Your AI journey starts here.", 0.97),
]
TEMPO = {}
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
