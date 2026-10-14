"""EAI Healthcare cut -> per-scene RGB+Alpha clips for Premiere.

usage: python3 hc_alpha.py VIDEO OUT_DIR WORK_DIR [scene numbers...]

* Background (gradient, blobs, grid) is removed (hc_matte.py).
* Scene 3: the Revenue Cycle Intelligence rupee icon becomes a trending-up graph.
* Scene 4: the six-pillar diagram is replaced by the supplied artwork with
  pillars 4 and 5 swapped (hc_pillars.py); title, logo and progress bar kept.
* Clips are cut at the quietest frame of each transition and are contiguous:
  laid end to end they rebuild the exact original 78.73 s timeline.
"""
import json
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hc_matte import background_plate, degrid  # noqa: E402
from hc_clean import full_matte  # noqa: E402

# per-scene: photo/3D render box kept as an image; soft oval for the globe
PROTECT = {2: (735, 330, 1185, 900)}
DARK = os.environ.get("HC_DARK") == "1"          # full video on the Solix dark-blue background
DARK_BG = np.array([0x30, 0x26, 0x7b], np.float32)
ELLIPSE = {8: (1410, 555, 510, 345, 90)}

W, H, FPS = 1920, 1080, 30
ORANGE = np.array([249, 113, 20], np.float32)

# name, transition window that ends the scene, un-fade region (None = off), fill card holes
SCENES = [
    ("01_Intro_EAI_Healthcare_Platform", (2.8, 4.3), None, False),
    ("02_Fragmented_Data_to_Outcomes", (9.8, 11.2), (40, 40, 1540, 250), False),
    ("03_AI_Ready_Unified_Governance", (18.8, 19.8), (40, 40, 1540, 260), False),
    ("04_Six_Pillars", (33.4, 34.7), (40, 40, 1540, 200), False),
    ("05_AI_Patient_360_Title", (36.5, 37.5), None, False),
    ("06_Multi_Agentic_Every_Specialty", (50.4, 51.6), (40, 40, 1540, 150), True),
    ("07_Findings_with_Evidence", (59.0, 60.3), (40, 40, 1540, 150), True),
    ("08_Clinician_Validation", (66.8, 68.2), (40, 40, 1540, 150), True),
    ("09_Built_for_Global_Healthcare", (73.8, 75.2), (40, 330, 900, 700), False),
    ("10_End_EAI_Healthcare_Platform", None, None, False),
]
PILLAR_ZONE = (190, 1066)   # rows replaced by the new diagram in scene 4


def read_frames(video, scale=1):
    w, h = W // scale, H // scale
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"scale={w}:{h}:flags=area",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)


# ---------------------------------------------------------------- analysis
def analyse(video, work):
    """Low-res pass: transition cut frames and per-scene fade (opacity) curves."""
    path = f"{work}/analysis.json"
    if os.path.exists(path):
        return json.load(open(path))
    q = 4
    energy, regions = [], {}
    for fr in read_frames(video, q):
        c = fr.astype(np.float32)
        b = background_plate(c)
        d = cv2.GaussianBlur(np.abs(c - b).sum(axis=2), (0, 0), 1.5)
        d[: 130 // q, 1550 // q:] = 0
        d[1060 // q:] = 0
        energy.append(float(d.mean()))
        for i, sc in enumerate(SCENES):
            if sc[2]:
                x0, y0, x1, y1 = (v // q for v in sc[2])
                regions.setdefault(i, []).append(float(d[y0:y1, x0:x1].mean()))
    n = len(energy)
    energy = np.array(energy)
    cuts = [0]
    for _, win, _, _ in SCENES[:-1]:
        a, b = int(win[0] * FPS), int(win[1] * FPS)
        cuts.append(a + int(np.argmin(energy[a:b])))
    cuts.append(n)
    fades = {}
    for i, sc in enumerate(SCENES):
        s, e = cuts[i], cuts[i + 1]
        if not sc[2]:
            fades[i] = [1.0] * (e - s)
            continue
        r = np.array(regions[i][s:e])
        ref = np.percentile(r, 90)
        o = np.clip(r / max(ref, 1e-3), 0, 1)
        o = np.convolve(np.pad(o, 2, mode="edge"), np.ones(5) / 5, mode="valid")
        o[o > 0.94] = 1.0
        fades[i] = [float(v) for v in o]
    res = {"cuts": cuts, "fades": fades, "frames": n}
    json.dump(res, open(path, "w"))
    return res


# ---------------------------------------------------------------- scene 3
def _trend_icon(size):
    """Anti-aliased 'trending up' line icon (white mask), size x size."""
    ss = 4
    S = size * ss
    m = np.zeros((S, S), np.uint8)
    k = S / 24.0
    pts1 = np.int32([[22, 7], [13.5, 15.5], [8.5, 10.5], [2, 17]]) * 0 + np.int32(
        np.array([[22, 7], [13.5, 15.5], [8.5, 10.5], [2, 17]]) * k)
    pts2 = np.int32(np.array([[16, 7], [22, 7], [22, 13]]) * k)
    th = max(1, int(round(2.1 * k)))
    cv2.polylines(m, [pts1], False, 255, th, cv2.LINE_AA)
    cv2.polylines(m, [pts2], False, 255, th, cv2.LINE_AA)
    for p in list(pts1) + list(pts2):
        cv2.circle(m, tuple(int(v) for v in p), th // 2, 255, -1, cv2.LINE_AA)
    return cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def swap_rupee(c):
    x0, y0, x1, y1 = 1372, 500, 1490, 620
    roi = c[y0:y1, x0:x1]
    r, g, b = roi[..., 0], roi[..., 1], roi[..., 2]
    orange = (r - b > 120) & (g > 60) & (g < 175) & (r > 150)
    if orange.sum() < 200:
        return c
    ys, xs = np.nonzero(orange)
    cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
    rad = (ys.max() - ys.min()) / 2
    yy, xx = np.mgrid[0:roi.shape[0], 0:roi.shape[1]]
    inner = np.hypot(yy - cy, xx - cx) < rad * 0.72
    ring = inner & orange
    circ = np.median(roi[ring], axis=0) if ring.sum() > 50 else ORANGE
    glyph = inner & (g > circ[1] + 18)
    if glyph.sum() < 10:
        return c
    o = np.clip((np.percentile(g[glyph], 95) - circ[1]) / (255 - ORANGE[1]), 0, 1)
    mask = cv2.dilate(glyph.astype(np.uint8), np.ones((3, 3), np.uint8))
    fixed = cv2.inpaint(np.clip(roi, 0, 255).astype(np.uint8), mask, 4, cv2.INPAINT_TELEA).astype(np.float32)
    fixed[inner] = fixed[inner] * 0 + circ  # flat circle colour under the new glyph
    size = int(round(rad * 1.08))
    ic = _trend_icon(size)
    gy, gx = int(round(cy - size / 2)), int(round(cx - size / 2))
    sub = fixed[gy:gy + size, gx:gx + size]
    sub += ic[: sub.shape[0], : sub.shape[1], None] * o * (255 - ORANGE)
    out = c.copy()
    out[y0:y1, x0:x1] = np.where(inner[..., None], fixed, roi)
    return out


# ---------------------------------------------------------------- workers
_P = None


def _init():
    global _P
    from hc_pillars import Pillars
    _P = Pillars(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets_hc", "six_pillars.png"), dark=DARK)


def process(job):
    """Returns (straight RGBA uint8, preview RGB uint8 over the original background)."""
    fr, scene, t, o, diag_o = job
    c = degrid(fr.astype(np.float32))
    if scene == 2 and o >= 0.999:
        c = swap_rupee(c)
    fill = SCENES[scene][3]
    outl = scene == 8  # badges in "Built for global healthcare"
    if o < 0.06:
        rgb = c
        a = np.zeros(c.shape[:2], np.float32)
        b = background_plate(c)
    elif o < 0.999:
        b0 = background_plate(c)
        cu = np.clip(b0 + (c - b0) / o, 0, 255)
        if scene == 2:
            cu = swap_rupee(cu)  # also while the scene fades (no rupee flash at the end)
        rgb, a, _ = full_matte(cu, fill, outl, PROTECT.get(scene), ELLIPSE.get(scene), dark=DARK)
        a = a * o
        b = b0
    else:
        rgb, a, b = full_matte(c, fill, outl, PROTECT.get(scene), ELLIPSE.get(scene), dark=DARK)
    if scene == 3:
        y0, y1 = PILLAR_ZONE
        a[y0:y1] = 0
        pm = _P.render(t) * diag_o
        prem = np.dstack([rgb * a[..., None], a])
        prem = pm + prem * (1 - pm[..., 3:4])
        a = prem[..., 3]
        rgb = np.where(a[..., None] > 1e-3, prem[..., :3] / np.maximum(a, 1e-3)[..., None], 0)
    a8 = np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8)
    rgb8 = np.clip(rgb, 0, 255).astype(np.uint8)
    rgb8[a8 == 0] = 0
    rgba = np.dstack([rgb8, a8])
    under = DARK_BG if DARK else b
    prev = (rgb * a[..., None] + under * (1 - a[..., None])).clip(0, 255).astype(np.uint8)
    return rgba, prev


def run_scene(video, out, work, i, ana, pool):
    name = SCENES[i][0]
    s, e = ana["cuts"][i], ana["cuts"][i + 1]
    fades = ana["fades"][str(i)] if isinstance(next(iter(ana["fades"])), str) else ana["fades"][i]
    diag = fades if i == 3 else None
    mov = f"{out}/alpha/{name}.mov"
    os.makedirs(f"{out}/alpha", exist_ok=True)
    os.makedirs(f"{work}/preview", exist_ok=True)
    enc = None if DARK else subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", mov], stdin=subprocess.PIPE)
    pre = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                            f"{work}/preview/{name}.mp4"], stdin=subprocess.PIPE)

    def jobs():
        for k, fr in enumerate(read_frames(video)):
            if k < s:
                continue
            if k >= e:
                break
            t = k / FPS
            o = fades[k - s]
            d = 1.0
            if diag is not None and t > 31.5:
                d = o
            yield (fr, i, t, o, d)

    for rgba, prev in pool.imap(process, jobs(), chunksize=2):
        if enc:
            enc.stdin.write(rgba.tobytes())
        pre.stdin.write(prev.tobytes())
    if enc:
        enc.stdin.close(); enc.wait()
    pre.stdin.close(); pre.wait()
    print(f"{name}: frames {s}-{e - 1} ({(e - s) / FPS:.3f}s)", flush=True)


def main():
    video, out, work = sys.argv[1:4]
    only = [int(x) - 1 for x in sys.argv[4:]] or list(range(len(SCENES)))
    os.makedirs(work, exist_ok=True)
    ana = analyse(video, work)
    print("cuts (s):", [round(c / FPS, 3) for c in ana["cuts"]], flush=True)
    with Pool(4, initializer=_init) as pool:
        for i in only:
            run_scene(video, out, work, i, ana, pool)


if __name__ == "__main__":
    main()
