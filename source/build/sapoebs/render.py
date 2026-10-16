# Frame renderer + parallel full render.  usage:
#   python3 render.py still OUTDIR t1 t2 ...      -> PNG previews
#   python3 render.py video OUT.mp4 [workers]      -> silent 1080p30 master
import sys, os, subprocess, multiprocessing as mp
import numpy as np, cv2
from lib import *
from scenes import SCENES, SC, energy

TOTAL = 2333
_G = {}
def init():
    _G["bg"] = make_bg()[..., ::-1].copy(); _G["net"] = Net()
    rs = np.random.RandomState(5); _G["noise"] = [rs.randint(-3, 4, (H, W, 1)).astype(np.int16) for _ in range(6)]
    _G["logo"] = np.asarray(LOGO(46)).astype(np.float32) / 255

def frame(i):
    t = i / FPS; bg, net = _G["bg"], _G["net"]
    shift = (30 * math.sin(t * .33), 18 * math.cos(t * .27))
    f = np.clip(bg.astype(np.int16) + net.draw(t, energy(t), shift), 0, 255).astype(np.uint8)
    L = np.zeros((H, W, 4), np.float32); G = np.zeros((H, W, 3), np.uint8); O = np.zeros((H, W, 3), np.uint8)
    zoom = 1.0
    for n, (k, (a, b)) in enumerate(SC.items()):
        if not (a <= t < b or (k == "J" and t >= a)): continue            # plain hard cuts: no fades, slides or wipes
        c = Ctx(L, G, O); SCENES[k](c, t)
        u = clamp((t - a) / (b - a)); zoom = 1.0 + .03 * (u if n % 2 == 0 else 1 - u)
    f = glow_add(f, G, 1.0)
    al = L[..., 3:4]; f = (f.astype(np.float32) * (1 - al) + L[..., [2, 1, 0]] * 255).astype(np.uint8)
    f = glow_add(f, O, 1.0)
    if zoom != 1.0:
        M = np.float32([[zoom, 0, -(zoom - 1) * W / 2], [0, zoom, -(zoom - 1) * H / 2]]); f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR)
    f = np.clip(f.astype(np.int16) + _G["noise"][i % 6], 0, 255).astype(np.uint8)
    # fixed brand furniture: logo top-right (entire film) + event tag top-left
    la = E(pr(t, .1, .5)); lg = _G["logo"]; h, w = lg.shape[:2]; x, y = W - 64 - w, 46
    reg = f[y:y + h, x:x + w].astype(np.float32); a2 = lg[..., 3:4] * la
    f[y:y + h, x:x + w] = (reg * (1 - a2) + lg[..., [2, 1, 0]] * 255 * a2).astype(np.uint8)
    tag = np.asarray(T("SOLIXEMPOWER 2026", "m", "Bold", 15, (110, 140, 205), 4)).astype(np.float32) / 255
    th, tw_ = tag.shape[:2]; a3 = tag[..., 3:4] * la * .9
    f[52:52 + th, 64:64 + tw_] = (f[52:52 + th, 64:64 + tw_].astype(np.float32) * (1 - a3) + tag[..., [2, 1, 0]] * 255 * a3).astype(np.uint8)
    f = (f.astype(np.float32) * E(pr(t, 0, .35))).astype(np.uint8) if t < .4 else f
    return f

def work(args):
    s, e, out = args
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "13", "-preset", "fast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(s, e): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait(); return out

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        init(); os.makedirs(sys.argv[2], exist_ok=True)
        for tt in sys.argv[3:]:
            cv2.imwrite(f"{sys.argv[2]}/t{float(tt):06.2f}.png", frame(int(round(float(tt) * FPS))))
    else:
        out = sys.argv[2]; nw = int(sys.argv[3]) if len(sys.argv) > 3 else 4; tmp = out + ".parts"; os.makedirs(tmp, exist_ok=True)
        step = 120; jobs = [(s, min(TOTAL, s + step), f"{tmp}/p{s:05d}.mp4") for s in range(0, TOTAL, step)]
        with mp.Pool(nw, initializer=init) as pool:
            for r in pool.imap(work, jobs): print("done", r, flush=True)
        open(f"{tmp}/list.txt", "w").write("".join(f"file '{os.path.abspath(j[2])}'\n" for j in jobs))
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", out], check=True)
