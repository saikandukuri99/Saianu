# Solix Empower 2026 AV - v2 renderer (motion graphics, light coral reference style)
import json, os, re, sys, math, subprocess, glob, random
from functools import lru_cache
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import screens6 as screens
import human3d

B = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(B)
A1, A2 = f"{S}/assets", f"{S}/assets2"
C1, C2, C3 = f"{S}/clips", f"{S}/clips2", f"{S}/clips3"
W, H, FPS = 1920, 1080, 30
RED = (238, 36, 36)        # #ee2424
BLUE = (0, 136, 207)       # #0088cf
INDIGO = (48, 38, 123)     # #30267b
KICK = (64, 172, 232)      # brand blue, lifted for big-screen legibility
TXT = (255, 255, 255)
TXT2 = (190, 194, 228)
BGC = (30, 24, 82)         # average background tone for line fades
DRED = (190, 22, 30)
INK = (17, 17, 17)
GREY = (112, 112, 120)
BLUSH = (251, 226, 224)
FD = "/usr/share/fonts/opentype/inter/"
FONTS = {"black": FD + "InterDisplay-Black.otf", "xbold": FD + "InterDisplay-ExtraBold.otf", "bold": FD + "Inter-Bold.otf",
         "semi": FD + "Inter-SemiBold.otf", "med": FD + "Inter-Medium.otf", "reg": FD + "Inter-Regular.otf"}

# ------------------------------------------------------------------ timeline
LINES = json.load(open(f"{B}/lines_90.json"))
FIRST = 0.5       # first VO line start
SCENE_PAD = 0.35  # extra air at scene changes
PRE = 0.6         # scene starts this long before its first line
TAIL = 2.2
t = FIRST
for i, L in enumerate(LINES):
    if i and L["scene"] != LINES[i - 1]["scene"]:
        t += SCENE_PAD
    L["start"] = t
    L["dur"] = sf.info(f"{B}/vo90/{i:02d}.wav").duration
    t += L["dur"] + L["gap"]
TOTAL = LINES[-1]["start"] + LINES[-1]["dur"] + TAIL
SC = []
for k in range(8):
    idx = [i for i, L in enumerate(LINES) if L["scene"] == k]
    SC.append({"lines": idx, "start": (LINES[idx[0]]["start"] - PRE) if idx else None})
nxt = TOTAL
for k in range(7, -1, -1):
    if SC[k]["start"] is None:
        SC[k]["start"] = nxt
    SC[k]["end"] = nxt
    nxt = SC[k]["start"]
SC[1]["start"] = 0.0


def cue(i, phrase=None, occ=0):
    L = LINES[i]
    if phrase is None:
        return L["start"]
    pos = -1
    for _ in range(occ + 1):
        pos = L["tts"].find(phrase, pos + 1)
    assert pos >= 0, (i, phrase)
    return L["start"] + L["dur"] * pos / len(L["tts"])


def lc(k, i, phrase=None, occ=0, lead=0.2):
    """cue local to scene k"""
    return cue(i, phrase, occ) - SC[k]["start"] - lead


def chunks(text, maxc=74):
    parts = re.findall(r"[^,.;]+[,.;]?", text)
    out, cur = [], ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if cur and len(cur) + 1 + len(p) > maxc:
            out.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur:
        out.append(cur)
    res = []
    for c in out:
        while len(c) > maxc + 8:
            k = c.rfind(" ", 0, maxc)
            res.append(c[:k]); c = c[k + 1:]
        res.append(c)
    return res


CAPS = []
for i, L in enumerate(LINES):
    cs = chunks(L["cap"])
    tot = sum(len(c) for c in cs)
    tt = L["start"]
    for j, c in enumerate(cs):
        d = L["dur"] * len(c) / tot
        end = tt + d + (min(L["gap"], 0.6) if j == len(cs) - 1 else 0)
        CAPS.append((tt, end, c, i, j == 0))
        tt += d


# ------------------------------------------------------------------ helpers
def ease(p):
    p = max(0.0, min(1.0, p)); return 1 - (1 - p) ** 3


def eio(p):
    p = max(0.0, min(1.0, p)); return p * p * (3 - 2 * p)


def back(p):
    p = max(0.0, min(1.0, p)); c1 = 1.4; c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def vis(t, tin, tout=None, d=0.6, dout=0.45):
    a = ease((t - tin) / d)
    if tout is not None:
        a *= 1 - eio((t - tout) / dout)
    return a


def mix(c1, c2, k):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


@lru_cache(None)
def font(w, s):
    return ImageFont.truetype(FONTS[w], s)


@lru_cache(None)
def text(s, w, size, color=INK, track=0):
    f = font(w, size)
    asc, desc = f.getmetrics()
    widths = [f.getlength(ch) for ch in s] if track else None
    tw = int(sum(widths) + track * (len(s) - 1)) + 4 if track else int(f.getlength(s)) + 4
    im = Image.new("RGBA", (max(tw, 1), asc + desc + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track:
        x = 0
        for ch, wd in zip(s, widths):
            d.text((x, 0), ch, font=f, fill=color); x += wd + track
    else:
        d.text((0, 0), s, font=f, fill=color)
    return im


def fit_text(s, w, size, maxw, color=INK, track=0):
    while size > 14:
        im = text(s, w, size, color, track)
        if im.width <= maxw:
            return im
        size -= 2
    return text(s, w, size, color, track)


def put(c, im, x, y, a=1.0):
    if a <= 0.004 or im is None:
        return
    if a < 0.996:
        c.paste(im, (int(round(x)), int(round(y))), im.getchannel("A").point(lambda v: int(v * a)))
    else:
        c.paste(im, (int(round(x)), int(round(y))), im)


def put_scaled(c, im, cx, cy, s, a):
    if a <= 0.004 or s <= 0.02:
        return
    if abs(s - 1) > 0.01:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    put(c, im, cx - im.width / 2, cy - im.height / 2, a)


@lru_cache(None)
def rounded_mask(w, h, r):
    ss = 3
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


@lru_cache(None)
def shadow(w, h, r=16, blur=26, alpha=58, dy=16):
    pad = blur * 2
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad + dy, pad + w, pad + h + dy), r, fill=(4, 2, 20, int(alpha * 2.0)))
    return im.filter(ImageFilter.GaussianBlur(blur)), pad


def box(w, h, r=14, fill=(255, 255, 255, 255), border=None, bw=2):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=border, width=bw if border else 0)
    return im


def finish_card(im, w, h, r=14):
    im = im.convert("RGBA")
    im.putalpha(rounded_mask(w, h, r))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, outline=(226, 222, 224, 255), width=2)
    return im


def draw_card(c, im, x, y, a=1.0):
    if a <= 0.004:
        return
    sh, pad = shadow(im.width, im.height)
    put(c, sh, x - pad, y - pad, a)
    put(c, im, x, y, a)


@lru_cache(None)
def asset(name):
    p = f"{A2}/{name}.png" if os.path.exists(f"{A2}/{name}.png") else f"{A1}/{name}.png"
    return Image.open(p).convert("RGB")


def fit_size(name, maxw, maxh):
    im = asset(name)
    sc = min(maxw / im.width, maxh / im.height)
    return int(im.width * sc), int(im.height * sc)


LOWRES = {"datasense", "dataask", "aiwh", "agentic", "appret", "datapres", "sap", "oracle"}
_REG = set()


def _register(name):
    if name in _REG:
        return
    if os.path.exists(f"{S}/assets3/{name}_page.png"):
        im = Image.open(f"{S}/assets3/{name}_page.png").convert("RGB")
    elif name == "ecs":
        im = ecs_panel(10.0, 1160, 600)
        bgw = Image.new("RGB", im.size, (255, 255, 255)); bgw.paste(im, (0, 0), im); im = bgw
    elif name == "recog":
        im = recog_panel(10.0, 1100, 590, False)
        bgw = Image.new("RGB", im.size, (250, 251, 253)); bgw.paste(im, (0, 0), im); im = bgw
    elif name == "eaihc":
        raw = Image.open(f"{S}/../images/3.webp") if os.path.exists(f"{S}/../images/3.webp") else None
        raw = Image.open("/tmp/claude-0/-home-user-Saianu/ba5b8708-a66d-5516-a47a-bca1964d7744/images/3.webp").convert("RGBA")
        im = Image.new("RGB", raw.size, (255, 255, 255)); im.paste(raw, (0, 0), raw)
    else:
        im = asset(name)
    screens.register(name, im)
    _REG.add(name)


def screen_size(name, maxw, maxh):
    _register(name)
    sw, sh = screens._img(name).size
    bar = 44 if maxh > 300 else 32
    w = min(maxw, int((maxh - bar) * sw / sh))
    h = int(w * sh / sw) + bar
    return w, h


def still(name, maxw, maxh, lt=0.0, dur=6.0):
    """Animated product screen in a browser window."""
    w, h = screen_size(name, maxw, maxh)
    return screens.screen_still(name, lt, w, h, dur, lowres=name in LOWRES)


@lru_cache(None)
def frames(name):
    d = next(f"{x}/{name}" for x in (C3, C2, C1) if os.path.isdir(f"{x}/{name}"))
    return sorted(glob.glob(f"{d}/*.jpg"))


WEBCLIPS = {"cdp", "edg", "akg", "analysts", "logos"}


def clip(name, lt, w, h, rate=1.0, top=False):
    fr = frames(name)
    n = len(fr)
    i = min(n - 1, max(0, int(lt * FPS * rate)))
    im = Image.open(fr[i])
    if name in WEBCLIPS:
        return screens.screen_clip(im.convert("RGB"), name, lt, w, h)
    sc = max(w / im.width, h / im.height)
    nw, nh = int(im.width * sc + 0.5), int(im.height * sc + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    l = (nw - w) // 2
    tt = 0 if top else (nh - h) // 2
    return finish_card(im.crop((l, tt, l + w, tt + h)), w, h)


@lru_cache(None)
def logo(w):
    im = Image.open(f"{A1}/logo_white.png").convert("RGBA")
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


@lru_cache(None)
def bolt(w):
    return Image.open(f"{A1}/icon.png").convert("RGBA").resize((w, w), Image.LANCZOS)


# ------------------------------------------------------------------ vector icons
@lru_cache(None)
def icon(kind, size, color=RED, bgc=None):
    ss = 4
    S_ = size * ss
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = color + (255,)
    lw = max(2, int(S_ * 0.06))
    m = S_ * 0.18
    if bgc:
        d.ellipse((0, 0, S_ - 1, S_ - 1), fill=bgc + (255,))
    if kind == "db":
        x0, x1 = S_ * 0.26, S_ * 0.74
        for k, y in enumerate((0.28, 0.45, 0.62)):
            d.ellipse((x0, S_ * y - S_ * 0.07, x1, S_ * y + S_ * 0.07), outline=col, width=lw)
        d.line((x0, S_ * 0.28, x0, S_ * 0.72), fill=col, width=lw); d.line((x1, S_ * 0.28, x1, S_ * 0.72), fill=col, width=lw)
        d.arc((x0, S_ * 0.65, x1, S_ * 0.79), 0, 180, fill=col, width=lw)
    elif kind == "shield":
        pts = [(S_ * 0.5, S_ * 0.2), (S_ * 0.74, S_ * 0.3), (S_ * 0.72, S_ * 0.55), (S_ * 0.5, S_ * 0.8), (S_ * 0.28, S_ * 0.55), (S_ * 0.26, S_ * 0.3)]
        d.line(pts + [pts[0]], fill=col, width=lw, joint="curve")
        d.line([(S_ * 0.39, S_ * 0.5), (S_ * 0.47, S_ * 0.58), (S_ * 0.62, S_ * 0.42)], fill=col, width=lw, joint="curve")
    elif kind == "doc":
        d.rounded_rectangle((S_ * 0.3, S_ * 0.22, S_ * 0.7, S_ * 0.78), S_ * 0.04, outline=col, width=lw)
        for y in (0.38, 0.5, 0.62):
            d.line((S_ * 0.38, S_ * y, S_ * 0.62, S_ * y), fill=col, width=lw)
    elif kind == "spark":
        cx = cy = S_ / 2
        for (r, rot, sc) in ((0.28, 0, 1), (0.12, 0, 0.6)):
            pass
        pts = []
        for k in range(8):
            ang = k * math.pi / 4 - math.pi / 2
            r = S_ * (0.3 if k % 2 == 0 else 0.09)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=col)
        d.ellipse((S_ * 0.68, S_ * 0.2, S_ * 0.78, S_ * 0.3), fill=col)
    elif kind == "person":
        d.ellipse((S_ * 0.38, S_ * 0.2, S_ * 0.62, S_ * 0.44), outline=col, width=lw)
        d.arc((S_ * 0.24, S_ * 0.5, S_ * 0.76, S_ * 1.02), 180, 360, fill=col, width=lw)
    elif kind == "chart":
        for k, hgt in enumerate((0.25, 0.4, 0.55)):
            x = S_ * (0.3 + k * 0.15)
            d.rectangle((x, S_ * (0.75 - hgt), x + S_ * 0.09, S_ * 0.75), fill=col)
        d.line((S_ * 0.25, S_ * 0.78, S_ * 0.78, S_ * 0.78), fill=col, width=lw)
    elif kind == "chat":
        d.rounded_rectangle((S_ * 0.22, S_ * 0.26, S_ * 0.78, S_ * 0.64), S_ * 0.08, outline=col, width=lw)
        d.polygon([(S_ * 0.34, S_ * 0.62), (S_ * 0.34, S_ * 0.78), (S_ * 0.48, S_ * 0.63)], fill=col)
        for x in (0.38, 0.5, 0.62):
            d.ellipse((S_ * x - S_ * 0.03, S_ * 0.42, S_ * x + S_ * 0.03, S_ * 0.48), fill=col)
    elif kind == "graph":
        P = [(0.3, 0.3), (0.7, 0.32), (0.5, 0.55), (0.3, 0.72), (0.72, 0.7)]
        for a_, b_ in ((0, 2), (1, 2), (2, 3), (2, 4), (0, 1)):
            d.line((S_ * P[a_][0], S_ * P[a_][1], S_ * P[b_][0], S_ * P[b_][1]), fill=col, width=lw)
        for x, y in P:
            d.ellipse((S_ * x - S_ * 0.06, S_ * y - S_ * 0.06, S_ * x + S_ * 0.06, S_ * y + S_ * 0.06), fill=col)
    elif kind == "warehouse":
        d.polygon([(S_ * 0.22, S_ * 0.42), (S_ * 0.5, S_ * 0.22), (S_ * 0.78, S_ * 0.42)], outline=col, width=lw)
        d.rectangle((S_ * 0.27, S_ * 0.42, S_ * 0.73, S_ * 0.76), outline=col, width=lw)
        for y in (0.54, 0.64):
            d.line((S_ * 0.36, S_ * y, S_ * 0.64, S_ * y), fill=col, width=lw)
    elif kind == "agent":
        d.rounded_rectangle((S_ * 0.28, S_ * 0.32, S_ * 0.72, S_ * 0.7), S_ * 0.08, outline=col, width=lw)
        d.ellipse((S_ * 0.38, S_ * 0.44, S_ * 0.46, S_ * 0.52), fill=col); d.ellipse((S_ * 0.54, S_ * 0.44, S_ * 0.62, S_ * 0.52), fill=col)
        d.line((S_ * 0.5, S_ * 0.32, S_ * 0.5, S_ * 0.22), fill=col, width=lw); d.ellipse((S_ * 0.46, S_ * 0.16, S_ * 0.54, S_ * 0.24), fill=col)
        d.line((S_ * 0.42, S_ * 0.6, S_ * 0.58, S_ * 0.6), fill=col, width=lw)
    elif kind == "cap":
        d.polygon([(S_ * 0.5, S_ * 0.24), (S_ * 0.82, S_ * 0.4), (S_ * 0.5, S_ * 0.56), (S_ * 0.18, S_ * 0.4)], fill=col)
        d.arc((S_ * 0.32, S_ * 0.36, S_ * 0.68, S_ * 0.76), 0, 180, fill=col, width=lw)
        d.line((S_ * 0.78, S_ * 0.42, S_ * 0.78, S_ * 0.66), fill=col, width=lw)
    elif kind == "dollar":
        f = ImageFont.truetype(FONTS["bold"], int(S_ * 0.55))
        d.text((S_ / 2, S_ / 2), "$", font=f, fill=col, anchor="mm")
    elif kind == "globe":
        d.ellipse((S_ * 0.24, S_ * 0.24, S_ * 0.76, S_ * 0.76), outline=col, width=lw)
        d.ellipse((S_ * 0.38, S_ * 0.24, S_ * 0.62, S_ * 0.76), outline=col, width=lw)
        d.line((S_ * 0.24, S_ * 0.5, S_ * 0.76, S_ * 0.5), fill=col, width=lw)
    elif kind == "cycle":
        d.arc((S_ * 0.24, S_ * 0.24, S_ * 0.76, S_ * 0.76), 200, 340, fill=col, width=lw)
        d.arc((S_ * 0.24, S_ * 0.24, S_ * 0.76, S_ * 0.76), 20, 160, fill=col, width=lw)
        d.polygon([(S_ * 0.74, S_ * 0.3), (S_ * 0.8, S_ * 0.44), (S_ * 0.66, S_ * 0.42)], fill=col)
        d.polygon([(S_ * 0.26, S_ * 0.7), (S_ * 0.2, S_ * 0.56), (S_ * 0.34, S_ * 0.58)], fill=col)
    elif kind == "image":
        d.rounded_rectangle((S_ * 0.22, S_ * 0.26, S_ * 0.78, S_ * 0.74), S_ * 0.05, outline=col, width=lw)
        d.line([(S_ * 0.28, S_ * 0.68), (S_ * 0.44, S_ * 0.48), (S_ * 0.56, S_ * 0.6), (S_ * 0.64, S_ * 0.52), (S_ * 0.74, S_ * 0.66)], fill=col, width=lw, joint="curve")
        d.ellipse((S_ * 0.58, S_ * 0.33, S_ * 0.68, S_ * 0.43), fill=col)
    elif kind == "check":
        d.line([(S_ * 0.28, S_ * 0.52), (S_ * 0.44, S_ * 0.68), (S_ * 0.74, S_ * 0.34)], fill=col, width=int(lw * 1.4), joint="curve")
    elif kind == "flask":
        d.line([(S_ * 0.42, S_ * 0.2), (S_ * 0.42, S_ * 0.42), (S_ * 0.26, S_ * 0.76), (S_ * 0.74, S_ * 0.76), (S_ * 0.58, S_ * 0.42), (S_ * 0.58, S_ * 0.2)], fill=col, width=lw, joint="curve")
        d.line((S_ * 0.36, S_ * 0.2, S_ * 0.64, S_ * 0.2), fill=col, width=lw)
    elif kind == "heart":
        d.line([(S_ * 0.2, S_ * 0.52), (S_ * 0.38, S_ * 0.52), (S_ * 0.46, S_ * 0.34), (S_ * 0.56, S_ * 0.7), (S_ * 0.64, S_ * 0.52), (S_ * 0.8, S_ * 0.52)], fill=col, width=lw, joint="curve")
    elif kind == "factory":
        d.polygon([(S_ * 0.2, S_ * 0.76), (S_ * 0.2, S_ * 0.46), (S_ * 0.38, S_ * 0.56), (S_ * 0.38, S_ * 0.46), (S_ * 0.56, S_ * 0.56), (S_ * 0.56, S_ * 0.3), (S_ * 0.7, S_ * 0.3), (S_ * 0.7, S_ * 0.76)], outline=col, width=lw)
    elif kind == "chip":
        d.rounded_rectangle((S_ * 0.32, S_ * 0.32, S_ * 0.68, S_ * 0.68), S_ * 0.04, outline=col, width=lw)
        for k in range(3):
            v = S_ * (0.4 + 0.1 * k)
            for (a_, b_, c_, d_) in ((v, 0.22, v, 0.32), (v, 0.68, v, 0.78), (0.22, v, 0.32, v), (0.68, v, 0.78, v)):
                xx0 = a_ if a_ > 1 else S_ * a_; yy0 = b_ if b_ > 1 else S_ * b_
                xx1 = c_ if c_ > 1 else S_ * c_; yy1 = d_ if d_ > 1 else S_ * d_
                d.line((xx0, yy0, xx1, yy1), fill=col, width=max(2, lw // 2))
    elif kind == "bank":
        d.polygon([(S_ * 0.2, S_ * 0.38), (S_ * 0.5, S_ * 0.2), (S_ * 0.8, S_ * 0.38)], outline=col, width=lw)
        for x in (0.3, 0.45, 0.6, 0.72):
            d.line((S_ * x, S_ * 0.44, S_ * x, S_ * 0.7), fill=col, width=lw)
        d.line((S_ * 0.2, S_ * 0.76, S_ * 0.8, S_ * 0.76), fill=col, width=lw)
    elif kind == "trophy":
        d.arc((S_ * 0.3, S_ * 0.1, S_ * 0.7, S_ * 0.62), 0, 180, fill=col, width=lw)
        d.line((S_ * 0.3, S_ * 0.36, S_ * 0.7, S_ * 0.36), fill=col, width=lw)
        d.line((S_ * 0.5, S_ * 0.62, S_ * 0.5, S_ * 0.74), fill=col, width=lw)
        d.line((S_ * 0.36, S_ * 0.78, S_ * 0.64, S_ * 0.78), fill=col, width=lw)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(None)
def node(kind, size, active=True):
    """glossy 3D sphere-like disc with icon"""
    pad = 34
    S_ = size + pad * 2
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad + 4, pad + 14, pad + size - 4, pad + size + 14), fill=(0, 0, 10, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(sphere_img(size, active), (pad, pad))
    ic = icon(kind, int(size * 0.56))
    im.alpha_composite(ic, (pad + (size - ic.width) // 2, pad + (size - ic.height) // 2))
    return im


@lru_cache(None)
def sphere_img(d, rim=True):
    """white glossy disc: radial shading + specular highlight + red rim"""
    ss = 2
    D = d * ss
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    lx, ly = cx - D * 0.18, cy - D * 0.22
    l = np.hypot(xx - lx, yy - ly) / D
    shade = np.clip(1.0 - 0.32 * l ** 1.4 - 0.18 * np.clip(r - 0.72, 0, 1) * 3, 0.55, 1.0)
    rgb = np.stack([248 * shade, 248 * shade, 255 * shade], -1)
    spec = np.exp(-(((xx - (cx - D * 0.2)) / (D * 0.16)) ** 2 + ((yy - (cy - D * 0.26)) / (D * 0.09)) ** 2))
    rgb = np.clip(rgb + spec[..., None] * 40, 0, 255)
    a = np.clip((1 - r) * D * 0.5, 0, 1) * 255
    if rim:
        ring = np.clip(1 - np.abs(r - 0.955) / 0.035, 0, 1)
        rgb = rgb * (1 - ring[..., None]) + np.array(RED)[None, None] * ring[..., None]
    im = Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA")
    return im.resize((d, d), Image.LANCZOS)


# ------------------------------------------------------------------ background
@lru_cache(None)
def background():
    BW, BH = W + 260, H + 180
    g = Image.linear_gradient("L").resize((BW, BH))
    deep = Image.new("RGB", (BW, BH), (12, 9, 40))
    ind = Image.new("RGB", (BW, BH), INDIGO)
    im = Image.composite(deep, ind, g.point(lambda v: int(255 * (v / 255) ** 0.8)))
    ov = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((BW - 1000, -520, BW + 420, 760), fill=BLUE + (150,))
    d.ellipse((-520, BH - 420, 560, BH + 520), fill=RED + (70,))
    d.ellipse((BW * 0.3, BH * 0.25, BW * 0.75, BH * 0.85), fill=(70, 56, 170, 60))
    ov = ov.filter(ImageFilter.GaussianBlur(170))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


rnd = random.Random(11)
PART = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(-14, 14), rnd.uniform(-9, 9), rnd.uniform(1.6, 3.6)) for _ in range(46)]


@lru_cache(None)
def bokeh(r, blur, col, alpha):
    pad = int(blur * 3) + 2
    im = Image.new("RGBA", (2 * (r + pad), 2 * (r + pad)), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((pad, pad, pad + 2 * r, pad + 2 * r), fill=col + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else im


@lru_cache(None)
def orb(d, tint):
    """glossy glass sphere sprite"""
    ss = 2
    D = d * ss
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    base = np.array(tint, float)
    shade = np.clip(0.35 + 0.65 * (1 - np.hypot(xx - cx + D * 0.15, yy - cy + D * 0.2) / D), 0.2, 1)
    rgb = base[None, None] * shade[..., None]
    rim = np.clip((r - 0.75) / 0.25, 0, 1) ** 2
    rgb = rgb + rim[..., None] * np.array([120, 190, 255]) * 0.7
    spec = np.exp(-(((xx - (cx - D * 0.22)) / (D * 0.12)) ** 2 + ((yy - (cy - D * 0.28)) / (D * 0.07)) ** 2))
    rgb = np.clip(rgb + spec[..., None] * 200, 0, 255)
    a = np.clip((1 - r) * D * 0.4, 0, 1) * (0.55 + 0.45 * rim + 0.6 * spec) * 255
    im = Image.fromarray(np.dstack([rgb, np.clip(a, 0, 255)]).astype(np.uint8), "RGBA").resize((d, d), Image.LANCZOS)
    return im.filter(ImageFilter.GaussianBlur(1.2))


rb = random.Random(21)
# (x, y, vx, vy, radius, blur, colour, alpha, parallax layer)
BOKEH = []
for layer, n, rads, blur, al in ((0, 26, (2, 5), 1.0, 150), (1, 14, (10, 22), 6, 70), (2, 6, (40, 80), 22, 40)):
    for _ in range(n):
        col = rb.choice([(110, 190, 255), (150, 210, 255), (255, 120, 120), (200, 190, 255)])
        BOKEH.append((rb.uniform(0, W), rb.uniform(0, H), rb.uniform(-10, 10) * (1 + layer), rb.uniform(-6, 6) * (1 + layer),
                      rb.randint(*rads), blur, col, al, layer))
ORBS = [(1885, 930, 120, (40, 70, 160), 0.0), (50, 760, 110, (120, 30, 60), 2.0), (1000, 1075, 70, (30, 90, 170), 4.0)]


def particles(c, t, strength=1.0):
    for (x0, y0, vx, vy, r, blur, col, al, layer) in BOKEH:
        x = (x0 + vx * t + 25 * math.sin(t * 0.21 + y0)) % (W + 300) - 150
        y = (y0 + vy * t + 18 * math.cos(t * 0.17 + x0)) % (H + 300) - 150
        tw = 0.75 + 0.25 * math.sin(t * (0.8 + layer * 0.3) + x0)
        im = bokeh(r, blur, col, int(al * tw))
        put(c, im, x - im.width / 2, y - im.height / 2, strength)
    for (x0, y0, d, tint, ph) in ORBS:
        x = x0 + 30 * math.sin(t * 0.13 + ph)
        y = y0 + 22 * math.cos(t * 0.11 + ph)
        o = orb(d, tint)
        put(c, o, x - d / 2, y - d / 2, 0.85 * strength)


def bg_frame(t):
    bg = background()
    ox = 130 + 120 * math.sin(t / 10.0)
    oy = 90 + 80 * math.cos(t / 12.0)
    c = bg.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    particles(c, t)
    return c


# ------------------------------------------------------------------ UI pieces
def heading(c, lt, kicker, title, G, x=92, y=96, tout=None, size=58):
    return
    k = text(kicker, "bold", 19, KICK, 4)
    kw = KEYWORD.get(title)
    if kw:
        return heading_kw(c, lt, k, title, kw, G, x, y, tout, size)
    ti = fit_text(title, "xbold", size, W - 2 * x, TXT)
    a1 = vis(lt, 0.25, tout) * G
    a2 = vis(lt, 0.4, tout) * G
    put(c, k, x - (1 - ease((lt - 0.25) / 0.6)) * 40, y, a1)
    # title reveal: slide up with clip
    p = ease((lt - 0.4) / 0.7)
    if a2 > 0:
        hh = int(ti.height * min(1, p * 1.2)) or 1
        put(c, ti.crop((0, 0, ti.width, ti.height)), x, y + 30 + (1 - p) * 34, a2)
    # red underline grows
    ln = int(70 * ease((lt - 0.6) / 0.6))
    if ln > 0 and G > 0.3:
        ImageDraw.Draw(c).rectangle((x, y + 30 + ti.height + 8, x + ln, y + 30 + ti.height + 11), fill=mix(BGC, RED, G))


KEYWORD = {"Step One: AI-Ready": "AI-Ready", "Solix Enterprise AI": "Enterprise AI", "Move It Once. Access It Always.": "Access It Always.",
           "Enterprise AI, Built for Industry": "Built for Industry", "One Unified Enterprise Platform": "Enterprise Platform", "Bringing Intelligence to Enterprise Data": "Enterprise Data",
           "Retire. Preserve. Archive. Activate.": "Activate.", "Purpose-Built for Every Industry": "Every Industry",
           "Solving Complex Data Challenges at Enterprise Scale": "Enterprise Scale", "Recognized by Leading Research Firms": "Leading Research Firms"}


def heading_kw(c, lt, k, title, kw, G, x, y, tout, size):
    pre = title[: title.index(kw)].rstrip()
    a1 = vis(lt, 0.25, tout) * G
    put(c, k, x - (1 - ease((lt - 0.25) / 0.6)) * 40, y, a1)
    tp = text(pre, "xbold", size, TXT)
    tk = text(kw, "xbold", size, (255, 255, 255))
    a2 = vis(lt, 0.4, tout) * G
    p = ease((lt - 0.4) / 0.7)
    yy = y + 30 + (1 - p) * 34
    put(c, tp, x, yy, a2)
    # keyword: blue pill sweeps in, then the word lands on it
    kx = x + tp.width + 14
    pw = tk.width + 28
    sp = eio((lt - 0.85) / 0.55)
    if sp > 0 and G > 0.01:
        ph = tk.height + 2
        pill_ = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        ImageDraw.Draw(pill_).rounded_rectangle((0, 0, int(pw * sp), ph - 1), 12, fill=BLUE + (255,))
        put(c, pill_, kx - 14, yy - 2, G * (1 - (eio((lt - tout) / 0.45) if tout is not None else 0)))
    ta = vis(lt, 1.05, tout, 0.4) * G
    put(c, tk, kx + (1 - ease((lt - 1.05) / 0.4)) * 16, yy, ta)


@lru_cache(None)
def callout_img_r(title, sub, active=False):
    """mirror of callout_img: text right-aligned, accent bar on the right (inner) side"""
    t1 = text(title, "bold", 30, TXT)
    t2 = text(sub, "med", 20, TXT2) if sub else None
    tw = max(t1.width, t2.width if t2 else 0)
    w = tw + 20
    h = t1.height + (t2.height + 2 if t2 else 0) + 6
    im = Image.new("RGBA", (w, max(h, 40)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((w - 4, 4, w - 1, h - 2), 2, fill=(RED if active else KICK) + (255,))
    im.alpha_composite(t1, (w - 20 - t1.width, 0))
    if t2:
        im.alpha_composite(t2, (w - 20 - t2.width, t1.height + 2))
    return im


def callout_r(c, x_right, y, title, sub, a, active=False):
    """right edge of the callout sits at x_right; wipes in from the inner side"""
    if a <= 0.004:
        return
    im = callout_img_r(title, sub, active)
    vw = max(1, int(im.width * min(1.0, a * 1.15)))
    put(c, im.crop((im.width - vw, 0, im.width, im.height)), x_right - vw, y + (1 - a) * 14, a)


@lru_cache(None)
def callout_img(num, title, sub, w, active=False, ico=None):
    t1 = fit_text(title, "bold", 30, w - 24, TXT)
    t2 = fit_text(sub, "med", 20, w - 24, TXT2) if sub else None
    h = t1.height + (t2.height + 2 if t2 else 0) + 6
    im = Image.new("RGBA", (w, max(h, 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 4, 4, h - 2), 2, fill=(RED if active else KICK) + (255,))
    im.alpha_composite(t1, (20, 0))
    if t2:
        im.alpha_composite(t2, (20, t1.height + 2))
    return im


def callout(c, x, y, num, title, sub, w, a, active=False, slide=40, ico=None):
    if a <= 0.004:
        return
    im = callout_img(num, title, sub, w, active, ico)
    # wipe-in reveal from the left + rise
    vw = max(1, int(im.width * min(1.0, a * 1.15)))
    put(c, im.crop((0, 0, vw, im.height)), x, y + (1 - a) * 14, a)


@lru_cache(None)
def pill_img(label, active, size=19, padx=26, h=48, track=2, dim=False):
    fg = (255, 255, 255) if active else ((150, 150, 190) if dim else (225, 228, 248))
    tx = text(label, "bold", size, fg, track)
    w = tx.width + padx * 2
    im = box(w, h, h // 2, RED + (255,) if active else (66, 56, 150, 235), None if active else (98, 88, 180), 2)
    im.alpha_composite(tx, (padx, int(h / 2 - tx.height / 2) + 1))
    return im


def pill(c, s, a, y=962, size=27, cx=W / 2):
    im = sub_text(s, size + 2)
    put(c, im, cx - im.width / 2, y - 6, a)


def sub_text(s, size=30):
    return _sub_text(s, size)


@lru_cache(64)
def _sub_text(s, size):
    tx = fit_text(s, "semi", size, 1700, (255, 255, 255))
    pad = 16
    im = Image.new("RGBA", (tx.width + pad * 2, tx.height + pad * 2), (0, 0, 0, 0))
    shd = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shd.alpha_composite(tx, (pad, pad + 2))
    al = shd.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: min(255, int(v * 1.6)))
    black = Image.new("RGBA", im.size, (4, 2, 20, 0)); black.putalpha(al)
    im.alpha_composite(black)
    im.alpha_composite(tx, (pad, pad))
    return im


def caption(c, t):
    for (t0, t1, s, i, first) in CAPS:
        if t0 <= t < t1:
            if LINES[i]["scene"] == 7 and i >= len(LINES) - 2:
                return
            a = vis(t, t0, t1 - 0.2, 0.25, 0.2) if first or True else 1.0
            # chunks within a line switch with a quick fade
            im = sub_text(s, 30)
            put(c, im, (W - im.width) / 2, 966, max(a, 0.0))
            return


def chrome(c, t, show_logo=1.0):
    put(c, text("SOLIX EMPOWER 2026", "bold", 15, TXT2, 4), 92, 46, vis(t, 0.6, None, 0.8))
    if show_logo > 0:
        put(c, logo(210), W - 92 - 210, 34, show_logo)
    ImageDraw.Draw(c).rectangle((0, H - 6, int(W * t / TOTAL), H), fill=RED)


def bez(p0, p1, p2, p3, n=48):
    out = []
    for k in range(n + 1):
        u = k / n
        out.append(tuple((1 - u) ** 3 * p0[i] + 3 * (1 - u) ** 2 * u * p1[i] + 3 * (1 - u) * u ** 2 * p2[i] + u ** 3 * p3[i] for i in range(2)))
    return out


def connector(c, pts, p, a, t, pulse=True, width=3):
    """draw a line progressively with a travelling pulse dot"""
    if a <= 0 or p <= 0:
        return
    d = ImageDraw.Draw(c)
    n = max(2, int(len(pts) * p))
    col = mix(BGC, RED, a)
    d.line(pts[:n], fill=col, width=width)
    hx, hy = pts[n - 1]
    d.ellipse((hx - 6, hy - 6, hx + 6, hy + 6), fill=col)
    if pulse and p >= 1:
        u = (t * 0.6) % 1
        k = int(u * (len(pts) - 1))
        x, y = pts[k]
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=mix(BGC, (255, 140, 140), a))
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 255))


@lru_cache(None)
def glow(r, alpha=70):
    im = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((r, r, r * 3, r * 3), fill=BLUE + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(r * 0.45))


def dashed_ring(c, cx, cy, r, t, a, n=36, speed=0.25, width=4):
    if a <= 0:
        return
    d = ImageDraw.Draw(c)
    col = mix(BGC, (110, 190, 240), a * 0.9)
    for k in range(n):
        ang = 2 * math.pi * k / n + t * speed
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=col)


def hub_center(c, cx, cy, size, lt, t, a, label=None):
    if a <= 0:
        return
    g = glow(int(size * 0.9))
    put(c, g, cx - g.width / 2, cy - g.height / 2, a * (0.8 + 0.2 * math.sin(t * 2.2)))
    disc = disc_img(int(size * 1.5))
    put(c, disc, cx - disc.width / 2, cy - disc.height / 2, a)
    dashed_ring(c, cx, cy, size * 0.95, t, a)
    s = back((lt) / 0.7)
    put_scaled(c, bolt(size), cx, cy, max(0.01, s), a)
    if label:
        tl_ = text(label, "bold", 20, TXT, 3)
        put(c, tl_, cx - tl_.width / 2, cy + size * 1.0, a)


@lru_cache(None)
def disc_img(d):
    pad = 40
    im = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad + 6, pad + 16, pad + d - 6, pad + d + 16), fill=(0, 0, 10, 160))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    im.alpha_composite(sphere_img(d, False), (pad, pad))
    return im


def card_switch(c, lt, items, x, y, maxw, maxh, G, dur=0.7, align="center"):
    """items: list of (t_on, kind, name, extra). Cross-slide with push-in."""
    cur = None
    for k, it in enumerate(items):
        if lt >= it[0]:
            cur = k
    if cur is None:
        return None

    def get(it, l):
        t_on, kind, name = it[:3]
        if kind == "still":
            k_ = items.index(it)
            dd = (items[k_ + 1][0] - t_on) if k_ + 1 < len(items) else 9.0
            return still(name, maxw, maxh, l, dd)
        if kind == "fn":
            return name(l)
        if kind == "scroll":
            k_ = items.index(it)
            dd = (items[k_ + 1][0] - t_on) if k_ + 1 < len(items) else 9.0
            _register(name)
            return screens.screen_scroll(name, l, maxw, maxh, dd)
        ex = it[3] if len(it) > 3 else {}
        return clip(name, l + ex.get("off", 0), ex.get("w", maxw), ex.get("h", maxh), ex.get("rate", 1.0), ex.get("top", False))

    def xo(im):
        return (maxw - im.width) / 2 if align == "center" else 0
    t_on = items[cur][0]
    p = eio((lt - t_on) / dur)
    im = get(items[cur], lt - t_on)
    if cur > 0 and p < 1:
        prev = get(items[cur - 1], lt - items[cur - 1][0])
        draw_card(c, prev, x + xo(prev) - p * 140, y, (1 - p) * G)
        draw_card(c, im, x + xo(im) + (1 - p) * 140, y, p * G)
    else:
        a = vis(lt, t_on, None, 0.7) if cur == 0 else 1.0
        draw_card(c, im, x + xo(im) + (1 - ease((lt - t_on) / 0.7)) * 80 * (cur == 0), y + (1 - a) * 20, a * G)
    return im



# ------------------------------------------------------------------ crisp native panels
def wrap(s, w, size, maxw):
    f = font(w, size)
    out, cur = [], ""
    for word in s.split():
        tst = (cur + " " + word).strip()
        if f.getlength(tst) > maxw and cur:
            out.append(cur); cur = word
        else:
            cur = tst
    if cur:
        out.append(cur)
    return out


def para(im, s, w, size, color, x, y, maxw, lh=1.45):
    d = ImageDraw.Draw(im)
    f = font(w, size)
    for i, ln in enumerate(wrap(s, w, size, maxw)):
        d.text((x, y + i * size * lh), ln, font=f, fill=color)
    return y + len(wrap(s, w, size, maxw)) * size * lh


SITE_BLUE = (16, 132, 196)
SITE_INK = (22, 26, 44)
SITE_GREY = (88, 94, 108)


@lru_cache(None)
def ecs_base(w, h):
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    tag = text("ENTERPRISE CONTENT SERVICES", "semi", 15, SITE_BLUE, 1)
    d.rounded_rectangle((40, 30, 40 + tag.width + 24, 30 + 34), 6, fill=(226, 242, 251))
    im.alpha_composite(tag, (52, 36))
    im.alpha_composite(text("SOLIX ECS", "black", 34, SITE_INK), (40, 78))
    para(im, "Solix ECS is an all-in-one, cloud-native platform offering secure, centralized content management, AI-powered automation, robust compliance, and seamless collaboration for enterprise workgroups.",
         "reg", 17, SITE_GREY, 40, 128, w - 80)
    tiles = [("Enterprise Cloud Repository", "Break data silos with a single, secure cloud content hub. Store, organize, discover, process, and govern every file in one place.", "db"),
             ("Generative AI", "Embedded GenAI services auto-classify documents, surface insights, enable Q&A, generate summaries, and power natural-language search.", "spark"),
             ("Secure Sharing & Collaboration", "Share content safely with colleagues, partners, and customers.", "shield"),
             ("Governance & Compliance", "Automated audit trails, encryption in transit and at rest, and retention.", "doc")]
    tw, th = 318, 186
    for j, (ti, de, ic) in enumerate(tiles):
        x0 = 40 + (j % 2) * (tw + 18)
        y0 = 200 + (j // 2) * (th + 16)
        d.rounded_rectangle((x0, y0, x0 + tw, y0 + th), 10, fill=(248, 250, 252), outline=(232, 236, 242), width=2)
        im.alpha_composite(icon(ic, 40, SITE_BLUE), (x0 + 16, y0 + 16))
        tl = wrap(ti, "bold", 18, tw - 80)
        for k, ln in enumerate(tl):
            d.text((x0 + 66, y0 + 18 + k * 23), ln, font=font("bold", 18), fill=SITE_INK)
        para(im, de, "reg", 14, SITE_GREY, x0 + 16, y0 + 70, tw - 32, 1.42)
    return im


def ecs_panel(l, w=1160, h=600):
    im = ecs_base(w, h).copy()
    d = ImageDraw.Draw(im)
    cx, cy = 720 + (w - 720) // 2, 395
    for r, col in ((170, (232, 244, 252)), (122, (214, 236, 250)), (76, (190, 224, 247))):
        rr = r * (0.9 + 0.1 * ease(l / 1.2))
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    ic = icon("doc", 70, SITE_BLUE)
    im.alpha_composite(ic, (cx - 35, cy - 35))
    chips = [("Governance and compliance", (40, 70, 160), -150, -150), ("Bulk data migration tools", (36, 64, 120), -190, -60),
             ("Secure file sharing", (24, 160, 210), 40, 120), ("Mobile access", (224, 70, 100), -200, 150)]
    for j, (lab, col, dx, dy) in enumerate(chips):
        a = ease((l - 0.4 - 0.25 * j) / 0.6)
        if a <= 0:
            continue
        fy = 5 * math.sin(l * 1.6 + j)
        tx = text(lab, "semi", 14, (60, 80, 140))
        bw = tx.width + 52
        x0, y0 = cx + dx, cy + dy + fy + (1 - a) * 14
        chip = box(bw, 40, 8, (255, 255, 255, int(255 * a)), (226, 232, 242))
        chip.alpha_composite(tx, (42, 10))
        ImageDraw.Draw(chip).ellipse((10, 8, 34, 32), fill=col + (int(255 * a),))
        al = chip.getchannel("A").point(lambda v: int(v * a))
        chip.putalpha(al)
        im.alpha_composite(chip, (int(x0), int(y0)))
    return finish_card(im.convert("RGB"), w, h)


def wordmark(name, size):
    if name == "Forrester":
        f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", size)
        im = Image.new("RGBA", (int(f.getlength("FORRESTER")) + 10, size + 12), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), "FORRESTER", font=f, fill=(20, 92, 64))
        return im
    if name == "Gartner":
        return text("Gartner", "bold", int(size * 1.15), (0, 32, 96))
    im = Image.new("RGBA", (int(size * 4.2), size + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, size * 0.3, size * 0.45, size * 0.75), outline=(60, 120, 170), width=3)
    im.alpha_composite(text("Bloor", "black", int(size * 1.1), (40, 110, 170)), (int(size * 0.55), -4))
    return im


RECOG = [("Forrester", "Forrester - Now Tech: Data Masking (2021)", "Recognized as a vendor in Persistent, Dynamic and Unstructured Data Masking"),
         ("Forrester", "Forrester - Now Tech: Data Governance (2021)", "Recognized as a vendor in data strategy and process solutions"),
         ("Gartner", "Gartner - Market Guide: Data Masking (2020)", "Recognized as a vendor in Structured & Unstructured Data Masking"),
         ("Bloor", "Bloor - Market Guide: Sensitive Data Discovery (2020)", "Recognized as a Strong Challenger in its Sensitive Data Discovery capabilities"),
         ("Bloor", "Bloor - Market Guide: Data Governance (2020)", "Recognized as a Strong Innovator in the Data Governance space")]


@lru_cache(None)
def recog_card(j, w, h, hl):
    nm, ti, de = RECOG[j]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 10, fill=(255, 255, 255, 255), outline=RED if hl else (232, 236, 242), width=3 if hl else 2)
    im.alpha_composite(wordmark(nm, 30), (22, 18))
    y = 72
    for ln in wrap(ti, "semi", 16, w - 44):
        d.text((22, y), ln, font=font("semi", 16), fill=SITE_BLUE); y += 22
    para(im, de, "reg", 14, SITE_GREY, 22, y + 6, w - 44, 1.4)
    return im


def recog_panel(l, w=1100, h=590, bloor_on=False):
    im = Image.new("RGBA", (w, h), (250, 251, 253, 255))
    d = ImageDraw.Draw(im)
    cw, ch = 340, 172
    pos = [(26, 26), (384, 26), (26, 214), (384, 214), (26, 402)]
    for j, (x0, y0) in enumerate(pos):
        a = ease((l - 0.15 * j) / 0.6)
        if a <= 0:
            continue
        card = recog_card(j, cw if j < 4 else 698, ch, bool(bloor_on and RECOG[j][0] == "Bloor"))
        card = card.copy(); card.putalpha(card.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(card, (x0, int(y0 + (1 - a) * 16)))
    tag = text("Analysts Recognitions", "semi", 14, SITE_BLUE)
    d.rounded_rectangle((760, 200, 760 + tag.width + 24, 232), 6, fill=(226, 242, 251))
    im.alpha_composite(tag, (772, 206))
    for k, ln in enumerate(wrap("TRUSTED BY LEADING ANALYSTS", "black", 28, 310)):
        im.alpha_composite(text(ln, "black", 28, SITE_INK), (760, 248 + k * 36))
    para(im, "Analysts Recognize Solix As A Pioneer In Innovative Data Security and Compliance Solutions.", "reg", 16, SITE_GREY, 760, 330, 310)
    return finish_card(im.convert("RGB"), w, h)


# ------------------------------------------------------------------ scenes
def scene0(c, t, lt, G):
    return


@lru_cache(None)
def new_badge():
    tx = text("NEW AT EMPOWER", "black", 15, (255, 255, 255), 2)
    im = Image.new("RGBA", (tx.width + 30, 32), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, tx.width + 29, 31), 16, fill=RED + (255,))
    im.alpha_composite(tx, (15, 6))
    return im





@lru_cache(None)
def pill_icon(size):
    ss = 4; S_ = size * ss
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = int(S_ * 0.06)
    d.rounded_rectangle((S_ * 0.2, S_ * 0.38, S_ * 0.8, S_ * 0.62), S_ * 0.12, outline=RED + (255,), width=lw)
    d.line((S_ * 0.5, S_ * 0.38, S_ * 0.5, S_ * 0.62), fill=RED + (255,), width=lw)
    im = im.rotate(35, resample=Image.BICUBIC)
    return im.resize((size, size), Image.LANCZOS)


def patient360(c, cx, cy, l, t, a):
    if a <= 0.004:
        return
    srcs = [("EHR", "doc"), ("IMAGING", "chart"), ("BILLING", "dollar"), ("PHARMACY", "pill"), ("LAB", "flask")]
    holo = human3d.hologram(t, 560, a)
    hx, hy = cx - holo.width / 2, cy - holo.height / 2 - 10
    nodes = []
    for j, (lab, ic) in enumerate(srcs):
        ang = j * 2 * math.pi / len(srcs) + t * 0.35
        nx = cx + 340 * math.cos(ang)
        nz = math.sin(ang)
        ny = cy - 40 + 70 * nz
        nodes.append((nz, nx, ny, lab, ic, j))
    nodes.sort()
    back_ = [n for n in nodes if n[0] < 0]
    front = [n for n in nodes if n[0] >= 0]

    def draw_nodes(lst):
        for (nz, nx, ny, lab, ic, j) in lst:
            t0 = 0.3 + 0.15 * j
            aa = vis(l, t0) * a * (0.55 + 0.45 * (nz + 1) / 2)
            if aa <= 0:
                continue
            sz = int(70 + 22 * (nz + 1) / 2)
            if ic == "pill":
                nd = node("doc", sz).copy()
                pad = 34
                ImageDraw.Draw(nd).ellipse((pad + sz * 0.12, pad + sz * 0.12, pad + sz * 0.88, pad + sz * 0.88), fill=(250, 250, 255, 255))
                pi_ = pill_icon(int(sz * 0.6))
                nd.alpha_composite(pi_, (int(pad + sz * 0.2), int(pad + sz * 0.2)))
            else:
                nd = node(ic, sz)
            pts = [(nx + (cx - nx) * u / 20, ny + (cy - 60 - ny) * u / 20) for u in range(21)]
            connector(c, pts, ease((l - t0) / 0.8), aa * 0.8, t + j * 0.2, width=2)
            put_scaled(c, nd, nx, ny, max(0.05, back((l - t0) / 0.5)), aa)
            tl_ = text(lab, "bold", 15, TXT, 2)
            put(c, tl_, nx - tl_.width / 2, ny + sz / 2 + 10, aa)
    draw_nodes(back_)
    g = glow(150, 45)
    put(c, g, cx - g.width / 2, cy - g.height / 2, a)
    put(c, holo, hx, hy, 1.0)
    draw_nodes(front)
    tl_ = text("UNIFIED PATIENT RECORD", "black", 22, (255, 120, 120), 3)
    put(c, tl_, cx - tl_.width / 2, cy + holo.height / 2 + 6, a)


# --- EAI Pharma + EAI Healthcare section (v7): pure motion graphics -------------------------------

@lru_cache(None)
def atom_img(d, col):
    ss = 2
    D = max(4, d * ss)
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    lam = np.clip(1.05 - 0.75 * np.hypot(xx - (cx - D * 0.18), yy - (cy - D * 0.2)) / D * 1.6, 0.25, 1.0)
    rgb = np.array(col, float)[None, None] * lam[..., None]
    spec = np.exp(-(((xx - (cx - D * 0.2)) / (D * 0.13)) ** 2 + ((yy - (cy - D * 0.24)) / (D * 0.09)) ** 2))
    rgb = np.clip(rgb + spec[..., None] * 170, 0, 255)
    a = np.clip((1 - r) * D * 0.5, 0, 1) * 255
    return Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA").resize((max(2, d), max(2, d)), Image.LANCZOS)


@lru_cache(None)
def bolt_sphere(d):
    """Big glossy Solix bolt sphere with soft drop shadow."""
    pad = 60
    im = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad + 10, pad + 26, pad + d - 10, pad + d + 26), fill=(0, 0, 10, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    b = bolt(d).copy()
    D = d
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    shade = np.clip(1.0 - 0.38 * np.clip(r - 0.35, 0, 1) ** 1.5, 0, 1)
    arr = np.asarray(b).astype(float)
    arr[..., :3] *= shade[..., None]
    spec = np.exp(-(((xx - (cx - D * 0.2)) / (D * 0.2)) ** 2 + ((yy - (cy - D * 0.27)) / (D * 0.1)) ** 2))
    arr[..., :3] = np.clip(arr[..., :3] + spec[..., None] * 90, 0, 255)
    im.alpha_composite(Image.fromarray(arr.astype(np.uint8), "RGBA"), (pad, pad))
    return im


# simple drug-like molecule (fused 6/5 ring + side chains), unit coordinates
MOL_ATOMS = [
    ("C", (0.0, 1.0, 0.0)), ("C", (0.87, 0.5, 0.0)), ("C", (0.87, -0.5, 0.0)), ("C", (0.0, -1.0, 0.0)), ("C", (-0.87, -0.5, 0.0)), ("C", (-0.87, 0.5, 0.0)),
    ("N", (1.82, -0.86, 0.12)), ("C", (2.45, 0.05, 0.2)), ("C", (1.85, 0.95, 0.12)),
    ("O", (0.0, 2.15, -0.25)), ("C", (-1.95, -1.05, 0.45)), ("N", (-2.95, -0.45, 0.85)), ("O", (-2.05, -2.2, 0.2)),
    ("C", (3.7, 0.05, 0.55)), ("O", (4.35, 0.95, 0.8)), ("N", (4.25, -1.0, 0.7)),
    ("H", (0.0, -2.05, 0.1)), ("H", (-0.55, 2.7, -0.6)), ("H", (-3.7, -1.0, 1.1)), ("H", (2.4, 1.95, 0.0)),
]
MOL_BONDS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (2, 6), (6, 7), (7, 8), (8, 1), (0, 9), (4, 10), (10, 11), (10, 12),
             (7, 13), (13, 14), (13, 15), (3, 16), (9, 17), (11, 18), (8, 19)]
MOL_COL = {"C": (70, 150, 230), "N": (120, 110, 255), "O": (238, 60, 60), "H": (235, 238, 250)}
MOL_SIZE = {"C": 46, "N": 48, "O": 48, "H": 26}


def molecule(c, cx, cy, l, t, a, scale=115):
    if a <= 0.01:
        return []
    P = np.array([p for _, p in MOL_ATOMS], float)
    P = P - P.mean(axis=0)
    ay, ax = t * 0.45, 0.35 + 0.25 * math.sin(t * 0.3)
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Q = P @ Ry.T @ Rx.T
    persp = 1 / (1 + Q[:, 2] * 0.08)
    sx = cx + Q[:, 0] * scale * persp
    sy = cy - Q[:, 1] * scale * persp
    order = np.argsort(Q[:, 2])[::-1]  # far first (larger z = farther)
    d = ImageDraw.Draw(c)
    grow = [ease((l - 0.25 - 0.05 * i) / 0.5) for i in range(len(P))]
    for (i, j) in MOL_BONDS:
        g = min(grow[i], grow[j])
        if g <= 0:
            continue
        zc = (Q[i, 2] + Q[j, 2]) / 2
        k = (0.55 + 0.45 * (1 - (zc + 3) / 6)) * a * g
        x2 = sx[i] + (sx[j] - sx[i]) * g; y2 = sy[i] + (sy[j] - sy[i]) * g
        d.line((sx[i], sy[i], x2, y2), fill=mix(BGC, (170, 210, 255), k), width=max(2, int(7 * persp[i])))
    for i in order:
        g = grow[i]
        if g <= 0:
            continue
        el = MOL_ATOMS[i][0]
        sz = int(MOL_SIZE[el] * persp[i] * (0.4 + 0.6 * back(g)) * scale / 115)
        im = atom_img(max(4, sz // 2 * 2), MOL_COL[el])
        dz = 0.6 + 0.4 * (1 - (Q[i, 2] + 3) / 6)
        put(c, im, sx[i] - im.width / 2, sy[i] - im.height / 2, a * min(1, dz + 0.2))
    return list(zip(sx, sy))


def kin_word(c, s, x, y, size, col, a, lt0, l, w="black", track=0):
    """word rises in from a mask line"""
    im = text(s, w, size, col, track)
    p = ease((l - lt0) / 0.55)
    if p <= 0 or a <= 0:
        return im
    hh = im.height
    show = im.crop((0, 0, im.width, hh))
    put(c, show, x, y + (1 - p) * hh * 0.6, a * p)
    return im


def tag_pill(label, fill, size=40, padx=26, h=72):
    tx = text(label, "black", size, (255, 255, 255), 2)
    im = Image.new("RGBA", (tx.width + padx * 2, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, tx.width + padx * 2 - 1, h - 1), h // 2, fill=fill + (255,))
    im.alpha_composite(tx, (padx, int(h / 2 - tx.height / 2) + 1))
    return im


def phase_alpha(lt, t0, t1, din=0.5, dout=0.5):
    return ease((lt - t0) / din) * (1 - eio((lt - t1) / dout))


def pharma_phase(c, t, l, a):
    # title block (left)
    tD = 1.25
    tX = lc(4, 7, "transforming", lead=0.3) + 0.25
    tI = lc(4, 7, "intelligent insights", lead=0.3)
    # DATA + AI chips, then merge into ACCELERATE DRUG DISCOVERY
    m = eio((l - tX) / 0.6)
    if l >= tD and m < 1:
        pd = back((l - tD) / 0.5); pa = back((l - tD - 0.18) / 0.5)
        d_ = tag_pill("DATA", BLUE); a_ = tag_pill("AI", RED); pl = text("+", "black", 64, TXT)
        x0 = 120
        gx = 0 + m * 120
        put_scaled(c, d_, x0 + d_.width / 2 + gx, 580, max(0.05, pd) * (1 - 0.3 * m), a * (1 - m))
        put(c, pl, x0 + d_.width + 20 + gx * 1.4, 540, a * ease((l - tD - 0.1) / 0.3) * (1 - m))
        put_scaled(c, a_, x0 + d_.width + 90 + a_.width / 2 + gx * 0.4, 580, max(0.05, pa) * (1 - 0.3 * m), a * (1 - m))
    if l >= tX:
        w1 = kin_word(c, "ACCELERATE", 120, 530, 70, TXT, a, tX + 0.15, l, "black", 2)
        p2 = eio((l - tX - 0.45) / 0.5)
        tk = text("DRUG DISCOVERY", "black", 70, (255, 255, 255), 2)
        if p2 > 0:
            pw = int((tk.width + 40) * p2)
            pill_ = Image.new("RGBA", (tk.width + 40, tk.height + 10), (0, 0, 0, 0))
            ImageDraw.Draw(pill_).rounded_rectangle((0, 0, pw, tk.height + 9), 14, fill=BLUE + (255,))
            put(c, pill_, 100, 622, a)
            put(c, tk, 120 + (1 - ease((l - tX - 0.7) / 0.4)) * 20, 625, a * ease((l - tX - 0.7) / 0.4))
    if l >= tI:
        p = ease((l - tI) / 0.6)
        t1 = text("RESEARCH", "bold", 24, TXT2, 4)
        t2 = text("INTELLIGENT INSIGHTS", "bold", 24, KICK, 4)
        put(c, t1, 122, 770, a * p)
        ax0, ax1 = 122 + t1.width + 18, 122 + t1.width + 18 + 70 * p
        ImageDraw.Draw(c).line((ax0, 785, ax1, 785), fill=mix(BGC, RED, a * p), width=3)
        if p > 0.6:
            ImageDraw.Draw(c).polygon([(ax1, 778), (ax1 + 12, 785), (ax1, 792)], fill=mix(BGC, RED, a))
        put(c, t2, ax1 + 26, 770, a * ease((l - tI - 0.3) / 0.5))
    # molecule + research data, AI connections (right)
    cx, cy = 1440, 520
    g = glow(230, 40)
    put(c, g, cx - g.width / 2, cy - g.height / 2, a * 0.9)
    pts = molecule(c, cx, cy, l, t, a, 100)
    tags = [("COMPOUNDS", (1700, 250), 0), ("ASSAYS", (1760, 700), 7), ("GENOMICS", (1050, 840), 12), ("TRIALS", (1000, 200), 14)]
    d = ImageDraw.Draw(c)
    for j, (lab, (tx, ty), ai) in enumerate(tags):
        t0 = 1.2 + 0.25 * j
        aa = a * ease((l - t0) / 0.5)
        if aa <= 0 or not pts:
            continue
        fy = ty + 8 * math.sin(t * 1.2 + j)
        ax_, ay_ = pts[ai]
        p = ease((l - t0 - 0.2) / 0.7)
        # dashed AI connection
        n = 18
        for q in range(int(n * p)):
            if q % 2 == 0:
                u0, u1 = q / n, (q + 1) / n
                d.line((ax_ + (tx - ax_) * u0, ay_ + (fy - ay_) * u0, ax_ + (tx - ax_) * u1, ay_ + (fy - ay_) * u1), fill=mix(BGC, (120, 190, 255), aa * 0.8), width=2)
        if p >= 1:
            u = (t * 0.7 + j * 0.3) % 1
            px, py = ax_ + (tx - ax_) * u, ay_ + (fy - ay_) * u
            d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=mix(BGC, (255, 255, 255), aa))
        d.ellipse((tx - 7, fy - 7, tx + 7, fy + 7), fill=mix(BGC, RED, aa))
        tl_ = text(lab, "bold", 18, TXT, 4)
        put(c, tl_, tx + 16, fy - tl_.height / 2, aa)


def foundation_phase(c, t, l, a):
    e = text("EAI", "black", 96, RED)
    h_ = text("HEALTHCARE", "black", 96, TXT)
    tw = e.width + 24 + h_.width
    x0 = (W - tw) / 2
    k_ = text("EAI HEALTHCARE PLATFORM", "bold", 18, KICK, 6)
    st = text("Accelerated Care by empowering clinicians for intelligent outcomes.", "med", 30, TXT2)
    put(c, st, (W - st.width) / 2, 322 + (1 - ease((l - 0.6) / 0.6)) * 14, a * ease((l - 0.6) / 0.6))
    p1 = text("Care Creates Data", "bold", 32, TXT); bar = text("|", "bold", 32, RED); p2 = text("Data Accelerates Cure", "bold", 32, (255, 90, 90))
    tw2 = p1.width + 30 + bar.width + 30 + p2.width
    x2 = (W - tw2) / 2
    a2 = a * ease((l - 0.95) / 0.6)
    put(c, p1, x2 - (1 - ease((l - 0.95) / 0.6)) * 30, 372, a2)
    put(c, bar, x2 + p1.width + 30, 372, a2)
    put(c, p2, x2 + p1.width + 60 + bar.width + (1 - ease((l - 1.15) / 0.6)) * 30, 372, a * ease((l - 1.15) / 0.6))
    stages = [("TRUSTED DATA", "FOUNDATION", "db", "trusted data"), ("COLLABORATIVE", "INTELLIGENCE", "spark", "collaborative"),
              ("ACTIONABLE", "OUTCOMES", "heart", "actionable")]
    xs = [420, 960, 1500]
    y = 600
    d = ImageDraw.Draw(c)
    for j, (l1, l2, ic, ph) in enumerate(stages):
        tk = lc(4, 8, ph, lead=0.35) - SC_LOCAL[4]["tF"]
        aa = a * ease((l - tk) / 0.5)
        if j > 0:
            # flowing data link from previous stage
            tp = ease((l - tk + 0.3) / 0.6)
            xa, xb = xs[j - 1] + 95, xs[j] - 95
            if tp > 0:
                d.line((xa, y, xa + (xb - xa) * tp, y), fill=mix(BGC, (120, 190, 255), a * 0.9), width=3)
                if tp >= 1:
                    for q in range(4):
                        u = (t * 0.55 + q / 4) % 1
                        px = xa + (xb - xa) * u
                        d.ellipse((px - 5, y - 5, px + 5, y + 5), fill=mix(BGC, (255, 255, 255), a))
                    d.polygon([(xb - 2, y - 9), (xb + 12, y), (xb - 2, y + 9)], fill=mix(BGC, RED, a))
        if aa <= 0:
            continue
        put_scaled(c, node(ic, 170), xs[j], y, max(0.05, back((l - tk) / 0.6)), aa)
        t1 = text(l1, "black", 34, TXT, 2)
        t2 = text(l2, "black", 34, KICK if j < 2 else (255, 110, 110), 2)
        put(c, t1, xs[j] - t1.width / 2, y + 120 + (1 - ease((l - tk - 0.15) / 0.5)) * 16, aa)
        put(c, t2, xs[j] - t2.width / 2, y + 166 + (1 - ease((l - tk - 0.25) / 0.5)) * 16, aa * ease((l - tk - 0.25) / 0.5))


PLAT_NODES = [  # label lines, sub, icon, (dx, dy)  -> three down the left, three down the right
    (("1. AI WAREHOUSE",), "The unified enterprise data foundation", "warehouse", (-470, 230)),
    (("2. FEDERATED", "GOVERNANCE"), "Trust, control and accountability", "shield", (-470, 0)),
    (("3. AI PATIENT", "360 ANALYTICS"), "A longitudinal intelligence layer for every patient", "chart", (-470, -230)),
    (("4. INTELLIGENT", "IMAGING & RADIOLOGY"), "Imaging intelligence in the enterprise context", "image", (470, -230)),
    (("5. AI CLINICAL", "INTELLIGENCE"), "From data to contextual, explainable intelligence", "chat", (470, 0)),
    (("6. PURPOSE-BUILT", "HEALTHCARE MODELS"), "Specialty-specific multi-agentic intelligence", "heart", (470, 230)),
]


def platform_phase(c, t, l, a, cx0=960, cy0=540, dim_all=False):
    hl = [(2, lc(4, 9, "Patient three sixty", lead=0.3)), (4, lc(4, 9, "AI Clinical", lead=0.3)), (3, lc(4, 9, "Intelligent Imaging", lead=0.3)), (5, lc(4, 9, "Purpose-Built", lead=0.3))]
    hl = [(i, tk - SC_LOCAL[4]["tC"]) for i, tk in hl]
    act = None
    for i, tk in hl:
        if l >= tk:
            act = (i, tk)
    # gentle camera drift toward the active node
    if act:
        dx, dy = PLAT_NODES[act[0]][3]
        p = eio((l - act[1]) / 0.8)
        cx, cy = cx0, cy0
    else:
        cx, cy = cx0, cy0
    d = ImageDraw.Draw(c)
    # motion points converging into the Solix bolt
    rr = random.Random(9)
    conv = ease(l / 1.4)
    if conv < 1:
        for k in range(70):
            sx_, sy_ = rr.uniform(-100, W + 100), rr.uniform(-100, H + 100)
            x = sx_ + (cx - sx_) * conv
            y = sy_ + (cy - sy_) * conv
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=mix(BGC, (130, 200, 255), a * (1 - conv * 0.7)))
    bs = 360
    sph = bolt_sphere(bs)
    g = glow(220, 50)
    put(c, g, cx - g.width / 2, cy - g.height / 2, a)
    dashed_ring(c, cx, cy, bs * 0.66, t, a, n=48, speed=0.2, width=5)
    put_scaled(c, sph, cx, cy, max(0.05, back((l - 0.6) / 0.7)), a)
    tl_ = text("EAI ", "black", 34, RED, 2)
    th_ = text("HEALTHCARE", "black", 34, TXT, 2)
    put(c, tl_, cx - (tl_.width + th_.width) / 2, cy + bs * 0.72 + 6, a * ease((l - 0.9) / 0.5))
    put(c, th_, cx - (tl_.width + th_.width) / 2 + tl_.width, cy + bs * 0.72 + 6, a * ease((l - 0.9) / 0.5))
    for j, (lines, sub, ic, (dx, dy)) in enumerate(PLAT_NODES):
        t0 = 0.9 + 0.12 * j
        aa = a * ease((l - t0) / 0.5)
        if aa <= 0:
            continue
        is_act = act is not None and act[0] == j
        was = any(i == j and l >= tk for i, tk in hl)
        dimk = 0.45 if (act is not None and not was) else 1.0
        nx, ny = cx + dx, cy + dy
        # connector from ring to node
        ang = math.atan2(dy, dx)
        rx, ry = cx + bs * 0.66 * math.cos(ang), cy + bs * 0.66 * math.sin(ang)
        p = ease((l - t0) / 0.6)
        col = RED if was else (140, 190, 240)
        ex_, ey_ = nx - (70 if dx > 0 else -70), ny
        d.line((rx, ry, rx + (ex_ - rx) * p, ry + (ey_ - ry) * p), fill=mix(BGC, col, aa * dimk), width=4 if was else 2)
        d.ellipse((rx - 9, ry - 9, rx + 9, ry + 9), fill=mix(BGC, BLUE if not was else RED, aa))
        d.ellipse((rx - 4, ry - 4, rx + 4, ry + 4), fill=(255, 255, 255))
        if was and p >= 1:
            u = (t * 0.8 + j * 0.2) % 1
            px, py = rx + (ex_ - rx) * u, ry + (ey_ - ry) * u
            d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=(255, 255, 255))
        sc_ = 1.0 + (0.18 * eio((l - [tk for i, tk in hl if i == j][0]) / 0.5) if was else 0)
        if is_act:
            pr = 0.5 + 0.5 * math.sin(t * 5)
            rg = 66 * sc_ + 10 + 8 * pr
            d.ellipse((nx - rg, ny - rg, nx + rg, ny + rg), outline=mix(BGC, RED, aa * (0.5 + 0.5 * pr)), width=3)
        put_scaled(c, node(ic, 124), nx, ny, max(0.05, back((l - t0) / 0.5)) * sc_, aa * (dimk if not was else 1))
        # labels outward (left column right-aligned, right column left-aligned)
        left = dx < 0
        lx = nx - 96 if left else nx + 96
        ly = ny - (34 if len(lines) == 2 else 20)
        tcol = (255, 255, 255) if was else KICK
        yy = ly
        maxw = (lx - 56) if left else (W - 56 - lx)
        for li, s_ in enumerate(lines):
            im = fit_text(s_, "black", 26 if was else 24, maxw, tcol, 1)
            xx = (lx - im.width) if left else lx
            put(c, im, xx, yy, aa * dimk)
            yy += im.height - 2
        # full subtext, wrapped to fit (never truncated)
        sa = aa * dimk * (1 if was or act is None else 0.7)
        sy = yy + 4
        for sl in wrap(sub, "med", 18, maxw):
            sub_im = text(sl, "med", 18, TXT2)
            put(c, sub_im, (lx - sub_im.width) if left else lx, sy, sa)
            sy += 24


CAPS4 = [("AI-POWERED", "DOCUMENTATION", "doc", "AI-Powered", 3), ("AI CLINICAL", "ASSISTANT", "chat", "AI Clinical Assistants", 0), ("PREVENTIVE", "CARE", "heart", "Preventive Care", 1),
         ("REVENUE CYCLE", "INTELLIGENCE", "dollar", "Revenue Cycle", 2)]


def cap_visual(c, j, x, y, l, t, a):
    d = ImageDraw.Draw(c)
    wcol = mix(BGC, (225, 235, 255), a)
    if j == 0:   # chat bubble with typing dots, then reply line
        d.rounded_rectangle((x - 90, y, x + 90, y + 56), 16, outline=wcol, width=3)
        d.polygon([(x - 60, y + 54), (x - 72, y + 74), (x - 40, y + 55)], fill=wcol)
        for q in range(3):
            bump = 6 * max(0, math.sin(t * 6 - q * 0.8))
            d.ellipse((x - 30 + q * 30 - 7, y + 28 - 7 - bump, x - 30 + q * 30 + 7, y + 28 + 7 - bump), fill=mix(BGC, KICK, a))
    elif j == 1:  # ECG line drawing
        pts = []
        for k in range(61):
            u = k / 60
            xx = x - 110 + 220 * u
            ph = (u * 2 + t * 0.8) % 1
            yv = 0
            if 0.40 < ph < 0.44: yv = -14
            elif 0.44 < ph < 0.48: yv = 34
            elif 0.48 < ph < 0.52: yv = -46
            elif 0.52 < ph < 0.56: yv = 10
            pts.append((xx, y + 36 - yv * 0.8))
        d.line(pts, fill=mix(BGC, (255, 110, 110), a), width=4, joint="curve")
    elif j == 2:  # cycle arrows + rising bars
        ang = t * 90
        d.arc((x - 110, y - 2, x - 30, y + 78), ang, ang + 270, fill=wcol, width=4)
        hx = x - 70 + 40 * math.cos(math.radians(ang + 270)); hy = y + 38 + 40 * math.sin(math.radians(ang + 270))
        d.ellipse((hx - 7, hy - 7, hx + 7, hy + 7), fill=mix(BGC, RED, a))
        for q, v in enumerate((0.35, 0.55, 0.8, 1.0)):
            gp = ease((l - 0.3 - q * 0.1) / 0.5)
            d.rectangle((x - 5 + q * 30, y + 76 - 70 * v * gp, x + 15 + q * 30, y + 76), fill=mix(BGC, KICK if q < 3 else RED, a))
    else:        # document lines writing + sparkle
        d.rounded_rectangle((x - 60, y - 8, x + 60, y + 86), 8, outline=wcol, width=3)
        for q in range(5):
            gp = ease((l - 0.3 - q * 0.25) / 0.4)
            wl = (80 if q % 2 == 0 else 60) * gp
            d.line((x - 40, y + 10 + q * 15, x - 40 + wl, y + 10 + q * 15), fill=mix(BGC, KICK, a), width=4)
        s_ = 0.7 + 0.3 * math.sin(t * 4)
        put_scaled(c, icon("spark", 50, (255, 255, 255)), x + 62, y - 6, s_, a)


def caps_phase(c, t, l, a, lock_t):
    xs = [300, 740, 1180, 1610]
    put(c, text("HEALTHCARE CAPABILITIES", "bold", 20, KICK, 6), 120, 230, a * ease(l / 0.5))
    for j, (l1, l2, ic, ph, vid) in enumerate(CAPS4):
        tk = lc(4, 20, ph, lead=0.35) - SC_LOCAL[4]["tL"]
        aa = a * ease((l - tk) / 0.45)
        if aa <= 0:
            continue
        x = xs[j]
        put_scaled(c, node(ic, 150), x, 420, max(0.05, back((l - tk) / 0.55)), aa)
        kin_word(c, l1, x - text(l1, "black", 30, TXT, 1).width / 2, 520, 30, TXT, aa, tk + 0.2, l, "black", 1)
        kin_word(c, l2, x - text(l2, "black", 30, KICK, 1).width / 2, 560, 30, KICK, aa, tk + 0.32, l, "black", 1)
        va = aa * ease((l - tk - 0.55) / 0.5)
        if va > 0:
            cap_visual(c, vid, x, 650, l - tk - 0.55, t, va)


def lockup_phase(c, t, l, a):
    cx = W / 2
    put(c, glow(260, 45), cx - glow(260, 45).width / 2, 430 - glow(260, 45).height / 2, a)
    put_scaled(c, bolt_sphere(230), cx, 400, max(0.05, back(l / 0.7)), a)
    e = text("EAI ", "black", 92, RED, 2); h_ = text("HEALTHCARE", "black", 92, TXT, 2)
    x0 = cx - (e.width + h_.width) / 2
    kin_word(c, "EAI ", x0, 580, 92, RED, a, 0.2, l, "black", 2)
    kin_word(c, "HEALTHCARE", x0 + e.width, 580, 92, TXT, a, 0.3, l, "black", 2)
    tg = text("TRUSTED DATA FOUNDATION  →  COLLABORATIVE AI INTELLIGENCE  →  ACTIONABLE OUTCOMES", "bold", 22, KICK, 3)
    put(c, tg, cx - tg.width / 2, 712, a * ease((l - 0.6) / 0.6))



WHEEL = [  # (title lines, product, icon, start_deg, end_deg)  math angles, counter-clockwise
    (("AI-Ready", "Data"), "Solix CDP", "db", 94, 206),
    (("AI-Ready", "People"), "Solix Academy", "people", 334, 446),
    (("AI-Ready", "Enterprise"), "Solix EAI", "building", 214, 326),
]
SEG_TOP = (252, 230, 230)
SEG_SIDE = (205, 120, 128)
SEG_SIDE2 = (170, 80, 92)


@lru_cache(None)
def people_icon(size):
    ss = 4; S_ = size * ss
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = RED + (255,)
    for cx_, cy_, r_ in ((0.5, 0.36, 0.13), (0.24, 0.42, 0.1), (0.76, 0.42, 0.1)):
        d.ellipse((S_ * (cx_ - r_), S_ * (cy_ - r_), S_ * (cx_ + r_), S_ * (cy_ + r_)), fill=col)
    d.rounded_rectangle((S_ * 0.33, S_ * 0.52, S_ * 0.67, S_ * 0.8), S_ * 0.08, fill=col)
    d.rounded_rectangle((S_ * 0.1, S_ * 0.55, S_ * 0.38, S_ * 0.78), S_ * 0.07, fill=col)
    d.rounded_rectangle((S_ * 0.62, S_ * 0.55, S_ * 0.9, S_ * 0.78), S_ * 0.07, fill=col)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(None)
def building_icon(size):
    ss = 4; S_ = size * ss
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = RED + (255,)
    d.rectangle((S_ * 0.2, S_ * 0.3, S_ * 0.55, S_ * 0.85), fill=col)
    d.rectangle((S_ * 0.55, S_ * 0.15, S_ * 0.82, S_ * 0.85), fill=col)
    for yy in (0.38, 0.5, 0.62, 0.74):
        for xx in (0.26, 0.4):
            d.rectangle((S_ * xx, S_ * yy, S_ * (xx + 0.07), S_ * (yy + 0.06)), fill=(255, 255, 255, 255))
        d.rectangle((S_ * 0.62, S_ * (yy - 0.12), S_ * 0.69, S_ * (yy - 0.06)), fill=(255, 255, 255, 255))
    return im.resize((size, size), Image.LANCZOS)


def wheel_icon(kind, size):
    if kind == "people":
        return people_icon(size)
    if kind == "building":
        return building_icon(size)
    return icon("db", size, RED)


def wheel3d(c, cx, cy, l, t, a, segt=(0.15, 0.37, 0.59)):
    """Extruded 3-segment ring: segments fly in, tilt settles, gentle float."""
    if a <= 0.01:
        return
    R, r, h = 360, 140, 46
    settle = eio((l - 0.2) / max(1.8, segt[2] + 0.6))
    tilt = math.radians(62 - 40 * settle + 2.5 * math.sin(t * 0.8))
    spin = math.radians(-50 * (1 - settle) + 3 * math.sin(t * 0.5))
    ct, st_ = math.cos(tilt), math.sin(tilt)
    # ground shadow
    sh = Image.new("RGBA", (int(2 * R + 200), int(2 * R * ct + 200)), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((100, 100 + 40, 100 + 2 * R, 100 + 2 * R * ct + 40), fill=(0, 0, 12, int(150 * a)))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    put(c, sh, cx - sh.width / 2, cy - sh.height / 2 + h * st_ + 20, 1.0)

    def P(rad, ang, z, off=(0, 0)):
        x = rad * math.cos(ang) + off[0]
        y = rad * math.sin(ang) + off[1]
        return (cx + x, cy - y * ct - z * st_)

    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    segs = []
    for j, (tl, prod, ic, a0, a1) in enumerate(WHEEL):
        p = back((l - segt[j]) / 0.75)
        if p <= 0:
            continue
        mid = math.radians((a0 + a1) / 2) + spin
        pop = 30 * max(0.0, 1 - ease((l - segt[j]) / 0.9)) + 14 * max(0.0, math.sin(t * 1.4 + j * 2.1)) * settle * 0.4
        lift = (1 - min(1.0, p)) * -260
        off = (pop * math.cos(mid), pop * math.sin(mid))
        angs = [math.radians(a0 + (a1 - a0) * k / 40) + spin for k in range(41)]
        segs.append((math.sin(mid), j, angs, off, lift, min(1.0, max(0.0, p)), tl, prod, ic, mid))
    segs.sort(key=lambda s_: -s_[0])  # back (top of screen) first
    for (_, j, angs, off, lift, pp, tl, prod, ic, mid) in segs:
        al = int(255 * pp * a)
        # inner wall (visible on the far side)
        for k in range(len(angs) - 1):
            if math.sin(angs[k]) > 0:
                q = [P(r, angs[k], lift, off), P(r, angs[k + 1], lift, off), P(r, angs[k + 1], lift - h, off), P(r, angs[k], lift - h, off)]
                d.polygon(q, fill=SEG_SIDE2 + (al,))
        # outer wall (front half)
        for k in range(len(angs) - 1):
            if math.sin(angs[k]) < 0.05:
                shade = 0.75 + 0.25 * math.cos(angs[k] + 0.6)
                col = tuple(int(v * shade) for v in SEG_SIDE)
                q = [P(R, angs[k], lift, off), P(R, angs[k + 1], lift, off), P(R, angs[k + 1], lift - h, off), P(R, angs[k], lift - h, off)]
                d.polygon(q, fill=col + (al,))
        # end caps
        for ang in (angs[0], angs[-1]):
            q = [P(r, ang, lift, off), P(R, ang, lift, off), P(R, ang, lift - h, off), P(r, ang, lift - h, off)]
            d.polygon(q, fill=SEG_SIDE2 + (al,))
        # top face
        top = [P(R, an, lift, off) for an in angs] + [P(r, an, lift, off) for an in reversed(angs)]
        d.polygon(top, fill=SEG_TOP + (al,))
        # rim highlight
        d.line([P(R, an, lift, off) for an in angs], fill=(255, 255, 255, int(al * 0.9)), width=2)
    lay = lay.filter(ImageFilter.SMOOTH)
    c.paste(lay, (0, 0), lay)
    # labels on top faces
    for (_, j, angs, off, lift, pp, tl, prod, ic, mid) in segs:
        la = a * ease((l - segt[j] - 0.55) / 0.5)
        if la <= 0:
            continue
        rm = (R + r) / 2 + 12
        lx, ly = P(rm, mid, lift, off)
        icn = wheel_icon(ic, 46)
        t1 = text(tl[0], "bold", 34, INK)
        t2 = text(tl[1], "bold", 34, INK)
        t3 = text(prod, "semi", 24, RED)
        hgt = icn.height + 6 + t1.height + t2.height - 8 + t3.height
        y0 = ly - hgt / 2
        put(c, icn, lx - icn.width / 2, y0, la); y0 += icn.height + 6
        put(c, t1, lx - t1.width / 2, y0, la); y0 += t1.height - 6
        put(c, t2, lx - t2.width / 2, y0, la); y0 += t2.height - 2
        put(c, t3, lx - t3.width / 2, y0, la)
    # centre disc
    ca = a * ease((l - 0.7) / 0.6)
    if ca > 0:
        rr_ = r - 14
        disc = Image.new("RGBA", (int(2 * rr_ + 4), int(2 * rr_ * ct + 4)), (0, 0, 0, 0))
        ImageDraw.Draw(disc).ellipse((2, 2, 2 * rr_ + 2, 2 * rr_ * ct + 2), fill=(255, 255, 255, 255))
        put(c, disc, cx - disc.width / 2, cy - disc.height / 2, ca)
        yy = cy - 46
        for s_ in ("Your AI", "Journey Starts", "Here"):
            im = text(s_, "bold", 26, RED)
            put(c, im, cx - im.width / 2, yy, a * ease((l - 1.0) / 0.5))
            yy += 31


SC_LOCAL = {}





@lru_cache(None)
def firm_img(nm):
    tx = text(nm, "xbold", 44, TXT)
    im = Image.new("RGBA", (560, 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 14, 5, 66), 2, fill=RED + (255,))
    im.alpha_composite(tx, (24, int(40 - tx.height / 2)))
    return im





def scene1(c, t, lt, G):
    k = 1
    t1 = lc(k, 1, "Common Data")
    t2 = lc(k, 1, "Content Services")
    t3 = lc(k, 2, "Enterprise Data Governance")
    pills = [("Common Data Platform", "Structured and unstructured data, together", t1, "db"),
             ("Enterprise Content Services", "Governs documents and email", t2, "doc"),
             ("Enterprise Data Governance", "Enforces policy everywhere, including AI", t3, "shield")]
    act = -1
    for j, p in enumerate(pills):
        if lt >= p[2]:
            act = j
    for j, (ti, sub, tk, ic) in enumerate(pills):
        a = vis(lt, 0.4 + 0.15 * j) * G
        callout(c, 92, 262 + j * 116, j + 1, ti, sub, 540, a, active=(j == act), ico=ic)
        if j == 2 and a > 0:
            bdg = new_badge()
            ba = vis(lt, t3 + 0.2, None, 0.4) * G
            put_scaled(c, bdg, 92 + 540 - bdg.width / 2 - 6, 262 + 2 * 116 - 4, 0.8 + 0.2 * back((lt - t3 - 0.2) / 0.5), ba)
    chips = [("STRUCTURED + UNSTRUCTURED", lc(k, 1, "structured")), ("DOCUMENTS + EMAIL", lc(k, 1, "documents")),
             ("POLICY EVERYWHERE, INCLUDING AI", lc(k, 2, "including AI"))]
    for j, (lab, tk) in enumerate(chips):
        im = text(lab, "bold", 18, KICK if j < 2 else (255, 120, 120), 3)
        put(c, im, 92 + (1 - ease((lt - tk) / 0.5)) * 24, 650 + j * 40, vis(lt, tk, None, 0.5) * G)
    items = [(0.45, "scroll", "cdp"), (t2, "still", "ecs"), (t3, "scroll", "edg")]
    im = card_switch(c, lt, items, 680, 262, 1160, 600, G)
    if lt >= t3 and im is not None:
        bdg = new_badge()
        put_scaled(c, bdg, 680 + im.width - bdg.width / 2 - 24, 262 + 76, 0.8 + 0.2 * back((lt - t3 - 0.5) / 0.5), vis(lt, t3 + 0.5, None, 0.4) * G)


def scene2(c, t, lt, G):
    k = 2
    chain = [("DATA SENSE", lc(k, 4, "Data Sense", lead=0.3)), ("DATA ASK", lc(k, 4, "Data Ask", lead=0.3)),
             ("AI WAREHOUSE", lc(k, 4, "AI Warehouse", lead=0.3)), ("AGENTS", lc(k, 4, "agents", lead=0.3))]
    info = [("Understand", "Application Knowledge Graph", "spark"), ("Answer", "Cited answers in plain English", "chat"),
            ("Build", "Teams build on it", "warehouse"), ("Act", "Agents act with confidence", "agent")]
    tB = chain[0][1] - 0.3
    if lt < tB + 0.6:
        g = G * (1 - eio((lt - tB + 0.1) / 0.6))
        cx, cy = W / 2, 560
        hub_center(c, cx, cy, 170, lt - 0.2, t, vis(lt, 0.2) * g)
        labs = [("Understand", "Data Sense", "spark", -1, -1), ("Answer", "Data Ask", "chat", -1, 1),
                ("Build", "AI Warehouse", "warehouse", 1, -1), ("Act", "Agents", "agent", 1, 1)]
        for j, (lab, sub, ic, sx, sy) in enumerate(labs):
            t0 = 0.4 + 0.2 * j
            aa = vis(lt, t0) * g
            if aa <= 0:
                continue
            ex = cx + sx * 470
            pts = bez((cx + sx * 140, cy + sy * 30), (cx + sx * 280, cy + sy * 30), (cx + sx * 300, cy + sy * 160), (ex, cy + sy * 160))
            connector(c, pts, ease((lt - t0) / 0.7), aa, t + j * 0.25)
            if sx > 0:
                callout(c, ex + 10, cy + sy * 160 - 48, j + 1, lab, sub, 460, aa, ico=ic)
            else:
                callout_r(c, ex - 10, cy + sy * 160 - 48, lab, sub, aa)
    if lt < tB:
        return
    act = 0
    for j, (_, tk) in enumerate(chain):
        if lt >= tk:
            act = j
    x = 92
    for j, (lab, _) in enumerate(chain):
        im = pill_img(lab, j == act, 16, 20, 44, 1, dim=j > act)
        a = vis(lt, tB + 0.1 * j) * G
        put(c, im, x, 236 + (1 - a) * 12, a)
        if j < 3:
            put(c, text("→", "bold", 24, RED if j < act else (200, 170, 170)), x + im.width + 9, 241, a)
            x += im.width + 46
    items = [(tB + 0.15, "still", "datasense"), (chain[1][1], "still", "dataask"), (chain[2][1], "still", "aiwh"), (chain[3][1], "still", "agentic")]
    card_switch(c, lt, items, 92, 318, 1180, 590, G, align="left")
    lab, sub, ic = info[act]
    a = vis(lt, chain[act][1] + 0.25, None, 0.5) * G
    put_scaled(c, node(ic, 150), 1560, 470, max(0.05, back((lt - chain[act][1] - 0.1) / 0.6)), a)
    callout(c, 1330, 600, act + 1, lab, sub, 470, a)


def scene3(c, t, lt, G):
    k = 3
    tEnd = lc(k, 6, lead=0.3)
    labels = ["Application Retirement", "Data Preservation", "SAP", "Oracle", "Mainframe", "Email", "File", "Database", "Active Archiving"]
    phrases = [(5, "retires legacy"), (5, "applications"), (5, "SAP"), (5, "Oracle"), (5, "mainframe"),
               (5, "email"), (5, "file"), (5, "database"), (5, "database")]
    tl_ = [lc(k, i, ph, lead=0.25) for i, ph in phrases]
    tl_[8] += 0.4
    tG1 = min(tl_[0], 0.35)
    x = 92
    for j, lab in enumerate(labels):
        on = lt >= tl_[j]
        im = pill_img(lab.upper(), on and lt < tEnd, 14, 16, 38, 1, dim=not on)
        a = vis(lt, 0.3 + 0.04 * j) * G
        put(c, im, x, 236 + (1 - a) * 10, a)
        x += im.width + 10
    # retire + preserve
    tS = tl_[2] - 0.1
    if tG1 <= lt < tS + 0.5:
        l = lt - tG1
        g = G * (1 - eio((lt - tS) / 0.5))
        for j, (nm, lab, tj) in enumerate([("appret", "APPLICATION RETIREMENT", 0.0), ("datapres", "DATA PRESERVATION", tl_[1] - tG1)]):
            im = still(nm, 840, 520, l - tj, tS - tG1 - tj)
            x0 = 92 + j * 900
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.6)) * 100, 330, a)
            put(c, pill_img(lab, True, 15, 18, 40, 2), x0 + 20, 300 + (1 - a) * 10, a)
    # SAP / Oracle / Mainframe
    tE = tl_[5] - 0.1
    if tS <= lt < tE + 0.5:
        l = lt - tS
        g = G * (1 - eio((lt - tE) / 0.5))
        for j, (nm, lab) in enumerate([("sap", "SAP"), ("oracle", "ORACLE"), ("mainframe", "MAINFRAME")]):
            tj = max(0.0, tl_[2 + j] - tS)
            im = still(nm, 760, 380, l - tj, tE - tS - tj)
            x0, y0 = 92 + j * 300, 330 + j * 120
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.6)) * 120, y0, a)
            put(c, pill_img(lab, True, 16, 20, 42, 2), x0 + 18, y0 - 26, a)
    # Email / File / Database / Active archiving
    if tE <= lt < tEnd + 0.5:
        l = lt - tE
        g = G * (1 - eio((lt - tEnd) / 0.5))
        cells = [("email", "EMAIL"), ("file", "FILE"), ("database", "DATABASE"), ("active", "ACTIVE ARCHIVING")]
        for j, (nm, lab) in enumerate(cells):
            tj = max(0.0, tl_[5 + j] - tE)
            cx0, cy0 = 92 + (j % 2) * 880, 320 + (j // 2) * 316
            im = still(nm, 840, 290, l - tj, tEnd - tE - tj)
            a = vis(l, tj) * g
            draw_card(c, im, cx0 + (840 - im.width) / 2, cy0 + 22 + (1 - ease((l - tj) / 0.6)) * 40, a)
            put(c, pill_img(lab, True, 15, 18, 40, 2), cx0 + 10, cy0 - 2, a)
    # closing statement
    if lt >= tEnd:
        l = lt - tEnd
        a = G * ease(l / 0.5)
        t1 = text("THAT HISTORY BECOMES", "black", 64, TXT, 2)
        put(c, t1, (W - t1.width) / 2, 430 + (1 - ease(l / 0.6)) * 24, a)
        t2 = text("AI-READY,", "black", 84, (255, 255, 255), 2)
        t3 = text("NOT DEAD WEIGHT.", "black", 84, TXT, 2)
        tw = t2.width + 40 + t3.width + 24
        x0 = (W - tw) / 2
        sp = eio((l - 0.4) / 0.5)
        if sp > 0:
            pl = Image.new("RGBA", (t2.width + 40, t2.height + 8), (0, 0, 0, 0))
            ImageDraw.Draw(pl).rounded_rectangle((0, 0, int((t2.width + 40) * sp), t2.height + 7), 14, fill=BLUE + (255,))
            put(c, pl, x0, 528, a)
        put(c, t2, x0 + 20, 532, G * ease((l - 0.6) / 0.4))
        put(c, t3, x0 + t2.width + 64, 532 + (1 - ease((l - 0.8) / 0.5)) * 20, G * ease((l - 0.8) / 0.5))


def scene5(c, t, lt, G):
    k = 5
    draw_card(c, clip("logos", lt * 1.6, 1100, 620, 1.0), 92 + (1 - ease((lt - 0.15) / 0.7)) * 80, 262, vis(lt, 0.15) * G)
    tf = lc(k, 11, "Fortune", lead=0.3)
    a = vis(lt, tf) * G
    if a > 0:
        cnt = int(round(2000 * ease((lt - tf) / 1.2) / 10)) * 10
        put(c, text("FORTUNE", "bold", 22, KICK, 6), 1270, 380 + (1 - a) * 10, a)
        put(c, text(f"{cnt}", "black", 140, TXT), 1258, 410 + (1 - a) * 10, a)
        put(c, text("ENTERPRISES", "bold", 22, TXT2, 4), 1270, 580, a)


def scene6(c, t, lt, G):
    k = 6
    items = [(0.15, "still", "recog")]
    card_switch(c, lt, items, 92, 262, 1100, 590, G)
    firms = [("Gartner", "Gartner"), ("IDC", "I D C"), ("Forrester", "Forrester"), ("Bloor Research", "Bloor")]
    for j, (nm, ph) in enumerate(firms):
        tk = lc(k, 12, ph, lead=0.25)
        a = vis(lt, tk) * G
        if a <= 0:
            continue
        put(c, firm_img(nm), 1250 + (1 - a) * 40, 330 + j * 110, a)


def scene7(c, t, lt, G):
    k = 7
    tg = lc(k, 13, "From governance", lead=0.25)
    tE = lc(k, 14, lead=0.3)
    tAg = lc(k, 14, "The Agentic", lead=0.2)
    SC_LOCAL[7] = {"tE": tE}
    if lt < tE + 0.6:
        g = G * (1 - eio((lt - tE + 0.5) / 0.5))
        grey1 = ease((lt - tg) / 0.6)
        c1 = mix(TXT, (96, 90, 160), grey1)
        c1r = mix(RED, (120, 60, 120), grey1)
        X = 150
        t0 = 0.3
        put(c, text("FROM", "bold", 22, KICK, 4), X + 8, 312, vis(lt, t0) * g)
        put(c, text("DATA", "black", 104, c1), X, 336 + (1 - ease((lt - t0) / 0.7)) * 30, vis(lt, t0) * g)
        tt = lc(k, 13, "to intelligence", lead=0.2)
        put(c, text("TO", "bold", 22, KICK, 4), X + 560, 312, vis(lt, tt) * g)
        put(c, text("INTELLIGENCE", "black", 104, c1r), X + 552, 336 + (1 - ease((lt - tt) / 0.7)) * 30, vis(lt, tt) * g)
        put(c, text("FROM", "bold", 22, KICK, 4), X + 8, 532, vis(lt, tg) * g)
        put(c, text("GOVERNANCE", "black", 104, TXT), X, 556 + (1 - ease((lt - tg) / 0.7)) * 30, vis(lt, tg) * g)
        ta = lc(k, 13, "to action", lead=0.2)
        put(c, text("TO", "bold", 22, KICK, 4), X + 860, 532, vis(lt, ta) * g)
        put(c, text("ACTION", "black", 104, RED), X + 852, 556 + (1 - ease((lt - ta) / 0.7)) * 30, vis(lt, ta) * g)
    if lt >= tE + 0.15:
        l = lt - tE - 0.15
        cx = W / 2
        hub_glow = glow(260, 40)
        put(c, hub_glow, cx - hub_glow.width / 2, 300 - hub_glow.height / 2 + 120, vis(l, 0) * G)
        lw = 700
        put_scaled(c, logo(lw), cx, 230 + (1 - ease(l / 0.8)) * 30, 0.92 + 0.08 * ease(l / 1.2), vis(l, 0, None, 0.8) * G)
        t1 = text("SOLIX EMPOWER 2026", "black", 112, TXT)
        put(c, t1, (W - t1.width) / 2, 345 + (1 - ease((l - 0.3) / 0.7)) * 30, vis(l, 0.3) * G)
        la = tAg - tE
        t2 = text("THE AGENTIC ENTERPRISE", "xbold", 70, RED, 2)
        put(c, t2, (W - t2.width) / 2, 485 + (1 - ease((l - la) / 0.7)) * 30, vis(l, la) * G)
        ln = int(260 * ease((l - la - 0.2) / 0.7))
        if ln > 0:
            ImageDraw.Draw(c).rectangle(((W - ln) // 2, 592, (W + ln) // 2, 595), fill=RED)
        t3 = text("Where Data, AI and Industry Come Together.", "med", 36, TXT2)
        put(c, t3, (W - t3.width) / 2, 624, vis(l, la + 0.6) * G)


def academy_phase(c, t, l, a):
    """Solix Academy: 3D AI-journey wheel straight away (no title, no learning path)."""
    tA = SC_LOCAL[4]["tA"]
    segt = [0.35, max(0.9, lc(4, 10, "organizations", lead=0.35) - tA), lc(4, 10, "AI-ready", lead=0.35) - tA]
    wheel3d(c, 900, 540, l, t, a * ease(l / 0.4), segt)
    items = [("AI-READY DATA", "Solix CDP"), ("AI-READY PEOPLE", "Solix Academy"), ("AI-READY ENTERPRISE", "Solix EAI")]
    for j, (t1_, t2_) in enumerate(items):
        ia = a * ease((l - segt[j] - 0.2) / 0.5)
        if ia <= 0:
            continue
        y_ = 360 + j * 130
        ImageDraw.Draw(c).rectangle((1450, y_ + 4, 1455, y_ + 82), fill=mix(BGC, RED, ia))
        put(c, text(t1_, "black", 30, TXT, 1), 1474 + (1 - ia) * 24, y_, ia)
        put(c, text(t2_, "semi", 24, KICK), 1476 + (1 - ia) * 24, y_ + 44, ia)


def scene4(c, t, lt, G):
    k = 4
    tF = lc(k, 8, lead=0.55)
    tC = lc(k, 9, lead=0.5)
    tLock = lc(k, 10, lead=0.5)
    SC_LOCAL[4] = {"tF": tF, "tC": tC, "tL": tLock, "tA": tLock + 0.2}
    if lt < tF + 0.5:
        pharma_phase(c, t, lt, G * phase_alpha(lt, 0.0, tF, 0.4, 0.5))
    if tF <= lt < tC + 0.5:
        foundation_phase(c, t, lt - tF, G * phase_alpha(lt, tF, tC, 0.3, 0.5))
    if tC <= lt < tLock + 0.5:
        platform_phase(c, t, lt - tC, G * phase_alpha(lt, tC, tLock, 0.3, 0.5))
    if lt >= tLock + 0.2:
        academy_phase(c, t, lt - tLock - 0.2, G * ease((lt - tLock - 0.2) / 0.5))


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7]
MODE = os.environ.get("MODE", "plain")   # plain | alpha


def scenes_on(c, t):
    for k, s in enumerate(SC):
        if s["start"] <= t < s["end"]:
            SCENES[k](c, t, t - s["start"], 1.0)
    return c


def plain_bg(t):
    bg = background()
    ox = 130 + 120 * math.sin(t / 10.0)
    oy = 90 + 80 * math.cos(t / 12.0)
    return bg.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))


def frame_plain(t):
    return scenes_on(plain_bg(t), t)


def frame_rgba(t):
    """Difference matte: render the graphics over black and over white, solve for colour + alpha."""
    b = np.asarray(scenes_on(Image.new("RGB", (W, H), (0, 0, 0)), t), np.float32)
    w = np.asarray(scenes_on(Image.new("RGB", (W, H), (255, 255, 255)), t), np.float32)
    al = np.clip(1.0 - (w - b).mean(axis=2) / 255.0, 0.0, 1.0)
    rgb = np.where(al[..., None] > 1e-3, b / np.maximum(al[..., None], 1e-3), 0.0)
    out = np.dstack([np.clip(rgb, 0, 255), al * 255]).round().astype(np.uint8)
    return out


def frame(t):
    return frame_plain(t)


def render_clip(args):
    name, t0, t1, outdir = args
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/{name}"
    if MODE == "alpha":
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", out + ".mov"]
    else:
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "13", "-tune", "animation", "-pix_fmt", "yuv420p", out + ".mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        im = frame_rgba(f / FPS) if MODE == "alpha" else np.asarray(frame_plain(f / FPS))
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return name


def write_srt(name, t0, t1, outdir):
    def ts(x):
        x = max(0.0, x); h = int(x // 3600); m = int(x % 3600 // 60); s_ = x % 60
        return f"{h:02d}:{m:02d}:{int(s_):02d},{int(round((s_ % 1) * 1000)):03d}".replace(",1000", ",999")
    n = 0; out = []
    for (a, b, txt, i, first) in CAPS:
        if a >= t0 - 0.01 and a < t1:
            n += 1
            out.append(f"{n}\n{ts(a - t0)} --> {ts(min(b, t1) - t0)}\n{txt}\n")
    open(f"{outdir}/{name}.srt", "w").write("\n".join(out))


def part_specs():
    s4 = SC[4]["start"]
    tF = lc(4, 8, lead=0.55); tC = lc(4, 9, lead=0.5); tLock = lc(4, 10, lead=0.5)
    s7 = SC[7]["start"]
    tE = lc(7, 14, lead=0.3)
    return [("02_Foundation", 0.0, SC[2]["start"]),
            ("03_Enterprise_AI", SC[2]["start"], SC[3]["start"]),
            ("04_Data_Lifecycle", SC[3]["start"], SC[4]["start"]),
            ("05a_EAI_Pharma", s4, s4 + tF + 0.25),
            ("05b_EAI_Healthcare_Foundation", s4 + tF + 0.25, s4 + tC + 0.25),
            ("05c_EAI_Healthcare_Platform", s4 + tC + 0.25, s4 + tLock + 0.35),
            ("05d_Solix_Academy", s4 + tLock + 0.35, SC[5]["start"]),
            ("06_Customers_Recognition", SC[5]["start"], SC[7]["start"]),
            ("07a_Close_Statement", s7, s7 + tE + 0.1),
            ("07b_End_Lockup", s7 + tE + 0.1, TOTAL)]


def dump_timeline():
    segs = [{"i": k, "start": SC[k]["start"], "end": SC[k]["end"]} for k in range(8)]
    json.dump({"total": TOTAL, "segs": segs, "lines": [{"start": L["start"], "dur": L["dur"]} for L in LINES],
               "parts": part_specs()}, open(f"{B}/timeline_90.json", "w"), indent=1)


if __name__ == "__main__":
    mode = sys.argv[1]
    dump_timeline()
    if mode == "info":
        print("total", round(TOTAL, 2)); [print(k, round(s["start"], 2), round(s["end"], 2)) for k, s in enumerate(SC)]
        for p in part_specs():
            print(p[0], round(p[1], 3), round(p[2], 3), round(p[2] - p[1], 2))
    elif mode == "still":
        for ts in sys.argv[2:]:
            if MODE == "alpha":
                Image.fromarray(frame_rgba(float(ts)), "RGBA").save(f"{B}/a14_{ts}.png")
            else:
                frame_plain(float(ts)).save(f"{B}/s14_{ts}.jpg", quality=90)
    elif mode == "parts":
        from multiprocessing import Pool
        outdir = sys.argv[2]
        nw = int(sys.argv[3]) if len(sys.argv) > 3 else 4
        only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
        os.makedirs(outdir, exist_ok=True)
        specs = [p for p in part_specs() if only is None or p[0] in only]
        for nm, a, b in specs:
            write_srt(nm, a, b, outdir)
        ext = ".mov" if MODE == "alpha" else ".mp4"
        chunks = []
        for nm, a, b in specs:
            nf = int(round(b * FPS)) - int(round(a * FPS))
            n = max(1, nf // 120)
            fa = int(round(a * FPS))
            for q in range(n):
                f0 = fa + nf * q // n; f1 = fa + nf * (q + 1) // n
                chunks.append((f"{nm}__{q:02d}", f0 / FPS, f1 / FPS, outdir + "/_chunks"))
        with Pool(nw) as pool:
            for r_ in pool.imap_unordered(render_clip, chunks):
                pass
        for nm, a, b in specs:
            nf = int(round(b * FPS)) - int(round(a * FPS))
            n = max(1, nf // 120)
            lst = f"{outdir}/_chunks/{nm}.txt"
            with open(lst, "w") as f:
                for q in range(n):
                    f.write(f"file '{outdir}/_chunks/{nm}__{q:02d}{ext}'\n")
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                            f"{outdir}/{nm}{ext}"], check=True)
            print("PART", nm, round(a, 3), round(b, 3), flush=True)
