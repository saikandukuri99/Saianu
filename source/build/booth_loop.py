# Solix Enterprise AI - booth loop (white edition)
# Silent, seamless 90 s loop: white background, live tech network in #0088cf / #ee2424,
# product screens from the v4 booth loop in a floating browser card, kinetic text.
# Usage: python3 booth_loop.py SRC.mp4 OUT.mp4 [--frames a:b] [--still t1,t2,...]
import sys, os, math, subprocess, argparse
import numpy as np
import skia

B = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(B)
W, H, FPS = 1920, 1080, 30
T = 90.0
NF = int(T * FPS)

BLUE = (0, 136, 207)      # #0088cf
RED = (238, 36, 36)       # #ee2424
INDIGO = (48, 38, 123)    # #30267b
INK = (34, 36, 58)
BODY = (78, 84, 108)
MUTE = (150, 156, 178)
FD = "/usr/share/fonts/opentype/inter/"


def col(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(1, a)) * 255))


TF = {k: skia.Typeface.MakeFromFile(FD + f) for k, f in {
    "black": "InterDisplay-Black.otf", "xbold": "InterDisplay-ExtraBold.otf", "bold": "InterDisplay-Bold.otf",
    "semi": "Inter-SemiBold.otf", "med": "Inter-Medium.otf", "reg": "Inter-Regular.otf"}.items()}
_fonts = {}


def font(k, size):
    key = (k, size)
    if key not in _fonts:
        f = skia.Font(TF[k], size)
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        _fonts[key] = f
    return _fonts[key]


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, d):
    return clamp((t - t0) / d) if d > 0 else float(t >= t0)


def e_out3(x):
    return 1 - (1 - x) ** 3


def e_outx(x):
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def e_io(x):
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def e_back(x, s=1.70158):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, x):
    return a + (b - a) * x


# ------------------------------------------------------------------ storyboard
# src: [start, end] of the product-screen recording in the v4 source loop
SCENES = [
    dict(key="ds", t0=6.5, t1=20.0, src=(6.40, 18.60), nav=0, url="solix.com/data-sense",
         kick="DATA SENSE", head="Make your data |ready for AI.|",
         body="AKGs for your applications. AI drafts the meaning; your experts certify it."),
    dict(key="cur", t0=20.0, t1=31.5, src=(19.95, 30.50), nav=0, url="solix.com/data-sense/curation",
         kick="DATA SENSE · CURATION", head="Experts stay |in the loop.|",
         body="AI proposes the meaning. Your experts decide, in the order that matters."),
    dict(key="ask", t0=31.5, t1=45.5, src=(31.50, 44.55), nav=1, url="solix.com/data-ask",
         kick="DATA ASK", head="Ask in plain words. Get |cited answers.|",
         body="Every answer carries the certified definition, the tables it used and the SQL it ran."),
    dict(key="xkg", t0=45.5, t1=58.0, src=(45.50, 57.00), nav=2, url="solix.com/xkg",
         kick="XKG", head="|One meaning| across every application.",
         body="Each application answers through its own AKG. XKG combines results using certified business meaning."),
    dict(key="aiw", t0=58.0, t1=69.5, src=(58.00, 68.55), nav=3, url="solix.com/ai-warehouse",
         kick="AI WAREHOUSE", head="Build AI apps on |governed data.|",
         body="Notebooks start from data products that already carry their meaning and rules."),
    dict(key="agt", t0=69.5, t1=81.5, src=(69.50, 80.55), nav=4, url="solix.com/agentic",
         kick="AGENTIC", head="Agents that |build, test and run.|",
         body="Every step is logged. A person approves each gate."),
]
OPEN = dict(t0=81.5, t1=88.6, kick="OPEN BY DESIGN", head="Fits the stack |you already run.|",
            body="Any LLM. Any application. Any data platform.")
NAV = ["Data Sense", "Data Ask", "XKG", "AI Warehouse", "Agentic"]
SOFTCUTS = [10.933]            # hard cuts inside a source segment, softened with a dissolve
TR = 0.9                       # screen-to-screen transition length
CARD_IN = (6.0, 1.3)           # card fly-in after the intro
CARD_OUT = (81.15, 0.9)
END_OUT = 88.6                 # everything clears; 89.4-90 is the bare network = frame 0


def src_time(sc, t):
    """Map loop time to source time (content plays as the scene's own clock, held at the ends)."""
    a, b = sc["src"]
    slot = (sc["t1"] - sc["t0"]) - 0.6
    r = (b - a) / slot
    return clamp(a + (t - sc["t0"] - 0.15) * r, a, b - 1 / FPS)


# ------------------------------------------------------------------ source reader
CROP = (625, 135, 1220, 700)   # x, y, w, h of the product window in the source frame


class Source:
    def __init__(self, path, need):
        self.need = need                       # list per output frame of needed src frame indices
        lo = min(min(n) for n in need if n) if any(need) else 0
        self.base = max(0, lo - 2)
        x, y, w, h = CROP
        self.w, self.h = w, h
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{self.base / FPS:.4f}", "-i", path,
                                   "-vf", f"crop={w}:{h}:{x}:{y}", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                                  stdout=subprocess.PIPE)
        self.pos = self.base
        self.cache = {}
        self.last_use = {}
        for i, n in enumerate(need):
            for k in n:
                self.last_use[k] = i

    def frame(self, idx, now):
        while self.pos <= idx:
            buf = self.p.stdout.read(self.w * self.h * 4)
            if len(buf) < self.w * self.h * 4:
                break
            if self.pos in self.last_use:
                self.cache[self.pos] = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 4)
            self.pos += 1
        for k in [k for k in self.cache if self.last_use.get(k, -1) < now]:
            del self.cache[k]
        if idx in self.cache:
            return self.cache[idx]
        if self.cache:
            return self.cache[min(self.cache, key=lambda k: abs(k - idx))]
        return np.zeros((self.h, self.w, 4), np.uint8)


def src_indices(sc, t):
    st = src_time(sc, t)
    i = int(round(st * FPS))
    out = [i]
    for c in SOFTCUTS:
        if c <= st < c + 0.45:
            out.append(int(round(c * FPS)) - 1)
    return out, st


def content_needs(t):
    """Which scenes' screens are visible at t and with what wipe progress."""
    res = []
    for k, sc in enumerate(SCENES):
        a = sc["t0"] - (TR / 2 if k else 0)
        b = sc["t1"] + (TR / 2 if k < len(SCENES) - 1 else 0)
        if k == 0:
            a = CARD_IN[0]
        if a <= t < b:
            res.append(k)
    return res


def frame_needs(f):
    t = f / FPS
    out = []
    for k in content_needs(t):
        idx, _ = src_indices(SCENES[k], t)
        out += idx
    return out


def to_image(arr):
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)


# ------------------------------------------------------------------ background network
rng = np.random.default_rng(7)
NN = 112
NB = np.c_[rng.uniform(-60, W + 60, NN), rng.uniform(-60, H + 60, NN)]
NA = rng.uniform(25, 70, (NN, 2))
NK = rng.integers(1, 3, (NN, 2))          # integer harmonics -> exactly periodic over T
NP = rng.uniform(0, 2 * np.pi, (NN, 2))
NR = rng.random(NN) < 0.26                # red nodes
NS = rng.uniform(2.2, 4.6, NN)
LINK = 205.0


def nodes(t):
    ph = 2 * np.pi * t / T
    return NB + NA * np.sin(NK * ph + NP)


def soft_mask(x, y):
    """Fade the network down behind the text column so the copy stays clean."""
    d = np.clip((x - 120) / 600, 0, 1)
    k = 1 - 0.55 * np.exp(-((x - 360) / 330) ** 2 - ((y - 520) / 300) ** 2)
    return k


def draw_bg(c, t):
    c.clear(skia.ColorWHITE)
    # soft colour fields for depth
    for (cx, cy, r, cc, a) in [(220, 120, 900, BLUE, .07), (1780, 1000, 900, RED, .055), (1500, 120, 620, BLUE, .045)]:
        p = skia.Paint(Shader=skia.GradientShader.MakeRadial(
            (cx, cy), r, [col(cc, a), col(cc, 0)]))
        c.drawRect(skia.Rect(0, 0, W, H), p)
    P = nodes(t)
    dx = P[:, None, 0] - P[None, :, 0]
    dy = P[:, None, 1] - P[None, :, 1]
    D = np.sqrt(dx * dx + dy * dy)
    m = soft_mask(P[:, 0], P[:, 1])
    lp = skia.Paint(AntiAlias=True, StrokeWidth=1.15, Style=skia.Paint.kStroke_Style)
    ii, jj = np.nonzero(np.triu(D < LINK, 1))
    for i, j in zip(ii, jj):
        a = (1 - D[i, j] / LINK) ** 1.3 * 0.55 * min(m[i], m[j])
        cc = RED if (NR[i] and NR[j]) else BLUE
        lp.setColor(col(cc, a))
        c.drawLine(P[i, 0], P[i, 1], P[j, 0], P[j, 1], lp)
        # data pulses travelling along a subset of links (periodic over T)
        h = (i * 73856093 ^ j * 19349663) & 0xffff
        if h % 5 == 0:
            ph = (t / T * (6 + h % 5) + (h % 97) / 97.0) % 1.0
            px, py = lerp(P[i, 0], P[j, 0], ph), lerp(P[i, 1], P[j, 1], ph)
            pa = a * 2.2 * math.sin(math.pi * ph)
            c.drawCircle(px, py, 2.4, skia.Paint(AntiAlias=True, Color=col(RED if h % 3 == 0 else BLUE, pa)))
    np_ = skia.Paint(AntiAlias=True)
    for i in range(NN):
        cc = RED if NR[i] else BLUE
        a = 0.85 * m[i]
        tw = 0.5 + 0.5 * math.sin(2 * math.pi * (t / T * (8 + i % 5)) + NP[i, 0])
        np_.setColor(col(cc, a * 0.16 * tw))
        c.drawCircle(P[i, 0], P[i, 1], NS[i] * 3.2, np_)
        np_.setColor(col(cc, a))
        c.drawCircle(P[i, 0], P[i, 1], NS[i], np_)
        np_.setColor(col((255, 255, 255), a))
        c.drawCircle(P[i, 0], P[i, 1], NS[i] * 0.38, np_)


# ------------------------------------------------------------------ logo
LOGO = np.array(__import__("PIL.Image", fromlist=["Image"]).open(f"{S}/assets/logo.png").convert("RGBA"))
LOGO_ICON = to_image(LOGO[:, :392])
LOGO_WORD = to_image(LOGO[:, 400:1797][:300])
LOGO_TAG = to_image(LOGO[:, 400:1797][300:])


def draw_logo(c, x, y, h, t_icon=1.0, t_word=1.0, t_tag=1.0, alpha=1.0, spin=True):
    """Solix logo with its icon top-left at (x, y), icon height h."""
    s = h / 394.0
    sm = skia.SamplingOptions(skia.CubicResampler.Mitchell())
    if t_icon > 0:
        k = e_back(clamp(t_icon), 2.2) if t_icon < 1 else 1.0
        c.save()
        cx, cy = x + 196 * s, y + 197 * s
        c.translate(cx, cy)
        c.scale(k, k)
        if spin:
            c.rotate(-120 * (1 - e_out3(clamp(t_icon))))
        c.drawImageRect(LOGO_ICON, skia.Rect(-196 * s, -197 * s, 196 * s, 197 * s), sm,
                        skia.Paint(Alphaf=alpha * clamp(t_icon * 3)))
        c.restore()
    if t_word > 0:
        w = 1397 * s
        e = e_outx(clamp(t_word))
        c.save()
        c.clipRect(skia.Rect(x + 392 * s, y - 10, x + 392 * s + 18 * s + w * e, y + 300 * s + 6))
        c.drawImageRect(LOGO_WORD, skia.Rect(x + 400 * s - (1 - e) * 120 * s, y, x + 400 * s + w - (1 - e) * 120 * s, y + 300 * s),
                        sm, skia.Paint(Alphaf=alpha))
        c.restore()
    if t_tag > 0:
        c.drawImageRect(LOGO_TAG, skia.Rect(x + 400 * s, y + 300 * s + (1 - e_out3(t_tag)) * 10, x + 1797 * s,
                                            y + 394 * s + (1 - e_out3(t_tag)) * 10), sm,
                        skia.Paint(Alphaf=alpha * clamp(t_tag)))


# ------------------------------------------------------------------ text helpers
def spaced(c, txt, x, y, f, color, track, alpha=1.0, t_in=1.0, stagger=0.025):
    """Letter-spaced caps with a per-letter rise/fade-in. Returns the advance."""
    p = skia.Paint(AntiAlias=True)
    n = len(txt)
    for i, ch in enumerate(txt):
        li = clamp((t_in * (1 + n * stagger) - i * stagger) / 1.0) if t_in < 1 else 1.0
        e = e_out3(li)
        p.setColor(col(color, alpha * e))
        c.drawString(ch, x + (1 - e) * 14, y, f, p)
        x += f.measureText(ch) + track
    return x


def width_spaced(txt, f, track):
    return sum(f.measureText(ch) + track for ch in txt) - track


def wrap_words(words, f, maxw):
    lines, cur, cw = [], [], 0
    sp = f.measureText(" ")
    for w in words:
        ww = f.measureText(w[0])
        if cur and cw + sp + ww > maxw:
            lines.append(cur)
            cur, cw = [], 0
        cur.append(w)
        cw += (sp if len(cur) > 1 else 0) + ww
    if cur:
        lines.append(cur)
    return lines


def parse_head(s):
    out, hi = [], False
    for part in s.split("|"):
        for w in part.split():
            out.append((w, hi))
        hi = not hi
    return out


class TextBlock:
    """Kicker + headline + body for one scene, with AE-style in/out animation."""

    def __init__(self, sc, x=110, maxw=530, cy=505, hsize=66):
        self.sc, self.x, self.maxw = sc, x, maxw
        self.fk = font("semi", 21)
        self.fh = font("xbold", hsize)
        self.fb = font("reg", 27)
        self.hl = wrap_words(parse_head(sc["head"]), self.fh, maxw)
        self.bl = [[w for w, _ in ln] for ln in wrap_words([(w, 0) for w in sc["body"].split()], self.fb, maxw - 40)]
        self.lh = hsize * 1.1
        self.bh = 27 * 1.5
        hgt = 34 + 30 + len(self.hl) * self.lh + 28 + len(self.bl) * self.bh
        self.y0 = cy - hgt / 2

    def draw(self, c, t, t_in, t_out):
        """t_in: start of the build, t_out: start of the exit."""
        x, y = self.x, self.y0
        out = e_io(prog(t, t_out, 0.7))
        if out >= 1 or t < t_in:
            return
        oy = -40 * out

        def oa(order):  # staggered exit alpha
            return 1 - clamp((t - t_out - order * 0.07) / 0.45)

        # kicker: red dash grows, letters track in
        k = prog(t, t_in, 0.5)
        a = oa(0)
        dash = 46 * e_out3(k)
        c.drawRect(skia.Rect(x, y + 12 + oy, x + dash, y + 15.5 + oy), skia.Paint(Color=col(RED, a)))
        kx = spaced(c, self.sc["kick"], x + 64, y + 22 + oy, self.fk, BLUE, 6.5, a, prog(t, t_in + 0.12, 0.7))
        if self.sc.get("tag"):
            tg = prog(t, t_in + 0.6, 0.45)
            if tg > 0:
                ft = font("bold", 15)
                tw = width_spaced(self.sc["tag"], ft, 2.5)
                bx, by = kx + 16, y + 1 + oy
                sc_ = e_back(tg, 2.0)
                c.save()
                c.translate(bx + (tw + 26) / 2, by + 15)
                c.scale(sc_, sc_)
                rr = skia.RRect.MakeRectXY(skia.Rect(-(tw + 26) / 2, -15, (tw + 26) / 2, 15), 15, 15)
                c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=col(RED, a * clamp(tg * 2))))
                spaced(c, self.sc["tag"], -tw / 2, 5.5, ft, (255, 255, 255), 2.5, a * clamp(tg * 2))
                c.restore()
        # headline: masked word rise, highlighted phrase in brand blue with a red underline sweep
        y += 34 + 30
        hp = skia.Paint(AntiAlias=True)
        sp = self.fh.measureText(" ")
        wi = 0
        hl_spans = []
        for li, ln in enumerate(self.hl):
            bx = x
            base = y + li * self.lh + self.fh.getSize() * 0.80
            c.save()
            c.clipRect(skia.Rect(x - 20, base - self.fh.getSize() * 1.0 + oy, x + self.maxw + 200, base + self.fh.getSize() * 0.28 + oy))
            for w, hi in ln:
                ww = self.fh.measureText(w)
                wp = e_outx(prog(t, t_in + 0.35 + wi * 0.075, 0.9))
                dy = (1 - wp) * self.lh
                hp.setColor(col(BLUE if hi else INDIGO, oa(1 + li * 0.5)))
                c.drawString(w, bx, base + dy + oy, self.fh, hp)
                if hi:
                    hl_spans.append((bx, bx + ww, base, wi))
                bx += ww + sp
                wi += 1
            c.restore()
        # underline per highlighted line
        if hl_spans:
            first = hl_spans[0][3]
            lines = {}
            for x0, x1, base, _ in hl_spans:
                L = lines.setdefault(base, [x0, x1])
                L[0], L[1] = min(L[0], x0), max(L[1], x1)
            u = e_io(prog(t, t_in + 0.55 + wi * 0.075, 0.6))
            tot = sum(v[1] - v[0] for v in lines.values())
            acc = u * tot
            for base, (x0, x1) in sorted(lines.items()):
                seg = min(acc, x1 - x0)
                acc -= seg
                if seg > 0:
                    yy = base + 14 + oy
                    sh = skia.GradientShader.MakeLinear([(x0, 0), (x1, 0)], [col(RED, oa(2)), col((255, 92, 92), oa(2))])
                    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0, yy, x0 + seg, yy + 6), 3, 3),
                                skia.Paint(AntiAlias=True, Shader=sh))
        # body lines
        y += len(self.hl) * self.lh + 28
        bp = skia.Paint(AntiAlias=True)
        for li, ln in enumerate(self.bl):
            bpg = e_out3(prog(t, t_in + 0.95 + li * 0.12, 0.7))
            bp.setColor(col(BODY, bpg * oa(3 + li * 0.5)))
            c.drawString(" ".join(ln), x, y + li * self.bh + 27 + (1 - bpg) * 18 + oy, self.fb, bp)


# ------------------------------------------------------------------ chrome: nav, pill, corners
def draw_chrome(c, t):
    a_in = e_out3(prog(t, 4.6, 0.9))
    a_out = 1 - e_io(prog(t, END_OUT + 0.15, 0.7))
    a = a_in * a_out
    if a <= 0:
        return
    # corner brackets
    bp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2, Color=col((180, 192, 210), a))
    L = 30 * a
    for (x, y, sx, sy) in [(44, 44, 1, 1), (W - 44, 44, -1, 1), (44, H - 44, 1, -1), (W - 44, H - 44, -1, -1)]:
        c.drawLine(x, y, x + sx * L, y, bp)
        c.drawLine(x, y, x, y + sy * L, bp)
    # bottom navigation with active state + scene progress
    f = font("med", 22)
    fa = font("semi", 22)
    x = 110
    y = 985 + (1 - a_in) * 30
    active, pr = None, 0
    for sc in SCENES:
        if sc["t0"] <= t < sc["t1"]:
            active = sc["nav"]
    grp = [s for s in SCENES if active is not None and s["nav"] == active]
    if grp:
        pr = prog(t, grp[0]["t0"], grp[-1]["t1"] - grp[0]["t0"])
    all_on = OPEN["t0"] <= t
    for i, name in enumerate(NAV):
        on = (i == active) or all_on
        tw = (fa if on else f).measureText(name)
        dp = skia.Paint(AntiAlias=True)
        if on:
            puls = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.5)
            dp.setColor(col(BLUE, a * 0.25 * (1 - puls)))
            c.drawCircle(x + 6, y - 7, 6 + 9 * puls, dp)
            dp.setColor(col(BLUE, a))
            c.drawCircle(x + 6, y - 7, 6, dp)
        else:
            dp.setColor(col(MUTE, a * 0.8))
            c.drawCircle(x + 6, y - 7, 4.5, dp)
        tp = skia.Paint(AntiAlias=True, Color=col(INDIGO if on else MUTE, a))
        c.drawString(name, x + 22, y, fa if on else f, tp)
        if i == active and not all_on:
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x + 22, y + 14, x + 22 + tw, y + 17), 1.5, 1.5),
                        skia.Paint(AntiAlias=True, Color=col((222, 228, 238), a)))
            sh = skia.GradientShader.MakeLinear([(x + 22, 0), (x + 22 + tw, 0)], [col(BLUE, a), col(RED, a)])
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x + 22, y + 14, x + 22 + tw * pr, y + 17), 1.5, 1.5),
                        skia.Paint(AntiAlias=True, Shader=sh))
        x += 22 + tw + 46
    # live demo pill
    fp = font("semi", 21)
    txt = "Live demo at this stand"
    tw = fp.measureText(txt)
    pw, ph = tw + 70, 46
    px, py = W - 110 - pw, 985 - 31 + (1 - a_in) * 30
    rr = skia.RRect.MakeRectXY(skia.Rect(px, py, px + pw, py + ph), 23, 23)
    c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=col(RED, a)))
    puls = (t / 1.5) % 1.0
    c.drawCircle(px + 28, py + 23, 6 + 10 * puls, skia.Paint(AntiAlias=True, Color=col((255, 255, 255), a * 0.45 * (1 - puls))))
    c.drawCircle(px + 28, py + 23, 6, skia.Paint(AntiAlias=True, Color=col((255, 255, 255), a)))
    c.drawString(txt, px + 46, py + 30.5, fp, skia.Paint(AntiAlias=True, Color=col((255, 255, 255), a)))


# ------------------------------------------------------------------ product card
CX, CY, CW = 690, 168, 1140     # card content box (screen) left/top/width
CHR = 44                        # browser chrome height
CH = CW * CROP[3] / CROP[2]
SAMP = skia.SamplingOptions(skia.CubicResampler.Mitchell())


def card_rect():
    return skia.Rect(CX, CY, CX + CW, CY + CHR + CH)


def shadow(c, rect, rad, a):
    for (blur, dy, al) in [(60, 34, .16), (18, 10, .10)]:
        p = skia.Paint(AntiAlias=True, Color=col((30, 34, 80), al * a),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur / 2))
        c.drawRRect(skia.RRect.MakeRectXY(rect.makeOffset(0, dy), rad, rad), p)


def draw_card(c, t, src):
    ks = content_needs(t)
    if not ks:
        return
    pin = e_outx(prog(t, CARD_IN[0], CARD_IN[1]))
    pout = e_io(prog(t, CARD_OUT[0], CARD_OUT[1]))
    alpha = clamp(prog(t, CARD_IN[0], 0.5)) * (1 - pout)
    if alpha <= 0:
        return
    r = card_rect()
    c.save()
    # entrance: slide in from the right with a slight scale + perspective-ish skew; exit: drift right
    sc = lerp(0.9, 1.0, pin) * lerp(1.0, 0.94, pout)
    ox = (1 - pin) * 380 + pout * 260
    float_y = 4 * math.sin(2 * math.pi * t / 7.5)   # 90/7.5 = 12 cycles, loop-safe
    cx, cy = r.centerX(), r.centerY()
    c.translate(cx + ox, cy + float_y)
    c.scale(sc, sc)
    c.translate(-cx, -cy)
    c.saveLayerAlpha(None, int(alpha * 255))
    rad = 18
    shadow(c, r, rad, 1)
    rr = skia.RRect.MakeRectXY(r, rad, rad)
    c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=col((255, 255, 255))))
    c.save()
    c.clipRRect(rr, True)
    # chrome
    c.drawRect(skia.Rect(r.left(), r.top(), r.right(), r.top() + CHR), skia.Paint(Color=col((244, 246, 250))))
    for i, cc in enumerate([RED, (245, 179, 1), BLUE]):
        c.drawCircle(r.left() + 26 + i * 22, r.top() + CHR / 2, 6.5, skia.Paint(AntiAlias=True, Color=col(cc)))
    ub = skia.Rect(r.left() + 120, r.top() + 9, r.right() - 120, r.top() + CHR - 9)
    c.drawRRect(skia.RRect.MakeRectXY(ub, 13, 13), skia.Paint(AntiAlias=True, Color=col((255, 255, 255))))
    c.drawRRect(skia.RRect.MakeRectXY(ub, 13, 13), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                               StrokeWidth=1, Color=col((222, 227, 236))))
    # lock glyph + url (crossfades between scenes)
    lx, ly = ub.left() + 18, ub.centerY()
    lp = skia.Paint(AntiAlias=True, Color=col((40, 160, 90)), Style=skia.Paint.kStroke_Style, StrokeWidth=1.6)
    c.drawArc(skia.Rect(lx - 4, ly - 8, lx + 4, ly), 180, 180, False, lp)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(lx - 6, ly - 3, lx + 6, ly + 6), 2, 2),
                skia.Paint(AntiAlias=True, Color=col((40, 160, 90))))
    fu = font("med", 17)
    content = r.makeInset(0, 0)
    content = skia.Rect(r.left(), r.top() + CHR, r.right(), r.bottom())
    c.drawRect(content, skia.Paint(Color=col((11, 12, 26))))
    for k in ks:
        sc_ = SCENES[k]
        # wipe progress: 0 = hidden, 1 = fully shown
        if k == 0:
            w = 1.0
        else:
            w = e_io(prog(t, sc_["t0"] - TR / 2, TR))
        ua = clamp((w - 0.55) / 0.2) if k else 1.0
        if k + 1 in ks:
            ua *= 1 - clamp((e_io(prog(t, SCENES[k + 1]["t0"] - TR / 2, TR)) - 0.2) / 0.2)
        uw = fu.measureText(sc_["url"])
        c.drawString(sc_["url"], ub.centerX() - uw / 2, ub.centerY() + 6, fu,
                     skia.Paint(AntiAlias=True, Color=col((90, 96, 120), ua)))
        idx, st = src_indices(sc_, t)
        img = to_image(src.frame(idx[0], src_now))
        # slow push-in across the scene
        z = 1.0 + 0.035 * prog(t, sc_["t0"], sc_["t1"] - sc_["t0"])
        dst = skia.Rect(content.left(), content.top(), content.right(), content.bottom())
        dst = skia.Rect(dst.centerX() - dst.width() * z / 2, dst.top(), dst.centerX() + dst.width() * z / 2,
                        dst.top() + dst.height() * z)
        c.save()
        if w < 1:
            # angled wipe from left to right
            edge = lerp(content.left() - 220, content.right() + 220, w)
            path = skia.Path()
            path.moveTo(content.left() - 10, content.top())
            path.lineTo(edge + 110, content.top())
            path.lineTo(edge - 110, content.bottom())
            path.lineTo(content.left() - 10, content.bottom())
            path.close()
            c.clipPath(path, skia.ClipOp.kIntersect, True)
        c.clipRect(content)
        c.drawImageRect(img, dst, SAMP)
        if len(idx) > 1:   # soften an internal hard cut
            cut = next(cc for cc in SOFTCUTS if cc <= st < cc + 0.45)
            fa = 1 - e_io((st - cut) / 0.45)
            c.drawImageRect(to_image(src.frame(idx[1], src_now)), dst, SAMP, skia.Paint(Alphaf=fa))
        c.restore()
        if 0 < w < 1:
            edge = lerp(content.left() - 220, content.right() + 220, w)
            c.save()
            c.clipRect(content)
            for (off, cc, wd) in [(0, BLUE, 7), (12, RED, 4)]:
                p = skia.Paint(AntiAlias=True, StrokeWidth=wd, Color=col(cc))
                c.drawLine(edge + 110 - off, content.top(), edge - 110 - off, content.bottom(), p)
            gp = skia.Paint(AntiAlias=True, StrokeWidth=40, Color=col(BLUE, 0.25),
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
            c.drawLine(edge + 110, content.top(), edge - 110, content.bottom(), gp)
            c.restore()
    # light sweep across the glass after each scene change
    for sc_ in SCENES:
        g = prog(t, sc_["t0"] + 0.4, 1.4)
        if 0 < g < 1:
            gx = lerp(r.left() - 400, r.right() + 400, e_io(g))
            sh = skia.GradientShader.MakeLinear([(gx - 160, 0), (gx + 160, 0)],
                                                [col((255, 255, 255), 0), col((255, 255, 255), 0.10), col((255, 255, 255), 0)], [0, 0.5, 1])
            c.drawRect(content, skia.Paint(Shader=sh))
    c.restore()
    c.drawRRect(rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.2,
                               Color=col((214, 220, 232))))
    c.restore()
    c.restore()


# ------------------------------------------------------------------ intro
def draw_intro(c, t):
    if t > 7.0:
        return
    # big centred logo assembles, then flies to the top-right corner
    LH = 150
    lw = 1797 / 394 * LH
    x0, y0 = (W - lw) / 2, 250
    mv = e_io(prog(t, 5.7, 1.1))
    hx, hy, hh = W - 110 - 1797 / 394 * 56 * (1797 - 0) / 1797, 62, 56
    x = lerp(x0, W - 110 - 1797 / 394 * hh, mv)
    y = lerp(y0, hy, mv)
    h = lerp(LH, hh, mv)
    draw_logo(c, x, y, h, prog(t, 0.35, 0.8), prog(t, 0.85, 0.9), prog(t, 1.45, 0.6) * (1 - mv))
    out = e_io(prog(t, 5.35, 0.6))
    if out >= 1:
        return
    oy = -30 * out
    oa = 1 - out
    # ENTERPRISE AI with gradient rules either side
    fk = font("bold", 30)
    txt = "ENTERPRISE AI"
    tw = width_spaced(txt, fk, 14)
    ky = 520 + oy
    g = e_out3(prog(t, 1.75, 0.8))
    for side in (-1, 1):
        x0_ = W / 2 + side * (tw / 2 + 30)
        x1_ = x0_ + side * 150 * g
        sh = skia.GradientShader.MakeLinear([(x0_, 0), (x0_ + side * 150, 0)], [col(RED, oa), col(RED, 0)])
        c.drawRect(skia.Rect(min(x0_, x1_), ky - 13, max(x0_, x1_), ky - 10), skia.Paint(Shader=sh))
    spaced(c, txt, W / 2 - tw / 2, ky, fk, BLUE, 14, oa, prog(t, 1.6, 0.8), 0.04)
    # tagline with highlighted phrase
    tb = TextBlock(dict(kick="", head="Enterprise AI for |real business impact.|", body=""), hsize=58)
    fh = tb.fh
    words = parse_head(tb.sc["head"])
    sp = fh.measureText(" ")
    tot = sum(fh.measureText(w) for w, _ in words) + sp * (len(words) - 1)
    bx = W / 2 - tot / 2
    base = 640 + oy
    p = skia.Paint(AntiAlias=True)
    hx0 = hx1 = None
    c.save()
    c.clipRect(skia.Rect(0, base - 64, W, base + 20))
    for i, (w, hi) in enumerate(words):
        ww = fh.measureText(w)
        wp = e_outx(prog(t, 2.35 + i * 0.08, 0.9))
        p.setColor(col(BLUE if hi else INDIGO, oa))
        c.drawString(w, bx, base + (1 - wp) * 70, fh, p)
        if hi:
            hx0 = bx if hx0 is None else hx0
            hx1 = bx + ww
        bx += ww + sp
    c.restore()
    u = e_io(prog(t, 3.0, 0.6))
    if u > 0:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(hx0, base + 14, hx0 + (hx1 - hx0) * u, base + 20), 3, 3),
                    skia.Paint(AntiAlias=True, Color=col(RED, oa)))
    # product chips pop in
    fc = font("semi", 22)
    chips = ["Data Sense", "Data Ask", "AI Warehouse", "Agentic"]   # opening products per storyboard
    cw = [fc.measureText(s) + 64 for s in chips]
    tot = sum(cw) + 18 * (len(chips) - 1)
    cx = W / 2 - tot / 2
    for i, s in enumerate(chips):
        k = prog(t, 3.35 + i * 0.12, 0.55)
        if k <= 0:
            cx += cw[i] + 18
            continue
        e = e_back(k, 2.0)
        r = skia.Rect(cx, 730 + oy, cx + cw[i], 784 + oy)
        c.save()
        c.translate(r.centerX(), r.centerY() + (1 - e_out3(k)) * 24)
        c.scale(e, e)
        c.translate(-r.centerX(), -r.centerY())
        a = oa * clamp(k * 2)
        rr = skia.RRect.MakeRectXY(r, 27, 27)
        c.drawRRect(rr.makeOffset(0, 6) if hasattr(rr, "makeOffset") else rr,
                    skia.Paint(AntiAlias=True, Color=col((30, 34, 80), 0.07 * a),
                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8)))
        c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=col((255, 255, 255), a)))
        cc = RED if i % 2 else BLUE
        c.drawRRect(rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.5, Color=col(cc, a * 0.55)))
        c.drawCircle(r.left() + 26, r.centerY(), 6, skia.Paint(AntiAlias=True, Color=col(cc, a)))
        c.drawString(s, r.left() + 44, r.centerY() + 8, fc, skia.Paint(AntiAlias=True, Color=col(INDIGO, a)))
        c.restore()
        cx += cw[i] + 18


def draw_corner_logo(c, t):
    if t < 6.8:
        return
    a = 1 - e_io(prog(t, END_OUT + 0.1, 0.6))
    if a <= 0:
        return
    hh = 56
    draw_logo(c, W - 110 - 1797 / 394 * hh, 62, hh, 1, 1, 0, a, spin=False)


# ------------------------------------------------------------------ open by design
ICONS = ["db", "spark", "graph", "cloud", "lock"]
CARDS = [("Any data", "Structured and unstructured"), ("Any model", "Hosted, open-source or your own"),
         ("AKGs", "Knowledge graphs for live and retired applications"),
         ("Any deployment", "Cloud or on-premises"), ("Any platform", "Your data stays where it is")]


def icon(c, kind, cx, cy, s, a):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.6, Color=col((255, 255, 255), a),
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if kind == "db":
        for dy in (-9, 0, 9):
            c.drawOval(skia.Rect(cx - 12, cy + dy - 9, cx + 12, cy + dy - 1), p) if dy == -9 else \
                c.drawArc(skia.Rect(cx - 12, cy + dy - 9, cx + 12, cy + dy - 1), 0, 180, False, p)
        c.drawLine(cx - 12, cy - 5, cx - 12, cy + 12, p)
        c.drawLine(cx + 12, cy - 5, cx + 12, cy + 12, p)
    elif kind == "spark":
        path = skia.Path()
        path.moveTo(cx, cy - 14)
        path.quadTo(cx + 2, cy - 2, cx + 14, cy)
        path.quadTo(cx + 2, cy + 2, cx, cy + 14)
        path.quadTo(cx - 2, cy + 2, cx - 14, cy)
        path.quadTo(cx - 2, cy - 2, cx, cy - 14)
        c.drawPath(path, p)
    elif kind == "graph":
        pts = [(cx - 10, cy - 9), (cx + 11, cy - 6), (cx - 4, cy + 11), (cx + 9, cy + 10)]
        for i, j in [(0, 1), (0, 2), (1, 3), (2, 3), (1, 2)]:
            c.drawLine(*pts[i], *pts[j], p)
        for q in pts:
            c.drawCircle(*q, 3.6, skia.Paint(AntiAlias=True, Color=col((255, 255, 255), a)))
    elif kind == "cloud":
        path = skia.Path()
        path.moveTo(cx - 13, cy + 8)
        path.cubicTo(cx - 20, cy + 8, cx - 20, cy - 3, cx - 11, cy - 3)
        path.cubicTo(cx - 9, cy - 13, cx + 6, cy - 14, cx + 8, cy - 4)
        path.cubicTo(cx + 18, cy - 5, cx + 18, cy + 8, cx + 10, cy + 8)
        path.close()
        c.drawPath(path, p)
    elif kind == "lock":
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - 11, cy - 3, cx + 11, cy + 13), 3, 3), p)
        c.drawArc(skia.Rect(cx - 7, cy - 14, cx + 7, cy + 2), 180, 180, False, p)
        c.drawLine(cx - 7, cy - 6, cx - 7, cy - 3, p)
        c.drawLine(cx + 7, cy - 6, cx + 7, cy - 3, p)


def draw_open(c, t):
    if t < OPEN["t0"] - 0.2 or t > END_OUT + 1.2:
        return
    tb = OPEN_TB
    tb.draw(c, t, OPEN["t0"] + 0.1, END_OUT)
    # 3 + 2 card grid on the right, linked to a hub line
    cw, ch, g = 352, 192, 26
    x0 = 728
    rows = [(x0, 318, [0, 1, 2]), (x0 + (cw + g) / 2, 318 + ch + g, [3, 4])]
    ft, fs = font("bold", 30), font("reg", 19)
    out = e_io(prog(t, END_OUT, 0.8))
    order = 0
    for (rx, ry, ids) in rows:
        for n, i in enumerate(ids):
            k = prog(t, OPEN["t0"] + 0.55 + order * 0.16, 0.7)
            order += 1
            if k <= 0:
                continue
            e = e_back(k, 1.6)
            a = clamp(k * 2) * (1 - clamp((t - END_OUT - (4 - order) * 0.06) / 0.5))
            if a <= 0:
                continue
            r = skia.Rect(rx + n * (cw + g), ry, rx + n * (cw + g) + cw, ry + ch)
            c.save()
            c.translate(r.centerX(), r.centerY() + (1 - e_out3(k)) * 40 - 30 * out)
            c.scale(lerp(0.85, 1, e), lerp(0.85, 1, e))
            c.translate(-r.centerX(), -r.centerY())
            c.saveLayerAlpha(None, int(a * 255))
            shadow(c, r, 18, 0.8)
            rr = skia.RRect.MakeRectXY(r, 18, 18)
            c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=col((255, 255, 255))))
            # sequential highlight: a blue/red accent bar travels card to card
            cyc = ((t - (OPEN["t0"] + 2.2)) / 0.75)
            hl = 1 if (cyc >= 0 and int(cyc) % 5 == i and t < END_OUT) else 0
            bw = cw * (e_out3(prog(t, OPEN["t0"] + 0.9 + order * 0.16, 0.6)))
            cc = BLUE if i % 2 == 0 else RED
            c.save()
            c.clipRRect(rr, True)
            c.drawRect(skia.Rect(r.left(), r.top(), r.left() + bw, r.top() + 5), skia.Paint(Color=col(cc)))
            c.restore()
            c.drawRRect(rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.2 + 1.3 * hl,
                                       Color=col(cc if hl else (222, 228, 238))))
            ib = skia.Rect(r.left() + 26, r.top() + 28, r.left() + 26 + 52, r.top() + 28 + 52)
            sh = skia.GradientShader.MakeLinear([(ib.left(), ib.top()), (ib.right(), ib.bottom())],
                                                [col(cc), col(INDIGO)])
            c.drawRRect(skia.RRect.MakeRectXY(ib, 13, 13), skia.Paint(AntiAlias=True, Shader=sh))
            icon(c, ICONS[i], ib.centerX(), ib.centerY(), 1, 1)
            c.drawString(CARDS[i][0], r.left() + 26, r.top() + 118, ft, skia.Paint(AntiAlias=True, Color=col(INDIGO)))
            for li, ln in enumerate(wrap_words([(w, 0) for w in CARDS[i][1].split()], fs, cw - 50)):
                c.drawString(" ".join(w for w, _ in ln), r.left() + 26, r.top() + 146 + li * 25, fs,
                             skia.Paint(AntiAlias=True, Color=col(BODY)))
            c.restore()
            c.restore()


OPEN_TB = None


# ------------------------------------------------------------------ frame
TBS = []
src_now = 0


def setup():
    global TBS, OPEN_TB
    TBS = [TextBlock(sc) for sc in SCENES]
    OPEN_TB = TextBlock(OPEN)


def render(c, t, src):
    draw_bg(c, t)
    draw_intro(c, t)
    draw_corner_logo(c, t)
    draw_card(c, t, src)
    for k, sc in enumerate(SCENES):
        t_in = sc["t0"] + (0.6 if k == 0 else 0.25)
        t_out = sc["t1"] - 0.75
        if k == len(SCENES) - 1:
            t_out = CARD_OUT[0] - 0.1
        TBS[k].draw(c, t, t_in, t_out)
    draw_open(c, t)
    draw_chrome(c, t)


def main():
    global src_now
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--frames", default=f"0:{NF}")
    ap.add_argument("--still", default="")
    a = ap.parse_args()
    setup()
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    if a.still:
        ts = [float(x) for x in a.still.split(",")]
        fr = [int(round(x * FPS)) for x in ts]
        need = [frame_needs(f) for f in sorted(fr)]
        src = Source(a.src, need)
        from PIL import Image
        for n, f in enumerate(sorted(fr)):
            src_now = n
            render(c, f / FPS, src)
            Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).save(
                f"{a.out}_{f / FPS:06.2f}.png")
        return
    f0, f1 = map(int, a.frames.split(":"))
    need = [frame_needs(f) for f in range(f0, f1)]
    src = Source(a.src, need)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                            "-pix_fmt", "yuv420p", "-x264-params", "keyint=60", a.out], stdin=subprocess.PIPE)
    for n, f in enumerate(range(f0, f1)):
        src_now = n
        render(c, f / FPS, src)
        enc.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        if n % 150 == 0:
            print(f"{a.out}: {n}/{f1 - f0}", flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
