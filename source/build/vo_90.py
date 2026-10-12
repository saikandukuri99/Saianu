# 90-second version narration: shortened script + industry lines. (scene, tts, caption, gap)
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
C2 = json.load(open(f"{B}/lines_cut2.json"))
V3 = json.load(open(f"{B}/lines3.json"))
LINES = [(L["scene"], L["tts"], L["cap"], L["gap"]) for L in C2[:7]]
for i, g in ((17, 0.45), (18, 0.45), (19, 0.5), (21, 1.0)):
    LINES.append((4, V3[i]["tts"], V3[i]["cap"], g))
LINES += [(L["scene"], L["tts"], L["cap"], L["gap"]) for L in C2[7:]]

if __name__ == "__main__":
    import soundfile as sf
    from kokoro_onnx import Kokoro
    D, voice, speed, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    k = Kokoro(D + "/kokoro.onnx", D + "/voices.bin")
    os.makedirs(out, exist_ok=True)
    for i, (sc, t, cap, gap) in enumerate(LINES):
        a, sr = k.create(t, voice=voice, speed=speed, lang="en-us")
        sf.write(f"{out}/{i:02d}.wav", a, sr)
    json.dump([dict(scene=s, tts=t, cap=c, gap=g) for s, t, c, g in LINES], open(f"{B}/lines_90.json", "w"), indent=1)
