"""New six-pillar diagram for the EAI Healthcare cut, built from the supplied
artwork (source/assets_hc/six_pillars.png) with pillar 4 and pillar 5 swapped:
AI Clinical Intelligence moves to the upper-right slot and Intelligent
Imaging & Radiology to the middle-right slot.

Animated like the original scene: centre logo, then the pillars one by one,
then each pillar is highlighted (grows slightly, label turns red) while the
narration names it.
"""
import cv2
import numpy as np

NAVY = np.array([0x30, 0x26, 0x7b], np.float32)   # Solix navy  #30267b
RED = np.array([0xee, 0x24, 0x24], np.float32)    # Solix red   #ee2424
BLUE = np.array([0x00, 0x88, 0xcf], np.float32)   # Solix blue  #0088cf

CENTER = (770, 455)          # centre logo in the source artwork
R_LOGO, R_HUB = 110, 172     # red disk, disk incl. ring + dots
R_FILL, R_OUT, R_GROUP = 79, 87, 104

# slot -> circle centre and label rect in the source artwork
SLOTS = {
    "warehouse": ((536, 781), (110, 750, 448, 810)),
    "federated": ((401, 453), (12, 395, 308, 512)),
    "p360":      ((542, 129), (110, 68, 450, 195)),
    "imaging":   ((1009, 128), (1104, 68, 1571, 195)),
    "clinical":  ((1140, 452), (1236, 395, 1530, 512)),
    "models":    ((1009, 776), (1104, 722, 1540, 842)),
}
# after the swap: which content sits in which slot
PLACE = {"warehouse": "warehouse", "federated": "federated", "p360": "p360",
         "clinical": "imaging", "imaging": "clinical", "models": "models"}

# reveal order / times and highlight windows (seconds, absolute video time)
REVEAL = [("warehouse", 20.45), ("federated", 20.65), ("p360", 20.85),
          ("clinical", 21.05), ("imaging", 21.25), ("models", 21.45)]
HIGHLIGHT = {"warehouse": (23.45, 24.75), "federated": (24.85, 26.20),
             "p360": (26.30, 27.85), "clinical": (27.90, 28.85),
             "imaging": (28.90, 30.00), "models": (30.05, 32.90)}
LOGO_IN = (19.95, 20.55)

SCALE = 0.948
FRAME_CENTER = (960.0, 590.0)


def _unmix_white(img):
    """Minimal-alpha unmix of artwork drawn on white -> premultiplied RGBA."""
    inv = 255.0 - img
    a = inv.max(axis=2) / 255.0
    return np.dstack([img - 255.0 * (1 - a)[..., None], a])  # premult rgb = C - (1-a)*255


def _disk(h, w, cx, cy, r, soft=1.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    return np.clip((r - d) / soft + 0.5, 0, 1)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def ease_back(x):
    x = np.clip(x, 0, 1)
    c1 = 1.4
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


class Pillars:
    def __init__(self, path, dark=False):
        self.dark = dark
        art = cv2.imread(path)[:, :, ::-1].astype(np.float32)
        h, w = art.shape[:2]
        self.h, self.w = h, w
        pm = _unmix_white(art)
        # solid discs: circles (light-blue fill + white rim) and the red logo
        for (cx, cy), _ in SLOTS.values():
            d = _disk(h, w, cx, cy, R_OUT)
            pm = pm * (1 - d[..., None]) + np.dstack([art, np.ones((h, w))]) * d[..., None]
        d = _disk(h, w, *CENTER, R_LOGO + 1)
        pm = pm * (1 - d[..., None]) + np.dstack([art, np.ones((h, w))]) * d[..., None]
        self.pm = pm
        hub = _disk(h, w, *CENTER, R_HUB, 3)
        self.hub = pm * hub[..., None]
        lab = np.zeros((h, w), np.uint8)
        for _, (x0, y0, x1, y1) in SLOTS.values():
            lab[y0:y1, x0:x1] = 1
        # every remaining pixel belongs to the nearest circle (lines, glows)
        rest = pm * (1 - hub[..., None]) * (1 - lab[..., None])
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        names = list(SLOTS)
        dist = np.stack([np.hypot(xx - SLOTS[n][0][0], yy - SLOTS[n][0][1]) for n in names])
        near = dist.argmin(0)
        self.shell, self.icon, self.label = {}, {}, {}
        for i, n in enumerate(names):
            (cx, cy), (x0, y0, x1, y1) = SLOTS[n]
            own = (near == i).astype(np.float32)
            inner = _disk(h, w, cx, cy, R_FILL - 1, 1.5)
            self.shell[n] = rest * (own * (1 - inner))[..., None]          # rim, glow, line
            ic = art[cy - R_FILL:cy + R_FILL, cx - R_FILL:cx + R_FILL].copy()
            # icon glyphs (dark blue on light blue) -> Solix blue, keeping anti-aliasing
            fillc = np.array([234, 246, 255], np.float32)
            src = np.array([21, 70, 160], np.float32)
            k = np.clip(((fillc - ic) * (fillc - src)).sum(axis=2) / ((fillc - src) ** 2).sum(), 0, 1)
            ic = fillc * (1 - k[..., None]) + BLUE * k[..., None]
            self.icon[n] = (ic, inner[cy - R_FILL:cy + R_FILL, cx - R_FILL:cx + R_FILL].copy())
            crop = art[y0:y1, x0:x1]
            a = np.clip((255.0 - crop[..., 0]) / (255.0 - 21.0), 0, 1)
            a[(crop.min(axis=2) > 200)] = 0
            ys, xs = np.nonzero(a > 0.05)
            self.label[n] = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            self.label_off = getattr(self, "label_off", {})
            self.label_off[n] = (x0 + xs.min() - cx, y0 + ys.min() + (ys.max() - ys.min()) / 2 - cy)

    # ---- placement helpers -------------------------------------------------
    def _M(self, scale, pivot):
        """Affine: scale about a pivot in artwork coords, then place in frame."""
        px, py = pivot
        k = SCALE
        fx = FRAME_CENTER[0] + (px - CENTER[0]) * k
        fy = FRAME_CENTER[1] + (py - CENTER[1]) * k
        s = k * scale
        return np.float32([[s, 0, fx - px * s], [0, s, fy - py * s]])

    @staticmethod
    def _over(dst, src_pm):
        a = src_pm[..., 3:4]
        dst[..., :3] = src_pm[..., :3] + dst[..., :3] * (1 - a)
        dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)

    def _warp(self, pm, M, size):
        return cv2.warpAffine(pm, M, size, flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))

    def render(self, t, size=(1920, 1080)):
        """Premultiplied RGBA float frame of the diagram at time t."""
        out = np.zeros((size[1], size[0], 4), np.float32)
        # highlight glows go underneath everything
        hl = {}
        for n, (a, b) in HIGHLIGHT.items():
            hl[n] = smooth((t - a) / 0.22) * smooth((b - t) / 0.22)
        u = (t - LOGO_IN[0]) / (LOGO_IN[1] - LOGO_IN[0])
        if u > 0:
            s = 0.6 + 0.4 * ease_back(u)
            hub = self._warp(self.hub * smooth(u * 1.4), self._M(s, CENTER), size)
            self._over(out, hub)
        for slot, t0 in REVEAL:
            v = (t - t0) / 0.38
            if v <= 0:
                continue
            fade = smooth(v)
            content = PLACE[slot]
            (cx, cy), _ = SLOTS[slot]
            h = hl[slot]
            if h > 0:
                g = np.zeros((self.h, self.w, 4), np.float32)
                disk = cv2.GaussianBlur(_disk(self.h, self.w, cx, cy, R_OUT * 1.15), (0, 0), 14)
                g[..., 3] = disk * 0.45 * h
                g[..., :3] = RED * g[..., 3:4]
                self._over(out, self._warp(g * fade, self._M(1.0, (cx, cy)), size))
            sc = (0.75 + 0.25 * ease_back(v)) * (1 + 0.10 * h)
            self._over(out, self._warp(self.shell[slot] * fade, self._M(sc, (cx, cy)), size))
            ic_rgb, ic_a = self.icon[content]
            ic = np.dstack([ic_rgb * ic_a[..., None], ic_a]) * fade
            k = SCALE * sc
            M = np.float32([[k, 0, 0], [0, k, 0]])
            fx = FRAME_CENTER[0] + (cx - CENTER[0]) * SCALE - R_FILL * k
            fy = FRAME_CENTER[1] + (cy - CENTER[1]) * SCALE - R_FILL * k
            M[0, 2], M[1, 2] = fx, fy
            self._over(out, self._warp(ic, M, size))
            # label: left/right anchored like the artwork, vertically centred on the circle
            la = self.label[content]
            ox, _ = self.label_off[slot]
            base = np.float32([255, 255, 255]) if self.dark else NAVY
            col = base * (1 - h) + RED * h
            lab = np.dstack([la[..., None] * col, la]) * smooth(v * 0.9)
            right_side = cx > CENTER[0]
            slide = (1 - smooth(v)) * 18 * (1 if right_side else -1)
            if right_side:
                lx = FRAME_CENTER[0] + (cx + ox - CENTER[0]) * SCALE + slide
            else:
                own_w = self.label[slot].shape[1]
                lx = FRAME_CENTER[0] + (cx + ox + own_w - CENTER[0]) * SCALE - la.shape[1] * SCALE + slide
            ly = FRAME_CENTER[1] + (cy - CENTER[1]) * SCALE - la.shape[0] * SCALE / 2
            M = np.float32([[SCALE, 0, lx], [0, SCALE, ly]])
            self._over(out, self._warp(lab, M, size))
        return out
