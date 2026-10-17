"""EAI Healthcare explainer rebuilt in the Solix EAI Pharma template.

The approved healthcare content (diagrams, screenshots, screen recordings,
wording), the female voice-over, the hyper-beat music and the scene timing
are kept; only the look follows the Pharma video:
  * dark navy/indigo background with drifting red/blue DNA helices, flowing
    wave ribbons and corner crop marks,
  * white Manrope headlines with a Solix-blue highlight box, red-dash spaced
    section label over a faint outlined section number, bullet list with
    dividers, red-bar caption at the bottom left,
  * product screens on floating, slightly tilted cards with a reflection,
  * SOLIX | EAI Healthcare lock-up for the intro and the end card.

usage: python3 hc_pharma.py V13_VIDEO OUT.mp4 [test_times]
"""
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hc_alpha import read_frames  # noqa: E402
import hc_pillars  # noqa: E402
import hc_v14_scenes as v14  # noqa: E402

FPS, W, H = 30, 1920, 1080
FONT = os.path.join(HERE, "..", "fonts", "Manrope.ttf")
WORK = os.environ.get("HC_WORK", "/tmp/hc_pharma")
BLUE = np.float32([0, 136, 207])        # Solix blue  #0088cf (highlight box)
RED = np.float32([238, 36, 36])         # Solix red   #ee2424
NAVY = np.float32([48, 38, 123])        # Solix navy  #30267b
WHITE = np.float32([255, 255, 255])


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = np.clip(x, 0, 1)
    return 1 - (1 - x) ** 3


def fade_io(t, t0, t1, a=0.45, b=0.4):
    return smooth((t - t0) / a) * smooth((t1 - t) / b)


def over(dst, pm, x, y, op=1.0):
    """Premultiplied RGBA over float RGB at integer position (clipped)."""
    if op <= 0.002:
        return
    h, w = pm.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    s = pm[y0 - y:y1 - y, x0 - x:x1 - x]
    reg = dst[y0:y1, x0:x1]
    reg[...] = s[..., :3] * op + reg * (1 - s[..., 3:4] * op)


# ---------------------------------------------------------------- text
_FONTS = {}


def font(size, weight="Bold"):
    k = (size, weight)
    if k not in _FONTS:
        f = ImageFont.truetype(FONT, size)
        f.set_variation_by_name(weight)
        _FONTS[k] = f
    return _FONTS[k]


def text_rgba(txt, size, weight="Bold", color=(255, 255, 255), spacing=0):
    """Render text to a premultiplied float RGBA array (tight box + padding)."""
    f = font(size, weight)
    if spacing:
        widths = [f.getlength(ch) + spacing for ch in txt]
        tw = int(sum(widths)) + 8
    else:
        tw = int(f.getlength(txt)) + 8
    asc, desc = f.getmetrics()
    img = Image.new("L", (tw + 8, asc + desc + 8), 0)
    d = ImageDraw.Draw(img)
    if spacing:
        x = 4
        for ch, wv in zip(txt, widths):
            d.text((x, 4), ch, font=f, fill=255)
            x += wv
    else:
        d.text((4, 4), txt, font=f, fill=255)
    a = np.asarray(img, np.float32) / 255.0
    col = np.float32(color)
    return np.dstack([a[..., None] * col, a]), asc


def ink(size, weight="Bold"):
    """(cap top, descender bottom) of a text_rgba image, in pixels from its top."""
    f = font(size, weight)
    return 4 + f.getbbox("H")[1], 4 + f.getbbox("gpyq")[3]


def boxed(out, pm, size, weight, x, box_top, frac_box, frac_text, op, pad_x=14):
    """Blue highlight box with the text centred vertically inside it; returns the box bottom."""
    cap, dsc = ink(size, weight)
    pad = int(round(size * 0.2))
    bh = (dsc - cap) + 2 * pad
    bw = pm.shape[1] - 8 + 2 * pad_x
    wd = int(bw * ease_out(frac_box))
    if wd > 1:
        x0 = int(x) - pad_x
        reg = out[box_top:box_top + bh, max(x0, 0):x0 + wd]
        reg[...] = reg * (1 - 0.95 * op) + BLUE * 0.95 * op
    over(out, pm, x - 4, box_top + pad - cap, smooth(frac_text) * op)
    return box_top + bh


def text_w(txt, size, weight="Bold"):
    return font(size, weight).getlength(txt)


def outline_rgba(txt, size, color=(40, 62, 130), stroke=2):
    f = font(size, "Bold")
    tw = int(f.getlength(txt)) + 20
    asc, desc = f.getmetrics()
    img = Image.new("L", (tw, asc + desc + 20), 0)
    d = ImageDraw.Draw(img)
    d.text((10, 10), txt, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
    full = np.asarray(img, np.float32)
    img2 = Image.new("L", img.size, 0)
    ImageDraw.Draw(img2).text((10, 10), txt, font=f, fill=255)
    inner = np.asarray(img2, np.float32)
    a = np.clip(full - inner, 0, 255) / 255.0
    return np.dstack([a[..., None] * np.float32(color), a])


# ---------------------------------------------------------------- background
class Background:
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.hypot((xx - W * 0.56) / W, (yy - H * 0.42) / H * 0.9)
        g = np.clip(1 - d / 0.78, 0, 1) ** 1.6
        base = np.float32([3, 3, 16]) * (1 - g[..., None]) + np.float32([14, 26, 88]) * g[..., None]
        haze = np.exp(-(((xx - W * 0.45) / (W * 0.5)) ** 2 + ((yy - H * 1.02) / (H * 0.32)) ** 2))[..., None]
        base = base + np.float32([40, 10, 38]) * haze
        vig = np.clip(1 - 0.55 * np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) ** 2.2, 0.25, 1)
        self.base = base * vig[..., None]
        self.vig = vig
        rng = np.random.default_rng(11)
        self.bokeh = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 6), rng.uniform(0.02, 0.06),
                       rng.uniform(0, 6.28)) for _ in range(26)]
        cm = np.zeros((H, W), np.float32)
        L, I = 26, 44
        for (cx, cy, sx, sy) in ((I, I, 1, 1), (W - I, I, -1, 1), (I, H - I, 1, -1), (W - I, H - I, -1, -1)):
            cv2.line(cm, (cx, cy), (cx + sx * L, cy), 1.0, 2, cv2.LINE_AA)
            cv2.line(cm, (cx, cy), (cx, cy + sy * L), 1.0, 2, cv2.LINE_AA)
        self.corners = cm

    # heartbeat traces: (baseline y, amplitude, period, scroll px/s, colour, opacity, phase)
    ECG = [(330, 95, 640, 70, np.float32([40, 110, 235]), 0.20, 0.0),
           (690, 120, 780, 95, np.float32([225, 40, 70]), 0.15, 0.35),
           (905, 70, 560, 55, np.float32([40, 110, 235]), 0.11, 0.7)]

    @staticmethod
    def _ecg(layer, glow, t, yb, amp, per, speed, col, alpha, ph):
        xs = np.arange(-20, W + 20, 3, dtype=np.float32)
        u = ((xs + t * speed) / per + ph) % 1.0
        g = lambda c, w: np.exp(-((u - c) / w) ** 2)  # noqa: E731
        y = yb - amp * (0.13 * g(0.18, 0.035) - 0.16 * g(0.300, 0.010) + 1.0 * g(0.318, 0.009)
                        - 0.38 * g(0.338, 0.010) + 0.26 * g(0.55, 0.05))
        head = (t * 420 + ph * 900) % (W + 700) - 350               # monitor sweep highlight
        boost = 1 + 1.6 * np.exp(-((xs - head) / 170) ** 2)
        pts = np.column_stack([xs, y]) * 8
        for i in range(0, len(xs) - 1, 4):
            a = alpha * float(boost[i])
            cv2.polylines(layer, [np.int32(pts[i:i + 5])], False, (col * a).tolist(), 2, cv2.LINE_AA, shift=3)
        i = int(np.argmin(np.abs(xs - head)))
        if 0 < head < W:
            cv2.circle(glow, (int(xs[i] * 8), int(y[i] * 8)), 5 * 8, (col * alpha * 1.4).tolist(), -1, cv2.LINE_AA,
                       shift=3)

    @staticmethod
    def _ribbon(layer, t, base, col, n, spread, amp, w, speed, alpha):
        xs = np.arange(-40, W + 40, 16, dtype=np.float32)
        for j in range(n):
            f = j / (n - 1)
            y = base(xs) + (f - 0.5) * spread * (0.6 + 0.4 * np.sin(xs / 380 + t * 0.15 + 1.3)) \
                + amp * np.sin(xs / w + t * speed + f * 2.4)
            a = alpha * (0.35 + 0.65 * np.sin(np.pi * f))
            cv2.polylines(layer, [np.int32(np.column_stack([xs, y]) * 8)], False, (col * a).tolist(), 1,
                          cv2.LINE_AA, shift=3)

    def frame(self, t):
        out = self.base.copy()
        layer = np.zeros((H, W, 3), np.float32)
        glow = np.zeros((H, W, 3), np.float32)
        drift = t * 6.0
        self._ribbon(layer, t, lambda x: 930 - 0.30 * x + 40 * np.sin(x / 700 + 0.4) - drift * 0.1,
                     np.float32([40, 90, 230]), 34, 150, 26, 260, 0.35, 0.06)
        self._ribbon(layer, t, lambda x: 1010 - 0.36 * x + 50 * np.sin(x / 820 + 2.0),
                     np.float32([200, 40, 90]), 28, 120, 22, 300, 0.28, 0.05)
        for (yb, amp, per, speed, col, alpha, ph) in self.ECG:
            self._ecg(layer, glow, t, yb, amp, per, speed, col, alpha, ph)
        out += layer + cv2.GaussianBlur(layer, (0, 0), 3) * 0.8
        out += glow * 0.8 + cv2.GaussianBlur(glow, (0, 0), 6) * 1.2
        bok = np.zeros((H, W, 3), np.float32)
        for (bx, by, r, a, ph) in self.bokeh:
            k = a * (0.6 + 0.4 * np.sin(t * 0.7 + ph))
            cv2.circle(bok, (int(bx), int(by)), int(r), (np.float32([90, 120, 220]) * k * 3).tolist(), -1, cv2.LINE_AA)
        out += cv2.GaussianBlur(bok, (0, 0), 2)
        out = out * (0.65 + 0.35 * self.vig[..., None])
        out += self.corners[..., None] * np.float32([95, 98, 120])
        return out


# ---------------------------------------------------------------- logo
def load_logo():
    """Supplied SOLIX logo (white wordmark + tagline, red disc) as premultiplied RGBA."""
    im = cv2.imread(os.path.join(v14.ASSETS, "solix_logo_white.webp"), cv2.IMREAD_UNCHANGED).astype(np.float32)
    a = im[..., 3:4] / 255.0
    return np.dstack([im[..., 2::-1] * a, a[..., 0]])


def scaled(pm, s):
    return cv2.resize(pm, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)


# ---------------------------------------------------------------- slide text system
class Slide:
    """Label + big outline number + headline (2nd line on a blue box) + bullets + captions."""

    def __init__(self, label, number, line1, line2, bullets=(), x=120, y_label=200, size=72,
                 t_in=0.0, bullets_t=(), captions=(), line2_box=True):
        self.x = x
        self.t_in = t_in
        self.lab, _ = text_rgba(label.upper(), 20, "Medium", (195, 200, 222), spacing=9)
        self.num = outline_rgba(number, 250) if number else None
        self.y_label = y_label
        self.l1, _ = text_rgba(line1, size, "Bold")
        self.l2, self.asc2 = text_rgba(line2, size, "Bold")
        self.size = size
        self.box = line2_box
        self.bul = [(text_rgba(b, 29, "Regular", (150, 156, 182))[0], text_rgba(b, 29, "Regular", (240, 242, 250))[0])
                    for b in bullets]
        self.bul_t = list(bullets_t)
        self.caps = [(t0, t1, text_rgba(c, 29, "Medium", (196, 200, 220))[0]) for t0, t1, c in captions]

    def draw(self, out, t, op=1.0, show_bullets=True):
        x, yl = self.x, self.y_label
        u = (t - self.t_in) / 0.5
        if u <= 0:
            return
        if self.num is not None:
            over(out, self.num, x - 12, yl - 85, 0.55 * smooth(u) * op)
        out_dash = smooth(u)
        cv2.line(out, (x + 4, yl + 12), (x + 4 + int(36 * out_dash), yl + 12), (RED * op).tolist(), 3, cv2.LINE_AA)
        over(out, self.lab, x + 52 - 18 * (1 - ease_out(u)), yl - 4, smooth(u) * op)
        y1 = yl + 52
        v = (t - self.t_in - 0.15) / 0.5
        over(out, self.l1, x - 4, y1 + 24 * (1 - ease_out(v)), smooth(v) * op)
        cap, dsc = ink(self.size)
        box_top = y1 + dsc + int(self.size * 0.24)            # line space under line 1
        v2 = (t - self.t_in - 0.35) / 0.45
        bottom = box_top + (dsc - cap) + 2 * int(round(self.size * 0.2))
        if v2 > 0:
            if self.box:
                boxed(out, self.l2, self.size, "Bold", x, box_top, v2, (v2 - 0.35) / 0.5, op)
            else:
                over(out, self.l2, x - 4, box_top - cap, smooth((v2 - 0.35) / 0.5) * op)
        self.bottom = bottom
        if show_bullets and self.bul:
            by = bottom + 78
            for i, (dim, lit) in enumerate(self.bul):
                tb = self.bul_t[i] if i < len(self.bul_t) else self.t_in + 0.8 + 0.25 * i
                w_ = smooth((t - tb) / 0.4)
                if w_ <= 0:
                    continue
                yy = by + i * 65
                ln = int(560 * ease_out((t - tb) / 0.5))
                cv2.line(out, (x + 4, yy - 28), (x + 4 + ln, yy - 28), (np.float32([70, 78, 120]) * w_ * op).tolist(),
                         1, cv2.LINE_AA)
                nxt = self.bul_t[i + 1] if i + 1 < len(self.bul_t) else 1e9
                act = smooth((t - tb) / 0.3) * (1 - smooth((t - nxt) / 0.3)) if self.bul_t else 0
                mk = RED * (0.5 + 0.5 * act)
                cv2.rectangle(out, (x + 6, yy - 4), (x + 13, yy + 3), (mk * w_ * op).tolist(), -1)
                over(out, dim, x + 30 - 14 * (1 - ease_out((t - tb) / 0.4)), yy - 22, w_ * op * (1 - act))
                over(out, lit, x + 30 - 14 * (1 - ease_out((t - tb) / 0.4)), yy - 22, w_ * op * act)
        for t0, t1, cap in self.caps:
            k = fade_io(t, t0, t1, 0.3, 0.3) * op
            if k > 0:
                cv2.rectangle(out, (123, 963), (126, 995), (RED * k).tolist(), -1)
                over(out, cap, 146, 960, k)


# ---------------------------------------------------------------- floating card
def rounded_mask(w, h, r):
    m = np.zeros((h * 4, w * 4), np.uint8)
    R = r * 4
    cv2.rectangle(m, (R, 0), (w * 4 - R, h * 4), 255, -1)
    cv2.rectangle(m, (0, R), (w * 4, h * 4 - R), 255, -1)
    for cx, cy in ((R, R), (w * 4 - R, R), (R, h * 4 - R), (w * 4 - R, h * 4 - R)):
        cv2.circle(m, (cx, cy), R, 255, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0


def draw_card(out, img, cx, cy, width, op=1.0, tilt=0.06, lift=0.0, reflect=True, rmask=None):
    """Card image (float RGB) floating with a slight 3D tilt, shadow and reflection."""
    h0, w0 = img.shape[:2]
    s = width / w0
    w, h = width, h0 * s
    tl = (cx - w / 2, cy - h / 2 + lift)
    # perspective: right edge slightly shorter (turned towards the viewer's left)
    k = tilt * h
    dst = np.float32([[tl[0], tl[1]], [tl[0] + w, tl[1] + k * 0.5], [tl[0] + w, tl[1] + h - k * 0.5],
                      [tl[0], tl[1] + h]])
    src = np.float32([[0, 0], [w0, 0], [w0, h0], [0, h0]])
    M = cv2.getPerspectiveTransform(src, dst)
    x0, y0 = int(max(dst[:, 0].min() - 60, 0)), int(max(dst[:, 1].min() - 60, 0))
    x1, y1 = int(min(dst[:, 0].max() + 60, W)), int(min(dst[:, 1].max() + 60 + h * 0.35, H))
    T = np.float32([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]]) @ M
    if rmask is None:
        rmask = rounded_mask(w0, h0, max(6, int(14 / s)))
    rgba = np.dstack([img * rmask[..., None], rmask])
    wp = cv2.warpPerspective(rgba, T, (x1 - x0, y1 - y0), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
    reg = out[y0:y1, x0:x1]
    sh = cv2.GaussianBlur(wp[..., 3], (0, 0), 22)
    sh = np.roll(sh, 18, axis=0) * 0.55 * op
    reg[...] = reg * (1 - sh[..., None])
    if reflect:
        Fl = np.float32([[1, 0, 0], [0, -1, 2 * (dst[3, 1] + 6 - y0)], [0, 0, 1]])
        rf = cv2.warpPerspective(wp, Fl, (x1 - x0, y1 - y0))
        fade = np.clip(1 - (np.arange(y1 - y0, dtype=np.float32) - (dst[3, 1] + 6 - y0)) / (h * 0.3), 0, 1) ** 2
        fade[: int(dst[3, 1] + 6 - y0)] = 0
        rf = rf * (fade[:, None, None] * 0.13 * op)
        reg[...] = rf[..., :3] + reg * (1 - rf[..., 3:4])
    reg[...] = wp[..., :3] * op + reg * (1 - wp[..., 3:4] * op)
    # thin light border like the Pharma glass cards
    edge = cv2.morphologyEx((wp[..., 3] > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    reg[...] = reg + edge[..., None].astype(np.float32) * np.float32([40, 50, 80]) * op * 0.6


# ---------------------------------------------------------------- scenes
# scene windows (v13 timing, synced to the voice-over); content fades out at the end
SCENES = [("intro", 0.0, 3.50), ("frag", 3.50, 10.53), ("gov", 10.53, 19.33), ("pillars", 19.33, 36.10),
          ("p360", 36.10, 38.50), ("agents", 38.50, 53.00), ("findings", 53.00, 61.55),
          ("clinic", 61.55, 69.60), ("global", 69.60, 76.45), ("end", 76.45, 81.0)]
# card crops from the approved v13 video: (scene, t0, t1 of the source window, rect)
CARD_SRC = {"agents": (38.5, 53.0, (241, 197, 1679, 830)), "findings": (53.0, 61.55, (101, 197, 1159, 872)),
            "clinic": (61.55, 69.6, (101, 197, 1159, 872))}


def extract_cards(video):
    os.makedirs(WORK, exist_ok=True)
    mm = {}
    for name, (t0, t1, (x0, y0, x1, y1)) in CARD_SRC.items():
        n = int(round((t1 - t0) * FPS)) + 1
        mm[name] = np.lib.format.open_memmap(os.path.join(WORK, f"card_{name}.npy"), "w+", np.uint8,
                                             (n, y1 - y0, x1 - x0, 3))
    for k, f in enumerate(read_frames(video)):
        t = k / FPS
        for name, (t0, t1, (x0, y0, x1, y1)) in CARD_SRC.items():
            i = int(round((t - t0) * FPS))
            if 0 <= i < mm[name].shape[0]:
                mm[name][i] = f[y0:y1, x0:x1]
    for m in mm.values():
        m.flush()


class Renderer:
    def __init__(self, logo_pm):
        self.bg = Background()
        self.logo_big = scaled(logo_pm, 0.26)
        self.logo_small = scaled(logo_pm, 0.178)
        self.cards = {n: np.load(os.path.join(WORK, f"card_{n}.npy"), mmap_mode="r") for n in CARD_SRC}
        self.rm = {n: rounded_mask(m.shape[2], m.shape[1], 14) for n, m in self.cards.items()}
        self._lockup()
        self._slides()
        self._diagrams()

    # -- intro / end lock-up: SOLIX | EAI Healthcare
    def _lockup(self):
        self.eai, _ = text_rgba("EAI Healthcare", 78, "Bold")
        self.intro_steps = [text_rgba(s, 22, "SemiBold", c, spacing=4)[0] for s, c in
                            (("TRUSTED DATA FOUNDATION", (205, 210, 230)), ("COLLABORATIVE INTELLIGENCE", (255, 255, 255)),
                             ("ACTIONABLE OUTCOMES", (205, 210, 230)))]
        self.arrow, _ = text_rgba("→", 26, "Bold", (238, 36, 36))
        self.end_tag1, _ = text_rgba("Accelerated care by empowering clinicians ", 34, "Medium", (215, 220, 238))
        self.end_tag2, _ = text_rgba("for intelligent outcomes.", 34, "Medium")
        self.end_care, _ = text_rgba("Care Creates Data", 26, "SemiBold", (230, 232, 245))
        self.end_cure, _ = text_rgba("Data Accelerates Cure", 26, "SemiBold", (238, 60, 60))

    def _draw_lockup(self, out, t, t0, op):
        lg = self.logo_big
        gap = 46
        total = lg.shape[1] + gap + self.eai.shape[1]
        x = (W - total) / 2
        y = 400
        u = smooth((t - t0) / 0.7)
        over(out, lg, x - 30 * (1 - u), y, u * op)
        hb = int(70 * smooth((t - t0 - 0.3) / 0.4))
        if hb > 0:
            cv2.line(out, (int(x + lg.shape[1] + gap / 2), y + 24), (int(x + lg.shape[1] + gap / 2), y + 24 + hb),
                     (RED * op).tolist(), 3, cv2.LINE_AA)
        v = smooth((t - t0 - 0.45) / 0.6)
        over(out, self.eai, x + lg.shape[1] + gap + 24 * (1 - v), y + 12, v * op)

    def _slides(self):
        cap = lambda *a: a  # noqa: E731
        self.s = {
            "frag": Slide("Fragmented data", "", "From fragmented data", "to better patient outcomes.", x=120,
                          y_label=112, size=60, t_in=3.6,
                          captions=[cap(3.6, 6.4, "Every hospital holds a wealth of clinical data."),
                                    cap(6.55, 10.3, "Unlocking insights that drive better patient outcomes.")]),
            "gov": Slide("Unify", "01", "AI ready foundation with", "Unified Governance.", x=120, y_label=112,
                         size=60, t_in=10.6,
                         captions=[cap(10.6, 13.85, "Solix AI Warehouse unifies healthcare data,"),
                                   cap(13.9, 16.7, "powering intelligent and personalized care,"),
                                   cap(16.75, 19.1, "transforming patient outcomes.")]),
            "pillars": Slide("Foundation", "02", "Six pillars of AI ready foundation", "for healthcare intelligence.",
                             x=120, y_label=112, size=56, t_in=19.45,
                             captions=[cap(19.45, 23.5, "Six pillars of an AI-ready foundation for healthcare intelligence."),
                                       cap(23.53, 30.05, "AI Warehouse. Federated Governance. Patient 360. Clinical Intelligence and Imaging."),
                                       cap(30.1, 35.6, "Multi-agentic intelligence, for every specialty.")]),
            "agents": Slide("AI Patient 360 Analytics", "03", "Purpose-built multi-agentic", "system for every specialty.",
                            x=120, y_label=112, size=56, t_in=38.6,
                            captions=[cap(38.6, 43.9, "Every specialty has its own multi-agent clusters, with a consensus score."),
                                      cap(45.0, 48.8, "Purpose-built Solix agents bring every system into focus,"),
                                      cap(48.9, 52.7, "turning real-time insights into better patient outcomes.")]),
            "findings": Slide("Specialty agent", "04", "Findings", "with Evidence.", x=120, y_label=200, size=72,
                              t_in=53.1, bullets=["Published guideline", "Readings cited", "Rule applied",
                                                  "Explainability by design"],
                              bullets_t=[54.4, 56.35, 57.73, 59.15],
                              captions=[cap(53.15, 56.3, "Every finding comes with its evidence, by design."),
                                        cap(56.35, 61.3, "The readings are cited. The rules are applied, based on the published guidelines.")]),
            "clinic": Slide("Clinician in control", "05", "Decisions are validated", "& approved by clinicians.",
                            x=120, y_label=200, size=60, t_in=61.65,
                            bullets=["Review the evidence", "Refine the findings", "Approve with confidence"],
                            bullets_t=[63.8, 65.15, 66.6],
                            captions=[cap(61.8, 63.76, "Clinicians lead every decision."),
                                      cap(63.8, 69.3, "Review the evidence, refine the findings, and approve with confidence, before sign-off.")]),
            "global": Slide("Global", "06", "Built for global healthcare.", "Governed by design.", x=120,
                            y_label=200, size=56, t_in=69.7,
                            bullets=["A unified Patient 360 knowledge layer", "Connected globally", "Governed by design"],
                            bullets_t=[69.9, 72.55, 73.95],
                            captions=[cap(69.75, 72.5, "A unified Patient 360 knowledge layer."),
                                      cap(72.55, 76.1, "Connected globally. Governed by design.")]),
        }
        self.p360_lab, _ = text_rgba("PATIENT 360", 20, "Medium", (195, 200, 222), spacing=9)
        self.p360_l1, _ = text_rgba("AI Patient 360", 96, "Bold")
        self.p360_l2, _ = text_rgba("Analytics.", 96, "Bold")
        self.p360_cap, _ = text_rgba("The outcome is a Patient 360.", 29, "Medium", (196, 200, 220))
        self.pills = [text_rgba(p, 24, "SemiBold")[0] for p in ("HIPAA", "GDPR", "NIST")]

    def _diagrams(self):
        # approved, animated diagrams from v14, placed for the Pharma layout
        class Frag(v14.Fragmented):
            S, OX, OY = 0.86, 260.0, 252.0
            SOLID_LOGO = True

            def __init__(self):
                super().__init__()
                self._clean_items()

            def _clean_items(self):
                """Rebuild the source/outcome chips: the artwork's pale pills carry checker noise
                that shows on a dark background. Icon discs and labels are kept from the artwork."""
                im = cv2.imread(os.path.join(v14.ASSETS, "fragmented_data_rgba.png"), cv2.IMREAD_UNCHANGED)
                im = im.astype(np.float32)
                a = im[..., 3:4] / 255.0
                comp = im[..., 2::-1] * a + 255 * (1 - a)
                lum = comp.mean(2)
                h, w = lum.shape
                yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
                navy = np.clip((205 - lum) / 150, 0, 1) * (comp[..., 2] > comp[..., 0] + 12)
                s, ox, oy = self.S, self.OX, self.OY
                X = lambda v: ox + s * v  # noqa: E731
                Y = lambda v: oy + s * v  # noqa: E731

                def chip(cx, cy, r, x_end):
                    pill = np.zeros((h * 2, w * 2), np.float32)
                    cv2.rectangle(pill, (int(cx * 2), int((cy - 30) * 2)), (int((x_end - 30) * 2), int((cy + 30) * 2)),
                                  1.0, -1)
                    cv2.circle(pill, (int((x_end - 30) * 2), int(cy * 2)), 60, 1.0, -1, cv2.LINE_AA)
                    pill = cv2.resize(pill, (w, h), interpolation=cv2.INTER_AREA)
                    disc = np.clip(r + 0.5 - np.hypot(xx - cx, yy - cy), 0, 1)
                    txt = navy * ((xx > cx + r + 2) & (xx < x_end + 4) & (np.abs(yy - cy) < 28))
                    pm = np.zeros((h, w, 4), np.float32)
                    sh = cv2.GaussianBlur(np.maximum(pill, disc), (0, 0), 8) * 0.35
                    pm[..., 3] = sh
                    pm[..., 3] = pill * 0.93 + pm[..., 3] * (1 - pill * 0.93)
                    pm[..., :3] = np.float32([246, 247, 253]) * (pill * 0.93)[..., None]
                    pm[..., :3] = np.float32([30, 34, 92]) * txt[..., None] + pm[..., :3] * (1 - txt[..., None])
                    pm[..., 3] = txt + pm[..., 3] * (1 - txt)
                    pm[..., :3] = comp * disc[..., None] + pm[..., :3] * (1 - disc[..., None])
                    pm[..., 3] = disc + pm[..., 3] * (1 - disc)
                    return Layer(v14.place(pm, s, ox, oy), np.ones((H, W)), (X(cx), Y(cy)))

                Layer = v14.Layer
                L_END = [215, 445, 325, 370, 405, 465]
                R_END = [1615, 1637, 1624]
                self.left = [chip(90, r, 46, e + 28) for r, e in zip(self.LEFT, L_END)]
                self.right = [chip(1320, r, 51, e + 30) for r, e in zip(self.RIGHT, R_END)]

        class Gov(v14.Governance):
            S, OX, OY = 1.0, 210.0, 228.0
            BOB, FEATHER, HAZE = 0.0, 14, 1.6
            WH_IMAGE = os.path.join(v14.ASSETS, "ai_warehouse_rgba.png")

        class Glob(v14.Global):
            S, OX, OY = 0.60, 965.0, 230.0
        self.frag, self.gov, self.glob = Frag(), Gov(), Glob()
        hc_pillars.SCALE = 0.64
        hc_pillars.FRAME_CENTER = (946.0, 672.0)
        hc_pillars.PLACE = {k: k for k in hc_pillars.SLOTS}
        self.pil = hc_pillars.Pillars(os.path.join(v14.ASSETS, "six_pillars.png"), dark=True, original=True)

    # -- frame
    def frame(self, k):
        t = k / FPS
        out = self.bg.frame(t)
        name, t0, t1 = next((n, a, b) for n, a, b in SCENES if a <= t < b) if t < SCENES[-1][2] else SCENES[-1]
        op = smooth((t1 - t) / 0.4) if name != "end" else 1.0
        if name not in ("intro", "end"):
            over(out, self.logo_small, 1468, 52, smooth((t - 3.5) / 0.6))
        getattr(self, "_" + name)(out, t, t0, t1, op)
        return np.clip(out + 0.5, 0, 255).astype(np.uint8)

    def _intro(self, out, t, t0, t1, op):
        self._draw_lockup(out, t, 0.15, op)
        x = W / 2
        ws = [s.shape[1] for s in self.intro_steps]
        total = sum(ws) + 2 * 70
        xx = x - total / 2
        for i, s in enumerate(self.intro_steps):
            u = smooth((t - 1.0 - 0.3 * i) / 0.5)
            if i == 1 and u > 0:
                cap, dsc = ink(22, "SemiBold")
                bw = int((s.shape[1] + 12) * ease_out((t - 1.3) / 0.45))
                reg = out[630 + cap - 9:630 + dsc - 3, int(xx) - 6:int(xx) - 6 + bw]
                reg[...] = reg * (1 - 0.95 * op) + BLUE * 0.95 * op
            over(out, s, xx, 630, u * op)
            xx += s.shape[1]
            if i < 2:
                over(out, self.arrow, xx + 18, 622, smooth((t - 1.2 - 0.3 * i) / 0.4) * op)
                xx += 70

    def _frag(self, out, t, t0, t1, op):
        self.s["frag"].draw(out, t, op)
        self._diagram(out, self.frag.render(t, out.copy()), op)

    def _gov(self, out, t, t0, t1, op):
        self.s["gov"].draw(out, t, op)
        self._diagram(out, self.gov.render(t, out.copy()), op)

    def _diagram(self, out, comp, op):
        out[...] = out + (comp - out) * op

    def _pillars(self, out, t, t0, t1, op):
        self.s["pillars"].draw(out, t, op)
        pm = self.pil.render(t)
        out[...] = out * (1 - pm[..., 3:4] * op) + pm[..., :3] * op

    def _p360(self, out, t, t0, t1, op):
        u = (t - 36.15) / 0.5
        y = 400
        lw = self.p360_lab.shape[1]
        x = (W - lw - 52) / 2
        cv2.line(out, (int(x), y + 12), (int(x + 36 * smooth(u)), y + 12), (RED * op).tolist(), 3, cv2.LINE_AA)
        over(out, self.p360_lab, x + 52, y - 4, smooth(u) * op)
        v = (t - 36.3) / 0.5
        over(out, self.p360_l1, (W - self.p360_l1.shape[1]) / 2, y + 50 + 20 * (1 - ease_out(v)), smooth(v) * op)
        v2 = (t - 36.55) / 0.45
        if v2 > 0:
            cap, dsc = ink(96)
            boxed(out, self.p360_l2, 96, "Bold", (W - self.p360_l2.shape[1] + 8) / 2, y + 50 + dsc + 22, v2,
                  (v2 - 0.3) / 0.5, op, pad_x=18)
        k = fade_io(t, 36.3, 38.4, 0.3, 0.3) * op
        if k > 0:
            cv2.rectangle(out, (123, 963), (126, 995), (RED * k).tolist(), -1)
            over(out, self.p360_cap, 146, 960, k)

    def _card(self, out, name, t, cx, cy, width, op, t_in):
        t0, t1, _ = CARD_SRC[name]
        cards = self.cards[name]
        i = int(np.clip(round((np.clip(t, t0 + 0.9, t1 - 0.5) - t0) * FPS), 0, cards.shape[0] - 1))
        img = cards[i].astype(np.float32)
        u = ease_out((t - t_in) / 0.8)
        if u <= 0:
            return
        draw_card(out, img, cx + 60 * (1 - u), cy, width * (0.94 + 0.06 * u), op * smooth((t - t_in) / 0.5),
                  tilt=0.05, lift=-4 * np.sin(t * 0.8), rmask=self.rm[name])

    def _agents(self, out, t, t0, t1, op):
        self.s["agents"].draw(out, t, op)
        self._card(out, "agents", t, 1180, 672, 1230, op, 38.75)

    def _findings(self, out, t, t0, t1, op):
        self.s["findings"].draw(out, t, op)
        self._card(out, "findings", t, 1290, 520, 900, op, 53.3)

    def _clinic(self, out, t, t0, t1, op):
        self.s["clinic"].draw(out, t, op)
        self._card(out, "clinic", t, 1310, 520, 880, op, 61.85)

    def _global(self, out, t, t0, t1, op):
        self.s["global"].draw(out, t, op, show_bullets=True)
        x = 124
        for i, p in enumerate(self.pills):
            u = smooth((t - 70.9 - 0.15 * i) / 0.4) * op
            if u > 0:
                pw = p.shape[1] + 40
                m = np.zeros((60, pw), np.float32)
                cv2.rectangle(m, (28, 2), (pw - 28, 58), 1.0, -1)
                cv2.circle(m, (28, 30), 28, 1.0, -1, cv2.LINE_AA)
                cv2.circle(m, (pw - 28, 30), 28, 1.0, -1, cv2.LINE_AA)
                reg = out[800:860, x:x + pw]
                reg[...] = reg * (1 - 0.10 * m[..., None] * u) + 255 * 0.10 * m[..., None] * u
                edge = cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8))
                reg[...] = reg + edge[..., None] * np.float32([60, 70, 110]) * u
                over(out, p, x + 16, 806 + 6 * (1 - u), u)
                x += pw + 22
        comp = self.glob.render(t, out.copy())
        out[...] = out + (comp - out) * op

    def _end(self, out, t, t0, t1, op):
        self._draw_lockup(out, t, 76.55, 1.0)
        u = smooth((t - 77.1) / 0.6)
        tw = self.end_tag1.shape[1] + self.end_tag2.shape[1]
        x = (W - tw) / 2
        over(out, self.end_tag1, x, 600, u)
        v = (t - 77.5) / 0.45
        if v > 0:
            cap, dsc = ink(34, "Medium")
            wd = int((self.end_tag2.shape[1] + 8) * ease_out(v))
            x2 = int(x + self.end_tag1.shape[1]) - 4
            reg = out[600 + cap - 9:600 + dsc + 9, x2:x2 + wd]
            reg[...] = reg * 0.05 + BLUE * 0.95
        over(out, self.end_tag2, x + self.end_tag1.shape[1], 600, u)
        w_ = smooth((t - 78.0) / 0.6)
        cw = self.end_care.shape[1] + 50 + self.end_cure.shape[1]
        cx = (W - cw) / 2
        over(out, self.end_care, cx, 690, w_)
        cv2.line(out, (int(cx + self.end_care.shape[1] + 25), 700), (int(cx + self.end_care.shape[1] + 25), 728),
                 (RED * w_).tolist(), 2, cv2.LINE_AA)
        over(out, self.end_cure, cx + self.end_care.shape[1] + 50, 690, w_)


R = None


def _init(logo):
    global R
    R = Renderer(logo)


def _job(k):
    return R.frame(k)


def main():
    video, out = sys.argv[1:3]
    test = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    if not os.path.exists(os.path.join(WORK, "card_clinic.npy")):
        extract_cards(video)
    logo = load_logo()
    n = int(round(80.6 * FPS))
    if test:
        _init(logo)
        for t in test:
            cv2.imwrite(f"{out}_{t}.png", R.frame(int(round(t * FPS)))[:, :, ::-1])
        return
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4, initializer=_init, initargs=(logo,)) as pool:
        for k, img in enumerate(pool.imap(_job, range(n), chunksize=4)):
            enc.stdin.write(img.tobytes())
            if k % 300 == 0:
                print("frame", k, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
