# Narration v2: (scene, tts_text, caption_text, gap_after_seconds)
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
LINES = [
    (0, "Welcome to Solix Empower 2026.", "Welcome to Solix Empower 2026.", 0.9),
    (0, "For more than two decades, Solix Technologies has helped enterprises transform their data into a strategic advantage.",
        "For more than two decades, Solix Technologies has helped enterprises transform their data into a strategic advantage.", 0.45),
    (0, "Bringing together data management, governance, content services, and AI, on one unified foundation.",
        "Bringing together data management, governance, content services, and AI on one unified foundation.", 1.0),
    (1, "At the foundation is the Solix Enterprise Platform.", "At the foundation is the Solix Enterprise Platform.", 0.4),
    (1, "Combining the Common Data Platform, Enterprise Data Governance, and Enterprise Content Services,",
        "Combining the Common Data Platform, Enterprise Data Governance, and Enterprise Content Services,", 0.25),
    (1, "to discover, manage, secure, govern, and activate enterprise information, across every environment.",
        "to discover, manage, secure, govern, and activate enterprise information across environments.", 1.0),
    (2, "Building on this foundation, Solix Enterprise AI brings intelligence to enterprise data.",
        "Building on this foundation, Solix Enterprise AI brings intelligence to enterprise data.", 0.6),
    (2, "Data Sense delivers semantic understanding.", "Data Sense delivers semantic understanding.", 0.35),
    (2, "Data Ask enables natural-language interaction.", "Data Ask enables natural-language interaction.", 0.35),
    (2, "Application Knowledge Graphs connect business context,", "Application Knowledge Graphs connect business context,", 0.25),
    (2, "while AI Warehouse and Solix Agentic help organizations build, and activate, governed AI.",
        "while AI Warehouse and Solix Agentic help organizations build and activate governed AI.", 1.0),
    (3, "Solix also delivers comprehensive data lifecycle solutions.", "Solix also delivers comprehensive data lifecycle solutions.", 0.8),
    (3, "From application retirement, and data preservation,", "From application retirement and data preservation,", 1.5),
    (3, "to SAP, Oracle, and mainframe,", "to SAP, Oracle, and mainframe,", 1.7),
    (3, "to email, file, database, and active archiving.", "to email, file, database, and active archiving.", 1.9),
    (3, "Enterprises can reduce complexity, control costs, and preserve valuable information, without costly migration.",
        "Enterprises can reduce complexity, control costs, and preserve valuable information without costly migration.", 1.0),
    (4, "Purpose-built solutions extend this platform across industries.", "Purpose-built solutions extend this platform across industries.", 0.6),
    (4, "E A I Healthcare brings data and AI capabilities to healthcare, delivering Patient 360, and governed clinical intelligence.",
        "EAI Healthcare brings data and AI capabilities to healthcare, delivering Patient 360 and governed clinical intelligence.", 0.8),
    (4, "E A I Pharma advances data and AI capabilities for pharmaceutical innovation.",
        "EAI Pharma advances data and AI capabilities for pharmaceutical innovation.", 0.8),
    (4, "And Solix Academy helps organizations build the skills needed for an AI-ready enterprise.",
        "And Solix Academy helps organizations build the skills needed for an AI-ready enterprise.", 1.0),
    (5, "Today, Solix technology supports leading enterprises across industries, including organizations within the Fortune two thousand.",
        "Today, Solix technology supports leading enterprises across industries, including organizations within the Fortune 2000.", 0.5),
    (5, "From healthcare and pharma, to financial services, manufacturing, and technology,",
        "From healthcare and pharma to financial services, manufacturing, and technology,", 0.2),
    (5, "customers rely on Solix to solve complex data challenges, at enterprise scale.",
        "customers rely on Solix to solve complex data challenges at enterprise scale.", 1.0),
    (6, "Solix's innovation has also earned recognition from leading technology research, and market intelligence organizations,",
        "Solix's innovation has also earned recognition from leading technology research and market intelligence organizations,", 0.2),
    (6, "including Gartner, I D C, Forrester, and Bloor Research,", "including Gartner, IDC, Forrester, and Bloor Research,", 0.2),
    (6, "reinforcing its position in enterprise data management and AI.", "reinforcing its position in enterprise data management and AI.", 1.0),
    (7, "From data to intelligence.", "From data to intelligence.", 0.35),
    (7, "From governance to action.", "From governance to action.", 0.5),
    (7, "Solix is helping enterprises build the agentic future.", "Solix is helping enterprises build the agentic future.", 0.6),
    (7, "Connect with our experts. Exchange ideas.", "Connect with our experts. Exchange ideas.", 0.7),
    (7, "Solix Empower 2026. The Agentic Enterprise.", "Solix Empower 2026. The Agentic Enterprise.", 0.0),
]

if __name__ == "__main__":
    import soundfile as sf
    from kokoro_onnx import Kokoro
    D, voice, speed = sys.argv[1], sys.argv[2], float(sys.argv[3])
    k = Kokoro(D + "/kokoro.onnx", D + "/voices.bin")
    os.makedirs(f"{B}/vo2", exist_ok=True)
    for i, (sc, t, cap, gap) in enumerate(LINES):
        a, sr = k.create(t, voice=voice, speed=speed, lang="en-us")
        sf.write(f"{B}/vo2/{i:02d}.wav", a, sr)
    json.dump([dict(scene=s, tts=t, cap=c, gap=g) for s, t, c, g in LINES], open(f"{B}/lines.json", "w"), indent=1)
