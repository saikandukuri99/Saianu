# Application Retirement 60s film: narration (Kokoro af_heart), one clip per line.
# (id, tts_text, caption, pause_after)
import json, os, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
B = os.path.dirname(os.path.abspath(__file__))
LINES = [
 ("hook", "Every enterprise carries applications... it has already moved on from.", "Every enterprise carries applications it has already moved on from.", 0.7),
 ("t1", "A renewal you shouldn't pay.", "A renewal you shouldn't pay.", 0.25),
 ("t2", "A system you can't patch.", "A system you can't patch.", 0.25),
 ("t3", "An acquisition to absorb.", "An acquisition to absorb.", 0.25),
 ("t4", "An archive at its limit.", "An archive at its limit.", 0.25),
 ("t5", "An AI program, short on history.", "An AI program short on history.", 0.8),
 ("one", "Many reasons. One engine.", "Many reasons. One engine.", 0.9),
 ("connect", "Solix Application Retirement connects to ERP, mainframe, custom and sass applications, files, and email.", "Solix Application Retirement connects to ERP, mainframe, custom and SaaS applications, files and email.", 0.5),
 ("migrate", "Data moves into a governed Preservation Zone, checked against the source, with retention and legal hold from the day it lands.", "Data moves into a governed Preservation Zone, checked against the source, with retention and legal hold from the day it lands.", 0.6),
 ("dark", "Only then does the application go dark. Its licenses, its servers, its risk... gone for good.", "Only then does the application go dark. Its licenses, its servers, its risk: gone for good.", 0.8),
 ("access", "Nothing it held is lost. Auditors get provable records. Users get the reports they know.", "Nothing it held is lost. Auditors get provable records. Users get the reports they know.", 0.6),
 ("ask", "With Solix Data Ask, people ask in plain English, and get cited answers from the application's own Knowledge Graph.", "With Solix Data Ask, people ask in plain English and get cited answers from the application's own Knowledge Graph.", 0.6),
 ("ai", "Governed history, ready for your AI.", "Governed history, ready for your AI.", 1.0),
 ("sign", "Solix Application Retirement. Retire the application... Keep every answer.", "Retire the application. Keep every answer.", 0.0),
]
VOICE = os.environ.get("VOICE", "af_heart"); SPEED = float(os.environ.get("SPEED", "0.94"))
k = Kokoro("/tmp/claude-0/kok/kokoro-v1.0.onnx", "/tmp/claude-0/kok/voices-v1.0.bin")
os.makedirs(f"{B}/vo_raw", exist_ok=True)
out = []
for i, (id_, tts, cap, pause) in enumerate(LINES):
    a, sr = k.create(tts, voice=VOICE, speed=SPEED, lang="en-us")
    sf.write(f"{B}/vo_raw/{i:02d}_{id_}.wav", a, sr)
    out.append(dict(i=i, id=id_, caption=cap, pause=pause, file=f"{i:02d}_{id_}.wav"))
    print(id_, round(len(a)/sr, 2))
json.dump(out, open(f"{B}/lines.json", "w"), indent=1)
