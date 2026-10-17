"""EAI Healthcare - rebuilt on a clean white background.

Every scene is rebuilt from layers instead of keyed frame by frame:
* text, icons, lines and badges come from one cleaned, fully-built frame per
  scene (Solix colours: #30267b text, #ee2424 highlights), split into
  elements; each element fades in/out exactly when it does in the approved
  video (its visibility is measured from that video);
* the "fragmented data" hub, rings, connector curves and particles are drawn
  fresh; the six-pillar diagram comes from the supplied artwork (Clinical
  Intelligence <-> Imaging & Radiology swapped);
* screenshots and the globe are placed whole each frame (re-lit to white);
* background: white with a low-opacity Solix-blue (#0088cf) heartbeat line;
* progress bar redrawn; voice-over and music copied unchanged.

usage: python3 hc_rebuild.py VIDEO ANALYSIS_JSON LAYER_DIR OUT.mp4 [WxH] [test_frames]
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
from hc_matte import background_plate, degrid  # noqa: E402
from hc_pillars import Pillars  # noqa: E402

W, H, FPS = 1920, 1080, 30
TOTAL = 78.8
NAVY = np.float32([0x30, 0x26, 0x7b])
BLUE = np.float32([0x00, 0x88, 0xcf])
RED = np.float32([0xee, 0x24, 0x24])
HERE = os.path.dirname(os.path.abspath(__file__))

HUB = (960, 590)
# zones rebuilt separately (removed from the static layer)
ZONES = {2: [("rect", 488, 280, 1380, 960)],
         4: [("rect", 0, PILLAR_ZONE[0], W, PILLAR_ZONE[1])],
         9: [("ellipse", 1410, 555, 520, 360)]}
CARDS = (6, 7, 8)
GLOBE = (1410, 555, 520, 360, 90)


# ------------------------------------------------------------------ background
def heartbeat_path(y, amp, x0=-40, x1=W + 40, period=430, offset=0):
    pts, x = [], x0 - offset
    while x < x1:
        seq = [(0, 0), (120, 0), (140, -0.18), (158, 0), (176, 0.25), (194, -1.0), (214, 0.55),
               (232, 0), (282, 0), (306, -0.28), (334, 0), (period, 0)]
        pts += [(x + dx, y + dy * amp) for dx, dy in seq]
        x += period
    return np.float32(pts)


def make_background():
    k = 2
    big = np.zeros((H * k, W * k), np.float32)
    soft = np.zeros_like(big)
    for y, amp, off, wgt in [(0.80, 95, 0, 1.0), (0.22, 55, 210, 0.45)]:
        p = (heartbeat_path(y * H, amp, offset=off) * k).astype(np.int32)
        layer = np.zeros_like(big)
        cv2.polylines(layer, [p], False, 1.0, int(3.2 * k), cv2.LINE_AA)
        big = np.maximum(big, layer * wgt)
        g = np.zeros_like(big)
        cv2.polylines(g, [p], False, 1.0, int(14 * k), cv2.LINE_AA)
        soft = np.maximum(soft, cv2.GaussianBlur(g, (0, 0), 12 * k) * wgt)
    line = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    glow = cv2.resize(soft, (W, H), interpolation=cv2.INTER_AREA)
    bg = np.full((H, W, 3), 255.0, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    tint = np.exp(-(((xx - W) ** 2 + yy ** 2) / (2 * 700.0 ** 2)))[..., None] * 0.05
    bg = bg * (1 - tint) + BLUE * tint
    a = (line * 0.13 + glow * 0.05)[..., None]
    return bg * (1 - a) + BLUE * a, line


def pulse(bg_line, t):
    """A soft travelling highlight along the heartbeat line."""
    x = (t * 260) % (W + 600) - 300
    xx = np.arange(W, dtype=np.float32)
    m = np.exp(-((xx - x) ** 2) / (2 * 110.0 ** 2))[None, :]
    return (bg_line * m * 0.22)[..., None]


# ------------------------------------------------------------------ layers
def load_layers(ldir):
    out = {}
    for s in range(1, 11):
        rgb = np.load(f"{ldir}/s{s}_rgb.npy").astype(np.float32)
        a = np.load(f"{ldir}/s{s}_a.npy").astype(np.float32) / 255
        a[1058:] = 0                                      # old progress bar
        r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        pinkish = (r_ > 180) & (r_ - g_ > 15) & (np.abs(g_ - b_) < 30) & (a < 0.9)
        a[pinkish] = 0                                    # old soft shadows
        n_, lab_, st_, _ = cv2.connectedComponentsWithStats((a > 0.05).astype(np.uint8), connectivity=8)
        amax = np.zeros(n_, np.float32)
        np.maximum.at(amax, lab_.ravel(), a.ravel())
        a[((st_[:, 4] < 40) & (amax < 0.7))[lab_]] = 0  # specks
        for z in ZONES.get(s, []):
            if z[0] == "rect":
                a[z[2]:z[4], z[1]:z[3]] = 0
            else:
                m = np.zeros(a.shape, np.uint8)
                cv2.ellipse(m, (z[1], z[2]), (z[3], z[4]), 0, 0, 360, 1, -1)
                a[m > 0] = 0
        if s in CARDS:
            x0, y0, x1, y1 = card_rect(a, ldir, s)
            a[y0 - 30:y1 + 60, x0 - 40:x1 + 40] = 0
        out[s] = (rgb, a)
    return out


def card_rect(a_unused, ldir, s):
    a = np.load(f"{ldir}/s{s}_a.npy").astype(np.float32) / 255
    m = (a > 0.97).astype(np.uint8)
    m[:180] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((25, 25), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    i = 1 + int(np.argmax(st[1:, 4]))
    x, y, w, h, _ = st[i]
    return int(x), int(y), int(x + w), int(y + h)


def elements(a):
    """Split a layer into elements (text lines, icons, arrows, badges)."""
    m = (a > 0.15).astype(np.uint8)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_RECT, (31, 13)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    lab[a <= 0.02] = 0
    return n, lab, st


# ------------------------------------------------------------------ visibility
def measure(video, cuts, layers, cache):
    """Per element visibility curve, measured from the approved video."""
    if os.path.exists(cache):
        return {int(k): {int(e): v for e, v in d.items()} for k, d in json.load(open(cache)).items()}
    q = 4
    info = {}
    for s in range(1, 11):
        rgb, a = layers[s]
        n, lab, st = elements(a)
        info[s] = (n, cv2.resize(lab.astype(np.int32), (W // q, H // q), interpolation=cv2.INTER_NEAREST),
                   cv2.resize(a, (W // q, H // q), interpolation=cv2.INTER_AREA))
    curves = {s: {} for s in range(1, 11)}
    raw = {s: [] for s in range(1, 11)}
    for k, fr in enumerate(read_frames(video, q)):
        s = int(np.searchsorted(cuts, k, side="right"))
        if s < 1 or s > 10:
            continue
        n, lab, aq = info[s]
        c = fr.astype(np.float32)
        b = background_plate(c)
        d = np.abs(c - b).sum(axis=2) * aq
        sums = np.bincount(lab.ravel(), weights=d.ravel(), minlength=n)
        raw[s].append(sums)
    for s in range(1, 11):
        arr = np.array(raw[s])                    # frames x elements
        ref = np.percentile(arr, 92, axis=0)
        v = np.clip(arr / np.maximum(ref, 1e-3), 0, 1)
        v[v > 0.93] = 1.0
        for e in range(1, arr.shape[1]):
            col = v[:, e]
            col = np.convolve(np.pad(col, 2, mode="edge"), np.ones(5) / 5, mode="valid")
            curves[s][e] = [round(float(x), 3) for x in col]
    json.dump(curves, open(cache, "w"))
    return curves


# ------------------------------------------------------------------ hub scene
def rounded_square(img, alpha, cx, cy, size, col, op, r=4):
    s = size / 2
    x0, y0, x1, y1 = int(cx - s), int(cy - s), int(cx + s), int(cy + s)
    x0c, y0c = max(x0, 0), max(y0, 0)
    x1c, y1c = min(x1, W), min(y1, H)
    if x1c <= x0c or y1c <= y0c:
        return
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    rr = min(r, (x1 - x0) // 3)
    cv2.rectangle(m, (rr, 0), (x1 - x0 - rr - 1, y1 - y0 - 1), 1.0, -1)
    cv2.rectangle(m, (0, rr), (x1 - x0 - 1, y1 - y0 - rr - 1), 1.0, -1)
    for cx_, cy_ in [(rr, rr), (x1 - x0 - rr - 1, rr), (rr, y1 - y0 - rr - 1), (x1 - x0 - rr - 1, y1 - y0 - rr - 1)]:
        cv2.circle(m, (cx_, cy_), rr, 1.0, -1, cv2.LINE_AA)
    m = m[y0c - y0:y1c - y0, x0c - x0:x1c - x0] * op
    sub = img[y0c:y1c, x0c:x1c]
    sub[:] = sub * (1 - m[..., None]) + col * m[..., None]


class Hub:
    def __init__(self):
        ic = cv2.imread(os.path.join(HERE, "..", "assets", "icon.png"), cv2.IMREAD_UNCHANGED)
        ic = cv2.cvtColor(ic, cv2.COLOR_BGRA2RGBA).astype(np.float32)
        self.logo = cv2.resize(ic, (252, 252), interpolation=cv2.INTER_AREA)
        rng = np.random.default_rng(11)
        self.parts = []
        for _ in range(58):
            ang = rng.uniform(0, 2 * np.pi)
            rad = rng.uniform(175, 390)
            size = rng.choice([12, 16, 22, 28, 34, 40], p=[.12, .18, .2, .2, .18, .12])
            kind = rng.choice(["red", "pink", "grey", "white"], p=[.36, .3, .2, .14])
            self.parts.append((ang, rad, size, kind, rng.uniform(0, 6.28), rng.uniform(0.04, 0.12)))
        self.left_y = [365, 469, 573, 677, 781, 885]
        self.right_y = [455, 620, 785]

    @staticmethod
    def bezier(p0, p1, p2, p3, n=80):
        t = np.linspace(0, 1, n)[:, None]
        return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)

    def draw(self, img, t, vis_left, vis_hub, vis_right):
        lay = np.zeros((H, W), np.float32)
        cx, cy = HUB
        if vis_left > 0:
            for i, y in enumerate(self.left_y):
                pts = self.bezier(np.float32([495, y]), np.float32([650, y]),
                                  np.float32([700, cy + (y - cy) * 0.15]), np.float32([cx - 150, cy]))
                cv2.polylines(lay, [np.int32(pts * 4)], False, vis_left, 4, cv2.LINE_AA, shift=2)
        if vis_right > 0:
            for y in self.right_y:
                pts = self.bezier(np.float32([cx + 150, cy]), np.float32([1220, cy]),
                                  np.float32([1250, y]), np.float32([1370, y]))
                cv2.polylines(lay, [np.int32(pts * 4)], False, vis_right, 4, cv2.LINE_AA, shift=2)
        a = (lay * 0.75)[..., None]
        img[:] = img * (1 - a) + RED * a
        if vis_hub <= 0:
            return
        # rings
        ring = np.zeros((H, W), np.float32)
        cv2.circle(ring, (cx * 4, cy * 4), 160 * 4, 1.0, 5, cv2.LINE_AA, shift=2)
        cv2.circle(ring, (cx * 4, cy * 4), 200 * 4, 1.0, 4, cv2.LINE_AA, shift=2)
        a = (ring * 0.35 * vis_hub)[..., None]
        img[:] = img * (1 - a) + RED * a
        glow = np.zeros((H, W), np.float32)
        cv2.circle(glow, (cx, cy), 135, 1.0, -1)
        glow = cv2.GaussianBlur(glow, (0, 0), 28) * 0.18 * vis_hub
        img[:] = img * (1 - glow[..., None]) + RED * glow[..., None]
        # particles orbit slowly and settle in as the hub appears
        for ang, rad, size, kind, ph, sp in self.parts:
            a_ = ang + t * sp
            r_ = rad * (0.55 + 0.45 * vis_hub)        # fly out from the hub as it appears
            px = cx + np.cos(a_) * r_
            py = cy + np.sin(a_) * r_ * 0.80 + 6 * np.sin(t * 1.3 + ph)
            if not (650 < px < 1270 and 320 < py < 930):
                continue                              # keep clear of the title and labels
            col, op = {"red": (RED, 1.0), "pink": (RED, 0.42), "grey": (np.float32([150, 160, 176]), 0.9),
                       "white": (np.float32([255, 255, 255]), 1.0)}[kind]
            if kind == "white":
                rounded_square(img, None, px + 2, py + 3, size + 4, np.float32([200, 205, 220]), 0.35 * vis_hub)
            rounded_square(img, None, px, py, size, col, op * vis_hub)
        # logo disc
        s = vis_hub ** 0.7
        size = int(252 * (0.7 + 0.3 * s))
        lg = cv2.resize(self.logo, (size, size), interpolation=cv2.INTER_AREA)
        x0, y0 = cx - size // 2, cy - size // 2
        la = lg[..., 3:4] / 255 * vis_hub
        sub = img[y0:y0 + size, x0:x0 + size]
        sub[:] = sub * (1 - la) + lg[..., :3] * la


# ------------------------------------------------------------------ placed images
def shadow(img, x0, y0, x1, y1, op):
    m = np.zeros((H, W), np.float32)
    cv2.rectangle(m, (x0 + 6, y0 + 14), (x1 - 6, y1 + 10), 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), 18) * 0.16 * op
    img[:] = img * (1 - m[..., None]) + NAVY * m[..., None]


def relit(c):
    b = background_plate(c)
    return c * (255.0 / np.maximum(b, 1.0))


def place_card(img, c_rel, rect, op):
    x0, y0, x1, y1 = rect
    shadow(img, x0, y0, x1, y1, op)
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    r = 14
    cv2.rectangle(m, (r, 2), (x1 - x0 - r - 1, y1 - y0 - 3), 1.0, -1)
    cv2.rectangle(m, (2, r), (x1 - x0 - 3, y1 - y0 - r - 1), 1.0, -1)
    for cx, cy in [(r, r), (x1 - x0 - r - 1, r), (r, y1 - y0 - r - 1), (x1 - x0 - r - 1, y1 - y0 - r - 1)]:
        cv2.circle(m, (cx, cy), r - 2, 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 0.6)[..., None] * op
    crop = np.clip(c_rel[y0:y1, x0:x1], 0, 255)
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - m) + crop * m
    # thin border
    cv2.rectangle(img, (x0 + 1, y0 + 1), (x1 - 2, y1 - 2), (226, 230, 240), 1, cv2.LINE_AA) if op > 0.95 else None


def place_globe(img, c_rel, newbg, op):
    cx, cy, rx, ry, fe = GLOBE
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    m = np.clip((1.0 - r) * min(rx, ry) / fe, 0, 1)
    m = (m * m * (3 - 2 * m))[..., None] * op
    img[:] = img * (1 - m) + np.clip(c_rel, 0, 255) * m


# ------------------------------------------------------------------ frame
_G = {}


def _init(ldir, curves, cuts, rects):
    _G["layers"] = load_layers(ldir)
    _G["els"] = {s: elements(_G["layers"][s][1]) for s in range(1, 11)}
    _G["curves"] = curves
    _G["cuts"] = cuts
    _G["rects"] = rects
    _G["bg"], _G["line"] = make_background()
    _G["hub"] = Hub()
    _G["pil"] = Pillars(os.path.join(HERE, "..", "assets_hc", "six_pillars.png"), original=True)


def scene_vis(s, k, boxes):
    """Max visibility of the elements whose centre falls inside any box."""
    n, lab, st = _G["els"][s]
    i = k - _G["cuts"][s - 1]
    best = 0.0
    for e in range(1, n):
        x, y, w, h, _ = st[e]
        cx, cy = x + w / 2, y + h / 2
        for x0, y0, x1, y1 in boxes:
            if x0 <= cx <= x1 and y0 <= cy <= y1 and e in _G["curves"][s]:
                best = max(best, _G["curves"][s][e][min(i, len(_G["curves"][s][e]) - 1)])
    return best


def render(job):
    k, fr = job
    t = k / FPS
    cuts = _G["cuts"]
    s = int(np.searchsorted(cuts, k, side="right"))
    img = _G["bg"].copy()
    p = pulse(_G["line"], t)
    img = img * (1 - p) + BLUE * p
    rgb, a = _G["layers"][s]
    n, lab, st = _G["els"][s]
    i = k - cuts[s - 1]
    vis = np.zeros(n, np.float32)
    for e, cv in _G["curves"][s].items():
        if e < n:
            vis[e] = cv[min(i, len(cv) - 1)]
    va = a * vis[lab]

    if s == 2:
        vl = scene_vis(2, k, [(40, 300, 480, 950)])
        vr = scene_vis(2, k, [(1370, 380, 1900, 880)])
        vt = scene_vis(2, k, [(400, 90, 1550, 300)])
        _G["hub"].draw(img, t, vl, min(1.0, max(vl, vt)), vr)
    if s in CARDS or s == 9:
        c = degrid(fr.astype(np.float32))
        c_rel = relit(c)
        if s in CARDS:
            rect = _G["rects"][s]
            x0, y0, x1, y1 = rect
            ref = _G["card_ref"].get(s)
            m = np.abs(c[y0 + 10:y1 - 10, x0 + 10:x1 - 10] - 245).mean()
            op = float(np.clip(_card_op(c, rect), 0, 1))
            place_card(img, c_rel, rect, op)
        else:
            op = scene_vis(9, k, [(40, 300, 900, 800)])
            op = max(op, float(np.clip(_globe_op(c), 0, 1)))
            place_globe(img, c_rel, _G["bg"], op)

    img = img * (1 - va[..., None]) + rgb * va[..., None]

    if s == 4:
        pm = _G["pil"].render(t)
        o = scene_vis(4, k, [(0, 0, 1600, 190)])
        pm = pm * (o if t > 31.5 else 1.0)
        img = pm[..., :3] + img * (1 - pm[..., 3:4])

    # progress bar
    bw = int(W * min(t / TOTAL, 1.0))
    img[1074:1080, :bw] = RED
    return np.clip(img, 0, 255).astype(np.uint8)


def _card_op(c, rect):
    """Card opacity: how far the card interior is from the old background."""
    x0, y0, x1, y1 = rect
    b = background_plate(c)
    inner = (slice(y0 + 20, y1 - 20), slice(x0 + 20, x1 - 20))
    d = np.abs(c[inner] - b[inner]).sum(axis=2).mean()
    db = np.abs(255.0 - b[inner]).sum(axis=2).mean()
    return d / max(db, 1.0) if db > 6 else 1.0


def _globe_op(c):
    cx, cy, rx, ry, _ = GLOBE
    b = background_plate(c)
    reg = c[cy - 150:cy + 150, cx - 250:cx + 250]
    return np.abs(reg - b[cy - 150:cy + 150, cx - 250:cx + 250]).sum(axis=2).mean() / 60.0


def main():
    video, ana_path, ldir, out = sys.argv[1:5]
    size = sys.argv[5] if len(sys.argv) > 5 else "3840x2160"
    test = [int(x) for x in sys.argv[6].split(",")] if len(sys.argv) > 6 else None
    OW, OH = map(int, size.split("x"))
    cuts = json.load(open(ana_path))["cuts"]
    layers = load_layers(ldir)
    curves = measure(video, cuts, layers, f"{ldir}/curves.json")
    rects = {s: card_rect(None, ldir, s) for s in CARDS}
    if test:
        _init(ldir, curves, cuts, rects)
        _G["card_ref"] = {}
        for k, fr in enumerate(read_frames(video)):
            if k in test:
                cv2.imwrite(f"{out}_{k}.png", render((k, fr))[:, :, ::-1])
            if k > max(test):
                break
        return
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a", "-vf", f"scale={OW}:{OH}:flags=lanczos",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)

    def init2(*a):
        _init(*a)
        _G["card_ref"] = {}
    with Pool(4, initializer=init2, initargs=(ldir, curves, cuts, rects)) as pool:
        for k, img in enumerate(pool.imap(render, ((k, fr) for k, fr in enumerate(read_frames(video))),
                                          chunksize=2)):
            enc.stdin.write(img.tobytes())
            if k % 300 == 0:
                print("frame", k, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
