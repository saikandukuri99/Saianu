"""EAI Healthcare: approved video on a white, light healthcare background.

Starts from the approved video (graph icon + swapped six pillars) and swaps
only the background: the pink gradient becomes white with a low-opacity
healthcare pattern (medical crosses, ECG line, molecule network) in Solix
colours. Content, timing, voice-over and music are unchanged. Text that sat
on the old background moves to the Solix palette:
dark text -> #30267b, grey text -> #0088cf, reds -> #ee2424.

Background swap per pixel (difference keying, keeps edges, fades, shadows):
    out = c + (1 - a) * (new_bg - old_bg)

usage: python3 hc_white.py VIDEO ANALYSIS_JSON OUT.mp4 [WIDTHxHEIGHT] [only_frames]
"""
import json
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hc_alpha import PILLAR_ZONE, read_frames  # noqa: E402
from hc_final import ICON_BOX, IconFix  # noqa: E402,F401
from hc_matte import degrid, matte_frame  # noqa: E402
from hc_pillars import Pillars  # noqa: E402

W0, H0, FPS = 1920, 1080, 30
GOV, PIL = 2, 3
NAVY = np.array([0x30, 0x26, 0x7b], np.float32)
BLUE = np.array([0x00, 0x88, 0xcf], np.float32)
RED = np.array([0xee, 0x24, 0x24], np.float32)
# screenshots / 3D renders keep their own colours (no text recolour inside)
PROTECT = {2: [(735, 330, 1185, 900)], 8: [(880, 180, 1920, 920)],
           5: [(100, 170, 1720, 1000)], 6: [(60, 170, 1220, 1000)], 7: [(60, 170, 1220, 1000)]}


def _plus(img, cx, cy, s, col, th):
    cv2.line(img, (cx - s, cy), (cx + s, cy), col, th, cv2.LINE_AA)
    cv2.line(img, (cx, cy - s), (cx, cy + s), col, th, cv2.LINE_AA)


def make_background(w=W0, h=H0, seed=7):
    """White base + soft Solix tints + low-opacity healthcare motifs (float32 RGB)."""
    k = 2
    W, H = w * k, h * k
    rng = np.random.default_rng(seed)
    bg = np.full((H, W, 3), 255.0, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    def glow(cx, cy, r, col, amt):
        g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))[..., None] * amt
        return bg * (1 - g) + col * g

    bg = glow(W * 0.95, H * 0.05, W * 0.28, BLUE, 0.10)
    bg = glow(W * 0.02, H * 1.0, W * 0.30, NAVY, 0.07)
    bg = glow(W * 0.55, H * 1.05, W * 0.22, RED, 0.035)

    ink = np.zeros((H, W), np.float32)      # navy motif layer
    blu = np.zeros((H, W), np.float32)      # blue motif layer
    red = np.zeros((H, W), np.float32)      # ECG line
    # sparse medical crosses
    for _ in range(46):
        x, y = int(rng.uniform(0, W)), int(rng.uniform(0, H))
        s = int(rng.uniform(10, 22) * k)
        _plus(blu if rng.random() < 0.6 else ink, x, y, s, 1.0, max(2, int(2.2 * k)))
    # molecule / network clusters (hexagon-ish rings with nodes)
    for cx, cy, sc in [(0.12, 0.22, 1.0), (0.86, 0.78, 1.2), (0.62, 0.12, 0.8), (0.30, 0.85, 0.9)]:
        cx, cy = cx * W, cy * H
        pts = []
        for i in range(6):
            ang = np.pi / 3 * i + 0.3
            pts.append((cx + np.cos(ang) * 70 * k * sc, cy + np.sin(ang) * 70 * k * sc))
        pts = np.int32(pts)
        cv2.polylines(blu, [pts], True, 1.0, int(2 * k), cv2.LINE_AA)
        for i, (px, py) in enumerate(pts):
            cv2.circle(blu, (int(px), int(py)), int(7 * k), 1.0, -1, cv2.LINE_AA)
            if i % 2 == 0:
                ex = int(px + (px - cx) * 0.8)
                ey = int(py + (py - cy) * 0.8)
                cv2.line(ink, (int(px), int(py)), (ex, ey), 1.0, int(2 * k), cv2.LINE_AA)
                cv2.circle(ink, (ex, ey), int(9 * k), 1.0, int(2 * k), cv2.LINE_AA)
    # ECG heartbeat line across the lower part
    base_y = int(H * 0.9)
    path, x = [], 0
    while x < W:
        path += [(x, base_y), (x + 90 * k, base_y), (x + 105 * k, base_y - 18 * k), (x + 120 * k, base_y),
                 (x + 135 * k, base_y + 22 * k), (x + 150 * k, base_y - 80 * k), (x + 168 * k, base_y + 40 * k),
                 (x + 185 * k, base_y), (x + 230 * k, base_y), (x + 250 * k, base_y - 24 * k),
                 (x + 275 * k, base_y)]
        x += 420 * k
    cv2.polylines(red, [np.int32(path)], False, 1.0, int(3 * k), cv2.LINE_AA)
    # faint dotted grid
    for gy in range(0, H, 48 * k):
        for gx in range(0, W, 48 * k):
            cv2.circle(ink, (gx, gy), int(1.6 * k), 0.5, -1, cv2.LINE_AA)

    bg = bg * (1 - ink[..., None] * 0.07) + NAVY * ink[..., None] * 0.07
    bg = bg * (1 - blu[..., None] * 0.08) + BLUE * blu[..., None] * 0.08
    bg = bg * (1 - red[..., None] * 0.10) + RED * red[..., None] * 0.10
    return cv2.resize(bg, (w, h), interpolation=cv2.INTER_AREA)


def recolor(out, a, newbg, scene, cards_fill=None):
    """Move text on the background to the Solix palette, keeping anti-aliasing."""
    h, w = a.shape
    protect = np.zeros((h, w), bool)
    for x0, y0, x1, y1 in PROTECT.get(scene, []):
        protect[y0:y1, x0:x1] = True
    if cards_fill is not None:
        protect |= cv2.dilate(cards_fill.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    lum = out.mean(axis=2)
    lb = newbg.mean(axis=2)
    chroma = out.max(axis=2) - out.min(axis=2)
    neutral = (chroma < 40) & ~protect & (a > 0.05)
    # dark ink -> navy, mid grey -> blue (coverage from luminance, keeps edges)
    k_dark = np.clip((lb - lum) / np.maximum(lb - 25.0, 1), 0, 1)
    region = cv2.dilate((neutral & (lum < 90)).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & neutral
    ink_grey = cv2.erode(np.where(region, lum, 255).astype(np.float32), np.ones((5, 5), np.uint8)) > 80
    col = np.where(ink_grey[..., None], BLUE, NAVY)
    rec = newbg + (col - newbg) * k_dark[..., None]
    grey = neutral & ~region & (lum > 90) & (lum < 190)
    k_g = np.clip((lb - lum) / np.maximum(lb - 120.0, 1), 0, 1)
    recg = newbg + (BLUE - newbg) * k_g[..., None]
    out = np.where(region[..., None], rec, out)
    out = np.where(grey[..., None], recg, out)
    # leftover pink glows / drop shadows from the old background -> soft navy shadow
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    glow = (r > 190) & (r - g > 8) & (np.abs(g - b) < 22) & (g > 110) & (a < 0.995)
    if cards_fill is not None:
        glow &= ~cv2.erode(cards_fill.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    sh = np.clip((r - g) / 90.0, 0, 1)[..., None] * 0.22
    out = np.where(glow[..., None], newbg * (1 - sh) + NAVY * sh, out)
    # reds -> Solix red (hue-only, keeps shading)
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    reds = (r > 150) & (r - g > 90) & (r - b > 80) & ~protect
    kr = np.clip((255 - g) / (255 - RED[1]), 0, 1)[..., None]
    out = np.where(reds[..., None], newbg + (RED - newbg) * kr, out)
    return out


_P = _FIX = _BG = None


def _init(ref):
    global _P, _FIX, _BG
    _P = Pillars(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets_hc", "six_pillars.png"),
                 original=True)
    _FIX = IconFix(ref)
    _BG = make_background()


def process(job):
    k, fr, cuts, pfade = job
    t = k / FPS
    c = fr.astype(np.float32)
    scene = int(np.searchsorted(cuts, k, side="right") - 1)
    if scene == GOV:
        if k < int(14.45 * FPS):
            dx, score = _FIX.locate(c)
            if score > 0.45:
                c = _FIX.apply(c, dx)
        else:
            c = _FIX.apply(c)
    c = degrid(c)
    cards = scene in (5, 6, 7)
    _, a, b, fill = matte_frame(c, cards, scene == 8, return_fill=True)
    # slow drift of the pattern (parallax feel), same everywhere
    dx = int(round(10 * np.sin(t / 12.0)))
    newbg = np.roll(_BG, dx, axis=1)
    out = c + (1 - a[..., None]) * (newbg - b)
    out = recolor(out, a, newbg, scene, fill if cards else None)
    if scene == PIL:
        o = pfade[k - cuts[PIL]]
        pm = _P.render(t) * (o if t > 31.5 else 1.0)
        y0, y1 = PILLAR_ZONE
        new = pm[..., :3] + newbg * (1 - pm[..., 3:4])
        for i in range(y0, y1):
            wgt = min(1.0, (i - y0 + 1) / 13, (y1 - i) / 13)
            out[i] = out[i] * (1 - wgt) + new[i] * wgt
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    video, ana_path, out = sys.argv[1:4]
    size = sys.argv[4] if len(sys.argv) > 4 else "3840x2160"
    only = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else None
    W, H = map(int, size.split("x"))
    ana = json.load(open(ana_path))
    cuts = ana["cuts"]
    pfade = ana["fades"]["3"]
    ref = None
    for k, fr in enumerate(read_frames(video)):
        if k == int(16.0 * FPS):
            ref = fr.astype(np.float32)
            break
    if only is not None:  # test frames -> PNGs
        _init(ref)
        for k, fr in enumerate(read_frames(video)):
            if k in only:
                cv2.imwrite(f"{out}_{k}.png", process((k, fr, cuts, pfade))[:, :, ::-1])
            if k > max(only):
                break
        return
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W0}x{H0}", "-r", str(FPS),
        "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a", "-vf", f"scale={W}:{H}:flags=lanczos",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    jobs = ((k, fr, cuts, pfade) for k, fr in enumerate(read_frames(video)))
    with Pool(4, initializer=_init, initargs=(ref,)) as pool:
        for k, img in enumerate(pool.imap(process, jobs, chunksize=2)):
            enc.stdin.write(img.tobytes())
            if k % 300 == 0:
                print("frame", k, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
