"""New female narration for the EAI Healthcare cut (replaces the old voice).

Each phrase starts at the same moment as in the finalized video, so on-screen
highlights stay in sync. Phrases that run longer than their slot are gently
time-compressed (pitch kept).

usage: python3 vo_healthcare_female.py MODEL_DIR OUT.wav DURATION [VOICE] [SPEED]
"""
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

SR = 48000
# (start_seconds, text) - starts measured from the original narration
LINES = [
    (0.73, "Every hospital holds a wealth of clinical data,"),
    (6.62, "unlocking insights that drive better patient outcomes."),
    (10.58, "Solix AI Warehouse unifies healthcare data,"),
    (13.93, "powering intelligent, and personalized care,"),
    (16.78, "transforming patient outcomes."),
    (19.40, "Six pillars of an AI-ready foundation,"),
    (22.05, "for healthcare intelligence."),
    (23.53, "AI Warehouse."),
    (24.90, "Federated Governance."),
    (26.33, "Patient three sixty."),
    (27.95, "Clinical Intelligence, and Imaging."),
    (30.10, "Multi-agentic intelligence, for every specialty."),
    (34.45, "The outcome is a Patient three sixty,"),
    (37.08, "where every specialty has its own multi-agent clusters,"),
    (40.48, "with a consensus score."),
    (43.18, "Purpose-built Solix agents"),
    (44.90, "bring every system into focus,"),
    (47.05, "turning real-time insights into better patient outcomes."),
    (51.30, "Every finding comes with its evidence,"),
    (53.45, "by design."),
    (54.50, "The readings are cited."),
    (55.88, "The rules are applied,"),
    (57.30, "based on the published guidelines."),
    (60.03, "Clinicians lead every decision."),
    (61.95, "Review the evidence,"),
    (63.30, "refine the findings, and approve with confidence, before sign-off."),
    (67.90, "A unified Patient three sixty knowledge layer."),
    (70.70, "Connected globally."),
    (72.10, "Governed by design."),
]


def stretch(x, sr, factor):
    with tempfile.TemporaryDirectory() as d:
        sf.write(f"{d}/i.wav", x, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{d}/i.wav", "-af",
                        f"rubberband=tempo={factor}:formant=preserved", f"{d}/o.wav"], check=True)
        y, _ = sf.read(f"{d}/o.wav")
    return y


def main():
    mdir, out, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
    voice = sys.argv[4] if len(sys.argv) > 4 else "af_heart"
    speed = float(sys.argv[5]) if len(sys.argv) > 5 else 0.95
    k = Kokoro(f"{mdir}/kokoro.onnx", f"{mdir}/voices.bin")
    track = np.zeros(int(dur * SR))
    for i, (t, text) in enumerate(LINES):
        a, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
        nz = np.flatnonzero(np.abs(a) > 0.01)
        a = a[max(0, nz[0] - int(0.02 * sr)): nz[-1] + int(0.08 * sr)]
        slot = (LINES[i + 1][0] if i + 1 < len(LINES) else dur - 1.0) - t - 0.12
        if len(a) / sr > slot:
            a = stretch(a, sr, min(len(a) / sr / slot, 1.25))
        a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
        a = a / np.abs(a).max() * 0.9
        s = int(t * SR)
        track[s: s + len(a)] += a[: len(track) - s]
        print(f"{t:6.2f}  {len(a) / SR:5.2f}s / slot {slot:5.2f}s  {text}")
    sf.write(out, track, SR)


if __name__ == "__main__":
    main()
