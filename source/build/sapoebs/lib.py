# Drawing primitives for the SAP + Oracle EBS film (1920x1080 design space, 30 fps).
# Everything is drawn procedurally: sprites (PIL, cached) + additive light layer (OpenCV).
import math, json, os
import numpy as np, cv2
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
# LIGHT THEME (v13 "new look"): white background, Solix indigo ink, brand blue / red accents.
BLUE, RED, IND = (0, 136, 207), (238, 36, 36), (48, 38, 123)
TEAL = (0, 160, 150)           # third family colour (Mainframe)
WHITE = (34, 28, 98)           # "primary ink": headings / body text on the white background (name kept from the dark version)
WF = (255, 255, 254)           # true white: text and icons sitting on coloured fills
SKY = (0, 112, 184)            # accent text (kickers, captions) on white
TXT = (74, 86, 138)            # body text
DIM = (128, 140, 180)          # secondary text
CARD = (255, 255, 255)         # card fill
LIGHT = True
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "..", "assets")
PAD = 26

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def pr(t, a, d): return clamp((t - a) / d)
def E(x): x = clamp(x); return 1 - (1 - x) ** 3                       # ease-out cubic
def E5(x): x = clamp(x); return 1 - (1 - x) ** 5
def IO(x): x = clamp(x); return 4 * x**3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def EB(x, k=1.6):                                                      # ease-out-back (soft overshoot)
    x = clamp(x); return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))

# ---------------------------------------------------------------- fonts / text
INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
IDISP = "/usr/share/fonts/opentype/inter/InterDisplay-%s.otf"
MONO = {"Regular": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"}

@lru_cache(None)
def font(kind, weight, size):
    if kind == "m": return ImageFont.truetype(MONO[weight], size)
    return ImageFont.truetype((IDISP if kind == "d" else INTER) % weight, size)

@lru_cache(4096)
def T(s, kind="i", weight="Bold", size=40, color=WHITE, track=0):
    f = font(kind, weight, size)
    asc, desc = f.getmetrics(); pad = 6
    width = f.getlength(s) if not track else sum(f.getlength(c) + track for c in s)
    m = Image.new("L", (int(width) + 2 * pad, asc + desc + 2 * pad), 0); d = ImageDraw.Draw(m)
    if not track: d.text((pad, pad), s, font=f, fill=255)
    else:
        x = pad
        for c in s: d.text((x, pad), c, font=f, fill=255); x += f.getlength(c) + track
    sp = Image.new("RGBA", m.size, tuple(color) + (255,)); sp.putalpha(m); return sp

def tw(s, kind="i", weight="Bold", size=40, track=0):
    f = font(kind, weight, size)
    return f.getlength(s) if not track else sum(f.getlength(c) + track for c in s)

def fit(s, kind, weight, size, maxw):
    while tw(s, kind, weight, size) > maxw and size > 10: size -= 2
    return size

# ---------------------------------------------------------------- shape sprites (2x supersampled)
def _ss(w, h, fn):
    S = 3; im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); fn(d, S)
    return im.resize((w, h), Image.LANCZOS)

@lru_cache(512)
def RR(w, h, r, fill, outline=None, ow=2, shadow=True, glow=None):
    """rounded rect sprite (size w+2PAD, h+2PAD). fill/outline are RGBA tuples."""
    base = Image.new("RGBA", (w + 2 * PAD, h + 2 * PAD), (0, 0, 0, 0))
    if shadow or glow:
        m = Image.new("L", base.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((PAD, PAD + (8 if not glow else 0), PAD + w, PAD + h + (8 if not glow else 0)), r, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(14 if not glow else 16))
        col = glow if glow else (0, 0, 0)
        sh = Image.new("RGBA", base.size, tuple(col) + (255,)); sh.putalpha(m.point(lambda v: int(v * (0.16 if not glow else 0.30))))
        base = Image.alpha_composite(base, sh)
    def fn(d, S):
        d.rounded_rectangle((PAD * S, PAD * S, (PAD + w) * S, (PAD + h) * S), r * S, fill=fill, outline=outline, width=ow * S if outline else 0)
    return Image.alpha_composite(base, _ss(w + 2 * PAD, h + 2 * PAD, fn))

@lru_cache(512)
def CIRCLE(d, fill, outline=None, ow=2, glow=None):
    base = Image.new("RGBA", (d + 2 * PAD, d + 2 * PAD), (0, 0, 0, 0))
    if glow:
        m = Image.new("L", base.size, 0); ImageDraw.Draw(m).ellipse((PAD, PAD, PAD + d, PAD + d), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(14))
        g = Image.new("RGBA", base.size, tuple(glow) + (255,)); g.putalpha(m.point(lambda v: int(v * .30))); base = Image.alpha_composite(base, g)
    def fn(dr, S):
        dr.ellipse((PAD * S, PAD * S, (PAD + d) * S, (PAD + d) * S), fill=fill, outline=outline, width=ow * S if outline else 0)
    return Image.alpha_composite(base, _ss(d + 2 * PAD, d + 2 * PAD, fn))

@lru_cache(512)
def BAR(w, h, color):          # pill without shadow, fully rounded (highlight chips, bars)
    w, h = max(2, int(w)), max(2, int(h))
    def fn(d, S): d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), h * S // 2, fill=tuple(color) + (255,))
    return _ss(w, h, fn)

@lru_cache(512)
def ICON(kind, size, color, lw=0.075):
    S = 4; n = size * S; m = Image.new("L", (n, n), 0); d = ImageDraw.Draw(m); L = max(2, int(n * lw))
    p = lambda x, y: (x * n, y * n)
    if kind == "db":
        d.ellipse((n*.14, n*.08, n*.86, n*.34), outline=255, width=L)
        d.line((n*.14, n*.21, n*.14, n*.78), fill=255, width=L); d.line((n*.86, n*.21, n*.86, n*.78), fill=255, width=L)
        d.arc((n*.14, n*.38, n*.86, n*.64), 0, 180, fill=255, width=L); d.arc((n*.14, n*.62, n*.86, n*.88), 0, 180, fill=255, width=L)
    elif kind == "search":
        d.ellipse((n*.12, n*.12, n*.64, n*.64), outline=255, width=L); d.line((n*.56, n*.56, n*.88, n*.88), fill=255, width=int(L*1.3))
    elif kind == "chart":
        for i, hh in enumerate((.42, .66, .9)):
            x = n*(.16 + i*.27); d.rounded_rectangle((x, n*(.92-hh*.8), x+n*.17, n*.92), n*.03, fill=255)
    elif kind == "lock":
        d.rounded_rectangle((n*.2, n*.44, n*.8, n*.9), n*.08, fill=255)
        d.arc((n*.3, n*.1, n*.7, n*.7), 180, 360, fill=255, width=L); d.line((n*.3, n*.4, n*.3, n*.46), fill=255, width=L); d.line((n*.7, n*.4, n*.7, n*.46), fill=255, width=L)
        d.ellipse((n*.45, n*.58, n*.55, n*.68), fill=0)
    elif kind == "key":
        d.ellipse((n*.1, n*.3, n*.46, n*.66), outline=255, width=L)
        d.line((n*.46, n*.48, n*.92, n*.48), fill=255, width=L); d.line((n*.74, n*.48, n*.74, n*.68), fill=255, width=L); d.line((n*.9, n*.48, n*.9, n*.64), fill=255, width=L)
    elif kind == "check":
        d.line((n*.16, n*.54, n*.4, n*.78), fill=255, width=int(L*1.5)); d.line((n*.4, n*.78, n*.86, n*.24), fill=255, width=int(L*1.5))
    elif kind == "shield":
        d.polygon([p(.5, .06), p(.88, .2), p(.84, .58), p(.5, .94), p(.16, .58), p(.12, .2)], outline=255, width=L)
        d.line((n*.32, n*.5, n*.46, n*.64), fill=255, width=L); d.line((n*.46, n*.64, n*.7, n*.36), fill=255, width=L)
    elif kind == "cloud":
        def cl(dr, f):
            dr.ellipse((n*.12, n*.38, n*.42, n*.7), fill=f); dr.ellipse((n*.28, n*.18, n*.64, n*.66), fill=f)
            dr.ellipse((n*.5, n*.3, n*.86, n*.7), fill=f); dr.rectangle((n*.27, n*.5, n*.72, n*.7), fill=f)
        cl(d, 255); inner = Image.new("L", (n, n), 0); di = ImageDraw.Draw(inner)
        d2 = ImageDraw.Draw(m); k = L * 1.2
        mm = Image.new("L", (n, n), 0); dm = ImageDraw.Draw(mm)
        dm.ellipse((n*.12+k, n*.38+k, n*.42-k, n*.7-k), fill=255); dm.ellipse((n*.28+k, n*.18+k, n*.64-k, n*.66-k), fill=255)
        dm.ellipse((n*.5+k, n*.3+k, n*.86-k, n*.7-k), fill=255); dm.rectangle((n*.27, n*.5, n*.72, n*.7-k), fill=255)
        m = Image.composite(Image.new("L", (n, n), 0), m, mm); d = ImageDraw.Draw(m); d.line((n*.14, n*.7, n*.84, n*.7), fill=255, width=L)
    elif kind == "clock":
        d.ellipse((n*.1, n*.1, n*.9, n*.9), outline=255, width=L); d.line((n*.5, n*.5, n*.5, n*.26), fill=255, width=L); d.line((n*.5, n*.5, n*.68, n*.6), fill=255, width=L)
    elif kind == "dollar":
        d.ellipse((n*.1, n*.1, n*.9, n*.9), outline=255, width=L)
        f = font("i", "Bold", int(n*.56)); d.text((n*.5, n*.52), "$", font=f, fill=255, anchor="mm")
    elif kind == "doc":
        d.rounded_rectangle((n*.2, n*.08, n*.8, n*.92), n*.07, outline=255, width=L)
        for y in (.32, .5, .68): d.line((n*.32, n*y, n*.68, n*y), fill=255, width=L)
    elif kind == "x":
        d.line((n*.2, n*.2, n*.8, n*.8), fill=255, width=int(L*1.4)); d.line((n*.8, n*.2, n*.2, n*.8), fill=255, width=int(L*1.4))
    elif kind == "up":
        d.line((n*.5, n*.85, n*.5, n*.2), fill=255, width=L); d.line((n*.24, n*.46, n*.5, n*.18), fill=255, width=L); d.line((n*.76, n*.46, n*.5, n*.18), fill=255, width=L)
    elif kind == "down":
        d.line((n*.5, n*.15, n*.5, n*.8), fill=255, width=L); d.line((n*.24, n*.54, n*.5, n*.82), fill=255, width=L); d.line((n*.76, n*.54, n*.5, n*.82), fill=255, width=L)
    elif kind == "arrow":
        d.line((n*.12, n*.5, n*.84, n*.5), fill=255, width=L); d.line((n*.58, n*.24, n*.86, n*.5), fill=255, width=L); d.line((n*.58, n*.76, n*.86, n*.5), fill=255, width=L)
    elif kind == "layers":
        for k, y in enumerate((.3, .5, .7)):
            d.polygon([p(.5, y-.2), p(.9, y), p(.5, y+.2), p(.1, y)], outline=255, width=L)
    elif kind == "gear":
        d.ellipse((n*.3, n*.3, n*.7, n*.7), outline=255, width=L)
        for a in range(0, 360, 45):
            x, y = .5 + .34*math.cos(math.radians(a)), .5 + .34*math.sin(math.radians(a))
            d.ellipse((n*(x-.07), n*(y-.07), n*(x+.07), n*(y+.07)), fill=255)
    elif kind == "box":
        d.polygon([p(.5, .08), p(.88, .28), p(.88, .72), p(.5, .92), p(.12, .72), p(.12, .28)], outline=255, width=L)
        d.line((n*.12, n*.28, n*.5, n*.48), fill=255, width=L); d.line((n*.88, n*.28, n*.5, n*.48), fill=255, width=L); d.line((n*.5, n*.48, n*.5, n*.92), fill=255, width=L)
    elif kind == "star":
        pts = []
        for i in range(10):
            r = .44 if i % 2 == 0 else .18; a = math.radians(-90 + i * 36); pts.append(p(.5 + r*math.cos(a), .52 + r*math.sin(a)))
        d.polygon(pts, fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    sp = Image.new("RGBA", (size, size), tuple(color) + (255,)); sp.putalpha(m); return sp

@lru_cache(None)
def LOGO(h):
    im = Image.open(os.path.join(ASSETS, "original", "solix_logo_black_tagline.png")).convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)

@lru_cache(None)
def EVENT_LOGO(h):
    im = Image.open(os.path.join(ASSETS, "original", "solix_ai_data_cloud_red.png")).convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)

@lru_cache(None)
def BOLT(d):
    im = Image.open(os.path.join(ASSETS, "original", "solix_mark_bolt.png")).convert("RGBA"); return im.resize((d, d), Image.LANCZOS)

# ---------------------------------------------------------------- compositing context
class Ctx:
    """one scene's draw target: premultiplied sprite layer + additive light canvas."""
    def __init__(s, L, G, O):
        s.L, s.G0, s.O, s.ox, s.oy, s.ga, s.top = L, G, O, 0, 0, 1.0, False
    @property
    def G(s): return s.O if s.top else s.G0
    def blit(s, sp, x, y, a=1.0, sc=1.0, c=False):
        a *= s.ga
        if a <= 0.004 or sc <= 0.001: return
        if sc != 1.0: sp = sp.resize((max(1, round(sp.width * sc)), max(1, round(sp.height * sc))), Image.BILINEAR)
        w, h = sp.size
        if c: x -= w / 2; y -= h / 2
        x = int(round(x + s.ox)); y = int(round(y + s.oy))
        x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
        if x0 >= x1 or y0 >= y1: return
        arr = np.asarray(sp)[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32) * (1 / 255)
        al = arr[..., 3:4] * a; d = s.L[y0:y1, x0:x1]
        d[..., :3] = arr[..., :3] * al + d[..., :3] * (1 - al); d[..., 3:4] = al + d[..., 3:4] * (1 - al)
    def card(s, x, y, w, h, a=1.0, sc=1.0, fill=None, outline=None, r=22, glow=None, c=False):
        fill = fill or CARD + (226,); outline = outline or BLUE + (150,)
        sp = RR(int(w), int(h), r, tuple(fill), tuple(outline), 2, glow is None, glow)
        s.blit(sp, x + w / 2, y + h / 2, a, sc, True)
    def text(s, st, x, y, kind="i", weight="Bold", size=40, color=WHITE, a=1.0, track=0, anchor="l", sc=1.0):
        sp = T(st, kind, weight, size, tuple(color), track); w = sp.width - 12
        if anchor == "c": x -= w * sc / 2
        elif anchor == "r": x -= w * sc
        s.blit(sp, x - 6 * sc, y - 6 * sc, a, sc)
    def icon(s, kind, x, y, size, color, a=1.0, sc=1.0, c=True): s.blit(ICON(kind, int(size), tuple(color)), x, y, a, sc, c)
    # ---- additive light primitives (glow canvas, uint8 BGR)
    def _col(s, color, a): k = min(1.0, a * s.ga); return (int(color[2] * k), int(color[1] * k), int(color[0] * k), int(255 * k))
    def line(s, p0, p1, color, a=1.0, th=2):
        cv2.line(s.G, (int(p0[0] + s.ox), int(p0[1] + s.oy)), (int(p1[0] + s.ox), int(p1[1] + s.oy)), s._col(color, a), th, cv2.LINE_AA)
    def poly(s, pts, color, a=1.0, th=2):
        q = np.array([[int(x + s.ox), int(y + s.oy)] for x, y in pts], np.int32)
        cv2.polylines(s.G, [q], False, s._col(color, a), th, cv2.LINE_AA)
    def dot(s, p, r, color, a=1.0):
        cv2.circle(s.G, (int(p[0] + s.ox), int(p[1] + s.oy)), int(r), s._col(color, a), -1, cv2.LINE_AA)
    def ring(s, p, r, color, a=1.0, th=2):
        cv2.circle(s.G, (int(p[0] + s.ox), int(p[1] + s.oy)), int(r), s._col(color, a), th, cv2.LINE_AA)
    def dashed(s, p0, p1, color, a=1.0, th=2, dash=12, gap=10, off=0.0):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L; d = -off % (dash + gap) - (dash + gap)
        while d < L:
            a0, a1 = max(0, d), min(L, d + dash)
            if a1 > a0: s.line((p0[0] + ux * a0, p0[1] + uy * a0), (p0[0] + ux * a1, p0[1] + uy * a1), color, a, th)
            d += dash + gap
    def pulse(s, p0, p1, t, speed=0.8, phase=0.0, color=WHITE, r=5, a=1.0, trail=0.12):
        k = (t * speed + phase) % 1.0
        for j in range(5):
            kk = k - j * trail / 5
            if kk < 0: continue
            q = (lerp(p0[0], p1[0], kk), lerp(p0[1], p1[1], kk)); s.dot(q, max(1, r - j), color, a * (1 - j / 5))

def bezier(p0, p1, p2, k):
    return ((1 - k) ** 2 * p0[0] + 2 * (1 - k) * k * p1[0] + k * k * p2[0], (1 - k) ** 2 * p0[1] + 2 * (1 - k) * k * p1[1] + k * k * p2[1])

# ---------------------------------------------------------------- background (dark blue + AI network)
def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([255, 255, 255], np.float32); mid = np.array([240, 246, 255], np.float32)
    r = np.sqrt(((xx - .60 * W) / W) ** 2 + ((yy - .42 * H) / H) ** 2 * 1.4)
    bg = mid + (base - mid) * np.clip(1 - r / .85, 0, 1)[..., None] ** 1.2          # faint blue wash toward the corners
    g1 = np.exp(-(((xx - .02 * W) / (.35 * W)) ** 2 + ((yy - 1.0 * H) / (.45 * H)) ** 2))[..., None] * np.array([-10, -12, -34], np.float32) * .55   # indigo tint, bottom-left
    g2 = np.exp(-(((xx - .98 * W) / (.30 * W)) ** 2 + ((yy - 0.0 * H) / (.40 * H)) ** 2))[..., None] * np.array([-30, -12, 0], np.float32) * .55      # sky tint, top-right
    return np.clip(bg + g1 + g2, 0, 255).astype(np.uint8)

NET_OPACITY = 0.26          # AI-network lines/nodes (ink on white)

class Net:
    N = 70
    def __init__(s):
        rs = np.random.RandomState(11)
        s.b = rs.rand(s.N, 2) * [W * 1.05, H * 1.05] - [30, 30]; s.amp = rs.rand(s.N, 2) * 46 + 18
        s.fr = rs.rand(s.N, 2) * .16 + .05; s.ph = rs.rand(s.N, 2) * 6.28; s.d = rs.rand(s.N) * .6 + .4; s.c = rs.rand(s.N)
        s.pp = rs.rand(400)
    def draw(s, t, energy=0.0, shift=(0, 0)):
        cv = np.zeros((H, W, 4), np.uint8)
        P = s.b + s.amp * np.sin(s.fr * t * 6.283 + s.ph) + np.array(shift)[None] * s.d[:, None]
        dx = P[:, None, 0] - P[None, :, 0]; dy = P[:, None, 1] - P[None, :, 1]; D = np.sqrt(dx * dx + dy * dy)
        I, J = np.where(np.triu(D < 260, 1)); en = 1.05 + 1.2 * energy
        def ink(col, a): a = min(1.0, a * NET_OPACITY * 1.8); return (int(col[2] * a), int(col[1] * a), int(col[0] * a), int(255 * a))
        for k, (i, j) in enumerate(zip(I, J)):
            a = (1 - D[i, j] / 260) * .62 * en * (s.d[i] + s.d[j]) / 2
            col = ink(BLUE, a) if (i + j) % 7 else ink(RED, a * .8)
            cv2.line(cv, (int(P[i, 0]), int(P[i, 1])), (int(P[j, 0]), int(P[j, 1])), col, 1, cv2.LINE_AA)
            if k % 4 == 0:
                u = (t * (.28 + .1 * s.pp[k % 400]) + s.pp[k % 400]) % 1
                q = (int(lerp(P[i, 0], P[j, 0], u)), int(lerp(P[i, 1], P[j, 1], u)))
                cv2.circle(cv, q, 2, ink(IND, min(1, a * 3.2 * en)), -1, cv2.LINE_AA)
        for i in range(s.N):
            r = 2 + int(2 * s.d[i]); b = (.55 + .45 * math.sin(t * 1.4 + s.ph[i, 0])) * (.6 + .6 * energy) * s.d[i]
            col = (RED if s.c[i] > .93 else TEAL if s.c[i] < .15 else BLUE)
            cv2.circle(cv, (int(P[i, 0]), int(P[i, 1])), r, ink(col, b), -1, cv2.LINE_AA)
        return cv

def ink_over(frame, G):
    """composite a premultiplied BGRA ink canvas over a BGR uint8 frame (light theme: no bloom, no additive light)."""
    al = G[..., 3:4].astype(np.float32) * (1 / 255)
    return np.clip(frame.astype(np.float32) * (1 - al) + G[..., :3].astype(np.float32), 0, 255).astype(np.uint8)

def glow_add(frame, G, k=1.0):
    """frame uint8 + light canvas + its blur (bloom)."""
    sm = cv2.resize(G, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bl = cv2.GaussianBlur(sm, (0, 0), 5); bl = cv2.resize(bl, (W, H), interpolation=cv2.INTER_LINEAR)
    out = frame.astype(np.float32) + G.astype(np.float32) * k + bl.astype(np.float32) * 1.6 * k
    return np.clip(out, 0, 255).astype(np.uint8)


def bolt_solix(c, x, y, d, a=1.0, name_size=None):
    """the red bolt mark is never shown alone: SOLIX sits beneath it (manager). (x, y) = top-left of the mark."""
    ns = name_size or max(10, int(d * .2)); bw = tw("SOLIX", "d", "Bold", ns, 2)
    c.blit(BOLT(d), x, y, a, 1, False)
    c.text("SOLIX", x + d / 2, y + d + 1, "d", "Bold", ns, WHITE, a, track=2, anchor="c")
    return d + ns + 6
