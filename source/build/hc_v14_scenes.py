"""v13 white-ECG video with four scenes rebuilt from the supplied, final artwork
and animated in sync with the voice-over:

  3.50-10.53  From fragmented data      (assets_hc/fragmented_data_rgba.png)
 10.53-19.33  Unified governance        (assets_hc/unified_governance.webp)
 19.33-36.10  Six pillars               (assets_hc/six_pillars.png, = supplied 12.png)
 69.50-76.45  Built for global health   (assets_hc/global_network.webp)

Only the diagram area of each scene is replaced: titles, header, logo, ECG
background, progress bar, transitions and audio stay exactly as they are.
Each artwork is split into layers (items, connectors, hub, ...) that build in
one by one on the narration and fade out with the original scene transition.

usage: python3 hc_v14_scenes.py VIDEO OUT.mp4 [test_frames]
"""
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hc_alpha import read_frames  # noqa: E402
import hc_pillars  # noqa: E402

ASSETS = os.path.join(HERE, "..", "assets_hc")
FPS, W, H = 30, 1920, 1080


# ---------------------------------------------------------------- helpers
def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = np.clip(x, 0, 1)
    return 1 - (1 - x) ** 3


def ease_back(x, c1=1.5):
    x = np.clip(x, 0, 1)
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def load_rgba(path, amax=255.0):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED).astype(np.float32)
    rgb = im[..., 2::-1]
    a = np.clip(im[..., 3] / amax, 0, 1)
    return np.dstack([rgb * a[..., None], a])          # premultiplied


def place(pm, s, ox, oy):
    """Scale premultiplied artwork by s and place its origin at (ox, oy) on the canvas."""
    M = np.float32([[s, 0, ox], [0, s, oy]])
    flags = cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC
    out = cv2.warpAffine(pm, M, (W, H), flags=flags, borderValue=(0, 0, 0, 0))
    out[..., 3] = np.clip(out[..., 3], 0, 1)
    out[..., :3] = np.clip(out[..., :3], 0, 255 * out[..., 3:4])
    return out


class Layer:
    """A cut-out of the placed artwork; drawn with scale/offset/opacity/reveal."""

    def __init__(self, canvas, mask, pivot, reveal=None):
        mask = mask.astype(np.float32)
        ys, xs = np.nonzero(mask > 0.002)
        if len(xs) == 0:
            self.pm = None
            return
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        self.box = (x0, y0)
        self.pm = canvas[y0:y1, x0:x1] * mask[y0:y1, x0:x1, None]
        self.pivot = pivot
        self.reveal = None if reveal is None else reveal[y0:y1, x0:x1]

    def draw(self, out, op=1.0, s=1.0, dx=0.0, dy=0.0, rev=None, soft=0.06, angle=0.0):
        if self.pm is None or op <= 0.002:
            return
        pm = self.pm * op
        if rev is not None:
            k = smooth((rev - self.reveal) / soft + 0.5)
            pm = pm * k[..., None]
        x0, y0 = self.box
        px, py = self.pivot
        if s == 1.0 and angle == 0.0 and abs(dx) < 1e-3 and abs(dy) < 1e-3:
            h, w = pm.shape[:2]
            reg = out[y0:y0 + h, x0:x0 + w]
            reg[...] = pm[..., :3] + reg * (1 - pm[..., 3:4])
            return
        R = cv2.getRotationMatrix2D((px - x0, py - y0), angle, s)
        R[0, 2] += x0 + dx
        R[1, 2] += y0 + dy
        h, w = pm.shape[:2]
        cn = R @ np.float32([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]]).T
        bx0, by0 = max(int(np.floor(cn[0].min())) - 2, 0), max(int(np.floor(cn[1].min())) - 2, 0)
        bx1, by1 = min(int(np.ceil(cn[0].max())) + 2, W), min(int(np.ceil(cn[1].max())) + 2, H)
        if bx1 <= bx0 or by1 <= by0:
            return
        R[0, 2] -= bx0
        R[1, 2] -= by0
        wp = cv2.warpAffine(pm, R, (bx1 - bx0, by1 - by0), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        reg = out[by0:by1, bx0:bx1]
        reg[...] = wp[..., :3] + reg * (1 - wp[..., 3:4])


def bezier(p0, p1, p2, p3, n=90):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.float32(p) for p in (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def draw_curve(out, pts, u, col, width=2, dot=False):
    """Draw the first fraction u of a polyline, anti-aliased."""
    k = max(2, int(round(u * len(pts))))
    p = pts[:k]
    x0, y0 = np.floor(p.min(0)).astype(int) - 8
    x1, y1 = np.ceil(p.max(0)).astype(int) + 8
    x0, y0 = max(x0, 0), max(y0, 0)
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    q = np.round((p - (x0, y0)) * 8).astype(np.int32)
    cv2.polylines(m, [q], False, 255, width, cv2.LINE_AA, shift=3)
    if dot:
        cv2.circle(m, tuple(q[-1]), 5 * 8, 255, -1, cv2.LINE_AA, shift=3)
    a = (m.astype(np.float32) / 255.0)[..., None]
    reg = out[y0:y1, x0:x1]
    reg[...] = reg * (1 - a[:reg.shape[0], :reg.shape[1]]) + col * a[:reg.shape[0], :reg.shape[1]]


def band_masks(h, w, centers, x0, x1, ys, xs):
    """Split a column of list items into one mask per row (nearest row centre)."""
    c = np.float32(centers)
    near = np.abs(ys[..., None] - c).argmin(-1)
    inx = (xs >= x0) & (xs < x1)
    return [((near == i) & inx) for i in range(len(centers))]


def arrows_to_rows(art, band, centers, colors, x_item, x_hub, y_hub):
    """Assign connector pixels to their item row: each arrow has its item's colour;
    rows with similar colours are told apart by the expected path position."""
    h, w = art.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rgb = art[..., :3] / np.maximum(art[..., 3:4], 1e-3)
    f = np.clip((xx - x_item) / (x_hub - x_item), 0, 1)
    cost = []
    for yc, col in zip(centers, colors):
        yexp = yc + (y_hub - yc) * f * 0.7
        cost.append(np.linalg.norm(rgb - np.float32(col), axis=2) + 0.9 * np.abs(yy - yexp))
    rows = np.argmin(np.stack(cost), 0)
    rows[~band | (art[..., 3] < 0.003)] = -1
    return rows


# ---------------------------------------------------------------- scene 1: fragmented data
class Fragmented:
    T0, T1, FADE = 3.50, 10.53, (10.03, 10.50)
    S, OX, OY = 1.08, 42.0, 123.0
    LEFT = [222, 328, 437, 545, 653, 763]
    RIGHT = [311, 480, 643]
    LOGO = (856.0, 452.0)
    SOLID_LOGO = False
    NODE = (711.0, 455.0)
    L_START = [(338, 226), (469, 332), (360, 436), (398, 545), (425, 653), (482, 749)]
    R_END = [311.0, 478.0, 640.0]
    LINE = np.float32([240, 45, 30])
    L_IN = [3.95 + 0.2 * i for i in range(6)]
    R_IN = [6.75, 7.35, 7.95]          # "unlocking insights that drive better patient outcomes"
    REGION_Y = 296

    def __init__(self):
        art = load_rgba(os.path.join(ASSETS, "fragmented_data_rgba.png"))
        h, w = art.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        art[(yy < 190) & (xx > 790) & (xx < 930)] = 0          # stray dash under the title
        rgb = art[..., :3] / np.maximum(art[..., 3:4], 1e-3)
        a = art[..., 3]
        cx, cy = self.LOGO
        r = np.hypot(xx - cx, yy - cy)
        comp = art[..., :3] + 255.0 * (1 - a[..., None])           # artwork on white
        # hub halo + rings: rebuilt radially symmetric from the artwork's median profile
        ang = np.linspace(0, 2 * np.pi, 720, endpoint=False)
        radii = np.arange(0, 260)
        prof = np.full((len(radii), 3), 255.0, np.float32)
        for i, rr in enumerate(radii[112:240]):
            px = np.clip((cx + rr * np.cos(ang)).astype(int), 0, w - 1)
            py = np.clip((cy + rr * np.sin(ang)).astype(int), 0, h - 1)
            prof[112 + i] = np.median(comp[py, px], 0)
        fade = np.clip((235 - radii) / 25.0, 0, 1)[:, None]
        prof = 255 - (255 - prof) * fade
        ri = np.clip(r, 0, len(radii) - 1.001)
        r0 = ri.astype(int)
        fr = (ri - r0)[..., None]
        halo = prof[r0] * (1 - fr) + prof[r0 + 1] * fr
        ha = np.clip((255 - halo.min(axis=2)) / (255 - 36.0), 0, 1)
        halo_pm = np.dstack([halo - 255 * (1 - ha[..., None]), ha])
        logo_m = np.clip(113.5 - r, 0, 1)
        logo_src = art
        if self.SOLID_LOGO:          # logo disc taken opaque (its white bolt carried checker noise)
            logo_src = np.dstack([comp, np.ones((h, w), np.float32)])
        hub_pm = logo_src * logo_m[..., None] + halo_pm * (1 - logo_m[..., None])
        hub_pm[r > 236] = 0
        # data squares: found on the artwork, redrawn clean (the source had checker baked in)
        diff = np.abs(comp - halo * (r[..., None] < 236) - 255 * (r[..., None] >= 236)).max(axis=2)
        fg = (diff > 16) & (r > 116) & (xx > 600) & (xx < 1250) & (yy > 150) & (yy < 820)
        fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(fg, connectivity=4)
        self.sq = []
        rng = np.random.default_rng(3)
        s, ox, oy = self.S, self.OX, self.OY
        X = lambda v: ox + s * v  # noqa: E731
        Y = lambda v: oy + s * v  # noqa: E731
        sqmask = np.zeros((h, w), bool)
        def squareish(ww, hh, ar):
            return 9 <= ww <= 62 and 9 <= hh <= 62 and 0.72 < ww / hh < 1.38 and ar > 0.55 * ww * hh

        boxes = []
        for i in range(1, n):
            x, y, ww, hh, ar = st[i]
            if squareish(ww, hh, ar):
                boxes.append((x, y, ww, hh, lab[y:y + hh, x:x + ww] == i))
                continue
            if ww > 110 or hh > 110 or ar < 150:
                continue
            m = (lab == i).astype(np.uint8)
            for kk in (5, 9, 13, 17):             # overlapping squares: erode until they separate
                er = cv2.erode(m, np.ones((kk, kk), np.uint8))
                n2, lab2, st2, _ = cv2.connectedComponentsWithStats(er, connectivity=4)
                parts = [(st2[j][0] - kk // 2, st2[j][1] - kk // 2, st2[j][2] + kk - 1, st2[j][3] + kk - 1,
                          st2[j][4]) for j in range(1, n2)]
                if n2 > 2 and all(squareish(p[2], p[3], p[2] * p[3]) for p in parts):
                    for j, p in zip(range(1, n2), parts):
                        x2, y2, w2, h2, _ = p
                        mm = cv2.dilate((lab2 == j).astype(np.uint8), np.ones((kk, kk), np.uint8))[
                            y2:y2 + h2, x2:x2 + w2] > 0
                        boxes.append((x2, y2, w2, h2, mm))
                    break
        for x, y, ww, hh, mm in boxes:
            if np.hypot(x + ww / 2 - self.NODE[0], y + hh / 2 - self.NODE[1]) < 22:
                continue
            inner = cv2.erode(mm.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            if inner.sum() < 10:
                continue
            col = np.median(comp[y:y + hh, x:x + ww][inner], 0)
            sqmask[max(y - 4, 0):y + hh + 4, max(x - 4, 0):x + ww + 4] = True
            size = (ww + hh) / 2 * s
            pxc, pyc = X(x + ww / 2), Y(y + hh / 2)
            self.sq.append((self._square(pxc, pyc, size, col), (pxc, pyc), 5.0 + rng.uniform(0, 1.1),
                            np.arctan2(pyc - Y(cy), pxc - X(cx)), rng.uniform(0, 2 * np.pi), rng.uniform(2.2, 3.6)))
        # connectors (thin red strokes), excluding the rebuilt rings and squares
        core = (a > 0.35).astype(np.uint8)
        thin = cv2.distanceTransform(core, cv2.DIST_L2, 3) < 3.2
        red = (rgb[..., 0] - rgb[..., 1] > 70) & (a > 0.4) & thin
        node = np.hypot(xx - self.NODE[0], yy - self.NODE[1]) < 19
        ringband = (np.abs(r - 134) < 3) | (np.abs(r - 150) < 3) | (np.abs(r - 184) < 3)
        th = np.degrees(np.arctan2(yy - cy, xx - cx))
        sector = (np.abs(th) < 32) | (np.abs(th) > 150)           # inside the rings only the radial joins
        line = red & (r > 113) & ~sqmask & ((r > 190) | (sector & ~ringband))
        line = cv2.dilate(line.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (a > 0.003) \
            & ~sqmask & (r > 113) & ((r > 190) | (sector & ~ringband))
        line |= node & (a > 0.003)
        lline = line & (xx >= 300) & (xx < cx)
        rline = line & (xx >= cx) & (xx < 1268)
        left = (xx < 500) & ~lline
        right = (xx >= 1250) & ~rline
        C = place(art, s, ox, oy)
        P = lambda m: place(np.dstack([m.astype(np.float32)] * 4), s, ox, oy)[..., 0]  # noqa: E731
        Yc, Xc = np.mgrid[0:H, 0:W].astype(np.float32)
        lm = band_masks(H, W, [Y(c) for c in self.LEFT], 0, W, Yc, Xc)
        rm = band_masks(H, W, [Y(c) for c in self.RIGHT], 0, W, Yc, Xc)
        Lm, Rm = P(left), P(right)
        self.left = [Layer(C, Lm * m, (X(90), Y(c))) for m, c in zip(lm, self.LEFT)]
        self.right = [Layer(C, Rm * m, (X(1320), Y(c))) for m, c in zip(rm, self.RIGHT)]
        nd = np.zeros((h, w, 4), np.float32)
        ndm = np.clip(12.5 - np.hypot(xx - self.NODE[0], yy - self.NODE[1]), 0, 1) * 0.85
        nd[..., :3] = np.float32([250, 175, 175]) * ndm[..., None]
        nd[..., 3] = ndm
        self.node = Layer(place(nd, s, ox, oy), np.ones((H, W)), (X(self.NODE[0]), Y(self.NODE[1])))
        # connectors redrawn as clean curves (the artwork's strokes run under the squares)
        nx, ny = self.NODE
        self.lcurves = []
        for x0, y0 in self.L_START:
            pts = bezier((x0, y0), (x0 + 0.45 * (nx - x0), y0), (nx - 0.35 * (nx - x0), ny), (nx, ny))
            pts = np.vstack([pts, np.linspace((nx, ny), (cx - 112, cy), 12)[1:]])
            self.lcurves.append(np.column_stack([X(pts[:, 0]), Y(pts[:, 1])]))
        self.rcurves = []
        for yd in self.R_END:
            x0, x3 = cx + 112, 1252.0
            pts = bezier((x0, cy), (x0 + 0.4 * (x3 - x0), cy), (x3 - 0.45 * (x3 - x0), yd), (x3, yd))
            self.rcurves.append(np.column_stack([X(pts[:, 0]), Y(pts[:, 1])]))
        self.hub = Layer(place(hub_pm, s, ox, oy), np.ones((H, W)), (X(cx), Y(cy)))
        self.center = (X(cx), Y(cy))

    @staticmethod
    def _square(pxc, pyc, size, col):
        """Rounded square with a soft shadow, premultiplied, as a Layer."""
        k = 4
        pad = int(size * 0.6) + 8
        n = int(size + 2 * pad)
        big = np.zeros((n * k, n * k), np.float32)
        x0 = pad * k
        x1 = int((pad + size) * k)
        rad = int(size * 0.16 * k)
        cv2.rectangle(big, (x0 + rad, x0), (x1 - rad, x1), 1.0, -1)
        cv2.rectangle(big, (x0, x0 + rad), (x1, x1 - rad), 1.0, -1)
        for qx, qy in ((x0 + rad, x0 + rad), (x1 - rad, x0 + rad), (x0 + rad, x1 - rad), (x1 - rad, x1 - rad)):
            cv2.circle(big, (qx, qy), rad, 1.0, -1)
        m = cv2.resize(big, (n, n), interpolation=cv2.INTER_AREA)
        sh = cv2.GaussianBlur(np.roll(m, 3, axis=0), (0, 0), size * 0.12 + 1.5) * 0.16
        pm = np.zeros((n, n, 4), np.float32)
        pm[..., :3] = np.float32([70, 70, 100]) * sh[..., None]
        pm[..., 3] = sh
        col = np.float32(col)
        pm[..., :3] = col * m[..., None] + pm[..., :3] * (1 - m[..., None])
        pm[..., 3] = m + pm[..., 3] * (1 - m)
        canvas = np.zeros((H, W, 4), np.float32)
        gx, gy = int(round(pxc - n / 2)), int(round(pyc - n / 2))
        sx0, sy0 = max(-gx, 0), max(-gy, 0)
        ex, ey = min(n, W - gx), min(n, H - gy)
        canvas[gy + sy0:gy + ey, gx + sx0:gx + ex] = pm[sy0:ey, sx0:ex]
        return Layer(canvas, np.ones((H, W)), (pxc, pyc))

    def render(self, t, plate):
        out = plate.copy()
        # hub: logo + rings pop in, then breathe; pulse rings ripple out
        u = (t - 4.6) / 0.55
        if u > 0:
            if t > 5.2:
                for ph in (0.0, 0.5):
                    q = ((t - 5.2) / 1.6 + ph) % 1.0
                    ring = np.zeros((H, W), np.float32)
                    cv2.circle(ring, (int(self.center[0] * 4), int(self.center[1] * 4)), int((125 + 110 * q) * 4),
                               1.0, 8, cv2.LINE_AA, shift=2)
                    k = (ring * 0.28 * (1 - q) * smooth(u))[..., None]
                    out[...] = out * (1 - k) + np.float32([238, 36, 36]) * k
            breathe = 1 + 0.02 * np.sin(max(t - 5.2, 0) * 2 * np.pi / 1.6)
            self.hub.draw(out, smooth(u * 1.6), (0.55 + 0.45 * ease_back(u)) * breathe)
        # data squares fly in from the hub and keep floating
        for ly, _, t0, ang, ph, per in self.sq:
            u = (t - t0) / 0.6
            if u > 0:
                e = ease_out(u)
                fl = 5 * np.sin((t - t0) * 2 * np.pi / per + ph)
                dr = -70 * (1 - e)
                ly.draw(out, smooth(u * 1.5), 0.6 + 0.4 * ease_back(u),
                        dx=dr * np.cos(ang) + fl * 0.5, dy=dr * np.sin(ang) + fl)
        for i, ly in enumerate(self.left):
            u = (t - self.L_IN[i]) / 0.45
            if u > 0:
                ly.draw(out, smooth(u), 0.92 + 0.08 * ease_back(u), dx=-46 * (1 - ease_out(u)))
        for i, pts in enumerate(self.lcurves):
            u = (t - 5.1 - 0.07 * i) / 1.0
            if u > 0:
                draw_curve(out, pts, ease_out(u), self.LINE)
        u = (t - 5.85) / 0.4
        if u > 0:
            self.node.draw(out, smooth(u), 0.6 + 0.4 * ease_back(u))
        for i, pts in enumerate(self.rcurves):
            u = (t - self.R_IN[i] + 0.4) / 0.55
            if u > 0:
                draw_curve(out, pts, ease_out(u), self.LINE, dot=u > 0.95)
        for i, ly in enumerate(self.right):
            u = (t - self.R_IN[i]) / 0.5
            if u > 0:
                ly.draw(out, smooth(u), 0.9 + 0.1 * ease_back(u), dx=46 * (1 - ease_out(u)))
        return out


# ---------------------------------------------------------------- scene 2: unified governance
class Governance:
    T0, T1, FADE = 10.53, 19.33, (18.90, 19.33)
    S, OX, OY = 1.28, 0.0, 51.0
    LEFT = [203, 275, 344, 414, 489, 566, 643]
    RIGHT = [203, 273, 341, 408, 478, 548, 613, 678]
    LCOL = [(255, 44, 41), (35, 45, 95), (154, 90, 244), (244, 179, 3), (11, 191, 205), (10, 159, 54),
            (74, 110, 130)]
    RCOL = [(21, 122, 247), (6, 177, 187), (138, 83, 252), (252, 128, 8), (7, 146, 58), (11, 116, 240),
            (250, 173, 15), (131, 77, 250)]
    WH = (745.0, 430.0)
    BOB, FEATHER, HAZE = 1.0, 0, 1.0
    WH_IMAGE, WH_BOX = None, (745.0, 226.0, 370.0)     # supplied warehouse cut-out: centre x, top, width
    L_IN = [11.25 + 0.27 * i for i in range(7)]     # "Solix AI Warehouse unifies healthcare data"
    R_IN = [13.95 + 0.29 * i for i in range(8)]     # "powering intelligent and personalized care"
    REGION_Y = 256

    def __init__(self):
        art = load_rgba(os.path.join(ASSETS, "unified_governance.webp"), 253.0)
        h, w = art.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        art[(yy < 168) | ((yy < 200) & (xx > 300) & (xx < 1110))] = 0   # artwork title (video keeps its own)
        a = art[..., 3]
        if self.HAZE < 1:            # soften the pale glow (made for white) on dark backgrounds
            rgbn = art[..., :3] / np.maximum(art[..., 3:4], 1e-3)
            pale = np.clip((rgbn.min(axis=2) - 170) / 60, 0, 1)
            a0 = art[..., 3]
            a1 = a0 * (1 - pale) + (a0 ** (1.0 / self.HAZE)) * pale
            art = art * (a1 / np.maximum(a0, 1e-4))[..., None]
            a = art[..., 3]
        larr = (xx >= 300) & (xx < 562)
        rarr = (xx >= 925) & (xx < 1118)
        wh = (xx >= 562) & (xx < 925)
        if self.WH_IMAGE:           # replace the warehouse with the supplied cut-out
            pale = (art[..., :3] / np.maximum(art[..., 3:4], 1e-3)).min(axis=2) > 160
            old = ((xx >= 557) & (xx < 933) & (yy > 160)) | \
                (pale & ((((xx - 745) / 250) ** 2 + ((yy - 440) / 280) ** 2) < 1))
            art[old] = 0
            a = art[..., 3]
        if self.WH_IMAGE:
            whs = np.zeros((h, w), np.float32)
            larr_s, rarr_s = (xx < 743).astype(np.float32), (xx >= 743).astype(np.float32)
        elif self.FEATHER:
            whs = cv2.GaussianBlur(wh.astype(np.float32), (0, 0), self.FEATHER)
            larr_s, rarr_s = (1 - whs) * (xx < 743), (1 - whs) * (xx >= 743)
        else:
            whs, larr_s, rarr_s = wh.astype(np.float32), larr.astype(np.float32), rarr.astype(np.float32)
        lrows = arrows_to_rows(art, larr, self.LEFT, self.LCOL, 310, 560, 425)
        rrows = arrows_to_rows(art, rarr, self.RIGHT, self.RCOL, 1110, 925, 425)
        s, ox, oy = self.S, self.OX, self.OY
        C = place(art, s, ox, oy)
        P = lambda m: place(np.dstack([m.astype(np.float32)] * 4), s, ox, oy)[..., 0]  # noqa: E731
        X = lambda v: ox + s * v  # noqa: E731
        Y = lambda v: oy + s * v  # noqa: E731
        Yc, Xc = np.mgrid[0:H, 0:W].astype(np.float32)
        lm = band_masks(H, W, [Y(c) for c in self.LEFT], 0, X(300), Yc, Xc)
        rm = band_masks(H, W, [Y(c) for c in self.RIGHT], X(1118), W, Yc, Xc)
        self.left = [Layer(C, m, (X(70), Y(c))) for m, c in zip(lm, self.LEFT)]
        self.right = [Layer(C, m, (X(1160), Y(c))) for m, c in zip(rm, self.RIGHT)]
        revL = (Xc - X(300)) / (X(562) - X(300))
        revR = (X(1118) - Xc) / (X(1118) - X(925))
        if self.FEATHER:            # arrows keep their own pixels, the warehouse takes the soft rest
            lrows = arrows_to_rows(art, (xx >= 300) & (xx < 743), self.LEFT, self.LCOL, 310, 560, 425)
            rrows = arrows_to_rows(art, (xx >= 743) & (xx < 1118), self.RIGHT, self.RCOL, 1110, 925, 425)
        self.larr = [Layer(C, P((lrows == i) * larr_s), (0, 0), reveal=revL) for i in range(len(self.LEFT))]
        self.rarr = [Layer(C, P((rrows == i) * rarr_s), (0, 0), reveal=revR) for i in range(len(self.RIGHT))]
        self.wh = Layer(C, P(whs), (X(self.WH[0]), Y(self.WH[1])))
        if self.WH_IMAGE:
            cx, top, width = self.WH_BOX
            im = cv2.imread(self.WH_IMAGE, cv2.IMREAD_UNCHANGED).astype(np.float32)
            al = im[..., 3] / 255.0
            ys, xs = np.nonzero(al > 0.5)
            k = width / (xs.max() - xs.min())
            pm = np.dstack([im[..., 2::-1] * al[..., None], al])
            ox_, oy_ = X(cx) - s * k * (xs.min() + xs.max()) / 2, Y(top) - s * k * ys.min()
            Cw = place(pm, s * k, ox_, oy_)
            hgt = s * k * (ys.max() - ys.min())
            self.wh = Layer(Cw, np.ones((H, W)), (X(cx), Y(top) + hgt / 2))

    def render(self, t, plate):
        out = plate.copy()
        u = (t - 10.85) / 0.75
        if u > 0:
            bob = 5 * np.sin((t - 10.85) * 2 * np.pi / 2.6) * self.BOB
            pulse = 0.02 * smooth((t - 16.75) / 0.3) * smooth((17.9 - t) / 0.5) * self.BOB
            self.wh.draw(out, smooth(u * 1.3), (0.86 + 0.14 * ease_back(u)) * (1 + pulse), dy=bob * smooth(u))
        for i in range(len(self.LEFT)):
            u = (t - self.L_IN[i]) / 0.45
            if u > 0:
                self.left[i].draw(out, smooth(u), 0.92 + 0.08 * ease_back(u), dx=-50 * (1 - ease_out(u)))
                v = (t - self.L_IN[i] - 0.25) / 0.7
                if v > 0:
                    self.larr[i].draw(out, 1.0, rev=ease_out(v) * 1.1)
        for i in range(len(self.RIGHT)):
            u = (t - self.R_IN[i]) / 0.45
            if u > 0:
                self.right[i].draw(out, smooth(u), 0.92 + 0.08 * ease_back(u), dx=50 * (1 - ease_out(u)))
                v = (t - self.R_IN[i] - 0.2) / 0.7
                if v > 0:
                    self.rarr[i].draw(out, 1.0, rev=ease_out(v) * 1.1)
        return out


# ---------------------------------------------------------------- scene 3: six pillars
class SixPillars:
    T0, T1, FADE = 19.33, 36.10, (35.40, 36.10)
    REGION_Y = 190

    def __init__(self):
        hc_pillars.PLACE = {k: k for k in hc_pillars.SLOTS}   # supplied layout is final: no swap
        self.p = hc_pillars.Pillars(os.path.join(ASSETS, "six_pillars.png"), original=True)

    def render(self, t, plate):
        pm = self.p.render(t)
        return pm[..., :3] + plate * (1 - pm[..., 3:4])


# ---------------------------------------------------------------- scene 4: global healthcare
class Global:
    T0, T1, FADE = 69.50, 76.45, (75.97, 76.45)
    S, OX, OY = 0.65, 878.0, 226.0
    HUB = (785.0, 470.0)
    # hospital clusters (artwork coords) in pop-in order
    HOSP = [(0, 60, 500, 340), (1100, 90, 1450, 290), (1235, 355, 1576, 590),
            (0, 630, 500, 960), (1090, 650, 1576, 990)]
    H_IN = [70.85 + 0.28 * i for i in range(5)]
    REGION_X, REGION_Y = 842, 190

    def __init__(self):
        art = load_rgba(os.path.join(ASSETS, "global_network.webp"), 253.0)
        h, w = art.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        hx, hy = self.HUB
        hub = ((((xx - hx) / 340) ** 2 + ((yy - hy) / 320) ** 2) < 1) | ((xx > 470) & (xx < 1115) & (yy > 540) & (yy < 770))
        hub = cv2.GaussianBlur(hub.astype(np.float32), (0, 0), 22)          # soft cut-outs, no hard seams
        hosp = []
        for x0, y0, x1, y1 in self.HOSP:
            m = np.zeros((h, w), np.float32)
            m[y0:y1, x0:x1] = 1
            hosp.append(cv2.GaussianBlur(m, (0, 0), 10) * (1 - hub))
        lines = np.clip(1 - hub - np.sum(hosp, 0), 0, 1)
        s, ox, oy = self.S, self.OX, self.OY
        C = place(art, s, ox, oy)
        P = lambda m: place(np.dstack([m.astype(np.float32)] * 4), s, ox, oy)[..., 0]  # noqa: E731
        X = lambda v: ox + s * v  # noqa: E731
        Y = lambda v: oy + s * v  # noqa: E731
        Yc, Xc = np.mgrid[0:H, 0:W].astype(np.float32)
        self.hc = (X(hx), Y(hy))
        dist = np.hypot(Xc - self.hc[0], (Yc - self.hc[1]) * 1.25)
        self.dist = dist
        self.lines = Layer(C, P(lines), (0, 0), reveal=dist / 700.0)
        self.hub = Layer(C, P(hub), self.hc)
        self.hosp = [Layer(C, P(m), (X((b[0] + b[2]) / 2), Y((b[1] + b[3]) / 2))) for m, b in zip(hosp, self.HOSP)]
        # glowing blue connector pixels, for the travelling light pulses
        rgb = C[..., :3] / np.maximum(C[..., 3:4], 1e-3)
        self.glowmask = (P(lines) * C[..., 3] * ((rgb[..., 2] > 200) & (rgb[..., 0] < 190))).astype(np.float32)

    def render(self, t, plate):
        out = plate.copy()
        u = (t - 70.35) / 1.2
        if u > 0:
            self.lines.draw(out, 1.0, rev=ease_out(u) * 1.1, soft=0.08)
        for i, ly in enumerate(self.hosp):
            u = (t - self.H_IN[i]) / 0.5
            if u > 0:
                ly.draw(out, smooth(u * 1.4), 0.8 + 0.2 * ease_back(u), dy=8 * (1 - ease_out(u)))
        u = (t - 69.7) / 0.75
        if u > 0:
            bob = 4 * np.sin((t - 69.7) * 2 * np.pi / 2.8)
            self.hub.draw(out, smooth(u * 1.3), 0.85 + 0.15 * ease_back(u), dy=bob * smooth(u))
        # "Connected globally": light pulses run out along the connectors
        u = smooth((t - 72.45) / 0.4)
        if u > 0:
            ph = ((t - 72.45) * 260.0) % 420.0
            w = np.exp(-((self.dist - ph) / 26.0) ** 2) + np.exp(-((self.dist - ph + 420) / 26.0) ** 2)
            k = (self.glowmask * w * 0.75 * u)[..., None]
            out[...] = out + (255.0 - out) * k
        return out


SCENES = None


def _init():
    global SCENES
    SCENES = [Fragmented(), Governance(), SixPillars(), Global()]
    for sc in SCENES:
        sc.plate = PLATE


PLATE = cv2.imread(os.path.join(ASSETS, "v13_white_plate.png"))[:, :, ::-1].astype(np.float32)
# the background ECG scrolls left at 260 px/s; its full strip was recovered from the video
ECG = np.load(os.path.join(ASSETS, "ecg_bottom_strip.npy")).astype(np.float32)
ECG_Y, ECG_V = 760, -260.0 / 30
ECG_TINT = (255 - np.float32([190, 196, 214])) / (255 - 190.0)    # lavender line colour


def background(k):
    """Clean background of frame k: white plate + the scrolling bottom ECG."""
    bg = PLATE.copy()
    g = cv2.warpAffine(ECG, np.float32([[1, 0, ECG_V * k], [0, 1, 0]]), (W, ECG.shape[0]),
                       flags=cv2.INTER_LINEAR, borderValue=255)
    bg[ECG_Y:ECG_Y + ECG.shape[0]] = 255 - (255 - g)[..., None] * ECG_TINT
    return bg


def process(job):
    k, fr = job
    t = k / FPS
    for sc in SCENES:
        if sc.T0 <= t < sc.T1:
            break
    else:
        return fr
    orig = fr.astype(np.float32)
    bg = background(k)
    new = sc.render(t, bg)
    f0, f1 = sc.FADE
    o = 1.0 - np.clip((t - f0) / (f1 - f0), 0, 1)
    new = bg + (new - bg) * o
    out = orig.copy()
    y0 = sc.REGION_Y
    x0 = getattr(sc, "REGION_X", 0)
    y1 = 1066
    out[y0:y1, x0:] = new[y0:y1, x0:]
    if isinstance(sc, Governance):
        # keep the video's title underline (sits inside the replaced area)
        r = np.clip(orig[y0:300, 880:1040] / np.maximum(PLATE[y0:300, 880:1040], 1), 0, 1)
        out[y0:300, 880:1040] *= r
    if isinstance(sc, Global):
        # red "GOVERNED BY DESIGN." letters that overlap the old panel's soft edge
        ys, ye, xs, xe = 510, 605, x0, 930
        reg = orig[ys:ye, xs:xe]
        pg = orig[ys - 6:ys - 2, xs:xe, 1].mean(0)
        a = np.clip((pg - reg[..., 1]) / np.maximum(pg - 36.0, 1), 0, 1)
        a[reg[..., 0] < 150] = 0
        T = np.float32([238, 36, 36])
        out[ys:ye, xs:xe] = out[ys:ye, xs:xe] * (1 - a[..., None]) + T * a[..., None]
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def main():
    video, out = sys.argv[1:3]
    test = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    if test:
        _init()
        for k, fr in enumerate(read_frames(video)):
            if k in test:
                cv2.imwrite(f"{out}_{k}.png", process((k, fr))[:, :, ::-1])
            if k >= max(test):
                break
        return
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4, initializer=_init) as pool:
        for k, img in enumerate(pool.imap(process, enumerate(read_frames(video)), chunksize=4)):
            enc.stdin.write(img.tobytes())
            if k % 300 == 0:
                print("frame", k, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
