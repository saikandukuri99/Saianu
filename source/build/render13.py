# Solix Empower 2026 AV - v12 renderer.
# Re-skins the v11 motion-graphics engine with a crafted, filmic look:
# no spheres / bokeh, flat frosted icons, soft light-leak backdrop, film grain, colour grade,
# slow camera push, zoom-flare transitions and a floating, glowing product-window treatment.
import math, os, sys, random, subprocess
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import render12 as R

W, H, FPS = R.W, R.H, R.FPS
RED, BLUE, KICK, INDIGO = R.RED, R.BLUE, R.KICK, R.INDIGO
ease, eio, back, vis, put, put_scaled = R.ease, R.eio, R.back, R.vis, R.put, R.put_scaled
SC, TOTAL = R.SC, R.TOTAL
R.A1  # noqa

# ------------------------------------------------------------------ backdrop
NAVY = (7, 9, 32)


@lru_cache(None)
def backdrop():
    BW, BH = W + 360, H + 240
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    u, v = xx / BW, yy / BH
    base = np.zeros((BH, BW, 3), np.float32)
    top, bot = np.array([26, 22, 88], np.float32), np.array(NAVY, np.float32)
    k = np.clip(v * 0.9 + (1 - u) * 0.15, 0, 1)[..., None]
    base[:] = top * (1 - k) + bot * k

    def blob(cx, cy, rx, ry, col, amt):
        g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))[..., None]
        return g * np.array(col, np.float32) * amt

    base += blob(BW * 0.88, BH * 0.02, 620, 420, (0, 126, 210), 0.78)      # cool key light, top right
    base += blob(BW * 0.05, BH * 0.98, 560, 320, (214, 30, 44), 0.55)      # warm kicker, bottom left
    base += blob(BW * 0.48, BH * 0.55, 700, 380, (70, 56, 170), 0.35)      # soft fill
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


@lru_cache(None)
def streak(w, h, ang):
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    d.polygon([(w * 0.35, 0), (w * 0.65, 0), (w * 0.35 + h * ang, h), (w * 0.05 + h * ang, h)], fill=255)
    return im.filter(ImageFilter.GaussianBlur(70))


def bg_frame(t):
    bg = backdrop()
    ox = 180 + 140 * math.sin(t / 14.0)
    oy = 120 + 90 * math.cos(t / 17.0)
    c = bg.crop((int(ox), int(oy), int(ox) + W, int(oy) + H)).copy()
    # slow volumetric light sweep (very subtle)
    s = streak(W, H, 0.55)
    ph = (t * 0.035) % 1.0
    sx = int(-W * 0.6 + ph * W * 1.9)
    layer = Image.new("RGB", (W, H), (120, 170, 255))
    m = Image.new("L", (W, H), 0)
    m.paste(s.point(lambda p: int(p * 0.16)), (sx, 0))
    c.paste(layer, (0, 0), m)
    return c


# ------------------------------------------------------------------ flat frosted icons / hub
@lru_cache(None)
def node(kind, size, active=True):
    pad = 40
    S_ = size + pad * 2
    ss = 3
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    gl = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    gcol = RED if active else (90, 150, 255)
    ImageDraw.Draw(gl).ellipse((pad - 6, pad - 6, pad + size + 6, pad + size + 6), fill=gcol + ((95 if active else 40),))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18)))
    D = size * ss
    disc = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    if active:
        dd.ellipse((0, 0, D - 1, D - 1), fill=RED + (255,))
        dd.ellipse((D * 0.03, D * 0.03, D * 0.97, D * 0.97), outline=(255, 255, 255, 70), width=ss * 2)
    else:
        dd.ellipse((0, 0, D - 1, D - 1), fill=(255, 255, 255, 26), outline=(255, 255, 255, 120), width=ss * 2)
    im.alpha_composite(disc.resize((size, size), Image.LANCZOS), (pad, pad))
    ic = R.icon(kind, int(size * 0.5), (255, 255, 255) if active else (205, 215, 245))
    im.alpha_composite(ic, (pad + (size - ic.width) // 2, pad + (size - ic.height) // 2))
    return im


@lru_cache(None)
def disc_img(d):
    pad = 40
    im = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    ss = 3
    D = d * ss
    disc = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse((0, 0, D - 1, D - 1), fill=(255, 255, 255, 14), outline=(255, 255, 255, 70), width=ss * 2)
    im.alpha_composite(disc.resize((d, d), Image.LANCZOS), (pad, pad))
    return im


@lru_cache(None)
def bolt_sphere(d):
    """flat Solix bolt with a soft red bloom (replaces the glossy sphere)"""
    pad = 70
    im = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    gl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((pad - 10, pad - 10, pad + d + 10, pad + d + 10), fill=RED + (120,))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(34)))
    im.alpha_composite(R.bolt(d), (pad, pad))
    return im


# ------------------------------------------------------------------ product windows: soft glow, depth, gentle float
@lru_cache(None)
def card_glow(w, h):
    pad = 90
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad + 10, pad + w, pad + h + 10), 24, fill=(40, 120, 255, 90))
    return im.filter(ImageFilter.GaussianBlur(46)), pad


@lru_cache(None)
def card_edge(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), 14, outline=(255, 255, 255, 90), width=1)
    return im


_T = [0.0]


def draw_card(c, im, x, y, a=1.0):
    if a <= 0.004:
        return
    big = im.width > 420 and im.height > 220
    fy = 5 * math.sin(_T[0] * 0.55 + x * 0.003) if big else 0
    if big:
        g, gp = card_glow(im.width, im.height)
        put(c, g, x - gp, y + fy - gp, a * 0.55)
    sh, pad = R.shadow(im.width, im.height, 18, 34, 70, 22)
    put(c, sh, x - pad, y + fy - pad, a)
    put(c, im, x, y + fy, a)
    if big:
        put(c, card_edge(im.width, im.height), x, y + fy, a)


# ------------------------------------------------------------------ transitions
def zoom(c, s):
    if s <= 1.0005:
        return c
    w, h = int(W / s), int(H / s)
    x0, y0 = (W - w) // 2, (H - h) // 2
    return c.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)


@lru_cache(None)
def flare_line():
    im = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((W * 0.08, 70, W * 0.92, 90), fill=(190, 225, 255, 255))
    im = im.filter(ImageFilter.GaussianBlur(14))
    return im


TR = 0.5


def transition(c, t):
    for k in range(1, 8):
        b = SC[k]["start"]
        if abs(t - b) < TR:
            p = 1 - abs(t - b) / TR
            p = eio(p)
            c = zoom(c, 1 + 0.16 * p)
            c = c.filter(ImageFilter.GaussianBlur(11 * p))
            fl = Image.new("RGB", (W, H), (150, 205, 255))
            c = Image.blend(c, fl, 0.38 * p ** 1.6)
            c = c.convert("RGBA")
            put(c, flare_line(), 0, H / 2 - 80, p ** 1.4)
            return c.convert("RGB")
    return c


# ------------------------------------------------------------------ finishing: grade, bloom, vignette, grain
_rng = np.random.default_rng(7)
GR = [(_rng.normal(0, 1, (H, W)).astype(np.float32)) for _ in range(6)]
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.30 * np.clip(np.hypot((xx_ - W / 2) / (W * 0.62), (yy_ - H / 2) / (H * 0.66)) - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)


def finish(c, fi):
    a = np.asarray(c, np.float32) / 255.0
    # bloom
    small = c.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    b = np.asarray(small, np.float32) / 255.0
    a = 1 - (1 - a) * (1 - np.clip(b - 0.42, 0, 1) * 0.55)
    # gentle S-curve + cool shadows / warm highlights
    a = a * a * (3 - 2 * a) * 0.35 + a * 0.65
    a[..., 0] += 0.012 * a[..., 0]
    a[..., 2] += 0.014 * (1 - a[..., 2])
    a *= VIG
    n = GR[fi % 6] * 0.018 + np.roll(GR[(fi + 3) % 6], 97, axis=1) * 0.01
    a = a + n[..., None] * (0.55 + 0.9 * (1 - a))
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def chrome(c, t, show_logo=1.0):
    R.put(c, R.text("SOLIX EMPOWER 2026", "bold", 15, R.TXT2, 4), 92, 46, vis(t, 0.6, None, 0.8))
    if show_logo > 0:
        R.put(c, R.logo(210), W - 92 - 210, 34, show_logo)
    ImageDraw.Draw(c).rectangle((0, H - 4, int(W * t / TOTAL), H), fill=RED)


def frame(t):
    _T[0] = t
    c = bg_frame(t)
    cur = 0
    for k, s in enumerate(SC):
        if s["start"] <= t < s["end"]:
            R.SCENES[k](c, t, t - s["start"], 1.0)
            cur = k
    # slow camera push, restarting every scene
    s0, s1 = SC[cur]["start"], SC[cur]["end"]
    c = zoom(c, 1.0 + 0.035 * ((t - s0) / max(1.0, s1 - s0)))
    s7 = SC[7]
    lt7 = t - s7["start"]
    show = 1.0
    if t < R.cue(1) - 0.3:
        show = 0.0
    elif t >= s7["start"] and lt7 >= R.lc(7, 32, lead=0.3):
        show = 0.0
    elif t < R.cue(1) + 0.4:
        show = ease((t - R.cue(1) + 0.3) / 0.7)
    chrome(c, t, show)
    R.caption(c, t)
    c = transition(c, t)
    c = finish(c, int(round(t * FPS)))
    if t < 0.5:
        c = Image.blend(Image.new("RGB", (W, H), NAVY), c, t / 0.5)
    if t > TOTAL - 1.0:
        c = Image.blend(c, Image.new("RGB", (W, H), NAVY), min(1, (t - (TOTAL - 1.0)) / 1.0))
    return c


# ------------------------------------------------------------------ patch the v11 engine
for nm, fn in (("node", node), ("disc_img", disc_img), ("bolt_sphere", bolt_sphere), ("draw_card", draw_card), ("bg_frame", bg_frame), ("chrome", chrome)):
    setattr(R, nm, fn)
R.SEG_TOP, R.SEG_SIDE, R.SEG_SIDE2 = (244, 246, 253), (0, 126, 200), (22, 78, 150)
R.BGC = (20, 18, 70)


# ------------------------------------------------------------------ cold open (replaces the scattered network graphic)
import inspect, re as _re
_src = inspect.getsource(R.scene0)
_src = _src.replace("aA = vis(lt, 0.0, tA_out, 0.6, 0.6) * G", "aA = 0").replace("def scene0(", "def scene0_orig(")
exec(_src, R.__dict__)


@lru_cache(None)
def logo_sweep_mask(w, h):
    m = Image.new("L", (w * 2, h), 0)
    ImageDraw.Draw(m).polygon([(w * 0.7, 0), (w * 1.05, 0), (w * 0.85, h), (w * 0.5, h)], fill=255)
    return m.filter(ImageFilter.GaussianBlur(26))


def scene0(c, t, lt, G):
    cx, cy = W / 2, 450
    l0 = R.cue(0)
    tA_out = R.cue(1) - 0.6
    aA = vis(lt, 0.0, tA_out, 0.5, 0.6) * G
    if aA > 0:
        # a single light line opens like a camera slit, then the logo is revealed inside it
        p = eio(lt / 1.1)
        ln = int(1500 * p)
        d = ImageDraw.Draw(c)
        slit = Image.new("RGBA", (W, 80), (0, 0, 0, 0))
        ImageDraw.Draw(slit).rounded_rectangle((W / 2 - ln / 2, 36, W / 2 + ln / 2, 42), 3, fill=(200, 230, 255, int(255 * (1 - 0.8 * ease((lt - 1.2) / 0.8)))))
        slit = slit.filter(ImageFilter.GaussianBlur(3))
        put(c, slit, 0, cy - 40, aA)
        lw = 900
        lg = R.logo(lw)
        rv = eio((lt - 1.0) / 1.2)
        if rv > 0:
            vh = max(2, int(lg.height * rv))
            top = lg.crop((0, (lg.height - vh) // 2, lg.width, (lg.height - vh) // 2 + vh))
            sc_ = 0.93 + 0.07 * ease((lt - 1.0) / 2.0)
            top = top.resize((int(top.width * sc_), int(top.height * sc_)), Image.LANCZOS)
            put(c, top, cx - top.width / 2, cy - top.height / 2, vis(lt, 1.0, tA_out, 0.5, 0.5) * G)
            # light sweep across the mark
            sp = (lt - 2.0) / 1.2
            if 0 < sp < 1:
                m = logo_sweep_mask(lg.width, lg.height)
                off = int(-lg.width * 0.7 + sp * lg.width * 1.6)
                sweep = Image.new("RGBA", lg.size, (255, 255, 255, 0))
                al = Image.new("L", lg.size, 0)
                al.paste(m, (off, 0))
                al = Image.fromarray((np.minimum(np.asarray(al, np.float32), np.asarray(lg.getchannel("A"), np.float32)) * 0.9).astype(np.uint8))
                sweep.putalpha(al)
                put(c, sweep, cx - lg.width / 2, cy - lg.height / 2, aA)
        wk = R.text("SOLIX TECHNOLOGIES", "bold", 22, KICK, 6)
        R.put(c, wk, cx - wk.width / 2 + (1 - ease((lt - 2.6) / 0.8)) * 0, cy + 172 + (1 - ease((lt - 2.6) / 0.8)) * 16, vis(lt, 2.6, tA_out, 0.6, 0.5) * G)
        t1 = R.text("What AI needs most:", "xbold", 54, R.TXT)
        t2 = R.text("its own data.", "xbold", 54, (255, 255, 255))
        tw = t1.width + 18 + t2.width + 28
        x0 = cx - tw / 2
        yy = cy + 214
        ta = R.cue(0, "what AI") - 0.15
        R.put(c, t1, x0, yy + (1 - ease((lt - ta) / 0.6)) * 20, vis(lt, ta, tA_out, 0.6, 0.5) * G)
        tk = R.cue(0, "its own") - 0.2
        sp2 = eio((lt - tk) / 0.5)
        if sp2 > 0:
            pl = Image.new("RGBA", (t2.width + 28, t2.height + 4), (0, 0, 0, 0))
            ImageDraw.Draw(pl).rounded_rectangle((0, 0, int((t2.width + 28) * sp2), t2.height + 3), 12, fill=BLUE + (255,))
            R.put(c, pl, x0 + t1.width + 18, yy - 2, G * (1 - eio((lt - tA_out) / 0.5)))
        R.put(c, t2, x0 + t1.width + 32, yy, vis(lt, tk + 0.25, tA_out, 0.4, 0.5) * G)
    R.scene0_orig(c, t, lt, G)


R.SCENES[0] = scene0

# keep the (already zoomed) recovered recordings from being zoomed a second time
_orig_clip = R.screens.screen_clip


def _clip(frame_img, key, lt, w, h, zoom_to=1.06):
    return _orig_clip(frame_img, key, lt, w, h, 1.0 if key in ("logos", "analysts") else zoom_to)


R.screens.screen_clip = _clip


def render_range(args):
    f0, f1, out = args
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"{R.B}/s13_{ts}.jpg", quality=92)
    elif mode == "video":
        from multiprocessing import Pool
        nf = int(TOTAL * FPS)
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        nparts = nw * 4
        edges = [nf * q // nparts for q in range(nparts + 1)]
        jobs = [(edges[q], edges[q + 1], f"{R.B}/p13_{q:02d}.mp4") for q in range(nparts)]
        with Pool(nw) as pool:
            for o in pool.imap(render_range, jobs):
                print("done", o, flush=True)
        with open(f"{R.B}/parts13.txt", "w") as f:
            for j in jobs:
                f.write(f"file '{j[2]}'\n")
