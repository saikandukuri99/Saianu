# Rotating 3D holographic human (point-cloud) for the Patient 360 graphic.
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

rng = np.random.default_rng(3)


def _ellipsoid(c, r, n):
    u = rng.normal(size=(n, 3))
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    return np.asarray(c) + u * np.asarray(r)


def _capsule(a, b, r0, r1, n):
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = rng.random(n)
    axis = b - a
    L = np.linalg.norm(axis)
    ax = axis / L
    tmp = np.array([1.0, 0, 0]) if abs(ax[0]) < 0.9 else np.array([0, 0, 1.0])
    e1 = np.cross(ax, tmp); e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    th = rng.random(n) * 2 * math.pi
    r = r0 + (r1 - r0) * t
    return a + np.outer(t, axis) + (np.cos(th) * r)[:, None] * e1 + (np.sin(th) * r)[:, None] * e2


@lru_cache(None)
def body_points():
    P = []
    P.append(_ellipsoid((0, 1.63, 0), (0.095, 0.118, 0.105), 520))           # head
    P.append(_capsule((0, 1.47, 0), (0, 1.53, 0), 0.05, 0.048, 120))         # neck
    P.append(_ellipsoid((0, 1.29, 0), (0.185, 0.2, 0.105), 1300))           # chest
    P.append(_ellipsoid((0, 1.04, 0), (0.15, 0.17, 0.095), 900))            # abdomen
    P.append(_ellipsoid((0, 0.88, 0), (0.165, 0.1, 0.1), 600))              # pelvis
    for sx in (-1, 1):
        P.append(_ellipsoid((sx * 0.2, 1.41, 0), (0.07, 0.06, 0.065), 200))  # shoulder
        P.append(_capsule((sx * 0.22, 1.39, 0), (sx * 0.27, 1.1, 0.01), 0.048, 0.04, 420))
        P.append(_capsule((sx * 0.27, 1.1, 0.01), (sx * 0.3, 0.84, 0.05), 0.04, 0.032, 380))
        P.append(_ellipsoid((sx * 0.305, 0.78, 0.06), (0.03, 0.06, 0.025), 120))
        P.append(_capsule((sx * 0.09, 0.84, 0), (sx * 0.1, 0.46, 0.01), 0.075, 0.055, 700))
        P.append(_capsule((sx * 0.1, 0.46, 0.01), (sx * 0.1, 0.08, -0.01), 0.052, 0.04, 620))
        P.append(_ellipsoid((sx * 0.1, 0.04, 0.05), (0.04, 0.03, 0.09), 140))
    return np.concatenate(P)


@lru_cache(None)
def organ_points():
    heart = _ellipsoid((0.035, 1.3, 0.03), (0.045, 0.05, 0.04), 260) * 1.0
    return heart


def hologram(t, height=430, alpha=1.0):
    """RGBA sprite of the rotating holographic body (+ scan ring + platform)."""
    W = int(height * 0.75)
    H = height + 60
    pts = body_points()
    ang = t * 0.55
    ca, sa = math.cos(ang), math.sin(ang)
    x = pts[:, 0] * ca + pts[:, 2] * sa
    z = -pts[:, 0] * sa + pts[:, 2] * ca
    y = pts[:, 1]
    sc = height / 1.8
    px = (W / 2 + x * sc).astype(int)
    py = (H - 40 - y * sc).astype(int)
    depth = (z - z.min()) / (np.ptp(z) + 1e-6)
    inten = 0.25 + 0.75 * depth
    buf = np.zeros((H, W), float)
    ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
    np.add.at(buf, (py[ok], px[ok]), inten[ok])
    # scan band moving up and down
    scan_y = (0.5 + 0.5 * math.sin(t * 1.3)) * 1.75
    band = np.exp(-((y - scan_y) ** 2) / (2 * 0.02 ** 2))
    np.add.at(buf, (py[ok], px[ok]), (band * 2.5)[ok])
    buf = np.clip(buf / 0.9, 0, 1)
    core = Image.fromarray((buf * 255).astype(np.uint8))
    glow = core.filter(ImageFilter.GaussianBlur(5))
    lum = np.clip(np.asarray(core, float) * 1.0 + np.asarray(glow, float) * 1.8, 0, 255)
    rgb = np.zeros((H, W, 4), np.uint8)
    # hologram blue-cyan with white-hot core
    k = lum / 255
    rgb[..., 0] = np.clip(60 + 190 * k ** 1.5, 0, 255)
    rgb[..., 1] = np.clip(150 + 105 * k, 0, 255)
    rgb[..., 2] = 255
    rgb[..., 3] = np.clip(lum * alpha, 0, 255).astype(np.uint8)
    im = Image.fromarray(rgb, "RGBA")
    # heart pulse (red)
    hp = organ_points()
    hx = hp[:, 0] * ca + hp[:, 2] * sa
    hz = -hp[:, 0] * sa + hp[:, 2] * ca
    pulse = 1 + 0.12 * max(0, math.sin(t * 6.0)) ** 4
    hpx = (W / 2 + hx * sc * pulse).astype(int); hpy = (H - 40 - hp[:, 1] * sc).astype(int)
    hb = np.zeros((H, W), float)
    ok2 = (hpx >= 0) & (hpx < W) & (hpy >= 0) & (hpy < H)
    np.add.at(hb, (hpy[ok2], hpx[ok2]), 1.0)
    hb = Image.fromarray((np.clip(hb / 1.2, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))
    red = Image.new("RGBA", (W, H), (255, 70, 70, 0))
    red.putalpha(hb.point(lambda v: int(min(255, v * 2.2 * alpha))))
    im = Image.alpha_composite(im, red)
    # platform rings
    d = ImageDraw.Draw(im)
    for i, rr in enumerate((0.42, 0.33, 0.24)):
        rw, rh = W * rr, W * rr * 0.22
        a_ = int((110 - i * 25) * alpha)
        d.ellipse((W / 2 - rw, H - 40 - rh, W / 2 + rw, H - 40 + rh), outline=(90, 190, 255, a_), width=2)
    return im
