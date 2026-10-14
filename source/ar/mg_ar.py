# Crisp 2D motion graphics (After Effects style) that replace the 3D particle shapes:
# stroke draw-ons, ring wipes, pop-ins with overshoot, dashed rotating rings, flowing data dots.
# Every element is drawn supersampled (2x) on its own small canvas, downsampled, given a soft
# glow and composited, so edges stay sharp. All positions are in 1920x1080 screen pixels.
import math, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "/usr/share/fonts/opentype/inter/"
SS = 2
BLUE = (0, 136, 207); BLUE_L = (90, 190, 245); WHITE = (255, 255, 255); RED = (238, 36, 36)
NAVY = (14, 34, 82); DIM = (120, 150, 200)

@lru_cache(None)
def F(name, size): return ImageFont.truetype(FD + name, size)
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = cl(x); return 1 - (1 - x)**3
def ei(x): x = cl(x); return x*x*(3 - 2*x)
def back(x, s=1.7):
    """Ease-out with overshoot (After Effects 'pop')."""
    x = cl(x); x -= 1; return x*x*((s + 1)*x + s) + 1

class Cv:
    """A supersampled RGBA canvas covering screen box (x0, y0, w, h)."""
    def __init__(self, x0, y0, w, h):
        self.x0, self.y0, self.w, self.h = int(x0), int(y0), int(w), int(h)
        self.im = Image.new("RGBA", (self.w*SS, self.h*SS), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def p(self, x, y): return ((x - self.x0)*SS, (y - self.y0)*SS)
    def circle(self, x, y, r, fill=None, outline=None, width=2):
        (a, b) = self.p(x - r, y - r); (c, e) = self.p(x + r, y + r)
        if c - a < 1: return
        self.d.ellipse((a, b, c, e), fill=fill, outline=outline, width=int(width*SS))
    def arc(self, x, y, r, a0, a1, col, width=3):
        if a1 - a0 < .5: return
        (a, b) = self.p(x - r, y - r); (c, e) = self.p(x + r, y + r)
        self.d.arc((a, b, c, e), a0, a1, fill=col, width=int(width*SS))
    def line(self, pts, col, width=3):
        self.d.line([self.p(*q) for q in pts], fill=col, width=int(width*SS), joint="curve")
    def rrect(self, x, y, w, h, r, fill=None, outline=None, width=2):
        (a, b) = self.p(x, y); (c, e) = self.p(x + w, y + h)
        if c - a < 2 or e - b < 2: return
        self.d.rounded_rectangle((a, b, c, e), int(r*SS), fill=fill, outline=outline, width=int(width*SS))
    def poly(self, pts, fill=None, outline=None, width=2):
        self.d.polygon([self.p(*q) for q in pts], fill=fill, outline=outline, width=int(width*SS))
    def text(self, x, y, s, size, col, font="InterDisplay-SemiBold.otf", anchor="mm"):
        self.d.text(self.p(x, y), s, font=F(font, size*SS), fill=col, anchor=anchor)
    def paste(self, img, x, y, alpha=1.0):
        im = img
        if alpha < 1:
            a = np.asarray(im, np.float32); a[..., 3] *= alpha; im = Image.fromarray(a.astype(np.uint8), "RGBA")
        self.im.alpha_composite(im, (int((x - self.x0)*SS), int((y - self.y0)*SS)))
    def blit(self, fr, alpha=1.0, glow=.6, gcol=(0.25, 0.65, 1.0)):
        sm = self.im.resize((self.w, self.h), Image.LANCZOS)
        a = np.asarray(sm, np.float32)/255
        H, W = fr.shape[:2]
        x0, y0 = self.x0, self.y0; x1, y1 = x0 + self.w, y0 + self.h
        fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if fx1 <= fx0 or fy1 <= fy0: return
        sl = (slice(fy0 - y0, fy1 - y0), slice(fx0 - x0, fx1 - x0))
        reg = fr[fy0:fy1, fx0:fx1]
        if glow > 0:
            g = np.asarray(Image.fromarray((a[..., 3]*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)), np.float32)/255
            g = g[sl][..., None]*glow*alpha
            reg[:] = reg + (1 - reg)*g*np.array(gcol, np.float32)
        aa = a[..., 3:][sl]*alpha
        reg[:] = reg*(1 - aa) + a[..., :3][sl]*aa

def rgba(c, a=1.0): return tuple(int(v) for v in c) + (int(255*cl(a)),)

def dashed_ring(cv, x, y, r, rot, col, n=36, duty=.55, width=2, sweep=1.0):
    step = 360/n
    for i in range(int(n*sweep)):
        a0 = rot + i*step; cv.arc(x, y, r, a0, a0 + step*duty, col, width)

def ring_wipe(cv, x, y, r, p, col, width=3, start=-90):
    if p > 0: cv.arc(x, y, r, start, start + 360*cl(p), col, width)

# ---------------------------------------------------------------- icons (line art, stroke in col)
def icon(cv, kind, x, y, s, col, a=1.0, prog=1.0):
    c = rgba(col, a); w = max(2, s*.07)
    if kind == "cost":
        cv.circle(x, y, s*.42, outline=c, width=w); cv.text(x, y + s*.02, "$", int(s*.5), c, "InterDisplay-Bold.otf")
    elif kind == "risk":
        pts = [(x, y - s*.46), (x + s*.38, y - s*.3), (x + s*.34, y + s*.12), (x, y + s*.46), (x - s*.34, y + s*.12), (x - s*.38, y - s*.3)]
        cv.poly(pts, outline=c, width=w); cv.text(x, y, "!", int(s*.48), c, "InterDisplay-Bold.otf")
    elif kind == "mna":
        dx = s*.17*(1 - prog)
        cv.circle(x - s*.14 - dx, y, s*.28, outline=c, width=w); cv.circle(x + s*.14 + dx, y, s*.28, outline=c, width=w)
    elif kind == "archive":
        for i in range(3):
            yy = y - s*.36 + i*s*.26
            cv.rrect(x - s*.4, yy, s*.8, s*.2, s*.04, outline=c, width=w)
            cv.line([(x - s*.1, yy + s*.1), (x + s*.1, yy + s*.1)], c, w)
    elif kind == "ai":
        cv.rrect(x - s*.3, y - s*.3, s*.6, s*.6, s*.08, outline=c, width=w)
        for k in range(3):
            o = -s*.16 + k*s*.16
            for (p0, p1) in (((x + o, y - s*.3), (x + o, y - s*.44)), ((x + o, y + s*.3), (x + o, y + s*.44)),
                             ((x - s*.3, y + o), (x - s*.44, y + o)), ((x + s*.3, y + o), (x + s*.44, y + o))):
                cv.line([p0, p1], c, w*.8)
        cv.text(x, y + s*.01, "AI", int(s*.24), c, "InterDisplay-Bold.otf")
    elif kind == "db":
        cv.circle(x, y - s*.28, 0, outline=c)
        for i in range(3):
            yy = y - s*.3 + i*s*.24
            cv.d.ellipse((*cv.p(x - s*.34, yy - s*.08), *cv.p(x + s*.34, yy + s*.08)), outline=c, width=int(w*SS))
        cv.line([(x - s*.34, y - s*.3), (x - s*.34, y + s*.18)], c, w); cv.line([(x + s*.34, y - s*.3), (x + s*.34, y + s*.18)], c, w)
    elif kind == "mainframe":
        cv.rrect(x - s*.3, y - s*.42, s*.6, s*.84, s*.05, outline=c, width=w)
        for i in range(3): cv.line([(x - s*.18, y - s*.24 + i*s*.18), (x + s*.18, y - s*.24 + i*s*.18)], c, w*.8)
    elif kind == "app":
        cv.rrect(x - s*.42, y - s*.32, s*.84, s*.64, s*.06, outline=c, width=w)
        cv.line([(x - s*.42, y - s*.14), (x + s*.42, y - s*.14)], c, w)
        cv.rrect(x - s*.3, y - s*.02, s*.24, s*.22, s*.03, outline=c, width=w*.8)
    elif kind == "cloud":
        cv.circle(x - s*.16, y + s*.04, s*.2, outline=c, width=w); cv.circle(x + s*.12, y - s*.06, s*.26, outline=c, width=w)
        cv.line([(x - s*.36, y + s*.24), (x + s*.38, y + s*.24)], c, w)
    elif kind == "file":
        cv.poly([(x - s*.3, y - s*.4), (x + s*.12, y - s*.4), (x + s*.3, y - s*.22), (x + s*.3, y + s*.4), (x - s*.3, y + s*.4)], outline=c, width=w)
        for i in range(3): cv.line([(x - s*.16, y - s*.06 + i*s*.14), (x + s*.16, y - s*.06 + i*s*.14)], c, w*.8)
    elif kind == "mail":
        cv.rrect(x - s*.4, y - s*.28, s*.8, s*.56, s*.05, outline=c, width=w)
        cv.line([(x - s*.38, y - s*.24), (x, y + s*.06), (x + s*.38, y - s*.24)], c, w)
    elif kind == "lock":
        cv.arc(x, y - s*.12, s*.2, 180, 360, c, w)
        cv.line([(x - s*.2, y - s*.12), (x - s*.2, y)], c, w); cv.line([(x + s*.2, y - s*.12), (x + s*.2, y)], c, w)
        cv.rrect(x - s*.3, y, s*.6, s*.42, s*.06, outline=c, width=w)
        cv.circle(x, y + s*.18, s*.05, fill=c)

# ---------------------------------------------------------------- scene elements
TRIG = [("t1", "cost", "Cost"), ("t2", "risk", "Risk"), ("t3", "mna", "M&A"), ("t4", "archive", "Old archive"), ("t5", "ai", "AI")]
def triggers(fr, t, R):
    """Per trigger: a big icon badge (ring wipe + pop) top-right, and a five-step tracker under the word."""
    t0 = R.LN["t1"]["start"] - .2; t_end = R.LN["one"]["start"]
    if not (t0 - .3 <= t <= t_end + .8): return
    cur = None
    for i, (tid, kind, lab) in enumerate(TRIG):
        a0 = R.LN[tid]["start"] - .1; a1 = R.SC_END[tid] - .25
        if a0 - .2 <= t <= a1 + .5: cur = (i, tid, kind, a0, a1)
    # big badge top-right
    if cur and t < t_end:
        i, tid, kind, a0, a1 = cur
        p = back((t - a0)/.5); q = ei((t - a1)/.3)
        if p > 0 and q < 1:
            cx, cy = 1640, 255; s = 190*p
            col = RED if tid == "t2" else BLUE_L
            cv = Cv(cx - 190, cy - 190, 380, 380)
            cv.circle(cx, cy, 120*p, fill=rgba(NAVY, .85*(1 - q)))
            ring_wipe(cv, cx, cy, 136, eo((t - a0)/.6), rgba(col, 1 - q), 4)
            dashed_ring(cv, cx, cy, 160, (t*40) % 360, rgba(col, .55*(1 - q)), n=40, width=2, sweep=eo((t - a0 - .1)/.6))
            icon(cv, kind, cx, cy, s*.9, WHITE, 1 - q, prog=eo((t - a0 - .2)/1.0))
            cv.blit(fr, glow=.55, gcol=(1, .3, .3) if tid == "t2" else (.25, .65, 1))
    # five-step tracker under the word
    out = ei((t - (t_end - .3))/.5)
    if out < 1:
        x0, y0 = 152, 700
        cv = Cv(x0 - 40, y0 - 60, 820, 150)
        for i, (tid, kind, lab) in enumerate(TRIG):
            a0 = R.LN[tid]["start"] - .1
            p = back((t - a0)/.45)
            x = x0 + 40 + i*150; y = y0
            active = cur is not None and cur[0] == i
            done = t >= a0
            if not done:
                cv.circle(x, y, 34, outline=rgba(DIM, .35*(1 - out)), width=2)
                continue
            col = RED if (tid == "t2" and active) else (BLUE if active else (60, 110, 170))
            cv.circle(x, y, 34*max(p, .01), fill=rgba(col, (1 - out)*(1 if active else .75)))
            icon(cv, kind, x, y, 50*p, WHITE, (1 - out)*(1 if active else .7))
            cv.text(x, y + 62, lab, 20, rgba(WHITE, (1 - out)*(1 if active else .6)), "Inter-SemiBold.otf")
            if i > 0:
                cv.line([(x - 150 + 40, y), (x - 40, y)], rgba(BLUE_L, .5*(1 - out)), 2)
        cv.blit(fr, glow=.35)

def converge(fr, t, R):
    """The five triggers fly into one point, which bursts open into the Solix engine hub."""
    s0 = R.SC["one"]; t_open = R.word_time("one", "One engine"); te = R.SC["connect"]
    if not (s0 - .1 <= t <= te + .1): return
    cx, cy = 960, 620
    if t >= te: return
    cv = Cv(cx - 560, cy - 380, 1120, 760)
    if t < t_open + .2:
        for i, (tid, kind, lab) in enumerate(TRIG):
            sx, sy = 152 + 40 + i*150, 700
            u = ei((t - s0 - i*.06)/max(.3, t_open - s0 - .2))
            x = sx + (cx - sx)*u; y = sy + (cy - sy)*u - math.sin(u*math.pi)*120
            r = 34*(1 - .6*u)
            cv.circle(x, y, r, fill=rgba(BLUE, 1 - ei((t - t_open)/.2)))
            icon(cv, kind, x, y, 50*(1 - .6*u), WHITE, 1 - ei((t - t_open)/.2))
    if t >= t_open - .05:
        k = (t - t_open)
        p = back(k/.6)
        shock = eo(k/.8)
        if shock < 1: cv.circle(cx, cy, 60 + 460*shock, outline=rgba(BLUE_L, (1 - shock)*.9), width=3)
        hub(cv, cx, cy, p, t, 1.0, sc=1.4)
    cv.blit(fr, glow=.7)

ENGINE_ICON = None
def engine_icon(size):
    from PIL import Image as I
    im = I.open(__file__.rsplit("/", 1)[0] + "/../assets/icon.png").convert("RGBA")
    return im.resize((size, size), I.LANCZOS)
@lru_cache(None)
def _icon(size): return engine_icon(size)

def hub(cv, cx, cy, p, t, a, label=True, sc=1.0):
    if p <= 0: return
    p = p*sc
    cv.circle(cx, cy, 128*p, fill=rgba(NAVY, .92*a), outline=rgba(BLUE, a), width=3)
    dashed_ring(cv, cx, cy, 160*p, (t*30) % 360, rgba(BLUE_L, .7*a), n=48, width=2)
    dashed_ring(cv, cx, cy, 196*p, (-t*18) % 360, rgba(BLUE_L, .35*a), n=24, duty=.3, width=3)
    ring_wipe(cv, cx, cy, 145*p, 1.0, rgba(BLUE, .5*a), 2)
    sz = int(110*p)
    if sz > 4:
        cv.paste(_icon(sz*SS), cx - sz/2, cy - sz/2 - (14*p if label else 0), alpha=a)
    if label and p > .8*sc:
        cv.text(cx, cy + 56*p, "SOLIX ENGINE", int(15*sc), rgba(WHITE, a*min(1, (p/sc - .8)*5)), "Inter-SemiBold.otf")

SRC = [("ERP", "app", "ERP"), ("Mainframe", "mainframe", "mainframe"), ("Custom apps", "app", "custom"),
       ("SaaS", "cloud", "SaaS"), ("Files", "file", "files"), ("Email", "mail", "email")]
def connect(fr, t, R):
    s0 = R.SC["connect"]; te = R.SC_END["connect"] - .45
    if not (s0 - .1 <= t <= te + .6): return
    out = ei((t - te)/.5)
    # the hub glides from the centre to the stage on the right
    m = ei((t - s0)/1.4)
    hx, hy = 960 + (1200 - 960)*m, 620 + (600 - 620)*m
    cv = Cv(640, 150, 1280, 830)
    a = 1 - out
    nodes = []
    for k, (lab, kind, wd) in enumerate(SRC):
        ang = math.radians(-120 + k*60)
        nx, ny = 1200 + 470*math.cos(ang), 600 + 260*math.sin(ang)
        ti = R.word_time("connect", wd)
        nodes.append((nx, ny, lab, kind, ti))
    for k, (nx, ny, lab, kind, ti) in enumerate(nodes):
        u = eo((t - ti)/.5)
        if u <= 0: continue
        ex, ey = nx + (hx - nx)*u, ny + (hy - ny)*u
        cv.line([(nx, ny), (ex, ey)], rgba(BLUE_L, .55*a), 2)
        if u >= 1:
            for j in range(3):
                ph = ((t*.7 + j/3 + k*.17) % 1.0)
                cv.circle(nx + (hx - nx)*ph, ny + (hy - ny)*ph, 5, fill=rgba(WHITE, a*math.sin(ph*math.pi)))
    hub(cv, hx, hy, 1.0, t, a, label=True, sc=1.4 - .4*m)
    for k, (nx, ny, lab, kind, ti) in enumerate(nodes):
        p = back((t - ti)/.45)
        if p <= 0: continue
        cv.circle(nx, ny, 50*p, fill=rgba(NAVY, .95*a), outline=rgba(BLUE, a), width=3)
        icon(cv, kind, nx, ny, 58*p, WHITE, a)
        cv.text(nx, ny + 80, lab, 26, rgba(WHITE, a*cl((t - ti - .1)/.3)), "InterDisplay-SemiBold.otf")
    cv.blit(fr, glow=.6)

def vault(cv, cx, cy, fill, t, a, scale=1.0, lit=1.0):
    w, h = 330*scale, 270*scale
    x0, y0 = cx - w/2, cy - h/2
    cv.rrect(x0, y0, w, h, 26*scale, fill=rgba(NAVY, .9*a), outline=rgba(BLUE, a), width=3)
    n = 7
    for i in range(n):
        f = cl(fill*n - i)
        if f <= 0: continue
        yy = y0 + h - 28*scale - (i + 1)*30*scale
        ww = (w - 60*scale)*eo(f)
        cv.rrect(cx - ww/2, yy, ww, 20*scale, 8*scale, fill=rgba(BLUE if i % 2 == 0 else (40, 160, 225), a*(.55 + .45*lit)))
    icon(cv, "lock", cx, y0 - 2*scale, 64*scale, WHITE, a)
    cv.circle(cx, y0 - 2*scale, 44*scale, outline=rgba(BLUE_L, a*.8), width=2)
    sweep = ((t*.6) % 1.4) - .2
    if 0 < sweep < 1 and fill >= 1:
        xx = x0 + w*sweep
        cv.line([(xx, y0 + 12*scale), (xx, y0 + h - 12*scale)], rgba(WHITE, a*.5*lit), 2)

def migrate(fr, t, R):
    sm = R.SC["migrate"]; sd = R.SC["dark"]; Ed = R.SC_END["dark"] - .45
    if not (sm - .1 <= t <= Ed + .6): return
    a_in = back((t - sm - .2)/.6)
    fill = ei((t - sm - .8)/4.5)
    mv = ei((t - sd + .2)/1.0)
    cx, cy = 1160 + (1600 - 1160)*mv, 620 + (520 - 620)*mv
    sc = 1.0 - .2*mv
    out = ei((t - Ed)/.45)
    a = 1 - out
    cv = Cv(cx - 260, 230, 520, 640)
    # data packets falling from the source window into the vault
    if t < sd:
        for j in range(10):
            ph = ((t*.9 + j/10) % 1.0)
            y = 330 + (cy - 140 - 330)*ph
            cv.rrect(cx - 8 + 30*math.sin(j*2.1), y, 16, 10, 3, fill=rgba(BLUE_L, a*math.sin(ph*math.pi)*(1 - fill*.6)))
    if a_in > 0: vault(cv, cx, cy, fill if t < sd else 1.0, t, a*min(1, a_in), scale=sc*max(.01, min(1.0, a_in)), lit=1.0)
    cv.blit(fr, glow=.6)

def platform(fr, t, R):
    """Access beat: a crisp stage line of light under the documents."""
    s0 = R.SC["access"]; te = R.SC_END["access"] - .45
    if not (s0 - .1 <= t <= te + .6): return
    p = eo((t - s0 - .1)/.9); a = 1 - ei((t - te)/.45)
    cv = Cv(160, 860, 1600, 80)
    w = 1400*p
    cv.line([(960 - w/2, 900), (960 + w/2, 900)], rgba(BLUE_L, .55*a), 2)
    for j in range(6):
        ph = ((t*.25 + j/6) % 1.0)
        cv.circle(960 - 700 + 1400*ph, 900, 4, fill=rgba(WHITE, a*math.sin(ph*math.pi)*p))
    cv.blit(fr, glow=.5)

KG = [("Supplier", 1080, 430, True), ("Invoice", 1560, 440, True), ("Payment", 1330, 760, True),
      ("Purchase order", 960, 720, False), ("Receipt", 1720, 700, False), ("Vendor", 1450, 330, False)]
KG_L = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 4), (2, 4), (1, 5), (0, 5)]
def graph(fr, t, R):
    s0 = R.SC["ask"]; te = R.SC_END["ask"] - .45
    if not (s0 - .1 <= t <= te + .6): return
    a = 1 - ei((t - te)/.45)
    t0 = R.word_time("ask", "cited") - 1.4
    lit = [ei((t - t0 - k*.6)/.5) if KG[k][3] else 0.0 for k in range(len(KG))]
    cv = Cv(820, 190, 1060, 700)
    for i, (u, v) in enumerate(KG_L):
        d = eo((t - s0 - .3 - i*.12)/.6)
        if d <= 0: continue
        x0, y0 = KG[u][1], KG[u][2]; x1, y1 = KG[v][1], KG[v][2]
        both = min(lit[u], lit[v])
        cv.line([(x0, y0), (x0 + (x1 - x0)*d, y0 + (y1 - y0)*d)], rgba(BLUE_L if both > .5 else DIM, a*(.35 + .5*both)), 2 + 1.5*both)
        if both > .5:
            ph = ((t*.8 + i*.21) % 1.0)
            cv.circle(x0 + (x1 - x0)*ph, y0 + (y1 - y0)*ph, 6, fill=rgba(WHITE, a*math.sin(ph*math.pi)))
    for k, (lab, x, y, main) in enumerate(KG):
        p = back((t - s0 - .2 - k*.1)/.5)
        if p <= 0: continue
        r = (44 if main else 28)*p
        cv.circle(x, y, r, fill=rgba(BLUE if lit[k] > .5 else NAVY, a*.95), outline=rgba(BLUE_L, a), width=3)
        if lit[k] > 0 and lit[k] < 1: cv.circle(x, y, r + 40*lit[k], outline=rgba(BLUE_L, a*(1 - lit[k])), width=2)
        cv.text(x, y - r - 26, lab, 30 if main else 22, rgba(WHITE, a*(1 if main else .6)), "InterDisplay-SemiBold.otf")
    cv.blit(fr, glow=.6)

def enable_ai(fr, t, R):
    """AI readiness ring: the missing segments (the history gap) fill with governed data."""
    s0 = R.SC["ai"]; te = R.SC_END["ai"] - .45
    if not (s0 - .1 <= t <= te + .6): return
    a = 1 - ei((t - te)/.45)
    cx, cy = 1300, 560; N = 24; base = 14
    cv = Cv(cx - 330, cy - 330, 660, 760)
    p = back((t - s0)/.6)
    step = 360/N
    for i in range(N):
        a0 = -90 + i*step
        if i < base:
            on = 1.0
        else:
            on = eo((t - s0 - .8 - (i - base)*.12)/.35)
        col = rgba(BLUE if i < base else BLUE_L, a*(.25 + .75*on))
        cv.arc(cx, cy, 230*p, a0 + 1.5, a0 + step - 1.5, col, 26 if on > .5 else 10)
    dashed_ring(cv, cx, cy, 275*p, (t*25) % 360, rgba(BLUE_L, .45*a), n=60, width=2)
    icon(cv, "ai", cx, cy, 170*p, WHITE, a)
    # data rising from the Preservation Zone into the gap
    for j in range(8):
        ph = ((t*.9 + j/8) % 1.0)
        if t > s0 + .6 and t < s0 + 3.0:
            ang = math.radians(-90 + (base + (j % (N - base)))*step)
            x = cx + (230*math.cos(ang) - 0)*ph; y = cy + 360 - (360 - 230*math.sin(ang))*ph
            cv.rrect(x - 7, y - 5, 14, 10, 3, fill=rgba(BLUE_L, a*math.sin(ph*math.pi)))
    full = cl((t - s0 - 2.2)/.4)
    cv.text(cx, cy + 330, "History complete", 26, rgba(WHITE, a*full), "Inter-SemiBold.otf")
    cv.blit(fr, glow=.6)

def signoff(fr, t, R):
    s0 = R.SC["sign"]
    if t < s0 - .1: return
    cx, cy = 960, 370
    p = eo((t - s0 - .1)/1.0)
    cv = Cv(cx - 560, cy - 230, 1120, 460)
    def ell(rx, ry, rot, col, n, duty, width, sweep=1.0):
        step = 360/n
        for i in range(int(n*sweep)):
            a0 = math.radians(rot + i*step); a1 = math.radians(rot + i*step + step*duty)
            pts = [(cx + rx*math.cos(a0 + (a1 - a0)*k/4), cy + ry*math.sin(a0 + (a1 - a0)*k/4)) for k in range(5)]
            cv.line(pts, col, width)
    ell(500*p, 150*p, t*10, rgba(BLUE_L, .6), 64, .55, 2, sweep=p)
    ell(540*p, 175*p, -t*6, rgba(BLUE, .45), 32, .3, 3, sweep=p)
    cv.blit(fr, glow=.6)

def title_rings(fr, t, R):
    T0 = R.LN["hook"]["start"]
    if t > T0 + .6: return
    a = 1 - ei((t - T0 + .2)/.6)
    cv = Cv(960 - 520, 440 - 330, 1040, 660)
    for k in range(3):
        ph = ((t*.35 + k/3) % 1.0)
        cv.circle(960, 440, 140 + 380*ph, outline=rgba(BLUE_L, a*.45*(1 - ph)), width=2)
    dashed_ring(cv, 960, 440, 300, (t*20) % 360, rgba(BLUE_L, .3*a), n=72, width=2, sweep=eo(t/1.2))
    cv.blit(fr, glow=.4)
