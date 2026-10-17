# Product screens for the 60-second overview (illustrative, fictional demo data):
# Solix Common Data Platform archive console, compliance policy with masking, CDP Navigator Data Ask.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ar"))
from functools import lru_cache
from PIL import Image, ImageDraw
from docs_ar import F, tracked, INK, MUTE, PAPER, INDIGO, BLUE, RED, TINT, icon as _icon

NAVY = (14, 34, 82)
def eo(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x)**3
def mix(c, a): return tuple(int(255 - (255 - v)*a) for v in c)

def frame(w, h, title, sub, head=NAVY):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w-1, h-1), 30, fill=PAPER + (255,))
    d.rounded_rectangle((0, 0, w-1, 118), 30, fill=head + (255,)); d.rectangle((0, 80, w-1, 118), fill=head + (255,))
    im.alpha_composite(_icon(48), (36, 34))
    d.text((100, 30), title, font=F("InterDisplay-SemiBold.otf", 36), fill=(255, 255, 255))
    d.text((100, 74), sub, font=F("Inter-Medium.otf", 22), fill=(190, 205, 235))
    return im, d

SETS = [("Finance ERP", "Structured", 6747325), ("HR system", "Structured", 1204118), ("CRM", "Structured", 2981440),
        ("Email archive", "Unstructured", 845210), ("Contracts & PDFs", "Unstructured", 312904)]
@lru_cache(None)
def cdp(step):
    """Common Data Platform archive console: datasets land and their record counts fill in."""
    p = step/30.0
    w, h = 1100, 760
    im, d = frame(w, h, "Solix Common Data Platform", "Secure, governed archive")
    hf = F("Inter-SemiBold.otf", 20)
    for x, lab in ((48, "SOURCE"), (430, "TYPE"), (700, "RECORDS ARCHIVED"), (970, "")): d.text((x, 146), lab, font=hf, fill=MUTE)
    for i, (name, typ, n) in enumerate(SETS):
        y = 190 + i*92
        k = eo((p - i*.12)*2.4)
        if k <= 0: continue
        d.rounded_rectangle((28, y - 14, w - 28, y + 62), 16, fill=mix(TINT, k))
        d.text((48, y), name, font=F("InterDisplay-SemiBold.otf", 32), fill=mix(INK, k))
        col = BLUE if typ == "Structured" else (40, 150, 120)
        f = F("Inter-SemiBold.otf", 22); tw = f.getlength(typ) + 32
        d.rounded_rectangle((430, y + 2, 430 + tw, y + 42), 20, fill=mix(tuple(int(c*.14 + 255*.86) for c in col), k))
        d.text((446, y + 10), typ, font=f, fill=mix(col, k))
        c = eo((p - .15 - i*.1)*2.6)
        d.text((920, y + 2), f"{int(n*c):,}", font=F("Inter-SemiBold.otf", 30), fill=mix(INK, k), anchor="ra")
        if c >= 1: d.text((1010, y - 2), "✓", font=F("InterDisplay-Bold.otf", 36), fill=BLUE)
    a = eo((p - .8)*5)
    if a > 0:
        d.rounded_rectangle((28, h - 106, w - 28, h - 30), 20, fill=mix((225, 240, 250), a))
        d.text((64, h - 88), "✓  12,090,997 records archived  ·  Encrypted  ·  Governed", font=F("InterDisplay-SemiBold.otf", 30), fill=mix(BLUE, a))
    return im

@lru_cache(None)
def policy(step):
    """Compliance policy: retention, legal hold, masking of sensitive fields, defensible deletion."""
    p = step/30.0
    w, h = 1100, 820
    im, d = frame(w, h, "Records & Compliance Policy", "Finance ERP archive  ·  Policy-based")
    rows = [("Retention", "7 years after fiscal close"), ("Legal hold", "Active  ·  2 matters"), ("eDiscovery", "Indexed  ·  searchable")]
    for i, (k, v) in enumerate(rows):
        y = 146 + i*84; a = eo((p - i*.08)*3)
        d.text((48, y), k.upper(), font=F("Inter-SemiBold.otf", 20), fill=mix(MUTE, a))
        d.text((48, y + 28), v, font=F("InterDisplay-SemiBold.otf", 32), fill=mix(INK, a))
        d.text((w - 60, y + 22), "✓", font=F("InterDisplay-Bold.otf", 38), fill=mix(BLUE, a), anchor="ra")
    # sensitive data: identified, then masked
    y0 = 420
    d.text((48, y0), "SENSITIVE DATA", font=F("Inter-SemiBold.otf", 20), fill=MUTE)
    recs = [("Employee SSN", "471-82-6639", "•••-••-6639"), ("Bank account", "0042 7781 5530", "•••• •••• 5530")]
    for i, (k, raw, masked) in enumerate(recs):
        y = y0 + 36 + i*70
        found = p > .35 + i*.05; mk = p > .5 + i*.06
        d.rounded_rectangle((28, y - 8, w - 28, y + 52), 14, fill=(253, 236, 236) if (found and not mk) else TINT)
        d.text((48, y + 4), k, font=F("Inter-Medium.otf", 28), fill=INK)
        d.text((560, y + 2), masked if mk else raw, font=F("InterDisplay-SemiBold.otf", 30), fill=BLUE if mk else (INK if not found else RED))
        tag = "Masked" if mk else ("Identified" if found else "")
        if tag:
            f = F("Inter-SemiBold.otf", 20); tw = f.getlength(tag) + 28
            col = BLUE if mk else RED
            d.rounded_rectangle((w - 60 - tw, y + 6, w - 60, y + 42), 18, fill=tuple(int(c*.14 + 255*.86) for c in col))
            d.text((w - 60 - tw + 14, y + 13), tag, font=f, fill=col)
    # defensible deletion when retention ends
    y = 640
    a = eo((p - .7)*4)
    if a > 0:
        d.text((48, y), "RETENTION ENDED  ·  DEFENSIBLE DELETION", font=F("Inter-SemiBold.otf", 20), fill=mix(MUTE, a))
        d.rounded_rectangle((48, y + 40, w - 48, y + 76), 18, fill=mix(TINT, a))
        k = eo((p - .78)*5)
        d.rounded_rectangle((48, y + 40, 48 + (w - 96)*k, y + 76), 18, fill=mix(BLUE, a))
        d.text((w - 48, y + 92), "Records past 2018 schedule deleted  ·  Certificate logged" if k >= 1 else "Deleting expired records…",
               font=F("Inter-SemiBold.otf", 22), fill=mix(BLUE if k >= 1 else MUTE, a), anchor="ra")
    return im

Q = "Which vendors were paid late most often in 2019?"
ANS = [("Halden Industrial Supply", "42", "18 days"), ("Brightwater Metals", "31", "11 days"), ("Corrin Logistics", "27", "9 days")]
@lru_cache(None)
def data_ask(nq, think, ans):
    """CDP Navigator, Data Ask: a plain-language question, a moment of thinking, an instant cited answer."""
    w, h = 1240, 780
    im, d = frame(w, h, "CDP Navigator  ·  Data Ask", "Talk to your archived data")
    # question bubble (user)
    q = Q[:nq]
    if nq:
        f = F("InterDisplay-Medium.otf", 32); tw = min(w - 200, f.getlength(Q) + 60)
        d.rounded_rectangle((w - 48 - tw, 150, w - 48, 224), 26, fill=BLUE)
        d.text((w - 48 - tw + 30, 168), q, font=f, fill=(255, 255, 255))
        if nq < len(Q): x = w - 48 - tw + 30 + f.getlength(q) + 3; d.rectangle((x, 170, x + 3, 206), fill=(255, 255, 255))
    if think > 0 and ans <= 0:
        for k in range(3):
            r = 9 + 4*max(0, math.sin(think*8 - k*.9))
            d.ellipse((80 + k*36 - r, 290 - r, 80 + k*36 + r, 290 + r), fill=(150, 170, 210))
        d.text((200, 276), "Searching archived Finance ERP…", font=F("Inter-Medium.otf", 24), fill=MUTE)
    if ans > 0:
        a = eo(ans*2.5)
        d.rounded_rectangle((48, 252, w - 160, 700), 26, fill=mix(TINT, a))
        d.text((84, 276), "Three vendors account for most late payments in 2019:", font=F("InterDisplay-Medium.otf", 30), fill=mix(INK, a))
        hf = F("Inter-SemiBold.otf", 20)
        for x, lab in ((84, "VENDOR"), (640, "LATE PAYMENTS"), (860, "AVG DAYS LATE")): d.text((x, 340), lab, font=hf, fill=mix(MUTE, a))
        for i, (v, n, dl) in enumerate(ANS):
            k = eo((ans - .15 - i*.12)*4)
            if k <= 0: continue
            y = 380 + i*70
            d.rounded_rectangle((64, y - 10, w - 180, y + 48), 14, fill=mix((255, 255, 255), k))
            d.text((84, y), v, font=F("InterDisplay-SemiBold.otf", 30), fill=mix(INK, k))
            d.text((640, y), n, font=F("InterDisplay-SemiBold.otf", 30), fill=mix(INK, k))
            d.text((860, y), dl, font=F("InterDisplay-SemiBold.otf", 30), fill=mix(INK, k))
        k = eo((ans - .55)*4)
        if k > 0:
            d.text((84, 610), "⚡ Answered in 1.8 s", font=F("Inter-SemiBold.otf", 24), fill=mix(BLUE, k))
            x = 360
            for s in ("Source 1", "Source 2", "Source 3"):
                f = F("Inter-SemiBold.otf", 20); tw = f.getlength(s) + 28
                d.rounded_rectangle((x, 606, x + tw, 640), 17, fill=mix((220, 236, 250), k)); d.text((x + 14, 612), s, font=f, fill=mix(BLUE, k)); x += tw + 12
    if nq == 0 and ans <= 0:   # empty state: suggested questions
        d.text((w/2, 250), "What would you like to know?", font=F("InterDisplay-SemiBold.otf", 40), fill=INK, anchor="mm")
        d.text((w/2, 300), "Ask in plain language. Answers come from your archived applications.", font=F("Inter-Medium.otf", 24), fill=MUTE, anchor="mm")
        for i, sug in enumerate(("Show invoices over $10K from 2018", "Which contracts expire this year?", "Top suppliers by spend, 2015–2019")):
            f = F("Inter-SemiBold.otf", 26); tw = f.getlength(sug) + 60; y = 380 + i*84
            d.rounded_rectangle((w/2 - tw/2, y, w/2 + tw/2, y + 60), 30, fill=(232, 242, 252), outline=(190, 215, 240), width=2)
            d.text((w/2, y + 30), sug, font=f, fill=BLUE, anchor="mm")
    # input bar
    d.rounded_rectangle((48, h - 70, w - 48, h - 22), 24, fill=TINT)
    d.text((80, h - 60), "Ask anything about your archived data…", font=F("Inter-Medium.otf", 24), fill=MUTE)
    return im
