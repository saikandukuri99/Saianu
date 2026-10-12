# 90-second cut narration (manager script). (scene, tts, caption, gap)
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
LINES = [
    (1, "It starts with AI-ready data.", "It starts with AI-ready data.", 0.35),
    (1, "The Solix Common Data Platform brings structured and unstructured data together.", "The Solix Common Data Platform brings structured and unstructured data together.", 0.3),
    (1, "Enterprise Content Services governs documents and email.", "Enterprise Content Services governs documents and email.", 0.3),
    (1, "And Enterprise Data Governance enforces policy wherever data is used, including by AI.", "And Enterprise Data Governance enforces policy wherever data is used, including by AI.", 0.8),
    (2, "Then, Solix Enterprise AI activates it.", "Then Solix Enterprise AI activates it.", 0.35),
    (2, "Data Sense builds an Application Knowledge Graph.", "Data Sense builds an Application Knowledge Graph.", 0.3),
    (2, "Data Ask gives anyone cited answers, in plain English.", "Data Ask gives anyone cited answers in plain English.", 0.3),
    (2, "AI Warehouse lets teams build on it.", "AI Warehouse lets teams build on it.", 0.3),
    (2, "And agents can act on it with confidence.", "And agents can act on it with confidence.", 0.8),
    (3, "Solix also tackles the hardest data in the enterprise.", "Solix also tackles the hardest data in the enterprise:", 0.3),
    (3, "Retiring legacy applications, preserving records,", "retiring legacy applications, preserving records,", 0.25),
    (3, "and archiving SAP, Oracle, mainframe, email, file, and database data.", "and archiving SAP, Oracle, mainframe, email, file and database data.", 0.4),
    (3, "That history becomes AI-ready, not dead weight.", "That history becomes AI-ready, not dead weight.", 0.8),
    (5, "Trusted by leading enterprises, including Fortune two thousand organizations,", "Trusted by leading enterprises, including Fortune 2000 organizations,", 0.2),
    (6, "Solix is recognized by Gartner, I D C, Forrester, and Bloor Research.", "Solix is recognized by Gartner, IDC, Forrester, and Bloor Research.", 0.8),
    (7, "From data to intelligence.", "From data to intelligence,", 0.3),
    (7, "From governance to action.", "from governance to action,", 0.4),
    (7, "Solix is helping enterprises build the agentic future.", "Solix is helping enterprises build the agentic future.", 0.7),
    (7, "Solix Empower 2026.", "Solix Empower 2026.", 0.4),
    (7, "The Agentic Enterprise.", "The Agentic Enterprise.", 0.0),
]
if __name__ == "__main__":
    import soundfile as sf
    from kokoro_onnx import Kokoro
    D, voice, speed, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    k = Kokoro(D + "/kokoro.onnx", D + "/voices.bin")
    os.makedirs(out, exist_ok=True)
    for i, (sc, t, cap, gap) in enumerate(LINES):
        a, sr = k.create(t, voice=voice, speed=speed, lang="en-us")
        sf.write(f"{out}/{i:02d}.wav", a, sr)
    json.dump([dict(scene=s, tts=t, cap=c, gap=g) for s, t, c, g in LINES], open(f"{B}/lines_cut.json", "w"), indent=1)
