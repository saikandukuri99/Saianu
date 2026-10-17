"""v13 (white ECG) video -> Solix dark blue (#30267b) background.

Smooth, threshold-free background swap: every pixel is treated as ink over
white, c = a*K + (1-a)*255, and moved onto the new background with
    out = c + (1 - a) * (D - 255)
which reproduces each element exactly (no grain). Dark text/lines (invisible
on dark blue) become white with the same coverage; dark icon discs become
Solix blue #0088cf; white glyphs inside discs and the white screenshot cards
stay white (cards fade with their own opacity). Audio copied unchanged.

usage: python3 hc_darkblue.py VIDEO OUT.mp4 [WxH] [test_frames]
"""
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hc_alpha import read_frames  # noqa: E402

FPS = 30
D = np.float32([0x30, 0x26, 0x7b])
BLUE = np.float32([0x00, 0x88, 0xcf])
WHITE = np.float32([255, 255, 255])
# screenshot cards in the v13 timeline: (t0, t1, rect)
CARDS = [(38.5, 53.0, (239, 195, 1681, 832)), (52.9, 61.6, (99, 195, 1161, 874)),
         (61.5, 69.7, (99, 195, 1161, 874))]
_REF = {}


def card_op(c, rect, key):
    x0, y0, x1, y1 = rect
    strip = 255.0 - c[y0 + 4:y0 + 28, x0 + 10:x1 - 10].min(axis=2)
    v = float(strip.mean())
    ref = _REF.get(key, 0.0)
    return float(np.clip(v / ref, 0, 1)) if ref > 1 else 1.0


def process(job):
    k, fr = job
    t = k / FPS
    c = fr.astype(np.float32)
    h, w = c.shape[:2]
    m = c.min(axis=2)
    kmin = cv2.erode(m, np.ones((7, 7), np.uint8))
    a = np.clip(np.maximum(255.0 - m - 5.0, 0) / np.maximum(255.0 - kmin, 160.0), 0, 1)
    # ink colour estimate (per channel local min ~ the element's colour)
    K = np.dstack([cv2.erode(c[..., i], np.ones((5, 5), np.uint8)) for i in range(3)])
    lum = K.mean(axis=2)
    chroma = K.max(axis=2) - K.min(axis=2)

    # enclosed light regions inside solid shapes (glyphs, bolt, badges) keep white
    solid = (a > 0.6).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(1 - solid, connectivity=4)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        x, y, ww, hh, area = st[i]
        if area < 9000 and x > 0 and y > 0 and x + ww < w and y + hh < h and hh < 140:
            keep[i] = True
    hole = keep[lab]
    # only holes inside round discs (icon discs, logo) stay white - never letter counters
    if hole.any():
        ns, sl, ss, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
        nh, hl, _, _ = cv2.connectedComponentsWithStats(hole.astype(np.uint8), connectivity=4)
        rl = cv2.dilate(sl.astype(np.float32), np.ones((5, 5), np.uint8)).astype(np.int32)
        ok = np.zeros(nh, bool)
        par = np.zeros(nh, np.int64)
        np.maximum.at(par, hl.ravel(), rl.ravel())
        for j in range(1, nh):
            p_ = par[j]
            if p_ <= 0:
                continue
            x, y, ww, hh, area = ss[p_]
            if not (30 <= ww <= 300 and 0.8 < ww / max(hh, 1) < 1.25):
                continue
            comp = (sl[y:y + hh, x:x + ww] == p_).astype(np.uint8)
            cn, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            filled = max(cv2.contourArea(q) for q in cn)
            hole_area = float((hl == j).sum())
            q = max(cn, key=cv2.contourArea)
            solidity = filled / max(cv2.contourArea(cv2.convexHull(q)), 1)
            ok[j] = (0.85 < filled / (np.pi * ww * hh / 4) < 1.15 and area > 0.62 * filled
                     and solidity > 0.94 and hole_area < 0.2 * filled)   # glyphs, not letter counters
        hole &= ok[hl]

    out = c + (1 - a[..., None]) * (D - 255.0)
    out = np.where(hole[..., None], c, out)

    # dark neutral ink: thin -> white text, thick round -> Solix blue disc
    reddish = (K[..., 0] - K[..., 2] > 60)
    ink = ((((lum < 110) & (chroma < 90)) | ((lum < 175) & (chroma < 40))) & ~reddish) & (a > 0.0) & ~hole
    dist = cv2.distanceTransform((ink & (a > 0.5)).astype(np.uint8), cv2.DIST_L2, 3)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats((ink & (a > 0.3)).astype(np.uint8), connectivity=8)
    thick = np.zeros(n2, np.float32)
    np.maximum.at(thick, lab2.ravel(), dist.ravel())
    roundd = np.zeros(n2, bool)
    for j in range(1, n2):
        x, y, ww, hh, area = st2[j]
        if not (45 <= ww <= 140 and 0.85 < ww / max(hh, 1) < 1.18):
            continue
        comp = (lab2[y:y + hh, x:x + ww] == j).astype(np.uint8)
        cn, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = max(cv2.contourArea(q) for q in cn)
        ell = np.pi * ww * hh / 4
        # a solid disc: round outline and mostly ink (letters are thin strokes)
        # letters O/D: counter is one big hole (~40%); icon discs: ink with small glyph gaps
        roundd[j] = 0.88 < filled / ell < 1.12 and 0.62 * filled < area and (filled - area) < 0.3 * filled \
            and ww >= 55
    disc = roundd[lab2] & ink & (lum < 120)
    text = ink & ~disc
    ink_col = np.where((lum < 120)[..., None], WHITE, np.float32([214, 218, 232]))
    out = np.where(text[..., None], D * (1 - a[..., None]) + ink_col * a[..., None], out)
    out = np.where(disc[..., None], D * (1 - a[..., None]) + BLUE * a[..., None], out)

    # screenshot cards: exact un-blend from white with the card's own opacity
    for i, (t0, t1, rect) in enumerate(CARDS):
        if t0 <= t < t1:
            x0, y0, x1, y1 = rect
            o = card_op(c, rect, i)
            sub = c[y0:y1, x0:x1]
            out[y0:y1, x0:x1] = sub + (1 - o) * (D - 255.0)
    return np.clip(out, 0, 255).astype(np.uint8)


def init_refs(video):
    want = {i: int(((t0 + t1) / 2) * FPS) for i, (t0, t1, _) in enumerate(CARDS)}
    for k, fr in enumerate(read_frames(video)):
        for i, kk in want.items():
            if k == kk:
                x0, y0, x1, y1 = CARDS[i][2]
                c = fr.astype(np.float32)
                _REF[i] = float((255.0 - c[y0 + 4:y0 + 28, x0 + 10:x1 - 10].min(axis=2)).mean())
        if k > max(want.values()):
            break


def _init(refs):
    _REF.update(refs)


def main():
    video, out = sys.argv[1:3]
    size = sys.argv[3] if len(sys.argv) > 3 else "1920x1080"
    test = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
    OW, OH = map(int, size.split("x"))
    init_refs(video)
    if test:
        for k, fr in enumerate(read_frames(video)):
            if k in test:
                cv2.imwrite(f"{out}_{k}.png", process((k, fr))[:, :, ::-1])
            if k > max(test):
                break
        return
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS),
        "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a", "-vf", f"scale={OW}:{OH}:flags=lanczos",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4, initializer=_init, initargs=(dict(_REF),)) as pool:
        for k, img in enumerate(pool.imap(process, enumerate(read_frames(video)), chunksize=2)):
            enc.stdin.write(img.tobytes())
            if k % 300 == 0:
                print("frame", k, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
