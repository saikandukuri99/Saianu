# Storyboard: Head (hook + problem) / Body (SAP, Oracle, policy) / Tail (result, AI-ready, logo).
# Every cue is derived from the voice-over timing in cues.py.
import math
from lib import *
from cues import cue, line_t, OFF, VO, TITLE

# --------------------------------------------------------------------------- shared helpers
def ctext(c, st, x, yc, kind="i", weight="Bold", size=40, color=WHITE, a=1.0, track=0, anchor="l"):
    """draw text with the middle of its capital letters on yc (true optical centring inside boxes)"""
    asc = font(kind, weight, size).getmetrics()[0]
    c.text(st, x, yc - asc + .363 * size, kind, weight, size, color, a, track=track, anchor=anchor)

def kicker(c, label, x, y, t0, t, color=SKY, bar=RED, anchor="l"):
    a = E(pr(t, t0, .45))
    w = tw(label, "i", "Bold", 22, 7)
    if anchor == "c": x = x - (w + 40) / 2
    c.blit(BAR(max(2, int(28 * E(pr(t, t0, .5)))), 5, bar), x, y + 11, a)
    c.text(label, x + 44, y, "i", "Bold", 22, color, a, track=7)

def words(c, items, x, y, size, times, t, kind="d", weight="Bold", anchor="l", gap=.27, rise=22):
    """items: (text, color, chip_color|None). each word eases up at its time; chips sweep in behind with roomy padding."""
    f = font(kind, weight, size); sp = size * gap; padc = int(size * .5)
    ws = [f.getlength(it[0]) + (2 * padc if it[2] else 0) for it in items]
    tot = sum(ws) + sp * (len(items) - 1)
    cx = x - tot / 2 if anchor == "c" else x
    asc = f.getmetrics()[0]; ch = int(size * 1.62)
    for it, w, ti in zip(items, ws, times):
        a = E(pr(t, ti, .30)); dy = (1 - a) * rise
        if it[2]:
            sw = E(pr(t, ti + .05, .36)); cw = int(w * sw) // 6 * 6
            yc = y + asc - .363 * size + .07 * size + dy             # middle of the capitals (nudged for descenders) = middle of the chip
            if cw > 4: c.blit(BAR(cw, ch, it[2]), cx, yc - ch / 2, a, 1.0)
            c.text(it[0], cx + padc, y + dy, kind, weight, size, WF, a)
        else:
            c.text(it[0], cx, y + dy, kind, weight, size, it[1], a)
        cx += w + sp
    return tot

def pill(c, x, y, w, h, label, icon, col, a, t_on=None, t=0, size=32):
    """pill card with coloured icon disc"""
    on = 1.0 if t_on is None else E(pr(t, t_on, .35))
    outline = mix(BLUE, col, on) + (int(lerp(70, 220, on)),)
    c.card(x, y, w, h, a, outline=outline, r=h // 2, fill=CARD + (int(lerp(190, 235, on)),))
    c.blit(CIRCLE(h - 20, col + (int(lerp(60, 255, on)),)), x + h / 2, y + h / 2, a, 1.0, True)
    c.icon(icon, x + h / 2, y + h / 2, (h - 20) * .52, WF, a)
    ctext(c, label, x + h + 6, y + h / 2, "i", "Bold", size, mix(TXT, WHITE, on), a)

def mono(c, s, x, y, size, color, a=1.0, w="Regular", anchor="l"):
    c.text(s, x, y, "m", w, size, color, a, anchor=anchor)

# --------------------------------------------------------------------------- scene windows (absolute seconds)
_V = lambda i: VO[i]["start"] - .07                    # scene windows follow the voice-over, so pacing changes move the visuals with it
SC = {"T": (0.0, OFF), "A": (OFF, _V(1)), "B": (_V(1), _V(2)), "C": (_V(2), _V(3)), "E": (_V(3), _V(4)), "D": (_V(4), _V(5)),
      "F": (_V(5), _V(6)), "K": (_V(6), _V(7)), "DA": (_V(7), VO[9]["start"] - .03)}
SC["G"] = (SC["DA"][1], SC["DA"][1] + 2.0)                # "The result?" holds 2 s
SC["H"] = (SC["G"][1], _V(11)); SC["I"] = (_V(11), _V(12)); SC["J"] = (_V(12), round(VO[12]["end"] + 6.9, 2))
CUTS = []          # hard cuts: no transition effects

# --------------------------------------------------------------------------- T  video title card (music only, before the voice-over starts)
def tri_underline(c, x, y, w, k, h=8):
    """underline drawn left to right in three colour segments (red, blue, teal)"""
    uw = int(w * k)
    if uw <= 6: return
    seg = w / 3.0
    for i, col in enumerate((RED, BLUE, TEAL)):
        a0 = seg * i; a1 = min(uw, seg * (i + 1) + (6 if i < 2 else 0))
        if a1 - a0 > 3: c.blit(BAR(int(a1 - a0), h, col), x + a0, y, 1)

def family_pill(c, label, col, x, y, size, a, h=None):
    h = h or int(size * 1.7); w = int(tw(label, "d", "Bold", size) + size * 1.1)
    c.blit(BAR(w, h, col), x - w / 2, y - h / 2, a)
    ctext(c, label, x, y, "d", "Bold", size, WF, a, anchor="c")
    return w

def scene_T(c, t):
    kicker(c, "SOLIXEMPOWER 2026", 960, 250, .15, t, anchor="c")
    size = 100; hw = [("Enterprise", WHITE, None), ("Application", WHITE, None), ("Archiving", WHITE, None)]
    words(c, hw, 960, 330, size, [.35, .6, .85], t, anchor="c")
    f = font("d", "Bold", size); wd = sum(f.getlength(i[0]) for i in hw) + size * .27 * 2
    tri_underline(c, 960 - wd / 2, 490, wd, E(pr(t, 1.4, .7)), 8)
    items = [("Oracle Applications", RED, 2.1), ("SAP", BLUE, 2.5), ("Mainframe", TEAL, 2.9)]
    ws = [int(tw(l, "d", "Bold", 40) + 44) for l, _, _ in items]
    tot_ = 70 + 18 + sum(ws) + 18 * 2; x = 960 - tot_ / 2
    a_ = E(pr(t, 1.9, .4)); ctext(c, "for", x + 22, 618 + (1 - a_) * 10, "i", "Medium", 40, TXT, a_, anchor="c"); x += 70 + 18
    for (l, col, ti), w in zip(items, ws):
        a = E(pr(t, ti, .35)); yy = 618 + (1 - a) * 14
        c.blit(BAR(w, 70, col), x, yy - 35, a); ctext(c, l, x + w / 2, yy, "d", "Bold", 40, WF, a, anchor="c"); x += w + 18

# --------------------------------------------------------------------------- A  (HEAD) opening headline
def scene_A(c, t):
    kicker(c, "SOLIXEMPOWER 2026", 960, 215, .15 + OFF, t, anchor="c")
    L1 = [("Enterprise", WHITE, None), ("Applications", WHITE, None)]
    T1 = [cue(0, "Enterprise") - .1, cue(0, "applications") - .1]
    words(c, L1, 960, 270, 104, T1, t, anchor="c")
    L2 = [("run", WHITE, None), ("the", WHITE, None), ("business.", WHITE, None)]
    T2 = [cue(0, "run") - .2, cue(0, "the business") - .2, cue(0, "business") - .2]
    tot = words(c, L2, 960, 405, 104, T2, t, anchor="c")
    tri_underline(c, 960 - tot / 2, 545, tot, E(pr(t, T2[2] + .45, .6)), 9)
    fams = [("Oracle Applications", RED, 480, cue(0, "Oracle") - .15, ["E-Business Suite", "PeopleSoft", "JD Edwards", "Siebel"]),
            ("SAP", BLUE, 1040, cue(0, "S A P") - .15, ["SAP ECC", "SAP S/4HANA"]),
            ("Mainframe", TEAL, 1520, cue(0, "mainframes") - .15, ["IBM zSeries", "Mainframe applications"])]
    for label, col, cx, ti, chips in fams:
        a = E(pr(t, ti, .4)); family_pill(c, label, col, cx, 655 + (1 - a) * 16, 38, a)
        cw = [int(tw(n_, "i", "Bold", 19, 2) + 44) for n_ in chips]
        rows = [(0, 1), (2, 3)] if len(chips) == 4 else [tuple(range(len(chips)))]
        for ri, row in enumerate(rows):
            tot_ = sum(cw[k] for k in row) + 12 * (len(row) - 1); x = cx - tot_ / 2
            for k in row:
                ca = E(pr(t, ti + .35 + (ri * 2 + (k - row[0])) * .12, .3)); yy = 745 + ri * 64 + (1 - ca) * 10
                c.card(x, yy - 24, cw[k], 48, ca, outline=col + (200,), fill=CARD + (255,), r=24)
                ctext(c, chips[k], x + cw[k] / 2, yy, "i", "Bold", 19, TXT, ca, track=2, anchor="c"); x += cw[k] + 12

# --------------------------------------------------------------------------- B  (HEAD) the challenge
def db_rows(c, x, y, w, n, t, t_from, t_to, hot_color, row_h=25, pitch=33, label_size=15, active_first=True, shrink=None):
    """stack of tablespace slabs, one per fiscal year, sliding in over [t_from, t_to]."""
    for i in range(n):
        ti = lerp(t_from, t_to, i / max(1, n - 1)); a = E(pr(t, ti, .35))
        if a <= 0: continue
        yy = y + i * pitch + (1 - a) * -16
        act = (i == 0 and active_first)
        fill = (14, 96, 168, 255) if act else ROWF3 + (255,)
        out = BLUE + (230,) if act else ROWO3 + (255,)
        c.card(x, yy, w, row_h, a, fill=fill, outline=out, r=8)
        yr = 2026 - i
        mono(c, f"FY{yr}", x + 14, yy + 4, label_size, WF if act else DIM, a, "Bold")
        mono(c, "ACTIVE" if act else "INACTIVE", x + w - 14, yy + 4, label_size, WF if act else INACT, a, "Regular", "r")

def scene_B(c, t):
    kicker(c, "THE CHALLENGE", 120, 205, line_t(1)[0] - .1, t)
    T0 = cue(1, "years") - .1
    words(c, [("Years", WHITE, None), ("of", WHITE, None)], 120, 232, 92, [T0, T0 + .12], t)
    words(c, [("inactive", WHITE, RED), ("data", WHITE, None)], 120, 378, 92, [cue(1, "inactive") - .15, cue(1, "data") - .05], t)
    items = [("Bloating databases", "db", cue(1, "bloating")), ("Slowing performance", "clock", cue(1, "slowing")), ("Driving up costs", "dollar", cue(1, "driving up"))]
    for i, (lab, ic, ti) in enumerate(items):
        a = E(pr(t, ti - .12, .4)); yy = 538 + i * 90
        pill(c, 120 + (1 - a) * -40, yy, 600, 72, lab, ic, RED, a, ti, t, 34)
    # planning a move to the cloud
    tm = cue(1, "planning a move") - .1; a = E(pr(t, tm, .4))
    base = "Planning a move to the "
    c.text(base, 120, 812 + (1 - a) * 16, "i", "Medium", 36, TXT, a)
    wv = tw(base, "i", "Medium", 36)
    tcl = cue(1, "cloud") - .12; s4 = E(pr(t, tcl, .4)); cw = int((tw("cloud.", "d", "Bold", 36) + 44) * s4) // 6 * 6
    ycap = 812 + font("i", "Medium", 36).getmetrics()[0] - .363 * 36
    if cw > 6: c.blit(BAR(cw, 58, BLUE), 120 + wv - 8, ycap - 29, a)
    c.text("cloud.", 120 + wv + 14, 812 + (1 - a) * 16, "d", "Bold", 36, WF, a * E(pr(t, tcl, .3)))

    # ---- database stack (right-centre), bloating over time
    dbx, dby, dbw = 900, 215, 400
    grow = pr(t, cue(1, "years") - .1, cue(1, "bloating") + .9 - cue(1, "years"))
    n = 16; hot = mix(BLUE, RED, E(pr(t, cue(1, "bloating"), 1.6)))
    c.card(dbx - 18, dby, dbw + 36, 640, E(pr(t, T0, .5)), outline=hot + (200,), glow=None, r=26)
    mono(c, "PRODUCTION DATABASE", dbx + dbw / 2, dby + 22, 16, mix(SKY, RED, E(pr(t, cue(1, "bloating"), 1.6))), E(pr(t, T0, .5)), "Bold", "c")
    db_rows(c, dbx, dby + 66, dbw, n, t, T0 + .2, cue(1, "bloating") + 1.0, hot)
    # size meter on the container's right edge
    mh = int(520 * E(grow)); mhot = mix(BLUE, RED, E(grow))
    if mh > 4: c.blit(BAR(8, mh, mhot), dbx + dbw + 4, dby + 600 - mh, E(pr(t, T0, .5)))
    show_side = 1 - E(pr(t, cue(1, "the cloud") - .35, .45))
    # performance card
    pa = E(pr(t, cue(1, "slowing") - .1, .5)) * show_side
    if pa > .01:
        x0, y0, w0, h0 = 1390 + (1 - E(pr(t, cue(1, "slowing") - .1, .5))) * 60, 300, 410, 205
        c.card(x0, y0, w0, h0, pa, outline=RED + (170,))
        c.icon("clock", x0 + 38, y0 + 38, 30, SKY, pa); c.text("Response time", x0 + 66, y0 + 22, "i", "Bold", 24, TXT, pa)
        c.top = True
        pts = []; kk = E(pr(t, cue(1, "slowing"), 1.4))
        for j in range(41):
            u = j / 40
            if u > kk: break
            base = 140 - 64 * (u ** 1.6); jit = (math.sin(j * 1.9 + t * 7) * 7 + math.sin(j * 4.1) * 4) * u
            pts.append((x0 + 28 + u * (w0 - 56), y0 + base + h0 * .0 - jit + 8))
        if len(pts) > 1: c.poly(pts, mix(SKY, RED, .85), pa, 3)
        c.top = False
        c.text("slower", x0 + w0 - 24, y0 + 22, "i", "Bold", 22, RED, pa * E(pr(t, cue(1, "slowing") + .9, .3)), anchor="r")
    ca = E(pr(t, cue(1, "driving up") - .1, .5)) * show_side
    if ca > .01:
        x0, y0, w0, h0 = 1390 + (1 - E(pr(t, cue(1, "driving up") - .1, .5))) * 60, 545, 410, 205
        c.card(x0, y0, w0, h0, ca, outline=RED + (170,))
        c.icon("dollar", x0 + 38, y0 + 38, 30, SKY, ca); c.text("Storage & licence cost", x0 + 66, y0 + 22, "i", "Bold", 24, TXT, ca)
        for j in range(7):
            hh = int((24 + j * 15) * E(pr(t, cue(1, "driving up") + .1 * j, .5)))
            if hh > 3: c.blit(BAR(34, hh, mix(BLUE, RED, j / 6)), x0 + 36 + j * 52, y0 + h0 - 26 - hh, ca)
        c.icon("up", x0 + w0 - 36, y0 + 40, 28, RED, ca * E(pr(t, cue(1, "driving up") + .9, .3)))
    # destination: S/4HANA / cloud
    ta = cue(1, "the cloud") - .25; da = E(pr(t, ta, .55))
    if da > .01:
        x0, y0, w0, h0 = 1390 + (1 - da) * 70, 330, 410, 330
        c.card(x0, y0, w0, h0, da, outline=BLUE + (230,), glow=BLUE)
        c.text("PLANNED MIGRATION", x0 + w0 / 2, y0 + 30, "i", "Bold", 18, SKY, da, track=5, anchor="c")
        c.icon("cloud", x0 + w0 / 2, y0 + 140, 140, SKY, da)
        sz_ = 38
        while tw("Oracle  /  SAP S/4HANA", "d", "Bold", sz_) > w0 - 40: sz_ -= 1
        c.text("Oracle  /  SAP S/4HANA", x0 + w0 / 2, y0 + 232, "d", "Bold", sz_, WHITE, da, anchor="c")
        p0, p1 = (dbx + dbw + 22, dby + 320), (x0 - 12, y0 + 165)
        c.dashed(p0, p1, SKY, da * .8, 3, 14, 10, t * 60)
        c.pulse(p0, p1, t, 0.55, 0.0, WHITE, 6, da)

# --------------------------------------------------------------------------- C  (HEAD) 20+ years, to both
def node_ring(c, cx, cy, d, label, sub, col, a, t, active):
    c.blit(CIRCLE(d, CARD + (240,), col + (int(120 + 110 * active),), 3, glow=col if active > .5 else None), cx, cy, a, 1.0, True)
    c.ring((cx, cy), d // 2 + 14 + 6 * math.sin(t * 2.2), col, a * (.2 + .5 * active), 2)
    big = len(label) < 5
    c.text(label, cx, cy - (56 if big else 46), "d", "Bold", 60 if big else 46, WHITE, a, anchor="c")
    for n_, ln in enumerate(sub.split("|") if sub else []):
        c.text(ln, cx, cy + (26 if big else 16) + n_ * 22, "i", "Bold", 16, mix(SKY, col, .35 + .35 * active), a, track=3, anchor="c")

def scene_C(c, t):
    t0 = line_t(2)[0]
    a0 = E(pr(t, t0 - .1, .5))
    # lockup: Solix mark + "Solix CDP" on one line (same size and weight), Common Data Platform smaller beneath
    wS = tw("Solix CDP", "d", "Bold", 74, 4); x = 960 - (70 + 22 + wS) / 2
    bolt_solix(c, x, 196, 70, a0, 15)                                   # the bolt always carries the SOLIX name beneath it
    c.text("Solix CDP", x + 92, 214, "d", "Bold", 74, WHITE, a0, track=4)
    ac = E(pr(t, cue(2, "C D P") + .6, .5))
    ctext(c, "COMMON DATA PLATFORM", 960, 350, "i", "Bold", 17, DIM, ac, track=7, anchor="c")
    # counter
    tn = cue(2, "twenty") - .25; k = E(pr(t, tn, 1.5)); n = int(round(20 * k))
    s = E(pr(t, tn, .4)); sc = lerp(.94, 1.0, s)
    c.text(str(n), 960 - 62, 380, "d", "Bold", 270, WHITE, s, anchor="c", sc=sc)
    wd = tw(str(n), "d", "Bold", 270)
    c.text("+", 960 - 62 + wd / 2 * sc + 12, 380, "d", "Bold", 270, RED, s, sc=sc)
    c.text("YEARS OF ERP ARCHIVING EXPERTISE", 960, 705, "i", "Bold", 30, SKY, E(pr(t, cue(2, "E R P") - .15, .5)), track=7, anchor="c")
    # both: SAP + Oracle nodes linked
    tb = cue(2, "all of them") - .05; act = E(pr(t, tb, .6))
    na = E(pr(t, t0 + .2, .6))
    node_ring(c, 300, 560, 220, "Oracle", "ERP", RED, na, t, act)
    node_ring(c, 1620, 560, 220, "SAP", "ERP", BLUE, na, t, act)
    for (p0, p1, col, ph) in (((560, 560), (300 + 112, 560), RED, 0), ((1360, 560), (1620 - 112, 560), BLUE, .5)):
        c.dashed((960 - 0, 560) if False else p0, p1, col, .25 * na + .6 * act, 3, 12, 9, t * 50)
    ctr = (960, 560)
    for i, (n_x, col) in enumerate(((300 + 112, RED), (1620 - 112, BLUE))):
        ex = n_x
        pts = [bezier(ctr, (ctr[0] + (ex - ctr[0]) / 2, 330 if False else 470), (ex, 560), u / 24) for u in range(25)]
        c.poly(pts, col, act * .9, 3)
        pp = int(E((t * .7 + i * .35) % 1) * 24)
        c.dot(pts[min(24, pp)], 7, WHITE, act)
    # the hub dot in the middle of the beams
    c.ring(ctr, int(16 + 6 * math.sin(t * 3)), SKY, act * .9, 3)

# --------------------------------------------------------------------------- D  (BODY) For SAP
def scene_D(c, t):
    t0 = line_t(4)[0]
    kicker(c, "SAP  ·  ARCHIVE DEVELOPMENT KIT", 120, 215, t0 - .05, t, bar=BLUE)
    words(c, [("For", WHITE, None), ("SAP", WHITE, BLUE)], 120, 300, 140, [t0 - .02, t0 + .15], t)
    a = E(pr(t, cue(4, "works natively") - .1, .5))
    c.text("Works natively through", 120, 535 + (1 - a) * 14, "i", "Medium", 40, TXT, a)
    c.text("SAP's Archive Development Kit", 120, 590 + (1 - a) * 14, "i", "Bold", 40, WHITE, a)
    c.blit(BAR(int(520 * E(pr(t, cue(4, "works natively") + .3, .8))) // 6 * 6 + 6, 6, BLUE), 120, 664, a)
    # pipeline: SAP -> ADK -> SOLIXCloud
    pa = E(pr(t, t0 + .1, .6)); y = 300
    c.card(930 + (1 - pa) * 50, y, 250, 150, pa, outline=BLUE + (210,))
    c.text("SAP", 1055 + (1 - pa) * 50, y + 34, "d", "Bold", 52, WHITE, pa, anchor="c"); c.text("SYSTEM", 1055 + (1 - pa) * 50, y + 98, "i", "Bold", 18, SKY, pa, track=6, anchor="c")
    ak = E(pr(t, cue(4, "Archive Development") - .5, .6))
    c.blit(CIRCLE(140, BLUE + (255,), OUTL + (255,), 3, glow=BLUE if ak > .4 else None), 1395, y + 75, ak, 1, True)
    c.text("ADK", 1395, y + 46, "d", "Bold", 44, WF, ak, anchor="c"); c.text("NATIVE", 1395, y + 100, "i", "Bold", 15, WF, ak, track=5, anchor="c")
    sa = E(pr(t, cue(4, "Archive Development") - .1, .6))
    c.card(1570 + (1 - sa) * 50, y, 250, 150, sa, outline=RED + (210,))
    c.icon("db", 1650 + (1 - sa) * 50, y + 50, 46, SKY, sa)
    c.text("SOLIXCloud", 1695 + (1 - sa) * 50, y + 30, "d", "Bold", 28, WHITE, sa, anchor="c") if False else c.text("SOLIX", 1692 + (1 - sa) * 50, y + 38, "d", "Bold", 30, WHITE, sa, track=3)
    c.text("ARCHIVE", 1695 + (1 - sa) * 50, y + 100, "i", "Bold", 18, SKY, sa, track=6, anchor="c")
    for (p0, p1, vis) in (((1190, y + 75), (1320, y + 75), ak), ((1470, y + 75), (1560, y + 75), sa)):
        c.line(p0, p1, BLUE, .55 * vis, 3); c.pulse(p0, p1, t, .9, p0[0] / 3000., WHITE, 6, vis)
    # standard archive objects
    ha = E(pr(t, cue(4, "pre-built") - .1, .5))
    c.text("PRE-BUILT SUPPORT FOR STANDARD ARCHIVE OBJECTS", 930, 515, "i", "Bold", 21, SKY, ha, track=4)
    c.blit(BAR(int(860 * E(pr(t, cue(4, "pre-built"), .9))) // 6 * 6 + 6, 3, BLUE + ()), 930, 553, ha * .6)
    cards = [("Finance", "FI_DOCUMNT", "chart", cue(4, "Finance")), ("Materials", "MM_MATBEL", "box", cue(4, "Materials")),
             ("Sales", "SD_VBAK", "doc", cue(4, "Sales")), ("And more", "+ DOZENS OF OBJECTS", "layers", cue(4, "and more"))]
    for i, (nm, code, ic, ti) in enumerate(cards):
        a = EB(pr(t, ti - .15, .5)); col = BLUE if i < 3 else RED
        gx, gy = 930 + (i % 2) * 450, 590 + (i // 2) * 135
        c.card(gx + 0, gy, 420, 110, clamp(a), sc=lerp(.9, 1.0, clamp(a)), outline=col + (200,), glow=None)
        c.blit(CIRCLE(70, col + (255,), glow=col), gx + 64, gy + 55, clamp(a), 1, True)
        c.icon(ic, gx + 64, gy + 55, 40, WF, clamp(a))
        c.text(nm, gx + 118, gy + 20, "d", "Bold", 38, WHITE, clamp(a))
        mono(c, code, gx + 118, gy + 70, 18, SKY, clamp(a), "Bold")

# --------------------------------------------------------------------------- E  (BODY) For Oracle EBS
def rows_to_vault(c, x, y, w, h, t, t0, A=1.0):
    """small loop: record bars slide into a vault"""
    c.blit(RR(96, 96, 18, CARD + (255,), BLUE + (200,), 2, False), x + w - 60, y + h / 2, A, 1, True)
    c.icon("lock", x + w - 60, y + h / 2, 54, SKY, A)
    for k in range(3):
        u = ((t - t0) * .55 + k / 3.0) % 1.0
        xx = lerp(x + 10, x + w - 128, E(u)); a = (1 - clamp((u - .85) / .15)) * A
        c.blit(BAR(96, 16, mix((120, 140, 190), BLUE, u)), xx, y + h / 2 - 34 + k * 26, a * .95)

def retire_grid(c, x, y, t, t0, A=1.0):
    k = pr(t, t0, 2.0)
    for r in range(2):
        for q in range(3):
            i = r * 3 + q; off = clamp((k * 7 - i) * .8)
            col = mix(BLUE, OFFC, off)
            c.blit(RR(46, 46, 10, col + (255,), None, 0, False), x + q * 58 + 23, y + r * 58 + 23, A, 1, True)
    ek = E(pr(t, t0 + 1.8, .45)) * A
    c.text("RETIRED", x + 200, y + 28, "i", "Bold", 22, RED, ek, track=6)
    c.icon("check", x + 214, y + 82, 40, RED, ek)

def scene_E(c, t):
    t0 = line_t(3)[0]
    kicker(c, "ORACLE  ·  VALIDATED", 120, 215, t0 - .05, t, bar=RED)
    words(c, [("For", WHITE, None), ("Oracle", WHITE, RED)], 120, 312, 120, [t0 - .02, t0 + .3], t)
    a = E(pr(t, t0 + .3, .5))
    c.text("Oracle E-Business Suite", 120, 535 + (1 - a) * 14, "i", "Medium", 40, TXT, a)
    c.blit(BAR(int(420 * E(pr(t, t0 + .5, .8))) // 6 * 6 + 6, 6, RED), 120, 600, a)
    # validated badge
    tc = cue(3, "validated") - .15; ca = EB(pr(t, tc, .6))
    ca = clamp(ca); x0, y0 = 930, 290
    c.card(x0 + (1 - E(pr(t, tc, .6))) * 60, y0, 870, 170, ca, outline=RED + (230,), glow=RED)
    c.blit(CIRCLE(104, RED + (255,), glow=RED), x0 + 96 + (1 - E(pr(t, tc, .6))) * 60, y0 + 85, ca, 1, True)
    c.icon("shield", x0 + 96 + (1 - E(pr(t, tc, .6))) * 60, y0 + 85, 64, WF, ca)
    s1_ = 60
    while tw("Solix is Validated by Oracle", "d", "Bold", s1_) > 660: s1_ -= 1
    s2_ = 19
    while tw("ORACLE VALIDATED INTEGRATION  ·  ORACLE E-BUSINESS SUITE", "i", "Bold", s2_, 4) > 660: s2_ -= 1
    c.text("Solix is Validated by Oracle", x0 + 178 + (1 - E(pr(t, tc, .6))) * 60, y0 + 38, "d", "Bold", s1_, WHITE, ca)
    c.text("ORACLE VALIDATED INTEGRATION  ·  ORACLE E-BUSINESS SUITE", x0 + 180 + (1 - E(pr(t, tc, .6))) * 60, y0 + 116, "i", "Bold", s2_, SKY, ca, track=4)
    c.ring((x0 + 96, y0 + 85), int(52 + 70 * E(pr(t, tc + .1, .9))), RED, (1 - E(pr(t, tc + .1, .9))) * .8, 3)
    # archiving + application retirement
    for (nm, sub, ti, col, x, kind) in (("Archiving", "Inactive data out of production", cue(3, "archiving") - .12, BLUE, 930, "arch"),
                                         ("Application retirement", "Decommission the whole app", cue(3, "full application") - .15, RED, 1370, "ret")):
        a = E(pr(t, ti, .5)); xs = x + (1 - a) * 50
        c.card(xs, 520, 430, 330, a, outline=col + (200,))
        c.text(nm, xs + 30, 552, "d", "Bold", 34, WHITE, a); c.text(sub.upper(), xs + 30, 604, "i", "Bold", 15, SKY, a, track=3)
        c.blit(BAR(int(80 * a), 5, col), xs + 30, 636, a)
        if kind == "arch": rows_to_vault(c, xs + 30, 670, 370, 130, t, ti, a)
        else: retire_grid(c, xs + 40, 680, t, ti, a)
    # other connected apps, bottom left, once "validated by Oracle" has been said
    ta = cue(3, "by Oracle", end=True) + .1; pa = E(pr(t, ta, .5))
    if pa > .01:
        px, py, pw, ph = 120 - (1 - pa) * 30, 668, 740, 300
        c.card(px, py, pw, ph, pa, outline=RED + (190,), r=24)
        c.blit(BAR(28, 5, RED), px + 34, py + 36, pa); ctext(c, "CONNECT", px + 76, py + 38, "i", "Bold", 22, SKY, pa, track=8)
        x = px + 34
        for i, nm in enumerate(("EBS", "PEOPLESOFT", "JDE", "SIEBEL")):
            ca = E(pr(t, ta + .3 + i * .16, .35)); w = int(tw(nm, "i", "Bold", 22, 3) + 50); col = RED if i % 2 == 0 else BLUE
            c.card(x, py + 86 + (1 - ca) * 10, w, 54, ca * pa, outline=col + (220,), fill=CARD + (235,), r=27)
            ctext(c, nm, x + w / 2, py + 113 + (1 - ca) * 10, "i", "Bold", 22, WHITE, ca * pa, track=3, anchor="c"); x += w + 16
        sa = E(pr(t, ta + 1.05, .4)) * pa
        f = font("i", "Bold", 46); w1 = f.getlength("& "); w2 = f.getlength("200+")
        ctext(c, "& ", px + 34, py + 180, "i", "Bold", 46, WHITE, sa); ctext(c, "200+", px + 34 + w1, py + 180, "i", "Bold", 46, RED, sa)
        ctext(c, " Sources", px + 34 + w1 + w2, py + 180, "i", "Bold", 46, WHITE, sa)
        fa = E(pr(t, ta + 1.4, .4)) * pa
        yb = py + 250
        c.card(px + 28, yb - 36, 58, 72, fa, outline=RED + (230,), fill=BOLTF + (255,), r=12); bolt_solix(c, px + 40, yb - 31, 34, fa, 11)
        x2 = px + 106; ctext(c, "Through ", x2, yb, "i", "Medium", 28, TXT, fa); x2 += tw("Through ", "i", "Medium", 28)
        ctext(c, "Solix Connect", x2, yb, "i", "Bold", 28, WHITE, fa)
        ctext(c, "\u00bb\u00bb\u00bb", px + pw - 34, yb, "i", "Bold", 30, SKY, fa * .8, anchor="r")
    badge = E(pr(t, cue(3, "both") - .1, .5))
    c.text("BOTH  ·  ONE PLATFORM", 1085, 888, "i", "Bold", 17, SKY, badge * (1 - E(pr(t, line_t(3)[1] - .5, .4))), track=6, anchor="c")

# --------------------------------------------------------------------------- F  (BODY) policy -> archive, searchable / reportable / legal hold
def scene_F(c, t):
    t0 = line_t(5)[0]
    kicker(c, "POLICY-DRIVEN ARCHIVING", 120, 190, t0 - .05, t, bar=BLUE)
    words(c, [("Inactive", WHITE, RED), ("data", WHITE, None)], 120, 240, 84, [t0 - .05, t0 + .2], t)
    words(c, [("moves", WHITE, None), ("out", WHITE, None), ("on", WHITE, None), ("policy.", WHITE, BLUE)], 120, 372, 84,
          [cue(5, "moves") - .1, cue(5, "out") - .1, cue(5, "on policy") - .1, cue(5, "policy") - .1], t)
    ta = t0 + .2; fa = E(pr(t, ta, .6)); y0 = 528; h0 = 220
    PX, AX, RW, RH, SY, ST = 176, 1436, 308, 24, y0 + 52, 31
    gx = 960
    # frames
    c.card(150, y0, 360, h0, fa, outline=BLUE + (170,)); mono(c, "PRODUCTION", 330, y0 + 18, 16, SKY, fa, "Bold", "c")
    c.card(1410, y0, 360, h0, fa, outline=RED + (170,)); mono(c, "SOLIX ARCHIVE", 1590, y0 + 18, 16, SKY, fa, "Bold", "c")
    c.icon("lock", 1690, y0 + 152, 54, RED, fa * E(pr(t, cue(5, "searchable") - .3, .8)))
    c.line((510, y0 + 110), (gx - 175, y0 + 110), BLUE, fa * .35, 2); c.line((gx + 175, y0 + 110), (1410, y0 + 110), BLUE, fa * .35, 2)
    # records: each glides in ONE continuous eased move from its production slot to its archive slot (no pops, no resizing)
    NROW, GAP, FLY = 5, 1.0, 2.7; t_dep = cue(5, "moves") + .15
    def row(x, y, i, a, lit):
        c.card(x, y, RW, RH, a, fill=(14, 96, 168, 255) if i == 0 else mix(ROWF3, (14, 84, 156), lit) + (255,),
               outline=(BLUE + (230,)) if i == 0 else mix(ROWO3, SKY, lit) + (230,), r=7)
        mono(c, "FY2026" if i == 0 else f"FY{2025 - i}", x + 14, y + 4, 14, WF if (i == 0 or lit > .5) else DIM, a, "Bold")
    row(PX, SY, 0, fa, 0)
    for i in range(1, NROW):
        ts = t_dep + (i - 1) * GAP; u = (t - ts) / FLY; sy = SY + i * ST; dy_ = SY + (i - 1) * ST
        c.dashed((PX, sy + 12), (PX + RW, sy + 12), (90, 110, 170), fa * .5 * E(pr(u, 0, .12)), 1, 8, 8)    # soft empty slot
        if u <= 0: row(PX, sy, i, fa, 0)
        else:
            k = IO(clamp(u)); row(lerp(PX, AX, k), lerp(sy, dy_, k), i, fa, E(pr(u, .62, .38)))
    # policy gate drawn on top: records slide beneath it and re-emerge
    c.card(gx - 175, y0 + 6, 350, h0 - 12, fa, outline=BLUE + (230,))
    c.icon("gear", gx - 118, y0 + 62, 44, SKY, fa); c.text("POLICY", gx - 80, y0 + 40, "i", "Bold", 22, SKY, fa, track=6)
    c.text("Older than 7 years", gx, y0 + 98, "d", "Bold", 36, WHITE, fa, anchor="c"); c.text("→  ARCHIVE", gx, y0 + 150, "i", "Bold", 20, BLUE, fa, track=5, anchor="c")
    # searchable / accessible / reportable
    bl = [("Searchable", "search", cue(5, "searchable")), ("Accessible", "key", cue(5, "accessible")), ("Reportable", "chart", cue(5, "reportable"))]
    for i, (lab, ic, ti) in enumerate(bl):
        a = E(pr(t, ta + .6 + i * .12, .5)); on = E(pr(t, ti - .05, .45)); col = RED if i == 1 else BLUE
        x = 150 + i * 560
        c.card(x, 808, 500, 104, a, outline=mix(CHIPB, col, on) + (int(lerp(CHIPA[0], CHIPA[1], on)),), fill=CARD + (int(lerp(CFA[0], CFA[1], on)),))
        c.blit(CIRCLE(68, col + (int(lerp(70, 255, on)),)), x + 62, 860, a, 1, True); c.icon(ic, x + 62, 860, 38, WF, a)
        ctext(c, lab, x + 118, 860, "d", "Bold", 40, mix(TXT, WHITE, on), a)
        if on > .5: c.icon("check", x + 462, 860, 30, SKY, a * on)
    tl = cue(5, "for as long") - .1; a = E(pr(t, tl, .5)); k = E(pr(t, tl, 2.4))
    c.blit(BAR(1620, 4, TRK), 150, 970, a); c.blit(BAR(max(6, int(1620 * k)) // 6 * 6, 4, BLUE), 150, 970, a)
    c.blit(CIRCLE(22, WHITE + (255,), glow=BLUE), 150 + 1620 * k, 972, a, 1, True)
    c.text("FOR AS LONG AS YOU NEED IT", 150, 996, "i", "Bold", 18, SKY, a, track=6)

# --------------------------------------------------------------------------- K  (BODY) pre-built Application Knowledge Graphs for these applications
AKG_NODES = ["Vendor", "Invoice", "Payment", "Purchase order", "GL account", "Contract", "Customer", "Material"]
def scene_K(c, t):
    t0 = line_t(6)[0]; tk = cue(6, "Knowledge") - .1
    kicker(c, "APPLICATION KNOWLEDGE GRAPHS", 120, 190, t0 - .05, t, bar=BLUE)
    words(c, [("Pre-built", WHITE, None)], 120, 235, 100, [cue(6, "pre-built") - .1], t)
    words(c, [("AKGs", WHITE, BLUE)], 120, 360, 100, [cue(6, "A K G") - .1], t)
    a1 = E(pr(t, tk, .5)); a2 = E(pr(t, cue(6, "these applications") - .1, .5))
    c.text("Application Knowledge Graphs", 120, 575 + (1 - a1) * 14, "i", "Medium", 40, TXT, a1)
    c.text("for these applications", 120, 630 + (1 - a2) * 14, "i", "Bold", 40, WHITE, a2)
    # the applications that ship with pre-built AKGs
    apps = ["ECC", "SAP S/4HANA", "OEBS", "PEOPLESOFT", "JDE", "SIEBEL"]; ta = cue(6, "these applications") - .05
    for i, nm in enumerate(apps):
        on = E(pr(t, ta + i * .14, .4)); w = 240; gx, gy = 120 + (i % 3) * (w + 12), 730 + (i // 3) * 82; col = BLUE if i % 2 == 0 else RED
        c.card(gx, gy, w, 64, on, outline=col + (220,), fill=CARD + (236,), r=32)
        c.blit(CIRCLE(30, col + (255,), glow=col), gx + 34, gy + 32, on, 1, True); c.icon("check", gx + 34, gy + 32, 18, WF, on)
        ctext(c, nm, gx + 62, gy + 32, "i", "Bold", 19, WHITE, on, track=2)
    # the knowledge graph panel
    pa = E(pr(t, tk - .1, .6)); px, py, pw, ph = 930, 205, 870, 700
    c.card(px, py, pw, ph, pa, outline=SKY + (200,), glow=BLUE)
    mono(c, "APPLICATION KNOWLEDGE GRAPH", px + pw / 2, py + 24, 17, SKY, pa, "Bold", "c"); c.blit(BAR(pw - 60, 2, SOFT), px + 30, py + 56, pa * .8)
    cx, cy = px + pw / 2, py + 390; pts = []
    for i in range(len(AKG_NODES)):
        ang = -math.pi / 2 + i * 2 * math.pi / len(AKG_NODES); pts.append((cx + 300 * math.cos(ang), cy + 232 * math.sin(ang)))
    c.top = True
    for i, p in enumerate(pts):
        e = clamp(E(pr(t, tk + .3 + i * .16, .5)))
        if e > .01:
            d_ = math.hypot(p[0] - cx, p[1] - cy); s0 = (cx + (p[0] - cx) * 56 / d_, cy + (p[1] - cy) * 56 / d_)        # lines start at the hub's rim
            c.line(s0, p, SKY, .7 * e, 2); c.pulse(s0, p, t, .55, (i * .17) % 1, WHITE, 4, e)
            q = pts[(i + 1) % len(pts)]; e2 = clamp(E(pr(t, tk + .5 + i * .16, .5)))
            if e2 > .01: c.line(p, q, SKY, .35 * e2, 1)
    c.top = False
    ha = EB(pr(t, tk + .15, .5), 1.8)
    c.blit(CIRCLE(104, BLUE + (255,), OUTL + (255,), 3, glow=BLUE), cx, cy, clamp(ha), clamp(ha), True); c.text("AKG", cx, cy - 24, "d", "Bold", 34, WF, clamp(ha), anchor="c")
    for i, (p, nm) in enumerate(zip(pts, AKG_NODES)):
        e = EB(pr(t, tk + .3 + i * .16, .5), 2.0)
        if e > .01:
            col = RED if i in (2, 5) else SKY
            c.blit(CIRCLE(34, col + (255,), glow=col), p[0], p[1], clamp(e), clamp(e), True)
            ctext(c, nm, p[0], p[1] + (-40 if p[1] < cy else 42), "i", "Bold", 20, TXT, clamp(e), anchor="c")

# --------------------------------------------------------------------------- DA  (BODY) Data Ask: ask in plain language, cited answers
QUESTION = "How much did Tarrow Freight bill us in FY2012?"
INV = [("1900004417", "2012-03-14", "18,420.50"), ("1900004602", "2012-04-02", "7,935.00"), ("1900005288", "2012-06-19", "22,610.75"),
       ("1900006031", "2012-09-07", "16,044.20"), ("1900006977", "2012-11-28", "19,302.40")]
DINK, GREY, LINE_ = (22, 40, 84), (98, 112, 144), TRK

def scene_DA(c, t):
    ta = cue(7, "Ask") - .1; t2 = cue(8, "Every") - .12
    kicker(c, "DATA ASK", 120, 215, ta, t, bar=BLUE)
    # headline 1 hands over to headline 2
    g0 = c.ga; c.ga = g0 * (1 - E(pr(t, t2 - .35, .35)))
    if c.ga > .004:
        words(c, [("Ask", WHITE, None), ("in", WHITE, None), ("plain", WHITE, None)], 120, 285, 84, [cue(7, "Ask") - .1, cue(7, "plain") - .3, cue(7, "plain") - .1], t)
        words(c, [("language.", WHITE, BLUE)], 120, 412, 84, [cue(7, "language") - .15], t)
    c.ga = g0
    if t > t2 - .3:
        words(c, [("Every", WHITE, None), ("answer", WHITE, None)], 120, 285, 84, [cue(8, "Every") - .1, cue(8, "answer") - .1], t)
        words(c, [("cites", WHITE, None), ("its", WHITE, None), ("source.", WHITE, RED)], 120, 412, 84, [cue(8, "cites") - .1, cue(8, "its source") - .1, cue(8, "source") - .1], t)
    pills = [("Data Ask", "search", BLUE, cue(7, "Data Ask") - .1), ("Cites its source", "doc", RED, cue(8, "cites its") - .05),
             ("Permission-checked", "shield", BLUE, cue(8, "permission") - .1), ("Audit-logged", "lock", RED, cue(8, "audit") - .1)]
    for i, (lab, ic, col, ti) in enumerate(pills):
        a = E(pr(t, ti - .1, .4)); on = E(pr(t, ti, .35)); yy = 610 + i * 92
        c.card(120 - (1 - a) * 40, yy, 560, 72, a, outline=mix((60, 80, 140), col, on) + (int(lerp(110, 235, on)),), fill=CARD + (int(lerp(190, 238, on)),), r=36)
        c.blit(CIRCLE(52, col + (255,)), 120 + 36 - (1 - a) * 40, yy + 36, a, 1, True); c.icon(ic, 156 - (1 - a) * 40, yy + 36, 28, WF, a)
        ctext(c, lab, 196 - (1 - a) * 40, yy + 36, "i", "Bold", 32, mix(TXT, WHITE, on), a)
    # ---- the Data Ask panel
    pa = E(pr(t, ta + .1, .6)); px, py, pw, ph = 930, 190, 870, 790
    sc = lerp(.97, 1.0, pa)
    c.card(px, py, pw, ph, pa, sc=sc, fill=(247, 249, 253, 255), outline=(190, 206, 236, 255), r=26)
    if pa < .5: return
    pp = (pa - .5) * 2; X = px + 30
    c.blit(CIRCLE(14, BLUE + (255,)), px + 40, py + 40, pp, 1, True)
    ctext(c, "Data Ask", px + 62, py + 40, "i", "Bold", 28, (14, 86, 160), pp)
    c.blit(RR(232, 40, 10, (226, 234, 248, 255), None, 0, False), px + pw - 146, py + 40, pp, 1, True)
    ctext(c, "KB_ECC_PRD_01", px + pw - 146, py + 40, "m", "Bold", 17, (30, 66, 120), pp, anchor="c")
    c.blit(BAR(pw - 60, 2, LINE_), X, py + 80, pp)
    # question box with typing
    c.blit(RR(pw - 60, 76, 14, (255, 255, 255, 255), (BLUE + (255,)) if t < t2 + .4 else (200, 212, 236, 255), 2, False), X + (pw - 60) / 2, py + 138, pp, 1, True)
    c.icon("search", X + 36, py + 138, 28, GREY, pp)
    tt0 = ta + .9; n = int(len(QUESTION) * clamp((t - tt0) / 2.1)); typed = QUESTION[:n]
    cur = "|" if (t < t2 + .2 and (int(t * 2.6) % 2 == 0 or n < len(QUESTION))) else ""
    ctext(c, typed + cur, X + 70, py + 138, "i", "Medium", 28, DINK, pp)
    done = tt0 + 2.1
    # searching
    if done < t < t2 + .35:
        ctext(c, "Searching KB_ECC_PRD_01 …", X + 4, py + 232, "m", "Regular", 17, GREY, E(pr(t, done, .3)))
        k = (t - done) % 1.2 / 1.2; c.blit(BAR(int(220 * (1 - abs(2 * k - 1)) + 30), 6, BLUE), X + 4 + k * (pw - 320), py + 262, E(pr(t, done, .3)))
    # answer
    t_ans = t2 + .35; aa = E(pr(t, t_ans, .45))
    if aa > .01:
        val = 84312.85 * E(pr(t, t_ans, 1.0))
        ctext(c, f"{val:,.2f} USD", X + 4, py + 240 + (1 - aa) * 10, "d", "Bold", 68, DINK, aa)
        ctext(c, "5 invoices · Tarrow Freight Partners (sample) · FY2012", X + 4, py + 318, "i", "Medium", 23, GREY, E(pr(t, t_ans + .3, .4)))
        ctext(c, "SOURCES · FI DOCUMENTS · ARCHIVE", X + 4, py + 362, "m", "Regular", 15, GREY, E(pr(t, t_ans + .4, .4)), track=3)
        for i, (no, dt, amt) in enumerate(INV):
            ti = lerp(cue(8, "cites its"), cue(8, "source") + .5, i / 4) - .05; ra = E(pr(t, ti, .4)); yy = py + 384 + i * 56
            if ra < .01: continue
            hi = E(pr(t, ti + .1, .35))
            c.blit(RR(pw - 60, 48, 10, (236, 241, 250, 255) if i % 2 else (255, 255, 255, 255), mix(LINE_, RED, hi) + (255,), 2, False), X + (pw - 60) / 2, yy + 24 - (1 - ra) * 8, ra, 1, True)
            c.blit(CIRCLE(30, RED + (255,)), X + 30, yy + 24, ra, 1, True); ctext(c, str(i + 1), X + 30, yy + 24, "i", "Bold", 18, WF, ra, anchor="c")
            ctext(c, no, X + 66, yy + 24, "i", "Medium", 22, DINK, ra); ctext(c, dt, X + 300, yy + 24, "i", "Medium", 22, DINK, ra)
            ctext(c, amt, X + pw - 60 - 214, yy + 24, "i", "Medium", 22, DINK, ra, anchor="r")
            c.blit(RR(166, 32, 16, (226, 234, 248, 255), None, 0, False), X + pw - 60 - 100, yy + 24, ra, 1, True)
            ctext(c, "SAP · FI_DOCUMNT", X + pw - 60 - 100, yy + 24, "m", "Regular", 14, (40, 70, 120), ra, anchor="c")
        # chips row
        cy = py + ph - 52
        for (lab, ti, fill, ink, w) in (("Permission-checked · fin.records", cue(8, "permission"), (222, 240, 250, 255), (12, 92, 150), 372),
                                         ("Audit-logged", cue(8, "audit"), (236, 239, 246, 255), (50, 64, 98), 186)):
            ca = E(pr(t, ti - .05, .4))
            if ca > .01:
                xx = X + (0 if "Permission" in lab else 392)
                c.blit(RR(w, 40, 20, fill, None, 0, False), xx + w / 2, cy, ca, 1, True)
                ctext(c, lab, xx + w / 2, cy, "i", "Bold", 19, ink, ca, anchor="c")
        sa = E(pr(t, cue(8, "audit") + .35, .4))
        if sa > .01: ctext(c, "‹› View generated SQL", X + pw - 60, cy, "i", "Bold", 20, (14, 86, 160), sa, anchor="r")


# --------------------------------------------------------------------------- G  (TAIL) The result?
def scene_G(c, t):
    a0, b0 = SC["G"]; k = EB(pr(t, a0 - .03, .45), 1.9)
    sc = lerp(.82, 1.0, clamp(k)) * (1 + .02 * (t - a0)); a = E(pr(t, a0 - .05, .25))
    ww = tw("The result", "d", "Bold", 190)
    c.text("The result", 960 - 40, 410, "d", "Bold", 190, WHITE, a, anchor="c", sc=sc)
    c.text("?", 960 - 40 + ww * sc / 2 + 36, 410, "d", "Bold", 190, RED, a, sc=sc)
    c.blit(BAR(int(640 * E(pr(t, a0 + .1, .45))) // 6 * 6 + 6, 8, BLUE), 960 - 320, 660, a)
    c.ring((960, 540), int(120 + 700 * E(pr(t, a0 - .02, .8))), BLUE, (1 - E(pr(t, a0 - .02, .8))) * .6, 3)

# --------------------------------------------------------------------------- H  (TAIL) leaner / cleaner / 30-60% smaller
def scene_H(c, t):
    t0 = line_t(10)[0]
    kicker(c, "THE RESULT", 120, 190, t0 - .05, t, bar=BLUE)
    # row 1/2
    for i, (lab, key, y) in enumerate((("Leaner production systems", "Leaner", 262), ("Cleaner migrations", "cleaner", 372))):
        ti = cue(10, key) - .12; a = E(pr(t, ti, .45))
        c.blit(CIRCLE(62, BLUE + (255,), glow=BLUE), 120 + 31 - (1 - a) * 30, y + 38, a, 1, True); c.icon("check", 151 - (1 - a) * 30, y + 38, 34, WF, a)
        c.text(lab, 206 - (1 - a) * 30, y + 5, "d", "Bold", 58, WHITE, a)
    # 30-60%
    tn = cue(10, "thirty") - .2; a = E(pr(t, tn, .4))
    da_ = E(pr(t, cue(10, "legacy") - .1, .45))
    c.text("Legacy databases, up to", 120, 505 + (1 - da_) * 16, "d", "Bold", 52, SKY, da_)
    c.text("30–60%", 120, 560 + (1 - a) * 24, "d", "Bold", 214, WHITE, a, sc=1.0)
    wn = tw("30–60%", "d", "Bold", 214)
    sa_ = E(pr(t, cue(10, "smaller") - .15, .4))
    ua = E(pr(t, cue(10, "smaller") - .1, .55)); c.blit(BAR(int((wn) * ua) // 6 * 6 + 6, 9, RED), 124, 826, sa_)
    c.text("smaller", 120, 850, "d", "Bold", 76, WHITE, sa_ , sc=1.0)
    c.icon("down", 120 + tw("smaller ", "d", "Bold", 76) + 26, 892, 56, RED, sa_)
    # database visual
    sh = E(pr(t, cue(10, "Leaner") + .2, 1.6))              # 0 = full, 1 = lean
    ma = E(pr(t, t0 - .1, .5)); n = 14
    keep = int(round(lerp(n, 8, sh)))                      # about 40% lighter slab stack
    dx, dy, dw = 1040, 270, 440
    hh = 66 + n * 33 + 24; ch = int(lerp(hh, 66 + 8 * 33 + 24, sh)) // 8 * 8
    c.card(dx - 18, dy, dw + 36, ch, ma, outline=mix(RED, BLUE, sh) + (210,), r=26)
    mono(c, "DATABASE", dx + dw / 2, dy + 22, 16, SKY, ma, "Bold", "c")
    for i in range(n):
        yy = dy + 66 + i * 33
        if i < keep: c.card(dx, yy, dw, 25, ma, fill=((14, 96, 168, 255) if i == 0 else ROWF3 + (255,)), outline=(BLUE + (230,)) if i == 0 else ROWO3 + (255,), r=8)
        else:
            fa = 1 - E(pr(t, cue(10, "Leaner") + .2 + (n - i) * .09, .5))
            if fa > .02: c.card(dx, yy - 14 * (1 - fa), dw, 25, ma * fa, fill=ROWF3 + (255,), outline=ROWO3 + (255,), r=8)
            # ghost outline of removed slabs
            c.dashed((dx, yy + 12), (dx + dw, yy + 12), (90, 110, 170), ma * .30 * sh, 1, 8, 8)
        if i < keep:
            mono(c, f"FY{2026 - i}", dx + 14, yy + 4, 15, WF if i == 0 else DIM, ma, "Bold")
    # archive chip (where the weight went)
    aa = E(pr(t, cue(10, "Leaner") + .6, .5))
    c.card(dx + dw + 60 - 0, dy + 24, 200, 80, aa, outline=RED + (200,), r=18)
    c.icon("lock", dx + dw + 96, dy + 64, 34, RED, aa); c.text("ARCHIVE", dx + dw + 126, dy + 38, "i", "Bold", 17, SKY, aa, track=4); mono(c, "searchable", dx + dw + 126, dy + 64, 15, TXT, aa)
    c.dashed((dx + dw + 10, dy + 120), (dx + dw + 150, dy + 64), RED, aa * .8, 2, 8, 6, t * 40)
    # cleaner migration -> cloud
    tm = cue(10, "cleaner") - .15; ka = E(pr(t, tm, .6))
    if ka > .01:
        cx0 = 1560 + (1 - ka) * 60
        c.card(cx0, 600, 250, 230, ka, outline=BLUE + (230,), glow=BLUE)
        c.icon("cloud", cx0 + 125, 662, 84, SKY, ka)
        c.text("Modernization", cx0 + 125, 712, "d", "Bold", 30, WHITE, ka, anchor="c"); c.text("application", cx0 + 125, 752, "d", "Bold", 30, WHITE, ka, anchor="c")
        p0, p1 = (dx + dw + 18, 700), (cx0 - 10, 715)
        c.line(p0, p1, BLUE, ka * .7, 3); c.pulse(p0, p1, t, .8, 0, WHITE, 6, ka)
    c.text("ILLUSTRATIVE", 120, 1010, "m", "Regular", 15, (90, 112, 170), .9, track=3)

# --------------------------------------------------------------------------- I  (TAIL) ERP history -> AI-ready data
NODES0 = [(1160, 560), (1260, 470), (1370, 520), (1470, 450), (1560, 560), (1450, 640), (1330, 650), (1220, 700), (1120, 640),
         (1290, 570), (1400, 580), (1180, 480), (1500, 530), (1360, 440), (1240, 600), (1470, 700)]
NCARD = (960, 478, 840, 390)                         # the "AI-activated data" screen that now holds the network
NODES = [(NCARD[0] + 50 + (x - 1120) / 440 * 740, NCARD[1] + 82 + (y - 440) / 260 * 262) for x, y in NODES0]
EDGES = [(0, 11), (11, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 0), (0, 14), (14, 9), (9, 2), (9, 10), (10, 12), (12, 4), (12, 3),
         (13, 1), (13, 3), (10, 5), (9, 6), (14, 7), (15, 5), (15, 6), (10, 2), (11, 14)]
def scene_I(c, t):
    t0 = line_t(11)[0]
    words(c, [("Your", WHITE, None), ("ERP", WHITE, None), ("history", WHITE, None), ("becomes", WHITE, None)], 960, 98, 80,
          [cue(11, "Your") - .1, cue(11, "E R P") - .1, cue(11, "history") - .1, cue(11, "becomes") - .1], t, anchor="c")
    words(c, [("AI-activated", WHITE, BLUE), ("data", WHITE, None)], 960, 232, 128, [cue(11, "activated") - .12, cue(11, "data") - .08], t, anchor="c")
    ta = t0; fa = E(pr(t, ta, .6)); tb = cue(11, "becomes")
    # archive records table
    x0, y0, w0, h0 = 170, 478, 520, 390
    c.card(x0, y0, w0, h0, fa, outline=BLUE + (170,)); mono(c, "ERP HISTORY  ·  ARCHIVE", x0 + 26, y0 + 20, 16, SKY, fa, "Bold")
    # the AI screen that receives the data (network lives inside it)
    na = E(pr(t, tb - .2, .7)); nx, ny, nw, nh = NCARD
    c.card(nx, ny, nw, nh, na, outline=SKY + (200,), glow=BLUE)
    mono(c, "AI-ACTIVATED DATA", nx + nw / 2, ny + 22, 17, SKY, na, "Bold", "c")
    c.blit(BAR(nw - 60, 2, SOFT), nx + 30, ny + 52, na * .8)
    recs = [("FI documents", "FY2012"), ("Purchase orders", "FY2013"), ("Sales orders", "FY2014"), ("Material docs", "FY2015"),
            ("Payables invoices", "FY2016"), ("Journal entries", "FY2017"), ("Cost allocations", "FY2018")]
    c.top = True                                                  # streams + network lines sit on top of the screens
    for i, (nm, fy) in enumerate(recs):
        lit = E(pr(t, tb + i * .12, .4)); yy = y0 + 62 + i * 45
        if lit > .02:
            tgt = NODES[(i * 2 + 1) % len(NODES)]; p0 = (x0 + w0 - 22, yy + 18)
            ctrl = ((p0[0] + tgt[0]) / 2, min(p0[1], tgt[1]) - 60 - 10 * i)
            pts = [bezier(p0, ctrl, tgt, u / 22) for u in range(23)]
            c.poly(pts, SKY, .5 * lit, 2)
            for q in range(2):
                u = ((t - tb) * .75 + i * .13 + q * .5) % 1; c.dot(bezier(p0, ctrl, tgt, u), 5, WHITE, lit * .95)
    for (i, j) in EDGES:
        e = clamp(E(pr(t, tb + .35 + (i + j) * .035, .5)))
        if e > 0.01:
            p, q = NODES[i], NODES[j]; c.line(p, q, SKY, .7 * e, 2)
            if (i + j) % 3 == 0: c.pulse(p, q, t, .6, (i * .13) % 1, WHITE, 4, e)
    c.top = False
    for i, (nm, fy) in enumerate(recs):                           # table rows (drawn after the streams' origin)
        ai = E(pr(t, ta + .1 + i * .08, .4)); lit = E(pr(t, tb + i * .12, .4)); yy = y0 + 62 + i * 45
        c.card(x0 + 22, yy, w0 - 44, 36, ai * fa, fill=mix(ROWF3, (14, 96, 168), lit) + (255,), outline=mix(ROWO3, BLUE, lit) + (230,), r=9)
        mono(c, fy, x0 + 38, yy + 9, 15, WF if lit > .5 else DIM, ai * fa, "Bold"); mono(c, nm, x0 + 130, yy + 9, 15, WF if lit > .5 else TXT, ai * fa, "Regular")
    for i, (x, y) in enumerate(NODES):
        e = EB(pr(t, tb + .3 + i * .06, .5), 2.2)
        if e > .01:
            r = 11 + (i % 3) * 3; col = RED if i in (4, 8, 13) else SKY
            c.blit(CIRCLE(r * 2, col + (255,), glow=col), x + 6 * math.sin(t * 1.3 + i), y + 5 * math.cos(t * 1.1 + i * 2), clamp(e), clamp(e), True)
    # not "dead weight": only the two words are struck through (red line through the middle)
    td = cue(11, "dead weight") - .45; da = E(pr(t, td, .45)); st = E(pr(t, cue(11, "dead weight") + .15, .5))
    f = font("d", "Medium", 50); w1 = f.getlength("not "); w2 = f.getlength("dead weight."); gx = 960 - (w1 + w2) / 2
    c.text("not ", gx, 905, "d", "Medium", 50, DIM, da)
    c.text("dead weight.", gx + w1, 905, "d", "Medium", 50, mix(DIM, (96, 108, 150), st), da)
    ymid = 905 + f.getmetrics()[0] - .30 * 50
    if st > .01: c.blit(BAR(int(w2 * st) // 6 * 6 + 6, 6, RED), gx + w1 - 4, ymid - 3, da)

# --------------------------------------------------------------------------- J  (TAIL) closing: "Solix CDP. Built for enterprise applications." -> end card
PROOF = ["20+ years of ERP archiving", "Native to SAP's Archive Development Kit", "Validated by Oracle for E-Business Suite"]
def end_card_t(): return VO[12]["end"] + 2.6
def scene_J(c, t):
    E12 = VO[12]["end"]; tg = E12 + .5                                  # "Built for" group leaves, end card builds
    out = 1 - E(pr(t, tg, .4)); a_sol = E(pr(t, cue(12, "Solix") - .1, .5))
    # Solix CDP stays; its tri-colour underline arrives with the end card
    sz = 120; cyS = 250 + (1 - a_sol) * 16
    ctext(c, "Solix CDP", 960, cyS, "d", "Bold", sz, WHITE, a_sol, track=3, anchor="c")
    wd = tw("Solix CDP", "d", "Bold", sz, 3)
    tri_underline(c, 960 - wd / 2, 335, wd, E(pr(t, tg + .25, .6)), 9)
    # "Built for" + one gradient pill + the three families
    tb = cue(12, "Built for") - .1; te = cue(12, "enterprise") - .1
    g0 = c.ga; c.ga = g0 * out
    ab = E(pr(t, tb, .45)); ae = E(pr(t, te, .5))
    f1 = font("d", "Bold", 64); wB = f1.getlength("Built for"); pw_ = int(tw("Enterprise Applications", "d", "Bold", 64) + 80); tot = wB + 26 + pw_; x = 960 - tot / 2
    c.text("Built for", x, 420 + (1 - ab) * 14, "d", "Bold", 64, WHITE, ab)
    if ae > .01:
        px_ = x + wB + 26; ph_ = 104; yy = 420 + f1.getmetrics()[0] - .363 * 64 + .07 * 64
        gd = np.zeros((ph_, pw_, 4), np.uint8)
        for k in range(pw_):
            u = k / max(1, pw_ - 1); col = mix(RED, BLUE, u / .5) if u < .5 else mix(BLUE, TEAL, (u - .5) / .5); gd[:, k, :3] = col; gd[:, k, 3] = 255
        gim = Image.fromarray(gd, "RGBA"); mk = BAR(pw_, ph_, (255, 255, 255)).split()[3]; gim.putalpha(mk)
        c.blit(gim, px_, yy - ph_ / 2, ae)
        ctext(c, "Enterprise Applications", px_ + pw_ / 2, yy, "d", "Bold", 64, WF, ae, anchor="c")
    fams = [("Oracle Applications", RED), ("SAP", BLUE), ("Mainframe", TEAL)]
    cw = [int(tw(n_.upper(), "i", "Bold", 24, 3) + 70) for n_, _ in fams]; x = 960 - (sum(cw) + 18 * 2) / 2
    for i, ((n_, col), w) in enumerate(zip(fams, cw)):
        ca = E(pr(t, te + .7 + i * .22, .35)); yy = 560 + (1 - ca) * 12
        c.card(x, yy - 28, w, 56, ca, outline=col + (220,), fill=CARD + (255,), r=28)
        c.blit(CIRCLE(12, col + (255,)), x + 26, yy, ca, 1, True); ctext(c, n_.upper(), x + 44, yy, "i", "Bold", 24, TXT, ca, track=3); x += w + 18
    c.ga = g0
    # end card: proof row, the one Solix logo, "Visit our booth", trademark lines
    sz2 = 28
    while sum(tw(p_, "i", "Medium", sz2) + 62 for p_ in PROOF) + 44 * 2 > 1760: sz2 -= 1
    ws = [tw(p_, "i", "Medium", sz2) + 62 for p_ in PROOF]; x = 960 - (sum(ws) + 44 * 2) / 2; tp = tg + .55
    for i, p_ in enumerate(PROOF):
        a = E(pr(t, tp + i * .3, .45)); yy = 450 + (1 - a) * 22; col = BLUE if i != 1 else RED
        c.blit(CIRCLE(36, col + (255,), glow=col), x + 18, yy, a, 1, True); c.icon("check", x + 18, yy, 20, WF, a)
        ctext(c, p_, x + 50, yy, "i", "Medium", sz2, TXT, a); x += ws[i] + 44
    ea = E(pr(t, end_card_t(), .8))
    if ea > .01:
        lg = LOGO(150); c.blit(lg, 960 - lg.width / 2, 540 - 14 * (1 - ea), ea)
        ctext(c, "Visit our booth", 960, 810, "d", "Bold", 54, SKY, E(pr(t, end_card_t() + .5, .6)), anchor="c")
        fa = E(pr(t, end_card_t() + .8, .7)) * .9
        for k, ln in enumerate(("SAP and SAP S/4HANA are trademarks or registered trademarks of SAP SE.",
                                "Oracle, Oracle E-Business Suite, PeopleSoft, JD Edwards and Siebel are trademarks or registered trademarks of Oracle and/or its affiliates.",
                                "IBM and IBM zSeries are trademarks or registered trademarks of International Business Machines Corporation.")):
            c.text(ln, 960, 960 + k * 24, "i", "Regular", 15, (118, 130, 170), fa, anchor="c")

SCENES = {"K": scene_K, "T": scene_T, "DA": scene_DA, "A": scene_A, "B": scene_B, "C": scene_C, "D": scene_D, "E": scene_E, "F": scene_F, "G": scene_G, "H": scene_H, "I": scene_I, "J": scene_J}

def energy(t):
    e = .35
    if SC["G"][0] - .05 < t < SC["G"][1] + .6: e = lerp(.35, 1.7, E(pr(t, SC["G"][0] - .05, .3))) * (1 - .5 * E(pr(t, SC["G"][1], .6)))
    if SC["I"][0] < t < SC["J"][0]: e = lerp(.4, 1.5, E(pr(t, cue(11, "becomes"), 1.2)))
    if t >= SC["J"][0]: e = lerp(1.2, .85, E(pr(t, VO[12]["end"] + .5, 1.5)))
    return e
