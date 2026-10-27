# Solix XKG - booth loop (white edition)
# Same look as booth_loop.py: white background + live #0088cf/#ee2424 network, kinetic text column on the
# left, product screens from the XKG booth loop in a floating browser card, and the diagram scenes
# (why it fails, introducing XKG, how it works, one layer, outcomes, end card) rebuilt natively in white.
# Usage: python3 xkg_loop.py SRC.mp4 OUT.mp4 [--frames a:b] [--still t1,t2,...]
import math, subprocess, argparse
import numpy as np
import skia
import booth_loop as bl
from booth_loop import (col, font, clamp, prog, e_out3, e_outx, e_io, e_back, lerp, spaced, width_spaced,
                        wrap_words, parse_head, shadow, to_image, draw_bg, draw_logo, LOGO_ICON,
                        BLUE, RED, INDIGO, INK, BODY, MUTE, W, H, FPS, T, NF)

bl.CROP = (250, 118, 1420, 784)          # product window in the XKG source frame (clear of the watermark)
MONO = skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf")
TEAL = (0, 150, 136)
AMBER = (214, 140, 0)
GREEN = (30, 150, 80)
LINE = (222, 228, 238)
TINT = (244, 247, 251)
SAMP = skia.SamplingOptions(skia.CubicResampler.Mitchell())
_mono = {}


def mono(size):
    if size not in _mono:
        f = skia.Font(MONO, size)
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        _mono[size] = f
    return _mono[size]


def P(c, a=1.0, **kw):
    return skia.Paint(AntiAlias=True, Color=col(c, a), **kw)


def stroke(c, a=1.0, w=1.2):
    return skia.Paint(AntiAlias=True, Color=col(c, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w)


def rrect(x0, y0, x1, y1, r):
    return skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r)


def text(c, s, x, y, f, color, a=1.0, align="l"):
    w = f.measureText(s)
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    c.drawString(s, x, y, f, P(color, a))
    return w


# ------------------------------------------------------------------ storyboard
# kind: "card" = product screen from the source, else a native white diagram
SCENES = [
    dict(t0=0.0, t1=13.2, kind="card", src=(0.6, 12.9), nav=0, url="solix.com/ai-assistant", kick="THE QUESTION",
         beats=[(0.7, "One question. |Three applications.|", ""),
                (5.8, "The same supplier, |stored three different ways.|", ""),
                (10.4, "So the AI can't give an answer |you can trust.|", "")]),
    dict(t0=13.2, t1=22.2, kind="fails", nav=1, kick="WHY IT FAILS",
         beats=[(13.4, "Every application speaks |its own language.|", "Its own schema. Its own names. Its own definitions."),
                (19.0, "Every application speaks |its own language.|",
                 "An LLM can read each system. It can't know what they mean together.")]),
    dict(t0=22.2, t1=28.7, kind="intro", nav=2, kick="INTRODUCING",
         beats=[(22.7, "Solix |XKG|", "")],
         hsize=112, sub="Cross-Application Knowledge Graph", foot="A Solix Data Sense capability · Governed by Solix EDG"),
    dict(t0=28.7, t1=41.7, kind="how", nav=2, kick="HOW IT WORKS",
         beats=[(29.1, "|Resolve identity.|", "One record for each real-world thing."),
                (33.3, "|Certify meaning.|", "One definition for each business term."),
                (37.5, "|Answer in place.|", "Each system answers in its own schema.")]),
    dict(t0=41.7, t1=51.2, kind="card", src=(42.2, 51.0), nav=3, url="solix.com/data-sense/xkg/golden-records",
         kick="IN THE PRODUCT · GOLDEN RECORDS",
         beats=[(42.1, "It proposes. |Your stewards decide.|", ""),
                (46.5, "It proposes. |Your stewards decide.|", "Exact matches confirm. Name-only matches wait for a steward.")]),
    dict(t0=51.2, t1=60.7, kind="card", src=(51.7, 60.5), nav=3, url="solix.com/data-sense/xkg/business-terms",
         kick="IN THE PRODUCT · CERTIFIED TERMS",
         beats=[(51.6, "|Certified once.|", "One definition, one column in each application."),
                (56.2, "A steward adds |a missing binding.|", "Every answer uses it.")]),
    dict(t0=60.7, t1=68.5, kind="card", src=(61.0, 68.3), nav=3, url="solix.com/ai-assistant", kick="THE ANSWER",
         beats=[(61.1, "Same question. Now |one answer you can check.|", ""),
                (65.0, "Same question. Now |one answer you can check.|", "Each system's share shown. Retired systems included.")]),
    dict(t0=68.5, t1=77.5, kind="layer", nav=4, kick="ONE LAYER, MANY QUESTIONS",
         beats=[(68.7, "One layer. |Questions across| your applications.", "Not just suppliers: customers, materials and more."),
                (73.3, "One layer. |Questions across| your applications.",
                 "Start with one entity type. Add more when a question needs it.")]),
    dict(t0=77.5, t1=85.5, kind="outcomes", nav=4, kick="BUSINESS OUTCOMES",
         beats=[(77.7, "What it |unlocks.|", "Identity and meaning, decided once. Applied everywhere.")]),
]
END = (85.5, 89.3)                     # end card; 89.3-90 is the bare network = frame 0
NAV = ["The question", "Why it fails", "Solix XKG", "In the product", "What it unlocks"]
CTA = "Ask us for a live demo"
TR = 0.9
CARD_RUNS = [(0, 0), (4, 6)]           # consecutive card scenes share one card (wipes between them)
APPS = [("Oracle E-Business Suite", "RETIRED · ARCHIVED", "db"), ("SAP ERP", "LIVE", "server"),
        ("Oracle Fusion Cloud ERP", "LIVE", "cloud")]
RX0, RX1 = 690, 1830                   # right-hand stage


def scene_at(t):
    for k, s in enumerate(SCENES):
        if s["t0"] <= t < s["t1"]:
            return k
    return None


# ------------------------------------------------------------------ text column
TX, TW = 110, 540


def head_layout(s, size):
    f = font("xbold", size)
    return f, wrap_words(parse_head(s), f, TW)


def fit_head(s, size):
    while size > 50:
        f, lines = head_layout(s, size)
        if len(lines) <= 3:
            return f, lines
        size -= 4
    return head_layout(s, size)


def draw_head(c, t, s, y, t_in, t_out, size=66):
    f, lines = fit_head(s, size)
    lh = f.getSize() * 1.1
    out = e_io(prog(t, t_out, 0.5))
    if t < t_in or out >= 1:
        return y + len(lines) * lh
    oy = -34 * out
    a = 1 - out
    sp = f.measureText(" ")
    wi = 0
    spans = []
    for li, ln in enumerate(lines):
        bx = TX
        base = y + li * lh + f.getSize() * 0.8
        c.save()
        c.clipRect(skia.Rect(TX - 20, base - f.getSize() + oy, TX + TW + 300, base + f.getSize() * 0.3 + oy))
        for w, hi in ln:
            ww = f.measureText(w)
            wp = e_outx(prog(t, t_in + wi * 0.07, 0.85))
            c.drawString(w, bx, base + (1 - wp) * lh + oy, f, P(BLUE if hi else INDIGO, a))
            if hi:
                spans.append((bx, bx + ww, base))
            bx += ww + sp
            wi += 1
        c.restore()
    if spans:
        rows = {}
        for x0, x1, b in spans:
            r = rows.setdefault(b, [x0, x1])
            r[0], r[1] = min(r[0], x0), max(r[1], x1)
        u = e_io(prog(t, t_in + 0.25 + wi * 0.07, 0.6))
        acc = u * sum(v[1] - v[0] for v in rows.values())
        for b, (x0, x1) in sorted(rows.items()):
            seg = min(acc, x1 - x0)
            acc -= seg
            if seg > 0:
                yy = b + f.getSize() * 0.2 + oy
                c.drawRRect(rrect(x0, yy, x0 + seg, yy + max(5, f.getSize() * 0.085), 3), P(RED, a))
    return y + len(lines) * lh


def draw_lines(c, t, s, y, t_in, t_out, f, color, lh, maxw=TW - 20):
    if not s:
        return y
    lines = [[w for w, _ in ln] for ln in wrap_words([(w, 0) for w in s.split()], f, maxw)]
    out = e_io(prog(t, t_out, 0.45))
    if t >= t_in and out < 1:
        for li, ln in enumerate(lines):
            p = e_out3(prog(t, t_in + li * 0.1, 0.6))
            c.drawString(" ".join(ln), TX, y + li * lh + f.getSize() + (1 - p) * 16 - 26 * out, f,
                         P(color, p * (1 - out)))
    return y + len(lines) * lh


def segments(beats, idx, t_end):
    """Merge consecutive beats sharing the same element -> [(value, t_in, t_out)]."""
    out = []
    for i, b in enumerate(beats):
        v = b[idx]
        if out and out[-1][0] == v:
            continue
        out.append([v, b[0], None])
    for i in range(len(out)):
        out[i][2] = (out[i + 1][1] - 0.5) if i + 1 < len(out) else t_end
    return out


def draw_text(c, t):
    for sc in SCENES:
        if not (sc["t0"] - 0.2 <= t < sc["t1"] + 0.6):
            continue
        t_end = sc["t1"] - 0.6
        t_in = sc["beats"][0][0]
        y = 300
        # kicker
        ko = e_io(prog(t, t_end, 0.5))
        if t >= t_in - 0.3 and ko < 1:
            k = prog(t, t_in - 0.3, 0.5)
            a = 1 - ko
            c.drawRect(skia.Rect(TX, y + 12 - 30 * ko, TX + 46 * e_out3(k), y + 15.5 - 30 * ko), P(RED, a))
            fk, tr = font("semi", 20), 6.0
            while width_spaced(sc["kick"], fk, tr) > TW - 90 and tr > 2:
                tr -= 0.5
            spaced(c, sc["kick"], TX + 64, y + 22 - 30 * ko, fk, BLUE, tr, a, prog(t, t_in - 0.2, 0.7))
        y += 62
        heads = segments(sc["beats"], 1, t_end)
        bodies = segments(sc["beats"], 2, t_end)
        for hv, hi, ho in heads:
            if hi - 0.1 <= t < ho + 0.6:
                yb = draw_head(c, t, hv, y, hi, ho, sc.get("hsize", 66))
        yb = y + 0  # recompute layout height from the active head
        hv = next((h for h in heads if h[1] - 0.1 <= t), heads[0])
        for h in heads:
            if h[1] - 0.1 <= t:
                hv = h
        f, lines = fit_head(hv[0], sc.get("hsize", 66))
        yb = y + len(lines) * f.getSize() * 1.1
        if sc.get("sub"):
            yb = draw_lines(c, t, sc["sub"], yb + 2, t_in + 0.45, t_end, font("semi", 26), INDIGO, 36, TW + 40) + 10
        yb += 20
        for bv, bi, bo in bodies:
            if bv and bi <= t < bo + 0.5:
                draw_lines(c, t, bv, yb, bi + (0.55 if bi == t_in else 0.1), bo, font("reg", 27), BODY, 40)
        if sc.get("foot"):
            lines_b = wrap_words([(w, 0) for w in sc["beats"][0][2].split()], font("reg", 27), TW - 20)
            draw_lines(c, t, sc["foot"], yb + len(lines_b) * 40 + 18, t_in + 1.0, t_end, font("med", 19), MUTE, 28)


# ------------------------------------------------------------------ chrome
def chrome_alpha(t):
    return e_out3(prog(t, 0.3, 0.9)) * (1 - e_io(prog(t, END[0] - 0.3, 0.7)))


def draw_chrome(c, t):
    a = chrome_alpha(t)
    if a <= 0:
        return
    bp = stroke((180, 192, 210), a, 2)
    for (x, y, sx, sy) in [(44, 44, 1, 1), (W - 44, 44, -1, 1), (44, H - 44, 1, -1), (W - 44, H - 44, -1, -1)]:
        c.drawLine(x, y, x + sx * 30, y, bp)
        c.drawLine(x, y, x, y + sy * 30, bp)
    hh = 56
    draw_logo(c, W - 110 - 1797 / 394 * hh, 62, hh, 1, 1, 0, a, spin=False)
    k = scene_at(t)
    active = SCENES[k]["nav"] if k is not None else None
    grp = [s for s in SCENES if s["nav"] == active]
    pr = prog(t, grp[0]["t0"], grp[-1]["t1"] - grp[0]["t0"]) if grp else 0
    f, fa = font("med", 21), font("semi", 21)
    x, y = 110, 985
    for i, name in enumerate(NAV):
        on = i == active
        ff = fa if on else f
        tw = ff.measureText(name)
        if on:
            pl = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.5)
            c.drawCircle(x + 6, y - 7, 6 + 9 * pl, P(BLUE, a * 0.25 * (1 - pl)))
            c.drawCircle(x + 6, y - 7, 6, P(BLUE, a))
        else:
            c.drawCircle(x + 6, y - 7, 4.5, P(MUTE, a * 0.8))
        c.drawString(name, x + 22, y, ff, P(INDIGO if on else MUTE, a))
        if on:
            c.drawRRect(rrect(x + 22, y + 14, x + 22 + tw, y + 17, 1.5), P(LINE, a))
            sh = skia.GradientShader.MakeLinear([(x + 22, 0), (x + 22 + tw, 0)], [col(BLUE, a), col(RED, a)])
            c.drawRRect(rrect(x + 22, y + 14, x + 22 + tw * pr, y + 17, 1.5), skia.Paint(AntiAlias=True, Shader=sh))
        x += 22 + tw + 42
    fp = font("semi", 21)
    tw = fp.measureText(CTA)
    pw = tw + 70
    px, py = W - 110 - pw, 954
    c.drawRRect(rrect(px, py, px + pw, py + 46, 23), P(RED, a))
    pu = (t / 1.5) % 1.0
    c.drawCircle(px + 28, py + 23, 6 + 10 * pu, P((255, 255, 255), a * 0.45 * (1 - pu)))
    c.drawCircle(px + 28, py + 23, 6, P((255, 255, 255), a))
    c.drawString(CTA, px + 46, py + 30.5, fp, P((255, 255, 255), a))


# ------------------------------------------------------------------ product card
CX, CY, CW = 690, 168, 1140
CHR = 44
CH = CW * bl.CROP[3] / bl.CROP[2]


def src_time(sc, t):
    a, b = sc["src"]
    t0 = sc["t0"] + (0.15 if sc["t0"] > 0 else 0.4)
    r = (b - a) / ((sc["t1"] - 0.45) - t0)
    return clamp(a + (t - t0) * r, a, b - 1 / FPS)


def card_scenes(t):
    out = []
    for (k0, k1) in CARD_RUNS:
        for k in range(k0, k1 + 1):
            sc = SCENES[k]
            a = sc["t0"] - (TR / 2 if k > k0 else 0)
            b = sc["t1"] + (TR / 2 if k < k1 else 0.2)
            if a <= t < b:
                out.append(k)
    return out


def frame_needs(f):
    t = f / FPS
    return [int(round(src_time(SCENES[k], t) * FPS)) for k in card_scenes(t)]


def draw_card(c, t, src, now):
    ks = card_scenes(t)
    if not ks:
        return
    k0, k1 = next(r for r in CARD_RUNS if r[0] <= ks[0] <= r[1])
    tin = SCENES[k0]["t0"] + (0.3 if k0 == 0 else 0.0)
    tout = SCENES[k1]["t1"] - 0.5
    pin = e_outx(prog(t, tin, 1.2))
    pout = e_io(prog(t, tout, 0.75))
    alpha = clamp(prog(t, tin, 0.45)) * (1 - pout)
    if alpha <= 0:
        return
    r = skia.Rect(CX, CY, CX + CW, CY + CHR + CH)
    c.save()
    s = lerp(0.9, 1.0, pin) * lerp(1.0, 0.94, pout)
    ox = (1 - pin) * 380 + pout * 260
    fy = 4 * math.sin(2 * math.pi * t / 7.5)
    c.translate(r.centerX() + ox, r.centerY() + fy)
    c.scale(s, s)
    c.translate(-r.centerX(), -r.centerY())
    c.saveLayerAlpha(None, int(alpha * 255))
    shadow(c, r, 18, 1)
    rr = skia.RRect.MakeRectXY(r, 18, 18)
    c.drawRRect(rr, P((255, 255, 255)))
    c.save()
    c.clipRRect(rr, True)
    c.drawRect(skia.Rect(r.left(), r.top(), r.right(), r.top() + CHR), P((244, 246, 250)))
    for i, cc in enumerate([RED, (245, 179, 1), BLUE]):
        c.drawCircle(r.left() + 26 + i * 22, r.top() + CHR / 2, 6.5, P(cc))
    ub = skia.Rect(r.left() + 120, r.top() + 9, r.right() - 120, r.top() + CHR - 9)
    c.drawRRect(skia.RRect.MakeRectXY(ub, 13, 13), P((255, 255, 255)))
    c.drawRRect(skia.RRect.MakeRectXY(ub, 13, 13), stroke(LINE, 1, 1))
    lx, ly = ub.left() + 18, ub.centerY()
    c.drawArc(skia.Rect(lx - 4, ly - 8, lx + 4, ly), 180, 180, False, stroke((40, 160, 90), 1, 1.6))
    c.drawRRect(rrect(lx - 6, ly - 3, lx + 6, ly + 6, 2), P((40, 160, 90)))
    content = skia.Rect(r.left(), r.top() + CHR, r.right(), r.bottom())
    c.drawRect(content, P((11, 12, 26)))
    fu = font("med", 17)
    for k in ks:
        sc = SCENES[k]
        w = 1.0 if k == k0 else e_io(prog(t, sc["t0"] - TR / 2, TR))
        ua = 1.0 if k == k0 else clamp((w - 0.55) / 0.2)
        if k + 1 in ks:
            ua *= 1 - clamp((e_io(prog(t, SCENES[k + 1]["t0"] - TR / 2, TR)) - 0.2) / 0.2)
        text(c, sc["url"], ub.centerX(), ub.centerY() + 6, fu, (90, 96, 120), ua, "c")
        idx = int(round(src_time(sc, t) * FPS))
        img = to_image(src.frame(idx, now))
        z = 1.0 + 0.03 * prog(t, sc["t0"], sc["t1"] - sc["t0"])
        dst = skia.Rect(content.centerX() - content.width() * z / 2, content.top(),
                        content.centerX() + content.width() * z / 2, content.top() + content.height() * z)
        c.save()
        if w < 1:
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
        c.restore()
        if 0 < w < 1:
            edge = lerp(content.left() - 220, content.right() + 220, w)
            c.save()
            c.clipRect(content)
            for (off, cc, wd) in [(0, BLUE, 7), (12, RED, 4)]:
                c.drawLine(edge + 110 - off, content.top(), edge - 110 - off, content.bottom(),
                           skia.Paint(AntiAlias=True, StrokeWidth=wd, Color=col(cc)))
            c.drawLine(edge + 110, content.top(), edge - 110, content.bottom(),
                       skia.Paint(AntiAlias=True, StrokeWidth=40, Color=col(BLUE, 0.25),
                                  MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))
            c.restore()
        g = prog(t, sc["t0"] + 0.4, 1.4)
        if 0 < g < 1:
            gx = lerp(r.left() - 400, r.right() + 400, e_io(g))
            sh = skia.GradientShader.MakeLinear([(gx - 160, 0), (gx + 160, 0)],
                                                [col((255, 255, 255), 0), col((255, 255, 255), 0.1),
                                                 col((255, 255, 255), 0)], [0, 0.5, 1])
            c.drawRect(content, skia.Paint(Shader=sh))
    c.restore()
    c.drawRRect(rr, stroke((214, 220, 232), 1, 1.2))
    c.restore()
    c.restore()


# ------------------------------------------------------------------ native building blocks
def pop(c, cx, cy, k, fn, lift=30, s0=0.88):
    """Run fn() under a pop-in transform (k: 0..1 progress)."""
    if k <= 0:
        return
    e = e_back(clamp(k), 1.6)
    c.save()
    c.translate(cx, cy + (1 - e_out3(clamp(k))) * lift)
    sc = lerp(s0, 1, e)
    c.scale(sc, sc)
    c.translate(-cx, -cy)
    c.saveLayerAlpha(None, int(255 * clamp(k * 2.2)))
    fn()
    c.restore()
    c.restore()


def panel(c, x0, y0, x1, y1, accent=None, r=16, hl=0.0):
    rect = skia.Rect(x0, y0, x1, y1)
    shadow(c, rect, r, 0.75)
    rr = skia.RRect.MakeRectXY(rect, r, r)
    c.drawRRect(rr, P((255, 255, 255)))
    if accent:
        c.save()
        c.clipRRect(rr, True)
        c.drawRect(skia.Rect(x0, y0, x1, y0 + 5), P(accent))
        c.restore()
    c.drawRRect(rr, stroke(accent if (accent and hl > 0) else LINE, 1, 1.2 + 1.3 * hl))


def icon_box(c, x, y, s, cc, kind):
    ib = skia.Rect(x, y, x + s, y + s)
    sh = skia.GradientShader.MakeLinear([(x, y), (x + s, y + s)], [col(cc), col(INDIGO)])
    c.drawRRect(skia.RRect.MakeRectXY(ib, s * 0.25, s * 0.25), skia.Paint(AntiAlias=True, Shader=sh))
    glyph(c, kind, x + s / 2, y + s / 2, s / 52)


def glyph(c, kind, cx, cy, k=1.0):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.6 * k, Color=col((255, 255, 255)),
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    c.save()
    c.translate(cx, cy)
    c.scale(k, k)
    if kind == "db":
        c.drawOval(skia.Rect(-11, -14, 11, -6), p)
        c.drawArc(skia.Rect(-11, -5, 11, 3), 0, 180, False, p)
        c.drawArc(skia.Rect(-11, 4, 11, 12), 0, 180, False, p)
        c.drawLine(-11, -10, -11, 8, p)
        c.drawLine(11, -10, 11, 8, p)
    elif kind == "server":
        c.drawRRect(rrect(-12, -12, 12, -1, 3), p)
        c.drawRRect(rrect(-12, 2, 12, 13, 3), p)
        c.drawCircle(-6, -6.5, 1.6, P((255, 255, 255)))
        c.drawCircle(-6, 7.5, 1.6, P((255, 255, 255)))
    elif kind == "cloud":
        path = skia.Path()
        path.moveTo(-13, 8)
        path.cubicTo(-20, 8, -20, -3, -11, -3)
        path.cubicTo(-9, -13, 6, -14, 8, -4)
        path.cubicTo(18, -5, 18, 8, 10, 8)
        path.close()
        c.drawPath(path, p)
    elif kind == "diamond":
        path = skia.Path()
        path.moveTo(0, -13)
        path.lineTo(13, 0)
        path.lineTo(0, 13)
        path.lineTo(-13, 0)
        path.close()
        c.drawPath(path, p)
        c.drawCircle(0, 0, 3.5, p)
    elif kind == "award":
        c.drawCircle(0, -4, 8, p)
        c.drawLine(-5, 3, -7, 13, p)
        c.drawLine(5, 3, 7, 13, p)
    elif kind == "shield":
        path = skia.Path()
        path.moveTo(0, -13)
        path.lineTo(11, -8)
        path.lineTo(10, 3)
        path.quadTo(7, 10, 0, 13)
        path.quadTo(-7, 10, -10, 3)
        path.lineTo(-11, -8)
        path.close()
        c.drawPath(path, p)
        c.drawLine(-4, 0, -1, 4, p)
        c.drawLine(-1, 4, 5, -3, p)
    elif kind == "check":
        c.drawRRect(rrect(-11, -11, 11, 11, 4), p)
        c.drawLine(-5, 0, -1, 4, p)
        c.drawLine(-1, 4, 6, -4, p)
    elif kind == "trend":
        c.drawLine(-12, 8, -4, 0, p)
        c.drawLine(-4, 0, 1, 5, p)
        c.drawLine(1, 5, 12, -7, p)
        c.drawLine(12, -7, 5, -7, p)
        c.drawLine(12, -7, 12, 0, p)
    elif kind == "layers":
        for dy in (-6, 0, 6):
            path = skia.Path()
            path.moveTo(-12, dy)
            path.lineTo(0, dy - 6)
            path.lineTo(12, dy)
            path.lineTo(0, dy + 6)
            path.close()
            c.drawPath(path, p)
    elif kind == "truck":
        c.drawRRect(rrect(-13, -8, 3, 6, 2), p)
        c.drawRRect(rrect(3, -3, 12, 6, 2), p)
        c.drawCircle(-7, 9, 2.6, p)
        c.drawCircle(7, 9, 2.6, p)
    elif kind == "people":
        c.drawCircle(-4, -6, 4.5, p)
        c.drawArc(skia.Rect(-12, 1, 4, 15), 180, 180, False, p)
        c.drawCircle(7, -4, 3.5, p)
        c.drawArc(skia.Rect(2, 3, 14, 15), 200, 140, False, p)
    elif kind == "cube":
        path = skia.Path()
        path.moveTo(0, -13)
        path.lineTo(11, -6)
        path.lineTo(11, 7)
        path.lineTo(0, 13)
        path.lineTo(-11, 7)
        path.lineTo(-11, -6)
        path.close()
        c.drawPath(path, p)
        c.drawLine(-11, -6, 0, 0, p)
        c.drawLine(11, -6, 0, 0, p)
        c.drawLine(0, 0, 0, 13, p)
    c.restore()


def status_pill(c, x, y, s, a=1.0):
    f = font("bold", 12)
    tw = width_spaced(s, f, 1.8)
    cc = AMBER if "RETIRED" in s else GREEN
    c.drawRRect(rrect(x, y, x + tw + 18, y + 22, 6), P(cc, 0.1 * a))
    c.drawRRect(rrect(x, y, x + tw + 18, y + 22, 6), stroke(cc, 0.6 * a, 1))
    spaced(c, s, x + 9, y + 15.5, f, cc, 1.8, a)
    return tw + 18


def chip(c, x, y, s, cc, kind="check", a=1.0, h=40, f=None, fill=False):
    f = f or font("semi", 18)
    tw = f.measureText(s)
    w = tw + 62
    rr = rrect(x, y, x + w, y + h, h / 2)
    c.drawRRect(rr, P(cc if fill else (255, 255, 255), a))
    c.drawRRect(rr, stroke(cc, 0.55 * a, 1.4))
    ix, iy = x + 22, y + h / 2
    ic = (255, 255, 255) if fill else cc
    c.drawCircle(ix, iy, 10, P(cc if not fill else (255, 255, 255), (0.14 if not fill else 0.25) * a))
    ip = stroke(ic, a, 2.2)
    ip.setStrokeCap(skia.Paint.kRound_Cap)
    if kind == "check":
        c.drawLine(ix - 4.5, iy, ix - 1, iy + 3.5, ip)
        c.drawLine(ix - 1, iy + 3.5, ix + 5, iy - 3.5, ip)
    elif kind == "x":
        c.drawLine(ix - 4, iy - 4, ix + 4, iy + 4, ip)
        c.drawLine(ix + 4, iy - 4, ix - 4, iy + 4, ip)
    elif kind == "lock":
        c.drawRRect(rrect(ix - 5, iy - 1, ix + 5, iy + 6, 1.5), P(ic, a))
        c.drawArc(skia.Rect(ix - 3.5, iy - 7, ix + 3.5, iy + 1), 180, 180, False, stroke(ic, a, 1.8))
    c.drawString(s, x + 42, y + h / 2 + f.getSize() * 0.36, f, P((255, 255, 255) if fill else INK, a))
    return w


def stage_alpha(sc, t, lead=0.0):
    """Native scenes: in with the scene, out over the last 0.55 s."""
    return 1 - e_io(prog(t, sc["t1"] - 0.45, 0.45))


# ------------------------------------------------------------------ 2. why it fails
def draw_fails(c, t, sc):
    oa = stage_alpha(sc, t)
    if oa <= 0:
        return
    vals = [("AP_SUPPLIERS · AP_INVOICES_ALL", "ZENTARA COMPONENTS LLC", "INVOICE_AMOUNT"),
            ("LFA1 · RBKP", "Zentara Components", "RBKP.RMWWR"),
            ("HZ_PARTIES · AP_INVOICES_ALL", "Zentara Comp. Ltd", "INVOICE_AMOUNT")]
    labels = ["ITS OWN SCHEMA", "ITS NAME FOR THE SUPPLIER", "ITS COLUMN FOR SPEND"]
    cw, gap, y0, ch = 352, 42, 232, 396
    c.saveLayerAlpha(None, int(oa * 255))
    c.translate(0, -24 * (1 - oa))
    for i, (name, st, ic) in enumerate(APPS):
        x0 = RX0 + i * (cw + gap)
        k = prog(t, 13.5 + i * 0.35, 0.7)

        def body(i=i, x0=x0, name=name, st=st, ic=ic):
            panel(c, x0, y0, x0 + cw, y0 + ch, accent=[BLUE, RED, BLUE][i])
            icon_box(c, x0 + 22, y0 + 26, 46, [TEAL, BLUE, INDIGO][i], ic)
            text(c, name, x0 + 82, y0 + 48, font("bold", 21 if len(name) > 18 else 23), INDIGO)
            status_pill(c, x0 + 82, y0 + 58, st)
            for j in range(3):
                rk = prog(t, 14.4 + i * 0.25 + j * 0.3, 0.5)
                if rk <= 0:
                    continue
                yy = y0 + 118 + j * 92
                spaced(c, labels[j], x0 + 22, yy, font("semi", 12), MUTE, 2.4, rk)
                bx = skia.Rect(x0 + 22, yy + 12, x0 + cw - 22, yy + 54)
                warn = j > 0 and t > 15.6 + j * 0.4
                c.drawRRect(skia.RRect.MakeRectXY(bx, 8, 8), P(TINT, rk))
                c.drawRRect(skia.RRect.MakeRectXY(bx, 8, 8), stroke(AMBER if warn else LINE, rk, 1.2 + 0.4 * warn))
                c.drawString(vals[i][j], bx.left() + 14, bx.centerY() + 6, mono(16 if len(vals[i][j]) < 26 else 14),
                             P(INDIGO, rk))
                if warn:
                    text(c, "?", bx.right() - 14, bx.centerY() + 7, font("bold", 19), AMBER, rk, "r")
        pop(c, x0 + cw / 2, y0 + ch / 2, k, body)
    # "not equal" markers between cards
    for i in range(2):
        k = prog(t, 15.4 + i * 0.25, 0.5)
        if k > 0:
            cx = RX0 + (i + 1) * (cw + gap) - gap / 2
            cy = y0 + ch / 2
            e = e_back(k, 2.2)
            c.drawCircle(cx, cy, 22 * e, P((255, 255, 255)))
            c.drawCircle(cx, cy, 22 * e, stroke(RED, clamp(k * 2), 2.2))
            pp = stroke(RED, clamp(k * 2), 2.4)
            c.drawLine(cx - 8 * e, cy - 4 * e, cx + 8 * e, cy - 4 * e, pp)
            c.drawLine(cx - 8 * e, cy + 4 * e, cx + 8 * e, cy + 4 * e, pp)
            c.drawLine(cx + 5 * e, cy - 11 * e, cx - 5 * e, cy + 11 * e, pp)
    # failure chips
    fails = ["Same supplier counted twice", "The wrong amount column added up", "A system that quietly returns nothing"]
    f = font("semi", 17)
    for i, s in enumerate(fails):
        k = prog(t, 18.6 + i * 0.22, 0.5)
        if k <= 0:
            continue
        x0 = RX0 + i * (cw + gap)
        w = f.measureText(s) + 62
        pop(c, x0 + cw / 2, y0 + ch + 56, k,
            lambda x0=x0, w=w, s=s: chip(c, x0 + (cw - w) / 2, y0 + ch + 36, s, RED, "x", 1, 42, f))
    c.restore()


# ------------------------------------------------------------------ 3. introducing XKG
def draw_intro(c, t, sc):
    oa = stage_alpha(sc, t)
    if oa <= 0:
        return
    c.saveLayerAlpha(None, int(oa * 255))
    cx = (RX0 + RX1) / 2
    hub = skia.Rect(RX0 + 60, 250, RX1 - 60, 350)
    k = prog(t, 23.2, 0.8)

    def hubf():
        panel(c, hub.left(), hub.top(), hub.right(), hub.bottom(), r=50)
        sh = skia.GradientShader.MakeLinear([(hub.left(), 0), (hub.right(), 0)], [col(BLUE, 0.08), col(RED, 0.06)])
        c.drawRRect(skia.RRect.MakeRectXY(hub, 50, 50), skia.Paint(AntiAlias=True, Shader=sh))
        c.drawImageRect(LOGO_ICON, skia.Rect(hub.left() + 26, hub.top() + 22, hub.left() + 82, hub.top() + 78), SAMP)
        text(c, "XKG", hub.left() + 98, hub.centerY() + 11, font("black", 30), INDIGO)
        text(c, "Identity and meaning, decided once", hub.right() - 34, hub.centerY() + 9, font("bold", 24), BLUE,
             1, "r")
    pop(c, hub.centerX(), hub.centerY(), k, hubf)
    # three apps, each governed by its own AKG
    cw, gap = 340, 60
    x0 = cx - (3 * cw + 2 * gap) / 2
    for i, (name, st, ic) in enumerate(APPS):
        bx = x0 + i * (cw + gap)
        ax = bx + cw / 2
        lk = e_io(prog(t, 24.4 + i * 0.2, 0.8))
        if lk > 0:
            path = skia.Path()
            path.moveTo(ax, hub.bottom())
            path.cubicTo(ax, hub.bottom() + 90, ax, 470, ax, 560)
            meas = skia.PathMeasure(path, False)
            L = meas.getLength()
            seg = skia.Path()
            meas.getSegment(0, L * lk, seg, True)
            c.drawPath(seg, stroke(BLUE if i != 1 else RED, 0.8, 2.4))
            if lk >= 1:
                ph = ((t - 25.4) / 1.2 + i * 0.33) % 1.0
                pos = meas.getPosTan(L * (1 - ph))[0]
                c.drawCircle(pos.x(), pos.y(), 5, P(BLUE if i != 1 else RED))
                c.drawCircle(pos.x(), pos.y(), 11, P(BLUE if i != 1 else RED, 0.18))
        kk = prog(t, 23.9 + i * 0.25, 0.7)

        def appf(bx=bx, name=name, st=st, ic=ic, i=i):
            panel(c, bx, 560, bx + cw, 700, accent=[BLUE, RED, BLUE][i])
            icon_box(c, bx + 22, 585, 44, [TEAL, BLUE, INDIGO][i], ic)
            text(c, name, bx + 80, 614, font("bold", 20 if len(name) > 18 else 22), INDIGO)
            gk = prog(t, 25.0 + i * 0.25, 0.5)
            if gk > 0:
                chip(c, bx + 22, 646 - 6 * (1 - gk), "Governed by its AKG", GREEN, "check", gk, 30, font("semi", 14))
        pop(c, bx + cw / 2, 630, kk, appf)
    c.restore()


# ------------------------------------------------------------------ 4. how it works
STEPS = [("Resolve identity", BLUE, 29.1), ("Certify meaning", RED, 33.3), ("Answer in place", INDIGO, 37.5)]
CONTRIB = [412000, 288500, 175000]
APPEARS = ["ZENTARA COMPONENTS LLC", "Zentara Components", "Zentara Comp. Ltd"]
SPENDCOL = ["INVOICE_AMOUNT", "RBKP.RMWWR", "INVOICE_AMOUNT"]


def money(v):
    return "${:,.0f}".format(v)


def draw_how(c, t, sc):
    oa = stage_alpha(sc, t)
    if oa <= 0:
        return
    c.saveLayerAlpha(None, int(oa * 255))
    ent = prog(t, 28.8, 0.7)
    # stepper
    f = font("semi", 19)
    ws = [f.measureText(s) + 74 for s, _, _ in STEPS]
    x = (RX0 + RX1) / 2 - (sum(ws) + 2 * 16) / 2
    for i, (s, cc, ts) in enumerate(STEPS):
        on = t >= ts
        k = prog(t, 28.8 + i * 0.12, 0.5)
        a = clamp(k * 2)
        rr = rrect(x, 172, x + ws[i], 216, 22)
        c.drawRRect(rr, P(cc if on else (255, 255, 255), a * (0.1 if on else 1)))
        c.drawRRect(rr, stroke(cc if on else LINE, a, 1.6 if on else 1.2))
        c.drawCircle(x + 24, 194, 13, P(cc if on else (232, 236, 243), a))
        text(c, str(i + 1), x + 24, 200.5, font("bold", 15), (255, 255, 255) if on else MUTE, a, "c")
        text(c, s, x + 46, 201, f, INDIGO if on else MUTE, a)
        x += ws[i] + 16
    # XKG layer panel
    L0, L1 = RX0, RX1
    ly0, ly1 = 240, 470
    lp = e_out3(ent)
    c.drawRRect(rrect(L0, ly0, L1, ly1, 18), P((240, 247, 253), lp))
    dash = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.4, Color=col(BLUE, 0.45 * lp),
                      PathEffect=skia.DashPathEffect.Make([7, 6], 0))
    c.drawRRect(rrect(L0, ly0, L1, ly1, 18), dash)
    spaced(c, "THE XKG LAYER · GOVERNED BY SOLIX EDG", L0 + 26, ly0 + 32, font("semi", 13), BLUE, 3, lp)
    s2 = "LINEAGE & AUDIT ON EVERY VALUE"
    spaced(c, s2, L1 - 26 - width_spaced(s2, font("semi", 13), 3), ly0 + 32, font("semi", 13), MUTE, 3, lp)
    # app cards
    cw, gap = 360, 30
    cy0, cy1 = 590, 850
    tops = []
    for i, (name, st, ic) in enumerate(APPS):
        bx = RX0 + i * (cw + gap)
        tops.append(bx + cw / 2)
        k = prog(t, 29.0 + i * 0.15, 0.7)

        def appf(bx=bx, name=name, st=st, ic=ic, i=i):
            panel(c, bx, cy0, bx + cw, cy1)
            icon_box(c, bx + 20, cy0 + 20, 40, [TEAL, BLUE, INDIGO][i], ic)
            text(c, name, bx + 72, cy0 + 47, font("bold", 19 if len(name) > 18 else 21), INDIGO)
            rows = [("Appears as", APPEARS[i], BLUE, 30.4 + i * 0.15), ("Spend column", SPENDCOL[i], RED, 34.6 + i * 0.15)]
            for j, (lab, v, cc, th) in enumerate(rows):
                yy = cy0 + 82 + j * 56
                text(c, lab, bx + 20, yy + 26, font("reg", 15), BODY)
                bxr = skia.Rect(bx + 128, yy + 2, bx + cw - 18, yy + 42)
                h = e_out3(prog(t, th, 0.5))
                c.drawRRect(skia.RRect.MakeRectXY(bxr, 8, 8), P(TINT))
                c.drawRRect(skia.RRect.MakeRectXY(bxr, 8, 8), stroke(cc if h > 0 else LINE, 1, 1.2 + 0.8 * h))
                c.drawString(v, bxr.left() + 12, bxr.centerY() + 5.5, mono(14.5), P(INDIGO))
            text(c, "Contributes", bx + 20, cy1 - 26, font("reg", 15), BODY)
            cp = e_io(prog(t, 37.9 + i * 0.2, 1.8))
            if cp > 0:
                text(c, money(round(CONTRIB[i] * cp / 100) * 100 if cp < 1 else CONTRIB[i]), bx + 128, cy1 - 22,
                     font("xbold", 30), INDIGO, clamp(cp * 4))
        pop(c, bx + cw / 2, (cy0 + cy1) / 2, k, appf)
    # top nodes
    gx0, gx1 = RX0 + 24, RX0 + 404
    tx0, tx1 = RX1 - 380, RX1 - 36
    rx0, rx1 = (RX0 + RX1) / 2 - 150, (RX0 + RX1) / 2 + 150
    ny0, ny1 = 300, 400

    def node(x0, x1, cc, kind, lab, val, k, sub, sk):
        def f_():
            panel(c, x0, ny0, x1, ny1, accent=cc, hl=1.0)
            icon_box(c, x0 + 20, ny0 + 25, 50, cc, kind)
            spaced(c, lab, x0 + 86, ny0 + 40, font("semi", 13), cc, 3)
            text(c, val, x0 + 86, ny0 + 78, font("xbold", 26), INDIGO)
        pop(c, (x0 + x1) / 2, (ny0 + ny1) / 2, k, f_)
        if sk > 0:
            fs = font("semi", 15)
            w = fs.measureText(sub) + 62
            chip(c, (x0 + x1) / 2 - w / 2, ny1 + 14 + 6 * (1 - e_out3(sk)), sub, cc, "check", clamp(sk * 2), 32, fs)

    # links (drawn before nodes so they sit behind)
    def link(xa, ya, xb, yb, cc, k, up=False, ph0=0.0):
        if k <= 0:
            return
        path = skia.Path()
        path.moveTo(xa, ya)
        my = (ya + yb) / 2
        path.cubicTo(xa, my, xb, my, xb, yb)
        meas = skia.PathMeasure(path, False)
        L = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L * e_io(k), seg, True)
        c.drawPath(seg, stroke(cc, 0.75, 2.4))
        if k >= 1:
            ph = ((t * 0.8) + ph0) % 1.0
            pos = meas.getPosTan(L * ((1 - ph) if up else ph))[0]
            c.drawCircle(pos.x(), pos.y(), 4.5, P(cc))
            c.drawCircle(pos.x(), pos.y(), 10, P(cc, 0.18))

    for i, x in enumerate(tops):
        link((gx0 + gx1) / 2, ny1 + 46, x - 40, cy0, BLUE, prog(t, 30.0 + i * 0.12, 0.9), False, i * 0.3)
        link((tx0 + tx1) / 2, ny1 + 46, x + 40, cy0, RED, prog(t, 34.2 + i * 0.12, 0.9), False, i * 0.3 + 0.15)
        link(x, cy0, (rx0 + rx1) / 2, ny1 + 46, INDIGO, prog(t, 38.0 + i * 0.12, 0.9), False, i * 0.3 + 0.5)
    node(gx0, gx1, BLUE, "diamond", "GOLDEN RECORD", "Zentara Components", prog(t, 29.4, 0.7),
         "Confirmed by a steward", prog(t, 31.4, 0.5))
    node(tx0, tx1, RED, "award", "CERTIFIED TERM", "Spend", prog(t, 33.6, 0.7), "One column per system",
         prog(t, 35.6, 0.5))
    # governed result
    rk = prog(t, 38.4, 0.7)

    def resf():
        panel(c, rx0, ny0, rx1, ny1, accent=INDIGO, hl=1.0)
        cp = e_io(prog(t, 38.6, 1.6))
        v = round(875500 * cp / 10) * 10 if cp < 1 else 875500
        text(c, money(v), (rx0 + rx1) / 2, ny0 + 58, font("xbold", 40), INDIGO, 1, "c")
        if cp >= 1:
            chip(c, (rx0 + rx1) / 2 - 56, ny0 + 66, "Verified", GREEN, "check", prog(t, 40.3, 0.4), 26, font("semi", 13))
    pop(c, (rx0 + rx1) / 2, (ny0 + ny1) / 2, rk, resf)
    gk = prog(t, 40.5, 0.45)
    if gk > 0:
        fs = font("semi", 15)
        w = fs.measureText("Governed result") + 62
        chip(c, (rx0 + rx1) / 2 - w / 2, ny1 + 14 + 6 * (1 - e_out3(gk)), "Governed result", INDIGO, "lock",
             clamp(gk * 2), 32, fs, fill=True)
    c.restore()


# ------------------------------------------------------------------ 8. one layer, many questions
ENTITIES = [("Suppliers", "truck", "What did we spend with Zentara Components?", "SUMMARY", "One total, with each system's share"),
            ("Customers", "people", "List the open invoices for this customer.", "DETAIL", "Every row tagged with its source system"),
            ("Materials", "cube", "Which suppliers sell us this material?", "DETAIL", "Matched across systems, codes and all")]


def draw_layer(c, t, sc):
    oa = stage_alpha(sc, t)
    if oa <= 0:
        return
    c.saveLayerAlpha(None, int(oa * 255))
    cw, gap, y0, ch = 360, 30, 250, 330
    for i, (name, ic, q, lab, v) in enumerate(ENTITIES):
        bx = RX0 + i * (cw + gap)
        k = prog(t, 68.9 + i * 0.55, 0.7)

        def f_(bx=bx, name=name, ic=ic, q=q, lab=lab, v=v, i=i):
            cc = [BLUE, RED, INDIGO][i]
            panel(c, bx, y0, bx + cw, y0 + ch, accent=cc)
            icon_box(c, bx + 22, y0 + 26, 46, cc, ic)
            text(c, name, bx + 82, y0 + 58, font("bold", 26), INDIGO)
            # question bubble
            fq = font("med", 17)
            lines = [" ".join(w for w, _ in ln) for ln in wrap_words([(w, 0) for w in q.split()], fq, cw - 80)]
            bh = 24 + 24 * len(lines)
            bb = skia.Rect(bx + 22, y0 + 98, bx + cw - 22, y0 + 98 + bh)
            sh = skia.GradientShader.MakeLinear([(bb.left(), 0), (bb.right(), 0)], [col(BLUE), col(INDIGO)])
            c.drawRRect(skia.RRect.MakeRectXY(bb, 12, 12), skia.Paint(AntiAlias=True, Shader=sh))
            for li, ln in enumerate(lines):
                c.drawString(ln, bb.left() + 16, bb.top() + 30 + li * 24, fq, P((255, 255, 255)))
            spaced(c, lab, bx + 22, y0 + ch - 66, font("semi", 12), cc, 2.6)
            fv = font("reg", 17)
            for li, ln in enumerate(wrap_words([(w, 0) for w in v.split()], fv, cw - 44)):
                c.drawString(" ".join(w for w, _ in ln), bx + 22, y0 + ch - 40 + li * 22, fv, P(BODY))
        pop(c, bx + cw / 2, y0 + ch / 2, k, f_)
    pills = ["No federated join", "Certified business terms", "Results merged by identity"]
    f = font("semi", 18)
    ws = [f.measureText(s) + 62 for s in pills]
    x = (RX0 + RX1) / 2 - (sum(ws) + 2 * 18) / 2
    for i, s in enumerate(pills):
        k = prog(t, 71.7 + i * 0.25, 0.5)
        pop(c, x + ws[i] / 2, 650, k, lambda x=x, s=s: chip(c, x, 630, s, GREEN, "check", 1, 42, f))
        x += ws[i] + 18
    # connector rail from the cards to the pills
    rk = e_io(prog(t, 71.4, 0.8))
    if rk > 0:
        c.drawLine((RX0 + RX1) / 2 - 520 * rk, 605, (RX0 + RX1) / 2 + 520 * rk, 605, stroke(LINE, 1, 2))
    c.restore()


# ------------------------------------------------------------------ 9. outcomes
TILES = [("shield", "Governance that holds across applications", "A control that applies in one application applies across the layer."),
         ("check", "Answers that show their sources", "Which systems contributed, and how far to trust the result."),
         ("trend", "Cross-application insight from governed meaning", "Application results combined through XKG."),
         ("layers", "A governed build when you need one", "The same agreement, generated as a dbt project.")]


def draw_outcomes(c, t, sc):
    oa = stage_alpha(sc, t)
    if oa <= 0:
        return
    c.saveLayerAlpha(None, int(oa * 255))
    tw, th, g = 555, 196, 30
    for i, (ic, title, sub) in enumerate(TILES):
        bx = RX0 + (i % 2) * (tw + g)
        by = 250 + (i // 2) * (th + g)
        k = prog(t, 78.0 + i * 0.3, 0.7)
        cyc = (t - 80.0) / 1.1
        hl = 1.0 if (cyc >= 0 and int(cyc) % 4 == i) else 0.0

        def f_(bx=bx, by=by, ic=ic, title=title, sub=sub, i=i, hl=hl):
            cc = [BLUE, RED, RED, BLUE][i]
            panel(c, bx, by, bx + tw, by + th, accent=cc, hl=hl)
            icon_box(c, bx + 26, by + 30, 54, cc, ic)
            ft = font("bold", 25)
            yy = by + 52
            for ln in wrap_words([(w, 0) for w in title.split()], ft, tw - 130):
                c.drawString(" ".join(w for w, _ in ln), bx + 100, yy, ft, P(INDIGO))
                yy += 32
            fs = font("reg", 18)
            yy += 6
            for ln in wrap_words([(w, 0) for w in sub.split()], fs, tw - 130):
                c.drawString(" ".join(w for w, _ in ln), bx + 100, yy, fs, P(BODY))
                yy += 25
        pop(c, bx + tw / 2, by + th / 2, k, f_)
    c.restore()


# ------------------------------------------------------------------ 10. end card
def draw_end(c, t):
    if not (END[0] - 0.1 <= t < END[1] + 0.2):
        return
    out = e_io(prog(t, END[1] - 0.6, 0.6))
    oa = 1 - out
    cx = W / 2
    # mark: Solix icon + "Solix XKG" (Solix in indigo, XKG in brand blue)
    k = prog(t, END[0] + 0.1, 0.8)
    fx = font("black", 124)
    sw = fx.measureText("Solix ")
    xw = sw + fx.measureText("XKG")
    ih = 130
    tot = ih + 26 + xw
    x0 = cx - tot / 2
    y0 = 300
    if k > 0:
        e = e_back(k, 2.2)
        c.save()
        c.translate(x0 + ih / 2, y0 + ih / 2)
        c.scale(e, e)
        c.rotate(-120 * (1 - e_out3(k)))
        c.drawImageRect(LOGO_ICON, skia.Rect(-ih / 2, -ih / 2, ih / 2, ih / 2), SAMP, skia.Paint(Alphaf=oa * clamp(k * 3)))
        c.restore()
        wk = e_outx(prog(t, END[0] + 0.4, 0.8))
        c.save()
        c.clipRect(skia.Rect(x0 + ih + 10, y0 - 20, x0 + ih + 26 + xw * wk + 10, y0 + ih + 20))
        bx = x0 + ih + 26 - (1 - wk) * 60
        c.drawString("Solix", bx, y0 + ih * 0.86, fx, P(INDIGO, oa))
        c.drawString("XKG", bx + sw, y0 + ih * 0.86, fx, P(BLUE, oa))
        c.restore()
    sk = prog(t, END[0] + 0.8, 0.7)
    if sk > 0:
        txt = "CROSS-APPLICATION KNOWLEDGE GRAPH"
        ff = font("bold", 26)
        tw = width_spaced(txt, ff, 8)
        spaced(c, txt, cx - tw / 2, 520, ff, BLUE, 8, oa, sk, 0.02)
        g = e_out3(sk)
        for side in (-1, 1):
            xa = cx + side * (tw / 2 + 28)
            sh = skia.GradientShader.MakeLinear([(xa, 0), (xa + side * 140, 0)], [col(RED, oa), col(RED, 0)])
            c.drawRect(skia.Rect(min(xa, xa + side * 140 * g), 509, max(xa, xa + side * 140 * g), 512),
                       skia.Paint(Shader=sh))
    # tagline
    fh = font("xbold", 54)
    words = parse_head("One shared meaning across |every application.|")
    sp = fh.measureText(" ")
    tot = sum(fh.measureText(w) for w, _ in words) + sp * (len(words) - 1)
    bx = cx - tot / 2
    base = 625
    hx0 = hx1 = None
    c.save()
    c.clipRect(skia.Rect(0, base - 60, W, base + 18))
    for i, (w, hi) in enumerate(words):
        ww = fh.measureText(w)
        wp = e_outx(prog(t, END[0] + 1.0 + i * 0.07, 0.8))
        c.drawString(w, bx, base + (1 - wp) * 64, fh, P(BLUE if hi else INDIGO, oa))
        if hi:
            hx0 = bx if hx0 is None else hx0
            hx1 = bx + ww
        bx += ww + sp
    c.restore()
    u = e_io(prog(t, END[0] + 1.6, 0.5))
    if u > 0:
        c.drawRRect(rrect(hx0, base + 13, hx0 + (hx1 - hx0) * u, base + 19, 3), P(RED, oa))
    # CTA + footer
    ck = prog(t, END[0] + 1.8, 0.5)
    if ck > 0:
        fp = font("semi", 24)
        tw = fp.measureText(CTA)
        pw = tw + 80
        e = e_back(ck, 2.0)
        c.save()
        c.translate(cx, 712)
        c.scale(e, e)
        a = oa * clamp(ck * 2)
        c.drawRRect(rrect(-pw / 2, -27, pw / 2, 27, 27), P(RED, a))
        pu = (t / 1.5) % 1.0
        c.drawCircle(-pw / 2 + 30, 0, 7 + 10 * pu, P((255, 255, 255), a * 0.45 * (1 - pu)))
        c.drawCircle(-pw / 2 + 30, 0, 7, P((255, 255, 255), a))
        c.drawString(CTA, -pw / 2 + 52, 8.5, fp, P((255, 255, 255), a))
        c.restore()
    fk = prog(t, END[0] + 2.2, 0.6)
    if fk > 0:
        text(c, "A Solix Data Sense capability  ·  Governed by Solix EDG", cx, 800 + 10 * (1 - e_out3(fk)),
             font("med", 21), MUTE, oa * fk, "c")


# ------------------------------------------------------------------ frame
NATIVE = {"fails": draw_fails, "intro": draw_intro, "how": draw_how, "layer": draw_layer, "outcomes": draw_outcomes}


def render(c, t, src, now):
    draw_bg(c, t)
    draw_card(c, t, src, now)
    for sc in SCENES:
        if sc["kind"] in NATIVE and sc["t0"] - 0.3 <= t < sc["t1"] + 0.1:
            NATIVE[sc["kind"]](c, t, sc)
    draw_text(c, t)
    draw_end(c, t)
    draw_chrome(c, t)


# The source answer screen briefly shows an older "Nothing copied" chip while the chips fade in and out.
# Replace that chip with the approved "AKG-governed" chip, matched to each frame's fade level.
CHIP = (690, 612, 210, 52)        # chip slot, in source-crop coordinates
COVERED = (130, 620, 288, 36)     # neighbouring "Covered" chip, used to measure the fade
BGREF = (910, 622, 120, 30)       # chip-free card area, used to measure background dimming
CHIP_SRC = (65.4, 68.7)


def grab(path, t):
    x, y, w, h = bl.CROP
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", path, "-frames:v", "1", "-vf",
                          f"crop={w}:{h}:{x}:{y}", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 4).astype(np.float32)


def reg(a, r):
    x, y, w, h = r
    return a[y:y + h, x:x + w]


class PatchedSource(bl.Source):
    def __init__(self, path, need):
        super().__init__(path, need)
        self.akg = grab(path, 66.5)        # steady frame with the AKG-governed chip
        self.empty = grab(path, 64.5)      # same screen before the chips appear
        self.done = {}

    def frame(self, idx, now):
        arr = super().frame(idx, now)
        if not (CHIP_SRC[0] * FPS <= idx <= CHIP_SRC[1] * FPS):
            return arr
        if idx not in self.done:
            f = arr.astype(np.float32)
            m, m0, m1 = (reg(f, COVERED)[..., :3].mean(), reg(self.empty, COVERED)[..., :3].mean(),
                         reg(self.akg, COVERED)[..., :3].mean())
            a = clamp((m - m0) / (m1 - m0)) if m1 > m0 else 1.0
            s = reg(f, BGREF)[..., :3].mean() / max(1e-3, reg(self.empty, BGREF)[..., :3].mean())
            # chips slide up while fading in: follow the vertical offset of the neighbouring chip row
            cx, cy, cw, ch = COVERED
            pf = f[cy - 20:cy + ch + 20, cx:cx + cw, :3].mean(axis=(1, 2))
            pa = self.akg[cy - 20:cy + ch + 20, cx:cx + cw, :3].mean(axis=(1, 2))
            pf, pa = pf - pf.mean(), pa - pa.mean()
            dy = 0
            if pf.std() > 0.5:
                dy = max(range(-14, 15), key=lambda d: float(np.dot(pf[20:-20], pa[20 - d:len(pa) - 20 - d])))
            x, y, w, h = CHIP
            akg = self.akg[y - dy:y - dy + h, x:x + w]
            patch = reg(self.empty, CHIP) * s * (1 - a) + akg * a
            out = arr.copy()
            out[y:y + h, x:x + w, :3] = np.clip(patch[..., :3], 0, 255).astype(np.uint8)
            self.done = {idx: out}
        return self.done[idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--frames", default=f"0:{NF}")
    ap.add_argument("--still", default="")
    a = ap.parse_args()
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    if a.still:
        fr = sorted(int(round(float(x) * FPS)) for x in a.still.split(","))
        src = PatchedSource(a.src, [frame_needs(f) for f in fr])
        from PIL import Image
        for n, f in enumerate(fr):
            render(c, f / FPS, src, n)
            Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).save(
                f"{a.out}_{f / FPS:06.2f}.png")
        return
    f0, f1 = map(int, a.frames.split(":"))
    src = PatchedSource(a.src, [frame_needs(f) for f in range(f0, f1)])
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                            "-pix_fmt", "yuv420p", "-x264-params", "keyint=60", a.out], stdin=subprocess.PIPE)
    for n, f in enumerate(range(f0, f1)):
        render(c, f / FPS, src, n)
        enc.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        if n % 150 == 0:
            print(f"{a.out}: {n}/{f1 - f0}", flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
