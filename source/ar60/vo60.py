# Solix Application Retirement, 60-second overview: female narration (Kokoro af_heart), one clip per sentence.
# (id, scene, tts_text, caption, pause_after)
import json, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
B = os.path.dirname(os.path.abspath(__file__))
LINES = [
 ("p1", "problem", "Every enterprise runs legacy applications it can't switch off... because the data inside still matters.",
  "Every enterprise runs legacy applications it can't switch off, because the data inside still matters.", .55),
 ("c1", "cost", "Keeping them alive drains budget, widens the attack surface, and locks history in silos.",
  "Keeping them alive drains budget, widens the attack surface, and locks history in silos.", .55),
 ("r1", "retire", "Solix Application Retirement moves structured and unstructured data into a governed Preservation Zone,",
  "Solix Application Retirement moves structured and unstructured data into a governed Preservation Zone,", .12),
 ("r2", "retire", "validates it against the source... then switches the old applications off, for good.",
  "validates it against the source, then switches the old applications off for good.", .6),
 ("m1", "comply", "Retention, legal hold, e-discovery and masking apply from the day data lands.",
  "Retention, legal hold, eDiscovery and masking apply from the day data lands.", .3),
 ("m2", "comply", "You stay audit-ready, and records are defensibly deleted when retention ends.",
  "You stay audit-ready, and records are defensibly deleted when retention ends.", .6),
 ("a1", "ai", "And preserved data doesn't sit idle.", "And preserved data doesn't sit idle.", .5),
 ("a2", "ai", "With Solix Data Ask, people ask in plain English and get cited answers,",
  "With Solix Data Ask, people ask in plain English and get cited answers,", .1),
 ("a3", "ai", "grounded in the application's own Knowledge Graph.", "grounded in the application's own Knowledge Graph.", .8),
 ("e1", "end", "Lower cost. Less risk. Governed history, ready for AI.", "Lower cost. Less risk. Governed history, ready for AI.", .5),
 ("e2", "end", "Retire, preserve, and activate... with Solix.", "Retire, preserve, and activate, with Solix.", 0.0),
]
VOICE = os.environ.get("VOICE", "af_heart"); SPEED = float(os.environ.get("SPEED", "1.0"))
k = Kokoro("/tmp/claude-0/kok/kokoro-v1.0.onnx", "/tmp/claude-0/kok/voices-v1.0.bin")
os.makedirs(f"{B}/vo_raw", exist_ok=True); out = []
for i, (id_, sc, tts, cap, pause) in enumerate(LINES):
    a, sr = k.create(tts, voice=VOICE, speed=SPEED, lang="en-us")
    sf.write(f"{B}/vo_raw/{i:02d}_{id_}.wav", a, sr)
    out.append(dict(i=i, id=id_, scene=sc, caption=cap, pause=pause, file=f"{i:02d}_{id_}.wav")); print(id_, round(len(a)/sr, 2))
json.dump(out, open(f"{B}/lines.json", "w"), indent=1)
