

# --- 3D "Your AI Journey Starts Here" wheel (Solix Academy) -----------------------------------------
WHEEL = [  # (title lines, product, icon, start_deg, end_deg)  math angles, counter-clockwise
    (("AI-Ready", "Data"), "Solix CDP", "db", 94, 206),
    (("AI-Ready", "People"), "Solix Academy", "people", 334, 446),
    (("AI-Ready", "Enterprise"), "Solix EAI", "building", 214, 326),
]
SEG_TOP = (252, 230, 230)
SEG_SIDE = (205, 120, 128)
SEG_SIDE2 = (170, 80, 92)


@lru_cache(None)
def people_icon(size):
    ss = 4; S_ = size * ss
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = RED + (255,)
    for cx_, cy_, r_ in ((0.5, 0.36, 0.13), (0.24, 0.42, 0.1), (0.76, 0.42, 0.1)):
        d.ellipse((S_ * (cx_ - r_), S_ * (cy_ - r_), S_ * (cx_ + r_), S_ * (cy_ + r_)), fill=col)
    d.rounded_rectangle((S_ * 0.33, S_ * 0.52, S_ * 0.67, S_ * 0.8), S_ * 0.08, fill=col)
    d.rounded_rectangle((S_ * 0.1, S_ * 0.55, S_ * 0.38, S_ * 0.78), S_ * 0.07, fill=col)
    d.rounded_rectangle((S_ * 0.62, S_ * 0.55, S_ * 0.9, S_ * 0.78), S_ * 0.07, fill=col)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(None)
def building_icon(size):
    ss = 4; S_ = size * ss
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = RED + (255,)
    d.rectangle((S_ * 0.2, S_ * 0.3, S_ * 0.55, S_ * 0.85), fill=col)
    d.rectangle((S_ * 0.55, S_ * 0.15, S_ * 0.82, S_ * 0.85), fill=col)
    for yy in (0.38, 0.5, 0.62, 0.74):
        for xx in (0.26, 0.4):
            d.rectangle((S_ * xx, S_ * yy, S_ * (xx + 0.07), S_ * (yy + 0.06)), fill=(255, 255, 255, 255))
        d.rectangle((S_ * 0.62, S_ * (yy - 0.12), S_ * 0.69, S_ * (yy - 0.06)), fill=(255, 255, 255, 255))
    return im.resize((size, size), Image.LANCZOS)


def wheel_icon(kind, size):
    if kind == "people":
        return people_icon(size)
    if kind == "building":
        return building_icon(size)
    return icon("db", size, RED)


def wheel3d(c, cx, cy, l, t, a):
    """Extruded 3-segment ring: segments fly in, tilt settles, gentle float."""
    if a <= 0.01:
        return
    R, r, h = 360, 140, 46
    settle = eio((l - 0.2) / 1.8)
    tilt = math.radians(62 - 40 * settle + 2.5 * math.sin(t * 0.8))
    spin = math.radians(-50 * (1 - settle) + 3 * math.sin(t * 0.5))
    ct, st_ = math.cos(tilt), math.sin(tilt)
    # ground shadow
    sh = Image.new("RGBA", (int(2 * R + 200), int(2 * R * ct + 200)), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((100, 100 + 40, 100 + 2 * R, 100 + 2 * R * ct + 40), fill=(0, 0, 12, int(150 * a)))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    put(c, sh, cx - sh.width / 2, cy - sh.height / 2 + h * st_ + 20, 1.0)

    def P(rad, ang, z, off=(0, 0)):
        x = rad * math.cos(ang) + off[0]
        y = rad * math.sin(ang) + off[1]
        return (cx + x, cy - y * ct - z * st_)

    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    segs = []
    for j, (tl, prod, ic, a0, a1) in enumerate(WHEEL):
        p = back((l - 0.15 - 0.22 * j) / 0.75)
        if p <= 0:
            continue
        mid = math.radians((a0 + a1) / 2) + spin
        pop = 30 * max(0.0, 1 - ease((l - 0.15 - 0.22 * j) / 0.9)) + 14 * max(0.0, math.sin(t * 1.4 + j * 2.1)) * settle * 0.4
        lift = (1 - min(1.0, p)) * -260
        off = (pop * math.cos(mid), pop * math.sin(mid))
        angs = [math.radians(a0 + (a1 - a0) * k / 40) + spin for k in range(41)]
        segs.append((math.sin(mid), j, angs, off, lift, min(1.0, max(0.0, p)), tl, prod, ic, mid))
    segs.sort(key=lambda s_: -s_[0])  # back (top of screen) first
    for (_, j, angs, off, lift, pp, tl, prod, ic, mid) in segs:
        al = int(255 * pp * a)
        # inner wall (visible on the far side)
        for k in range(len(angs) - 1):
            if math.sin(angs[k]) > 0:
                q = [P(r, angs[k], lift, off), P(r, angs[k + 1], lift, off), P(r, angs[k + 1], lift - h, off), P(r, angs[k], lift - h, off)]
                d.polygon(q, fill=SEG_SIDE2 + (al,))
        # outer wall (front half)
        for k in range(len(angs) - 1):
            if math.sin(angs[k]) < 0.05:
                shade = 0.75 + 0.25 * math.cos(angs[k] + 0.6)
                col = tuple(int(v * shade) for v in SEG_SIDE)
                q = [P(R, angs[k], lift, off), P(R, angs[k + 1], lift, off), P(R, angs[k + 1], lift - h, off), P(R, angs[k], lift - h, off)]
                d.polygon(q, fill=col + (al,))
        # end caps
        for ang in (angs[0], angs[-1]):
            q = [P(r, ang, lift, off), P(R, ang, lift, off), P(R, ang, lift - h, off), P(r, ang, lift - h, off)]
            d.polygon(q, fill=SEG_SIDE2 + (al,))
        # top face
        top = [P(R, an, lift, off) for an in angs] + [P(r, an, lift, off) for an in reversed(angs)]
        d.polygon(top, fill=SEG_TOP + (al,))
        # rim highlight
        d.line([P(R, an, lift, off) for an in angs], fill=(255, 255, 255, int(al * 0.9)), width=2)
    lay = lay.filter(ImageFilter.SMOOTH)
    c.paste(lay, (0, 0), lay)
    # labels on top faces
    for (_, j, angs, off, lift, pp, tl, prod, ic, mid) in segs:
        la = a * ease((l - 0.9 - 0.22 * j) / 0.5)
        if la <= 0:
            continue
        rm = (R + r) / 2 + 12
        lx, ly = P(rm, mid, lift, off)
        icn = wheel_icon(ic, 46)
        t1 = text(tl[0], "bold", 34, INK)
        t2 = text(tl[1], "bold", 34, INK)
        t3 = text(prod, "semi", 24, RED)
        hgt = icn.height + 6 + t1.height + t2.height - 8 + t3.height
        y0 = ly - hgt / 2
        put(c, icn, lx - icn.width / 2, y0, la); y0 += icn.height + 6
        put(c, t1, lx - t1.width / 2, y0, la); y0 += t1.height - 6
        put(c, t2, lx - t2.width / 2, y0, la); y0 += t2.height - 2
        put(c, t3, lx - t3.width / 2, y0, la)
    # centre disc
    ca = a * ease((l - 0.7) / 0.6)
    if ca > 0:
        rr_ = r - 14
        disc = Image.new("RGBA", (int(2 * rr_ + 4), int(2 * rr_ * ct + 4)), (0, 0, 0, 0))
        ImageDraw.Draw(disc).ellipse((2, 2, 2 * rr_ + 2, 2 * rr_ * ct + 2), fill=(255, 255, 255, 255))
        put(c, disc, cx - disc.width / 2, cy - disc.height / 2, ca)
        yy = cy - 46
        for s_ in ("Your AI", "Journey Starts", "Here"):
            im = text(s_, "bold", 26, RED)
            put(c, im, cx - im.width / 2, yy, a * ease((l - 1.0) / 0.5))
            yy += 31
