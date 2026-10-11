import re
p = "render6.py"; s = open(p).read()


def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:80], s.count(a)); s = s.replace(a, b)


def replace_func(name, new, deco=True):
    """replace a top-level function (with optional @lru_cache line) by new source"""
    global s
    key = f"\ndef {name}("
    i = s.index(key)
    start = i + 1
    if deco and s[:i].endswith("@lru_cache(None)"):
        start = i - len("@lru_cache(None)") + 0
    j = s.index("\n\n\n", i)
    s = s[:start] + new.strip("\n") + s[j:]


R("import screens\n", "import screens6 as screens\nimport human3d\n")

# ---------- 3D-shaded nodes and hub disc
replace_func("node", '''@lru_cache(None)
def node(kind, size, active=True):
    """glossy 3D sphere-like disc with icon"""
    pad = 34
    S_ = size + pad * 2
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad + 4, pad + 14, pad + size - 4, pad + size + 14), fill=(0, 0, 10, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(sphere_img(size, active), (pad, pad))
    ic = icon(kind, int(size * 0.56))
    im.alpha_composite(ic, (pad + (size - ic.width) // 2, pad + (size - ic.height) // 2))
    return im


@lru_cache(None)
def sphere_img(d, rim=True):
    """white glossy disc: radial shading + specular highlight + red rim"""
    ss = 2
    D = d * ss
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    lx, ly = cx - D * 0.18, cy - D * 0.22
    l = np.hypot(xx - lx, yy - ly) / D
    shade = np.clip(1.0 - 0.32 * l ** 1.4 - 0.18 * np.clip(r - 0.72, 0, 1) * 3, 0.55, 1.0)
    rgb = np.stack([248 * shade, 248 * shade, 255 * shade], -1)
    spec = np.exp(-(((xx - (cx - D * 0.2)) / (D * 0.16)) ** 2 + ((yy - (cy - D * 0.26)) / (D * 0.09)) ** 2))
    rgb = np.clip(rgb + spec[..., None] * 40, 0, 255)
    a = np.clip((1 - r) * D * 0.5, 0, 1) * 255
    if rim:
        ring = np.clip(1 - np.abs(r - 0.955) / 0.035, 0, 1)
        rgb = rgb * (1 - ring[..., None]) + np.array(RED)[None, None] * ring[..., None]
    im = Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA")
    return im.resize((d, d), Image.LANCZOS)''')
replace_func("disc_img", '''@lru_cache(None)
def disc_img(d):
    pad = 40
    im = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad + 6, pad + 16, pad + d - 6, pad + d + 16), fill=(0, 0, 10, 160))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    im.alpha_composite(sphere_img(d, False), (pad, pad))
    return im''')
R("from PIL import Image, ImageDraw, ImageFont, ImageFilter\n", "from PIL import Image, ImageDraw, ImageFont, ImageFilter\nimport numpy as np\n")

# ---------- background: no grid / rings; depth bokeh + glossy orbs
replace_func("background", '''@lru_cache(None)
def background():
    BW, BH = W + 260, H + 180
    g = Image.linear_gradient("L").resize((BW, BH))
    deep = Image.new("RGB", (BW, BH), (12, 9, 40))
    ind = Image.new("RGB", (BW, BH), INDIGO)
    im = Image.composite(deep, ind, g.point(lambda v: int(255 * (v / 255) ** 0.8)))
    ov = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((BW - 1000, -520, BW + 420, 760), fill=BLUE + (150,))
    d.ellipse((-520, BH - 420, 560, BH + 520), fill=RED + (70,))
    d.ellipse((BW * 0.3, BH * 0.25, BW * 0.75, BH * 0.85), fill=(70, 56, 170, 60))
    ov = ov.filter(ImageFilter.GaussianBlur(170))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")''')
replace_func("particles", '''@lru_cache(None)
def bokeh(r, blur, col, alpha):
    pad = int(blur * 3) + 2
    im = Image.new("RGBA", (2 * (r + pad), 2 * (r + pad)), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((pad, pad, pad + 2 * r, pad + 2 * r), fill=col + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else im


@lru_cache(None)
def orb(d, tint):
    """glossy glass sphere sprite"""
    ss = 2
    D = d * ss
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    base = np.array(tint, float)
    shade = np.clip(0.35 + 0.65 * (1 - np.hypot(xx - cx + D * 0.15, yy - cy + D * 0.2) / D), 0.2, 1)
    rgb = base[None, None] * shade[..., None]
    rim = np.clip((r - 0.75) / 0.25, 0, 1) ** 2
    rgb = rgb + rim[..., None] * np.array([120, 190, 255]) * 0.7
    spec = np.exp(-(((xx - (cx - D * 0.22)) / (D * 0.12)) ** 2 + ((yy - (cy - D * 0.28)) / (D * 0.07)) ** 2))
    rgb = np.clip(rgb + spec[..., None] * 200, 0, 255)
    a = np.clip((1 - r) * D * 0.4, 0, 1) * (0.55 + 0.45 * rim + 0.6 * spec) * 255
    im = Image.fromarray(np.dstack([rgb, np.clip(a, 0, 255)]).astype(np.uint8), "RGBA").resize((d, d), Image.LANCZOS)
    return im.filter(ImageFilter.GaussianBlur(1.2))


rb = random.Random(21)
# (x, y, vx, vy, radius, blur, colour, alpha, parallax layer)
BOKEH = []
for layer, n, rads, blur, al in ((0, 26, (2, 5), 1.0, 150), (1, 14, (10, 22), 6, 70), (2, 6, (40, 80), 22, 40)):
    for _ in range(n):
        col = rb.choice([(110, 190, 255), (150, 210, 255), (255, 120, 120), (200, 190, 255)])
        BOKEH.append((rb.uniform(0, W), rb.uniform(0, H), rb.uniform(-10, 10) * (1 + layer), rb.uniform(-6, 6) * (1 + layer),
                      rb.randint(*rads), blur, col, al, layer))
ORBS = [(1660, 180, 150, (40, 70, 160), 0.0), (260, 880, 110, (120, 30, 60), 2.0), (1500, 930, 70, (30, 90, 170), 4.0)]


def particles(c, t, strength=1.0):
    for (x0, y0, vx, vy, r, blur, col, al, layer) in BOKEH:
        x = (x0 + vx * t + 25 * math.sin(t * 0.21 + y0)) % (W + 300) - 150
        y = (y0 + vy * t + 18 * math.cos(t * 0.17 + x0)) % (H + 300) - 150
        tw = 0.75 + 0.25 * math.sin(t * (0.8 + layer * 0.3) + x0)
        im = bokeh(r, blur, col, int(al * tw))
        put(c, im, x - im.width / 2, y - im.height / 2, strength)
    for (x0, y0, d, tint, ph) in ORBS:
        x = x0 + 30 * math.sin(t * 0.13 + ph)
        y = y0 + 22 * math.cos(t * 0.11 + ph)
        o = orb(d, tint)
        put(c, o, x - d / 2, y - d / 2, 0.85 * strength)''')

# ---------- callouts -> simple text, no boxes
replace_func("callout_img", '''@lru_cache(None)
def callout_img(num, title, sub, w, active=False, ico=None):
    t1 = fit_text(title, "bold", 30, w - 24, TXT)
    t2 = fit_text(sub, "med", 20, w - 24, TXT2) if sub else None
    h = t1.height + (t2.height + 2 if t2 else 0) + 6
    im = Image.new("RGBA", (w, max(h, 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 4, 4, h - 2), 2, fill=(RED if active else KICK) + (255,))
    im.alpha_composite(t1, (20, 0))
    if t2:
        im.alpha_composite(t2, (20, t1.height + 2))
    return im''')
replace_func("callout", '''def callout(c, x, y, num, title, sub, w, a, active=False, slide=40, ico=None):
    if a <= 0.004:
        return
    im = callout_img(num, title, sub, w, active, ico)
    # wipe-in reveal from the left + rise
    vw = max(1, int(im.width * min(1.0, a * 1.15)))
    put(c, im.crop((0, 0, vw, im.height)), x, y + (1 - a) * 14, a)''')
R('''def caption(c, t):''', '''def sub_text(s, size=30):
    return _sub_text(s, size)


@lru_cache(64)
def _sub_text(s, size):
    tx = fit_text(s, "semi", size, 1700, (255, 255, 255))
    pad = 16
    im = Image.new("RGBA", (tx.width + pad * 2, tx.height + pad * 2), (0, 0, 0, 0))
    shd = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shd.alpha_composite(tx, (pad, pad + 2))
    al = shd.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: min(255, int(v * 1.6)))
    black = Image.new("RGBA", im.size, (4, 2, 20, 0)); black.putalpha(al)
    im.alpha_composite(black)
    im.alpha_composite(tx, (pad, pad))
    return im


def caption(c, t):''')
# pill(): text only
replace_func("pill", '''def pill(c, s, a, y=962, size=27, cx=W / 2):
    im = sub_text(s, size + 2)
    put(c, im, cx - im.width / 2, y - 6, a)''')
s = s.replace("            pill(c, s, max(a, 0.0))\n", "            im = sub_text(s, 30)\n            put(c, im, (W - im.width) / 2, 966, max(a, 0.0))\n")

# ---------- firm tiles -> text
replace_func("firm_img", '''@lru_cache(None)
def firm_img(nm):
    tx = text(nm, "xbold", 44, TXT)
    im = Image.new("RGBA", (560, 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 14, 5, 66), 2, fill=RED + (255,))
    im.alpha_composite(tx, (24, int(40 - tx.height / 2)))
    return im''')
R('''        sh, pad = shadow(im.width, im.height, 12, 16, 40, 8)
        dx = (1 - a) * 40
        put(c, sh, 1250 - pad + dx, 410 + j * 108 - pad, a)
        put(c, im, 1250 + dx, 410 + j * 108, a)''', '''        dx = (1 - a) * 40
        put(c, im, 1250 + dx, 410 + j * 100, a)''')

# ---------- scroll pages (top -> bottom only)
R('''    if name == "ecs":''', '''    if os.path.exists(f"{S}/assets3/{name}_page.png"):
        im = Image.open(f"{S}/assets3/{name}_page.png").convert("RGB")
    elif name == "ecs":''')
R('''        if kind == "fn":
            return name(l)''', '''        if kind == "fn":
            return name(l)
        if kind == "scroll":
            k_ = items.index(it)
            dd = (items[k_ + 1][0] - t_on) if k_ + 1 < len(items) else 9.0
            _register(name)
            return screens.screen_scroll(name, l, maxw, maxh, dd)''')
R('''    items = [(0.7, "clip", "cdp", {"w": 1160, "h": 600, "top": True, "rate": 0.9}),
             (t2, "still", "ecs"),
             (t3, "clip", "edg", {"w": 1160, "h": 600, "top": True, "rate": 0.9})]''', '''    items = [(0.7, "scroll", "cdp"), (t2, "still", "ecs"), (t3, "scroll", "edg")]''')
R('''             (lc(k, 7, "Application Knowledge", lead=0.3), "clip", "akg", {"w": 1180, "h": 590, "top": True, "rate": 0.8}),''',
  '''             (lc(k, 7, "Application Knowledge", lead=0.3), "scroll", "akg"),''')
# scene1 chips -> one kinetic text line
R('''    x, y = 92, 640
    for j, (lab, tk) in enumerate(chips):
        im = pill_img(lab, True, 15, 18, 40, 2)
        if x + im.width > 92 + 560:
            x, y = 92, y + 54
        put(c, im, x, y + (1 - ease((lt - tk) / 0.4)) * 14, vis(lt, tk, None, 0.4) * G)
        x += im.width + 12''', '''    y = 650
    for j, (lab, tk) in enumerate(chips):
        im = text(lab, "bold", 18, KICK if j < 3 else (255, 120, 120), 3)
        put(c, im, 92 + (1 - ease((lt - tk) / 0.5)) * 24, y + j * 40, vis(lt, tk, None, 0.5) * G)''')

# ---------- Patient 360: 3D holographic body
replace_func("patient360", '''def patient360(c, cx, cy, l, t, a):
    if a <= 0.004:
        return
    srcs = [("EHR", "doc"), ("IMAGING", "chart"), ("BILLING", "dollar"), ("PHARMACY", "pill"), ("LAB", "flask")]
    holo = human3d.hologram(t, 470, a)
    hx, hy = cx - holo.width / 2, cy - holo.height / 2 - 10
    nodes = []
    for j, (lab, ic) in enumerate(srcs):
        ang = j * 2 * math.pi / len(srcs) + t * 0.35
        nx = cx + 300 * math.cos(ang)
        nz = math.sin(ang)
        ny = cy - 40 + 70 * nz
        nodes.append((nz, nx, ny, lab, ic, j))
    nodes.sort()
    back_ = [n for n in nodes if n[0] < 0]
    front = [n for n in nodes if n[0] >= 0]

    def draw_nodes(lst):
        for (nz, nx, ny, lab, ic, j) in lst:
            t0 = 0.3 + 0.15 * j
            aa = vis(l, t0) * a * (0.55 + 0.45 * (nz + 1) / 2)
            if aa <= 0:
                continue
            sz = int(70 + 22 * (nz + 1) / 2)
            if ic == "pill":
                nd = node("doc", sz).copy()
                pad = 34
                ImageDraw.Draw(nd).ellipse((pad + sz * 0.12, pad + sz * 0.12, pad + sz * 0.88, pad + sz * 0.88), fill=(250, 250, 255, 255))
                pi_ = pill_icon(int(sz * 0.6))
                nd.alpha_composite(pi_, (int(pad + sz * 0.2), int(pad + sz * 0.2)))
            else:
                nd = node(ic, sz)
            pts = [(nx + (cx - nx) * u / 20, ny + (cy - 60 - ny) * u / 20) for u in range(21)]
            connector(c, pts, ease((l - t0) / 0.8), aa * 0.8, t + j * 0.2, width=2)
            put_scaled(c, nd, nx, ny, max(0.05, back((l - t0) / 0.5)), aa)
            tl_ = text(lab, "bold", 15, TXT, 2)
            put(c, tl_, nx - tl_.width / 2, ny + sz / 2 + 10, aa)
    draw_nodes(back_)
    g = glow(150, 45)
    put(c, g, cx - g.width / 2, cy - g.height / 2, a)
    put(c, holo, hx, hy, 1.0)
    draw_nodes(front)
    tl_ = text("UNIFIED PATIENT RECORD", "black", 22, (255, 120, 120), 3)
    put(c, tl_, cx - tl_.width / 2, cy + holo.height / 2 + 6, a)''')
s = s.replace('f"{B}/s5_{ts}.jpg"', 'f"{B}/s6_{ts}.jpg"').replace('else "p5"', 'else "p6"').replace('tag = "u5" if UHD', 'tag = "u6" if UHD').replace("parts5{", "parts6{")
open(p, "w").write(s); print("ok")
