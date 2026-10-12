import sys, json, os, soundfile as sf
from kokoro_onnx import Kokoro
D, B = sys.argv[1], sys.argv[2]
k = Kokoro(D + "/kokoro.onnx", D + "/voices.bin")
L = json.load(open(f"{B}/lines_90.json")); L3 = json.load(open(f"{B}/lines3b.json"))
os.makedirs(f"{B}/fix90_raw", exist_ok=True); os.makedirs(f"{B}/fix3_raw", exist_ok=True)
for i in (1, 7, 8):
    a, sr = k.create(L[i]["tts"], voice="af_heart", speed=1.12, lang="en-us"); sf.write(f"{B}/fix90_raw/{i:02d}.wav", a, sr)
a, sr = k.create(L3[18]["tts"], voice="af_heart", speed=1.0, lang="en-us"); sf.write(f"{B}/fix3_raw/18.wav", a, sr)
