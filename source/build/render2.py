# Solix Empower 2026 AV - v2 renderer (motion graphics, light coral reference style)
import json, os, re, sys, math, subprocess, glob, random
from functools import lru_cache
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

B = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(B)
A1, A2 = f"{S}/assets", f"{S}/assets2"
C1, C2 = f"{S}/clips", f"{S}/clips2"
W, H, FPS = 1920, 1080, 30
RED = (228, 35, 40)
DRED = (190, 22, 30)
INK = (17, 17, 17)
GREY = (112, 112, 120)
BLUSH = (251, 226, 224)
FD = "/usr/share/fonts/opentype/inter/"
FONTS = {"black": FD + "InterDisplay-Black.otf", "xbold": FD + "InterDisplay-ExtraBold.otf", "bold": FD + "Inter-Bold.otf",
         "semi": FD + "Inter-SemiBold.otf", "med": FD + "Inter-Medium.otf", "reg": FD + "Inter-Regular.otf"}

# ------------------------------------------------------------------ timeline
LINES = json.load(open(f"{B}/lines.json"))
FIRST = 3.0       # first VO line start (intro motion before it)
SCENE_PAD = 0.7   # extra air at scene changes
PRE = 0.75        # scene starts this long before its first line
TAIL = 4.5
t = FIRST
for i, L in enumerate(LINES):
    if i and L["scene"] != LINES[i - 1]["scene"]:
        t += SCENE_PAD
    L["start"] = t
    L["dur"] = sf.info(f"{B}/vo2/{i:02d}.wav").duration
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
    ImageDraw.Draw(im).rounded_rectangle((pad, pad + dy, pad + w, pad + h + dy), r, fill=(130, 20, 28, alpha))
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


def still(name, maxw, maxh, lt=0.0, zoom=0.045, zd=9.0):
    """Product screenshot card with slow push-in (Ken Burns inside fixed frame)."""
    w, h = fit_size(name, maxw, maxh)
    src = asset(name)
    s = 1 + zoom * eio(lt / zd)
    cw, ch = src.width / s, src.height / s
    l, t = (src.width - cw) / 2, (src.height - ch) * 0.35
    im = src.resize((w, h), Image.BILINEAR, box=(l, t, l + cw, t + ch))
    return finish_card(im, w, h)


@lru_cache(None)
def frames(name):
    d = f"{C2}/{name}" if os.path.isdir(f"{C2}/{name}") else f"{C1}/{name}"
    return sorted(glob.glob(f"{d}/*.jpg"))


def clip(name, lt, w, h, rate=1.0, top=False):
    fr = frames(name)
    n = len(fr)
    i = min(n - 1, max(0, int(lt * FPS * rate)))
    im = Image.open(fr[i])
    sc = max(w / im.width, h / im.height)
    nw, nh = int(im.width * sc + 0.5), int(im.height * sc + 0.5)
    im = im.resize((nw, nh), Image.BILINEAR)
    l = (nw - w) // 2
    tt = 0 if top else (nh - h) // 2
    return finish_card(im.crop((l, tt, l + w, tt + h)), w, h)


@lru_cache(None)
def logo(w):
    im = Image.open(f"{A1}/logo.png").convert("RGBA")
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
    """white circle with soft ring + icon, like reference hub nodes"""
    pad = 30
    S_ = size + pad * 2
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad, pad + 10, pad + size, pad + size + 10), fill=(140, 20, 30, 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ss = 3
    c = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0))
    ImageDraw.Draw(c).ellipse((0, 0, size * ss - 1, size * ss - 1), fill=(255, 255, 255, 255), outline=RED + (255,) if active else (230, 200, 200, 255), width=int(size * ss * 0.035))
    c = c.resize((size, size), Image.LANCZOS)
    im.alpha_composite(c, (pad, pad))
    ic = icon(kind, int(size * 0.62))
    im.alpha_composite(ic, (pad + (size - ic.width) // 2, pad + (size - ic.height) // 2))
    return im


# ------------------------------------------------------------------ background
@lru_cache(None)
def background():
    BW, BH = W + 260, H + 180
    base = Image.new("RGB", (BW, BH), (255, 255, 255))
    g = Image.linear_gradient("L").rotate(90).resize((BW, BH))
    blush = Image.new("RGB", (BW, BH), (247, 198, 196))
    im = Image.composite(base, blush, g.point(lambda v: int(255 * (v / 255) ** 0.55)))
    ov = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((BW - 900, -500, BW + 500, 700), fill=(240, 110, 108, 115))
    d.ellipse((BW - 1100, BH - 520, BW - 100, BH + 480), fill=(246, 150, 148, 70))
    d.ellipse((-400, BH - 300, 500, BH + 600), fill=(250, 210, 208, 90))
    ov = ov.filter(ImageFilter.GaussianBlur(160))
    im = Image.alpha_composite(im.convert("RGBA"), ov)
    gr = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gr)
    for x in range(0, BW, 96):
        gd.line((x, 0, x, BH), fill=(200, 120, 120, 13))
    for y in range(0, BH, 96):
        gd.line((0, y, BW, y), fill=(200, 120, 120, 13))
    im = Image.alpha_composite(im, gr)
    rg = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rg)
    cx, cy = BW - 380, BH - 260
    for rr, al in ((430, 38), (300, 28)):
        rd.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 255, 255, al))
    return Image.alpha_composite(im, rg.filter(ImageFilter.GaussianBlur(6))).convert("RGB")


rnd = random.Random(11)
PART = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(-14, 14), rnd.uniform(-9, 9), rnd.uniform(1.6, 3.6)) for _ in range(46)]


def particles(c, t, strength=1.0):
    d = ImageDraw.Draw(c)
    pts = []
    for (x0, y0, vx, vy, r) in PART:
        x = (x0 + vx * t + 30 * math.sin(t * 0.2 + y0)) % (W + 200) - 100
        y = (y0 + vy * t + 20 * math.cos(t * 0.17 + x0)) % (H + 200) - 100
        pts.append((x, y, r))
    bgc = (248, 228, 228)
    for i in range(len(pts)):
        xi, yi, _ = pts[i]
        for j in range(i + 1, len(pts)):
            xj, yj, _ = pts[j]
            dx, dy = xi - xj, yi - yj
            dd = dx * dx + dy * dy
            if dd < 230 * 230:
                k = (1 - math.sqrt(dd) / 230) * 0.32 * strength
                d.line((xi, yi, xj, yj), fill=mix(bgc, (226, 96, 100), k), width=1)
    for x, y, r in pts:
        d.ellipse((x - r, y - r, x + r, y + r), fill=mix(bgc, (226, 70, 76), 0.55 * strength))


def bg_frame(t):
    bg = background()
    ox = 130 + 120 * math.sin(t / 10.0)
    oy = 90 + 80 * math.cos(t / 12.0)
    c = bg.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    particles(c, t)
    return c


# ------------------------------------------------------------------ UI pieces
def heading(c, lt, kicker, title, G, x=92, y=96, tout=None, size=58):
    k = text(kicker, "bold", 19, RED, 4)
    ti = fit_text(title, "xbold", size, W - 2 * x)
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
        ImageDraw.Draw(c).rectangle((x, y + 30 + ti.height + 8, x + ln, y + 30 + ti.height + 11), fill=mix((250, 220, 220), RED, G))


@lru_cache(None)
def callout_img(num, title, sub, w, active=False, ico=None):
    h = 96 if sub else 74
    im = box(w, h, 12, (255, 255, 255, 255), (RED if active else (236, 232, 234)), 3 if active else 2)
    d = ImageDraw.Draw(im)
    if ico:
        ic = icon(ico, 46, RED)
        im.alpha_composite(ic, (16, int(h / 2 - 23)))
    else:
        d.ellipse((20, h / 2 - 17, 54, h / 2 + 17), fill=RED)
        n = text(str(num), "bold", 18, (255, 255, 255))
        im.alpha_composite(n, (int(37 - n.width / 2 + 1), int(h / 2 - 12)))
    t1 = fit_text(title, "bold", 24, w - 90, INK)
    if sub:
        im.alpha_composite(t1, (74, 17))
        im.alpha_composite(fit_text(sub, "med", 17, w - 92, GREY), (74, 54))
    else:
        im.alpha_composite(t1, (74, int(h / 2 - 16)))
    return im


def callout(c, x, y, num, title, sub, w, a, active=False, slide=40, ico=None):
    if a <= 0.004:
        return
    im = callout_img(num, title, sub, w, active, ico)
    sh, pad = shadow(im.width, im.height, 12, 16, 40, 8)
    dx = (1 - a) * slide
    put(c, sh, x - pad + dx, y - pad, a)
    put(c, im, x + dx, y, a)


@lru_cache(None)
def pill_img(label, active, size=19, padx=26, h=48, track=2, dim=False):
    fg = (255, 255, 255) if active else ((150, 150, 156) if dim else (70, 70, 76))
    tx = text(label, "bold", size, fg, track)
    w = tx.width + padx * 2
    im = box(w, h, h // 2, RED + (255,) if active else (255, 255, 255, 255), None if active else (230, 226, 228))
    im.alpha_composite(tx, (padx, int(h / 2 - tx.height / 2) + 1))
    return im


def pill(c, s, a, y=962, size=27, cx=W / 2):
    tx = fit_text(s, "semi", size, 1640, INK)
    w, h = tx.width + 64, 62
    x = cx - w / 2
    sh, pad = shadow(w, h, 12, 16, 45, 8)
    put(c, sh, x - pad, y - pad, a)
    put(c, box(w, h, 12), x, y, a)
    put(c, tx, x + 32, y + (h - tx.height) / 2 + 1, a)


def caption(c, t):
    for (t0, t1, s, i, first) in CAPS:
        if t0 <= t < t1:
            if LINES[i]["scene"] == 7 and i >= len(LINES) - 2:
                return
            a = vis(t, t0, t1 - 0.2, 0.25, 0.2) if first or True else 1.0
            # chunks within a line switch with a quick fade
            pill(c, s, max(a, 0.0))
            return


def chrome(c, t, show_logo=1.0):
    put(c, text("SOLIX EMPOWER 2026", "bold", 15, (110, 110, 116), 4), 92, 46, vis(t, 0.6, None, 0.8))
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
    col = mix((250, 225, 225), RED, a)
    d.line(pts[:n], fill=col, width=width)
    hx, hy = pts[n - 1]
    d.ellipse((hx - 6, hy - 6, hx + 6, hy + 6), fill=col)
    if pulse and p >= 1:
        u = (t * 0.6) % 1
        k = int(u * (len(pts) - 1))
        x, y = pts[k]
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=mix((250, 225, 225), (255, 120, 120), a))
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 255))


@lru_cache(None)
def glow(r, alpha=70):
    im = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((r, r, r * 3, r * 3), fill=(240, 80, 80, alpha))
    return im.filter(ImageFilter.GaussianBlur(r * 0.45))


def dashed_ring(c, cx, cy, r, t, a, n=36, speed=0.25, width=4):
    if a <= 0:
        return
    d = ImageDraw.Draw(c)
    col = mix((250, 225, 225), RED, a * 0.8)
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
    put_scaled(c, bolt(size), cx, cy - (18 if label else 0), max(0.01, s), a)
    if label:
        tl_ = text(label, "bold", 20, INK, 2)
        put(c, tl_, cx - tl_.width / 2, cy + size * 0.42, a)


@lru_cache(None)
def disc_img(d):
    pad = 40
    im = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad, pad + 12, pad + d, pad + d + 12), fill=(140, 20, 30, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    ss = 3
    c = Image.new("RGBA", (d * ss, d * ss), (0, 0, 0, 0))
    ImageDraw.Draw(c).ellipse((0, 0, d * ss - 1, d * ss - 1), fill=(255, 255, 255, 255))
    im.alpha_composite(c.resize((d, d), Image.LANCZOS), (pad, pad))
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
            return still(name, maxw, maxh, l)
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


# ------------------------------------------------------------------ scenes
def scene0(c, t, lt, G):
    """Pure motion graphics intro."""
    cx, cy = W / 2, 470
    l0 = cue(0) - 0.0   # welcome line start (global == local for scene 0)
    # A) network converging into the bolt (0 - l0)
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
            x = sx + (tx_ - sx) * conv
            y = sy + (ty_ - sy) * conv
            pts.append((x, y))
        bgc = (248, 230, 230)
        for k in range(n):
            x, y = pts[k]
            x2, y2 = pts[(k + 1) % n]
            d.line((x, y, x2, y2), fill=mix(bgc, (230, 110, 110), 0.5 * aA), width=1)
            if k % 3 == 0:
                d.line((x, y, cx, cy), fill=mix(bgc, (235, 150, 150), 0.35 * aA * conv), width=1)
        for (x, y) in pts:
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=mix(bgc, RED, 0.8 * aA))
        # logo reveal
        la = vis(lt, 1.6, tA_out, 0.8, 0.5) * G
        s = 0.86 + 0.14 * ease((lt - 1.6) / 1.4)
        put_scaled(c, logo(900), cx, cy, s, la)
        wk = text("WELCOME TO", "bold", 22, RED, 6)
        put(c, wk, cx - wk.width / 2, cy + 178 + (1 - ease((lt - l0 + 0.2) / 0.6)) * 16, vis(lt, l0 - 0.2, tA_out, 0.6, 0.5) * G)
        ev = text("SOLIX EMPOWER 2026", "black", 76, INK)
        put(c, ev, cx - ev.width / 2, cy + 214 + (1 - ease((lt - l0) / 0.7)) * 26, vis(lt, l0, tA_out, 0.7, 0.5) * G)
    # B) 20+ years (line 1)
    tB = cue(1) - 0.3
    tB_out = cue(2) - 0.7
    if tB - 0.1 <= lt < tB_out + 0.6:
        l = lt - tB
        a = vis(l, 0, tB_out - tB, 0.7, 0.5) * G
        put(c, text("SOLIX TECHNOLOGIES", "bold", 20, RED, 5), 150 - (1 - ease(l / 0.6)) * 40, 300, a)
        cnt = int(round(20 * ease(l / 1.6)))
        num = text(f"{cnt}+", "black", 280, RED)
        put(c, num, 136, 330 + (1 - ease(l / 0.6)) * 40, a)
        put(c, text("YEARS OF ENTERPRISE", "xbold", 60, INK), 150, 660 + (1 - ease((l - 0.3) / 0.6)) * 30, vis(l, 0.3, tB_out - tB) * G)
        put(c, text("DATA INNOVATION", "xbold", 60, INK), 150, 732 + (1 - ease((l - 0.45) / 0.6)) * 30, vis(l, 0.45, tB_out - tB) * G)
        # right: data -> strategic advantage motion graphic (rising bars + trend)
        bx, by, bw, bh = 1030, 300, 760, 520
        pa = vis(l, 0.4, tB_out - tB) * G
        if pa > 0:
            panel = box(bw, bh, 18)
            sh, pad = shadow(bw, bh)
            put(c, sh, bx - pad, by - pad, pa); put(c, panel, bx, by, pa)
            d = ImageDraw.Draw(c)
            put(c, text("FROM DATA", "bold", 16, GREY, 3), bx + 40, by + 36, pa)
            put(c, text("TO STRATEGIC ADVANTAGE", "bold", 16, RED, 3), bx + bw - 40 - text("TO STRATEGIC ADVANTAGE", "bold", 16, RED, 3).width, by + 36, pa)
            vals = [0.18, 0.26, 0.31, 0.42, 0.5, 0.63, 0.74, 0.9]
            base_y = by + bh - 70
            pts = []
            for k, v in enumerate(vals):
                gp = ease((l - 0.7 - k * 0.12) / 0.7)
                x0 = bx + 60 + k * 82
                hh = v * 330 * gp
                col = mix((250, 225, 225), mix((246, 170, 170), RED, k / 7), pa)
                d.rounded_rectangle((x0, base_y - hh, x0 + 50, base_y), 6, fill=col)
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
    # C) unified foundation: four nodes around a hub (line 2)
    tC = cue(2) - 0.5
    if lt >= tC - 0.1:
        l = lt - tC
        a = vis(l, 0, None, 0.7) * G
        k_ = text("ONE UNIFIED FOUNDATION", "bold", 20, RED, 5)
        put(c, k_, cx - k_.width / 2, 170, a)
        hx, hy = cx, 520
        hub_center(c, hx, hy, 150, l, t, a, "UNIFIED FOUNDATION")
        items = [("Data Management", "db", "data management", (-520, -170)), ("Governance", "shield", "governance", (520, -170)),
                 ("Content Services", "doc", "content services", (-520, 190)), ("AI", "spark", "AI,", (520, 190))]
        for lab, ic, ph, (dx, dy) in items:
            tk = cue(2, ph) - tC - 0.35
            p = ease((l - tk) / 0.8)
            aa = vis(l, tk, None, 0.5) * G
            if aa <= 0:
                continue
            nx, ny = hx + dx, hy + dy
            sgn = 1 if dx > 0 else -1
            pts = bez((hx + sgn * 120, hy + dy * 0.25), (hx + sgn * 260, hy + dy * 0.3), (nx - sgn * 220, ny), (nx - sgn * 80, ny))
            connector(c, pts, p, aa, t + dx * 0.001)
            nd = node(ic, 130)
            put_scaled(c, nd, nx, ny, max(0.05, back((l - tk) / 0.6)), aa)
            tl_ = text(lab.upper(), "bold", 22, INK, 3)
            put(c, tl_, nx - tl_.width / 2, ny + 82, aa)


def scene1(c, t, lt, G):
    k = 1
    heading(c, lt, "SOLIX ENTERPRISE FOUNDATION", "One Unified Enterprise Platform", G)
    t1 = lc(k, 4, "Common Data")
    t2 = lc(k, 4, "Enterprise Data Governance")
    t3 = lc(k, 4, "Enterprise Content")
    tv = [lc(k, 5, v) for v in ("discover", "manage", "secure", "govern", "activate")]
    pills = [("Common Data Platform", "Unified data foundation", t1, "db"), ("Enterprise Data Governance", "Catalog · Knowledge graph · Enforcement", t2, "shield"),
             ("Enterprise Content Services", "Secure, AI-ready content", t3, "doc")]
    act = -1
    for j, p in enumerate(pills):
        if lt >= p[2]:
            act = j
    for j, (ti, sub, tk, ic) in enumerate(pills):
        st = 0.6 + 0.18 * j
        callout(c, 92, 262 + j * 116, j + 1, ti, sub, 540, vis(lt, st) * G, active=(j == act), ico=ic)
    # verb flow
    verbs = ["DISCOVER", "MANAGE", "SECURE", "GOVERN", "ACTIVATE"]
    x, y = 92, 640
    for j, v in enumerate(verbs):
        on = lt >= tv[j]
        im = pill_img(v, on, 16, 20, 42)
        if x + im.width > 92 + 560:
            x, y = 92, y + 56
        put(c, im, x, y + (1 - ease((lt - 0.9) / 0.6)) * 14, vis(lt, 0.9 + 0.08 * j) * G * (1.0 if on else 0.75))
        x += im.width + 12
    items = [(0.7, "clip", "cdp", {"w": 1160, "h": 600, "top": True, "rate": 0.9}),
             (max(t2, 1.5), "clip", "edg", {"w": 1160, "h": 600, "top": True, "rate": 0.9}),
             (t3, "still", "found3")]
    card_switch(c, lt, items, 680, 262, 1160, 600, G)


def scene2(c, t, lt, G):
    k = 2
    heading(c, lt, "ENTERPRISE AI", "Bringing Intelligence to Enterprise Data", G)
    names = [("Data Sense", 7, "Data Sense", "datasense", "Semantic understanding", "Understand", "graph"),
             ("Data Ask", 8, "Data Ask", "dataask", "Natural-language interaction", "Answer", "chat"),
             ("Application Knowledge Graphs", 9, "Application", "akg", "Connected business context", "Build", "graph"),
             ("AI Warehouse", 10, "AI Warehouse", "aiwh", "Build governed AI", "Build", "warehouse"),
             ("Solix Agentic", 10, "Solix Agentic", "agentic", "Activate governed AI", "Activate", "agent")]
    ts = [lc(k, n[1], n[2], lead=0.3) for n in names]
    tB = ts[0] - 0.3
    # Phase A: hub with 4 pillars
    if lt < tB + 0.6:
        g = G * (1 - eio((lt - tB + 0.1) / 0.6))
        cx, cy = W / 2, 560
        hub_center(c, cx, cy, 170, lt - 0.5, t, vis(lt, 0.5) * g)
        labs = [("Understand", "Data Sense", "graph", -1, -1), ("Answer", "Data Ask", "chat", -1, 1), ("Build", "Knowledge Graphs · AI Warehouse", "warehouse", 1, -1), ("Activate", "Solix Agentic", "agent", 1, 1)]
        for j, (lab, sub, ic, sx, sy) in enumerate(labs):
            t0 = 1.0 + 0.4 * j
            aa = vis(lt, t0) * g
            if aa <= 0:
                continue
            ex = cx + sx * 470
            pts = bez((cx + sx * 140, cy + sy * 30), (cx + sx * 280, cy + sy * 30), (cx + sx * 300, cy + sy * 160), (ex, cy + sy * 160))
            connector(c, pts, ease((lt - t0) / 0.8), aa, t + j * 0.25)
            bx = ex - (470 if sx < 0 else -10)
            callout(c, bx if sx > 0 else ex - 470, cy + sy * 160 - 48, j + 1, lab, sub, 460, aa, ico=ic)
    if lt < tB:
        return
    l = lt
    act = 0
    for j, tk in enumerate(ts):
        if l >= tk:
            act = j
    # step chain
    x = 92
    for j, n in enumerate(names):
        im = pill_img(n[0].upper(), j == act, 16, 20, 44, 1, dim=j > act)
        a = vis(l, tB + 0.1 * j) * G
        put(c, im, x, 236 + (1 - a) * 12, a)
        if j < 4:
            ar = text("→", "bold", 24, RED if j < act else (200, 170, 170))
            put(c, ar, x + im.width + 9, 241, a)
            x += im.width + 46
    items = []
    for j, n in enumerate(names):
        tt = ts[j] if j else tB + 0.15
        if n[3] == "akg":
            items.append((tt, "clip", "akg", {"w": 1180, "h": 590, "top": True, "rate": 0.8}))
        else:
            items.append((tt, "still", n[3]))
    card_switch(c, l, items, 92, 318, 1180, 590, G, align="left")
    n = names[act]
    a = vis(l, ts[act] + 0.25, None, 0.5) * G
    # node + callout on the right
    put_scaled(c, node(n[6], 150), 1560, 470, max(0.05, back((l - ts[act] - 0.1) / 0.6)), a)
    callout(c, 1330, 600, act + 1, n[5], n[4], 470, a)


def scene3(c, t, lt, G):
    k = 3
    heading(c, lt, "DATA LIFECYCLE & ARCHIVING", "Retire. Preserve. Archive. Activate.", G)
    L = SC[3]["lines"]  # 11..15
    tIntro, tG1, tG2, tG3, tBen = [cue(i) - SC[3]["start"] - 0.35 for i in L]
    labels = ["Application Retirement", "Data Preservation", "SAP", "Oracle", "Mainframe", "Email", "File", "Database", "Active Archiving"]
    phrases = [(12, "application retirement"), (12, "data preservation"), (13, "SAP"), (13, "Oracle"), (13, "mainframe"), (14, "email"), (14, "file"), (14, "database"), (14, "active archiving")]
    tl_ = [lc(k, i, ph, lead=0.25) for i, ph in phrases]
    # tracker pills row
    x = 92
    for j, lab in enumerate(labels):
        on = lt >= tl_[j]
        im = pill_img(lab.upper(), on and lt < tBen, 14, 16, 38, 1, dim=not on)
        a = vis(lt, 0.8 + 0.05 * j) * G
        put(c, im, x, 236 + (1 - a) * 10, a)
        x += im.width + 10
    # phase 0: lifecycle ring motion graphic
    if lt < tG1 + 0.6:
        g = G * (1 - eio((lt - tG1) / 0.6))
        cx, cy = W / 2, 590
        a = vis(lt, 0.6) * g
        hub_center(c, cx, cy, 150, lt - 0.6, t, a, "DATA LIFECYCLE")
        stages = [("RETIRE", "cycle"), ("PRESERVE", "shield"), ("ARCHIVE", "db"), ("ACTIVATE", "spark")]
        R = 300
        for j, (lab, ic) in enumerate(stages):
            t0 = 1.0 + 0.35 * j
            aa = vis(lt, t0) * g
            if aa <= 0:
                continue
            ang = -math.pi / 2 + j * math.pi / 2 + 0.25
            # arc segment between nodes
            d = ImageDraw.Draw(c)
            p = ease((lt - t0) / 0.8)
            a0 = math.degrees(ang) + 14
            d.arc((cx - R * 1.35, cy - R * 0.78, cx + R * 1.35, cy + R * 0.78), a0, a0 + 62 * p, fill=mix((250, 225, 225), RED, aa), width=4)
            nx, ny = cx + R * 1.35 * math.cos(ang), cy + R * 0.78 * math.sin(ang)
            put_scaled(c, node(ic, 110), nx, ny, max(0.05, back((lt - t0) / 0.6)), aa)
            tlab = text(lab, "bold", 20, INK, 3)
            put(c, tlab, nx - tlab.width / 2, ny + 66, aa)
    # group 1: application retirement + data preservation
    if tG1 <= lt < tG2 + 0.7:
        l = lt - tG1
        g = G * (1 - eio((lt - tG2) / 0.7))
        for j, (nm, lab, tj) in enumerate([("appret", "APPLICATION RETIREMENT", 0.0), ("datapres", "DATA PRESERVATION", tl_[1] - tG1)]):
            im = still(nm, 840, 520, l - tj)
            x0 = 92 + j * 900
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.7)) * 100, 330, a)
            pi_ = pill_img(lab, True, 15, 18, 40, 2)
            put(c, pi_, x0 + 20, 300 + (1 - a) * 10, a)
    # group 2: SAP, Oracle, Mainframe cascade
    if tG2 <= lt < tG3 + 0.7:
        l = lt - tG2
        g = G * (1 - eio((lt - tG3) / 0.7))
        for j, (nm, lab) in enumerate([("sap", "SAP"), ("oracle", "ORACLE"), ("mainframe", "MAINFRAME")]):
            tj = max(0.0, tl_[2 + j] - tG2)
            im = still(nm, 760, 380, l - tj)
            x0 = 92 + j * 300
            y0 = 330 + j * 120
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.7)) * 120, y0, a)
            pi_ = pill_img(lab, True, 16, 20, 42, 2)
            put(c, pi_, x0 + 18, y0 - 26, a)
        # right callout panel
        callout(c, 1300, 360, 1, "Enterprise applications", "SAP · Oracle E-Business Suite", 520, vis(l, 0.5) * g, ico="db")
        callout(c, 1300, 476, 2, "Mainframe modernization", "Retire with confidence", 520, vis(l, tl_[4] - tG2 + 0.2) * g, ico="chip")
    # group 3: email, file, database, active (2x2)
    if tG3 <= lt < tBen + 0.7:
        l = lt - tG3
        g = G * (1 - eio((lt - tBen) / 0.7))
        cells = [("email", "EMAIL"), ("file", "FILE"), ("database", "DATABASE"), ("active", "ACTIVE ARCHIVING")]
        for j, (nm, lab) in enumerate(cells):
            tj = max(0.0, tl_[5 + j] - tG3)
            cx0 = 92 + (j % 2) * 880
            cy0 = 320 + (j // 2) * 316
            im = still(nm, 840, 270, l - tj)
            a = vis(l, tj) * g
            draw_card(c, im, cx0 + (840 - im.width) / 2, cy0 + 22 + (1 - ease((l - tj) / 0.7)) * 40, a)
            pi_ = pill_img(lab, True, 15, 18, 40, 2)
            put(c, pi_, cx0 + 10, cy0 - 2, a)
    # benefits: animated cost graphic
    if lt >= tBen:
        l = lt - tBen
        a = vis(l, 0) * G
        bx, by, bw, bh = 92, 320, 900, 560
        sh, pad = shadow(bw, bh)
        put(c, sh, bx - pad, by - pad, a); put(c, box(bw, bh, 18), bx, by, a)
        put(c, text("TOTAL COST OF LEGACY DATA", "bold", 16, GREY, 3), bx + 44, by + 38, a)
        d = ImageDraw.Draw(c)
        base_y = by + bh - 80
        before = [0.82, 0.86, 0.9, 0.94]
        for j in range(8):
            v0 = before[j] if j < 4 else before[3]
            target = v0 if j < 4 else [0.62, 0.45, 0.34, 0.28][j - 4]
            gp = ease((l - 0.5 - 0.1 * j) / 0.6)
            dv = ease((l - 1.6 - 0.12 * (j - 4)) / 0.9) if j >= 4 else 0
            v = (v0 + (target - v0) * dv) * gp
            x0 = bx + 70 + j * 100
            col = mix((255, 255, 255), (232, 222, 224) if j < 4 else mix(RED, (246, 160, 160), (j - 4) / 4), a)
            d.rounded_rectangle((x0, base_y - v * 340, x0 + 60, base_y), 8, fill=col)
        put(c, text("BEFORE", "bold", 15, GREY, 3), bx + 210, base_y + 20, a)
        put(c, text("WITH SOLIX", "bold", 15, RED, 3), bx + 600, base_y + 20, a)
        put_scaled(c, node("dollar", 110), bx + bw - 110, by + 110, max(0.05, back((l - 0.3) / 0.6)), a)
        bens = [("Reduce complexity", "Retire legacy applications", "reduce complexity", "cycle"), ("Control costs", "Lower infrastructure and license spend", "control costs", "dollar"),
                ("Preserve information", "Without costly migration", "preserve valuable", "shield")]
        for j, (ti, sub, ph, ic) in enumerate(bens):
            tk = lc(k, 15, ph) - tBen
            callout(c, 1060, 330 + j * 124, j + 1, ti, sub, 600, vis(l, max(0.3, tk)) * G, ico=ic)
        tn = lc(k, 15, "without costly") - tBen
        pa = vis(l, tn) * G
        if pa > 0:
            im = pill_img("NO COSTLY MIGRATION", True, 18, 28, 54, 3)
            put_scaled(c, im, 1060 + 300, 760, 0.85 + 0.15 * back((l - tn) / 0.6), pa)


def patient360(c, cx, cy, l, t, a):
    hub = node("person", 170)
    R1, R2 = 290, 190
    srcs = [("HIS", "db"), ("EMR", "doc"), ("LIS", "flask"), ("RIS / PACS", "chart"), ("VITALS", "heart"), ("CLAIMS", "dollar")]
    d = ImageDraw.Draw(c)
    for j, (lab, ic) in enumerate(srcs):
        t0 = 0.3 + 0.15 * j
        aa = vis(l, t0) * a
        if aa <= 0:
            continue
        ang = -math.pi / 2 + j * 2 * math.pi / len(srcs) + l * 0.05
        nx, ny = cx + R1 * math.cos(ang), cy + R2 * math.sin(ang)
        pts = bez((nx, ny), (nx * 0.7 + cx * 0.3, ny * 0.7 + cy * 0.3), (nx * 0.4 + cx * 0.6, ny * 0.4 + cy * 0.6), (cx, cy), 30)
        connector(c, pts, ease((l - t0) / 0.8), aa, t + j * 0.17)
        put_scaled(c, node(ic, 84), nx, ny, max(0.05, back((l - t0) / 0.5)), aa)
        tl_ = text(lab, "bold", 15, INK, 2)
        put(c, tl_, nx - tl_.width / 2, ny + 50, aa)
    g = glow(120)
    put(c, g, cx - g.width / 2, cy - g.height / 2, a * 0.8)
    put_scaled(c, hub, cx, cy, max(0.05, back(l / 0.6)), a)
    tl_ = text("PATIENT 360", "black", 26, RED, 3)
    put(c, tl_, cx - tl_.width / 2, cy + 104, a)


def scene4(c, t, lt, G):
    k = 4
    heading(c, lt, "INDUSTRY-SPECIFIC INNOVATION", "Purpose-Built for Every Industry", G)
    tI = lc(k, 16, lead=0.0)
    tH = lc(k, 17, lead=0.35)
    tP = lc(k, 18, lead=0.35)
    tA = lc(k, 19, lead=0.35)
    tabs = ["EAI HEALTHCARE", "EAI PHARMA", "SOLIX ACADEMY"]
    act = -1 if lt < tH else (0 if lt < tP else (1 if lt < tA else 2))
    x = 92
    for j, lab in enumerate(tabs):
        im = pill_img(lab, j == act, 17, 24, 46, 2)
        put(c, im, x, 238, vis(lt, 0.7 + 0.12 * j) * G)
        x += im.width + 14
    # intro: three industry nodes
    if lt < tH + 0.6:
        g = G * (1 - eio((lt - tH) / 0.6))
        for j, (ic, lab) in enumerate([("heart", "HEALTHCARE"), ("flask", "PHARMA"), ("cap", "ACADEMY")]):
            t0 = 0.8 + 0.25 * j
            aa = vis(lt, t0) * g
            nx = W / 2 + (j - 1) * 480
            put_scaled(c, node(ic, 200), nx, 560, max(0.05, back((lt - t0) / 0.6)), aa)
            tl_ = text(lab, "black", 30, INK, 4)
            put(c, tl_, nx - tl_.width / 2, 690, aa)
            if j < 2:
                pts = [(nx + 130 + u * 220 / 20, 560) for u in range(21)]
                connector(c, pts, ease((lt - t0 - 0.3) / 0.6), aa, t + j * 0.4)
    if tH <= lt < tP + 0.7:
        l = lt - tH
        g = G * (1 - eio((lt - tP) / 0.7))
        im = still("eaihc", 960, 560, l, 0.035)
        draw_card(c, im, 92 + (1 - ease(l / 0.8)) * 100, 320, vis(l, 0) * g)
        patient360(c, 1500, 540, l - 0.4, t, vis(l, 0.4) * g)
        tg = lc(k, 17, "governed clinical", lead=0.3) - tH
        pa = vis(l, tg) * g
        if pa > 0:
            pi_ = pill_img("GOVERNED CLINICAL INTELLIGENCE", True, 16, 22, 46, 2)
            put(c, pi_, 1500 - pi_.width / 2, 840 + (1 - pa) * 14, pa)
    if tP <= lt < tA + 0.7:
        l = lt - tP
        g = G * (1 - eio((lt - tA) / 0.7))
        draw_card(c, clip("pharma", l, 1080, 580, 0.9), 92 + (1 - ease(l / 0.8)) * 100, 310, vis(l, 0) * g)
        callout(c, 1240, 350, 1, "EAI Pharma", "Data and AI capabilities", 590, vis(l, 0.4) * g, ico="flask")
        tpi = lc(k, 18, "pharmaceutical", lead=0.3) - tP
        callout(c, 1240, 470, 2, "Pharmaceutical Innovation", "Governed data for research & discovery", 590, vis(l, tpi) * g, ico="spark")
    if lt >= tA:
        l = lt - tA
        a = vis(l, 0) * G
        # learning path motion graphic
        bx, by, bw, bh = 92, 310, 1100, 580
        sh, pad = shadow(bw, bh)
        put(c, sh, bx - pad + (1 - a) * 80, by - pad, a); put(c, box(bw, bh, 18), bx + (1 - a) * 80, by, a)
        put(c, text("SOLIX ACADEMY", "black", 40, INK, 2), bx + 50, by + 40, a)
        put(c, text("solixacademy.com", "semi", 20, RED), bx + 52, by + 96, a)
        put_scaled(c, node("cap", 120), bx + bw - 110, by + 90, max(0.05, back((l - 0.2) / 0.6)), a)
        steps = [("DATA", "db"), ("GOVERNANCE", "shield"), ("ENTERPRISE AI", "spark"), ("AGENTIC", "agent")]
        y0 = by + 330
        d = ImageDraw.Draw(c)
        x0, x1 = bx + 130, bx + bw - 130
        p = ease((l - 0.6) / 2.2)
        d.line((x0, y0, x1, y0), fill=mix((255, 255, 255), (236, 228, 230), a), width=8)
        if p > 0:
            d.line((x0, y0, x0 + (x1 - x0) * p, y0), fill=mix((255, 255, 255), RED, a), width=8)
        for j, (lab, ic) in enumerate(steps):
            nx = x0 + (x1 - x0) * j / 3
            on = p >= j / 3 - 0.01
            put_scaled(c, node(ic, 110, on), nx, y0, 1.0 if on else 0.85, a * (1.0 if on else 0.6))
            tl_ = text(lab, "bold", 18, INK if on else GREY, 2)
            put(c, tl_, nx - tl_.width / 2, y0 + 70, a)
        ts_ = lc(k, 19, "skills", lead=0.3) - tA
        callout(c, 1250, 360, 1, "Skills for every team", "Learn, practice and grow", 580, vis(l, max(0.5, ts_)) * G, ico="cap")
        tr = lc(k, 19, "AI-ready", lead=0.3) - tA
        callout(c, 1250, 480, 2, "AI-Ready Enterprise", "Build the skills needed for AI", 580, vis(l, tr) * G, ico="spark")


def scene5(c, t, lt, G):
    k = 5
    heading(c, lt, "TRUSTED BY GLOBAL ENTERPRISES", "Solving Complex Data Challenges at Enterprise Scale", G, size=54)
    dur = SC[5]["end"] - SC[5]["start"]
    draw_card(c, clip("logos", lt - 0.6, 1100, 620, min(1.0, 474 / max(1, (dur - 0.6) * FPS))), 92 + (1 - ease((lt - 0.6) / 0.8)) * 80, 262, vis(lt, 0.6) * G)
    # Fortune 2000 counter
    tf = lc(k, 20, "Fortune", lead=0.3)
    a = vis(lt, tf) * G
    if a > 0:
        cnt = int(round(2000 * ease((lt - tf) / 1.4) / 10)) * 10
        put(c, text("FORTUNE", "bold", 18, RED, 5), 1260, 262 + (1 - a) * 10, a)
        put(c, text(f"{cnt:,}".replace(",", ""), "black", 96, INK), 1252, 284 + (1 - a) * 10, a)
        put(c, text("ORGANIZATIONS INCLUDED", "bold", 14, GREY, 3), 1260, 396, a)
    chips = [("Healthcare", "healthcare", "heart"), ("Pharma", "pharma", "flask"), ("Financial Services", "financial", "bank"), ("Manufacturing", "manufacturing", "factory"), ("Technology", "technology", "chip")]
    for j, (lab, ph, ic) in enumerate(chips):
        tk = lc(k, 21, ph, lead=0.25)
        callout(c, 1260, 440 + j * 86, j + 1, lab, None, 560, vis(lt, tk) * G, ico=ic)


@lru_cache(None)
def firm_img(nm):
    w, h = 560, 96
    im = box(w, h, 12, (255, 255, 255, 255), (234, 230, 232))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 18, 6, h - 18), fill=RED)
    tx = text(nm, "xbold", 38, INK)
    im.alpha_composite(tx, (int((w - tx.width) / 2), int(h / 2 - tx.height / 2)))
    return im


def scene6(c, t, lt, G):
    k = 6
    heading(c, lt, "RECOGNIZED BY INDUSTRY EXPERTS", "Recognized by Leading Research Firms", G)
    dur = SC[6]["end"] - SC[6]["start"]
    draw_card(c, clip("analysts", lt - 0.6, 1100, 590, min(1.0, 420 / max(1, (dur - 0.6) * FPS)), top=True), 92 + (1 - ease((lt - 0.6) / 0.8)) * 80, 262, vis(lt, 0.6) * G)
    put_scaled(c, node("trophy", 110), 1530, 320, max(0.05, back((lt - 1.0) / 0.6)), vis(lt, 1.0) * G)
    firms = [("Gartner", "Gartner"), ("IDC", "I D C"), ("Forrester", "Forrester"), ("Bloor Research", "Bloor")]
    for j, (nm, ph) in enumerate(firms):
        tk = lc(k, 24, ph, lead=0.25)
        a = vis(lt, tk) * G
        if a <= 0:
            continue
        im = firm_img(nm)
        sh, pad = shadow(im.width, im.height, 12, 16, 40, 8)
        dx = (1 - a) * 40
        put(c, sh, 1250 - pad + dx, 410 + j * 108 - pad, a)
        put(c, im, 1250 + dx, 410 + j * 108, a)
    tr = lc(k, 25, lead=0.2)
    a = vis(lt, tr) * G
    if a > 0:
        im = pill_img("ENTERPRISE DATA MANAGEMENT & AI", True, 16, 24, 50, 2)
        put(c, im, 1250 + (560 - im.width) / 2, 850 + (1 - a) * 14, a)


def scene7(c, t, lt, G):
    k = 7
    tg = lc(k, 27, lead=0.25)
    tb = lc(k, 28, lead=0.25)
    tcn = lc(k, 29, lead=0.25)
    tE = lc(k, 30, lead=0.3)
    tAg = lc(k, 30, "The Agentic", lead=0.2)
    if lt < tE + 0.6:
        g = G * (1 - eio((lt - tcn + 0.7) / 0.5))
        grey1 = ease((lt - tg) / 0.6)
        c1 = mix(INK, (205, 200, 202), grey1)
        c1r = mix(RED, (240, 190, 190), grey1)
        X = 150
        t0 = 0.4
        put(c, text("FROM", "bold", 22, RED, 4), X + 8, 232, vis(lt, t0) * g)
        put(c, text("DATA", "black", 104, c1), X, 256 + (1 - ease((lt - t0) / 0.7)) * 30, vis(lt, t0) * g)
        tt = lc(k, 26, "to intelligence", lead=0.2)
        put(c, text("TO", "bold", 22, RED, 4), X + 560, 232, vis(lt, tt) * g)
        put(c, text("INTELLIGENCE", "black", 104, c1r), X + 552, 256 + (1 - ease((lt - tt) / 0.7)) * 30, vis(lt, tt) * g)
        put(c, text("FROM", "bold", 22, RED, 4), X + 8, 452, vis(lt, tg) * g)
        put(c, text("GOVERNANCE", "black", 104, INK), X, 476 + (1 - ease((lt - tg) / 0.7)) * 30, vis(lt, tg) * g)
        ta = lc(k, 27, "to action", lead=0.2)
        put(c, text("TO", "bold", 22, RED, 4), X + 860, 452, vis(lt, ta) * g)
        put(c, text("ACTION", "black", 104, RED), X + 852, 476 + (1 - ease((lt - ta) / 0.7)) * 30, vis(lt, ta) * g)
        im = text("BUILDING THE AGENTIC FUTURE", "xbold", 46, INK, 3)
        put(c, im, X + 8, 690 + (1 - ease((lt - tb) / 0.6)) * 20, vis(lt, tb) * g)
        ln = int(620 * ease((lt - tb - 0.2) / 0.9))
        if ln > 0 and g > 0.4:
            ImageDraw.Draw(c).rectangle((X + 8, 762, X + 8 + ln, 765), fill=mix((250, 225, 225), RED, g))
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
        t1 = text("CONNECT WITH EXPERTS", "black", 54, INK, 2)
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
        t1 = text("SOLIX EMPOWER 2026", "black", 112, INK)
        put(c, t1, (W - t1.width) / 2, 345 + (1 - ease((l - 0.3) / 0.7)) * 30, vis(l, 0.3) * G)
        la = tAg - tE
        t2 = text("THE AGENTIC ENTERPRISE", "xbold", 70, RED, 2)
        put(c, t2, (W - t2.width) / 2, 485 + (1 - ease((l - la) / 0.7)) * 30, vis(l, la) * G)
        ln = int(260 * ease((l - la - 0.2) / 0.7))
        if ln > 0:
            ImageDraw.Draw(c).rectangle(((W - ln) // 2, 592, (W + ln) // 2, 595), fill=RED)
        t3 = text("Where Data, AI and Industry Come Together.", "med", 36, (70, 70, 76))
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
            d.polygon([(L + Sl, 0), (R + Sl, 0), (R - Sl, H), (L - Sl, H)], fill=BLUSH)
            d.polygon([(R - 70 + Sl, 0), (R + Sl, 0), (R - Sl, H), (R - 70 - Sl, H)], fill=RED)
            d.polygon([(R - 110 + Sl, 0), (R - 86 + Sl, 0), (R - 86 - Sl, H), (R - 110 - Sl, H)], fill=(240, 120, 120))
            d.polygon([(L + Sl, 0), (L + 40 + Sl, 0), (L + 40 - Sl, H), (L - Sl, H)], fill=(240, 150, 150))
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
    elif t >= s7["start"] and lt7 >= lc(7, 29, lead=0.25):
        show = 0.0
    elif t < cue(1) + 0.4:
        show = ease((t - cue(1) + 0.3) / 0.7)
    chrome(c, t, show)
    caption(c, t)
    wipe(c, t)
    if t < 0.4:
        c = Image.blend(Image.new("RGB", (W, H), (255, 255, 255)), c, t / 0.4)
    if t > TOTAL - 0.8:
        c = Image.blend(c, Image.new("RGB", (W, H), (255, 255, 255)), min(1, (t - (TOTAL - 0.8)) / 0.8))
    return c


def render_range(args):
    f0, f1, out = args
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    return out


def dump_timeline():
    segs = [{"i": k, "start": SC[k]["start"], "end": SC[k]["end"]} for k in range(8)]
    json.dump({"total": TOTAL, "segs": segs, "lines": [{"start": L["start"], "dur": L["dur"]} for L in LINES]}, open(f"{B}/timeline2.json", "w"), indent=1)


if __name__ == "__main__":
    mode = sys.argv[1]
    dump_timeline()
    if mode == "info":
        print("total", round(TOTAL, 2)); [print(k, round(s["start"], 2), round(s["end"], 2)) for k, s in enumerate(SC)]
    elif mode == "still":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"{B}/s2_{ts}.jpg", quality=90)
    elif mode == "video":
        from multiprocessing import Pool
        nf = int(TOTAL * FPS)
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        nparts = nw * 4
        edges = [nf * q // nparts for q in range(nparts + 1)]
        jobs = [(edges[q], edges[q + 1], f"{B}/p2_{q:02d}.mp4") for q in range(nparts)]
        with Pool(nw) as pool:
            for o in pool.imap(render_range, jobs):
                print("done", o, flush=True)
        with open(f"{B}/parts2.txt", "w") as f:
            for j in jobs:
                f.write(f"file '{j[2]}'\n")
