import sys, json, os, soundfile as sf
from kokoro_onnx import Kokoro
D, B = sys.argv[1], sys.argv[2]
k = Kokoro(D + "/kokoro.onnx", D + "/voices.bin")
L = json.load(open(f"{B}/lines_90.json")); L3 = json.load(open(f"{B}/lines3b.json"))
for d in ("fx90_raw", "fx3_raw"): os.makedirs(f"{B}/{d}", exist_ok=True)
for i in (1, 2, 7, 8, 10):
    a, sr = k.create(L[i]["tts"], voice="af_heart", speed=1.12, lang="en-us"); sf.write(f"{B}/fx90_raw/{i:02d}.wav", a, sr)
a, sr = k.create(L3[18]["tts"], voice="af_heart", speed=1.0, lang="en-us"); sf.write(f"{B}/fx3_raw/18.wav", a, sr)
print(k.tokenizer.phonemize("Solix EAI Pharma", "en-us"))
