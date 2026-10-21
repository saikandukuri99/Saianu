"""Generate the voice-over lines (Kokoro, am_michael) into a work dir. Usage: vo.py MODEL_DIR OUT_DIR"""
import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
model_dir, out = sys.argv[1], sys.argv[2]
LINES = {
 "a1": "The world is entering a new era.",
 "a2": "An era where every business, every team, and every person at work, can do things a little differently.",
 "a3": "Picture it. Decisions made faster. Operations that run smoother. Customers who feel looked after. And new ideas, coming to life in days, not months.",
 "a4": "So how does a company make that real?",
 "a5": "It comes down to three things.",
 "p1": "First, data that's ready.",
 "p2": "Second, people who are ready.",
 "p3": "Third, an enterprise that's ready.",
 "b1": "That's why we built Solix Academy. A place where professionals, teams, and whole companies can learn to work with AI, with confidence.",
 "b2": "Here, the best of academia meets the best of industry. You learn from professors, practitioners, and technology experts.",
 "b3": "Through real projects, hands-on labs, and exercises built around real business problems.",
 "c1": "Our goal is simple. Help your people grow. Help your teams spot new possibilities. And help your company get more from its AI.",
 "c2": "Because the future belongs to the companies that keep on learning.",
 "c3": "Welcome to Solix Academy. Learn. Innovate. Transform.",
 "c4": "Your journey starts here.",
}
k = Kokoro(f"{model_dir}/kokoro.onnx", f"{model_dir}/voices.bin")
dur = {}
for key, t in LINES.items():
    s, sr = k.create(t, voice="am_michael", speed=0.93, lang="en-us")
    s = np.concatenate([np.zeros(int(.08*sr)), s, np.zeros(int(.12*sr))])
    sf.write(f"{out}/{key}.wav", s, sr); dur[key] = len(s)/sr
json.dump(dur, open(f"{out}/dur.json", "w"), indent=1); print(dur)
