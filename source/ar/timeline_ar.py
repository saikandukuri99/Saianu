# Polish VO clips (trim + broadcast chain), lay them on a timeline, write vo.wav + timeline.json.
import json, os, subprocess, numpy as np, soundfile as sf
B = os.path.dirname(os.path.abspath(__file__))
CHAIN = ("highpass=f=75,equalizer=f=220:t=q:w=1.0:g=-2,equalizer=f=3200:t=q:w=1.2:g=2,"
         "equalizer=f=9000:t=h:w=1:g=1.5,deesser=i=0.3,"
         "acompressor=threshold=-21dB:ratio=2.4:attack=6:release=140:makeup=2,"
         "aecho=0.92:0.9:19|37:0.06|0.04,aresample=48000")
SR = 48000; LEAD = 2.4; TAIL = 3.0
lines = json.load(open(f"{B}/lines.json"))
os.makedirs(f"{B}/vo", exist_ok=True)
t = LEAD; clips = []
for L in lines:
    a, sr = sf.read(f"{B}/vo_raw/{L['file']}")
    idx = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, idx[0] - int(.05*sr)): idx[-1] + int(.15*sr)]
    f = int(.015*sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    tmp = f"{B}/vo/_t.wav"; sf.write(tmp, a, sr)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-af", CHAIN, f"{B}/vo/{L['file']}"], check=True)
    os.remove(tmp)
    b, _ = sf.read(f"{B}/vo/{L['file']}")
    if b.ndim > 1: b = b.mean(1)
    d = len(b)/SR
    L.update(start=round(t, 3), end=round(t+d, 3)); clips.append(b)
    t += d + L["pause"]
total = t + TAIL
mix = np.zeros(int(total*SR)+SR)
for L, b in zip(lines, clips):
    s = int(L["start"]*SR); mix[s:s+len(b)] += b
mix = mix[:int(total*SR)]
mix *= 10**(-1/20) / max(1e-6, np.abs(mix).max())
sf.write(f"{B}/vo.wav", mix, SR)
json.dump(dict(total=round(total, 3), lines=lines), open(f"{B}/timeline.json", "w"), indent=1)
for L in lines: print(f"{L['start']:6.2f}-{L['end']:6.2f} {L['id']}")
print("total", round(total, 2))
