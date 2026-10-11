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
LINES = json.load(open(f"{B}/lines3.json"))
FIRST = 3.0       # first VO line start (intro motion before it)
SCENE_PAD = 0.7   # extra air at scene changes
PRE = 0.75        # scene starts this long before its first line
TAIL = 4.5
t = FIRST
for i, L in enumerate(LINES):
    if i and L["scene"] != LINES[i - 1]["scene"]:
        t += SCENE_PAD
    L["start"] = t
    L["dur"] = sf.info(f"{B}/vo3/{i:02d}.wav").duration
    t += L["dur"] + L["gap"]
TOTAL = LINES[-1]["start"] + LINES[-1]["dur"] + TAIL
SC = []
for k in range(8):
    idx = [i for i, L in enumerate(LINES) if L["scene"] == k]
    SC.append({"lines": idx, "start": 0.0 if k == 0 else LINES[idx[0]]["start"] - PRE})
for k in range(8):
    SC[k]["end"] = SC[k + 1]["start"] if k < 7 else TOTAL


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
ORBS = [(1870, 560, 150, (40, 70, 160), 0.0), (50, 760, 110, (120, 30, 60), 2.0), (1000, 1075, 70, (30, 90, 170), 4.0)]


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
    """Pure motion graphics intro."""
    cx, cy = W / 2, 450
    l0 = cue(0)
    tA_out = cue(1) - 0.6
    rr = random.Random(5)
    n = 64
    conv = ease((lt - 0.2) / 2.2)
    aA = vis(lt, 0.0, tA_out, 0.6, 0.6) * G
    if aA > 0:
        d = ImageDraw.Draw(c)
        pts = []
        for k in range(n):
            sx, sy = rr.uniform(-200, W + 200), rr.uniform(-200, H + 200)
            ang = 2 * math.pi * k / n + lt * 0.08
            rad = 330 + 90 * math.sin(k * 1.7)
            tx_, ty_ = cx + rad * math.cos(ang), cy + rad * 0.62 * math.sin(ang)
            pts.append((sx + (tx_ - sx) * conv, sy + (ty_ - sy) * conv))
        for k in range(n):
            x, y = pts[k]
            x2, y2 = pts[(k + 1) % n]
            d.line((x, y, x2, y2), fill=mix(BGC, (90, 170, 230), 0.6 * aA), width=1)
            if k % 3 == 0:
                d.line((x, y, cx, cy), fill=mix(BGC, (70, 130, 210), 0.35 * aA * conv), width=1)
        for (x, y) in pts:
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=mix(BGC, RED, 0.8 * aA))
        la = vis(lt, 1.6, tA_out, 0.8, 0.5) * G
        put_scaled(c, logo(900), cx, cy, 0.86 + 0.14 * ease((lt - 1.6) / 1.4), la)
        wk = text("SOLIX TECHNOLOGIES", "bold", 22, KICK, 6)
        put(c, wk, cx - wk.width / 2, cy + 172 + (1 - ease((lt - l0 + 0.4) / 0.6)) * 16, vis(lt, l0 - 0.4, tA_out, 0.6, 0.5) * G)
        # "What AI needs most: its own data."
        t1 = text("What AI needs most:", "xbold", 54, TXT)
        t2 = text("its own data.", "xbold", 54, (255, 255, 255))
        tw = t1.width + 18 + t2.width + 28
        x0 = cx - tw / 2
        yy = cy + 214
        ta = cue(0, "what AI") - 0.15
        put(c, t1, x0, yy + (1 - ease((lt - ta) / 0.6)) * 20, vis(lt, ta, tA_out, 0.6, 0.5) * G)
        tk = cue(0, "its own") - 0.2
        sp = eio((lt - tk) / 0.5)
        if sp > 0:
            pl = Image.new("RGBA", (t2.width + 28, t2.height + 4), (0, 0, 0, 0))
            ImageDraw.Draw(pl).rounded_rectangle((0, 0, int((t2.width + 28) * sp), t2.height + 3), 12, fill=BLUE + (255,))
            put(c, pl, x0 + t1.width + 18, yy - 2, G * (1 - eio((lt - tA_out) / 0.5)))
        put(c, t2, x0 + t1.width + 32, yy, vis(lt, tk + 0.25, tA_out, 0.4, 0.5) * G)
    # B) 20+ years of enterprise data (line 1)
    tB = cue(1) - 0.3
    tB_out = cue(1, "preserve it") - 0.6
    if tB - 0.1 <= lt < tB_out + 0.6:
        l = lt - tB
        a = vis(l, 0, tB_out - tB, 0.7, 0.5) * G
        put(c, text("SOLIX TECHNOLOGIES", "bold", 20, KICK, 5), 150 - (1 - ease(l / 0.6)) * 40, 300, a)
        cnt = int(round(20 * ease(l / 1.6)))
        put(c, text(f"{cnt}+", "black", 280, RED), 136, 330 + (1 - ease(l / 0.6)) * 40, a)
        put(c, text("YEARS OF", "xbold", 60, TXT), 150, 660 + (1 - ease((l - 0.3) / 0.6)) * 30, vis(l, 0.3, tB_out - tB) * G)
        put(c, text("ENTERPRISE DATA", "xbold", 60, TXT), 150, 732 + (1 - ease((l - 0.45) / 0.6)) * 30, vis(l, 0.45, tB_out - tB) * G)
        bx, by, bw, bh = 1030, 300, 760, 520
        pa = vis(l, 0.4, tB_out - tB) * G
        if pa > 0:
            sh, pad = shadow(bw, bh)
            put(c, sh, bx - pad, by - pad, pa); put(c, box(bw, bh, 18), bx, by, pa)
            d = ImageDraw.Draw(c)
            put(c, text("ENTERPRISE DATA, PUT TO WORK", "bold", 16, GREY, 3), bx + 40, by + 36, pa)
            vals = [0.18, 0.26, 0.31, 0.42, 0.5, 0.63, 0.74, 0.9]
            base_y = by + bh - 70
            pts = []
            for k, v in enumerate(vals):
                gp = ease((l - 0.7 - k * 0.12) / 0.7)
                x0 = bx + 60 + k * 82
                d.rounded_rectangle((x0, base_y - v * 330 * gp, x0 + 50, base_y), 6, fill=mix((250, 225, 225), mix((246, 170, 170), RED, k / 7), pa))
                pts.append((x0 + 25, base_y - v * 330 - 26))
            tp = ease((l - 1.6) / 1.6)
            if tp > 0:
                m = max(2, int(len(pts) * tp))
                dd = []
                for k in range(m - 1):
                    dd += bez(pts[k], (pts[k][0] + 30, pts[k][1]), (pts[k + 1][0] - 30, pts[k + 1][1]), pts[k + 1], 10)
                d.line(dd, fill=mix((250, 225, 225), INK, pa), width=4)
                hx, hy = dd[-1]
                d.ellipse((hx - 9, hy - 9, hx + 9, hy + 9), fill=mix((250, 225, 225), RED, pa))
            d.line((bx + 50, base_y + 2, bx + bw - 50, base_y + 2), fill=mix((255, 255, 255), (220, 210, 212), pa), width=2)
    # C) preserve it, govern it, put it to work
    tC = cue(1, "preserve it") - 0.5
    if lt >= tC - 0.1:
        l = lt - tC
        a = vis(l, 0, None, 0.7) * G
        k_ = text("YOUR DATA, PUT TO WORK", "bold", 20, KICK, 5)
        put(c, k_, cx - k_.width / 2, 150, a)
        hx, hy = cx, 560
        hub_center(c, hx, hy, 150, l, t, a, "YOUR OWN DATA")
        items = [("Preserve it", "db", "preserve it", (-560, -40)), ("Govern it", "shield", "govern it", (0, -300)), ("Put it to work", "spark", "put it to work", (560, -40))]
        for lab, ic, ph, (dx, dy) in items:
            tk = cue(1, ph) - tC - 0.35
            p = ease((l - tk) / 0.8)
            aa = vis(l, tk, None, 0.5) * G
            if aa <= 0:
                continue
            nx, ny = hx + dx, hy + dy
            if dx == 0:
                pts = [(hx, hy - 120 - u * (300 - 200) / 20) for u in range(21)]
            else:
                sgn = 1 if dx > 0 else -1
                pts = bez((hx + sgn * 120, hy - 10), (hx + sgn * 260, hy - 20), (nx - sgn * 220, ny), (nx - sgn * 80, ny))
            connector(c, pts, p, aa, t + dx * 0.001)
            put_scaled(c, node(ic, 130), nx, ny, max(0.05, back((l - tk) / 0.6)), aa)
            tl_ = text(lab.upper(), "bold", 22, TXT, 3)
            put(c, tl_, nx + (90 if dx == 0 else -tl_.width / 2), ny + (-14 if dx == 0 else 82), aa)


@lru_cache(None)
def new_badge():
    tx = text("NEW AT EMPOWER", "black", 15, (255, 255, 255), 2)
    im = Image.new("RGBA", (tx.width + 30, 32), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, tx.width + 29, 31), 16, fill=RED + (255,))
    im.alpha_composite(tx, (15, 6))
    return im


def scene1(c, t, lt, G):
    k = 1
    heading(c, lt, "SOLIX ENTERPRISE FOUNDATION", "Step One: AI-Ready", G)
    t1 = lc(k, 3, "Common Data")
    t2 = lc(k, 4, "Enterprise Content")
    t3 = lc(k, 5, "Enterprise Data Governance")
    pills = [("Common Data Platform", "One catalog · One security model", t1, "db"),
             ("Enterprise Content Services", "Governs your documents and email", t2, "doc"),
             ("Enterprise Data Governance", "Enforces policy wherever data is used", t3, "shield")]
    act = -1
    for j, p in enumerate(pills):
        if lt >= p[2]:
            act = j
    for j, (ti, sub, tk, ic) in enumerate(pills):
        a = vis(lt, 0.6 + 0.18 * j) * G
        callout(c, 92, 262 + j * 116, j + 1, ti, sub, 540, a, active=(j == act), ico=ic)
        if j == 2 and a > 0:
            bdg = new_badge()
            ba = vis(lt, t3 + 0.2, None, 0.4) * G
            put_scaled(c, bdg, 92 + 540 - bdg.width / 2 - 6, 262 + 2 * 116 - 4, 0.8 + 0.2 * back((lt - t3 - 0.2) / 0.5), ba)
    chips = [("STRUCTURED + UNSTRUCTURED", lc(k, 3, "structured")), ("ONE CATALOG", lc(k, 3, "one catalog")),
             ("ONE SECURITY MODEL", lc(k, 3, "security model")), ("INCLUDING BY AI", lc(k, 5, "including by AI"))]
    y = 650
    for j, (lab, tk) in enumerate(chips):
        im = text(lab, "bold", 18, KICK if j < 3 else (255, 120, 120), 3)
        put(c, im, 92 + (1 - ease((lt - tk) / 0.5)) * 24, y + j * 40, vis(lt, tk, None, 0.5) * G)
    items = [(0.7, "scroll", "cdp"), (t2, "still", "ecs"), (t3, "scroll", "edg")]
    im = card_switch(c, lt, items, 680, 262, 1160, 600, G)
    if lt >= t3 and im is not None:
        bdg = new_badge()
        ba = vis(lt, t3 + 0.5, None, 0.4) * G
        put_scaled(c, bdg, 680 + im.width - bdg.width / 2 - 24, 262 + 76, 0.8 + 0.2 * back((lt - t3 - 0.5) / 0.5), ba)


def scene2(c, t, lt, G):
    k = 2
    heading(c, lt, "STEP TWO: AI-ACTIVATED", "Solix Enterprise AI", G)
    chain = [("DATA SENSE", lc(k, 7, "Data Sense", lead=0.3)), ("DATA ASK", lc(k, 8, "Data Ask", lead=0.3)),
             ("AI WAREHOUSE", lc(k, 9, "AI Warehouse", lead=0.3)), ("AGENTS", lc(k, 10, "agents", lead=0.3))]
    info = [("Understand", "Application Knowledge Graph", "spark"), ("Answer", "Cited answers in plain English", "chat"),
            ("Build", "Your teams build on it", "warehouse"), ("Act", "Agents act with confidence", "agent")]
    tB = chain[0][1] - 0.3
    if lt < tB + 0.6:
        g = G * (1 - eio((lt - tB + 0.1) / 0.6))
        cx, cy = W / 2, 560
        hub_center(c, cx, cy, 170, lt - 0.5, t, vis(lt, 0.5) * g)
        labs = [("Understand", "Data Sense", "spark", -1, -1), ("Answer", "Data Ask", "chat", -1, 1),
                ("Build", "AI Warehouse", "warehouse", 1, -1), ("Act", "Agents", "agent", 1, 1)]
        for j, (lab, sub, ic, sx, sy) in enumerate(labs):
            t0 = 0.9 + 0.35 * j
            aa = vis(lt, t0) * g
            if aa <= 0:
                continue
            ex = cx + sx * 470
            pts = bez((cx + sx * 140, cy + sy * 30), (cx + sx * 280, cy + sy * 30), (cx + sx * 300, cy + sy * 160), (ex, cy + sy * 160))
            connector(c, pts, ease((lt - t0) / 0.8), aa, t + j * 0.25)
            callout(c, ex + 10 if sx > 0 else ex - 470, cy + sy * 160 - 48, j + 1, lab, sub, 460, aa, ico=ic)
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
    items = [(tB + 0.15, "still", "datasense"),
             (lc(k, 7, "Application Knowledge", lead=0.3), "scroll", "akg"),
             (chain[1][1], "still", "dataask"), (chain[2][1], "still", "aiwh"), (chain[3][1], "still", "agentic")]
    card_switch(c, lt, items, 92, 318, 1180, 590, G, align="left")
    lab, sub, ic = info[act]
    a = vis(lt, chain[act][1] + 0.25, None, 0.5) * G
    put_scaled(c, node(ic, 150), 1560, 470, max(0.05, back((lt - chain[act][1] - 0.1) / 0.6)), a)
    callout(c, 1330, 600, act + 1, lab, sub, 470, a)


def scene3(c, t, lt, G):
    k = 3
    heading(c, lt, "DATA LIFECYCLE & ARCHIVING", "Move It Once. Access It Always.", G)
    tIntro, tG1, tG2, tG3, tBen, tAI = [cue(i) - SC[3]["start"] - 0.35 for i in SC[3]["lines"]]
    labels = ["Application Retirement", "Data Preservation", "SAP", "Oracle", "Mainframe", "Email", "File", "Database", "Active Archiving"]
    phrases = [(12, "Retiring legacy"), (12, "preserving records"), (13, "SAP"), (13, "Oracle"), (13, "mainframe"),
               (14, "email"), (14, "file"), (14, "database"), (14, "database")]
    tl_ = [lc(k, i, ph, lead=0.25) for i, ph in phrases]
    tl_[8] += 0.6
    x = 92
    for j, lab in enumerate(labels):
        on = lt >= tl_[j]
        im = pill_img(lab.upper(), on and lt < tBen, 14, 16, 38, 1, dim=not on)
        a = vis(lt, 0.8 + 0.05 * j) * G
        put(c, im, x, 236 + (1 - a) * 10, a)
        x += im.width + 10
    if lt < tG1 + 0.6:
        g = G * (1 - eio((lt - tG1) / 0.6))
        cx, cy = W / 2, 590
        a = vis(lt, 0.6) * g
        hub_center(c, cx, cy, 150, lt - 0.6, t, a)
        stages = [("RETIRE", "cycle"), ("PRESERVE", "shield"), ("ARCHIVE", "db"), ("ACTIVATE", "spark")]
        R = 300
        for j, (lab, ic) in enumerate(stages):
            t0 = 1.0 + 0.35 * j
            aa = vis(lt, t0) * g
            if aa <= 0:
                continue
            ang = -math.pi / 2 + j * math.pi / 2 + 0.25
            d = ImageDraw.Draw(c)
            a0 = math.degrees(ang) + 14
            d.arc((cx - R * 1.35, cy - R * 0.78, cx + R * 1.35, cy + R * 0.78), a0, a0 + 62 * ease((lt - t0) / 0.8), fill=mix(BGC, RED, aa), width=4)
            nx, ny = cx + R * 1.35 * math.cos(ang), cy + R * 0.78 * math.sin(ang)
            put_scaled(c, node(ic, 110), nx, ny, max(0.05, back((lt - t0) / 0.6)), aa)
            tlab = text(lab, "bold", 20, TXT, 3)
            put(c, tlab, nx - tlab.width / 2, ny + 66, aa)
    if tG1 <= lt < tG2 + 0.7:
        l = lt - tG1
        g = G * (1 - eio((lt - tG2) / 0.7))
        for j, (nm, lab, tj) in enumerate([("appret", "APPLICATION RETIREMENT", 0.0), ("datapres", "DATA PRESERVATION", tl_[1] - tG1)]):
            im = still(nm, 840, 520, l - tj, tG2 - tG1 - tj)
            x0 = 92 + j * 900
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.7)) * 100, 330, a)
            put(c, pill_img(lab, True, 15, 18, 40, 2), x0 + 20, 300 + (1 - a) * 10, a)
    if tG2 <= lt < tG3 + 0.7:
        l = lt - tG2
        g = G * (1 - eio((lt - tG3) / 0.7))
        for j, (nm, lab) in enumerate([("sap", "SAP"), ("oracle", "ORACLE"), ("mainframe", "MAINFRAME")]):
            tj = max(0.0, tl_[2 + j] - tG2)
            im = still(nm, 760, 380, l - tj, tG3 - tG2 - tj)
            x0, y0 = 92 + j * 300, 330 + j * 120
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.7)) * 120, y0, a)
            put(c, pill_img(lab, True, 16, 20, 42, 2), x0 + 18, y0 - 26, a)
        callout(c, 1300, 360, 1, "Enterprise applications", "SAP · Oracle E-Business Suite", 520, vis(l, 0.5) * g, ico="db")
        callout(c, 1300, 476, 2, "Mainframe", "Retire with confidence", 520, vis(l, tl_[4] - tG2 + 0.2) * g, ico="chip")
    if tG3 <= lt < tBen + 0.7:
        l = lt - tG3
        g = G * (1 - eio((lt - tBen) / 0.7))
        cells = [("email", "EMAIL"), ("file", "FILE"), ("database", "DATABASE"), ("active", "ACTIVE ARCHIVING")]
        for j, (nm, lab) in enumerate(cells):
            tj = max(0.0, tl_[5 + j] - tG3)
            cx0, cy0 = 92 + (j % 2) * 880, 320 + (j // 2) * 316
            im = still(nm, 840, 290, l - tj, tBen - tG3 - tj)
            a = vis(l, tj) * g
            draw_card(c, im, cx0 + (840 - im.width) / 2, cy0 + 22 + (1 - ease((l - tj) / 0.7)) * 40, a)
            put(c, pill_img(lab, True, 15, 18, 40, 2), cx0 + 10, cy0 - 2, a)
    if lt >= tBen:
        l = lt - tBen
        a = vis(l, 0) * G
        bx, by, bw, bh = 92, 320, 900, 560
        sh, pad = shadow(bw, bh)
        put(c, sh, bx - pad, by - pad, a); put(c, box(bw, bh, 18), bx, by, a)
        put(c, text("COST OF RUNNING THE OLD SYSTEM", "bold", 16, GREY, 3), bx + 44, by + 38, a)
        d = ImageDraw.Draw(c)
        base_y = by + bh - 80
        before = [0.82, 0.86, 0.9, 0.94]
        tcut = lc(k, 15, "Cut the cost") - tBen
        for j in range(8):
            v0 = before[j] if j < 4 else before[3]
            target = v0 if j < 4 else [0.62, 0.45, 0.34, 0.28][j - 4]
            gp = ease((l - 0.3 - 0.08 * j) / 0.6)
            dv = ease((l - tcut - 0.12 * (j - 4)) / 0.9) if j >= 4 else 0
            v = (v0 + (target - v0) * dv) * gp
            x0 = bx + 70 + j * 100
            col = mix((255, 255, 255), (232, 222, 224) if j < 4 else mix(RED, (246, 160, 160), (j - 4) / 4), a)
            d.rounded_rectangle((x0, base_y - v * 340, x0 + 60, base_y), 8, fill=col)
        put(c, text("BEFORE", "bold", 15, GREY, 3), bx + 210, base_y + 20, a)
        put(c, text("WITH SOLIX", "bold", 15, RED, 3), bx + 600, base_y + 20, a)
        put_scaled(c, node("dollar", 110), bx + bw - 110, by + 110, max(0.05, back((l - 0.3) / 0.6)), a)
        bens = [("Shut down the old system", "Retire legacy applications", "Shut down", "cycle"),
                ("Cut the cost", "Infrastructure and licenses", "Cut the cost", "dollar"),
                ("Keep the history", "Records stay accessible", "Keep the history", "db")]
        for j, (ti, sub, ph, ic) in enumerate(bens):
            tk = lc(k, 15, ph) - tBen
            callout(c, 1060, 330 + j * 124, j + 1, ti, sub, 600, vis(l, max(0.2, tk)) * G, ico=ic)
        tn = lc(k, 16, "AI-ready") - tBen
        pa = vis(l, tn) * G
        if pa > 0:
            put(c, text("ON THE COMMON DATA PLATFORM", "bold", 15, KICK, 3), 1066, 712, pa)
            im = pill_img("AI-READY, NOT DEAD WEIGHT", True, 18, 28, 54, 3)
            put_scaled(c, im, 1060 + 300, 772, 0.85 + 0.15 * back((l - tn) / 0.6), pa)


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


def scene4(c, t, lt, G):
    k = 4
    heading(c, lt, "INDUSTRY SOLUTIONS", "Enterprise AI, Built for Industry", G)
    tP = lc(k, 18, lead=0.35)
    tH = lc(k, 19, lead=0.35)
    tabs = ["SOLIX EAI PHARMA", "SOLIX AI HEALTHCARE PLATFORM"]
    act = -1 if lt < tP else (0 if lt < tH else 1)
    x = 92
    for j, lab in enumerate(tabs):
        im = pill_img(lab, j == act, 17, 24, 46, 2)
        put(c, im, x, 238, vis(lt, 0.7 + 0.12 * j) * G)
        x += im.width + 14
    if lt < tP + 0.6:
        g = G * (1 - eio((lt - tP) / 0.6))
        for j, (ic, lab) in enumerate([("flask", "PHARMA"), ("heart", "HEALTHCARE")]):
            t0 = 0.8 + 0.3 * j
            aa = vis(lt, t0) * g
            nx = W / 2 + (j - 0.5) * 560
            put_scaled(c, node(ic, 200), nx, 560, max(0.05, back((lt - t0) / 0.6)), aa)
            tl_ = text(lab, "black", 30, TXT, 4)
            put(c, tl_, nx - tl_.width / 2, 690, aa)
        hub_center(c, W / 2, 560, 90, lt - 0.6, t, vis(lt, 0.6) * g)
        for j, sx in enumerate((-1, 1)):
            pts = [(W / 2 + sx * (80 + u * 100 / 20), 560) for u in range(21)]
            connector(c, pts, ease((lt - 1.2) / 0.6), vis(lt, 1.2) * g, t + j * 0.4)
    if tP <= lt < tH + 0.7:
        l = lt - tP
        g = G * (1 - eio((lt - tH) / 0.7))
        draw_card(c, clip("pharma", l, 1080, 580, 0.9), 92 + (1 - ease(l / 0.8)) * 100, 310, vis(l, 0) * g)
        callout(c, 1240, 350, 1, "Solix EAI Pharma", "Built on the same foundation", 590, vis(l, 0.4) * g, ico="flask")
        tpc = lc(k, 18, "preclinical", lead=0.3) - tP
        callout(c, 1240, 470, 2, "Preclinical drug discovery", "Compressed from years to months", 590, vis(l, tpc) * g, ico="spark")
        ty = lc(k, 18, "from years", lead=0.2) - tP
        pa = vis(l, ty) * g
        if pa > 0:
            im = pill_img("YEARS  →  MONTHS", True, 22, 34, 60, 4)
            put_scaled(c, im, 1240 + 295, 640, 0.85 + 0.15 * back((l - ty) / 0.6), pa)
    if lt >= tH:
        l = lt - tH
        im = still("eaihc", 960, 560, l, SC[4]["end"] - SC[4]["start"] - tH)
        draw_card(c, im, 92 + (1 - ease(l / 0.8)) * 100, 320, vis(l, 0) * G)
        patient360(c, 1510, 540, l - 0.4, t, vis(l, 0.4) * G)
        th = lc(k, 20, lead=0.3) - tH
        pa = vis(l, th) * G
        if pa > 0:
            pi_ = pill_img("HIPAA-COMPLIANT  ·  AI-READY FROM DAY ONE", True, 16, 22, 46, 2)
            put(c, pi_, 1500 - pi_.width / 2, 850 + (1 - pa) * 14, pa)


def scene5(c, t, lt, G):
    k = 5
    heading(c, lt, "TRUSTED BY GLOBAL ENTERPRISES", "Solving Complex Data Challenges at Enterprise Scale", G, size=54)
    dur = SC[5]["end"] - SC[5]["start"]
    draw_card(c, clip("logos", lt - 0.6, 1100, 620, min(1.0, 474 / max(1, (dur - 0.6) * FPS))), 92 + (1 - ease((lt - 0.6) / 0.8)) * 80, 262, vis(lt, 0.6) * G)
    # Fortune 2000 counter
    tf = lc(k, 21, "Fortune", lead=0.3)
    a = vis(lt, tf) * G
    if a > 0:
        cnt = int(round(2000 * ease((lt - tf) / 1.4) / 10)) * 10
        put(c, text("FORTUNE", "bold", 18, KICK, 5), 1260, 262 + (1 - a) * 10, a)
        put(c, text(f"{cnt:,}".replace(",", ""), "black", 96, TXT), 1252, 284 + (1 - a) * 10, a)
        put(c, text("ORGANIZATIONS INCLUDED", "bold", 14, TXT2, 3), 1260, 396, a)
    chips = [("Healthcare", "healthcare", "heart"), ("Pharma", "pharma", "flask"), ("Financial Services", "financial", "bank"), ("Manufacturing", "manufacturing", "factory"), ("Technology", "technology", "chip")]
    for j, (lab, ph, ic) in enumerate(chips):
        tk = lc(k, 22, ph, lead=0.25)
        callout(c, 1260, 440 + j * 86, j + 1, lab, None, 560, vis(lt, tk) * G, ico=ic)


@lru_cache(None)
def firm_img(nm):
    tx = text(nm, "xbold", 44, TXT)
    im = Image.new("RGBA", (560, 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 14, 5, 66), 2, fill=RED + (255,))
    im.alpha_composite(tx, (24, int(40 - tx.height / 2)))
    return im


def scene6(c, t, lt, G):
    k = 6
    heading(c, lt, "RECOGNIZED BY INDUSTRY EXPERTS", "Recognized by Leading Research Firms", G)
    tP = lc(k, 25, lead=0.6)
    items = [(0.6, "clip", "analysts", {"w": 1100, "h": 590, "top": True, "rate": min(1.0, 257 / max(1, (tP - 0.6) * FPS))}),
             (tP, "still", "recog")]
    card_switch(c, lt, items, 92, 262, 1100, 590, G)
    put_scaled(c, node("trophy", 110), 1530, 320, max(0.05, back((lt - 1.0) / 0.6)), vis(lt, 1.0) * G)
    firms = [("Gartner", "Gartner"), ("IDC", "I D C"), ("Forrester", "Forrester"), ("Bloor Research", "Bloor")]
    for j, (nm, ph) in enumerate(firms):
        tk = lc(k, 25, ph, lead=0.25)
        a = vis(lt, tk) * G
        if a <= 0:
            continue
        im = firm_img(nm)
        dx = (1 - a) * 40
        put(c, im, 1250 + dx, 410 + j * 100, a)
    tr = lc(k, 26, lead=0.2)
    a = vis(lt, tr) * G
    if a > 0:
        im = pill_img("ENTERPRISE DATA MANAGEMENT & AI", True, 16, 24, 50, 2)
        put(c, im, 1250 + (560 - im.width) / 2, 850 + (1 - a) * 14, a)


def scene7(c, t, lt, G):
    k = 7
    tg = lc(k, 28, lead=0.25)
    tb = lc(k, 29, lead=0.25)
    tE = lc(k, 30, lead=0.3)
    tcn = tE + 10.0  # (no separate connect-with-experts beat in this cut)
    tAg = lc(k, 31, lead=0.2)
    if lt < tE + 0.6:
        g = G * (1 - eio((lt - tE + 0.5) / 0.5))
        grey1 = ease((lt - tg) / 0.6)
        c1 = mix(TXT, (96, 90, 160), grey1)
        c1r = mix(RED, (120, 60, 120), grey1)
        X = 150
        t0 = 0.4
        put(c, text("FROM", "bold", 22, KICK, 4), X + 8, 232, vis(lt, t0) * g)
        put(c, text("DATA", "black", 104, c1), X, 256 + (1 - ease((lt - t0) / 0.7)) * 30, vis(lt, t0) * g)
        tt = lc(k, 27, "to intelligence", lead=0.2)
        put(c, text("TO", "bold", 22, KICK, 4), X + 560, 232, vis(lt, tt) * g)
        put(c, text("INTELLIGENCE", "black", 104, c1r), X + 552, 256 + (1 - ease((lt - tt) / 0.7)) * 30, vis(lt, tt) * g)
        put(c, text("FROM", "bold", 22, KICK, 4), X + 8, 452, vis(lt, tg) * g)
        put(c, text("GOVERNANCE", "black", 104, TXT), X, 476 + (1 - ease((lt - tg) / 0.7)) * 30, vis(lt, tg) * g)
        ta = lc(k, 28, "to action", lead=0.2)
        put(c, text("TO", "bold", 22, KICK, 4), X + 860, 452, vis(lt, ta) * g)
        put(c, text("ACTION", "black", 104, RED), X + 852, 476 + (1 - ease((lt - ta) / 0.7)) * 30, vis(lt, ta) * g)
        im = text("BUILDING THE AGENTIC FUTURE", "xbold", 46, TXT, 3)
        put(c, im, X + 8, 690 + (1 - ease((lt - tb) / 0.6)) * 20, vis(lt, tb) * g)
        ln = int(620 * ease((lt - tb - 0.2) / 0.9))
        if ln > 0 and g > 0.4:
            ImageDraw.Draw(c).rectangle((X + 8, 762, X + 8 + ln, 765), fill=mix(BGC, RED, g))
    # connect with experts
    if tcn <= lt < tE + 0.6:
        l = lt - tcn - 0.15
        g = G * (1 - eio((lt - tE + 0.35) / 0.45))
        cx, cy = W / 2, 540
        hub_center(c, cx, cy, 140, l, t, vis(l, 0) * g)
        ppl = [(-1, -1), (1, -1), (-1, 1), (1, 1), (-1.4, 0), (1.4, 0)]
        for j, (sx, sy) in enumerate(ppl):
            t0 = 0.2 + 0.12 * j
            aa = vis(l, t0) * g
            nx, ny = cx + sx * 380, cy + sy * 200
            pts = bez((cx, cy), (cx + sx * 150, cy), (nx - sx * 150, ny), (nx, ny), 30)
            connector(c, pts, ease((l - t0) / 0.7), aa, t + j * 0.2)
            put_scaled(c, node("person", 100), nx, ny, max(0.05, back((l - t0) / 0.5)), aa)
        t1 = text("CONNECT WITH EXPERTS", "black", 54, TXT, 2)
        put(c, t1, cx - t1.width / 2, 200 + (1 - ease(l / 0.6)) * 20, vis(l, 0) * g)
        ex = lc(k, 29, "Exchange", lead=0.2) - tcn
        t2 = text("EXCHANGE IDEAS", "black", 54, RED, 2)
        put(c, t2, cx - t2.width / 2, 790 + (1 - ease((l - ex) / 0.6)) * 20, vis(l, ex) * g)
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
        pa = vis(l, la + 1.2) * G
        if pa > 0:
            pill(c, "CONNECT WITH EXPERTS.   EXCHANGE IDEAS.", pa, y=790, size=26)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7]
WIPE = 1.0


def wipe(c, t):
    """Branded diagonal sweep at each scene boundary."""
    for k in range(1, 8):
        b = SC[k]["start"]
        if b - WIPE / 2 <= t <= b + WIPE / 2:
            p = eio((t - (b - WIPE / 2)) / WIPE)
            Sl = 260
            BWd = W + 2 * Sl + 240
            xl = -Sl + p * (W + Sl + BWd + Sl)
            L, R = xl - BWd, xl
            d = ImageDraw.Draw(c)
            d.polygon([(L + Sl, 0), (R + Sl, 0), (R - Sl, H), (L - Sl, H)], fill=INDIGO)
            d.polygon([(R - 70 + Sl, 0), (R + Sl, 0), (R - Sl, H), (R - 70 - Sl, H)], fill=RED)
            d.polygon([(R - 110 + Sl, 0), (R - 86 + Sl, 0), (R - 86 - Sl, H), (R - 110 - Sl, H)], fill=BLUE)
            d.polygon([(L + Sl, 0), (L + 40 + Sl, 0), (L + 40 - Sl, H), (L - Sl, H)], fill=BLUE)
            ia = 1 - min(1, abs(t - b) / 0.22)
            if ia > 0:
                put_scaled(c, bolt(130), W / 2, H / 2, 0.8 + 0.2 * ia, ia)
            return


def frame(t):
    c = bg_frame(t)
    for k, s in enumerate(SC):
        if s["start"] <= t < s["end"]:
            SCENES[k](c, t, t - s["start"], 1.0)
    s7 = SC[7]
    lt7 = t - s7["start"]
    show = 1.0
    if t < cue(1) - 0.3:
        show = 0.0
    elif t >= s7["start"] and lt7 >= lc(7, 30, lead=0.3):
        show = 0.0
    elif t < cue(1) + 0.4:
        show = ease((t - cue(1) + 0.3) / 0.7)
    chrome(c, t, show)
    caption(c, t)
    wipe(c, t)
    if t < 0.4:
        c = Image.blend(Image.new("RGB", (W, H), (14, 10, 44)), c, t / 0.4)
    if t > TOTAL - 0.8:
        c = Image.blend(c, Image.new("RGB", (W, H), (14, 10, 44)), min(1, (t - (TOTAL - 0.8)) / 0.8))
    return c


UHD = os.environ.get("UHD") == "1"


def render_range(args):
    f0, f1, out = args
    if UHD:
        p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "3840x2160", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-tune", "animation", "-profile:v", "high", "-level", "5.1",
                              "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            im = frame(f / FPS).resize((3840, 2160), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 45, 2))
            p.stdin.write(im.tobytes())
        p.stdin.close(); p.wait()
        return out
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-tune", "animation", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    return out


def dump_timeline():
    segs = [{"i": k, "start": SC[k]["start"], "end": SC[k]["end"]} for k in range(8)]
    json.dump({"total": TOTAL, "segs": segs, "lines": [{"start": L["start"], "dur": L["dur"]} for L in LINES]}, open(f"{B}/timeline5.json", "w"), indent=1)


if __name__ == "__main__":
    mode = sys.argv[1]
    dump_timeline()
    if mode == "info":
        print("total", round(TOTAL, 2)); [print(k, round(s["start"], 2), round(s["end"], 2)) for k, s in enumerate(SC)]
    elif mode == "still":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"{B}/s6_{ts}.jpg", quality=90)
    elif mode == "video":
        from multiprocessing import Pool
        nf = int(TOTAL * FPS)
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        nparts = nw * 4
        edges = [nf * q // nparts for q in range(nparts + 1)]
        tag = "u6" if UHD else "p6"
        jobs = [(edges[q], edges[q + 1], f"{B}/{tag}_{q:02d}.mp4") for q in range(nparts)]
        with Pool(nw) as pool:
            for o in pool.imap(render_range, jobs):
                print("done", o, flush=True)
        with open(f"{B}/parts6{'_uhd' if UHD else ''}.txt", "w") as f:
            for j in jobs:
                f.write(f"file '{j[2]}'\n")
