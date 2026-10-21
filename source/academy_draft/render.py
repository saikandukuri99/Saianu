"""Solix Academy intro - first draft. Pure motion graphics (no stock footage) + the three presenter clips.
Usage: render.py WORK_DIR UPLOADS_DIR OUT_DIR   (WORK_DIR holds the VO wavs + dur.json from vo.py)
Writes OUT_DIR/video_only.mp4 and OUT_DIR/audio_schedule.json (file, start) for mixing.
"""
import sys, json, math, glob, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORK, UP, OUT = sys.argv[1:4]
SRC = "/home/user/Saianu/source/assets"
W, H, FPS = 1920, 1080, 25
D = json.load(open(f"{WORK}/dur.json"))
FD = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
NAVY, BLUE, RED, WHITE = (8, 16, 38), (46, 120, 205), (229, 34, 41), (255, 255, 255)

_f = {}
def font(w, s):
    if (w, s) not in _f: _f[(w, s)] = ImageFont.truetype(FD % w, s)
    return _f[(w, s)]
def clamp(x): return max(0.0, min(1.0, x))
def p(t, a, d): return clamp((t - a) / d)
def eo(x): return 1 - (1 - x) ** 3
def eb(x):
    c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def col(c, a): return (*c, int(255 * clamp(a)))

def text(ov, s, xy, size, a=1.0, w="Bold", c=WHITE, anchor="mm"):
    if a > 0.01: ImageDraw.Draw(ov).text(xy, s, font=font(w, size), fill=col(c, a), anchor=anchor)

def rrect(ov, box, r, fill=None, outline=None, width=2):
    ImageDraw.Draw(ov).rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

# ---------- background: slow blue swirl ----------
_yy, _xx = np.mgrid[0:135, 0:240].astype(np.float32)
_xx = _xx / 240 * 3.2; _yy = _yy / 135 * 1.8
def background(t, glow=0.0):
    r = np.hypot(_xx - 1.6, _yy - 0.9)
    v = (np.sin(_xx * 2.1 + t * .35 + np.sin(_yy * 2 + t * .2)) + np.sin(r * 4 - t * .4) + np.sin(_yy * 3.1 - t * .3 + _xx)) / 3
    v = (v + 1) / 2
    vig = np.clip(1.15 - r * .38, .25, 1)
    k = (v * vig)[..., None]
    c0, c1 = np.array(NAVY, np.float32), np.array((22, 62, 118), np.float32)
    img = c0 + (c1 - c0) * k * (.55 + glow * .4)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)

# ---------- shared bits ----------
logo_w = Image.open(f"{SRC}/logo_white.png").convert("RGBA")
def logo(ov, cx, cy, width, a=1.0, academy=True):
    h = int(width * logo_w.height / logo_w.width)
    im = logo_w.resize((width, h), Image.LANCZOS)
    if a < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    ov.alpha_composite(im, (int(cx - width / 2), int(cy - h / 2)))
    if academy: text(ov, "Academy", (cx + width / 2 + 14, cy + h * .02), int(h * .62), a, "Medium", WHITE, "lm")

def corner_logo(ov, a=1.0):
    im = logo_w.resize((230, int(230 * logo_w.height / logo_w.width)), Image.LANCZOS)
    if a < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * a * .8)))
    ov.alpha_composite(im, (W - 290, 52))

rng = random.Random(7)
NODES = [(rng.uniform(.04, .96) * W, rng.uniform(.06, .94) * H, rng.uniform(0, 6.28)) for _ in range(70)]
def network(ov, t, zoom=1.0, a=1.0, conv=0.0):
    pts = []
    for x, y, ph in NODES:
        x = W / 2 + (x - W / 2 + 14 * math.sin(t * .6 + ph)) * zoom
        y = H / 2 + (y - H / 2 + 14 * math.cos(t * .5 + ph)) * zoom
        x += (W / 2 - x) * conv; y += (H / 2 - y) * conv
        pts.append((x, y))
    d = ImageDraw.Draw(ov)
    for i, (x, y) in enumerate(pts):
        for j in range(i + 1, len(pts)):
            dist = math.hypot(x - pts[j][0], y - pts[j][1])
            if dist < 260 * zoom: d.line([(x, y), pts[j]], fill=col((120, 180, 255), a * .28 * (1 - dist / (260 * zoom))), width=2)
    for i, (x, y) in enumerate(pts):
        r = 4 + 2 * math.sin(t * 2 + i)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col((190, 225, 255), a * .85))

def title_block(ov, lt, line1, line2=None, y=540, size=120):
    k = eo(p(lt, 0, .8))
    text(ov, line1, (W / 2, y + (1 - k) * 40), size, k)
    if line2: text(ov, line2, (W / 2, y + 100 + (1 - eo(p(lt, .4, .8))) * 30), 44, eo(p(lt, .4, .8)), "Regular", (190, 215, 245))

# ---------- scenes ----------
def sc_power(ov, lt, dur):
    zoom = 1 + .35 * (lt / dur) if lt < dur * .55 else 1.19 - .25 * ((lt - dur * .55) / (dur * .45))
    network(ov, lt, zoom, eo(p(lt, 0, 1.5)))
    k = eb(p(lt, 3.0, .9))
    text(ov, "Power of AI", (W / 2, 470), int(150 * max(k, .01)), p(lt, 3.0, .5))
    for i, s in enumerate(["Every business", "Every team", "Every employee"]):
        a = eo(p(lt, 3.9 + i * 1.5, .7))
        text(ov, s, (W / 2 + (i - 1) * 520, 640 + (1 - a) * 25), 42, a, "Regular", (190, 215, 245))
        if a > .02: ImageDraw.Draw(ov).line([(W / 2 + (i - 1) * 520 - 90, 690), (W / 2 + (i - 1) * 520 + 90, 690)], fill=col(RED, a), width=4)

DEPTS = ["Sales", "Marketing", "Finance", "HR", "Operations", "Customer Support"]
def sc_depts(ov, lt, dur):
    network(ov, lt + 20, 1.1, .25)
    text(ov, "Every function. One shift.", (W / 2, 120), 56, eo(p(lt, 0, .8)), "SemiBold")
    for i, s in enumerate(DEPTS):
        cx, cy = 360 + (i % 3) * 600, 330 + (i // 3) * 190
        on = eo(p(lt, .5 + i * .45, .5)); pop = eb(p(lt, .3 + i * .45, .5))
        w, h = 500 * (.85 + .15 * pop), 130 * (.85 + .15 * pop)
        box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
        if on > .02: rrect(ov, [b + o for b, o in zip(box, (-8, -8, 8, 8))], 40, col(RED, on * .18))
        rrect(ov, box, 34, col((255, 255, 255), .06 + .0 * on), col(RED if on > .5 else (120, 160, 210), .4 + .6 * on), 3)
        text(ov, s, (cx, cy), 46, clamp(pop * 1.5), "SemiBold")
    caps = [(2.0, "Faster decisions"), (3.9, "Smarter operations"), (5.6, "Personalized experiences"), (8.0, "Ideas in days, not months")]
    for i, (a0, s) in enumerate(caps):
        a_in = eo(p(lt, a0, .6)); a_out = 1 - p(lt, caps[i + 1][0] - .1, .3) if i < 3 else 1
        text(ov, s, (W / 2, 800 + (1 - a_in) * 30), 78, a_in * a_out, "Bold")

def sc_how(ov, lt, dur):
    network(ov, lt + 40, 1.0, .2)
    if lt < 2.9:
        for i in range(3):
            k = eb(p(lt, .1 + i * .3, .6)); text(ov, "?", (W / 2 + (i - 1) * 190, 520 + math.sin(lt * 3 + i) * 12), int(300 * max(k, .01)), clamp(k), "Bold", RED if i == 1 else WHITE)
        text(ov, "How?", (W / 2, 780), 64, eo(p(lt, 1.0, .6)), "Regular", (190, 215, 245))
    else:
        for i in range(3):
            k = eb(p(lt - 2.9, .15 + i * .35, .55)); r = 120 * max(k, .01); cx = W / 2 + (i - 1) * 420
            ImageDraw.Draw(ov).ellipse([cx - r, 540 - r, cx + r, 540 + r], fill=col(RED if i == 0 else BLUE, clamp(k)))
            text(ov, str(i + 1), (cx, 540), int(130 * max(k, .01)), clamp(k))
            if i < 2: ImageDraw.Draw(ov).line([(cx + 150, 540), (cx + 270, 540)], fill=col((200, 220, 250), clamp(k) * .6), width=4)

PILLARS = [
    ("AI-Ready Data", "Well-structured information", "A modern foundation that makes intelligence possible at scale"),
    ("AI-Ready People", "Lead AI-driven transformation", "A workforce that thinks differently and spots new opportunities"),
    ("AI-Ready Enterprise", "Models, agents and the right people", "The right technology and the right teams, together"),
]
CLIPS = ["45d10521", "37b87ee6", "079e1503"]
MASK = Image.new("L", (760, 760), 0); ImageDraw.Draw(MASK).rounded_rectangle([0, 0, 759, 759], 40, fill=255)

class Presenter:
    def __init__(self, idx):
        self.f = glob.glob(f"{UP}/{CLIPS[idx]}*.mp4")[0]; self.proc = None; self.first = None
    def frame(self, n):
        if self.proc is None:
            self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", self.f, "-vf", "crop=960:960:480:20,scale=760:760", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        b = self.proc.stdout.read(760 * 760 * 3)
        if len(b) < 760 * 760 * 3: return self.last
        self.last = Image.fromarray(np.frombuffer(b, np.uint8).reshape(760, 760, 3)); return self.last

def make_pillar(idx):
    title, sub, desc = PILLARS[idx]
    pd = D[f"p{idx+1}"]
    cdur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", glob.glob(f"{UP}/{CLIPS[idx]}*.mp4")[0]]))
    cstart = pd + .3
    pr = Presenter(idx); state = {"n": 0}
    def sc(ov, lt, dur, base):
        k = eo(p(lt, .2, .9))
        # big title first, then settles to the right column
        shift = eo(p(lt, pd - .2, .8))
        for i in range(3):
            cx = W / 2 + (i - 1) * 190 - shift * (W / 2 + (i - 1) * 190 - (1030 + i * 76))
            cy = 120 + (0 if shift < 1 else 0)
            r = 26 if i != idx else 34
            ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col(RED if i == idx else (255, 255, 255), .95 if i == idx else .22))
            text(ov, str(i + 1), (cx, cy), 26 if i != idx else 32, 1)
        fs = int(130 - 46 * shift); ty = 540 - shift * 160
        tx = (W / 2 - font("Bold", fs).getlength(title) / 2) * (1 - shift) + 1000 * shift
        text(ov, title, (tx, ty), fs, k, "Bold", WHITE, "lm")
        a2 = eo(p(lt, cstart, .7))
        if a2 > .01:
            ImageDraw.Draw(ov).line([(1000, 500), (1000 + 120 * a2, 500)], fill=col(RED, a2), width=5)
            text(ov, sub, (1000, 570 + (1 - a2) * 20), 52, a2, "SemiBold", WHITE, "lm")
            text(ov, desc, (1000, 650 + (1 - a2) * 20), 30, a2 * .85, "Regular", (190, 215, 245), "lm")
        # presenter
        ia = eo(p(lt, pd - .1, .9))
        if ia > .01:
            if lt < cstart:
                if pr.first is None: pr.first = pr.frame(0)
                fr = pr.first
            else: fr = pr.frame(1)
            x0 = int(130 - (1 - ia) * 160); y0 = 160
            glow = Image.new("RGBA", (800, 800), (0, 0, 0, 0)); rrect(glow, [20, 20, 780, 780], 50, col(BLUE, .5 * ia))
            glow = glow.filter(ImageFilter.GaussianBlur(26)); ov.alpha_composite(glow, (x0 - 20, y0 - 20))
            im = fr.convert("RGBA"); im.putalpha(MASK.point(lambda v: int(v * ia))); ov.alpha_composite(im, (x0, y0))
    return sc, pd + .3 + cdur + .6, cstart, cdur

COURSES = ["Common Data Platform", "Data Engineering", "Data Governance & Compliance", "Business Productivity", "Application Retirement",
           "Machine Learning Operations", "Forward Deployed Engineering", "Next-Gen AI Engineering", "Solix GPT", "RAG"]
def sc_logo(ov, lt, dur):
    network(ov, lt + 60, 1.0, .15)
    k = eb(p(lt, .2, 1.0))
    r = 260 + 80 * eo(p(lt, 0, 3)); a = (1 - p(lt, 0, 3)) * .5
    ImageDraw.Draw(ov).ellipse([W / 2 - r, 300 - r * .55, W / 2 + r, 300 + r * .55], outline=col(RED, a), width=4)
    logo(ov, W / 2 - 150, 300, int(560 * max(k, .02)), clamp(k))
    text(ov, "Learn. Innovate. Transform.", (W / 2, 430), 44, eo(p(lt, 1.2, .8)), "Regular", (190, 215, 245))
    text(ov, "A premier learning platform for professionals, teams and enterprises", (W / 2, 520), 34, eo(p(lt, 1.8, .8)) * .9, "Regular", (225, 235, 250))
    t0 = 3.2; step = (dur - t0 - .4) / len(COURSES)
    for i, s in enumerate(COURSES):
        a0 = t0 + i * step; x = (lt - a0) / step
        if 0 <= x < 1:
            a = min(1, x * 6) * min(1, (1 - x) * 5)
            w = font("SemiBold", 62).getlength(s) + 120
            rrect(ov, [W / 2 - w / 2, 690, W / 2 + w / 2, 810], 60, col(RED, .85 * a))
            text(ov, s, (W / 2, 750 + (1 - min(1, x * 6)) * 14), 62, a, "SemiBold")
    text(ov, f"{min(len(COURSES), max(0, int((lt - t0) / step) + 1)) if lt > t0 else 0} / {len(COURSES)} programs" if False else "", (W / 2, 900), 28, 1)

def person(ov, cx, cy, s, a):
    d = ImageDraw.Draw(ov); c = col((150, 175, 210), a * .55)
    d.ellipse([cx - 38 * s, cy - 100 * s, cx + 38 * s, cy - 24 * s], fill=c)
    d.pieslice([cx - 80 * s, cy - 8 * s, cx + 80 * s, cy + 150 * s], 180, 360, fill=c)

def sc_faculty(ov, lt, dur):
    network(ov, lt + 80, 1.0, .12)
    text(ov, "Learn from the best", (W / 2, 100), 64, eo(p(lt, 0, .7)))
    rows = [("Distinguished professors", .5), ("Leading AI practitioners & enterprise experts", 4.3)]
    for ri, (lab, t0) in enumerate(rows):
        y = 330 + ri * 360
        text(ov, lab, (160, y - 180), 34, eo(p(lt, t0, .5)), "SemiBold", (190, 215, 245), "lm")
        for i in range(4):
            a0 = t0 + .15 + i * .3; k = eb(p(lt, a0, .7)); a = clamp(k)
            cx = 345 + i * 410; off = (1 - eo(p(lt, a0, .7))) * 120
            rrect(ov, [cx - 160, y - 140 + off, cx + 160, y + 140 + off], 28, col((255, 255, 255), .08 * a), col((120, 170, 230), .6 * a), 3)
            person(ov, cx, y - 50 + off, 1.1, a)
            text(ov, "Faculty name", (cx, y + 78 + off), 28, a, "SemiBold")
            text(ov, "Title / organisation", (cx, y + 110 + off), 22, a * .8, "Regular", (190, 215, 245))
    text(ov, "DRAFT PLACEHOLDER - replace with faculty photos", (W / 2, 1040), 22, .6, "Regular", (255, 190, 190))

def sc_class(ov, lt, dur):
    network(ov, lt + 90, 1.0, .12)
    text(ov, "Learning that feels like the real thing", (W / 2, 100), 60, eo(p(lt, 0, .7)))
    caps = ["Real-world use cases", "Hands-on labs", "Enterprise projects"]
    for i, s in enumerate(caps):
        a0 = .5 + i * .6; k = eb(p(lt, a0, .8)); a = clamp(k); cx = 330 + i * 630
        sc = .85 + .15 * k
        box = [cx - 290 * sc, 420 - 190 * sc, cx + 290 * sc, 420 + 190 * sc]
        rrect(ov, box, 24, col((255, 255, 255), .07 * a), col((120, 170, 230), .7 * a), 3)
        text(ov, "Empower session photo", (cx, 420), 28, a * .55, "Regular", (190, 215, 245))
        text(ov, s, (cx, 700), 44, a, "SemiBold")
        ImageDraw.Draw(ov).line([(cx - 60, 750), (cx + 60 * a, 750)], fill=col(RED, a), width=5)
    text(ov, "DRAFT PLACEHOLDER - replace with classroom shots", (W / 2, 1040), 22, .6, "Regular", (255, 190, 190))

def sc_goals(ov, lt, dur):
    network(ov, lt + 100, 1.0, .2)
    items = [(1.0, "Your people grow"), (3.8, "Your teams discover new possibilities"), (6.3, "Your company gets more from its AI")]
    for i, (a0, s) in enumerate(items):
        y = 330 + i * 190; a = eo(p(lt, a0, .7)); k = eb(p(lt, a0, .6))
        ImageDraw.Draw(ov).ellipse([420 - 44 * k, y - 44 * k, 420 + 44 * k, y + 44 * k], fill=col(RED, clamp(k)))
        d = ImageDraw.Draw(ov)
        if a > .3: d.line([(402, y + 2), (415, y + 16), (440, y - 14)], fill=col(WHITE, a), width=8, joint="curve")
        text(ov, s, (510 + (1 - a) * 60, y), 62, a, "SemiBold", WHITE, "lm")

def sc_final(ov, lt, dur, t_c3, t_c4):
    conv = eo(p(lt, 0, 3.2)) * .92
    network(ov, lt + 120, 1.0 - .3 * conv, 1.0 - .9 * p(lt, t_c3 - .5, .8), conv)
    ti = eo(p(lt, 1.0, .9)) * (1 - p(lt, t_c3 - .3, .5))
    text(ov, "Learn, adapt, innovate - faster.", (W / 2, 540), 70, ti, "SemiBold")
    k = eb(p(lt, t_c3, 1.0))
    if k > .01:
        logo(ov, W / 2 - 150, 430, int(620 * max(k, .02)), clamp(k))
        text(ov, "Learn.  Innovate.  Transform.", (W / 2, 560), 50, eo(p(lt, t_c3 + .9, .8)), "Regular", (210, 228, 250))
    ya = eo(p(lt, t_c4, .8))
    text(ov, "Your AI journey starts here.", (W / 2, 720 + (1 - ya) * 30), 74, ya, "Bold")
    ImageDraw.Draw(ov).line([(W / 2 - 260, 790), (W / 2 - 260 + 520 * ya, 790)], fill=col(RED, ya), width=6)

# ---------- timeline ----------
GAP = .35
sched = []     # audio schedule
scenes = []    # (dur, fn)
t = 0.0
def add(dur, fn): global t; scenes.append((t, dur, fn)); t += dur
def vo(key, at): sched.append({"file": f"{WORK}/{key}.wav", "start": at})

s0 = t; vo("a1", s0 + .8); vo("a2", s0 + .8 + D["a1"] + .15); add(.8 + D["a1"] + .15 + D["a2"] + .5, lambda ov, lt, dur, base: sc_power(ov, lt, dur))
s0 = t; vo("a3", s0 + .3); add(.3 + D["a3"] + .5, lambda ov, lt, dur, base: sc_depts(ov, lt, dur))
s0 = t; vo("a4", s0 + .2); vo("a5", s0 + .2 + D["a4"] + .5); add(.2 + D["a4"] + .5 + D["a5"] + .6, lambda ov, lt, dur, base: sc_how(ov, lt, dur))
CLIPAUDIO = []
for i in range(3):
    s0 = t; fn, dur, cs, cd = make_pillar(i); vo(f"p{i+1}", s0 + .15)
    CLIPAUDIO.append({"file": glob.glob(f"{UP}/{CLIPS[i]}*.mp4")[0], "start": s0 + cs, "clip": True})
    add(dur, fn)
s0 = t; vo("b1", s0 + .3); add(.3 + D["b1"] + 1.3, lambda ov, lt, dur, base: sc_logo(ov, lt, dur))
s0 = t; vo("b2", s0 + .3); add(.3 + D["b2"] + .5, lambda ov, lt, dur, base: sc_faculty(ov, lt, dur))
s0 = t; vo("b3", s0 + .3); add(.3 + D["b3"] + .5, lambda ov, lt, dur, base: sc_class(ov, lt, dur))
s0 = t; vo("c1", s0 + .3); add(.3 + D["c1"] + .5, lambda ov, lt, dur, base: sc_goals(ov, lt, dur))
s0 = t; vo("c2", s0 + .3); vo("c3", s0 + .3 + D["c2"] + .3); vo("c4", s0 + .3 + D["c2"] + .3 + D["c3"] + .15)
tc3 = .3 + D["c2"] + .3; tc4 = tc3 + D["c3"] + .15
add(tc4 + D["c4"] + 2.4, lambda ov, lt, dur, base: sc_final(ov, lt, dur, tc3, tc4))
TOTAL = t
json.dump({"total": TOTAL, "vo": sched, "clips": CLIPAUDIO, "scenes": [(round(a, 2), round(b, 2)) for a, b, _ in scenes]}, open(f"{OUT}/audio_schedule.json", "w"), indent=1)
print("total", TOTAL, flush=True)

import os
STILLS = [float(x) for x in os.environ.get("STILLS", "").split(",") if x]
enc = None if STILLS else subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", f"{OUT}/video_only.mp4"], stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for fi in (range(n) if not STILLS else [int(x * FPS) for x in STILLS]):
    gt = fi / FPS
    si = max(i for i, (s, d, f) in enumerate(scenes) if s <= gt)
    s, d, fn = scenes[si]; lt = gt - s
    base = background(gt, 0)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ov, lt, d, base)
    if 3 <= si <= 5: corner_logo(ov, eo(p(lt, 0, .8)))
    fade = min(1, lt / .35 if si > 0 else 1) * min(1, (d - lt) / .35 if si < len(scenes) - 1 else 1)
    fade = max(fade, 0)
    if gt > TOTAL - 1.2: fade = min(fade, (TOTAL - gt) / 1.2)
    # crossfade through the background (dip) between scenes
    frame = base.convert("RGBA"); frame.alpha_composite(ov)
    if fade < 1: frame = Image.blend(background(gt, 0).convert("RGBA"), frame, fade)
    if STILLS: frame.convert("RGB").resize((960, 540)).save(f"{OUT}/still_{gt:06.2f}.png"); continue
    enc.stdin.write(frame.convert("RGB").tobytes())
    if fi % 100 == 0: print(fi, "/", n, flush=True)
if enc: enc.stdin.close(); enc.wait()
print("done")
