# Solix Application Retirement, 60-70 s big-screen film.
# Procedural 3D particle motion graphics on a Solix-red field, with kinetic text-only typography.
# Usage: python3 render_ar.py [preview t1 t2 ...]   (no args = full render to ar_video.mp4)
import json, os, sys, subprocess, math, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, zoom

B = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B, "..", "assets")
W, H, FPS = 1920, 1080, 30
TL = json.load(open(f"{B}/timeline.json")); T = TL["total"]
LN = {l["id"]: l for l in TL["lines"]}
FD = "/usr/share/fonts/opentype/inter/"
N = 3200
rng = np.random.default_rng(11)

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
    s = 0.0 if k == 0 else LN[sid]["start"] - (0.15 if sid.startswith("t") else 0.45)
    SC[sid] = s
SC_END = {sid: (SC[ORDER[k+1]] if k+1 < len(ORDER) else T) for k, sid in enumerate(ORDER)}
def scene_at(t):
    cur = ORDER[0]
    for sid in ORDER:
        if t >= SC[sid]: cur = sid
    return cur

# ---------------------------------------------------------------- particle shapes
U = rng.random((N, 6))
G = rng.standard_normal((N, 3))
def fib(n, r=1.0):
    i = np.arange(n) + .5; phi = np.arccos(1 - 2*i/n); th = np.pi*(1+5**.5)*i
    return np.stack([np.cos(th)*np.sin(phi), np.cos(phi), np.sin(th)*np.sin(phi)], 1)*r
SPH = fib(N)
SPH_P = SPH[rng.permutation(N)]
def dust(spread=4.0, seed=0):
    r = np.random.default_rng(100+seed)
    return (r.random((N, 3))-.5)*np.array([spread*1.8, spread, spread])

DUST = dust(5.0)

def sh_hook(t, lt):
    """Dormant legacy applications: dot-matrix screens drifting in depth, each with a running light."""
    P = DUST.copy()*np.array([1.2, 1.1, 1.0]); Bv = np.full(N, .14)
    cen = np.array([[-2.3, .7, -.6], [-.9, 1.05, .8], [.7, .55, -1.3], [2.2, .9, .2],
                    [-1.6, -.75, .5], [.1, -.55, .6], [1.6, -.85, -.7], [-.3, .15, -2.2]])
    gw, gh = 15, 9; per = gw*gh; k = 0
    for c, (cx, cy, cz) in enumerate(cen):
        gx, gy = np.meshgrid(np.linspace(-.42, .42, gw), np.linspace(-.25, .25, gh))
        yaw = .5*math.sin(c*1.7) + .05*math.sin(t*.3+c)
        x = gx.ravel()*math.cos(yaw); z = gx.ravel()*math.sin(yaw)
        drift = np.array([.08*math.sin(t*.25+c), .06*math.sin(t*.31+c*2), 0])
        P[k:k+per] = np.stack([x+cx, gy.ravel()+cy, z+cz], 1) + drift
        rows = (gy.ravel()+.25)/.5
        Bv[k:k+per] = .26 + .16*(np.sin(gx.ravel()*20+c) > .2)*(rows > .2)
        # running light: top-left corner dot pulses
        Bv[k] = 1.5 + 1.3*math.sin(t*3 + c*1.3)
        k += per
    return P, Bv

def sh_cost(t, lt):
    """A coin: thick ring with an inner disc, turning."""
    a = U[:, 0]*2*np.pi; m = U[:, 1]
    r = np.where(m < .6, 1.0 + .08*np.cos(U[:, 2]*2*np.pi), .82*np.sqrt(U[:, 3]))
    y = np.where(m < .6, .11*np.sin(U[:, 2]*2*np.pi), (U[:, 4]-.5)*.06)
    P = np.stack([r*np.cos(a), r*np.sin(a), y], 1)
    sp = t*1.3; c, s = math.cos(sp), math.sin(sp)
    P = np.stack([P[:, 0]*c+P[:, 2]*s, P[:, 1], -P[:, 0]*s+P[:, 2]*c], 1)
    return P, np.where(m < .6, 1.0, .45)

def sh_risk(t, lt):
    """Unpatched system: a fractured sphere that glitches."""
    seg = np.floor(U[:, 0]*14)
    j = 1 + .22*np.sin(seg*3.1 + t*9)*(np.sin(t*5.3+seg) > .55) + .06*G[:, 0]
    P = SPH_P*j[:, None]*.95
    shake = .03*np.sin(t*40)*(math.sin(t*5) > .6)
    P[:, 0] += shake
    Bv = .75 + .6*(np.sin(seg*7 + t*11) > .8)
    return P, Bv

def sh_mna(t, lt):
    """Acquisition: a second system drawn in and absorbed."""
    half = np.arange(N) < N*.55
    k = eout(lt/1.8)
    off = np.where(half, -.35 - .2*(1-k), .95 - .75*k)
    r = np.where(half, .85, .55)
    P = SPH*r[:, None]; P[:, 0] += off
    return P, np.where(half, .8, 1.1)

def sh_archive(t, lt):
    """Archive at its limit: a stack of layers, the top ones straining."""
    layer = np.floor(U[:, 0]*10); a = U[:, 1]*2*np.pi
    r = .9*np.sqrt(.25 + .75*U[:, 2])
    y = -1.0 + layer*.21 + .02*np.sin(t*2+layer)
    P = np.stack([r*np.cos(a), y, r*np.sin(a)], 1)
    Bv = .5 + .9*(layer >= 8)*(.6+.4*math.sin(t*7))
    return P, Bv

AI_WEDGE = (np.arctan2(SPH[:, 2], SPH[:, 0]) > -1.0) & (np.arctan2(SPH[:, 2], SPH[:, 0]) < 1.5) & (SPH[:, 1] > -.2)
def sh_ai_gap(t, lt):
    """AI program short on history: a neural sphere with a missing wedge."""
    P = SPH*1.0
    band = .55 + .45*(np.abs(np.sin(SPH[:, 1]*9)) > .8)
    P = np.where(AI_WEDGE[:, None], SPH*3.2 + G*.5, P)
    return rot_y(P, 0.25 - cam_yaw(t) + .08*lt), np.where(AI_WEDGE, .08, band)

def sh_one(t, lt):
    """Many reasons converge to a point, then open into the Solix engine."""
    t_open = word_time("one", "One engine") - SC["one"]
    if lt < t_open:
        return G*.025, np.full(N, 1.4)
    k = fl(eout((lt - t_open)/1.4))
    P, Bv = sh_engine(t, lt)
    return P*(.02 + .98*k), Bv*(1 + 1.5*(1-k))

def sh_engine(t, lt):
    m = U[:, 0]
    core = fib(N, .38)
    a = U[:, 1]*2*np.pi + t*.5
    r1 = np.stack([np.cos(a)*.95, .04*G[:, 1], np.sin(a)*.95], 1)
    r2 = np.stack([np.cos(-a*1.3)*1.3, np.sin(-a*1.3)*1.3*.35, np.sin(-a*1.3)*1.3*.94], 1)
    P = np.where((m < .45)[:, None], core, np.where((m < .75)[:, None], r1, r2))
    P = np.where((m > .93)[:, None], DUST*.8, P)
    Bv = np.where(m < .45, 1.0, np.where(m < .93, .8, .15))
    return P, Bv

SRC = ["ERP", "Mainframe", "Custom apps", "SaaS", "Files", "Email"]
SRC_A = np.array([[math.cos(k/6*2*np.pi+.3)*2.25, .9*math.sin(k*2.1), math.sin(k/6*2*np.pi+.3)*1.6] for k in range(6)])
def sh_connect(t, lt):
    """Sources stream into the engine."""
    m = U[:, 0]; s_id = (U[:, 1]*6).astype(int)
    P, Bv = sh_engine(t, lt)
    P = P*.75; Bv = Bv*1.0
    st = (m >= .35) & (m < .88)
    a = SRC_A[s_id]
    ph = (U[:, 2] + lt*.32) % 1.0
    ctrl = a*.5 + np.array([0, .9, 0])
    q = (1-ph)[:, None]**2*a + 2*((1-ph)*ph)[:, None]*ctrl + (ph**2)[:, None]*0
    q += G*.03
    # each source switches on in sequence
    on = np.array([ease((lt - (word_time("connect", w) - SC["connect"]))*2) for w in ["ERP", "mainframe", "custom", "SaaS", "files", "email"]])
    P = np.where(st[:, None], q, P)
    Bv = np.where(st, (.25 + .9*np.sin(ph*np.pi))*on[s_id], Bv)
    an = (m >= .88) & (m < .97)
    P = np.where(an[:, None], a + G*.09, P)
    Bv = np.where(an, .5 + .9*on[s_id], Bv)
    return P, Bv

CUBE_G = np.stack(np.meshgrid(*[np.linspace(-.62, .62, 12)]*3, indexing="ij"), -1).reshape(-1, 3)
def vault(fill):
    n = len(CUBE_G)
    P = DUST.copy()*.9; Bv = np.full(N, .08)
    lvl = (CUBE_G[:, 1]+.62)/1.24
    inside = lvl <= fill
    P[:n] = CUBE_G
    P[:n][~inside] = CUBE_G[~inside] + np.array([0, 1.6, 0]) + G[:n][~inside]*.25
    Bv[:n] = np.where(inside, .55, .12)
    edge = (np.abs(CUBE_G) > .6).sum(1) >= 2
    Bv[:n] = np.where(inside & edge, 1.3, Bv[:n])
    return P, Bv, n

def sh_migrate(t, lt):
    """Data lands in the governed Preservation Zone: a lattice vault filling bottom-up."""
    fill = ease((lt - .6)/4.5)
    P, Bv, n = vault(fill)
    # falling stream above the vault
    fs = slice(n, n+700)
    ph = (U[fs, 2] + lt*.6) % 1
    P[fs] = np.stack([G[fs, 0]*.25, 1.9 - ph*(1.9-(-.6+1.24*fill)), G[fs, 2]*.25], 1)
    Bv[fs] = .7*(fill < .99) + .1
    sweep = ((lt*.7) % 1.6) - .8
    Bv[:n] += .9*np.exp(-((CUBE_G[:, 0]-sweep)/.12)**2)*(lt > 5)
    return P, Bv

SHELL = fib(N, 1.0)*np.array([1.75, 1.15, 1.75])
def sh_dark(t, lt):
    """The source application powers down and falls away; the vault stays lit."""
    P, Bv, n = vault(1.0)
    rest = np.arange(N) >= n
    td = word_time("dark", "go dark") - SC["dark"] + .3
    k = ease((lt - td)/1.2)
    fall = clamp(lt - td - .6, 0, 10)
    S = SHELL.copy()
    ang = t*.15; c, s = math.cos(ang), math.sin(ang)
    S = np.stack([S[:, 0]*c - S[:, 2]*s, S[:, 1], S[:, 0]*s + S[:, 2]*c], 1)
    S[:, 1] -= (fall**2)*.35*(.4+U[:, 3])
    S[:, 0] += G[:, 0]*fall*.08; S[:, 2] += G[:, 2]*fall*.08
    P[rest] = S[rest]
    Bv[rest] = (.75*(1-k) + .06)*(1 + .8*(np.sin(t*30+U[rest, 4]*50) > .7)*(lt > td-.2)*(k < .6))
    Bv[:n] *= 1 + .25*k
    return P, Bv

DOCS = ["Invoice", "Purchase order", "Receipt", "Payment"]
DOC_A = np.array([[-1.25, .45, .1], [.9, 1.05, -.2], [1.25, -.45, .35], [-.3, -1.05, -.3]])
LINKS = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
def graph(nodes, links, lit, t, lt, flow=.25):
    m = U[:, 0]; P = DUST.copy()*.9; Bv = np.full(N, .08)
    nn = len(nodes); nid = (U[:, 1]*nn).astype(int)
    isn = m < .35
    P = np.where(isn[:, None], nodes[nid] + SPH_P*.17, P)
    Bv = np.where(isn, .35 + 1.0*lit[nid], Bv)
    il = (m >= .35) & (m < .85)
    lid = (U[:, 2]*len(links)).astype(int); la = np.array([links[i][0] for i in range(len(links))])[lid]
    lb = np.array([links[i][1] for i in range(len(links))])[lid]
    u = U[:, 3]
    seg = nodes[la]*(1-u)[:, None] + nodes[lb]*u[:, None] + G*.012
    llit = np.minimum(lit[la], lit[lb])
    pulse = np.exp(-(((u - (lt*flow + U[:, 4]*0)) % 1) - .5)**2/.004)
    P = np.where(il[:, None], seg, P)
    Bv = np.where(il, (.18 + .5*llit + .9*pulse*llit), Bv)
    return P, Bv

def sh_access(t, lt):
    tw = [word_time("access", w) - SC["access"] for w in ["Nothing", "Auditors", "Auditors", "Users"]]
    lit = np.array([ease((lt - tw[0] - .3)/.8), ease((lt-tw[1])/.8), ease((lt-tw[1]-.4)/.8), ease((lt-tw[3])/.8)])
    P, Bv = graph(DOC_A, LINKS, lit, t, lt)
    return P, Bv

KG = ["Supplier", "Invoice", "Payment"]
KG_A = np.array([[-.9, .6, .1], [.85, .55, -.3], [.1, -.75, .35], [-1.2, -.5, -.7], [1.35, -.3, .6], [.3, 1.2, .9]])
KG_L = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 4), (2, 4), (1, 5)]
def sh_ask(t, lt):
    t0 = word_time("ask", "grounded") - SC["ask"] if "grounded" in LN["ask"]["caption"] else word_time("ask", "cited") - SC["ask"] - 1.6
    lit = np.array([ease((lt - t0 - k*.6)/.6) for k in range(3)] + [.12, .12, .12])
    return graph(KG_A, KG_L, lit, t, lt, flow=.4)

def sh_ai(t, lt):
    """Governed history feeds AI: the missing wedge of the sphere fills in."""
    P0, B0 = sh_ai_gap(t, t - SC["t5"])
    k = eout((lt - .5 - U[:, 5]*1.2)/1.0)
    src = np.array([0, -2.2, 0]) + G*.3
    tgt = SPH*1.0
    Pw = src*(1-k)[:, None] + tgt*k[:, None]
    P = np.where(AI_WEDGE[:, None], rot_y(Pw, 0.25 - cam_yaw(t) + .08*(t - SC["t5"])), P0)
    band = .55 + .45*(np.abs(np.sin(SPH[:, 1]*9)) > .8)
    Bv = np.where(AI_WEDGE, band*(.3+.9*k) + 1.2*k*(1-k)*4*0.25, B0)
    sw = np.exp(-((SPH[:, 1] - (((lt*.5) % 1.4) - .7)*1.6)/.08)**2)
    return P, Bv + .7*sw*(lt > 2)

def sh_sign(t, lt):
    """A slow halo around the Solix mark."""
    a = U[:, 0]*2*np.pi + t*.12
    r = 2.45 + .07*G[:, 0] + .25*(U[:, 1] > .8)*U[:, 2]
    P = np.stack([np.cos(a)*r, .05*G[:, 1], np.sin(a)*r], 1)
    P = np.where((U[:, 3] > .85)[:, None], DUST*1.1, P)
    Bv = np.where(U[:, 3] > .85, .12, .55 + .3*np.sin(a*3 + t))
    return P, Bv

SHAPES = dict(hook=sh_hook, t1=sh_cost, t2=sh_risk, t3=sh_mna, t4=sh_archive, t5=sh_ai_gap, one=sh_one,
              connect=sh_connect, migrate=sh_migrate, dark=sh_dark, access=sh_access, ask=sh_ask, ai=sh_ai, sign=sh_sign)
MORPH = dict(t1=.7, t2=.6, t3=.6, t4=.6, t5=.6, one=1.0, connect=1.4, migrate=1.4, dark=.8, access=1.4, ask=1.4, ai=1.0, sign=1.6)
DELAY = U[:, 5]*.35

def particles(t):
    sid = scene_at(t); k = ORDER.index(sid); lt = t - SC[sid]
    P, Bv = SHAPES[sid](t, lt)
    if k > 0:
        dur = MORPH.get(sid, 1.0)
        if lt < dur*1.4:
            prev = ORDER[k-1]
            P0, B0 = SHAPES[prev](t, t - SC[prev])
            u = ease((lt/dur - DELAY)/(1-.35))
            P = P0*(1-u)[:, None] + P*u[:, None] + (np.sin(np.pi*u)*.55)[:, None]*G
            Bv = B0*(1-u) + Bv*u
    return P, Bv

# ---------------------------------------------------------------- camera
CAMX = dict(hook=960, t1=1290, t2=1290, t3=1290, t4=1290, t5=1290, one=960, connect=1200,
            migrate=1260, dark=1260, access=1240, ask=1320, ai=1260, sign=960)
CAMY = dict(hook=470, one=600, sign=390)
CAMS = dict(hook=1.0, one=1.0, connect=.9, migrate=1.05, dark=.95, access=1.0, ask=.95, ai=1.0, sign=1.0)
def cam_yaw(t):
    return (.04*t - .15) if t < SC["t1"] else .1*t + .25*math.sin(.13*t)

def rot_y(P, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([P[:, 0]*c + P[:, 2]*s, P[:, 1], -P[:, 0]*s + P[:, 2]*c], 1)

def cam(t):
    sid = scene_at(t); k = ORDER.index(sid); lt = t - SC[sid]
    def v(d, s, dflt): return d.get(s, dflt)
    cx, cy, cs = v(CAMX, sid, 960), v(CAMY, sid, 560), v(CAMS, sid, 1.0)
    if k > 0:
        p = ORDER[k-1]; u = fl(einout(lt/1.3))
        cx = v(CAMX, p, 960)*(1-u) + cx*u; cy = v(CAMY, p, 560)*(1-u) + cy*u; cs = v(CAMS, p, 1.0)*(1-u) + cs*u
    yaw = cam_yaw(t)
    pitch = .2 + .06*math.sin(.17*t)
    push = 1 + .035*clamp(lt/6, 0, 1)
    return cx, cy, cs*push, yaw, pitch

FOC = 860; DIST = 4.4
def project(P, t):
    cx, cy, cs, yaw, pitch = cam(t)
    c, s = math.cos(yaw), math.sin(yaw)
    x = P[:, 0]*c + P[:, 2]*s; z = -P[:, 0]*s + P[:, 2]*c; y = P[:, 1]
    cp, sp = math.cos(pitch), math.sin(pitch)
    y2 = y*cp - z*sp; z2 = y*sp + z*cp
    zc = z2 + DIST
    f = FOC*cs/np.maximum(zc, .3)
    return cx + x*f, cy - y2*f, zc

# ---------------------------------------------------------------- background
YY, XX = np.mgrid[0:H//4, 0:W//4].astype(np.float32)*4
def background(t):
    cx, cy, *_ = cam(t)
    d = np.sqrt(((XX - cx)/1100)**2 + ((YY - cy)/850)**2)
    a = np.clip(1 - d, 0, 1)**1.6
    b1x, b1y = 500 + 260*math.sin(t*.09), 260 + 120*math.sin(t*.07+1)
    b1 = np.exp(-(((XX-b1x)/700)**2 + ((YY-b1y)/500)**2))
    b2 = np.exp(-(((XX-(1550+200*math.sin(t*.06)))/600)**2 + ((YY-880)/420)**2))
    base = np.array([34, 3, 8], np.float32)/255
    mid = np.array([118, 9, 20], np.float32)/255
    hi = np.array([206, 26, 38], np.float32)/255
    img = base + (mid-base)*np.clip(a*1.6, 0, 1)[..., None] + (hi-mid)*(a**2)[..., None]
    img += (np.array([230, 40, 48], np.float32)/255 - img)*(.22*b1 + .16*b2)[..., None]
    img = zoom(img, (4, 4, 1), order=1)
    return img

GRAIN = [(np.random.default_rng(i).standard_normal((H, W, 1)).astype(np.float32)*.012) for i in range(6)]
BOKEH = np.random.default_rng(5).random((45, 5))

def glow_layer(t, flash=0.0):
    P, Bv = particles(t)
    sx, sy, zc = project(P, t)
    hw, hh = W//2, H//2
    x = sx/2; y = sy/2
    ok = (x > 1) & (x < hw-2) & (y > 1) & (y < hh-2) & (zc > .5)
    depth = clamp(1.25 - (zc - DIST)*.18, .35, 1.6)
    w = Bv*depth*ok
    dof = clamp(np.abs(zc - DIST)/1.6, 0, 1)
    A = np.zeros(hh*hw, np.float32); Bb = np.zeros(hh*hw, np.float32)
    x0 = np.floor(x[ok]).astype(int); y0 = np.floor(y[ok]).astype(int)
    fx = (x[ok]-x0).astype(np.float32); fy = (y[ok]-y0).astype(np.float32)
    ws, wb = (w[ok]*(1-dof[ok])).astype(np.float32), (w[ok]*dof[ok]).astype(np.float32)
    for dx, dy, ww in ((0, 0, (1-fx)*(1-fy)), (1, 0, fx*(1-fy)), (0, 1, (1-fx)*fy), (1, 1, fx*fy)):
        idx = (y0+dy)*hw + x0+dx
        A += np.bincount(idx, ws*ww, hh*hw).astype(np.float32)
        Bb += np.bincount(idx, wb*ww, hh*hw).astype(np.float32)
    A = A.reshape(hh, hw); Bb = Bb.reshape(hh, hw)
    I = gaussian_filter(A, .6)*1.9 + gaussian_filter(Bb, 2.2)*2.4
    q = zoom(A + Bb, .5, order=1)
    bloom = zoom(gaussian_filter(q, 7), 2, order=1)[:hh, :hw]*3.2
    bloom2 = zoom(gaussian_filter(q, 30), 2, order=1)[:hh, :hw]*(4.5+12*flash)
    # depth bokeh (far, soft)
    bk = np.zeros((hh//2, hw//2), np.float32)
    for bx, by, bz, bs, bp in BOKEH:
        px = ((bx*1.3 - .15 + t*.004*(1+bz)) % 1.3 - .15)*hw/2; py = ((by + .01*math.sin(t*.2+bp*6)))*hh/2
        if 0 <= px < hw/2-1 and 0 <= py < hh/2-1:
            bk[int(py), int(px)] += (.6 + bs)*(.6+.4*math.sin(t*.5+bp*9))
    bk = zoom(gaussian_filter(bk, 5), 2, order=1)[:hh, :hw]*26
    tot = I + bloom + bloom2 + bk
    return zoom(tot, 2, order=1)

WARM = np.array([1.0, .88, .84], np.float32)
def compose_bg(t, flash=0.0):
    bg = background(t)
    g = glow_layer(t, flash)[..., None]
    out = bg + (1 - bg)*(1 - np.exp(-g*.9))*WARM
    vy, vx = np.ogrid[0:H, 0:W]
    return out

VIG = None
def vignette():
    global VIG
    if VIG is None:
        vy, vx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((vx-W/2)/(W*.62))**2 + ((vy-H/2)/(H*.62))**2)
        VIG = (1 - .45*np.clip(d-.55, 0, 1)**1.5)[..., None]
    return VIG

# ---------------------------------------------------------------- typography
@lru_cache(None)
def font(name, size): return ImageFont.truetype(FD + name, size)

@lru_cache(None)
def word_img(text, fname, size, rgb=(255, 255, 255), track=0, shadow=True):
    f = font(fname, size)
    if track:
        widths = [f.getlength(ch) for ch in text]; tw = int(sum(widths) + track*(len(text)-1))
    else:
        tw = int(f.getlength(text))
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
    sh = np.asarray(im.filter(ImageFilter.GaussianBlur(size*.12)), np.float32)/255*.55 if shadow else a*0
    return a, sh, pad, tw, asc

@lru_cache(None)
def blurred(text, fname, size, rgb, track, level):
    a, sh, pad, tw, asc = word_img(text, fname, size, rgb, track)
    if level == 0: return a
    im = Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(level))
    return np.asarray(im, np.float32)/255

SHADOW = np.array([.16, 0, .02], np.float32)
def put(frame, text, fname, size, x, y, alpha=1.0, blur=0.0, rgb=(255, 255, 255), track=0, anchor="ls"):
    """Composite a text run with baseline at (x, y). anchor 'ls' left-baseline, 'ms' middle-baseline."""
    if alpha <= .003: return
    a, sh, pad, tw, asc = word_img(text, fname, size, rgb, track)
    lv = int(round(min(blur, 12)/2)*2)
    if lv: a = blurred(text, fname, size, rgb, track, lv)
    if anchor == "ms": x -= tw/2
    x0 = int(round(x - pad)); y0 = int(round(y - asc - pad))
    h, w = a.shape
    fx0, fy0 = max(0, x0), max(0, y0); fx1, fy1 = min(W, x0+w), min(H, y0+h)
    if fx1 <= fx0 or fy1 <= fy0: return
    aa = a[fy0-y0:fy1-y0, fx0-x0:fx1-x0, None]*alpha
    ss = sh[fy0-y0:fy1-y0, fx0-x0:fx1-x0, None]*alpha
    reg = frame[fy0:fy1, fx0:fx1]
    reg[:] = reg*(1-ss) + SHADOW*ss
    col = np.array(rgb, np.float32)/255
    reg[:] = reg*(1-aa) + col*aa

def measure(text, fname, size, track=0):
    f = font(fname, size)
    if track: return sum(f.getlength(c) for c in text) + track*(len(text)-1)
    return f.getlength(text)

def wrap(text, fname, size, maxw):
    words = text.split(" "); lines = [[]]
    for wd in words:
        cand = " ".join(lines[-1] + [wd])
        if lines[-1] and measure(cand, fname, size) > maxw: lines.append([wd])
        else: lines[-1].append(wd)
    return lines

def kinetic(frame, t, text, x, y, size, t_in, t_out, fname="InterDisplay-Bold.otf", maxw=900,
            align="left", lh=1.08, stagger=.07, rise=34, rgb=(255, 255, 255), dur=.65):
    """Word-by-word reveal: each word rises, sharpens and fades in; exits drifting up and softening."""
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
                put(frame, wd, fname, size, xx, yy + (1-p)*rise - q*18, a, blur=(1-p)*10 + q*8, rgb=rgb)
            xx += measure(wd, fname, size) + sp; k += 1

def fade_text(frame, t, text, x, y, size, t_in, t_out, fname="Inter-Medium.otf", anchor="ls", alpha=1.0, track=0, rgb=(255, 255, 255), dur=.45):
    a = fl(ease((t - t_in)/dur))*(1 - fl(ease((t - t_out)/.4)))*alpha
    if a > .003: put(frame, text, fname, size, x, y + (1-fl(eout((t-t_in)/dur)))*12, a, rgb=rgb, track=track, anchor=anchor)

# ---------------------------------------------------------------- logo
def load_logo():
    im = Image.open(f"{ASSETS}/logo_white.png").convert("RGBA")
    a = np.asarray(im, np.float32)/255
    rgb, al = a[..., :3], a[..., 3:]
    red = (rgb[..., 0] > .6) & (rgb[..., 1] < .45) & (al[..., 0] > .1)
    wht = (rgb.min(-1) > .8) & (al[..., 0] > .1)
    disc = np.zeros(rgb.shape[:2], bool); disc[:, :400] = True
    out = rgb.copy()
    out[red & disc] = 1.0
    out[wht & disc] = np.array([238, 36, 36])/255
    return np.concatenate([out, al], -1)
LOGO = load_logo()
def logo_scaled(h):
    im = Image.fromarray((LOGO*255).astype(np.uint8), "RGBA")
    w = int(im.width*h/im.height)
    return np.asarray(im.resize((w, h), Image.LANCZOS), np.float32)/255
LOGO_SM = logo_scaled(46); LOGO_LG = logo_scaled(150)
def put_rgba(frame, img, x, y, alpha):
    if alpha <= .003: return
    h, w = img.shape[:2]; x, y = int(x), int(y)
    a = img[..., 3:]*alpha
    frame[y:y+h, x:x+w] = frame[y:y+h, x:x+w]*(1-a) + img[..., :3]*a

# ---------------------------------------------------------------- overlays per scene
LX = 150
def overlays(fr, t):
    sid = scene_at(t)
    E = lambda s: SC_END[s] - .45
    # small Solix mark, top right, everywhere except the end card
    put_rgba(fr, LOGO_SM, W - 90 - LOGO_SM.shape[1], 58, (1 - fl(ease((t - SC["sign"] + .2)/.6)))*fl(ease((t - .6)/1.0))*.95)

    # 1. Hook
    kinetic(fr, t, "Applications you've moved on from.", LX, 860, 80, 1.0, E("hook"), maxw=1500)

    # 2. Five triggers: one big word each
    for tid, word, sub in (("t1", "Cost", None), ("t2", "Risk", None), ("t3", "M&A", None), ("t4", "Old archive", None), ("t5", "AI", None)):
        a0 = LN[tid]["start"] - .1
        a1 = SC_END[tid] - .25
        if a0 - .1 <= t <= a1 + .6:
            p = fl(eout((t - a0)/.35)); q = fl(ease((t - a1)/.25))
            sc = 1.12 - .12*p
            al = p*(1-q)
            size = int(200*sc) if len(word) < 6 else int(150*sc)
            put(fr, word, "InterDisplay-Bold.otf", size, LX - (sc-1)*60, 560, al, blur=(1-p)*8 + q*10)
            n = ORDER.index(tid)
            put(fr, f"0{n}", "Inter-SemiBold.otf", 30, LX + 6, 330, al*.7, track=4)

    # 3. Converge
    kinetic(fr, t, "Many reasons.", W/2, 190, 84, LN["one"]["start"], LN["connect"]["start"] + .1, align="center", maxw=1600)
    kinetic(fr, t, "One engine.", W/2, 290, 84, word_time("one", "One engine"), LN["connect"]["start"] + .1, align="center", maxw=1600)

    # Act 2-3 step tracker (text only): Connect > Migrate & Validate > Enable AI
    t_on, t_off = SC["connect"] + .2, SC["sign"] - .2
    if t_on - .1 < t <= t_off + .5:
        ga = fl(ease((t - t_on)/.6))*(1 - fl(ease((t - t_off)/.5)))
        steps = [("CONNECT", ("connect",)), ("MIGRATE & VALIDATE", ("migrate", "dark")), ("ENABLE AI", ("ai",))]
        x = LX
        done = {"connect": 0, "migrate": 1, "dark": 1, "access": 1, "ask": 1, "ai": 2}.get(sid, 0)
        for i, (lab, ss) in enumerate(steps):
            act = sid in ss
            al = 1.0 if act else (.62 if i < done else .34)
            put(fr, lab, "Inter-SemiBold.otf", 24, x, 100, ga*al, track=3)
            x += measure(lab, "Inter-SemiBold.otf", 24, 3) + 22
            if i < 2:
                put(fr, "›", "Inter-SemiBold.otf", 24, x, 100, ga*.4); x += 36

    # 4. Connect
    s = "connect"
    kinetic(fr, t, "Every source.", LX, 300, 84, SC[s] + 1.2, E(s), maxw=800)
    kinetic(fr, t, "One engine.", LX, 392, 84, SC[s] + 1.6, E(s), maxw=800)
    if SC[s] - .2 <= t <= SC_END[s] + .6:
        sx, sy, zc = project(SRC_A*1.0, t)
        for k, (lab, wd) in enumerate(zip(SRC, ["ERP", "mainframe", "custom", "SaaS", "files", "email"])):
            ti = word_time(s, wd)
            sz = int(np.clip(30 + (DIST - zc[k])*7, 24, 40))
            fade_text(fr, t, lab, sx[k], sy[k] - 34, sz, ti, E(s), fname="InterDisplay-SemiBold.otf", anchor="ms",
                      alpha=fl(clamp(1.35 - (zc[k]-DIST)*.35, .45, 1)))

    # 5. Migrate & Validate
    s = "migrate"
    kinetic(fr, t, "Governed from the day it lands.", LX, 300, 78, SC[s] + .3, E(s), maxw=760)
    checks = ["Validated against source", "Quality checked", "Retention applied", "Legal hold ready"]
    tc = [word_time(s, "checked") - .2, word_time(s, "checked") + .5, word_time(s, "retention"), word_time(s, "legal hold")]
    for k, (c, ti) in enumerate(zip(checks, tc)):
        fade_text(fr, t, "✓", LX, 560 + k*62, 38, ti, E(s), fname="InterDisplay-Bold.otf")
        fade_text(fr, t, c, LX + 54, 560 + k*62, 38, ti + .08, E(s), fname="InterDisplay-Medium.otf")

    # 6. Switch off
    s = "dark"
    kinetic(fr, t, "Then the application goes dark.", LX, 300, 78, SC[s] + .3, E(s), maxw=760)
    kinetic(fr, t, "For good.", LX, 480, 78, word_time(s, "gone for good"), E(s), maxw=760)
    for k, (lab, wd) in enumerate((("Licenses", "licenses"), ("Servers", "servers"), ("Unpatched risk", "risk"))):
        ti = word_time(s, wd) - .1
        # tag appears on the shell, then falls away
        fall = max(0.0, t - ti - .9)
        x = 1260 + (-330, 260, -40)[k]; y = (420, 470, 760)[k] + 240*fall**2
        a = fl(eout((t - ti)/.35))*(1 - fl(ease((t - ti - .9)/1.0)))
        put(fr, lab, "InterDisplay-SemiBold.otf", 40, x, y, a, blur=fl(clamp(fall*8, 0, 10)), anchor="ms")
    fade_text(fr, t, "Preservation Zone  ·  still on", 1260, 900, 30, word_time(s, "gone for good") - .2, E(s),
              fname="Inter-SemiBold.otf", anchor="ms", alpha=.9, track=2)

    # 7. Access
    s = "access"
    kinetic(fr, t, "Provable records.", LX, 300, 84, word_time(s, "Auditors") - .2, E(s), maxw=800)
    kinetic(fr, t, "Familiar reports.", LX, 396, 84, word_time(s, "Users") - .2, E(s), maxw=800)
    fade_text(fr, t, "Nothing it held is lost.", LX, 300 - 120, 34, SC[s] + .4, E(s), fname="Inter-Medium.otf", alpha=.8)
    if SC[s] - .2 <= t <= SC_END[s] + .6:
        sx, sy, zc = project(DOC_A, t)
        tw = [word_time(s, "Nothing") + .3, word_time(s, "Auditors"), word_time(s, "Auditors") + .4, word_time(s, "Users")]
        for k, lab in enumerate(DOCS):
            fade_text(fr, t, lab, sx[k], sy[k] - 52, 34, tw[k], E(s), fname="InterDisplay-SemiBold.otf", anchor="ms")

    # 8. Data Ask
    s = "ask"
    kinetic(fr, t, "Ask in plain English.", LX, 300, 78, SC[s] + .3, E(s), maxw=860)
    kinetic(fr, t, "Get cited answers.", LX, 390, 78, word_time(s, "cited"), E(s), maxw=860)
    q = "“Which suppliers were paid late in 2021?”"
    tq = word_time(s, "ask in plain")
    if tq <= t <= SC_END[s] + .6:
        n = int(clamp((t - tq)/1.9)*len(q))
        a = 1 - fl(ease((t - E(s))/.4))
        if n: put(fr, q[:n], "Inter-Italic.otf", 36, LX, 540, a*.95)
        if n < len(q) and int(t*2.5) % 2 == 0:
            put(fr, "|", "Inter-Medium.otf", 36, LX + measure(q[:n], "Inter-Italic.otf", 36) + 4, 540, a*.8)
    ta = word_time(s, "cited") + .4
    fade_text(fr, t, "3 suppliers  ·  answered with sources [1] [2] [3]", LX, 610, 32, ta, E(s), fname="Inter-SemiBold.otf", alpha=.92)
    if SC[s] - .2 <= t <= SC_END[s] + .6:
        sx, sy, zc = project(KG_A, t)
        t0 = word_time(s, "Knowledge Graph") - .6
        for k, lab in enumerate(KG):
            fade_text(fr, t, lab, sx[k], sy[k] - 50, 34, t0 + k*.6, E(s), fname="InterDisplay-SemiBold.otf", anchor="ms")
        fade_text(fr, t, "APPLICATION KNOWLEDGE GRAPH", 1320, 960, 24, t0, E(s), fname="Inter-SemiBold.otf", anchor="ms", alpha=.7, track=5)

    # 9. Enable AI
    s = "ai"
    kinetic(fr, t, "Enable AI", LX, 470, 120, SC[s] + .35, E(s), maxw=900)
    fade_text(fr, t, "Governed history, ready for your AI.", LX + 4, 560, 38, SC[s] + .9, E(s), fname="InterDisplay-Medium.otf", alpha=.9)

    # 10. Sign-off
    s = "sign"
    if t >= SC[s] - .1:
        lt = t - SC[s]
        p = fl(eout((lt - .3)/1.2))
        lw = LOGO_LG.shape[1]
        put_rgba(fr, LOGO_LG, W/2 - lw/2 + 12, 300 + (1-p)*30, p)
        kinetic(fr, t, "Retire the application.", W/2, 640, 72, word_time(s, "Retire"), T + 5, align="center", maxw=1700, fname="InterDisplay-Bold.otf")
        kinetic(fr, t, "Keep every answer.", W/2, 730, 72, word_time(s, "Keep every") + .1, T + 5, align="center", maxw=1700)
        fade_text(fr, t, "SOLIXCloud Application Retirement", W/2, 820, 34, word_time(s, "Keep every") + .9, T + 5,
                  fname="Inter-Medium.otf", anchor="ms", alpha=.85)
        fade_text(fr, t, "Data Ask is part of Solix Enterprise AI.  Visuals are illustrative.", W/2, 1030, 20,
                  word_time(s, "Keep every") + 1.4, T + 5, fname="Inter-Regular.otf", anchor="ms", alpha=.55)

def captions(fr, t):
    """VO subtitles: plain text with a soft shadow, no box."""
    for k, L in enumerate(TL["lines"]):
        if L["id"] in ("t1", "t2", "t3", "t4", "t5", "sign"): pass
        t0, t1 = L["start"] - .1, L["end"] + .3
        if not (t0 - .1 <= t <= t1 + .3): continue
        a = fl(ease((t - t0)/.2))*(1 - fl(ease((t - t1)/.25)))*.92
        if a <= .003: continue
        cap = L["caption"] if L["id"] != "sign" else "Solix Application Retirement. Retire the application. Keep every answer."
        if L["id"] == "sign": continue
        lines = wrap(cap, "Inter-Medium.otf", 32, 1400)
        y = 1000 - (len(lines)-1)*42
        for i, ln in enumerate(lines):
            put(fr, " ".join(ln), "Inter-Medium.otf", 32, W/2, y + i*42, a, anchor="ms")

def frame(t):
    flash = 0.0
    to = word_time("one", "One engine")
    if t > to: flash = 2.5*math.exp(-(t - to)*2.2)
    fr = compose_bg(t, flash).astype(np.float32)
    fr *= vignette()
    overlays(fr, t)
    captions(fr, t)
    # fade in/out
    fi = fl(ease(t/.8)); fo = 1 - fl(ease((t - (T - .9))/.9))
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
