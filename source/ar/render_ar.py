# Solix Application Retirement, 60-70 s big-screen film (v2).
# Procedural, lit 3D particle motion graphics on a Solix red / indigo field with blue highlights,
# kinetic text-only typography and extruded 3D headline words.
# Usage: python3 render_ar.py [preview t1 t2 ...]   (no args = full render to ar_video.mp4)
import json, os, sys, subprocess, math, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, zoom
import docs_ar as DOC

B = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B, "..", "assets")
W, H, FPS = 1920, 1080, 30
TL = json.load(open(f"{B}/timeline.json")); T = TL["total"]
LN = {l["id"]: l for l in TL["lines"]}
FD = "/usr/share/fonts/opentype/inter/"
N = 5000
rng = np.random.default_rng(11)

def hexc(h): return np.array([int(h[i:i+2], 16) for i in (1, 3, 5)], np.float32)/255
RED, BLUE, INDIGO = hexc("#ee2424"), hexc("#0088cf"), hexc("#30267b")
WH = np.array([1.0, .95, .94], np.float32)                 # particle white
BLG = np.array([.10, .62, 1.0], np.float32)                # #0088cf as emitted light
RDG = np.array([1.0, .22, .22], np.float32)                # #ee2424 as emitted light
LAV = np.array([.62, .58, 1.0], np.float32)                # far-depth haze (indigo family)

def clamp(x, a=0.0, b=1.0): return np.minimum(b, np.maximum(a, x))
def ease(x): x = clamp(x); return x*x*(3-2*x)
def eout(x): x = clamp(x); return 1-(1-x)**3
def einout(x): x = clamp(x); return np.where(x < .5, 4*x**3, 1-(-2*x+2)**3/2)
def fl(x): return float(x)

def word_time(lid, frag):
    """Approximate when a fragment is spoken within a line (character-proportional)."""
    L = LN[lid]; txt = L["caption"]; i = txt.find(frag)
    return L["start"] + (L["end"]-L["start"]) * max(0, i) / max(1, len(txt))

# ---------------------------------------------------------------- scenes
ORDER = ["hook", "t1", "t2", "t3", "t4", "t5", "one", "connect", "migrate", "dark", "access", "ask", "ai", "sign"]
SC = {}
for k, sid in enumerate(ORDER):
    SC[sid] = 0.0 if k == 0 else LN[sid]["start"] - (0.15 if sid.startswith("t") else 0.45)
SC_END = {sid: (SC[ORDER[k+1]] if k+1 < len(ORDER) else T) for k, sid in enumerate(ORDER)}
def scene_at(t):
    cur = ORDER[0]
    for sid in ORDER:
        if t >= SC[sid]: cur = sid
    return cur

# ---------------------------------------------------------------- particle shapes
# Each shape returns positions P (N,3), brightness Bv (N,), colour C (N,3).
U = rng.random((N, 6))
G = rng.standard_normal((N, 3))
def fib(n, r=1.0):
    i = np.arange(n) + .5; phi = np.arccos(1 - 2*i/n); th = np.pi*(1+5**.5)*i
    return np.stack([np.cos(th)*np.sin(phi), np.cos(phi), np.sin(th)*np.sin(phi)], 1)*r
SPH = fib(N)
SPH_P = SPH[rng.permutation(N)]
DUST = (np.random.default_rng(100).random((N, 3)) - .5)*np.array([9.0, 5.0, 6.0])
def cfill(c): return np.tile(c, (N, 1))
def cmix(mask, a, b): return np.where(np.asarray(mask)[:, None], a, b)
def rot_y(P, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([P[:, 0]*c + P[:, 2]*s, P[:, 1], -P[:, 0]*s + P[:, 2]*c], 1)
def rot_x(P, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([P[:, 0], P[:, 1]*c - P[:, 2]*s, P[:, 1]*s + P[:, 2]*c], 1)

# Hook: legacy application screens as 3D dot-matrix panels with thickness, title bar and content rows
PANELS = [(-2.6, .9, -.4, .5), (-1.0, 1.25, 1.2, -.3), (.9, .75, -1.2, .35), (2.6, 1.05, .5, -.55),
          (-2.0, -.8, .8, .4), (.0, -.55, .3, -.15), (1.9, -.95, -.6, -.4), (-.4, .35, -2.4, .2),
          (3.4, -.2, -1.8, -.7), (-3.4, .1, -1.6, .7), (.6, 2.0, -.2, .1), (-1.1, -1.9, -.9, -.2)]
GW, GH = 18, 11
def _panel_template():
    gx, gy = np.meshgrid(np.linspace(-.5, .5, GW), np.linspace(-.3, .3, GH))
    gx, gy = gx.ravel(), gy.ravel()
    row = np.round((gy + .3)/.6*(GH-1)).astype(int)
    col = np.round((gx + .5)*(GW-1)).astype(int)
    title = row == GH-1
    content = (row < GH-2) & (row % 2 == 1) & (col > 1) & (col < 2 + ((row*7) % 13) + 3)
    face = np.stack([gx, gy, np.zeros_like(gx)], 1)
    edge = (np.abs(gx) > .49) | (np.abs(gy) > .29)
    back = face[edge] + np.array([0, 0, .09])
    P = np.concatenate([face, back]); n = len(P)
    kind = np.concatenate([np.where(title, 2, np.where(content, 1, 0)), np.full(len(back), 3)])
    return P, kind
PT, PKIND = _panel_template()
NP = len(PT)
def sh_hook(t, lt):
    P = DUST.copy(); Bv = np.full(N, .16); C = cfill(LAV)
    k = 0
    for c, (cx, cy, cz, yaw) in enumerate(PANELS):
        if k + NP > N: break
        q = rot_y(PT, yaw + .08*math.sin(t*.3 + c)) + np.array([cx, cy + .06*math.sin(t*.4 + c*1.7), cz])
        P[k:k+NP] = q
        Bv[k:k+NP] = np.select([PKIND == 2, PKIND == 1, PKIND == 3], [.95, .7, .45], .32)
        C[k:k+NP] = np.where((PKIND == 2)[:, None], BLG, WH)
        Bv[k] = 2.2 + 1.6*math.sin(t*3.2 + c*1.3); C[k] = RDG   # running light
        k += NP
    return P, Bv, C

def sh_cost(t, lt):
    """A coin: thick ring with an inner disc, turning."""
    a = U[:, 0]*2*np.pi; m = U[:, 1]
    r = np.where(m < .6, 1.0 + .1*np.cos(U[:, 2]*2*np.pi), .84*np.sqrt(U[:, 3]))
    z = np.where(m < .6, .14*np.sin(U[:, 2]*2*np.pi), (U[:, 4]-.5)*.08)
    P = rot_y(np.stack([r*np.cos(a), r*np.sin(a), z], 1), t*1.2)
    return P, np.where(m < .6, 1.0, .5), cfill(WH)

def sh_risk(t, lt):
    """Unpatched system: a fractured sphere that glitches red."""
    seg = np.floor(U[:, 0]*14)
    hit = (np.sin(t*5.3 + seg) > .55)
    j = 1 + .25*np.sin(seg*3.1 + t*9)*hit + .05*G[:, 0]
    P = SPH_P*j[:, None]*.95
    P[:, 0] += .03*math.sin(t*40)*(math.sin(t*5) > .6)
    return P, .8 + .7*hit, cmix(hit, RDG, WH)

def sh_mna(t, lt):
    """Acquisition: a second system drawn in and absorbed."""
    half = np.arange(N) < N*.55
    k = fl(eout(lt/1.8))
    off = np.where(half, -.35 - .2*(1-k), 1.0 - .8*k)
    P = SPH*np.where(half, .85, .55)[:, None]; P[:, 0] += off
    return P, np.where(half, .8, 1.1), cmix(half, WH, BLG)

def sh_archive(t, lt):
    """Archive at its limit: a stack of layers, the top ones straining."""
    layer = np.floor(U[:, 0]*10); a = U[:, 1]*2*np.pi
    r = .9*np.sqrt(.25 + .75*U[:, 2])
    P = np.stack([r*np.cos(a), -1.0 + layer*.21 + .02*np.sin(t*2+layer), r*np.sin(a)], 1)
    top = layer >= 8
    return P, .55 + .9*top*(.6+.4*math.sin(t*7)), cmix(top, RDG, WH)

def cam_yaw(t):
    if t < SC["t1"]: return -.38 + .42*fl(einout(t/SC["t1"]))
    return .16*t + .3*math.sin(.13*t)

AI_WEDGE = (np.arctan2(SPH[:, 2], SPH[:, 0]) > -1.0) & (np.arctan2(SPH[:, 2], SPH[:, 0]) < 1.5) & (SPH[:, 1] > -.2)
AI_BAND = np.abs(np.sin(SPH[:, 1]*9)) > .8
def sh_ai_gap(t, lt):
    """AI program short on history: a neural sphere with a missing quadrant."""
    P = np.where(AI_WEDGE[:, None], SPH*3.2 + G*.5, SPH)
    Bv = np.where(AI_WEDGE, .08, .55 + .5*AI_BAND)
    return rot_y(P, .25 - cam_yaw(t) + .08*lt), Bv, cmix(AI_BAND, BLG, WH)

def sh_engine(t, lt):
    m = U[:, 0]
    core = fib(N, .42)
    a = U[:, 1]*2*np.pi + t*.5
    r1 = np.stack([np.cos(a)*1.0, .04*G[:, 1], np.sin(a)*1.0], 1)
    r2 = rot_x(np.stack([np.cos(-a*1.3)*1.4, .03*G[:, 2], np.sin(-a*1.3)*1.4], 1), .9)
    P = np.where((m < .45)[:, None], core, np.where((m < .72)[:, None], r1, r2))
    P = np.where((m > .93)[:, None], DUST*.6, P)
    Bv = np.where(m < .45, 1.0, np.where(m < .93, .9, .15))
    C = np.where((m < .45)[:, None], WH, np.where((m < .72)[:, None], BLG, np.where((m < .93)[:, None], WH, LAV)))
    return P, Bv, C

def sh_one(t, lt):
    """Many reasons converge to a point, then open into the Solix engine."""
    t_open = word_time("one", "One engine") - SC["one"]
    if lt < t_open:
        return G*.03, np.full(N, 1.3), cfill(WH)
    k = fl(eout((lt - t_open)/1.4))
    P, Bv, C = sh_engine(t, lt)
    return P*(.02 + .98*k), Bv*(1 + 1.5*(1-k)), C

SRC = ["ERP", "Mainframe", "Custom apps", "SaaS", "Files", "Email"]
SRC_W = ["ERP", "mainframe", "custom", "SaaS", "files", "email"]
SRC_A = np.array([[math.cos(k/6*2*np.pi+.3)*2.4, .95*math.sin(k*2.1), math.sin(k/6*2*np.pi+.3)*1.7] for k in range(6)])
def sh_connect(t, lt):
    """Sources stream into the engine."""
    m = U[:, 0]; s_id = (U[:, 1]*6).astype(int)
    P, Bv, C = sh_engine(t, lt); P = P*.75
    st = (m >= .35) & (m < .88)
    a = SRC_A[s_id]
    ph = (U[:, 2] + lt*.32) % 1.0
    ctrl = a*.5 + np.array([0, .9, 0])
    q = (1-ph)[:, None]**2*a + 2*((1-ph)*ph)[:, None]*ctrl + G*.03
    on = np.array([fl(ease((lt - (word_time("connect", w) - SC["connect"]))*2)) for w in SRC_W])
    P = np.where(st[:, None], q, P)
    Bv = np.where(st, (.25 + 1.0*np.sin(ph*np.pi))*on[s_id], Bv)
    C = np.where(st[:, None], BLG, C)
    an = (m >= .88) & (m < .97)
    P = np.where(an[:, None], a + SPH_P*.13, P)
    Bv = np.where(an, .5 + 1.0*on[s_id], Bv); C = np.where(an[:, None], WH, C)
    return P, Bv, C

CUBE_G = np.stack(np.meshgrid(*[np.linspace(-.7, .7, 13)]*3, indexing="ij"), -1).reshape(-1, 3)
NC = len(CUBE_G)
CUBE_EDGE = (np.abs(CUBE_G) > .69).sum(1) >= 2
def vault(fill):
    P = DUST.copy()*.9; Bv = np.full(N, .1); C = cfill(LAV)
    lvl = (CUBE_G[:, 1]+.7)/1.4
    inside = lvl <= fill
    P[:NC] = np.where(inside[:, None], CUBE_G, CUBE_G + np.array([0, 1.7, 0]) + G[:NC]*.3)
    Bv[:NC] = np.where(inside, .5, .1)
    Bv[:NC] = np.where(inside & CUBE_EDGE, 1.4, Bv[:NC])
    C[:NC] = np.where((inside & CUBE_EDGE)[:, None], BLG, WH)
    return P, Bv, C

def sh_migrate(t, lt):
    """Data lands in the governed Preservation Zone: a lattice vault filling bottom-up."""
    fill = fl(ease((lt - .6)/4.5))
    P, Bv, C = vault(fill)
    fs = slice(NC, NC+900)
    ph = (U[fs, 2] + lt*.6) % 1
    P[fs] = np.stack([G[fs, 0]*.28, 2.0 - ph*(2.0-(-.7+1.4*fill)), G[fs, 2]*.28], 1)
    Bv[fs] = .8*(fill < .99) + .1; C[fs] = BLG
    sweep = ((lt*.7) % 1.8) - .9
    Bv[:NC] += .9*np.exp(-((CUBE_G[:, 0]-sweep)/.12)**2)*(lt > 5)
    return P, Bv, C

SHELL = SPH_P*np.array([1.85, 1.2, 1.85])
def sh_dark(t, lt):
    """The source application powers down and falls away; the vault stays lit."""
    P, Bv, C = vault(1.0)
    rest = np.arange(N) >= NC
    td = word_time("dark", "go dark") - SC["dark"] + .3
    k = fl(ease((lt - td)/1.2))
    fall = max(0.0, lt - td - .6)
    S = rot_y(SHELL, t*.15)
    S[:, 1] -= (fall**2)*.35*(.4+U[:, 3])
    S[:, 0] += G[:, 0]*fall*.08; S[:, 2] += G[:, 2]*fall*.08
    P[rest] = S[rest]
    flick = (np.sin(t*30+U[:, 4]*50) > .7)*(lt > td-.2)*(k < .6)
    Bv[rest] = ((.75*(1-k) + .06)*(1 + .8*flick))[rest]
    C[rest] = np.where(((k > .15) | flick[rest].astype(bool))[:, None], RDG, WH)
    Bv[:NC] *= 1 + .25*k
    return P, Bv, C

DOCS = ["Invoice", "Purchase order", "Receipt", "Payment"]
DOC_A = np.array([[-1.3, .5, .1], [.95, 1.1, -.2], [1.3, -.45, .35], [-.3, -1.1, -.3]])
LINKS = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
def graph(nodes, links, lit, t, lt, flow=.25):
    m = U[:, 0]; P = DUST.copy()*.9; Bv = np.full(N, .1); C = cfill(LAV)
    nid = (U[:, 1]*len(nodes)).astype(int)
    isn = m < .38
    P = np.where(isn[:, None], nodes[nid] + SPH_P*.2, P)
    Bv = np.where(isn, .4 + 1.0*lit[nid], Bv)
    C = np.where(isn[:, None], WH*(1-lit[nid, None]*.5) + BLG*lit[nid, None]*.5, C)
    il = (m >= .38) & (m < .85)
    lid = (U[:, 2]*len(links)).astype(int)
    la = np.array([l[0] for l in links])[lid]; lb = np.array([l[1] for l in links])[lid]
    u = U[:, 3]
    seg = nodes[la]*(1-u)[:, None] + nodes[lb]*u[:, None] + G*.012
    llit = np.minimum(lit[la], lit[lb])
    pulse = np.exp(-((((u - lt*flow) % 1) - .5)**2)/.004)
    P = np.where(il[:, None], seg, P)
    Bv = np.where(il, .18 + .5*llit + 1.0*pulse*llit, Bv)
    C = np.where(il[:, None], BLG, C)
    return P, Bv, C

def sh_access(t, lt):
    """A glowing data platform the documents stand on."""
    m = U[:, 0]; a = U[:, 1]*2*np.pi + t*.08
    ring = m < .45; disc = (m >= .45) & (m < .8)
    r = np.where(ring, 3.3 + .06*G[:, 0], 3.2*np.sqrt(U[:, 2]))
    P = np.stack([np.cos(a)*r, np.full(N, -1.25) + .02*G[:, 1], np.sin(a)*r*.55], 1)
    P = np.where((ring | disc)[:, None], P, DUST*.9)
    Bv = np.where(ring, .7, np.where(disc, .16 + .3*(np.sin(r*6 - t*2) > .9), .1))
    C = np.where(ring[:, None], BLG, np.where(disc[:, None], WH, LAV))
    return P, Bv, C

KG = ["Supplier", "Invoice", "Payment"]
KG_A = np.array([[-.95, .65, .1], [.9, .6, -.3], [.1, -.8, .35], [-1.3, -.55, -.7], [1.45, -.3, .6], [.3, 1.3, .9]])
KG_L = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 4), (2, 4), (1, 5)]
def sh_ask(t, lt):
    t0 = word_time("ask", "cited") - SC["ask"] - 1.6
    lit = np.array([fl(ease((lt - t0 - k*.6)/.6)) for k in range(3)] + [.12, .12, .12])
    return graph(KG_A, KG_L, lit, t, lt, flow=.4)

def sh_ai(t, lt):
    """Governed history feeds AI: the missing quadrant of the sphere fills in."""
    P0, B0, C0 = sh_ai_gap(t, t - SC["t5"])
    k = eout((lt - .5 - U[:, 5]*1.2)/1.0)
    src = np.array([0, -2.4, 0]) + G*.3
    Pw = src*(1-k)[:, None] + SPH*k[:, None]
    P = np.where(AI_WEDGE[:, None], rot_y(Pw, .25 - cam_yaw(t) + .08*(t - SC["t5"])), P0)
    band = .55 + .5*AI_BAND
    Bv = np.where(AI_WEDGE, band*(.3+.9*k) + .4, B0)
    C = np.where(AI_WEDGE[:, None], BLG, C0)
    sw = np.exp(-((SPH[:, 1] - (((lt*.5) % 1.4) - .7)*1.6)/.08)**2)
    return P, Bv + .7*sw*(lt > 2), C

def sh_sign(t, lt):
    """A slow halo around the Solix mark."""
    a = U[:, 0]*2*np.pi + t*.12
    r = 2.5 + .07*G[:, 0] + .25*(U[:, 1] > .8)*U[:, 2]
    P = np.stack([np.cos(a)*r, .05*G[:, 1], np.sin(a)*r], 1)
    d = U[:, 3] > .85
    P = np.where(d[:, None], DUST*1.1, P)
    Bv = np.where(d, .12, .55 + .3*np.sin(a*3 + t))
    C = np.where(d[:, None], LAV, np.where((U[:, 4] > .5)[:, None], BLG, WH))
    return P, Bv, C

SHAPES = dict(hook=sh_hook, t1=sh_cost, t2=sh_risk, t3=sh_mna, t4=sh_archive, t5=sh_ai_gap, one=sh_one,
              connect=sh_connect, migrate=sh_migrate, dark=sh_dark, access=sh_access, ask=sh_ask, ai=sh_ai, sign=sh_sign)
MORPH = dict(t1=.8, t2=.6, t3=.6, t4=.6, t5=.6, one=1.0, connect=1.4, migrate=1.4, dark=.8, access=1.4, ask=1.4, ai=1.0, sign=1.6)
DELAY = U[:, 5]*.35

def particles(t):
    sid = scene_at(t); k = ORDER.index(sid); lt = t - SC[sid]
    P, Bv, C = SHAPES[sid](t, lt)
    if k > 0:
        dur = MORPH.get(sid, 1.0)
        if lt < dur*1.4:
            prev = ORDER[k-1]
            P0, B0, C0 = SHAPES[prev](t, t - SC[prev])
            u = ease((lt/dur - DELAY)/(1-.35))
            P = P0*(1-u)[:, None] + P*u[:, None] + (np.sin(np.pi*u)*.55)[:, None]*G
            Bv = B0*(1-u) + Bv*u
            C = C0*(1-u)[:, None] + C*u[:, None]
    return P, Bv, C

# ---------------------------------------------------------------- camera
CAMX = dict(hook=960, t1=1300, t2=1300, t3=1300, t4=1300, t5=1300, one=960, connect=1200,
            migrate=1270, dark=1270, access=960, ask=1330, ai=1270, sign=960)
CAMY = dict(hook=430, one=610, access=640, sign=390)
CAMS = dict(hook=1.0, t1=1.15, t2=1.15, t3=1.15, t4=1.1, t5=1.15, one=1.15, connect=1.0, migrate=1.15,
            dark=1.05, access=1.1, ask=1.05, ai=1.15, sign=1.0)
# red key-light behind the subject (x, y, strength); the end card drops it low so the red logo reads
GLOW = dict(sign=(960, 1000, .75))
def lerp_scene(t, d, dflt):
    sid = scene_at(t); k = ORDER.index(sid); lt = t - SC[sid]
    v = np.array(d.get(sid, dflt), float)
    if k > 0:
        u = fl(einout(lt/1.3)); v = np.array(d.get(ORDER[k-1], dflt), float)*(1-u) + v*u
    return v
def cam(t):
    sid = scene_at(t); lt = t - SC[sid]
    cx = fl(lerp_scene(t, CAMX, 960)); cy = fl(lerp_scene(t, CAMY, 560)); cs = fl(lerp_scene(t, CAMS, 1.0))
    pitch = .26 + .08*math.sin(.17*t)
    push = 1 + .05*fl(clamp(lt/6, 0, 1))
    return cx, cy, cs*push, cam_yaw(t), pitch

FOC = 860
def cam_dist(t):
    """Dolly: the film opens flying in through the legacy screens."""
    return 4.4 + 3.2*(1 - fl(eout(t/(SC["t1"] + .4))))

LIGHT = np.array([-.45, .6, -.66]); LIGHT /= np.linalg.norm(LIGHT)
def project(P, t, shade=False):
    cx, cy, cs, yaw, pitch = cam(t); D = cam_dist(t)
    c, s = math.cos(yaw), math.sin(yaw)
    x = P[:, 0]*c + P[:, 2]*s; z = -P[:, 0]*s + P[:, 2]*c; y = P[:, 1]
    cp, sp = math.cos(pitch), math.sin(pitch)
    y2 = y*cp - z*sp; z2 = y*sp + z*cp
    zc = z2 + D
    f = FOC*cs/np.maximum(zc, .3)
    if not shade: return cx + x*f, cy - y2*f, zc
    r = np.sqrt(x*x + y2*y2 + z2*z2) + 1e-6
    lam = (x*LIGHT[0] + y2*LIGHT[1] + z2*LIGHT[2])/r
    sh = np.where(r < 2.2, .42 + .85*np.maximum(lam, 0) + .25*np.maximum(-z2/r, 0), 1.0)  # key + rim-ish front fill
    return cx + x*f, cy - y2*f, zc, sh, D

# ---------------------------------------------------------------- background
YY, XX = np.mgrid[0:H//4, 0:W//4].astype(np.float32)*4
IND_DK = np.array([14, 10, 40], np.float32)/255
IND = INDIGO*.85
RED_DK = np.array([120, 14, 28], np.float32)/255
def background(t):
    cx, cy, *_ = cam(t)
    gx, gy, gs = lerp_scene(t, GLOW, (cx, cy + 40, 1.0))
    # indigo base: darker toward the top-left corner and edges
    base = IND_DK + (IND - IND_DK)*np.clip(1 - np.sqrt(((XX-1100)/1500)**2 + ((YY-650)/900)**2), 0, 1)[..., None]
    d = np.sqrt(((XX - gx)/980)**2 + ((YY - gy)/760)**2)
    a = (np.clip(1 - d, 0, 1)**1.35)*gs
    img = base + (RED_DK - base)*np.clip(a*1.7, 0, 1)[..., None]
    img = img + (RED - img)*(a**1.9*.85)[..., None]
    # blue light leak, bottom-left, drifting
    b = np.exp(-(((XX - (260 + 160*math.sin(t*.07)))/620)**2 + ((YY - 1000)/360)**2))
    img = img + (BLUE - img)*(.32*b)[..., None]
    # cool rim from top-right
    b2 = np.exp(-(((XX - 1900)/700)**2 + ((YY + 60)/420)**2))
    img = img + (INDIGO*1.3 - img)*(.35*b2)[..., None]
    return zoom(img, (4, 4, 1), order=1)

GRAIN = [(np.random.default_rng(i).standard_normal((H, W, 1)).astype(np.float32)*.011) for i in range(6)]
BOKEH = np.random.default_rng(5).random((48, 6))
BOKEH_C = [BLG, WH, RDG, LAV]

def glow_layer(t, flash=0.0):
    P, Bv, C = particles(t)
    sid = scene_at(t)
    sx, sy, zc, sh, D = project(P, t, shade=True)
    hw, hh = W//2, H//2
    near = clamp((D - .2 - zc)/1.3, 0, 1)
    far = clamp((zc - D - .3)/1.6, 0, 1)
    depth = clamp(1.3 - (zc - D)*.28, .25, 1.9)
    hazec = C*(1-far[:, None]*.6) + LAV*far[:, None]*.6
    w0 = Bv*depth*sh
    pts = [(sx/2, sy/2, w0, hazec, near, far)]
    if sid != "hook":
        # floor reflection under the subject
        FLOOR = -1.55
        Pr = P.copy(); Pr[:, 1] = 2*FLOOR - P[:, 1]
        rx, ry, rz = project(Pr, t)
        wr = Bv*.16*np.exp(-np.maximum(P[:, 1]-FLOOR, 0)*1.1)*(np.abs(P[:, 0]) < 3)
        pts.append((rx/2, ry/2, wr, C, np.zeros(N), np.ones(N)))
    bufs = {k: np.zeros((3, hh*hw), np.float32) for k in ("s", "n", "f")}
    for x, y, w, col, nr, fr in pts:
        ok = (x > 1) & (x < hw-2) & (y > 1) & (y < hh-2) & (w > 1e-4)
        x, y, w, col, nr, fr = x[ok], y[ok], w[ok], col[ok], nr[ok], fr[ok]
        x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
        fx = (x-x0).astype(np.float32); fy = (y-y0).astype(np.float32)
        parts = dict(s=w*(1-nr)*(1-fr), n=w*nr, f=w*fr)
        for dx, dy, ww in ((0, 0, (1-fx)*(1-fy)), (1, 0, fx*(1-fy)), (0, 1, (1-fx)*fy), (1, 1, fx*fy)):
            idx = (y0+dy)*hw + x0+dx
            for key, pw in parts.items():
                for ch in range(3):
                    bufs[key][ch] += np.bincount(idx, pw*ww*col[:, ch], hh*hw).astype(np.float32)
    S = bufs["s"].reshape(3, hh, hw); Nn = bufs["n"].reshape(3, hh, hw); F = bufs["f"].reshape(3, hh, hw)
    I = gaussian_filter(S, (0, .6, .6))*1.9 + gaussian_filter(Nn, (0, 1.5, 1.5))*2.6 + gaussian_filter(F, (0, 2.3, 2.3))*2.4
    q = zoom(S + Nn + F, (1, .5, .5), order=1)
    bloom = zoom(gaussian_filter(q, (0, 7, 7)), (1, 2, 2), order=1)[:, :hh, :hw]*3.2
    bloom2 = zoom(gaussian_filter(q, (0, 30, 30)), (1, 2, 2), order=1)[:, :hh, :hw]*(4.5 + 12*flash)
    bk = np.zeros((3, hh//2, hw//2), np.float32)
    for bx, by, bz, bs, bp, bc in BOKEH:
        px = ((bx*1.3 - .15 + t*.006*(1+bz)) % 1.3 - .15)*hw/2; py = (by + .01*math.sin(t*.2+bp*6))*hh/2
        if 0 <= px < hw/2-1 and 0 <= py < hh/2-1:
            bk[:, int(py), int(px)] += BOKEH_C[int(bc*4)]*(.6 + bs)*(.6+.4*math.sin(t*.5+bp*9))
    bk = zoom(gaussian_filter(bk, (0, 5, 5)), (1, 2, 2), order=1)[:, :hh, :hw]*24
    tot = (I + bloom + bloom2 + bk).transpose(1, 2, 0)
    return zoom(tot, (2, 2, 1), order=1)

def compose_bg(t, flash=0.0):
    bg = background(t)
    g = glow_layer(t, flash)
    lit = 1 - np.exp(-g*.9)
    out = bg + (1 - bg)*lit
    hot = np.clip((g.max(-1, keepdims=True) - 1.6)/3.5, 0, 1)   # very dense cores burn to white
    return out + (1 - out)*hot*.7

VIG = None
def vignette():
    global VIG
    if VIG is None:
        vy, vx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((vx-W/2)/(W*.62))**2 + ((vy-H/2)/(H*.62))**2)
        VIG = (1 - .5*np.clip(d-.5, 0, 1)**1.5)[..., None]
    return VIG

# ---------------------------------------------------------------- typography
@lru_cache(None)
def font(name, size): return ImageFont.truetype(FD + name, size)

@lru_cache(None)
def word_img(text, fname, size, track=0):
    f = font(fname, size)
    widths = [f.getlength(ch) for ch in text] if track else None
    tw = int(sum(widths) + track*(len(text)-1)) if track else int(f.getlength(text))
    asc, desc = f.getmetrics()
    pad = int(size*.5)
    im = Image.new("L", (tw + 2*pad, asc + desc + 2*pad), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = pad
        for ch, wd in zip(text, widths): d.text((x, pad), ch, font=f, fill=255); x += wd + track
    else:
        d.text((pad, pad), text, font=f, fill=255)
    a = np.asarray(im, np.float32)/255
    sh = np.asarray(im.filter(ImageFilter.GaussianBlur(size*.12)), np.float32)/255*.55
    return a, sh, pad, tw, asc

@lru_cache(None)
def blurred(text, fname, size, track, level):
    a = word_img(text, fname, size, track)[0]
    im = Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(level))
    return np.asarray(im, np.float32)/255

SHADOW = np.array([.05, .02, .12], np.float32)
def put(frame, text, fname, size, x, y, alpha=1.0, blur=0.0, rgb=(1, 1, 1), track=0, anchor="ls", shadow=True):
    """Composite a text run with baseline at (x, y). anchor 'ls' left-baseline, 'ms' middle-baseline."""
    if alpha <= .003: return
    a, sh, pad, tw, asc = word_img(text, fname, size, track)
    lv = int(round(min(blur, 12)/2)*2)
    if lv: a = blurred(text, fname, size, track, lv)
    if anchor == "ms": x -= tw/2
    x0 = int(round(x - pad)); y0 = int(round(y - asc - pad))
    h, w = a.shape
    fx0, fy0 = max(0, x0), max(0, y0); fx1, fy1 = min(W, x0+w), min(H, y0+h)
    if fx1 <= fx0 or fy1 <= fy0: return
    aa = a[fy0-y0:fy1-y0, fx0-x0:fx1-x0, None]*alpha
    reg = frame[fy0:fy1, fx0:fx1]
    if shadow:
        ss = sh[fy0-y0:fy1-y0, fx0-x0:fx1-x0, None]*alpha
        reg[:] = reg*(1-ss) + SHADOW*ss
    reg[:] = reg*(1-aa) + np.asarray(rgb, np.float32)*aa

def put3d(frame, text, fname, size, x, y, alpha, t, depth=16, blur=0.0, face=(1, 1, 1)):
    """Extruded 3D type: stacked layers toward a slowly moving vanishing direction, lit face on top."""
    if alpha <= .003: return
    ang = .9 + .35*math.sin(t*.6)
    dx, dy = math.cos(ang)*1.15, math.sin(ang)*1.15
    for i in range(depth, 0, -1):
        k = i/depth
        col = INDIGO*(1-k)*1.15 + np.array([.04, .02, .1])*k
        put(frame, text, fname, size, x + dx*i, y + dy*i, alpha, blur=blur, rgb=col, shadow=(i == depth))
    put(frame, text, fname, size, x + dx*.6, y + dy*.6, alpha*.9, blur=blur, rgb=BLUE*.9 + .1, shadow=False)  # blue edge highlight
    put(frame, text, fname, size, x, y, alpha, blur=blur, rgb=face, shadow=False)

def measure(text, fname, size, track=0):
    f = font(fname, size)
    if track: return sum(f.getlength(c) for c in text) + track*(len(text)-1)
    return f.getlength(text)

def wrap(text, fname, size, maxw):
    lines = [[]]
    for wd in text.split(" "):
        if lines[-1] and measure(" ".join(lines[-1] + [wd]), fname, size) > maxw: lines.append([wd])
        else: lines[-1].append(wd)
    return lines

WHITE = (1, 1, 1)
def kinetic(frame, t, text, x, y, size, t_in, t_out, fname="InterDisplay-Bold.otf", maxw=900,
            align="left", lh=1.08, stagger=.07, rise=34, hl=(), hlc=BLUE, dur=.65):
    """Word-by-word reveal: each word rises, sharpens and fades in; exits drifting up and softening.
    Words in `hl` are set in the highlight colour."""
    if t < t_in - .01 or t > t_out + .6: return
    lines = wrap(text, fname, size, maxw)
    sp = measure(" ", fname, size); k = 0
    q = fl(ease((t - t_out)/.5))
    for li, ln in enumerate(lines):
        lw = measure(" ".join(ln), fname, size)
        xx = x - (lw/2 if align == "center" else 0)
        yy = y + li*size*lh
        for wd in ln:
            p = fl(eout((t - t_in - k*stagger)/dur))
            a = p*(1-q)
            if a > .003:
                col = hlc if wd.strip(".,:") in hl else WHITE
                put(frame, wd, fname, size, xx, yy + (1-p)*rise - q*18, a, blur=(1-p)*10 + q*8, rgb=col)
            xx += measure(wd, fname, size) + sp; k += 1

def fade_text(frame, t, text, x, y, size, t_in, t_out, fname="Inter-Medium.otf", anchor="ls", alpha=1.0, track=0, rgb=WHITE, dur=.45):
    a = fl(ease((t - t_in)/dur))*(1 - fl(ease((t - t_out)/.4)))*alpha
    if a > .003: put(frame, text, fname, size, x, y + (1-fl(eout((t-t_in)/dur)))*12, a, rgb=rgb, track=track, anchor=anchor)

# ---------------------------------------------------------------- logo (original colours, unaltered)
LOGO = np.asarray(Image.open(f"{ASSETS}/logo_white.png").convert("RGBA"), np.float32)/255
def logo_scaled(h):
    im = Image.fromarray((LOGO*255).astype(np.uint8), "RGBA")
    return np.asarray(im.resize((int(im.width*h/im.height), h), Image.LANCZOS), np.float32)/255
LOGO_SM = logo_scaled(50); LOGO_LG = logo_scaled(160); LOGO_TI = logo_scaled(118)
def put_rgba(frame, img, x, y, alpha):
    if alpha <= .003: return
    h, w = img.shape[:2]; x, y = int(x), int(y)
    a = img[..., 3:]*alpha
    frame[y:y+h, x:x+w] = frame[y:y+h, x:x+w]*(1-a) + img[..., :3]*a

# ---------------------------------------------------------------- Access beat: 3D documents
KINDS = ["po", "gr", "inv", "pay"]
STEPS = ["Ordered", "Received", "Invoiced", "Paid"]
CW, CH = 1.62, 1.62*900/760
def slot(k):
    x = -2.85 + 1.9*k
    return np.array([x, -.15, .35*(x/2.85)**2]), .25*(x/2.85)
def lerp(a, b, u): return a*(1-u) + b*u
def access_docs(fr, t):
    s = "access"; SA = SC[s]; ta = word_time(s, "Auditors"); tu = LN["access2"]["start"]; te = SC_END[s] - .45
    out = fl(ease((t - te)/.45))
    cam = DOC.Cam(960 + 18*math.sin(t*.4), 600, 1050, 5.6, yaw=.07*math.sin(t*.35), pitch=.09)
    # Solix Search
    p = fl(eout((t - SA + .1)/.6)); q = fl(ease((t - ta - .15)/.55))
    if p > 0 and q < 1:
        n = int(fl(clamp((t - SA - .3)/.75))*len(DOC.VENDOR))
        rows = int(fl(clamp((t - SA - 1.08)/.4))*4 + .999) if t > SA + 1.08 else 0
        tex = DOC.search(n, min(rows, 4), t > SA + 1.55)
        c = lerp(np.array([3.0, -1.0, 2.5]), np.array([.35, .05, -1.6]), p) + np.array([-2.5, 1.6, 3.0])*q
        qd, nn, _ = DOC.quad(cam, c, 3.4, 3.4*760/1280, yaw=lerp(-.9, -.18, p) - .6*q, pitch=.05, roll=lerp(.15, 0, p))
        DOC.draw(fr, tex, qd, nn, alpha=p*(1-q), sheen=lerp(-.2, 1.3, fl(clamp((t - SA - .1)/.8))))
    # purchase-to-pay record
    rec = fl(ease((t - tu + .1)/.8))   # row recedes when the report arrives
    quads = []; alphas = []
    order = []
    for k, kind in enumerate(KINDS):
        tk = ta + .3 + .72*k
        a = fl(eout((t - tk)/.8)); b = fl(einout((t - tk - .8)/.6))
        if a <= 0: quads.append(None); alphas.append(0); continue
        sp, syaw = slot(k)
        start = np.array([4.6, -1.8, 3.2]); hero = np.array([.55, .05, -2.0])
        c = lerp(lerp(start, hero, a), sp, b) + np.array([0, .3, 1.6])*rec
        yaw = lerp(lerp(-1.5, -.12, a), syaw, b); roll = lerp(.25, 0, a)
        al = (1 - out)*(1 - .62*rec)
        order.append((c[2], k, c, yaw, roll, al, tk))
        sp_c = DOC.quad(cam, sp + np.array([0, .3, 1.6])*rec, CW, CH, yaw=syaw)[0]
        quads.append(sp_c if b > .98 else None); alphas.append(al)
    for z, k, c, yaw, roll, al, tk in sorted(order, key=lambda o: -o[0]):
        qd, nn, _ = DOC.quad(cam, c, CW, CH, yaw=yaw, roll=roll)
        if KINDS[k] == "pay":
            st = fl(ease((t - tk - .75)/.18))
            DOC.draw(fr, DOC.doc("pay", 0), qd, nn, alpha=al*(1 - st), sheen=lerp(-.2, 1.3, fl(clamp((t - tk - .2)/.7))))
            if st > 0: DOC.draw(fr, DOC.doc("pay", 1), qd, nn, alpha=al*st, shadow=0)
        else:
            DOC.draw(fr, DOC.doc(KINDS[k]), qd, nn, alpha=al, sheen=lerp(-.2, 1.3, fl(clamp((t - tk - .2)/.7))))
        # step label under each settled card
        if quads[k] is not None:
            bm = (quads[k][2] + quads[k][3])/2
            la = al*fl(ease((t - tk - 1.3)/.4))
            put(fr, f"0{k+1}", "Inter-SemiBold.otf", 24, bm[0] - measure(STEPS[k], "InterDisplay-SemiBold.otf", 30)/2 - 22, bm[1] + 50, la, rgb=BLUE*1.2, anchor="ms")
            put(fr, STEPS[k], "InterDisplay-SemiBold.otf", 30, bm[0] + 18, bm[1] + 50, la, anchor="ms")
    # glowing links tying the four documents together (drawn on as each pair settles)
    lay = Image.new("L", (W//2, H//2), 0); dr = ImageDraw.Draw(lay); any_l = False
    for k in range(3):
        if quads[k] is None or quads[k+1] is None: continue
        u = fl(eout((t - (ta + .3 + .72*(k+1) + 1.4))/.45))
        if u <= 0: continue
        p0 = (quads[k][0] + quads[k][1])/2; p1 = (quads[k+1][0] + quads[k+1][1])/2
        ctrl = (p0 + p1)/2 - np.array([0, 70])
        ss = np.linspace(0, u, 40)[:, None]
        pts = (1-ss)**2*p0 + 2*(1-ss)*ss*ctrl + ss**2*p1
        dr.line([tuple(v) for v in pts/2], fill=255, width=2); any_l = True
        dr.ellipse(tuple(np.r_[p0/2 - 4, p0/2 + 4]), fill=255)
        if u >= 1:
            dr.ellipse(tuple(np.r_[p1/2 - 4, p1/2 + 4]), fill=255)
            ph = ((t*.8 + k*.33) % 1.0)
            pd = (1-ph)**2*p0 + 2*(1-ph)*ph*ctrl + ph**2*p1
            dr.ellipse(tuple(np.r_[pd/2 - 5, pd/2 + 5]), fill=255)
    if any_l:
        L = np.asarray(lay, np.float32)/255*(1 - out)*(1 - .62*rec)
        g = L*1.2 + gaussian_filter(L, 5)*3.5
        g = zoom(g, 2, order=1)[:H, :W, None]
        fr[:] = fr + (1 - fr)*np.clip(g, 0, 1)*np.array([.35, .78, 1.0], np.float32)
    # Enterprise Business Record kicker
    ka = fl(ease((t - (ta + .3 + .72*3 + 1.2))/.5))*(1 - out)*(1 - rec)
    if ka > 0:
        put(fr, "ENTERPRISE BUSINESS RECORD  ·  " + DOC.VENDOR.upper(), "Inter-SemiBold.otf", 24, W/2, 352, ka, track=5, anchor="ms", rgb=BLUE*1.25)
    # standard report flies forward
    r = fl(eout((t - tu + .1)/.95))
    if r > 0:
        c = lerp(np.array([3.8, -2.2, 2.5]), np.array([.5, -.2, -2.25]), r)
        qd, nn, _ = DOC.quad(cam, c, 2.6, 2.6*820/1180, yaw=lerp(-1.0, -.14, r), pitch=lerp(.5, .04, r), roll=lerp(-.2, 0, r))
        DOC.draw(fr, DOC.doc("report"), qd, nn, alpha=r*(1 - out), sheen=lerp(-.2, 1.3, fl(clamp((t - tu - .3)/.8))))

# ---------------------------------------------------------------- overlays per scene
LX = 150
def overlays(fr, t):
    sid = scene_at(t)
    E = lambda s: SC_END[s] - .45
    T0 = LN["hook"]["start"]
    put_rgba(fr, LOGO_SM, W - 90 - LOGO_SM.shape[1], 56, (1 - fl(ease((t - SC["sign"] + .2)/.6)))*fl(ease((t - T0 - .3)/.5)))

    # 0. Main title: the original Solix logo and an extruded 3D "Application Retirement"
    if t < T0 + 1.0:
        p = fl(eout((t - .3)/.9)); q = fl(ease((t - (T0 - .15))/.6))
        put_rgba(fr, LOGO_TI, W/2 - LOGO_TI.shape[1]/2 + 10, 300 - 30*(1-p) - 60*q, fl(ease((t - .1)/.6))*(1-q))
        sc = (1.16 - .16*p)*(1 + .4*q)
        size = int(128*sc); tw = measure("Application Retirement", "InterDisplay-Bold.otf", size)
        put3d(fr, "Application Retirement", "InterDisplay-Bold.otf", size, W/2 - tw/2, 580 + 40*q, p*(1-q), t,
              depth=18, blur=(1-p)*10 + q*12)
        fade_text(fr, t, "EMPOWER 2026", W/2, 670 + 40*q, 28, .9, T0 - .15, fname="Inter-SemiBold.otf", anchor="ms",
                  track=8, rgb=BLUE*1.2)

    # 1. Hook
    kinetic(fr, t, "Applications you've moved on from.", LX, 860, 84, T0 + .5, E("hook"), maxw=1600)

    # 2. Five triggers: one extruded 3D word each
    for tid, word in (("t1", "Cost"), ("t2", "Risk"), ("t3", "M&A"), ("t4", "Old archive"), ("t5", "AI")):
        a0 = LN[tid]["start"] - .1; a1 = SC_END[tid] - .25
        if a0 - .1 <= t <= a1 + .6:
            p = fl(eout((t - a0)/.35)); q = fl(ease((t - a1)/.25))
            sc = 1.12 - .12*p; al = p*(1-q)
            size = int((200 if len(word) < 6 else 150)*sc)
            put3d(fr, word, "InterDisplay-Bold.otf", size, LX - (sc-1)*60, 560, al, t, blur=(1-p)*8 + q*10,
                  face=(RED*.25 + .75) if tid == "t2" else WHITE)
            put(fr, f"0{ORDER.index(tid)}  /  05", "Inter-SemiBold.otf", 28, LX + 6, 330, al, track=4, rgb=BLUE*1.15)

    # 3. Converge
    kinetic(fr, t, "Many reasons.", W/2, 190, 88, LN["one"]["start"], LN["connect"]["start"] + .1, align="center", maxw=1600)
    kinetic(fr, t, "One engine.", W/2, 292, 88, word_time("one", "One engine"), LN["connect"]["start"] + .1, align="center",
            maxw=1600, hl=("One", "engine"))

    # Act 2-3 step tracker (text only): Connect > Migrate & Validate > Enable AI
    t_on, t_off = SC["connect"] + .2, SC["sign"] - .2
    if t_on - .1 < t <= t_off + .5:
        ga = fl(ease((t - t_on)/.6))*(1 - fl(ease((t - t_off)/.5)))
        steps = [("CONNECT", ("connect",)), ("MIGRATE & VALIDATE", ("migrate", "dark")), ("ENABLE AI", ("ai",))]
        done = {"connect": 0, "migrate": 1, "dark": 1, "access": 2, "ask": 2, "ai": 2}.get(sid, 0)
        x = LX
        for i, (lab, ss) in enumerate(steps):
            act = sid in ss
            if act:
                put(fr, "●", "Inter-SemiBold.otf", 18, x, 98, ga, rgb=BLUE*1.15); x += 26
            put(fr, lab, "Inter-SemiBold.otf", 24, x, 100, ga*(1.0 if act else (.62 if i < done else .34)), track=3)
            x += measure(lab, "Inter-SemiBold.otf", 24, 3) + 22
            if i < 2:
                put(fr, "›", "Inter-SemiBold.otf", 24, x, 100, ga*.4); x += 36

    # 4. Connect
    s = "connect"
    kinetic(fr, t, "Every source.", LX, 300, 88, SC[s] + 1.2, E(s), maxw=800, hl=("Every", "source"))
    kinetic(fr, t, "One engine.", LX, 396, 88, SC[s] + 1.6, E(s), maxw=800)
    if SC[s] - .2 <= t <= SC_END[s] + .6:
        sx, sy, zc = project(SRC_A, t)
        for k, (lab, wd) in enumerate(zip(SRC, SRC_W)):
            sz = int(np.clip(30 + (cam_dist(t) - zc[k])*8, 24, 42))
            fade_text(fr, t, lab, sx[k], sy[k] - 38, sz, word_time(s, wd), E(s), fname="InterDisplay-SemiBold.otf", anchor="ms",
                      alpha=fl(clamp(1.35 - (zc[k]-cam_dist(t))*.35, .45, 1)))

    # 5. Migrate & Validate
    s = "migrate"
    kinetic(fr, t, "Governed from the day it lands.", LX, 300, 80, SC[s] + .3, E(s), maxw=760, hl=("Governed",))
    checks = ["Validated against source", "Quality checked", "Retention applied", "Legal hold ready"]
    tc = [word_time(s, "checked") - .2, word_time(s, "checked") + .5, word_time(s, "retention"), word_time(s, "legal hold")]
    for k, (c, ti) in enumerate(zip(checks, tc)):
        fade_text(fr, t, "✓", LX, 570 + k*64, 40, ti, E(s), fname="InterDisplay-Bold.otf", rgb=BLUE*1.2)
        fade_text(fr, t, c, LX + 56, 570 + k*64, 40, ti + .08, E(s), fname="InterDisplay-Medium.otf")

    # 6. Switch off
    s = "dark"
    kinetic(fr, t, "Then the application goes dark.", LX, 300, 80, SC[s] + .3, E(s), maxw=760)
    kinetic(fr, t, "For good.", LX, 490, 80, word_time(s, "gone for good"), E(s), maxw=760, hl=("For", "good"), hlc=RED*.4 + .6*np.array([1, .55, .55]))
    for k, (lab, wd) in enumerate((("Licenses", "licenses"), ("Servers", "servers"), ("Unpatched risk", "risk"))):
        ti = word_time(s, wd) - .1
        fall = max(0.0, t - ti - .9)
        x = 1270 + (-340, 280, -30)[k]; y = (420, 470, 780)[k] + 240*fall**2
        a = fl(eout((t - ti)/.35))*(1 - fl(ease((t - ti - .9)/1.0)))
        put(fr, lab, "InterDisplay-SemiBold.otf", 42, x, y, a, blur=fl(clamp(fall*8, 0, 10)), anchor="ms")
    fade_text(fr, t, "PRESERVATION ZONE  ·  STILL ON", 1270, 930, 26, word_time(s, "gone for good") - .2, E(s),
              fname="Inter-SemiBold.otf", anchor="ms", track=4, rgb=BLUE*1.2)

    # 7. Access: Solix Search, then the purchase-to-pay record in 3D, then a standard report
    s = "access"
    if SC[s] - .2 <= t <= SC_END[s] + .6:
        access_docs(fr, t)
    ta, tu = word_time(s, "Auditors"), LN["access2"]["start"]
    fade_text(fr, t, "Nothing it held is lost.", LX, 250, 56, SC[s] + .3, ta - .3, fname="InterDisplay-SemiBold.otf")
    kinetic(fr, t, "Provable records.", LX, 230, 64, ta - .1, E(s), maxw=900, hl=("Provable",))
    kinetic(fr, t, "Familiar reports.", LX, 302, 64, tu - .1, E(s), maxw=900, hl=("Familiar",))

    # 8. Data Ask
    s = "ask"
    kinetic(fr, t, "Ask in plain English.", LX, 300, 80, SC[s] + .3, E(s), maxw=860)
    kinetic(fr, t, "Get cited answers.", LX, 392, 80, word_time(s, "cited"), E(s), maxw=860, hl=("cited", "answers"))
    q = "“Which suppliers were paid late in 2021?”"
    tq = word_time(s, "ask in plain")
    if tq <= t <= SC_END[s] + .6:
        n = int(fl(clamp((t - tq)/1.9))*len(q))
        a = 1 - fl(ease((t - E(s))/.4))
        if n: put(fr, q[:n], "Inter-Italic.otf", 38, LX, 550, a*.95)
        if n < len(q) and int(t*2.5) % 2 == 0:
            put(fr, "|", "Inter-Medium.otf", 38, LX + measure(q[:n], "Inter-Italic.otf", 38) + 4, 550, a*.8, rgb=BLUE*1.2)
    ta = word_time(s, "cited") + .4
    fade_text(fr, t, "3 suppliers", LX, 624, 34, ta, E(s), fname="Inter-SemiBold.otf")
    fade_text(fr, t, "Sources  [1]  [2]  [3]", LX + measure("3 suppliers", "Inter-SemiBold.otf", 34) + 30, 624, 34, ta + .25, E(s),
              fname="Inter-SemiBold.otf", rgb=BLUE*1.2)
    if SC[s] - .2 <= t <= SC_END[s] + .6:
        sx, sy, zc = project(KG_A, t)
        t0 = word_time(s, "cited") - 1.6 + .2
        for k, lab in enumerate(KG):
            fade_text(fr, t, lab, sx[k], sy[k] - 54, 36, t0 + k*.6, E(s), fname="InterDisplay-SemiBold.otf", anchor="ms")
        fade_text(fr, t, "APPLICATION KNOWLEDGE GRAPH", 1330, 215, 24, t0, E(s), fname="Inter-SemiBold.otf", anchor="ms", track=5, rgb=BLUE*1.2)

    # 9. Enable AI
    s = "ai"
    if SC[s] - .1 <= t <= SC_END[s] + .6:
        p = fl(eout((t - SC[s] - .35)/.6)); q = fl(ease((t - E(s))/.5))
        put3d(fr, "Enable AI", "InterDisplay-Bold.otf", 130, LX, 480 + (1-p)*30, p*(1-q), t, blur=(1-p)*8 + q*8)
    fade_text(fr, t, "Governed history, ready for your AI.", LX + 4, 570, 40, SC[s] + .9, E(s), fname="InterDisplay-Medium.otf")

    # 10. Sign-off
    s = "sign"
    if t >= SC[s] - .1:
        p = fl(eout((t - SC[s] - .3)/1.2))
        lw = LOGO_LG.shape[1]
        put_rgba(fr, LOGO_LG, W/2 - lw/2 + 12, 290 + (1-p)*30, p)
        kinetic(fr, t, "Retire the application.", W/2, 650, 74, word_time(s, "Retire"), T + 5, align="center", maxw=1700)
        kinetic(fr, t, "Keep every answer.", W/2, 742, 74, word_time(s, "Keep every") + .1, T + 5, align="center", maxw=1700,
                hl=("Keep", "every", "answer"))
        fade_text(fr, t, "SOLIXCloud Application Retirement", W/2, 832, 34, word_time(s, "Keep every") + .9, T + 5,
                  fname="Inter-Medium.otf", anchor="ms", alpha=.9)
        fade_text(fr, t, "Data Ask is part of Solix Enterprise AI.  Visuals are illustrative.", W/2, 1030, 20,
                  word_time(s, "Keep every") + 1.4, T + 5, fname="Inter-Regular.otf", anchor="ms", alpha=.55)

def captions(fr, t):
    """VO subtitles: plain text with a soft shadow, no box."""
    LS = TL["lines"]
    for i, L in enumerate(LS):
        if L["id"] == "sign": continue
        t0, t1 = L["start"] - .1, L["end"] + .3
        if i + 1 < len(LS): t1 = min(t1, LS[i+1]["start"] - .35)
        if not (t0 - .1 <= t <= t1 + .3): continue
        a = fl(ease((t - t0)/.2))*(1 - fl(ease((t - t1)/.25)))*.92
        if a <= .003: continue
        lines = wrap(L["caption"], "Inter-Medium.otf", 32, 1400)
        y = 1004 - (len(lines)-1)*42
        for i, ln in enumerate(lines):
            put(fr, " ".join(ln), "Inter-Medium.otf", 32, W/2, y + i*42, a, anchor="ms")

def frame(t):
    to = word_time("one", "One engine")
    flash = 2.5*math.exp(-(t - to)*2.2) if t > to else 0.0
    fr = compose_bg(t, flash).astype(np.float32)
    fr *= vignette()
    overlays(fr, t)
    captions(fr, t)
    fi = 1.0; fo = 1 - fl(ease((t - (T - .9))/.9))
    fr = fr*fi*fo + GRAIN[int(t*FPS) % 6]
    return (np.clip(fr, 0, 1)*255 + .5).astype(np.uint8)

def render_range(i0, i1, out):
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "15",
                          "-pix_fmt", "yuv420p", "-tune", "film", out], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame(i/FPS).tobytes())
        if (i - i0) % 150 == 0: print(out, i, flush=True)
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        os.makedirs(f"{B}/preview", exist_ok=True)
        for ts in sys.argv[2:]:
            Image.fromarray(frame(float(ts))).save(f"{B}/preview/f_{float(ts):05.1f}.jpg", quality=88)
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "seg":
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]); sys.exit()
    NF = int(T*FPS); K = int(os.environ.get("JOBS", "4"))
    os.makedirs(f"{B}/seg", exist_ok=True)
    cuts = [NF*k//K for k in range(K+1)]
    procs = [subprocess.Popen([sys.executable, __file__, "seg", str(cuts[k]), str(cuts[k+1]), f"{B}/seg/s{k}.mp4"]) for k in range(K)]
    for p in procs: p.wait()
    with open(f"{B}/seg/list.txt", "w") as f:
        for k in range(K): f.write(f"file 's{k}.mp4'\n")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{B}/seg/list.txt",
                    "-c", "copy", f"{B}/ar_video.mp4"], check=True)
    print("done")
