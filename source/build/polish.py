# Trim edges (keep breath room), then broadcast-style voice chain via ffmpeg.
import sys, os, glob, subprocess, numpy as np, soundfile as sf
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
CHAIN = ("highpass=f=75,equalizer=f=220:t=q:w=1.0:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.2,"
         "equalizer=f=9000:t=h:w=1:g=1.5,deesser=i=0.35,"
         "acompressor=threshold=-21dB:ratio=2.4:attack=6:release=140:makeup=2.2,"
         "aecho=0.92:0.9:19|37:0.07|0.045,aresample=44100")
for f in sorted(glob.glob(f"{src}/*.wav")):
    a, sr = sf.read(f)
    env = np.abs(a) > 0.012
    idx = np.where(env)[0]
    a = a[max(0, idx[0] - int(0.06 * sr)): min(len(a), idx[-1] + int(0.18 * sr))]
    fade = int(0.02 * sr); a[:fade] *= np.linspace(0, 1, fade); a[-fade:] *= np.linspace(1, 0, fade)
    tmp = f"{dst}/_tmp.wav"; sf.write(tmp, a, sr)
    out = f"{dst}/{os.path.basename(f)}"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-af", CHAIN, out], check=True)
    os.remove(tmp)
    print(os.path.basename(f), round(sf.info(out).duration, 2))
