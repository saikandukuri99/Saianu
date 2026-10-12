# Screens for the opening and the five triggers (illustrative, fictional data):
# legacy application windows (ERP, green-screen mainframe, custom form) and the five
# notification screens (Cost, Risk, M&A, Old archive, AI). Each takes a quantised step
# so its inner animation can be cached frame to frame.
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from docs_ar import F, tracked, INK, MUTE, PAPER, INDIGO, BLUE, RED, TINT

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
@lru_cache(None)
def M(size): return ImageFont.truetype(MONO, size)

NW, NH = 1100, 640
def notice(head_col, kicker, title, sub):
    im = Image.new("RGBA", (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, NW-1, NH-1), 30, fill=PAPER + (255,))
    d.rounded_rectangle((0, 0, NW-1, 92), 30, fill=head_col + (255,)); d.rectangle((0, 60, NW-1, 92), fill=head_col + (255,))
    d.ellipse((40, 32, 66, 58), fill=(255, 255, 255) if head_col == RED else RED)
    d.text((86, 28), "Notification", font=F("Inter-SemiBold.otf", 30), fill=(255, 255, 255))
    d.text((NW-44, 30), "now", font=F("Inter-Medium.otf", 26), fill=(220, 222, 245), anchor="ra")
    tracked(d, (52, 130), kicker, F("Inter-SemiBold.otf", 22), RED if head_col == RED else MUTE, 4)
    d.text((52, 170), title, font=F("InterDisplay-Bold.otf", 54), fill=INK)
    d.text((52, 244), sub, font=F("Inter-Medium.otf", 28), fill=MUTE)
    return im, d

def eo(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x)**3

@lru_cache(None)
def trigger(kind, step):
    p = step/24.0
    if kind == "t1":
        im, d = notice(INDIGO, "LEGACY ERP  ·  VENDOR SUPPORT", "Annual maintenance renewal due", "For an application nobody uses day to day.")
        v = int(480000*eo(p*1.6))
        d.text((52, 330), "RENEWAL AMOUNT", font=F("Inter-SemiBold.otf", 22), fill=MUTE)
        d.text((52, 366), f"${v:,}", font=F("InterDisplay-Bold.otf", 110), fill=INK)
        d.text((52 + F("InterDisplay-Bold.otf", 110).getlength(f"${v:,}") + 18, 430), "/ year", font=F("Inter-Medium.otf", 34), fill=MUTE)
        d.text((52, 528), "Due in 14 days  ·  Auto-renews", font=F("Inter-Medium.otf", 28), fill=RED)
        bw = 300; g = .5 + .5*math.sin(p*14)
        d.rounded_rectangle((NW-52-bw, 512, NW-52, 584), 36, fill=tuple(int(c*(.85 + .15*g)) for c in BLUE))
        d.text((NW-52-bw/2, 548), "Review renewal", font=F("Inter-SemiBold.otf", 28), fill=(255, 255, 255), anchor="mm")
    elif kind == "t2":
        flash = (int(p*10) % 2 == 0)
        im, d = notice(RED if flash else (190, 24, 30), "SECURITY ALERT  ·  CRITICAL", "Critical vulnerability on an", "Vendor support has ended. No patch available.")
        d.rectangle((40, 160, NW-40, 300), fill=PAPER)
        d.text((52, 170), "Critical vulnerability on an", font=F("InterDisplay-Bold.otf", 54), fill=INK)
        d.text((52, 232), "unpatched legacy server", font=F("InterDisplay-Bold.otf", 54), fill=INK)
        d.text((52, 310), "Vendor support has ended. No patch available.", font=F("Inter-Medium.otf", 28), fill=MUTE)
        s = eo((p - .15)*3)
        if s > 0:
            w = int(260*s); d.rounded_rectangle((52, 380, 52 + max(w, 40), 470), 22, fill=(253, 232, 232))
            if s > .6: d.text((80, 396), "CVSS 9.8", font=F("InterDisplay-Bold.otf", 50), fill=RED)
        rows = [("Server", "fin-app-07  (Windows 2008)"), ("Patch status", "End of support")]
        for i, (k, v) in enumerate(rows):
            a = eo((p - .35 - i*.12)*4)
            if a > 0:
                col = tuple(int(255 - (255 - c)*a) for c in INK)
                d.text((360, 392 + i*50), k.upper(), font=F("Inter-SemiBold.otf", 20), fill=tuple(int(255 - (255 - c)*a) for c in MUTE))
                d.text((560, 386 + i*50), v, font=F("Inter-SemiBold.otf", 30), fill=col)
    elif kind == "t3":
        im, d = notice(INDIGO, "CORPORATE DEVELOPMENT", "Acquisition closed", "Inherited systems to absorb:")
        chips = ["ERP", "CRM", "HR", "Billing", "Data warehouse", "Payroll"]
        x, y = 52, 320
        for i, c in enumerate(chips):
            a = eo((p - i*.11)*4)
            f = F("Inter-SemiBold.otf", 32); tw = f.getlength(c) + 70
            if x + tw > NW - 52: x, y = 52, y + 100
            if a > 0:
                dy = int((1 - a)*40)
                fill = tuple(int(255 - (255 - c2)*a) for c2 in TINT)
                d.rounded_rectangle((x, y + dy, x + tw, y + 76 + dy), 20, fill=fill, outline=tuple(int(255 - (255 - c2)*a) for c2 in (200, 202, 222)), width=2)
                d.text((x + tw/2, y + 38 + dy), c, font=f, fill=tuple(int(255 - (255 - c2)*a) for c2 in INK), anchor="mm")
            x += tw + 22
        n = min(6, int(p*7.5))
        d.text((52, 560), f"{n} systems  ·  3 vendors  ·  2 data centres", font=F("Inter-Medium.otf", 28), fill=MUTE)
    elif kind == "t4":
        im, d = notice(INDIGO, "ARCHIVE PLATFORM", "Archive renewal date approaching", "Data inside: retained, but no business context and no AI access.")
        d.text((52, 330), "NOVEMBER", font=F("Inter-SemiBold.otf", 22), fill=MUTE)
        for i, day in enumerate(range(9, 16)):
            x = 52 + i*140; y = 380
            d.rounded_rectangle((x, y, x + 116, y + 116), 22, fill=TINT)
            d.text((x + 58, y + 58), str(day), font=F("InterDisplay-SemiBold.otf", 46), fill=INK, anchor="mm")
            if day == 13:
                a = eo((p - .15)*2.2)
                if a > 0:
                    d.arc((x - 16, y - 16, x + 132, y + 132), -90, -90 + 360*a, fill=RED, width=9)
        a = eo((p - .5)*3)
        if a > 0:
            d.text((52, 545), "Renewal in 4 days  ·  Storage contract", font=F("Inter-SemiBold.otf", 30),
                   fill=tuple(int(255 - (255 - c)*a) for c in RED))
    elif kind == "t5":
        im, d = notice(INDIGO, "AI PROGRAM  ·  TRAINING AND GROUNDING DATA", "Historical data needed", "Twenty years of history sits in retired applications.")
        base = 560; xs = [52 + i*144 for i in range(7)]
        hs = [150, 190, 170, 230]
        for i, x in enumerate(xs):
            if i < 4:
                h = int(hs[i]*eo((p - i*.1)*3))
                if h > 2: d.rounded_rectangle((x, base - h, x + 116, base), 12, fill=BLUE)
            else:
                g = .5 + .5*math.sin(p*12 + i)
                col = tuple(int(c) for c in (200 + 30*g, 202 + 30*g, 222 + 20*g))
                for yy in range(base - 230, base, 22):
                    d.line((x, yy, x, yy + 11), fill=col, width=3); d.line((x + 116, yy, x + 116, yy + 11), fill=col, width=3)
                for xx in range(x, x + 116, 22):
                    d.line((xx, base - 230, xx + 11, base - 230), fill=col, width=3); d.line((xx, base, xx + 11, base), fill=col, width=3)
        d.text((xs[4] + 20, base - 266), "Missing history", font=F("Inter-SemiBold.otf", 28), fill=RED)
        d.text((52, base + 30), "2006", font=F("Inter-Medium.otf", 24), fill=MUTE)
        d.text((NW - 52, base + 30), "2026", font=F("Inter-Medium.otf", 24), fill=MUTE, anchor="ra")
    return im

# ---------------------------------------------------------------- legacy application windows (opening)
SLATE = (30, 33, 52); SLATE2 = (44, 48, 72); DIM = (150, 156, 186)
def window(w, h, title, bar=SLATE2, body=SLATE):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w-1, h-1), 22, fill=body + (246,))
    d.rounded_rectangle((0, 0, w-1, 64), 22, fill=bar + (255,)); d.rectangle((0, 40, w-1, 64), fill=bar + (255,))
    for i, c in enumerate([(120, 124, 150), (120, 124, 150), (120, 124, 150)]):
        d.ellipse((24 + i*30, 22, 42 + i*30, 40), fill=c)
    d.text((130, 18), title, font=F("Inter-SemiBold.otf", 26), fill=(200, 204, 226))
    return im, d

@lru_cache(None)
def legacy(kind):
    if kind == "erp":
        im, d = window(1000, 640, "Finance ERP  R11  —  General Ledger")
        tabs = ["Journals", "Accounts", "Periods", "Reports"]
        for i, t in enumerate(tabs):
            d.text((40 + i*170, 92), t, font=F("Inter-Medium.otf", 26), fill=(230, 232, 248) if i == 0 else DIM)
        heads = ["JE #", "PERIOD", "ACCOUNT", "AMOUNT"]
        for i, hd in enumerate(heads): d.text((40 + i*235, 160), hd, font=F("Inter-SemiBold.otf", 20), fill=DIM)
        for r in range(6):
            y = 205 + r*58
            if r % 2 == 0: d.rounded_rectangle((24, y - 12, 976, y + 40), 10, fill=SLATE2)
            row = [f"JE-0{4410 + r*7}", f"P0{(r % 9) + 1}-2018", f"4{100 + r*13}-000", f"{(r*7919 % 90000) + 1200:,}.00"]
            for i, v in enumerate(row): d.text((40 + i*235, y), v, font=F("Inter-Medium.otf", 26), fill=(205, 208, 228))
        d.text((40, 580), "Read-only  ·  Last login 214 days ago", font=F("Inter-Medium.otf", 24), fill=DIM)
    elif kind == "mf":
        im, d = window(900, 600, "TN3270  —  ACCT.INQ", bar=(26, 30, 26), body=(6, 12, 8))
        G = (64, 230, 120); G2 = (40, 150, 80)
        lines = ["CICS  ACCOUNT INQUIRY            SYS: PRD1", "", "ACCT NO ...... 00418-22713", "CUSTOMER ..... HALDEN IND SUPPLY",
                 "STATUS ....... ACTIVE", "BALANCE ...... 0000039250.00", "LAST TXN ..... 1998-04-12", "",
                 "PF1=HELP  PF3=EXIT  PF7=BKWD  PF8=FWD", "==> _"]
        for i, l in enumerate(lines): d.text((36, 92 + i*46), l, font=M(28), fill=G if i in (0, 9) else G2)
    else:
        im, d = window(860, 620, "Plant Maintenance Tracker v2.3")
        d.rounded_rectangle((24, 84, 836, 134), 12, fill=(92, 40, 48))
        d.text((44, 94), "Unsupported since 2017", font=F("Inter-SemiBold.otf", 26), fill=(255, 200, 200))
        fields = [("Work order", "WO-20931"), ("Asset", "Compressor C-4"), ("Technician", "—"), ("Status", "Open")]
        for i, (k, v) in enumerate(fields):
            y = 170 + i*92
            d.text((44, y), k.upper(), font=F("Inter-SemiBold.otf", 20), fill=DIM)
            d.rounded_rectangle((44, y + 30, 816, y + 78), 10, fill=SLATE2)
            d.text((62, y + 38), v, font=F("Inter-Medium.otf", 26), fill=(205, 208, 228))
        d.rounded_rectangle((616, 552, 816, 602), 25, fill=(70, 74, 100))
        d.text((716, 577), "Submit", font=F("Inter-SemiBold.otf", 26), fill=DIM, anchor="mm")
    return im
