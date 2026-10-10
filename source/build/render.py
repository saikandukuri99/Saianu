# Solix Empower 2026 AV renderer: light coral "EAI Healthcare" style.
import json, os, re, sys, math, subprocess, glob
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

B = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(B)
A = f"{S}/assets"
CL = f"{S}/clips"
W, H, FPS = 1920, 1080, 30
RED = (228, 35, 40)
INK = (17, 17, 17)
GREY = (118, 118, 124)
LIGHT = (232, 230, 232)
FD = "/usr/share/fonts/opentype/inter/"
FONTS = {
    "black": FD + "InterDisplay-Black.otf",
    "xbold": FD + "InterDisplay-ExtraBold.otf",
    "bold": FD + "Inter-Bold.otf",
    "semi": FD + "Inter-SemiBold.otf",
    "med": FD + "Inter-Medium.otf",
    "reg": FD + "Inter-Regular.otf",
}

tl = json.load(open(f"{B}/timeline.json"))
TOTAL = tl["total"]
SEG = tl["segs"]

# TTS text (for cue timing) and on-screen caption text (script wording)
VO = open(f"{B}/vo.py").read()
VO_TEXT = re.findall(r'^"(.*)",$', VO, re.M)
CAP_TEXT = [
    "For more than two decades, Solix Technologies has helped enterprises transform their data into a strategic advantage, bringing together data management, governance, content services, and AI on a unified foundation.",
    "At the foundation is the Solix Enterprise Platform, combining the Common Data Platform, Enterprise Data Governance, and Enterprise Content Services to discover, manage, secure, govern, and activate enterprise information across environments.",
    "Building on this foundation, Solix Enterprise AI brings intelligence to enterprise data. Data Sense delivers semantic understanding. Data Ask enables natural-language interaction. Application Knowledge Graphs connect business context, while AI Warehouse and Solix Agentic help organizations build and activate governed AI.",
    "Solix also delivers comprehensive data lifecycle solutions, from application retirement and data preservation to SAP, Oracle, mainframe, email, file, database, and active archiving. Enterprises can reduce complexity, control costs, and preserve valuable information without costly migration.",
    "Purpose-built solutions extend this platform across industries. EAI Healthcare brings data and AI capabilities to healthcare, delivering Patient 360 and governed clinical intelligence, while EAI Pharma advances data and AI capabilities for pharmaceutical innovation, and Solix Academy helps organizations build the skills needed for an AI-ready enterprise.",
    "Today, Solix technology supports leading enterprises across industries, including organizations within the Fortune 2000. From healthcare and pharma to financial services, manufacturing, and technology, customers rely on Solix to solve complex data challenges at enterprise scale.",
    "Solix's innovation has also earned recognition from leading technology research and market intelligence organizations, including Gartner, IDC, Forrester, and Bloor Research, reinforcing its position in enterprise data management and AI.",
    "From data to intelligence, from governance to action, Solix is helping enterprises build the agentic future. Solix Empower 2026. The Agentic Enterprise.",
]


def cue(i, phrase, occ=0):
    """Approximate time (global) when `phrase` is spoken in VO segment i."""
    txt = VO_TEXT[i]
    pos = -1
    for _ in range(occ + 1):
        pos = txt.find(phrase, pos + 1)
    assert pos >= 0, (i, phrase)
    s = SEG[i]
    return s["vo_start"] + s["vo_dur"] * pos / len(txt)


def chunks(text, maxc=72):
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
    for c in out:  # split overly long chunks at word boundary
        while len(c) > maxc + 10:
            k = c.rfind(" ", 0, maxc)
            res.append(c[:k]); c = c[k + 1:]
        res.append(c)
    return res


CAPS = []
for i, txt in enumerate(CAP_TEXT):
    cs = chunks(txt)
    tot = sum(len(c) for c in cs)
    t = SEG[i]["vo_start"]
    for c in cs:
        d = SEG[i]["vo_dur"] * len(c) / tot
        CAPS.append((t, t + d, c, i))
        t += d


# ---------------------------------------------------------------- helpers
def ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


def vis(t, tin, tout=None, d=0.45, dout=0.3):
    a = ease((t - tin) / d)
    if tout is not None:
        a *= 1 - ease((t - tout) / dout)
    return a


@lru_cache(None)
def font(w, s):
    return ImageFont.truetype(FONTS[w], s)


@lru_cache(None)
def text(s, w, size, color=INK, track=0):
    f = font(w, size)
    asc, desc = f.getmetrics()
    if track:
        widths = [f.getlength(ch) for ch in s]
        tw = int(sum(widths) + track * (len(s) - 1)) + 4
    else:
        tw = int(f.getlength(s)) + 4
    im = Image.new("RGBA", (max(tw, 1), asc + desc + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track:
        x = 0
        for ch, wd in zip(s, widths):
            d.text((x, 0), ch, font=f, fill=color)
            x += wd + track
    else:
        d.text((0, 0), s, font=f, fill=color)
    return im


def fit_text(s, w, size, maxw, color=INK, track=0):
    while size > 20:
        im = text(s, w, size, color, track)
        if im.width <= maxw:
            return im
        size -= 2
    return text(s, w, size, color, track)


def put(c, im, x, y, a=1.0):
    if a <= 0.004 or im is None:
        return
    if a < 0.996:
        al = im.getchannel("A").point(lambda v: int(v * a))
        c.paste(im, (int(round(x)), int(round(y))), al)
    else:
        c.paste(im, (int(round(x)), int(round(y))), im)


@lru_cache(None)
def rounded_mask(w, h, r):
    ss = 3
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


@lru_cache(None)
def shadow(w, h, r=16, blur=24, alpha=60, dy=14):
    pad = blur * 2
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad + dy, pad + w, pad + h + dy), r, fill=(120, 20, 25, alpha))
    return im.filter(ImageFilter.GaussianBlur(blur)), pad


def box(w, h, r=14, fill=(255, 255, 255, 255), border=None, bw=2):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=border, width=bw if border else 0)
    return im


def card_img(im, w, h, r=14, border=True):
    im = im.convert("RGB").resize((w, h), Image.BILINEAR).convert("RGBA")
    im.putalpha(rounded_mask(w, h, r))
    if border:
        ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, outline=(225, 222, 224, 255), width=2)
    return im


def draw_card(c, im, x, y, a=1.0, shadow_on=True):
    if a <= 0.004:
        return
    if shadow_on:
        sh, pad = shadow(im.width, im.height)
        put(c, sh, x - pad, y - pad, a)
    put(c, im, x, y, a)


@lru_cache(None)
def asset(name):
    return Image.open(f"{A}/{name}.png").convert("RGBA")


@lru_cache(None)
def still_card(name, maxw, maxh):
    im = asset(name)
    sc = min(maxw / im.width, maxh / im.height)
    w, h = int(im.width * sc), int(im.height * sc)
    return card_img(im, w, h)


@lru_cache(None)
def clip_frames(name):
    return sorted(glob.glob(f"{CL}/{name}/*.jpg"))


def clip_card(name, lt, w, h, rate=1.0, r=14):
    fr = clip_frames(name)
    i = int(max(0, lt) * FPS * rate)
    n = len(fr)
    i = i % (2 * n - 2) if n > 1 else 0
    if i >= n:
        i = 2 * n - 2 - i  # ping-pong
    im = Image.open(fr[i])
    # cover-fit
    sc = max(w / im.width, h / im.height)
    nw, nh = int(im.width * sc + 0.5), int(im.height * sc + 0.5)
    im = im.resize((nw, nh), Image.BILINEAR)
    l, t = (nw - w) // 2, (nh - h) // 2
    im = im.crop((l, t, l + w, t + h)).convert("RGBA")
    im.putalpha(rounded_mask(w, h, r))
    return im


@lru_cache(None)
def logo(w):
    im = asset("logo")
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


@lru_cache(None)
def icon(w):
    return asset("icon").resize((w, w), Image.LANCZOS)


# ---------------------------------------------------------------- background
@lru_cache(None)
def background():
    BW, BH = W + 240, H + 160
    im = Image.new("RGB", (BW, BH), (255, 255, 255))
    # horizontal white->blush gradient
    g = Image.linear_gradient("L").rotate(90).resize((BW, BH))  # left 255 -> right 0
    blush = Image.new("RGB", (BW, BH), (247, 196, 194))
    im = Image.composite(im, blush, g.point(lambda v: int(255 * (v / 255) ** 0.55)))
    ov = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((BW - 900, -500, BW + 500, 700), fill=(240, 110, 108, 120))
    d.ellipse((BW - 1100, BH - 520, BW - 100, BH + 480), fill=(246, 150, 148, 70))
    d.ellipse((-400, BH - 300, 500, BH + 600), fill=(250, 210, 208, 90))
    ov = ov.filter(ImageFilter.GaussianBlur(160))
    im = Image.alpha_composite(im.convert("RGBA"), ov)
    # subtle grid
    gr = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gr)
    for x in range(0, BW, 96):
        gd.line((x, 0, x, BH), fill=(200, 120, 120, 14))
    for y in range(0, BH, 96):
        gd.line((0, y, BW, y), fill=(200, 120, 120, 14))
    im = Image.alpha_composite(im, gr)
    # big faint rings (like reference watermark circle)
    rg = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rg)
    cx, cy = BW - 380, BH - 260
    for rr, al in ((420, 40), (300, 30)):
        rd.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 255, 255, al))
    rg = rg.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(im, rg).convert("RGB")


def bg_frame(t):
    bg = background()
    ox = 120 + 110 * math.sin(t / 9.0)
    oy = 80 + 70 * math.cos(t / 11.0)
    return bg.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))


# ---------------------------------------------------------------- UI pieces
def heading(c, lt, kicker, title, G, x=90, y=96, tout=None, size=58, center=False):
    k = text(kicker, "bold", 19, RED, 4)
    ti = fit_text(title, "xbold", size, W - 2 * x)
    a1 = vis(lt, 0.0, tout) * G
    a2 = vis(lt, 0.12, tout) * G
    e1, e2 = ease(lt / 0.45), ease((lt - 0.12) / 0.5)
    if center:
        put(c, k, (W - k.width) / 2, y + (1 - e1) * 16, a1)
        put(c, ti, (W - ti.width) / 2, y + 30 + (1 - e2) * 26, a2)
    else:
        put(c, k, x - (1 - e1) * 30, y, a1)
        put(c, ti, x, y + 30 + (1 - e2) * 26, a2)


@lru_cache(None)
def callout_img(num, title, sub, w, active=False):
    h = 96 if sub else 74
    im = box(w, h, 12, (255, 255, 255, 255), (RED if active else (236, 232, 234)), 3 if active else 2)
    d = ImageDraw.Draw(im)
    d.ellipse((20, h / 2 - 17, 54, h / 2 + 17), fill=RED)
    n = text(str(num), "bold", 18, (255, 255, 255))
    im.alpha_composite(n, (int(37 - n.width / 2 + 2), int(h / 2 - 12)))
    t1 = fit_text(title, "bold", 24, w - 90, INK)
    if sub:
        im.alpha_composite(t1, (72, 18))
        t2 = fit_text(sub, "med", 17, w - 90, GREY)
        im.alpha_composite(t2, (72, 54))
    else:
        im.alpha_composite(t1, (72, int(h / 2 - 16)))
    return im


def callout(c, x, y, num, title, sub, w, a, active=False, slide=24):
    if a <= 0:
        return
    im = callout_img(num, title, sub, w, active)
    sh, pad = shadow(im.width, im.height, 12, 16, 40, 8)
    dx = (1 - a) * slide
    put(c, sh, x - pad + dx, y - pad, a)
    put(c, im, x + dx, y, a)


@lru_cache(None)
def pill_img(label, active, size=19, padx=26, h=48, track=2):
    t = text(label, "bold", size, (255, 255, 255) if active else (70, 70, 76), track)
    w = t.width + padx * 2
    im = box(w, h, h // 2, RED + (255,) if active else (255, 255, 255, 255), None if active else (230, 226, 228))
    im.alpha_composite(t, (padx, int(h / 2 - t.height / 2) + 1))
    return im


def caption(c, t, G=1.0):
    for (t0, t1, s, i) in CAPS:
        if t0 - 0.05 <= t < t1 + 0.05:
            if i == 7 and t >= cue(7, "Solix Empower"):
                return
            first = abs(t0 - SEG[i]["vo_start"]) < 0.01  # first chunk of a VO line
            a = vis(t, t0 - 0.05, None, 0.18) if first else 1.0
            pill(c, s, a * G)
            return


def pill(c, s, a, y=958, size=27):
    tx = fit_text(s, "semi", size, 1640, INK)
    w, h = tx.width + 60, 62
    x = (W - w) / 2
    bx = box(w, h, 12)
    sh, pad = shadow(w, h, 12, 16, 45, 8)
    put(c, sh, x - pad, y - pad, a)
    put(c, bx, x, y, a)
    put(c, tx, x + 30, y + (h - tx.height) / 2 + 1, a)


def chrome(c, t, show_logo=True):
    # eyebrow + top-right logo + progress line (reference layout)
    put(c, text("SOLIX EMPOWER 2026", "bold", 15, (110, 110, 116), 4), 92, 46, 1.0)
    if show_logo:
        put(c, logo(210), W - 92 - 210, 34, 1.0)
    p = t / TOTAL
    ImageDraw.Draw(c).rectangle((0, H - 6, int(W * p), H), fill=RED)


def switcher(c, lt, items, x, y, maxw, maxh, G, center=True, dur=0.35):
    """items: list of (t_on_local, kind, name). Slide-switch product cards."""
    cur = None
    for k, it in enumerate(items):
        if lt >= it[0]:
            cur = k
    if cur is None:
        return
    def get(it, l):
        _, kind, name = it[:3]
        if kind == "still":
            return still_card(name, maxw, maxh)
        ww, hh = it[3]
        return clip_card(name, l, ww, hh, it[4] if len(it) > 4 else 1.0)
    t_on = items[cur][0]
    p = ease((lt - t_on) / dur)
    im = get(items[cur], lt - t_on)
    ox = (maxw - im.width) / 2 if center else 0
    if cur > 0 and p < 1:
        prev = get(items[cur - 1], lt - items[cur - 1][0])
        pox = (maxw - prev.width) / 2 if center else 0
        draw_card(c, prev, x + pox - p * 90, y, (1 - p) * G)
    draw_card(c, im, x + ox + (1 - p) * 90, y + (1 - p) * 10, p * G if cur > 0 else vis(lt, t_on, None, 0.5) * G)
    return im


def bezier(p0, p1, p2, p3, n=40):
    pts = []
    for k in range(n + 1):
        u = k / n
        x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u ** 2 * p2[0] + u ** 3 * p3[0]
        y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u ** 2 * p2[1] + u ** 3 * p3[1]
        pts.append((x, y))
    return pts


# ---------------------------------------------------------------- scenes
def scene0(c, t, lt, G):
    s = SEG[0]
    # Phase A: logo reveal
    tA = 2.7
    a = vis(lt, 0.15, tA - 0.3, 0.7) * G
    if a > 0:
        sc = 0.9 + 0.1 * ease((lt - 0.15) / 1.2)
        lw = int(980 * sc)
        lg = logo(lw)
        put(c, lg, (W - lw) / 2, 380 - (lg.height - logo(980).height) / 2, a)
        k = text("SOLIX TECHNOLOGIES  ·  20+ YEARS OF ENTERPRISE DATA INNOVATION", "bold", 20, RED, 5)
        put(c, k, (W - k.width) / 2, 640, vis(lt, 0.8, tA - 0.3) * G)
        ln = int(560 * ease((lt - 0.6) / 1.0))
        if ln > 0 and lt < tA:
            ImageDraw.Draw(c).rectangle(((W - ln) // 2, 700, (W + ln) // 2, 703), fill=RED)
    # Phase B: 20+ years
    tB0, tB1 = tA, 7.2
    if tB0 - 0.1 <= lt < tB1 + 0.4:
        l = lt - tB0
        put(c, text("SOLIX TECHNOLOGIES", "bold", 19, RED, 4), 92 - (1 - ease(l / 0.4)) * 30, 300, vis(l, 0, tB1 - tB0) * G)
        big = text("20+", "black", 300, RED)
        put(c, big, 80, 320 + (1 - ease((l - 0.1) / 0.5)) * 40, vis(l, 0.1, tB1 - tB0) * G)
        put(c, text("YEARS OF ENTERPRISE", "xbold", 62, INK), 92, 660 + (1 - ease((l - 0.3) / 0.5)) * 30, vis(l, 0.3, tB1 - tB0) * G)
        put(c, text("DATA INNOVATION", "xbold", 62, INK), 92, 735 + (1 - ease((l - 0.4) / 0.5)) * 30, vis(l, 0.4, tB1 - tB0) * G)
        cards = [("clip", "cost", (720, 405), 1040, 230, 0.3), ("still", "found1", (560, 300), 1260, 560, 0.7), ("still", "datasense", (430, 240), 960, 650, 1.1)]
        for kind, name, (mw, mh), x, y, d0 in cards:
            aa = vis(l, d0, tB1 - tB0) * G
            if aa <= 0:
                continue
            im = clip_card(name, l, mw, mh) if kind == "clip" else still_card(name, mw, mh)
            draw_card(c, im, x + (1 - ease((l - d0) / 0.5)) * 80, y, aa)
    # Phase C: montage
    tC = tB1
    if lt >= tC - 0.1:
        l = lt - tC
        put(c, text("ONE UNIFIED FOUNDATION", "bold", 19, RED, 4), 92 - (1 - ease(l / 0.4)) * 30, 140, vis(l, 0) * G)
        words = [("Data Management", cue(0, "data management")), ("Governance", cue(0, "governance")), ("Content Services", cue(0, "content services")), ("AI", cue(0, "AI on"))]
        x = 92
        for wd, tw in words:
            ttl = s["vo_start"] + 0.0
            lw = tw - s["start"] - tC - 0.15
            act = l >= lw
            im = pill_img(wd.upper(), act, 22, 30, 58, 2)
            put(c, im, x, 190 + (1 - ease((l - lw) / 0.35)) * 20 if l >= lw else 190, (vis(l, lw, None, 0.35) if l >= lw else 0.0) * G)
            x += im.width + 16
        items = []
        seq = [("clip", "server", (1150, 600)), ("still", "found2"), ("still", "akg"), ("clip", "logos", (1150, 600)), ("still", "eaihc"), ("still", "agentic"), ("clip", "doctor", (1150, 600)), ("still", "dataask")]
        step = 0.78
        for k, it in enumerate(seq):
            tt = k * step + 0.1
            items.append((tt, it[0], it[1], it[2]) if it[0] == "clip" else (tt, it[0], it[1]))
        switcher(c, l, items, (W - 1150) / 2, 290, 1150, 600, G, dur=0.28)


def scene1(c, t, lt, G):
    s = SEG[1]
    heading(c, lt, "SOLIX ENTERPRISE FOUNDATION", "One Unified Enterprise Platform", G)
    t1 = cue(1, "Common Data") - s["start"] - 0.3
    t2 = cue(1, "Enterprise Data Governance") - s["start"] - 0.3
    t3 = cue(1, "Enterprise Content") - s["start"] - 0.3
    tv = cue(1, "discover") - s["start"] - 0.2
    pills = [("Common Data Platform", "Unified data foundation", t1, "found1"),
             ("Enterprise Data Governance", "Catalog · Knowledge graph · Enforcement", t2, "found2"),
             ("Enterprise Content Services", "Secure, AI-ready content", t3, "found3")]
    act = 0
    for k, p in enumerate(pills):
        if lt >= p[2]:
            act = k
    for k, (ti, sub, tk, _) in enumerate(pills):
        st = min(tk, 0.5 + 0.15 * k)
        callout(c, 92, 270 + k * 118, k + 1, ti, sub, 520, vis(lt, st) * G, active=(k == act and lt >= t1))
    verbs = ["DISCOVER", "MANAGE", "SECURE", "GOVERN", "ACTIVATE"]
    vt = [cue(1, v.lower()) - s["start"] - 0.15 for v in verbs]
    x, y = 92, 650
    for k, v in enumerate(verbs):
        im = pill_img(v, lt >= vt[k] and lt < vt[k] + 0.9 or (k == 4 and lt >= vt[k]), 16, 20, 42)
        if x + im.width > 92 + 540:
            x, y = 92, y + 56
        put(c, im, x, y + (1 - ease((lt - vt[k]) / 0.3)) * 14, vis(lt, vt[k], None, 0.3) * G)
        x += im.width + 12
    items = [(0.6, "still", "found1"), (max(t2, 0.6), "still", "found2"), (t3, "still", "found3")]
    switcher(c, lt, items, 680, 260, 1150, 640, G)


def hub(c, lt, G, cx=960, cy=560, labels=None, tout=None):
    ic = icon(200)
    a = vis(lt, 0.3, tout) * G
    # glow ring
    if a > 0:
        rg = ring_img()
        put(c, rg, cx - rg.width / 2, cy - rg.height / 2, a)
        sc = 0.7 + 0.3 * ease((lt - 0.3) / 0.6)
        im = icon(int(200 * sc))
        put(c, im, cx - im.width / 2, cy - im.height / 2, a)
    pos = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    d = ImageDraw.Draw(c)
    for k, (lab, sub) in enumerate(labels):
        sx, sy = pos[k]
        t0 = 0.9 + 0.35 * k
        p = ease((lt - t0) / 0.6)
        aa = vis(lt, t0, tout) * G
        if aa <= 0:
            continue
        bx = cx + sx * 520 - (420 if sx < 0 else 0)
        by = cy + sy * 150 - 48
        ex = cx + sx * 520
        pts = bezier((cx + sx * 100, cy + sy * 20), (cx + sx * 260, cy + sy * 20), (cx + sx * 300, cy + sy * 150), (ex, cy + sy * 150))
        n = max(2, int(len(pts) * p))
        col = tuple(int(255 + (v - 255) * aa) for v in RED)
        d.line(pts[:n], fill=col, width=3)
        hx, hy = pts[n - 1]
        d.ellipse((hx - 6, hy - 6, hx + 6, hy + 6), fill=col)
        callout(c, bx + (0 if sx < 0 else 10), by, k + 1, lab, sub, 410, aa)


@lru_cache(None)
def ring_img():
    im = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((60, 60, 460, 460), fill=(240, 90, 90, 50))
    d.ellipse((120, 120, 400, 400), fill=(240, 80, 80, 60))
    return im.filter(ImageFilter.GaussianBlur(30))


def scene2(c, t, lt, G):
    s = SEG[2]
    heading(c, lt, "ENTERPRISE AI", "Bringing Intelligence to Enterprise Data", G)
    names = [("Data Sense", "Data Sense", "datasense", "Semantic understanding", "UNDERSTAND"),
             ("Data Ask", "Data Ask", "dataask", "Natural-language interaction", "ANSWER"),
             ("Application Knowledge", "Application Knowledge Graphs", "akg", "Connected business context", "BUILD"),
             ("AI Warehouse", "AI Warehouse", "aiwh", "Build governed AI", "BUILD"),
             ("Solix Agentic", "Solix Agentic", "agentic", "Activate governed AI", "ACTIVATE")]
    ts = [cue(2, n[0]) - s["start"] - 0.25 for n in names]
    tB = ts[0] - 0.2
    hub(c, lt, G, labels=[("Understand", "Data Sense"), ("Answer", "Data Ask"), ("Build", "Knowledge Graphs · AI Warehouse"), ("Activate", "Solix Agentic")], tout=tB - 0.3)
    if lt < tB - 0.4:
        return
    l = lt
    # step chain
    act = 0
    for k, tk in enumerate(ts):
        if l >= tk:
            act = k
    x = 92
    for k, n in enumerate(names):
        im = pill_img(n[1].upper(), k == act, 16, 20, 44, 1)
        a = vis(l, tB + 0.08 * k) * G
        put(c, im, x, 236, a)
        if k < 4:
            ar = text("→", "bold", 24, RED)
            put(c, ar, x + im.width + 8, 241, a)
            x += im.width + 46
    items = [(ts[k] if k else tB + 0.1, "still", n[2]) for k, n in enumerate(names)]
    switcher(c, l, items, 92, 320, 1200, 590, G, center=False)
    # descriptor callout
    n = names[act]
    a = vis(l, ts[act] + 0.15, None, 0.35) * G
    callout(c, 1350, 360, act + 1, n[4].title(), n[3], 470, a)
    callout(c, 1350, 480, 0, n[1], "Solix Enterprise AI", 470, 0)


def scene3(c, t, lt, G):
    s = SEG[3]
    heading(c, lt, "DATA LIFECYCLE & ARCHIVING", "Retire. Preserve. Archive. Activate.", G)
    items = [("Application Retirement", "application retirement", "appret"), ("Data Preservation", "data preservation", "datapres"),
             ("SAP", "SAP", "sap"), ("Oracle", "Oracle", "oracle"), ("Mainframe", "mainframe", "mainframe"), ("Email", "email", "email"),
             ("File", "file", "file"), ("Database", "database", "database"), ("Active Archiving", "active archiving", "active")]
    ts = [cue(3, it[1]) - s["start"] - 0.2 for it in items]
    tben = cue(3, "Enterprises can") - s["start"] - 0.2
    act = 0
    for k, tk in enumerate(ts):
        if lt >= tk:
            act = k
    for k, (lab, _, _) in enumerate(items):
        is_act = (k == act and lt >= ts[0] and lt < tben) or (lt >= tben)
        im = row_img(k + 1, lab, is_act and lt < tben, done=(lt >= ts[k]))
        st = 0.3 + 0.06 * k
        put(c, im, 92 - (1 - ease((lt - st) / 0.4)) * 30, 252 + k * 70, vis(lt, st) * G)
    if lt < tben + 0.4:
        sw = [(0.4, "still", "appret")] + [(ts[k], "still", it[2]) for k, it in enumerate(items) if k > 0]
        g2 = G * (1 - ease((lt - tben) / 0.35))
        switcher(c, lt, sw, 580, 252, 1250, 620, g2, dur=0.25)
    if lt >= tben:
        l = lt - tben
        draw_card(c, clip_card("cost", l, 760, 428), 580 + (1 - ease(l / 0.5)) * 60, 252, vis(l, 0) * G)
        bens = [("Reduce complexity", "Retire legacy applications", "reduce complexity"), ("Control costs", "Lower infrastructure & licensing", "control costs"),
                ("Preserve information", "Without costly migration", "preserve valuable")]
        for k, (ti, sub, ph) in enumerate(bens):
            tk = cue(3, ph) - s["start"] - tben - 0.2
            callout(c, 1380, 252 + k * 120, k + 1, ti, sub, 450, vis(l, max(0.2, tk)) * G)


@lru_cache(None)
def row_img(n, label, active, done):
    w, h = 450, 58
    im = box(w, h, 10, RED + (255,) if active else (255, 255, 255, 255), None if active else (234, 230, 232))
    d = ImageDraw.Draw(im)
    num = text(f"{n:02d}", "bold", 17, (255, 255, 255) if active else RED, 1)
    im.alpha_composite(num, (20, int(h / 2 - num.height / 2) + 1))
    t = text(label, "bold", 22, (255, 255, 255) if active else INK)
    im.alpha_composite(t, (66, int(h / 2 - t.height / 2) + 1))
    return im


def scene4(c, t, lt, G):
    s = SEG[4]
    heading(c, lt, "INDUSTRY-SPECIFIC INNOVATION", "Purpose-Built for Every Industry", G)
    tH = cue(4, "E A I Healthcare") - s["start"] - 0.3
    tP = cue(4, "E A I Pharma") - s["start"] - 0.3
    tA = cue(4, "Solix Academy") - s["start"] - 0.3
    tabs = [("EAI HEALTHCARE", tH), ("EAI PHARMA", tP), ("SOLIX ACADEMY", tA)]
    act = 0 if lt < tP else (1 if lt < tA else 2)
    x = 92
    for k, (lab, _) in enumerate(tabs):
        im = pill_img(lab, k == act and lt >= tH - 0.2, 17, 24, 46, 2)
        put(c, im, x, 238, vis(lt, 0.4 + 0.1 * k) * G)
        x += im.width + 14
    # intro (before healthcare): three teaser cards
    if lt < tH + 0.3:
        g = G * (1 - ease((lt - tH) / 0.3))
        for k, (nm, sz) in enumerate([("doctor", (540, 360)), ("pharma", (540, 360)), ("academy", (540, 360))]):
            draw_card(c, clip_card(nm, lt, *sz), 92 + k * 590 + (1 - ease((lt - 0.5 - 0.15 * k) / 0.5)) * 60, 330, vis(lt, 0.5 + 0.15 * k) * g)
    if tH <= lt < tP + 0.4:
        l = lt - tH
        g = G * (1 - ease((lt - tP) / 0.35))
        draw_card(c, clip_card("doctor", l, 900, 326, 0.75), 92, 320 + (1 - ease(l / 0.5)) * 30, vis(l, 0) * g)
        draw_card(c, still_card("eaihc", 830, 470), 1010 + (1 - ease((l - 0.25) / 0.5)) * 60, 320, vis(l, 0.25) * g)
        tp = cue(4, "Patient 360") - s["start"] - tH - 0.3
        tg = cue(4, "governed clinical") - s["start"] - tH - 0.3
        callout(c, 92, 684, 1, "Patient 360", "One connected view of the patient", 440, vis(l, tp) * g)
        callout(c, 552, 684, 2, "Governed Clinical Intelligence", "Data & AI for healthcare", 440, vis(l, tg) * g)
        callout(c, 1010, 816, 3, "EAI Healthcare Platform", "Data and AI capabilities for healthcare", 830, vis(l, 0.8) * g)
    if tP <= lt < tA + 0.4:
        l = lt - tP
        g = G * (1 - ease((lt - tA) / 0.35))
        draw_card(c, clip_card("pharma", l, 1060, 560), 92 + (1 - ease(l / 0.5)) * 60, 320, vis(l, 0) * g)
        callout(c, 1200, 360, 1, "EAI Pharma", "Data and AI capabilities", 620, vis(l, 0.3) * g)
        callout(c, 1200, 480, 2, "Pharmaceutical Innovation", "Advancing research with governed AI", 620, vis(l, 0.9) * g)
    if lt >= tA:
        l = lt - tA
        draw_card(c, clip_card("academy", l, 1060, 560), 92 + (1 - ease(l / 0.5)) * 60, 320, vis(l, 0) * G)
        tsk = cue(4, "skills") - s["start"] - tA - 0.3
        callout(c, 1200, 360, 1, "Solix Academy", "solixacademy.com", 620, vis(l, 0.3) * G)
        callout(c, 1200, 480, 2, "Skills for an AI-Ready Enterprise", "Build the skills your teams need", 620, vis(l, max(0.8, tsk)) * G)


def scene5(c, t, lt, G):
    s = SEG[5]
    heading(c, lt, "TRUSTED BY GLOBAL ENTERPRISES", "Solving Complex Data Challenges at Enterprise Scale", G, size=54)
    dur = s["end"] - s["start"]
    draw_card(c, clip_card("logos", lt - 0.3, 1150, 649, min(1.0, 474 / ((dur - 0.3) * FPS))), 92 + (1 - ease((lt - 0.3) / 0.5)) * 50, 255, vis(lt, 0.3) * G)
    chips = [("Fortune 2000", "Fortune two"), ("Healthcare", "healthcare"), ("Pharma", "pharma"), ("Financial Services", "financial"), ("Manufacturing", "manufacturing"), ("Technology", "technology", 1)]
    for k, ch in enumerate(chips):
        tk = cue(5, ch[1], ch[2] if len(ch) > 2 else 0) - s["start"] - 0.25
        callout(c, 1290, 255 + k * 92, k + 1, ch[0], None, 540, vis(lt, tk) * G)


def scene6(c, t, lt, G):
    s = SEG[6]
    heading(c, lt, "RECOGNIZED BY INDUSTRY EXPERTS", "Recognized by Leading Research Firms", G)
    dur = s["end"] - s["start"]
    draw_card(c, clip_card("analysts", lt - 0.3, 1150, 587, min(1.0, 390 / ((dur - 0.3) * FPS))), 92 + (1 - ease((lt - 0.3) / 0.5)) * 50, 260, vis(lt, 0.3) * G)
    firms = [("Gartner", "Gartner"), ("IDC", "I D C"), ("Forrester", "Forrester"), ("Bloor Research", "Bloor")]
    for k, (nm, ph) in enumerate(firms):
        tk = cue(6, ph) - s["start"] - 0.25
        a = vis(lt, tk) * G
        if a <= 0:
            continue
        im = firm_img(nm)
        sh, pad = shadow(im.width, im.height, 12, 16, 40, 8)
        dx = (1 - a) * 24
        put(c, sh, 1290 - pad + dx, 260 + k * 118 - pad, a)
        put(c, im, 1290 + dx, 260 + k * 118, a)
    tr = cue(6, "reinforcing") - s["start"] - 0.2
    callout(c, 1290, 260 + 4 * 118 + 6, 0, "Enterprise Data Management & AI", "Analyst recognition", 540, 0)
    a = vis(lt, tr) * G
    if a > 0:
        im = pill_img("ENTERPRISE DATA MANAGEMENT & AI", True, 16, 24, 50, 2)
        put(c, im, 1290 + (540 - im.width) / 2, 260 + 4 * 118 + 14 + (1 - a) * 14, a)


@lru_cache(None)
def firm_img(nm):
    w, h = 540, 100
    im = box(w, h, 12, (255, 255, 255, 255), (234, 230, 232))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 18, 6, h - 18), fill=RED)
    t = text(nm, "xbold", 40, INK)
    im.alpha_composite(t, (int((w - t.width) / 2), int(h / 2 - t.height / 2)))
    return im


def scene7(c, t, lt, G):
    s = SEG[7]
    tg = cue(7, "from governance") - s["start"] - 0.2
    tE = cue(7, "Solix Empower") - s["start"] - 0.25
    tAg = cue(7, "The Agentic") - s["start"] - 0.2
    # phase A: from -> to statements (reference "FROM FRAGMENTED DATA / TO AN ...")
    if lt < tE + 0.4:
        g = G * (1 - ease((lt - tE) / 0.4))
        grey1 = ease((lt - tg) / 0.4)
        c1 = tuple(int(INK[i] + (200 - INK[i]) * grey1) for i in range(3))
        c1r = tuple(int(RED[i] + (236 - RED[i]) * grey1 * 0.75) for i in range(3))
        X = 150
        put(c, text("FROM", "bold", 22, RED, 4), X + 8, 232, vis(lt, 0.1) * g)
        put(c, text("DATA", "black", 104, c1), X, 256 + (1 - ease((lt - 0.15) / 0.5)) * 30, vis(lt, 0.15) * g)
        tt = cue(7, "to intelligence") - s["start"] - 0.2
        put(c, text("TO", "bold", 22, RED, 4), X + 560, 232, vis(lt, tt) * g)
        put(c, text("INTELLIGENCE", "black", 104, c1r), X + 552, 256 + (1 - ease((lt - tt) / 0.5)) * 30, vis(lt, tt) * g)
        put(c, text("FROM", "bold", 22, RED, 4), X + 8, 452, vis(lt, tg) * g)
        put(c, text("GOVERNANCE", "black", 104, INK), X, 476 + (1 - ease((lt - tg) / 0.5)) * 30, vis(lt, tg) * g)
        ta = cue(7, "to action") - s["start"] - 0.2
        put(c, text("TO", "bold", 22, RED, 4), X + 860, 452, vis(lt, ta) * g)
        put(c, text("ACTION", "black", 104, RED), X + 852, 476 + (1 - ease((lt - ta) / 0.5)) * 30, vis(lt, ta) * g)
        tb = cue(7, "build the agentic") - s["start"] - 0.3
        im = text("BUILDING THE AGENTIC FUTURE", "xbold", 46, INK, 3)
        put(c, im, X + 8, 690 + (1 - ease((lt - tb) / 0.5)) * 20, vis(lt, tb) * g)
        ln = int(560 * ease((lt - tb - 0.2) / 0.8))
        if ln > 0 and g > 0.5:
            ImageDraw.Draw(c).rectangle((X + 8, 762, X + 8 + ln, 765), fill=RED)
    # phase B: event lockup
    if lt >= tE:
        l = lt - tE
        lw = 700
        lg = logo(lw)
        put(c, lg, (W - lw) / 2, 150 + (1 - ease(l / 0.6)) * 30, vis(l, 0, None, 0.6) * G)
        t1 = text("SOLIX EMPOWER 2026", "black", 112, INK)
        put(c, t1, (W - t1.width) / 2, 345 + (1 - ease((l - 0.25) / 0.5)) * 30, vis(l, 0.25) * G)
        la = tAg - tE
        t2 = text("THE AGENTIC ENTERPRISE", "xbold", 70, RED, 2)
        put(c, t2, (W - t2.width) / 2, 485 + (1 - ease((l - la) / 0.5)) * 30, vis(l, la) * G)
        ln = int(240 * ease((l - la - 0.2) / 0.6))
        if ln > 0:
            ImageDraw.Draw(c).rectangle(((W - ln) // 2, 590, (W + ln) // 2, 593), fill=RED)
        t3 = text("Where Data, AI and Industry Come Together.", "med", 36, (70, 70, 76))
        put(c, t3, (W - t3.width) / 2, 622, vis(l, la + 0.6) * G)
        pa = vis(l, la + 1.2) * G
        if pa > 0:
            pill(c, "CONNECT WITH EXPERTS.   EXCHANGE IDEAS.", pa, y=800, size=26)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7]
XF = 0.35


def frame(t):
    c = bg_frame(t)
    for k, s in enumerate(SEG):
        if s["start"] <= t < s["end"] + XF:
            G = 1.0 - ease((t - s["end"]) / XF) if t >= s["end"] else 1.0
            SCENES[k](c, t, t - s["start"], G)
    lt0 = t
    s7 = SEG[7]
    show_logo = not (t < 2.7 or (t >= s7["start"] and t - s7["start"] >= cue(7, "Solix Empower") - s7["start"] - 0.25))
    chrome(c, t, show_logo)
    caption(c, t)
    # fade from/to white at very start/end
    if t < 0.25:
        c = Image.blend(Image.new("RGB", (W, H), (255, 255, 255)), c, t / 0.25)
    return c


def render_range(args):
    f0, f1, out = args
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"{B}/still_{ts}.jpg", quality=90)
    elif mode == "video":
        from multiprocessing import Pool
        nf = int(TOTAL * FPS)
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        nparts = nw * 3
        edges = [nf * k // nparts for k in range(nparts + 1)]
        jobs = [(edges[k], edges[k + 1], f"{B}/part_{k:02d}.mp4") for k in range(nparts)]
        with Pool(nw) as pool:
            for o in pool.imap(render_range, jobs):
                print("done", o, flush=True)
        with open(f"{B}/parts.txt", "w") as f:
            for j in jobs:
                f.write(f"file '{j[2]}'\n")
