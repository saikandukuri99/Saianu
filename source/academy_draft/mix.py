"""Mix VO + presenter clip audio + a soft synthetic music bed. Usage: mix.py OUT_DIR  (needs audio_schedule.json)"""
import sys, json, subprocess, numpy as np, soundfile as sf
OUT = sys.argv[1]; SR = 48000
S = json.load(open(f"{OUT}/audio_schedule.json")); N = int((S["total"] + 1) * SR)
def load(path, norm=True):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-vn", "-af", "loudnorm=I=-18:TP=-2:LRA=7" if norm else "anull", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32)
def place(buf, x, at):
    i = int(at * SR); buf[i:i + len(x)] += x[:len(buf) - i]
vo = np.zeros(N, np.float32); cl = np.zeros(N, np.float32)
for v in S["vo"]: place(vo, load(v["file"]) * 1.0, v["start"])
for c in S["clips"]: place(cl, load(c["file"]), c["start"])
# music bed: slow pad over Am - F - C - G, ducked under speech
t = np.arange(N) / SR; mus = np.zeros(N, np.float32)
chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
for i, ch in enumerate(chords):
    for f in ch:
        for det in (-.4, .4):
            env = np.clip(np.sin(np.pi * ((t / 8 - i) % 4) / 1.0), 0, 1) if False else None
for f_idx in range(4):
    seg = ((t // 8).astype(int)) % 4 == f_idx
    ph = (t % 8) / 8; env = np.sin(np.pi * ph) ** 0.6
    for f in chords[f_idx]:
        for det in (-.5, .5): mus += (seg * env * np.sin(2 * np.pi * (f + det) * t) * .03).astype(np.float32)
    mus += (seg * env * np.sin(2 * np.pi * chords[f_idx][0] / 2 * t) * .05).astype(np.float32)
speech = np.abs(vo) + np.abs(cl)
k = np.ones(SR // 2, np.float32) / (SR // 2); act = np.convolve(speech, k, "same")
duck = 1 - .6 * np.clip(act * 25, 0, 1)
fade = np.clip(np.minimum(t / 1.5, (S["total"] - t) / 2.0), 0, 1)
mix = vo * 1.0 + cl * 1.0 + mus * duck * fade * 1.6
mix = np.tanh(mix * .9) * .95
sf.write(f"{OUT}/mix.wav", mix, SR); print("mix ok", len(mix) / SR)
