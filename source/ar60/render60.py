# Solix Application Retirement, 60-second overview (new script).
# Dark Solix-blue field with a low-opacity AI network, crisp After Effects-style vector motion graphics,
# realistic product screens in perspective, kinetic type and captions.
# Usage: python3 render60.py [preview t1 t2 ...]   (no args = full render to video60.mp4)
import json, os, sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import zoom
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(B, "..", "ar"))
import render_ar as RA          # typography + logo helpers
import docs_ar as DOC           # perspective screen placement
import screens_ar as SCR        # legacy application windows
import mg_ar as MG              # crisp vector drawing + icons
import screens60 as S6

W, H, FPS = 1920, 1080, 30
TL = json.load(open(f"{B}/timeline.json")); T = TL["total"]
LN = {l["id"]: l for l in TL["lines"]}
put, kinetic, fade_text, measure = RA.put, RA.kinetic, RA.fade_text, RA.measure
BLUE, RED = RA.BLUE, RA.RED
BL = (90, 190, 245); NAVY = (14, 34, 82); WH = (255, 255, 255)
LX = 150

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x*x*(3 - 2*x)
def eout(x): x = clamp(x); return 1 - (1 - x)**3
def lerp(a, b, u): return a + (b - a)*u
def wt(lid, frag):
    L = LN[lid]; i = L["caption"].find(frag)
    return L["start"] + (L["end"] - L["start"])*max(0, i)/max(1, len(L["caption"]))

ORDER = ["problem", "cost", "retire", "comply", "ai", "end"]
FIRST = dict(problem="p1", cost="c1", retire="r1", comply="m1", ai="a1", end="e1")
SC = {s: (0.0 if s == "problem" else LN[FIRST[s]]["start"] - .35) for s in ORDER}
SC_END = {s: (SC[ORDER[i+1]] if i + 1 < len(ORDER) else T) for i, s in enumerate(ORDER)}
def E(s): return SC_END[s] - .4
def out(s, t): return ease((t - E(s))/.4)

# ---------------------------------------------------------------- background: dark Solix blue + low-opacity AI network
YY, XX = np.mgrid[0:H//4, 0:W//4].astype(np.float32)*4
NAVY_DK = np.array([3, 9, 28], np.float32)/255; NAVY_F = np.array([10, 30, 74], np.float32)/255
GLOW_C = np.array([18, 80, 160], np.float32)/255; NET_C = np.array([140, 200, 255], np.float32)/255
_nr = np.random.default_rng(23); NET = _nr.random((110, 5))
def network(t):
    hw, hh = W//2, H//2
    im = Image.new("L", (hw, hh), 0); d = ImageDraw.Draw(im); pts = []
    for x, y, lay, ph, sp in NET:
        L = int(lay*3); v = (.6 + .8*sp)*(1 + L*.6)
        px = ((x*1.2 - .1 + t*.004*v + .03*math.sin(t*.11 + ph*6)) % 1.2 - .1)*hw
        py = ((y*1.2 - .1 + .02*math.sin(t*.09 + ph*9) + t*.0015*v) % 1.2 - .1)*hh
        pts.append((px, py, L))
    lim = (90, 115, 145)
    for a in range(len(pts)):
        xa, ya, La = pts[a]
        for b in range(a + 1, len(pts)):
            xb, yb, Lb = pts[b]
            if La != Lb: continue
            dd = math.hypot(xa - xb, ya - yb)
            if dd < lim[La]: d.line((xa, ya, xb, yb), fill=int((1 - dd/lim[La])*(70 + 45*La)), width=1)
    for px, py, L in pts:
        r = .8 + .7*L; d.ellipse((px - r, py - r, px + r, py + r), fill=120 + 60*L)
    return zoom(np.asarray(im, np.float32)/255, 2, order=1)[:H, :W, None]
def background(t):
    gx, gy = 1250 + 120*math.sin(t*.13), 520 + 60*math.sin(t*.1)
    base = NAVY_DK + (NAVY_F - NAVY_DK)*np.clip(1 - np.sqrt(((XX - 980)/1500)**2 + ((YY - 540)/950)**2), 0, 1)[..., None]
    a = np.clip(1 - np.sqrt(((XX - gx)/900)**2 + ((YY - gy)/700)**2), 0, 1)**1.6
    img = base + (GLOW_C - base)*(a*.45)[..., None]
    b = np.exp(-(((XX - 200)/650)**2 + ((YY - 1040)/380)**2))
    img = img + (np.array([0, .53, .81], np.float32) - img)*(.12*b)[..., None]
    img = zoom(img, (4, 4, 1), order=1)
    return img + (NET_C - img)*network(t)*.30
VIG = None
def vignette():
    global VIG
    if VIG is None:
        vy, vx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((vx - W/2)/(W*.62))**2 + ((vy - H/2)/(H*.62))**2)
        VIG = (1 - .45*np.clip(d - .5, 0, 1)**1.5)[..., None]
    return VIG

# ---------------------------------------------------------------- helpers
CAM = None
def place(fr, tex, X, Y, wpx, t, a_in, a_out=0.0, alpha=1.0, sheen_t=None, from_side=1):
    """Put a texture on screen at (X, Y) with width wpx, flying in with perspective."""
    if a_in <= 0 or a_out >= 1: return None
    s = 1050/5.6
    cam = DOC.Cam(960, 540, 1050, 5.6, yaw=.03*math.sin(t*.4), pitch=.03)
    k = eout(a_in); o = ease(a_out)
    c = np.array([(X - 960)/s + from_side*2.4*(1 - k) - 1.2*o, (540 - Y)/s - .5*(1 - k) + .4*o, 2.2*(1 - k) + 2.4*o])
    w = wpx/s; h = w*tex.height/tex.width
    q, n, _ = DOC.quad(cam, c, w, h, yaw=from_side*(-1.0)*(1 - k) - .14*from_side + .6*o, roll=.12*(1 - k))
    sh = None if sheen_t is None else lerp(-.2, 1.3, clamp(sheen_t))
    DOC.draw(fr, tex, q, n, alpha=alpha*k*(1 - o), sheen=sh, shadow=.5)
    return q

def kicker(fr, t, text, y, t0, t1):
    fade_text(fr, t, text, LX + 2, y, 26, t0, t1, fname="Inter-SemiBold.otf", track=7, rgb=BLUE*1.25)

ICON_LOGO = RA.logo_scaled(50); LOGO_END = RA.logo_scaled(170)

# ---------------------------------------------------------------- 1. The problem: a cluttered data center, legacy apps stacking up
APPS = [("ERP", "app"), ("CRM", "app"), ("HR", "file"), ("Mainframe", "mainframe"), ("Billing", "cost"),
        ("Custom app", "app"), ("Payroll", "cost"), ("Legacy DB", "db"), ("Reporting", "file"), ("Inventory", "archive"), ("Portal", "cloud")]
RACK_X = [900 + i*186 for i in range(5)]
SLOTS = [(RACK_X[i] + 80, 512) for i in range(5)] + [(RACK_X[i] + 173, 452) for i in range(4)] + [(1180, 392), (1546, 392)]
def scene_problem(fr, t):
    s = "problem"
    if t > SC_END[s] + .1: return
    o = out(s, t); a = 1 - o
    kicker(fr, t, "THE PROBLEM", 236, .3, E(s))
    kinetic(fr, t, "Legacy apps you can't turn off.", LX, 330, 78, .45, E(s), maxw=700)
    fade_text(fr, t, "The data inside still matters.", LX, 560, 36, wt("p1", "because"), E(s), fname="InterDisplay-Medium.otf", rgb=np.array([.6, .8, 1.0]))
    cv = MG.Cv(860, 300, 1020, 660)
    for i, x in enumerate(RACK_X):
        p = MG.back((t - .15 - i*.09)/.6)
        if p <= 0: continue
        y0 = 545 + (1 - p)*360
        cv.rrect(x, y0, 160, 380, 10, fill=MG.rgba((12, 30, 72), .96*a), outline=MG.rgba((40, 110, 190), a), width=2)
        for u in range(9):
            yy = y0 + 22 + u*39
            cv.rrect(x + 14, yy, 132, 28, 4, fill=MG.rgba((20, 48, 104), a))
            for j in range(3):
                ph = math.sin(t*(3 + j + u*.7) + i*1.3 + u)
                col = (255, 80, 80) if (u + i) % 7 == 3 else ((80, 220, 140) if j == 0 else BL)
                cv.circle(x + 118 + j*0 - j*12, yy + 14, 3.2, fill=MG.rgba(col, a*(.35 + .65*(ph > -.2))))
            cv.line([(x + 24, yy + 14), (x + 70, yy + 14)], MG.rgba((60, 100, 160), a), 2)
    for i, ((lab, kind), (sx, sy)) in enumerate(zip(APPS, SLOTS)):
        ti = 1.0 + i*.42
        p = MG.back((t - ti)/.55, 1.3)
        if p <= 0: continue
        y = -80 + (sy - (-80))*p
        x = sx + 6*math.sin(i*2.3)
        cv.rrect(x - 78, y - 26, 156, 52, 10, fill=MG.rgba((24, 56, 120), a), outline=MG.rgba(BL, a), width=2)
        MG.icon(cv, kind, x - 52, y, 30, MG.WHITE, a)
        cv.text(x - 30, y, lab, 20, MG.rgba(WH, a), "InterDisplay-SemiBold.otf", anchor="lm")
        if i in (1, 4, 7) and t > ti + 1.2:
            pz = .55 + .45*math.sin(t*6 + i)
            cv.circle(x + 70, y - 24, 12, fill=MG.rgba((238, 36, 36), a*pz))
            cv.text(x + 70, y - 24, "!", 16, MG.rgba(WH, a), "InterDisplay-Bold.otf")
    cv.blit(fr, glow=.35)

# ---------------------------------------------------------------- 2. The cost: rising cost and risk, data locked in silos
def scene_cost(fr, t):
    s = "cost"
    if not (SC[s] - .1 <= t <= SC_END[s] + .1): return
    o = out(s, t); a = 1 - o; s0 = SC[s]
    kicker(fr, t, "THE COST", 236, s0 + .2, E(s))
    kinetic(fr, t, "Rising cost. Growing risk.", LX, 330, 78, s0 + .3, E(s), maxw=720, hl=("Growing", "risk"), hlc=RED*.35 + .65*np.array([1, .6, .6]))
    t1 = wt("c1", "drains budget"); t2 = wt("c1", "security risk"); t3 = wt("c1", "silos")
    rows = [("Licenses", "cost", .72, "$1.2M / yr", t1, BL), ("Infrastructure", "db", .58, "$860K / yr", t1 + .45, BL),
            ("Security exposure", "risk", .88, "High", t2, (238, 70, 70))]
    cv = MG.Cv(920, 230, 900, 700)
    for i, (lab, kind, f, val, ti, col) in enumerate(rows):
        p = MG.back((t - ti)/.5)
        if p <= 0: continue
        y = 300 + i*120
        cv.circle(990, y, 38*p, fill=MG.rgba(NAVY, .95*a), outline=MG.rgba(col, a), width=3)
        MG.icon(cv, kind, 990, y, 44*p, MG.WHITE, a)
        cv.text(1050, y - 22, lab, 28, MG.rgba(WH, a), "InterDisplay-SemiBold.otf", anchor="lm")
        cv.rrect(1050, y + 6, 600, 18, 9, fill=MG.rgba((30, 60, 110), a))
        g = eout((t - ti - .1)/1.0)*f
        cv.rrect(1050, y + 6, max(18, 600*g), 18, 9, fill=MG.rgba(col, a))
        cv.text(1700, y - 22, val, 28, MG.rgba(col, a*clamp((t - ti - .5)/.4)), "InterDisplay-Bold.otf", anchor="rm")
    # rising total-cost line
    pc = eout((t - s0 - .6)/3.2)
    if pc > 0:
        pts = [(990 + k*95, 860 - 18*k - 6*k*k*.9) for k in range(8)]
        n = 1 + int(pc*(len(pts) - 1)); fr_ = pc*(len(pts) - 1) - (n - 1)
        seg = pts[:n] + ([(pts[n-1][0] + (pts[n][0] - pts[n-1][0])*fr_, pts[n-1][1] + (pts[n][1] - pts[n-1][1])*fr_)] if n < len(pts) else [])
        cv.line(seg, MG.rgba((238, 70, 70), a), 4)
        for px, py in seg[:-1]: cv.circle(px, py, 5, fill=MG.rgba(WH, a))
        hx, hy = seg[-1]; cv.poly([(hx + 14, hy - 4), (hx - 4, hy - 14), (hx - 2, hy + 6)], fill=MG.rgba((238, 70, 70), a))
        cv.text(990, 900, "TOTAL COST OF KEEPING LEGACY APPS", 17, MG.rgba(BL, a), "Inter-SemiBold.otf", anchor="lm")
    cv.blit(fr, glow=.4)
    # silos: data locked away
    cv2 = MG.Cv(120, 560, 760, 380)
    for i in range(3):
        p = MG.back((t - t3 - i*.15)/.5)
        if p <= 0: continue
        x = 230 + i*200; yb = 860; hgt = 190*p
        cv2.rrect(x - 60, yb - hgt, 120, hgt, 14, fill=MG.rgba((20, 50, 105), a), outline=MG.rgba(BL, a), width=2)
        for k in range(3): cv2.d.ellipse((*cv2.p(x - 60, yb - hgt + k*hgt/3 - 10), *cv2.p(x + 60, yb - hgt + k*hgt/3 + 10)), outline=MG.rgba(BL, a), width=4)
        MG.icon(cv2, "lock", x, yb - hgt - 46, 56*p, (255, 120, 120), a)
    if t > t3: cv2.text(150, 900, "Valuable data locked in silos", 26, MG.rgba(WH, a*clamp((t - t3 - .3)/.4)), "InterDisplay-SemiBold.otf", anchor="lm")
    cv2.blit(fr, glow=.35)

# ---------------------------------------------------------------- 3. Retire: data flows into the Solix Common Data Platform, apps shut down
LEG = [("erp", 360, 470), ("mf", 440, 615), ("form", 520, 760)]
def scene_retire(fr, t):
    s = "retire"
    if not (SC[s] - .1 <= t <= SC_END[s] + .1): return
    o = out(s, t); a = 1 - o; s0 = SC[s]; tr2 = LN["r2"]["start"]
    kicker(fr, t, "RETIRE", 176, s0 + .2, E(s))
    kinetic(fr, t, "Move the data. Retire the app.", LX, 250, 64, s0 + .3, E(s), maxw=1500, hl=("Retire",))
    # legacy application windows (left), dim and stamped Retired at "shut ... down"
    offs = []
    for i, (kind, X, Y) in enumerate(LEG):
        ti = s0 + .3 + i*.2
        dark = ease((t - tr2 - .6 - i*.35)/.5)
        q = place(fr, SCR.legacy(kind), X, Y, 420, t, (t - ti)/.7, o, alpha=1 - .55*dark, sheen_t=(t - ti - .2)/.6, from_side=-1)
        offs.append((q, dark))
    cv = MG.Cv(140, 330, 1000, 640)
    for i, (q, dark) in enumerate(offs):
        if q is None or dark <= 0: continue
        cx, cy = q[:, 0].mean(), q[:, 1].mean()
        p = MG.back(dark/.6, 2.0)
        cv.rrect(cx - 105*p, cy - 30*p, 210*p, 60*p, 10, outline=MG.rgba((238, 50, 50), a), width=4, fill=MG.rgba((40, 10, 20), .55*a))
        cv.text(cx, cy, "RETIRED", int(30*p) if p > .05 else 1, MG.rgba((255, 90, 90), a), "InterDisplay-Bold.otf")
    cv.blit(fr, glow=.4, gcol=(1, .3, .3))
    # Solix Common Data Platform console (right)
    tc = s0 + .6
    place(fr, S6.cdp(int(clamp((t - tc - .8)/7.5)*30)), 1440, 590, 700, t, (t - tc)/.7, o, sheen_t=(t - tc - .2)/.6)
    # data flowing: structured and unstructured
    cv = MG.Cv(640, 330, 520, 560)
    flow = clamp((t - s0 - 1.0)/.5)*(1 - ease((t - tr2 - .2)/.6))*a
    if flow > 0:
        kinds = ["db", "file", "mail", "app", "file", "db"]
        for j in range(9):
            ph = (t*.55 + j/9) % 1.0
            lane = j % 3
            y0 = (470, 615, 760)[lane]; y1 = 520 + lane*80
            x = 700 + 400*ph; y = y0 + (y1 - y0)*ease(ph) - math.sin(ph*math.pi)*30
            al = flow*math.sin(ph*math.pi)
            cv.circle(x, y, 20, fill=MG.rgba((20, 60, 130), al), outline=MG.rgba(BL, al), width=2)
            MG.icon(cv, kinds[j % 6], x, y, 24, MG.WHITE, al)
        cv.text(900, 400, "STRUCTURED", 17, MG.rgba(BL, flow), "Inter-SemiBold.otf")
        cv.text(900, 860, "UNSTRUCTURED", 17, MG.rgba(BL, flow), "Inter-SemiBold.otf")
    cv.blit(fr, glow=.5)
    fade_text(fr, t, "Shut them down. For good.", LX, 320, 40, tr2 + .2, E(s), fname="InterDisplay-SemiBold.otf", rgb=np.array([1, .6, .6]))

# ---------------------------------------------------------------- 4. Comply: built-in compliance
CAPS = [("Retention", "archive", ("m2", "retention")), ("Legal hold", "lock", ("m2", "legal holds")), ("eDiscovery", "file", ("m2", "eDiscovery")),
        ("Masking", "risk", ("m3", "protected")), ("Audit trail", "app", ("m2", "audit-ready"))]
def scene_comply(fr, t):
    s = "comply"
    if not (SC[s] - .1 <= t <= SC_END[s] + .1): return
    o = out(s, t); a = 1 - o; s0 = SC[s]
    kicker(fr, t, "COMPLY", 176, s0 + .2, E(s))
    kinetic(fr, t, "Compliance, built in.", LX, 262, 76, s0 + .3, E(s), maxw=800, hl=("built", "in"))
    cv = MG.Cv(120, 300, 760, 640)
    for i, (lab, kind, (lid, frag)) in enumerate(CAPS):
        ti = wt(lid, frag) - .15
        p = MG.back((t - ti)/.45)
        y = 370 + i*84
        if p <= 0:
            cv.circle(190, y, 30, outline=MG.rgba((60, 100, 160), .5*a), width=2); continue
        cv.circle(190, y, 32*p, fill=MG.rgba((0, 136, 207), a), outline=MG.rgba(WH, .9*a*clamp(1 - (t - ti - .4)/.5)), width=2)
        MG.icon(cv, kind, 190, y, 38*p, MG.WHITE, a)
        cv.text(242, y, lab, 32, MG.rgba(WH, a*clamp((t - ti)/.3)), "InterDisplay-SemiBold.otf", anchor="lm")
        cv.text(560, y, "✓", 30, MG.rgba(BL, a*clamp((t - ti - .3)/.3)), "InterDisplay-Bold.otf")
    # regulation badges
    tb = s0 + .7
    for i, lab in enumerate(("GDPR", "HIPAA", "SOX")):
        p = MG.back((t - tb - i*.15)/.45)
        if p <= 0: continue
        x = 200 + i*150; y = 830
        pts = [(x, y - 52*p), (x + 46*p, y - 36*p), (x + 42*p, y + 14*p), (x, y + 50*p), (x - 42*p, y + 14*p), (x - 46*p, y - 36*p)]
        cv.poly(pts, fill=MG.rgba((14, 40, 95), a), outline=MG.rgba(BL, a), width=3)
        cv.text(x, y - 2, lab, int(20*p) if p > .05 else 1, MG.rgba(WH, a), "InterDisplay-Bold.otf")
    cv.blit(fr, glow=.45)
    # policy screen (right)
    tp = s0 + .5
    place(fr, S6.policy(int(clamp((t - LN["m2"]["start"] + .3)/(LN["m3"]["end"] - LN["m2"]["start"] + .2))*30)), 1390, 575, 780, t,
          (t - tp)/.7, o, sheen_t=(t - tp - .2)/.6)

# ---------------------------------------------------------------- 5. Activate with AI: Data Ask in CDP Navigator
def scene_ai(fr, t):
    s = "ai"
    if not (SC[s] - .1 <= t <= SC_END[s] + .1): return
    o = out(s, t); a = 1 - o; s0 = SC[s]
    kicker(fr, t, "ACTIVATE WITH AI", 176, s0 + .2, E(s))
    kinetic(fr, t, "Talk to your archived data.", LX, 262, 72, wt("a2", "simply talk") - .6, E(s), maxw=560, hl=("Talk",))
    fade_text(fr, t, "Retired data doesn't sit idle.", LX, 262, 44, s0 + .3, wt("a2", "simply talk") - .8, fname="InterDisplay-SemiBold.otf")
    tq = wt("a2", "simply talk") - .2; nq = int(clamp((t - tq)/2.0)*len(S6.Q))
    tth = tq + 2.1; tans = wt("a3", "get answers") - .2
    think = clamp((t - tth)/1.0) if t >= tth else 0.0
    ans = clamp((t - tans)/1.6) if t >= tans else 0.0
    ts = s0 + .4
    place(fr, S6.data_ask(nq, round(think*12)/12 if ans <= 0 else 0, round(ans*24)/24), 1270, 590, 960, t, (t - ts)/.7, o, sheen_t=(t - ts - .2)/.6)
    cv = MG.Cv(120, 440, 560, 420)
    chips = [("Plain-language questions", wt("a3", "Ask questions")), ("Answers in seconds", wt("a3", "seconds")),
             ("No reports to build", wt("a3", "no reports")), ("No legacy app to log into", wt("a3", "no legacy"))]
    for i, (lab, ti) in enumerate(chips):
        p = MG.back((t - ti + .1)/.4)
        if p <= 0: continue
        y = 500 + i*82
        cv.rrect(150, y - 30, 480*p, 60, 30, fill=MG.rgba((14, 44, 100), .95*a), outline=MG.rgba(BL, a), width=2)
        cv.circle(182, y, 15*p, fill=MG.rgba((0, 136, 207), a))
        cv.text(182, y, "✓", 18, MG.rgba(WH, a), "InterDisplay-Bold.otf")
        cv.text(212, y, lab, 26, MG.rgba(WH, a*clamp((t - ti)/.3)), "InterDisplay-SemiBold.otf", anchor="lm")
    cv.blit(fr, glow=.4)

# ---------------------------------------------------------------- 6. Payoff and CTA
PILLARS = [("Lower costs", "cost", "Lower costs"), ("Less risk", "risk", "less risk"), ("New value from old data", "ai", "new value")]
def scene_end(fr, t):
    s = "end"
    if t < SC[s] - .1: return
    s0 = SC[s]; t2 = LN["e2"]["start"] - .2
    po = ease((t - t2)/.45)
    if po < 1:
        cv = MG.Cv(240, 300, 1440, 500)
        for i, (lab, kind, frag) in enumerate(PILLARS):
            ti = wt("e1", frag) - .1
            p = MG.back((t - ti)/.45)
            if p <= 0: continue
            x = 480 + i*480; a = 1 - po
            cv.circle(x, 470, 92*p, fill=MG.rgba(NAVY, .95*a), outline=MG.rgba((0, 136, 207), a), width=4)
            MG.dashed_ring(cv, x, 470, 118*p, (t*30) % 360, MG.rgba(BL, .5*a), n=40, width=2)
            MG.icon(cv, kind, x, 470, 110*p, MG.WHITE, a)
            cv.text(x, 640, lab, 34, MG.rgba(WH, a*clamp((t - ti)/.3)), "InterDisplay-SemiBold.otf")
        cv.blit(fr, glow=.55)
    if t >= t2:
        p = eout((t - t2)/.9)
        RA.put_rgba(fr, LOGO_END, W/2 - LOGO_END.shape[1]/2 + 10, 250 + (1 - p)*30, p)
        cv = MG.Cv(360, 140, 1200, 560)
        for k, (rx, ry, sp, n, duty, w_, al) in enumerate(((520, 150, 10, 64, .55, 2, .55), (560, 176, -6, 32, .3, 3, .4))):
            step = 360/n
            for i in range(int(n*p)):
                a0 = math.radians(t*sp + i*step); a1 = math.radians(t*sp + i*step + step*duty)
                pts = [(960 + rx*math.cos(a0 + (a1 - a0)*j/4), 335 + ry*math.sin(a0 + (a1 - a0)*j/4)) for j in range(5)]
                cv.line(pts, MG.rgba(BL if k == 0 else (0, 136, 207), al), w_)
        cv.blit(fr, glow=.5)
        words = [("Retire.", t2 + .5), ("Comply.", wt("e2", "comply") - .05), ("Activate.", wt("e2", "activate") - .05)]
        tw = sum(measure(w, "InterDisplay-Bold.otf", 84) for w, _ in words) + 2*34
        x = W/2 - tw/2
        for i, (wd, ti) in enumerate(words):
            q = eout((t - ti)/.5)
            if q > 0: put(fr, wd, "InterDisplay-Bold.otf", 84, x, 640 + (1 - q)*26, q, blur=(1 - q)*8, rgb=(BLUE*1.2) if i == 2 else (1, 1, 1))
            x += measure(wd, "InterDisplay-Bold.otf", 84) + 34
        fade_text(fr, t, "www.solix.com", W/2, 730, 36, wt("e2", "with Solix"), T + 5, fname="Inter-SemiBold.otf", anchor="ms", rgb=np.array([.6, .82, 1.0]), track=2)
        fade_text(fr, t, "Solix Application Retirement", W/2, 790, 26, wt("e2", "with Solix") + .3, T + 5, fname="Inter-Medium.otf", anchor="ms", alpha=.8)

# ---------------------------------------------------------------- overlays
def tracker(fr, t):
    t_on = SC["retire"] + .1; t_off = LN["e2"]["start"] - .3
    if not (t_on - .1 < t <= t_off + .5): return
    ga = ease((t - t_on)/.5)*(1 - ease((t - t_off)/.4))
    cur = {"retire": 0, "comply": 1, "ai": 2}.get(next((s for s in reversed(ORDER) if t >= SC[s]), "problem"), 3)
    x = LX
    for i, lab in enumerate(("RETIRE", "COMPLY", "ACTIVATE")):
        act = (i == cur) or cur == 3
        if act and cur != 3: put(fr, "●", "Inter-SemiBold.otf", 18, x, 98, ga, rgb=BLUE*1.2); x += 26
        put(fr, lab, "Inter-SemiBold.otf", 24, x, 100, ga*(1.0 if act else (.6 if i < cur else .32)), track=4)
        x += measure(lab, "Inter-SemiBold.otf", 24, 4) + 22
        if i < 2: put(fr, "›", "Inter-SemiBold.otf", 24, x, 100, ga*.4); x += 34

def captions(fr, t):
    LS = TL["lines"]
    for i, L in enumerate(LS):
        if L["id"] == "e2": continue
        t0, t1 = L["start"] - .1, L["end"] + .3
        if i + 1 < len(LS): t1 = min(t1, LS[i+1]["start"] - .45)
        if not (t0 - .1 <= t <= t1 + .3): continue
        a = ease((t - t0)/.2)*(1 - ease((t - t1)/.25))*.92
        if a <= .003: continue
        lines = RA.wrap(L["caption"], "Inter-Medium.otf", 32, 1400)
        y = 1008 - (len(lines) - 1)*42
        for k, ln in enumerate(lines): put(fr, " ".join(ln), "Inter-Medium.otf", 32, W/2, y + k*42, a, anchor="ms")

def frame(t):
    fr = background(t).astype(np.float32)*vignette()
    for fn in (scene_problem, scene_cost, scene_retire, scene_comply, scene_ai, scene_end):
        try: fn(fr, t)
        except Exception as e: print("skip", fn.__name__, round(t, 3), e, flush=True)
    tracker(fr, t)
    RA.put_rgba(fr, ICON_LOGO, W - 90 - ICON_LOGO.shape[1], 56, ease((t - .2)/.5)*(1 - ease((t - LN["e2"]["start"] + .4)/.4)))
    captions(fr, t)
    fi = ease(t/.3); fo = 1 - ease((t - (T - .8))/.8)
    return (np.clip(fr*fi*fo, 0, 1)*255 + .5).astype(np.uint8)

def render_range(i0, i1, out_):
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", out_], stdin=subprocess.PIPE)
    for i in range(i0, i1): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    if sys.argv[1:2] == ["preview"]:
        os.makedirs(f"{B}/preview", exist_ok=True)
        for ts in sys.argv[2:]: Image.fromarray(frame(float(ts))).save(f"{B}/preview/f_{float(ts):05.1f}.jpg", quality=88)
        sys.exit()
    if sys.argv[1:2] == ["seg"]:
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]); sys.exit()
    NF = int(T*FPS); K = int(os.environ.get("JOBS", "4")); os.makedirs(f"{B}/seg", exist_ok=True)
    cuts = [NF*k//K for k in range(K + 1)]
    ps = [subprocess.Popen([sys.executable, __file__, "seg", str(cuts[k]), str(cuts[k+1]), f"{B}/seg/s{k}.mp4"]) for k in range(K)]
    for p in ps: p.wait()
    with open(f"{B}/seg/list.txt", "w") as f:
        for k in range(K): f.write(f"file 's{k}.mp4'\n")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{B}/seg/list.txt", "-c", "copy", f"{B}/video60.mp4"], check=True)
    print("done")
