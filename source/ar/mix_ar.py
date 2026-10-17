# Mix VO over the slow score (music ducks under the voice), loudness-normalise, mux with picture.
import json, os, subprocess, numpy as np, soundfile as sf
B = os.path.dirname(os.path.abspath(__file__))
vo, sr = sf.read(f"{B}/vo.wav"); mu, _ = sf.read(f"{B}/music.wav")
n = min(len(vo), len(mu)); vo = vo[:n]; mu = mu[:n]
# duck envelope from VO activity (smoothed), music sits ~-9 dB under speech
win = int(.05*sr); env = np.sqrt(np.convolve(vo**2, np.ones(win)/win, "same"))
act = (env > .01).astype(float)
k = int(.35*sr); act = np.convolve(act, np.ones(k)/k, "same")
duck = 1 - .5*np.clip(act*1.5, 0, 1)
mix = np.stack([vo, vo], 1)*1.0 + mu*.34*duck[:, None]
mix /= np.abs(mix).max()/.9
sf.write(f"{B}/mix.wav", mix, sr)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{B}/mix.wav", "-af", "loudnorm=I=-16:TP=-1.5:LRA=9",
                "-ar", "48000", f"{B}/mix_norm.wav"], check=True)
out = os.path.join(B, "..", "..", "output", "Solix_Application_Retirement_60s_1080p.mp4")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{B}/ar_video.mp4", "-i", f"{B}/mix_norm.wav",
                "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-b:v", "10M", "-maxrate", "14M", "-bufsize", "20M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest",
                "-movflags", "+faststart", out], check=True)
print(out)
