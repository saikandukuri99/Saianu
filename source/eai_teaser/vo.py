# EAI Teaser (Storyline A) narration: Kokoro af_heart, one line per cue.
# (cue_start_s, tts_text, caption_text)
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
LINES = [
    (0.3,  "AI is transforming how enterprises run and grow.", "AI is transforming how enterprises run and grow."),
    (5.5,  "But your AI is only as ready as your enterprise data is.", "But your AI is only as ready as your enterprise data is."),
    (10.3, "Tables with cryptic names.", "Tables with cryptic names."),
    (12.2, "Systems that don't talk to each other.", "Systems that don't talk to each other."),
    (14.2, "Documents no one has indexed.", "Documents no one has indexed."),
    (17.0, "So your AI can't use it.", "So your AI can't use it."),
    (19.8, "Solix Enterprise AI gets your data ready for AI.", "Solix Enterprise AI gets your data ready for AI."),
    (23.3, "So you can understand it, ask it anything,", "So you can understand it, ask it anything,"),
    (25.7, "build on it, and put it to work.", "build on it, and put it to work."),
    (29.3, "Data Sense makes sense of all your data, structured and unstructured.", "Data Sense makes sense of all your data, structured and unstructured."),
    (32.6, "It drafts the business meaning, and your experts review it.", "It drafts the business meaning, and your experts review it."),
    (35.6, "Knowledge graphs for your applications and cloud platforms", "Knowledge graphs for your applications and cloud platforms"),
    (38.5, "get you started in minutes.", "get you started in minutes."),
    (40.4, "And a steward's worklist keeps your experts in the loop, ranked by what matters most.", "And a steward's worklist keeps your experts in the loop, ranked by what matters most."),
    (44.8, "Here's what sets Solix apart.", "Here's what sets Solix apart."),
    (46.7, "One knowledge graph that connects meaning across all your applications.", "One knowledge graph that connects meaning across all your applications."),
    (50.9, "The same supplier in three systems becomes one record you can trust.", "The same supplier in three systems becomes one record you can trust."),
    (54.3, "One shared meaning, everywhere.", "One shared meaning, everywhere."),
    (56.7, "One governed answer across all your enterprise applications.", "One governed answer across all your enterprise applications."),
    (59.8, "Data Ask answers questions in plain language,", "Data Ask answers questions in plain language,"),
    (61.7, "across structured and unstructured data,", "across structured and unstructured data,"),
    (64.5, "grounded in your business context,", "grounded in your business context,"),
    (67.5, "with every answer cited.", "with every answer cited."),
    (70.8, "Then the people who know your business take over.", "Then the people who know your business take over."),
    (73.7, "They describe the application they need,", "They describe the application they need,"),
    (76.1, "and AI Warehouse builds it on governed, version-tracked data.", "and AI Warehouse builds it on governed, version-tracked data."),
    (79.1, "Your AI, on your data.", "Your AI, on your data."),
    (81.3, "Agentic goes further. Just describe the work you need done.", "Agentic goes further. Just describe the work you need done."),
    (85.2, "Agentic AI builds it, tests it, and runs it.", "Agentic AI builds it, tests it, and runs it."),
    (88.6, "Less manual work, more done every day.", "Less manual work, more done every day."),
    (91.8, "And it works with what you already have.", "And it works with what you already have."),
    (94.1, "Any L L M.", "Any LLM."),
    (95.9, "Any application.", "Any application."),
    (97.7, "Any data platform.", "Any data platform."),
    (99.9, "It fits right into your existing stack.", "It fits right into your existing stack."),
    (103.4, "Solix Enterprise AI.", "Solix Enterprise AI."),
    (104.9, "Put AI in the hands of your business.", "Put AI in the hands of your business."),
]

if __name__ == "__main__":
    import soundfile as sf
    from kokoro_onnx import Kokoro
    voice, speed, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    k = Kokoro("/opt/kokoro/kokoro-v1.0.onnx", "/opt/kokoro/voices-v1.0.bin")
    os.makedirs(out, exist_ok=True)
    only = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
    for i, (cue, t, cap) in enumerate(LINES):
        if only is not None and i not in only:
            continue
        # "Agentic" = ay-JEN-tik: force a clear first syllable with explicit phonemes
        ph = k.tokenizer.phonemize(t, "en-us").replace("eɪdʒˈɛntɪk", "ˌeɪ dʒˈɛntɪk")
        a, sr = k.create(ph, voice=voice, speed=speed, lang="en-us", is_phonemes=True)
        sf.write(f"{out}/{i:02d}.wav", a, sr)
        print(i, round(len(a) / sr, 2), flush=True)
    json.dump([dict(cue=c, tts=t, cap=p) for c, t, p in LINES], open(f"{B}/lines.json", "w"), indent=1)
