# Narration v3 (manager-approved script). One sentence per line, natural pacing.
# (scene, tts_text, caption_text, pause_after_seconds)
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
LINES = [
    (0, "Every enterprise already has what AI needs most: its own data.",
        "Every enterprise already has what AI needs most: its own data.", 0.7),
    (0, "For more than twenty years, Solix has helped the world's largest companies preserve it, govern it, and put it to work.",
        "For more than twenty years, Solix has helped the world's largest companies preserve it, govern it, and put it to work.", 1.0),

    (1, "It starts with AI-ready data.", "It starts with AI-ready data.", 0.5),
    (1, "The Solix Common Data Platform puts structured and unstructured data on one catalog, and one security model.",
        "The Solix Common Data Platform puts structured and unstructured data on one catalog and one security model.", 0.5),
    (1, "Enterprise Content Services governs your documents and email.", "Enterprise Content Services governs your documents and email.", 0.5),
    (1, "And Enterprise Data Governance, launching at Empower, enforces policy wherever data is used, including by AI.",
        "And Enterprise Data Governance, launching at Empower, enforces policy wherever data is used, including by AI.", 1.0),

    (2, "Then, Solix Enterprise AI activates it.", "Then Solix Enterprise AI activates it.", 0.6),
    (2, "Data Sense builds an Application Knowledge Graph, so AI understands what your data actually means.",
        "Data Sense builds an Application Knowledge Graph, so AI understands what your data actually means.", 0.5),
    (2, "Data Ask gives anyone cited answers, in plain English.", "Data Ask gives anyone cited answers in plain English.", 0.5),
    (2, "AI Warehouse lets your teams build on it.", "AI Warehouse lets your teams build on it.", 0.5),
    (2, "And with governance underneath, agents can act on it with confidence.",
        "And with governance underneath, agents can act on it with confidence.", 1.0),

    (3, "It works because Solix has spent two decades on the hardest data in the enterprise.",
        "It works because Solix has spent two decades on the hardest data in the enterprise:", 0.6),
    (3, "Retiring legacy applications, preserving records,", "retiring legacy applications, preserving records,", 0.8),
    (3, "and archiving SAP, Oracle, mainframe,", "and archiving SAP, Oracle, mainframe,", 0.8),
    (3, "email, file, and database data.", "email, file and database data.", 1.0),
    (3, "Shut down the old system. Cut the cost. Keep the history.", "Shut down the old system, cut the cost, keep the history.", 0.7),
    (3, "On the Common Data Platform, that history becomes AI-ready, not dead weight.",
        "On the Common Data Platform, that history becomes AI-ready, not dead weight.", 1.0),

    (4, "E A I Pharma accelerates drug discovery with data and AI, transforming research into intelligent insights.",
        "EAI Pharma accelerates drug discovery with data and AI, transforming research into intelligent insights.", 0.9),
    (4, "E A I Healthcare brings trusted data and collaborative AI intelligence together, for actionable healthcare outcomes.",
        "EAI Healthcare brings trusted data and collaborative AI intelligence together for actionable healthcare outcomes.", 0.8),
    (4, "It delivers Patient 360 Analytics, AI Clinical Intelligence, and Intelligent Imaging and Radiology.",
        "It delivers Patient 360 Analytics, AI Clinical Intelligence, and Intelligent Imaging and Radiology.", 0.8),
    (4, "From AI Clinical Assistants and Preventive Care, to Revenue Cycle Intelligence and AI-Powered Documentation.",
        "From AI Clinical Assistants and Preventive Care to Revenue Cycle Intelligence and AI-Powered Documentation.", 2.6),

    (5, "Today, Solix technology supports leading enterprises across industries, including organizations within the Fortune two thousand.",
        "Today, Solix technology supports leading enterprises across industries, including organizations within the Fortune 2000.", 0.5),
    (5, "From healthcare and pharma, to financial services, manufacturing, and technology,",
        "From healthcare and pharma to financial services, manufacturing, and technology,", 0.25),
    (5, "customers rely on Solix to solve complex data challenges at enterprise scale.",
        "customers rely on Solix to solve complex data challenges at enterprise scale.", 1.0),

    (6, "Solix's innovation has also earned recognition from leading technology research and market intelligence organizations,",
        "Solix's innovation has also earned recognition from leading technology research and market intelligence organizations,", 0.25),
    (6, "including Gartner, I D C, Forrester, and Bloor Research,", "including Gartner, IDC, Forrester, and Bloor Research,", 0.25),
    (6, "reinforcing its position in enterprise data management and AI.", "reinforcing its position in enterprise data management and AI.", 1.0),

    (7, "From data to intelligence.", "From data to intelligence,", 0.35),
    (7, "From governance to action.", "from governance to action,", 0.5),
    (7, "Solix is helping enterprises build the agentic future.", "Solix is helping enterprises build the agentic future.", 0.9),
    (7, "Solix Empower 2026.", "Solix Empower 2026.", 0.45),
    (7, "The Agentic Enterprise.", "The Agentic Enterprise.", 0.0),
]

if __name__ == "__main__":
    import soundfile as sf
    from kokoro_onnx import Kokoro
    D, voice, speed, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    k = Kokoro(D + "/kokoro.onnx", D + "/voices.bin")
    os.makedirs(out, exist_ok=True)
    only = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else None
    for i, (sc, t, cap, gap) in enumerate(LINES):
        if only is not None and i not in only:
            continue
        a, sr = k.create(t, voice=voice, speed=speed, lang="en-us")
        sf.write(f"{out}/{i:02d}.wav", a, sr)
    json.dump([dict(scene=s, tts=t, cap=c, gap=g) for s, t, c, g in LINES], open(f"{B}/lines3.json", "w"), indent=1)
