"""Render frames of scenes 3-4 with the two fixes into chunks/NNNNN.mkv (ffv1). Resumable.
usage: hc_chunk.py WORKER_INDEX N_WORKERS"""
import os, subprocess, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hc_alpha import swap_rupee, analyse, W, H, FPS
from hc_matte import background_plate
from hc_pillars import Pillars
SRC = "/mnt/user-data/uploads/Solix_EAI_Healthcare_FemaleVO_HyperBeat_1080p.mp4"
ZONE = (190, 1066)
ana = analyse(SRC, "wk"); cuts = ana["cuts"]
fades = {int(k): v for k, v in ana["fades"].items()}
s3, e3, s4, e4 = cuts[2], cuts[3], cuts[3], cuts[4]
P = Pillars("assets_hc/six_pillars.png")
def frames(a, b):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a / FPS:.6f}", "-i", SRC, "-frames:v", str(b - a),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    while True:
        x = p.stdout.read(W * H * 3)
        if len(x) < W * H * 3: break
        yield np.frombuffer(x, np.uint8).reshape(H, W, 3)
def fix(k, fr):
    t = k / FPS
    c = fr.astype(np.float32)
    if s3 <= k < e3:
        o = fades[2][k - s3]
        if o >= 0.999: c = swap_rupee(c)
        elif o >= 0.06:
            b0 = background_plate(c); cu = np.clip(b0 + (c - b0) / o, 0, 255)
            c = b0 + (swap_rupee(cu) - b0) * o
    else:
        b = background_plate(c); c[ZONE[0]:ZONE[1]] = b[ZONE[0]:ZONE[1]]
        d = fades[3][k - s4] if t > 31.5 else 1.0
        pm = P.render(t) * d
        c = pm[..., :3] + c * (1 - pm[..., 3:4])
    return np.clip(c, 0, 255).astype(np.uint8)
wi, nw = int(sys.argv[1]), int(sys.argv[2])
STEP = 60
os.makedirs("chunks", exist_ok=True)
for j, a in enumerate(range(s3, e4, STEP)):
    if j % nw != wi: continue
    b = min(a + STEP, e4); out = f"chunks/{a:05d}.mkv"
    if os.path.exists(out): continue
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "ffv1", "-f", "matroska", out + ".tmp"], stdin=subprocess.PIPE)
    n = 0
    for i, fr in enumerate(frames(a, b)):
        enc.stdin.write(fix(a + i, fr).tobytes()); n += 1
    enc.stdin.close(); enc.wait()
    assert n == b - a, (a, n)
    os.rename(out + ".tmp", out); print("chunk", a, b, flush=True)
print("WORKER DONE", wi, flush=True)
