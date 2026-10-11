# --- EAI Pharma + EAI Healthcare section (v7): pure motion graphics -------------------------------

@lru_cache(None)
def atom_img(d, col):
    ss = 2
    D = max(4, d * ss)
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    lam = np.clip(1.05 - 0.75 * np.hypot(xx - (cx - D * 0.18), yy - (cy - D * 0.2)) / D * 1.6, 0.25, 1.0)
    rgb = np.array(col, float)[None, None] * lam[..., None]
    spec = np.exp(-(((xx - (cx - D * 0.2)) / (D * 0.13)) ** 2 + ((yy - (cy - D * 0.24)) / (D * 0.09)) ** 2))
    rgb = np.clip(rgb + spec[..., None] * 170, 0, 255)
    a = np.clip((1 - r) * D * 0.5, 0, 1) * 255
    return Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA").resize((max(2, d), max(2, d)), Image.LANCZOS)


@lru_cache(None)
def bolt_sphere(d):
    """Big glossy Solix bolt sphere with soft drop shadow."""
    pad = 60
    im = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad + 10, pad + 26, pad + d - 10, pad + d + 26), fill=(0, 0, 10, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    b = bolt(d).copy()
    D = d
    yy, xx = np.mgrid[0:D, 0:D].astype(float)
    cx = cy = (D - 1) / 2
    r = np.hypot(xx - cx, yy - cy) / (D / 2)
    shade = np.clip(1.0 - 0.38 * np.clip(r - 0.35, 0, 1) ** 1.5, 0, 1)
    arr = np.asarray(b).astype(float)
    arr[..., :3] *= shade[..., None]
    spec = np.exp(-(((xx - (cx - D * 0.2)) / (D * 0.2)) ** 2 + ((yy - (cy - D * 0.27)) / (D * 0.1)) ** 2))
    arr[..., :3] = np.clip(arr[..., :3] + spec[..., None] * 90, 0, 255)
    im.alpha_composite(Image.fromarray(arr.astype(np.uint8), "RGBA"), (pad, pad))
    return im


# simple drug-like molecule (fused 6/5 ring + side chains), unit coordinates
MOL_ATOMS = [
    ("C", (0.0, 1.0, 0.0)), ("C", (0.87, 0.5, 0.0)), ("C", (0.87, -0.5, 0.0)), ("C", (0.0, -1.0, 0.0)), ("C", (-0.87, -0.5, 0.0)), ("C", (-0.87, 0.5, 0.0)),
    ("N", (1.82, -0.86, 0.12)), ("C", (2.45, 0.05, 0.2)), ("C", (1.85, 0.95, 0.12)),
    ("O", (0.0, 2.15, -0.25)), ("C", (-1.95, -1.05, 0.45)), ("N", (-2.95, -0.45, 0.85)), ("O", (-2.05, -2.2, 0.2)),
    ("C", (3.7, 0.05, 0.55)), ("O", (4.35, 0.95, 0.8)), ("N", (4.25, -1.0, 0.7)),
    ("H", (0.0, -2.05, 0.1)), ("H", (-0.55, 2.7, -0.6)), ("H", (-3.7, -1.0, 1.1)), ("H", (2.4, 1.95, 0.0)),
]
MOL_BONDS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (2, 6), (6, 7), (7, 8), (8, 1), (0, 9), (4, 10), (10, 11), (10, 12),
             (7, 13), (13, 14), (13, 15), (3, 16), (9, 17), (11, 18), (8, 19)]
MOL_COL = {"C": (70, 150, 230), "N": (120, 110, 255), "O": (238, 60, 60), "H": (235, 238, 250)}
MOL_SIZE = {"C": 46, "N": 48, "O": 48, "H": 26}


def molecule(c, cx, cy, l, t, a, scale=115):
    if a <= 0.01:
        return []
    P = np.array([p for _, p in MOL_ATOMS], float)
    P = P - P.mean(axis=0)
    ay, ax = t * 0.45, 0.35 + 0.25 * math.sin(t * 0.3)
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Q = P @ Ry.T @ Rx.T
    persp = 1 / (1 + Q[:, 2] * 0.08)
    sx = cx + Q[:, 0] * scale * persp
    sy = cy - Q[:, 1] * scale * persp
    order = np.argsort(Q[:, 2])[::-1]  # far first (larger z = farther)
    d = ImageDraw.Draw(c)
    grow = [ease((l - 0.25 - 0.05 * i) / 0.5) for i in range(len(P))]
    for (i, j) in MOL_BONDS:
        g = min(grow[i], grow[j])
        if g <= 0:
            continue
        zc = (Q[i, 2] + Q[j, 2]) / 2
        k = (0.55 + 0.45 * (1 - (zc + 3) / 6)) * a * g
        x2 = sx[i] + (sx[j] - sx[i]) * g; y2 = sy[i] + (sy[j] - sy[i]) * g
        d.line((sx[i], sy[i], x2, y2), fill=mix(BGC, (170, 210, 255), k), width=max(2, int(7 * persp[i])))
    for i in order:
        g = grow[i]
        if g <= 0:
            continue
        el = MOL_ATOMS[i][0]
        sz = int(MOL_SIZE[el] * persp[i] * (0.4 + 0.6 * back(g)) * scale / 115)
        im = atom_img(max(4, sz // 2 * 2), MOL_COL[el])
        dz = 0.6 + 0.4 * (1 - (Q[i, 2] + 3) / 6)
        put(c, im, sx[i] - im.width / 2, sy[i] - im.height / 2, a * min(1, dz + 0.2))
    return list(zip(sx, sy))


def kin_word(c, s, x, y, size, col, a, lt0, l, w="black", track=0):
    """word rises in from a mask line"""
    im = text(s, w, size, col, track)
    p = ease((l - lt0) / 0.55)
    if p <= 0 or a <= 0:
        return im
    hh = im.height
    show = im.crop((0, 0, im.width, hh))
    put(c, show, x, y + (1 - p) * hh * 0.6, a * p)
    return im


def tag_pill(label, fill, size=40, padx=26, h=72):
    tx = text(label, "black", size, (255, 255, 255), 2)
    im = Image.new("RGBA", (tx.width + padx * 2, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, tx.width + padx * 2 - 1, h - 1), h // 2, fill=fill + (255,))
    im.alpha_composite(tx, (padx, int(h / 2 - tx.height / 2) + 1))
    return im


def phase_alpha(lt, t0, t1, din=0.5, dout=0.5):
    return ease((lt - t0) / din) * (1 - eio((lt - t1) / dout))


def pharma_phase(c, t, l, a):
    # title block (left)
    put(c, text("INDUSTRY SOLUTIONS", "bold", 20, KICK, 6), 120 - (1 - ease(l / 0.6)) * 30, 300, a * ease(l / 0.6))
    e = kin_word(c, "EAI", 112, 330, 128, RED, a, 0.15, l)
    kin_word(c, "PHARMA", 112 + e.width + 26, 330, 128, TXT, a, 0.3, l)
    ln = int(520 * ease((l - 0.6) / 0.8))
    if ln > 0:
        ImageDraw.Draw(c).rectangle((120, 492, 120 + ln, 496), fill=mix(BGC, RED, a))
    tD = lc(4, 17, "data and AI", lead=0.35)
    tX = lc(4, 17, "transforming", lead=0.3)
    tI = lc(4, 17, "intelligent insights", lead=0.3)
    # DATA + AI chips, then merge into ACCELERATE DRUG DISCOVERY
    m = eio((l - tX) / 0.6)
    if l >= tD and m < 1:
        pd = back((l - tD) / 0.5); pa = back((l - tD - 0.18) / 0.5)
        d_ = tag_pill("DATA", BLUE); a_ = tag_pill("AI", RED); pl = text("+", "black", 64, TXT)
        x0 = 120
        gx = 0 + m * 120
        put_scaled(c, d_, x0 + d_.width / 2 + gx, 580, max(0.05, pd) * (1 - 0.3 * m), a * (1 - m))
        put(c, pl, x0 + d_.width + 20 + gx * 1.4, 540, a * ease((l - tD - 0.1) / 0.3) * (1 - m))
        put_scaled(c, a_, x0 + d_.width + 90 + a_.width / 2 + gx * 0.4, 580, max(0.05, pa) * (1 - 0.3 * m), a * (1 - m))
    if l >= tX:
        w1 = kin_word(c, "ACCELERATE", 120, 530, 70, TXT, a, tX + 0.15, l, "black", 2)
        p2 = eio((l - tX - 0.45) / 0.5)
        tk = text("DRUG DISCOVERY", "black", 70, (255, 255, 255), 2)
        if p2 > 0:
            pw = int((tk.width + 40) * p2)
            pill_ = Image.new("RGBA", (tk.width + 40, tk.height + 10), (0, 0, 0, 0))
            ImageDraw.Draw(pill_).rounded_rectangle((0, 0, pw, tk.height + 9), 14, fill=BLUE + (255,))
            put(c, pill_, 100, 622, a)
            put(c, tk, 120 + (1 - ease((l - tX - 0.7) / 0.4)) * 20, 625, a * ease((l - tX - 0.7) / 0.4))
    if l >= tI:
        p = ease((l - tI) / 0.6)
        t1 = text("RESEARCH", "bold", 24, TXT2, 4)
        t2 = text("INTELLIGENT INSIGHTS", "bold", 24, KICK, 4)
        put(c, t1, 122, 770, a * p)
        ax0, ax1 = 122 + t1.width + 18, 122 + t1.width + 18 + 70 * p
        ImageDraw.Draw(c).line((ax0, 785, ax1, 785), fill=mix(BGC, RED, a * p), width=3)
        if p > 0.6:
            ImageDraw.Draw(c).polygon([(ax1, 778), (ax1 + 12, 785), (ax1, 792)], fill=mix(BGC, RED, a))
        put(c, t2, ax1 + 26, 770, a * ease((l - tI - 0.3) / 0.5))
    # molecule + research data, AI connections (right)
    cx, cy = 1360, 520
    g = glow(230, 40)
    put(c, g, cx - g.width / 2, cy - g.height / 2, a * 0.9)
    pts = molecule(c, cx, cy, l, t, a, 118)
    tags = [("COMPOUNDS", (1700, 250), 0), ("ASSAYS", (1760, 700), 7), ("GENOMICS", (1050, 840), 12), ("TRIALS", (1000, 200), 14)]
    d = ImageDraw.Draw(c)
    for j, (lab, (tx, ty), ai) in enumerate(tags):
        t0 = 1.2 + 0.25 * j
        aa = a * ease((l - t0) / 0.5)
        if aa <= 0 or not pts:
            continue
        fy = ty + 8 * math.sin(t * 1.2 + j)
        ax_, ay_ = pts[ai]
        p = ease((l - t0 - 0.2) / 0.7)
        # dashed AI connection
        n = 18
        for q in range(int(n * p)):
            if q % 2 == 0:
                u0, u1 = q / n, (q + 1) / n
                d.line((ax_ + (tx - ax_) * u0, ay_ + (fy - ay_) * u0, ax_ + (tx - ax_) * u1, ay_ + (fy - ay_) * u1), fill=mix(BGC, (120, 190, 255), aa * 0.8), width=2)
        if p >= 1:
            u = (t * 0.7 + j * 0.3) % 1
            px, py = ax_ + (tx - ax_) * u, ay_ + (fy - ay_) * u
            d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=mix(BGC, (255, 255, 255), aa))
        d.ellipse((tx - 7, fy - 7, tx + 7, fy + 7), fill=mix(BGC, RED, aa))
        tl_ = text(lab, "bold", 18, TXT, 4)
        put(c, tl_, tx + 16, fy - tl_.height / 2, aa)


def foundation_phase(c, t, l, a):
    e = text("EAI", "black", 96, RED)
    h_ = text("HEALTHCARE", "black", 96, TXT)
    tw = e.width + 24 + h_.width
    x0 = (W - tw) / 2
    put_scaled(c, bolt_sphere(120), x0 - 90, 255, max(0.05, back((l - 0.1) / 0.6)), a)
    kin_word(c, "EAI", x0, 200, 96, RED, a, 0.15, l)
    kin_word(c, "HEALTHCARE", x0 + e.width + 24, 200, 96, TXT, a, 0.3, l)
    k_ = text("EAI HEALTHCARE PLATFORM", "bold", 18, KICK, 6)
    put(c, k_, (W - k_.width) / 2, 160, a * ease((l - 0.3) / 0.5))
    stages = [("TRUSTED DATA", "FOUNDATION", "db", "trusted data"), ("COLLABORATIVE", "AI INTELLIGENCE", "spark", "collaborative"),
              ("ACTIONABLE", "HEALTHCARE OUTCOMES", "heart", "actionable")]
    xs = [420, 960, 1500]
    y = 560
    d = ImageDraw.Draw(c)
    for j, (l1, l2, ic, ph) in enumerate(stages):
        tk = lc(4, 18, ph, lead=0.35) - SC_LOCAL[4]["tF"]
        aa = a * ease((l - tk) / 0.5)
        if j > 0:
            # flowing data link from previous stage
            tp = ease((l - tk + 0.3) / 0.6)
            xa, xb = xs[j - 1] + 95, xs[j] - 95
            if tp > 0:
                d.line((xa, y, xa + (xb - xa) * tp, y), fill=mix(BGC, (120, 190, 255), a * 0.9), width=3)
                if tp >= 1:
                    for q in range(4):
                        u = (t * 0.55 + q / 4) % 1
                        px = xa + (xb - xa) * u
                        d.ellipse((px - 5, y - 5, px + 5, y + 5), fill=mix(BGC, (255, 255, 255), a))
                    d.polygon([(xb - 2, y - 9), (xb + 12, y), (xb - 2, y + 9)], fill=mix(BGC, RED, a))
        if aa <= 0:
            continue
        put_scaled(c, node(ic, 170), xs[j], y, max(0.05, back((l - tk) / 0.6)), aa)
        t1 = text(l1, "black", 34, TXT, 2)
        t2 = text(l2, "black", 34, KICK if j < 2 else (255, 110, 110), 2)
        put(c, t1, xs[j] - t1.width / 2, y + 120 + (1 - ease((l - tk - 0.15) / 0.5)) * 16, aa)
        put(c, t2, xs[j] - t2.width / 2, y + 166 + (1 - ease((l - tk - 0.25) / 0.5)) * 16, aa * ease((l - tk - 0.25) / 0.5))


PLAT_NODES = [  # label lines, sub, icon, (dx, dy)
    (("1. AI WAREHOUSE",), "The unified enterprise data foundation", "warehouse", (-370, 40)),
    (("2. FEDERATED", "GOVERNANCE"), "Trust, control and accountability", "shield", (-300, -180)),
    (("3. AI PATIENT", "360 ANALYTICS"), "A longitudinal intelligence layer for every patient", "chart", (-118, -300)),
    (("4. INTELLIGENT", "IMAGING & RADIOLOGY"), "Imaging intelligence in the enterprise context", "graph", (118, -300)),
    (("5. AI CLINICAL", "INTELLIGENCE"), "From data to contextual, explainable intelligence", "chat", (300, -180)),
    (("6. PURPOSE-BUILT", "HEALTHCARE MODELS"), "Domain-specific multi-agentic intelligence", "heart", (370, 40)),
]


def platform_phase(c, t, l, a, cx0=960, cy0=600, dim_all=False):
    hl = [(2, lc(4, 19, "Patient 360", lead=0.3)), (4, lc(4, 19, "AI Clinical", lead=0.3)), (3, lc(4, 19, "Intelligent Imaging", lead=0.3))]
    hl = [(i, tk - SC_LOCAL[4]["tC"]) for i, tk in hl]
    act = None
    for i, tk in hl:
        if l >= tk:
            act = (i, tk)
    # gentle camera drift toward the active node
    if act:
        dx, dy = PLAT_NODES[act[0]][3]
        p = eio((l - act[1]) / 0.8)
        cx = cx0 - dx * 0.08 * p
        cy = cy0 - dy * 0.08 * p + 30 * p
    else:
        cx, cy = cx0, cy0
    d = ImageDraw.Draw(c)
    # motion points converging into the Solix bolt
    rr = random.Random(9)
    conv = ease(l / 1.4)
    if conv < 1:
        for k in range(70):
            sx_, sy_ = rr.uniform(-100, W + 100), rr.uniform(-100, H + 100)
            x = sx_ + (cx - sx_) * conv
            y = sy_ + (cy - sy_) * conv
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=mix(BGC, (130, 200, 255), a * (1 - conv * 0.7)))
    bs = 300
    sph = bolt_sphere(bs)
    g = glow(220, 50)
    put(c, g, cx - g.width / 2, cy - g.height / 2, a)
    dashed_ring(c, cx, cy, bs * 0.66, t, a, n=48, speed=0.2, width=5)
    put_scaled(c, sph, cx, cy, max(0.05, back((l - 0.6) / 0.7)), a)
    tl_ = text("EAI ", "black", 34, RED, 2)
    th_ = text("HEALTHCARE", "black", 34, TXT, 2)
    put(c, tl_, cx - (tl_.width + th_.width) / 2, cy + bs * 0.72 + 6, a * ease((l - 0.9) / 0.5))
    put(c, th_, cx - (tl_.width + th_.width) / 2 + tl_.width, cy + bs * 0.72 + 6, a * ease((l - 0.9) / 0.5))
    for j, (lines, sub, ic, (dx, dy)) in enumerate(PLAT_NODES):
        t0 = 0.9 + 0.12 * j
        aa = a * ease((l - t0) / 0.5)
        if aa <= 0:
            continue
        is_act = act is not None and act[0] == j
        was = any(i == j and l >= tk for i, tk in hl)
        dimk = 0.45 if (act is not None and not was) else 1.0
        nx, ny = cx + dx, cy + dy
        # connector from ring to node
        ang = math.atan2(dy, dx)
        rx, ry = cx + bs * 0.66 * math.cos(ang), cy + bs * 0.66 * math.sin(ang)
        p = ease((l - t0) / 0.6)
        col = RED if was else (140, 190, 240)
        d.line((rx, ry, rx + (nx - rx) * 0.62 * p, ry + (ny - ry) * 0.62 * p), fill=mix(BGC, col, aa * dimk), width=4 if was else 2)
        d.ellipse((rx - 9, ry - 9, rx + 9, ry + 9), fill=mix(BGC, BLUE if not was else RED, aa))
        d.ellipse((rx - 4, ry - 4, rx + 4, ry + 4), fill=(255, 255, 255))
        if was and p >= 1:
            u = (t * 0.8 + j * 0.2) % 1
            px, py = rx + (nx - rx) * 0.62 * u, ry + (ny - ry) * 0.62 * u
            d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=(255, 255, 255))
        sc_ = 1.0 + (0.18 * eio((l - [tk for i, tk in hl if i == j][0]) / 0.5) if was else 0)
        if is_act:
            pr = 0.5 + 0.5 * math.sin(t * 5)
            rg = 66 * sc_ + 10 + 8 * pr
            d.ellipse((nx - rg, ny - rg, nx + rg, ny + rg), outline=mix(BGC, RED, aa * (0.5 + 0.5 * pr)), width=3)
        put_scaled(c, node(ic, 116), nx, ny, max(0.05, back((l - t0) / 0.5)) * sc_, aa * (dimk if not was else 1))
        # labels outward
        left = dx < 0
        top = dy < -200
        lx = nx - 90 if left else nx + 90
        ly = ny - 20 if not top else ny - 150
        if top:
            lx = nx - 60 if left else nx + 60
        tcol = (255, 255, 255) if was else KICK
        yy = ly
        for li, s_ in enumerate(lines):
            im = text(s_, "black", 26 if was else 24, tcol, 1)
            xx = (lx - im.width) if left else lx
            put(c, im, xx, yy, aa * dimk)
            yy += im.height - 2
        sub_im = text(sub if len(sub) < 40 else sub[:sub.rfind(" ", 0, 38)] + "…", "med", 17, TXT2)
        put(c, sub_im, (lx - sub_im.width) if left else lx, yy + 4, aa * dimk * (1 if was or act is None else 0.7))


CAPS4 = [("AI CLINICAL", "ASSISTANT", "chat", "AI Clinical Assistants"), ("PREVENTIVE", "CARE", "heart", "Preventive Care"),
         ("REVENUE CYCLE", "INTELLIGENCE", "dollar", "Revenue Cycle"), ("AI-POWERED", "DOCUMENTATION", "doc", "AI-Powered")]


def cap_visual(c, j, x, y, l, t, a):
    d = ImageDraw.Draw(c)
    wcol = mix(BGC, (225, 235, 255), a)
    if j == 0:   # chat bubble with typing dots, then reply line
        d.rounded_rectangle((x - 90, y, x + 90, y + 56), 16, outline=wcol, width=3)
        d.polygon([(x - 60, y + 54), (x - 72, y + 74), (x - 40, y + 55)], fill=wcol)
        for q in range(3):
            bump = 6 * max(0, math.sin(t * 6 - q * 0.8))
            d.ellipse((x - 30 + q * 30 - 7, y + 28 - 7 - bump, x - 30 + q * 30 + 7, y + 28 + 7 - bump), fill=mix(BGC, KICK, a))
    elif j == 1:  # ECG line drawing
        pts = []
        for k in range(61):
            u = k / 60
            xx = x - 110 + 220 * u
            ph = (u * 2 + t * 0.8) % 1
            yv = 0
            if 0.40 < ph < 0.44: yv = -14
            elif 0.44 < ph < 0.48: yv = 34
            elif 0.48 < ph < 0.52: yv = -46
            elif 0.52 < ph < 0.56: yv = 10
            pts.append((xx, y + 36 - yv * 0.8))
        d.line(pts, fill=mix(BGC, (255, 110, 110), a), width=4, joint="curve")
    elif j == 2:  # cycle arrows + rising bars
        ang = t * 90
        d.arc((x - 110, y - 2, x - 30, y + 78), ang, ang + 270, fill=wcol, width=4)
        hx = x - 70 + 40 * math.cos(math.radians(ang + 270)); hy = y + 38 + 40 * math.sin(math.radians(ang + 270))
        d.ellipse((hx - 7, hy - 7, hx + 7, hy + 7), fill=mix(BGC, RED, a))
        for q, v in enumerate((0.35, 0.55, 0.8, 1.0)):
            gp = ease((l - 0.3 - q * 0.1) / 0.5)
            d.rectangle((x - 5 + q * 30, y + 76 - 70 * v * gp, x + 15 + q * 30, y + 76), fill=mix(BGC, KICK if q < 3 else RED, a))
    else:        # document lines writing + sparkle
        d.rounded_rectangle((x - 60, y - 8, x + 60, y + 86), 8, outline=wcol, width=3)
        for q in range(5):
            gp = ease((l - 0.3 - q * 0.25) / 0.4)
            wl = (80 if q % 2 == 0 else 60) * gp
            d.line((x - 40, y + 10 + q * 15, x - 40 + wl, y + 10 + q * 15), fill=mix(BGC, KICK, a), width=4)
        s_ = 0.7 + 0.3 * math.sin(t * 4)
        put_scaled(c, icon("spark", 50, (255, 255, 255)), x + 62, y - 6, s_, a)


def caps_phase(c, t, l, a, lock_t):
    xs = [270, 730, 1190, 1650]
    put(c, text("HEALTHCARE CAPABILITIES", "bold", 20, KICK, 6), 120, 230, a * ease(l / 0.5))
    for j, (l1, l2, ic, ph) in enumerate(CAPS4):
        tk = lc(4, 20, ph, lead=0.35) - SC_LOCAL[4]["tL"]
        aa = a * ease((l - tk) / 0.45)
        if aa <= 0:
            continue
        x = xs[j]
        put_scaled(c, node(ic, 150), x, 420, max(0.05, back((l - tk) / 0.55)), aa)
        kin_word(c, l1, x - text(l1, "black", 32, TXT, 1).width / 2, 520, 32, TXT, aa, tk + 0.2, l, "black", 1)
        kin_word(c, l2, x - text(l2, "black", 32, KICK, 1).width / 2, 562, 32, KICK, aa, tk + 0.32, l, "black", 1)
        va = aa * ease((l - tk - 0.55) / 0.5)
        if va > 0:
            cap_visual(c, j, x, 650, l - tk - 0.55, t, va)


def lockup_phase(c, t, l, a):
    cx = W / 2
    put(c, glow(260, 45), cx - glow(260, 45).width / 2, 430 - glow(260, 45).height / 2, a)
    put_scaled(c, bolt_sphere(230), cx, 400, max(0.05, back(l / 0.7)), a)
    e = text("EAI ", "black", 92, RED, 2); h_ = text("HEALTHCARE", "black", 92, TXT, 2)
    x0 = cx - (e.width + h_.width) / 2
    kin_word(c, "EAI ", x0, 580, 92, RED, a, 0.2, l, "black", 2)
    kin_word(c, "HEALTHCARE", x0 + e.width, 580, 92, TXT, a, 0.3, l, "black", 2)
    tg = text("TRUSTED DATA FOUNDATION  →  COLLABORATIVE AI INTELLIGENCE  →  ACTIONABLE HEALTHCARE OUTCOMES", "bold", 22, KICK, 3)
    put(c, tg, cx - tg.width / 2, 712, a * ease((l - 0.6) / 0.6))


SC_LOCAL = {}


def scene4(c, t, lt, G):
    k = 4
    st = SC[4]["start"]
    tF = lc(k, 18, lead=0.7)
    tC = lc(k, 19, lead=0.6)
    tL = lc(k, 20, lead=0.5)
    tLock = cue(20) + LINES[20]["dur"] - st - 0.1
    SC_LOCAL[4] = {"tF": tF, "tC": tC, "tL": tL}
    if lt < tF + 0.5:
        pharma_phase(c, t, lt, G * phase_alpha(lt, 0.0, tF, 0.4, 0.5))
    if tF <= lt < tC + 0.5:
        foundation_phase(c, t, lt - tF, G * phase_alpha(lt, tF, tC, 0.3, 0.5))
    if tC <= lt < tL + 0.5:
        platform_phase(c, t, lt - tC, G * phase_alpha(lt, tC, tL, 0.3, 0.5))
    if tL <= lt < tLock + 0.5:
        caps_phase(c, t, lt - tL, G * phase_alpha(lt, tL, tLock, 0.3, 0.5), tLock - tL)
    if lt >= tLock:
        lockup_phase(c, t, lt - tLock, G * ease((lt - tLock) / 0.5))
