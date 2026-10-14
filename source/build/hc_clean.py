"""Clean RGB+Alpha pull for the EAI Healthcare clips (v2).

v1 (hc_matte.py) kept everything that differed from the background, so the
pink drop shadows, white glows and haze of the flattened video came along and
looked dirty on any new background. v2 keeps only solid graphics:

* "background-like" pixels (same hue as the background, only lighter/darker:
  shadows, glows, haze) are dropped unless they form a sharp-edged object
  (grey particles, white badges/cards);
* inside the solid shape alpha is 1 and the colour is the real pixel;
* a 2-3 px edge band gets proper anti-aliased alpha with the edge colour taken
  from the solid interior (no pink fringe).
"""
import cv2
import numpy as np

from hc_matte import background_plate, degrid, _bg_family  # noqa: F401


def _solid_fill(c, b, a, S, cards, outlines):
    """Reuse v1's card / badge / icon-stroke logic on the solid mask."""
    from hc_matte import pull_matte
    _, a1, fill = pull_matte(c, b, cards, outlines=outlines)
    extra = (a1 > 0.97) & ~S
    # only take v1's fills that are enclosed by solid (cards, badges, icon strokes)
    return extra, fill


def clean_matte(c, b, cards=False, outlines=False):
    """c, b: float32 HxWx3. Returns straight rgb (float32) and alpha (0-1)."""
    h, w = c.shape[:2]
    diff = c - b
    d = np.sqrt((diff * diff).sum(axis=2))
    nc = np.linalg.norm(c, axis=2) + 1e-3
    nb = np.linalg.norm(b, axis=2) + 1e-3
    cos = (c * b).sum(axis=2) / (nc * nb)
    ratio = nc / nb
    bglike = (cos > 0.9965) & (ratio > 0.5)

    strong = (d > 16) & ~bglike
    cand = ((d > 9) & bglike).astype(np.uint8)
    gray = cv2.cvtColor(np.clip(c, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    grad = np.sqrt(gx * gx + gy * gy)
    keep = np.zeros((h, w), bool)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand, connectivity=8)
    if n > 1:
        edge = cand & ~cv2.erode(cand, np.ones((3, 3), np.uint8))
        el = lab[edge > 0]
        gs = np.bincount(el, weights=grad[edge > 0], minlength=n)
        gc = np.bincount(el, minlength=n)
        sharp = gs / np.maximum(gc, 1)
        ok = (sharp > 40) & (st[:, 4] >= 6)
        ok[0] = False
        keep = ok[lab]
    S = strong | keep

    # enclosed non-background holes (glass, white strokes inside solids)
    inv = (~S).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    if n > 1:
        dm = np.bincount(lab.ravel(), weights=d.ravel(), minlength=n) / np.maximum(st[:, 4], 1)
        border = np.zeros(n, bool)
        border[np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))] = True
        small = (st[:, 4] < 2500) & ~border & (dm > 7)
        small[0] = False
        S |= small[lab]

    # v1 card / badge fills (opaque white panels that equal the background colour)
    if cards or outlines:
        _, fill = _solid_fill(c, b, None, S, cards, outlines)
        if fill is not None:
            S |= fill.astype(bool)
        if outlines:
            from hc_matte import pull_matte
            _, a_o, _ = pull_matte(c, b, False, outlines=True)
            badge = (a_o > 0.99) & (d < 16)
            S |= badge & cv2.dilate(S.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)

    # remove isolated specks
    n, lab, st, _ = cv2.connectedComponentsWithStats(S.astype(np.uint8), connectivity=8)
    if n > 1:
        tiny = st[:, 4] < 8
        tiny[0] = False
        S &= ~tiny[lab]

    S8 = S.astype(np.uint8)
    inner = cv2.erode(S8, np.ones((3, 3), np.uint8)).astype(bool)
    near = cv2.dilate(S8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))).astype(bool)
    band = near & ~inner

    # edge colour: nearest solid-interior colour (fallback: any solid colour)
    src = inner if inner.any() else S
    m = src.astype(np.float32)
    num = cv2.GaussianBlur(c * m[..., None], (0, 0), 1.6)
    den = cv2.GaussianBlur(m, (0, 0), 1.6)[..., None]
    num2 = cv2.GaussianBlur(c * S[..., None].astype(np.float32), (0, 0), 3.0)
    den2 = cv2.GaussianBlur(S.astype(np.float32), (0, 0), 3.0)[..., None]
    f = np.where(den > 0.03, num / np.maximum(den, 1e-4), num2 / np.maximum(den2, 1e-4))
    fb = f - b
    nfb = (fb * fb).sum(axis=2)
    proj = np.clip((diff * fb).sum(axis=2) / np.maximum(nfb, 1.0), 0, 1)
    proj = np.where(nfb < 400, np.clip(d / 20.0, 0, 1), proj)

    a = np.zeros((h, w), np.float32)
    a[S] = 1.0
    a[band] = proj[band]
    a[inner] = 1.0
    rgb = np.where(band[..., None], f, c)
    return np.clip(rgb, 0, 255), a


def recolor(rgb, a, protect):
    """Solix theme for flat graphics: dark text -> #30267b, reds -> #ee2424.
    protect: bool mask of photo/screenshot areas left untouched."""
    navy = np.array([0x30, 0x26, 0x7b], np.float32)
    red = np.array([0xee, 0x24, 0x24], np.float32)
    r, g, bl = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    dark = (mx < 95) & (a > 0) & ~protect
    reds = (r > 170) & (g < 95) & (bl < 100) & (r - g > 110) & (a > 0) & ~protect
    out = rgb.copy()
    # keep the anti-aliasing: blend by how "pure" the source colour is
    k = np.clip((95 - mx) / 40, 0, 1)[..., None]
    out = np.where(dark[..., None], out * (1 - k) + navy * k, out)
    out = np.where(reds[..., None], red, out)
    return out


# Flat colours used by the graphics (measured from the video) + white.
PALETTE = np.array([
    [21, 22, 29], [1, 1, 1], [29, 40, 67], [29, 57, 138], [100, 116, 137], [140, 138, 139],
    [243, 37, 43], [237, 33, 33], [205, 27, 33], [231, 35, 42], [241, 84, 85], [240, 68, 58],
    [134, 86, 248], [19, 183, 214], [242, 156, 10], [249, 113, 20], [247, 185, 88],
    [34, 161, 73], [46, 105, 253], [255, 255, 255]], np.float32)
WHITE = len(PALETTE) - 1


def palette_unmix(c, b, pal=PALETTE, mask=None):
    """Per pixel: best flat colour K and coverage a with c = a*K + (1-a)*b.
    Only pixels in mask are evaluated (others: residual inf)."""
    h, w = c.shape[:2]
    best_r = np.full((h, w), 1e9, np.float32)
    best_a = np.zeros((h, w), np.float32)
    best_k = np.zeros((h, w), np.int16)
    idx = np.nonzero(mask) if mask is not None else np.nonzero(np.ones((h, w), bool))
    cc, bb = c[idx], b[idx]
    diff = cc - bb
    br = np.full(len(cc), 1e9, np.float32)
    ba = np.zeros(len(cc), np.float32)
    bk = np.zeros(len(cc), np.int16)
    for k, K in enumerate(pal):
        kb = K[None, :] - bb
        n = (kb * kb).sum(axis=1)
        a = np.clip((diff * kb).sum(axis=1) / np.maximum(n, 1.0), 0, 1)
        res = np.sqrt(((diff - a[:, None] * kb) ** 2).sum(axis=1))
        res = np.where(n < 1600, 1e9, res)  # colour too close to the background: ambiguous
        better = res < br
        br = np.where(better, res, br)
        ba = np.where(better, a, ba)
        bk = np.where(better, k, bk)
    best_r[idx], best_a[idx], best_k[idx] = br, ba, bk
    return best_a, best_k, best_r


THEME_NAVY = np.array([0x30, 0x26, 0x7b], np.float32)
THEME_RED = np.array([0xee, 0x24, 0x24], np.float32)
THEME_BLUE = np.array([0x00, 0x88, 0xcf], np.float32)
DARKS = np.array([[21, 22, 29], [1, 1, 1], [29, 40, 67]], np.float32)
REDS = np.array([[243, 37, 43], [237, 33, 33], [205, 27, 33], [231, 35, 42]], np.float32)


def full_matte(c, cards=False, outlines=False, protect_box=None, ellipse=None, dark=False):
    """v2 pull: v1 matte for photos/cards, palette unmix for flat graphics,
    weak haze dropped, Solix colour theme on flat graphics.
    Returns straight rgb, alpha, background plate."""
    from hc_matte import matte_frame
    rgb1, a1, b, fill = matte_frame(c, cards, outlines, return_fill=True)
    h, w = a1.shape
    protect = np.zeros((h, w), bool)
    if cards and fill is not None:
        protect |= cv2.dilate(fill.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    if protect_box is not None:
        x0, y0, x1, y1 = protect_box
        protect[y0:y1, x0:x1] = True
    dfull = np.sqrt(((c - b) ** 2).sum(axis=2))
    pa, pk, pr = palette_unmix(c, b, mask=(dfull > 4) & (a1 < 0.999))
    ok = (pr < 12) & (a1 < 0.999) & ~(protect & (a1 > 0.5))
    a = np.where(ok, pa, a1)
    rgb = np.where(ok[..., None], PALETTE[pk], rgb1)
    a = np.where(ok & (pk == WHITE) & (pa < 0.6), 0.0, a)
    a = np.where(~ok & (a1 < 0.4), 0.0, a)
    # photos / 3D renders: drop their baked-in pink/white haze, crumbs, soften the cut
    if protect.any():
        nc = np.linalg.norm(c, axis=2) + 1e-3
        nb = np.linalg.norm(b, axis=2) + 1e-3
        cos = (c * b).sum(axis=2) / (nc * nb)
        haze = protect & ~ok & (cos > 0.996) & (a < 0.8) & ~(cards & (a1 > 0.999))
        a = np.where(haze, 0.0, a)
        img = (a > 0.02) & protect & ~ok
        n, lab, st, _ = cv2.connectedComponentsWithStats(img.astype(np.uint8), connectivity=8)
        if n > 1:
            crumbs = st[:, 4] < 300
            crumbs[0] = False
            a = np.where(crumbs[lab], 0.0, a)
        soft = cv2.GaussianBlur(a, (0, 0), 0.8)
        edge = protect & (a < 0.999) & ~ok
        a = np.where(edge, np.minimum(a, soft), a)
    # white/light shapes enclosed by a solid (logo bolt, icon glyphs), also while fading
    dfull2 = np.sqrt(((c - b) ** 2).sum(axis=2))
    solid = (a > 0.45).astype(np.uint8)
    ns_, sl, ss, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    nh, hl, hs, _ = cv2.connectedComponentsWithStats(1 - solid, connectivity=4)
    for i in range(1, nh):
        x, y, ww_, hh_, area = hs[i]
        if area > 6000 or x == 0 or y == 0 or x + ww_ >= w or y + hh_ >= h:
            continue
        y0, y1, x0, x1 = y - 1, y + hh_ + 1, x - 1, x + ww_ + 1
        reg = hl[y0:y1, x0:x1] == i
        if dfull2[y0:y1, x0:x1][reg].mean() < 10:
            continue  # background seen through a letter counter
        ring = cv2.dilate(reg.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~reg
        par = sl[y0:y1, x0:x1][ring]
        par = par[par > 0]
        if len(par) == 0 or ss[np.bincount(par).argmax(), 4] < 2500:
            continue  # only inside big solids (icon discs), never inside letters
        pid = np.bincount(par).argmax()
        px, py, pw, ph = ss[pid, :4]
        if pw > 1.6 * ph or ph > 1.6 * pw:
            continue  # disc-like parents only (title words are wide)
        if ss[pid, 4] < 0.68 * pw * ph or area > 0.2 * pw * ph or pw < 50 or ph < 50:
            continue  # a ring (letter O) with a big opening, not a solid disc with a glyph
        ra = float(np.median(a[y0:y1, x0:x1][ring]))
        if ra < 0.45:
            continue
        sub_c, sub_b = c[y0:y1, x0:x1], b[y0:y1, x0:x1]
        a[y0:y1, x0:x1][reg] = ra
        rgb[y0:y1, x0:x1][reg] = np.clip(sub_b + (sub_c - sub_b) / ra, 0, 255)[reg]
    # red discs (Solix mark: the bolt cuts the disc in two, so it is no "hole")
    redm = ((np.linalg.norm(rgb - THEME_RED, axis=2) < 70) | (np.linalg.norm(rgb - REDS[1], axis=2) < 70)) & (a > 0.4)
    if redm.sum() > 800:
        circ = cv2.HoughCircles(cv2.GaussianBlur(redm.astype(np.uint8) * 255, (0, 0), 2), cv2.HOUGH_GRADIENT,
                                dp=1.5, minDist=60, param1=120, param2=38, minRadius=18, maxRadius=190)
        if circ is not None:
            yy, xx = np.mgrid[0:h, 0:w]
            for cx_, cy_, r_ in circ[0]:
                x0, x1 = int(max(cx_ - r_ - 2, 0)), int(min(cx_ + r_ + 3, w))
                y0, y1 = int(max(cy_ - r_ - 2, 0)), int(min(cy_ + r_ + 3, h))
                disk = (xx[y0:y1, x0:x1] - cx_) ** 2 + (yy[y0:y1, x0:x1] - cy_) ** 2 <= (r_ - 1.5) ** 2
                inner_red = redm[y0:y1, x0:x1] & disk
                if inner_red.sum() < 0.55 * disk.sum():
                    continue  # not a solid red disc
                d2 = (xx[y0:y1, x0:x1] - cx_) ** 2 + (yy[y0:y1, x0:x1] - cy_) ** 2
                ann = (d2 >= (0.3 * r_) ** 2) & (d2 <= (0.85 * r_) ** 2)
                if redm[y0:y1, x0:x1][ann].mean() < 0.72:
                    continue  # hollow (a letter O), not a solid disc
                yo0, yo1 = int(max(cy_ - r_ - 8, 0)), int(min(cy_ + r_ + 9, h))
                xo0, xo1 = int(max(cx_ - r_ - 8, 0)), int(min(cx_ + r_ + 9, w))
                dd_ = (xx[yo0:yo1, xo0:xo1] - cx_) ** 2 + (yy[yo0:yo1, xo0:xo1] - cy_) ** 2
                ring_ = (dd_ > (r_ + 3) ** 2) & (dd_ <= (r_ + 7) ** 2)
                if redm[yo0:yo1, xo0:xo1][ring_].mean() > 0.12:
                    continue  # red continues outside: a letter, not an isolated disc
                ra = float(np.median(a[y0:y1, x0:x1][inner_red]))
                fillp = disk & ~inner_red
                sub_c, sub_b = c[y0:y1, x0:x1], b[y0:y1, x0:x1]
                a[y0:y1, x0:x1][fillp] = ra
                rgb[y0:y1, x0:x1][fillp] = np.clip(sub_b + (sub_c - sub_b) / max(ra, 0.05), 0, 255)[fillp]
    # cards: clear the soft pink glow band around them (sides and below, not the title above)
    if cards and fill is not None and fill.any():
        f8 = fill.astype(np.uint8)
        top = int(np.nonzero(f8.any(axis=1))[0].min())
        halo = cv2.dilate(f8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (161, 161))).astype(bool) & \
            ~cv2.dilate(f8, np.ones((3, 3), np.uint8)).astype(bool)
        halo[:max(top - 12, 0)] = False
        keep = (a > 0.8) & ~((rgb[..., 0] > 200) & (rgb[..., 1] > 100) & (rgb[..., 2] > 100))  # not pink glow
        keep = cv2.dilate(keep.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        a = np.where(halo & ~keep, 0.0, a)
    # no free-floating soft shadows / glows: weak alpha must hug a solid shape
    core = (a > 0.8).astype(np.uint8)
    near = cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))).astype(bool)
    a = np.where((a < 0.8) & ~near & ~protect, 0.0, a)
    # a soft oval for a full-bleed render (globe): keep the image whole, feather its edge
    if ellipse is not None:
        cx, cy, rx, ry, fe = ellipse
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        m = np.clip((1.0 - r) * min(rx, ry) / fe, 0, 1)
        m = m * m * (3 - 2 * m)
        inside = m > 0
        a = np.where(inside, np.maximum(a * (r > 1), a1 * m), a)
        rgb = np.where(inside[..., None], rgb1, rgb)
        protect |= inside
    # Solix colour theme on flat graphics
    flat = (a > 0) & ~protect
    dd = np.min(np.linalg.norm(rgb[..., None, :] - DARKS[None, None], axis=3), axis=2)
    rd = np.min(np.linalg.norm(rgb[..., None, :] - REDS[None, None], axis=3), axis=2)
    rd_m = flat & (rd < 30)
    if not dark:
        rgb = np.where((flat & (dd < 30))[..., None], THEME_NAVY, rgb)
    else:
        # dark Solix background: dark text becomes white, grey text light grey,
        # dark filled discs become Solix blue; text sitting on white (badges) stays dark
        lum = rgb.mean(axis=2)
        chroma = rgb.max(axis=2) - rgb.min(axis=2)
        on_white = cv2.GaussianBlur(((a > 0.9) & (lum > 215)).astype(np.float32), (0, 0), 5) > 0.25
        # dark or grey ink (incl. anti-aliased edges), not red, not on a white badge/card
        ink = flat & ~on_white & ~rd_m & (lum < 185) & (chroma < 75) & ~((rgb[..., 0] > 150) & (rgb[..., 0] - rgb[..., 2] > 60))
        dist = cv2.distanceTransform((ink & (a > 0.5)).astype(np.uint8), cv2.DIST_L2, 3)
        n, lab, st, _ = cv2.connectedComponentsWithStats((ink & (a > 0.2)).astype(np.uint8), connectivity=8)
        thick = np.zeros(n, np.float32)
        np.maximum.at(thick, lab.ravel(), dist.ravel())
        roundish = np.zeros(n, bool)
        for j in np.nonzero(thick > 11)[0]:
            x_, y_, w_, h_, ar_ = st[j]
            roundish[j] = 0.75 < w_ / max(h_, 1) < 1.33 and ar_ > 0.62 * w_ * h_
        shape = (thick > 11)[lab] & ink                      # filled shapes (not text)
        disc_ink = roundish[lab] & ink                       # dark round icon discs
        text = ink & ~shape
        darkish = (lum < 110)
        rgb = np.where((disc_ink & darkish & (dd < 40))[..., None], THEME_BLUE, rgb)
        rgb = np.where((shape & ~disc_ink & darkish)[..., None], np.float32([255, 255, 255]), rgb)
        # text: pure white (or light grey) ink, coverage from how much darker than
        # the background the original pixel is -> smooth anti-aliased edges
        lc = c.mean(axis=2)
        lb = b.mean(axis=2)
        # around solid discs (icon circles, logo) nothing is text; their faint shadow goes
        solid8 = (a > 0.8).astype(np.uint8)
        dsol = cv2.distanceTransform(solid8, cv2.DIST_L2, 3)
        ns2, lab2, _, _ = cv2.connectedComponentsWithStats(solid8, connectivity=8)
        th2 = np.zeros(ns2, np.float32)
        np.maximum.at(th2, lab2.ravel(), dsol.ravel())
        body = (th2 > 14)[lab2] & (solid8 > 0)
        near_disc = cv2.dilate(body.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))).astype(bool)
        a = np.where(near_disc & ~body & (a < 0.7) & ~protect, 0.0, a)
        reg = cv2.dilate(text.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~shape & ~rd_m & ~near_disc
        if protect.any():
            reg &= ~protect
        ink = cv2.erode(np.where(reg, lc, 255).astype(np.float32), np.ones((7, 7), np.uint8))
        ink = np.minimum(ink, 150)
        cov = np.clip((lb - lc) / np.maximum(lb - ink, 30), 0, 1)
        grey_ink = ink > 95
        a = np.where(reg, cov, a)
        rgb = np.where((reg & ~grey_ink)[..., None], np.float32([255, 255, 255]), rgb)
        rgb = np.where((reg & grey_ink)[..., None], np.float32([214, 218, 232]), rgb)
    rgb = np.where(rd_m[..., None], THEME_RED, rgb)
    return np.clip(rgb, 0, 255), np.clip(a, 0, 1), b
