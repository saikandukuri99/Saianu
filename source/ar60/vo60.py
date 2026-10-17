# Solix Application Retirement, 60-second overview: female narration (Kokoro af_heart), one clip per sentence.
# (id, scene, tts_text, caption, pause_after)
import json, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
B = os.path.dirname(os.path.abspath(__file__))
LINES = [
 ("p1", "problem", "Every enterprise has legacy applications it can't turn off... because the data inside still matters.",
  "Every enterprise has legacy applications it can't turn off, because the data inside still matters.", .4),
 ("c1", "cost", "Keeping them running drains budget, adds security risk, and locks valuable data in silos.",
  "Keeping them running drains budget, adds security risk, and locks valuable data in silos.", .4),
 ("r1", "retire", "Solix Application Retirement moves structured and unstructured data from legacy systems into the Solix Common Data Platform... a secure, governed archive.",
  "Solix Application Retirement moves structured and unstructured data from legacy systems into the Solix Common Data Platform, a secure, governed archive.", .25),
 ("r2", "retire", "Then you shut the old applications down, for good.", "Then you shut the old applications down for good.", .4),
 ("m1", "comply", "Compliance is built in.", "Compliance is built in.", .3),
 ("m2", "comply", "Policy-based retention, legal holds, and e-discovery keep you audit-ready.",
  "Policy-based retention, legal holds, and eDiscovery keep you audit-ready.", .3),
 ("m3", "comply", "Sensitive data is identified and protected, and records are defensibly deleted when retention ends.",
  "Sensitive data is identified and protected, and records are defensibly deleted when retention ends.", .4),
 ("a1", "ai", "And your retired data doesn't sit idle.", "And your retired data doesn't sit idle.", .3),
 ("a2", "ai", "With Data Ask in C D P Navigator, you can simply talk to your archived data.",
  "With Data Ask in CDP Navigator, you can simply talk to your archived data.", .3),
 ("a3", "ai", "Ask questions in plain language and get answers in seconds... with no reports to build, and no legacy app to log into.",
  "Ask questions in plain language and get answers in seconds, with no reports to build and no legacy app to log into.", .4),
 ("e1", "end", "Lower costs, less risk, and new value from old data.", "Lower costs, less risk, and new value from old data.", .35),
 ("e2", "end", "Retire, comply, and activate... with Solix.", "Retire, comply, and activate, with Solix.", 0.0),
]
VOICE = os.environ.get("VOICE", "af_heart"); SPEED = float(os.environ.get("SPEED", "1.0"))
k = Kokoro("/tmp/claude-0/kok/kokoro-v1.0.onnx", "/tmp/claude-0/kok/voices-v1.0.bin")
os.makedirs(f"{B}/vo_raw", exist_ok=True); out = []
for i, (id_, sc, tts, cap, pause) in enumerate(LINES):
    a, sr = k.create(tts, voice=VOICE, speed=SPEED, lang="en-us")
    sf.write(f"{B}/vo_raw/{i:02d}_{id_}.wav", a, sr)
    out.append(dict(i=i, id=id_, scene=sc, caption=cap, pause=pause, file=f"{i:02d}_{id_}.wav")); print(id_, round(len(a)/sr, 2))
json.dump(out, open(f"{B}/lines.json", "w"), indent=1)
