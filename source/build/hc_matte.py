"""Background removal for the finalized EAI Healthcare video.

The video was delivered flattened on a soft white-to-pink animated gradient
(with a faint grid). Per frame we rebuild that background plate from the
pixels that look like background, then pull a straight-alpha matte of the
graphics against it:

  B  = smooth background plate (normalized convolution of background pixels)
  F  = local estimate of the solid foreground colour near each pixel
  a  = projection of (C - B) onto (F - B)
  out RGB = B + (C - B) / a   (colour decontaminated, straight alpha)
"""
import cv2
import numpy as np


GRID = 64


def degrid(c):
    """Remove the faint 1px background grid (every 64px) where it is not
    under graphics: replace the line pixel by the mean of its neighbours."""
    c = c.copy()
    h, w = c.shape[:2]
    for x in range(0, w, GRID):
        x0, x1 = max(x - 2, 0), min(x + 2, w - 1)
        nb = (c[:, x0] + c[:, x1]) / 2
        ok = np.abs(c[:, x] - nb).max(axis=1) < 14
        c[ok, x] = nb[ok]
    for y in range(0, h, GRID):
        y0, y1 = max(y - 2, 0), min(y + 2, h - 1)
        nb = (c[y0] + c[y1]) / 2
        ok = np.abs(c[y] - nb).max(axis=1) < 14
        c[y, ok] = nb[ok]
    return c


def _bg_family(img):
    """Pixels whose colour belongs to the white->pink background family."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    return (r > 236) & (g > 128) & (np.abs(g - b) < 9) & (r - g < 112) & (r >= g - 2)


def background_plate(c, exclude=None):
    """c: float32 HxWx3 (0-255). Returns smooth background plate B."""
    h, w = c.shape[:2]
    s = 8
    small = cv2.resize(c, (w // s, h // s), interpolation=cv2.INTER_AREA)
    # block flatness: background is smooth at 8px scale
    sq = cv2.resize(c * c, (w // s, h // s), interpolation=cv2.INTER_AREA)
    std = np.sqrt(np.maximum(sq - small * small, 0)).max(axis=2)
    m = (_bg_family(small) & (std < 3.0)).astype(np.float32)
    if exclude is not None:
        ex = cv2.resize(exclude.astype(np.float32), (w // s, h // s), interpolation=cv2.INTER_AREA)
        m = m * (ex < 0.01)
    m = cv2.erode(m, np.ones((3, 3), np.uint8))
    plate = None
    for sigma in (5, 12, 30):
        num = cv2.GaussianBlur(small * m[..., None], (0, 0), sigma)
        den = cv2.GaussianBlur(m, (0, 0), sigma)[..., None]
        est = num / np.maximum(den, 1e-4)
        if plate is None:
            plate, wsum = est * 0, np.zeros_like(den)
        wgt = np.clip(den * 8, 0, 1) * (1 - wsum)
        plate += est * wgt
        wsum += wgt
    plate = plate / np.maximum(wsum, 1e-4)
    # keep observed background where we trust it, smooth everywhere
    plate = cv2.GaussianBlur(plate, (0, 0), 1.5)
    return cv2.resize(plate, (w, h), interpolation=cv2.INTER_CUBIC)


def pull_matte(c, b, fill_holes=False, min_hole=20000, force=None, outlines=False):
    """Straight-alpha RGBA (float32, 0-1 alpha, 0-255 rgb) from frame c and plate b."""
    diff = c - b
    d = np.sqrt((diff * diff).sum(axis=2))
    core = (d > 40).astype(np.float32)
    # foreground colour estimate from nearby solid pixels
    num = cv2.GaussianBlur(c * core[..., None], (0, 0), 2.2)
    den = cv2.GaussianBlur(core, (0, 0), 2.2)[..., None]
    f = np.where(den > 0.02, num / np.maximum(den, 1e-4), c)
    fb = f - b
    nfb = (fb * fb).sum(axis=2)
    a_proj = (diff * fb).sum(axis=2) / np.maximum(nfb, 1.0)
    a_weak = d / 40.0
    a = np.where(nfb > 900, a_proj, a_weak)
    # suppress faint grid/noise
    a = a * np.clip((d - 9.0) / 8.0, 0, 1)
    a = np.clip(a, 0, 1)
    # thin dips between two solid colours (white icon strokes inside a coloured
    # circle) are not transparency: close them where the colour is clearly not background
    solid = (a > 0.85).astype(np.uint8)
    closed = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    a = np.where((closed > 0) & (d > 25) & ~_bg_family(c), 1.0, a)
    # white strokes enclosed by a big solid shape (icons inside circles) are
    # close to the background colour; fill them when they are not background-like
    solid = (a > 0.85).astype(np.uint8)
    ns, slab, sst, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    nh, hlab, hst, _ = cv2.connectedComponentsWithStats(1 - solid, connectivity=4)
    hh, ww = a.shape
    for i in range(1, nh):
        x, y, w_, h_, area = hst[i]
        if area > (12000 if outlines else 900) or x == 0 or y == 0 or x + w_ >= ww or y + h_ >= hh:
            continue
        ys0, ys1, xs0, xs1 = max(y - 1, 0), min(y + h_ + 1, hh), max(x - 1, 0), min(x + w_ + 1, ww)
        reg = hlab[ys0:ys1, xs0:xs1] == i
        ring = cv2.dilate(reg.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~reg
        par = slab[ys0:ys1, xs0:xs1][ring]
        par = par[par > 0]
        if len(par) == 0:
            continue
        pid = np.bincount(par).argmax()
        if outlines and area > 400:
            px, py, pw, ph = sst[pid, :4]
            if w_ * h_ > 0.75 * pw * ph and c[ys0:ys1, xs0:xs1][reg].mean() > 235:
                a[ys0:ys1, xs0:xs1][reg] = 1.0  # inside of an outlined badge/pill
            continue
        if area > 900 or sst[pid, 4] < 1500:
            continue
        thick = cv2.distanceTransform(np.pad(reg, 1).astype(np.uint8), cv2.DIST_L2, 3).max()
        if thick > 3.5:
            continue  # a real opening (letter counter), not a thin stroke
        a[ys0:ys1, xs0:xs1][reg] = 1.0
    # isolated noise specks
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.02).astype(np.uint8), connectivity=8)
    if n > 1:
        amax = np.zeros(n, np.float32)
        np.maximum.at(amax, lab.ravel(), a.ravel())
        kill = (st[:, 4] < 14) & (amax < 0.6)
        kill[0] = False
        a = np.where(kill[lab], 0.0, a)
    if outlines:
        # small outlined badges (white pills with a thin grey border)
        closed = cv2.morphologyEx((a > 0.12).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            x, y, ww_, hh_ = cv2.boundingRect(cnt)
            if not (50 <= ww_ <= 240 and 24 <= hh_ <= 100 and ww_ > 1.4 * hh_):
                continue
            if cv2.contourArea(cnt) < 0.75 * ww_ * hh_:
                continue
            m = np.zeros(a.shape, np.uint8)
            cv2.drawContours(m, [cnt], -1, 1, -1)
            m = cv2.erode(m, np.ones((3, 3), np.uint8)).astype(bool)
            if np.median(c[m].min(axis=1)) > 232:
                a[m] = 1.0
    if fill_holes:
        solid = (a > 0.35).astype(np.uint8)
        solid = cv2.dilate(solid, np.ones((3, 3), np.uint8))
        inv = 1 - solid
        n, lab, st, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
        h, w = a.shape
        fill = np.zeros_like(solid)
        for i in range(1, n):
            x, y, ww, hh, area = st[i]
            if (area < min_hole or ww < 180 or hh < 110 or area < 0.6 * ww * hh
                    or x == 0 or y == 0 or x + ww >= w or y + hh >= h):
                continue  # only big, card-shaped interiors
            reg = lab[y:y + hh, x:x + ww] == i
            if c[y:y + hh, x:x + ww][reg].mean() < 232:
                continue  # only fill bright (card-like) interiors
            fill[y:y + hh, x:x + ww][reg] = 1
        # whole cards: closed outline of a large, rectangular solid shape
        closed = cv2.morphologyEx((a > 0.3).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        closed[:175] = 0  # titles sit above the cards; never merge them
        cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            x, y, ww, hh = cv2.boundingRect(cnt)
            if ww < 300 or hh < 160:
                continue
            if cv2.contourArea(cnt) < 0.85 * ww * hh:
                continue
            cv2.drawContours(fill, [cnt], -1, 1, -1)
        fill = cv2.erode(fill, np.ones((3, 3), np.uint8))
        # the pink glow around a card is not the card: trim it, keep the card body
        if fill.any():
            r_, g_, b_ = c[..., 0], c[..., 1], c[..., 2]
            glow = (r_ > 200) & (g_ > 100) & (g_ < 225) & (np.abs(g_ - b_) < 14) & (r_ - g_ > 20)
            body = cv2.morphologyEx((fill.astype(bool) & ~glow).astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
            nb_, lb_, sb_, _ = cv2.connectedComponentsWithStats(body, connectivity=4)
            trimmed = np.zeros_like(fill)
            for j in range(1, nb_):
                if sb_[j, 4] > 40000:
                    comp = (lb_ == j).astype(np.uint8)
                    cn_, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cv2.drawContours(trimmed, cn_, -1, 1, -1)
            fill = trimmed
        a = np.maximum(a, fill.astype(np.float32))
    else:
        fill = None
    if force is not None:
        a = np.maximum(a, force.astype(np.float32))
    rgb = b + diff / np.maximum(a, 1e-3)[..., None]
    rgb = np.where(a[..., None] > 0.01, rgb, c)
    return np.clip(rgb, 0, 255), a, fill


def matte_frame(c, fill_holes=False, outlines=False, return_fill=False):
    """Two passes: the second rebuilds the plate without anything the first
    pass found to be graphics (cards, icons, text and their shadows)."""
    b = background_plate(c)
    _, a, fill = pull_matte(c, b, fill_holes, outlines=outlines)
    ex = cv2.dilate((a > 0.25).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    if fill is not None:
        ex |= cv2.dilate(fill, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    b = background_plate(c, ex)
    rgb, a, _ = pull_matte(c, b, False, force=fill, outlines=outlines)
    if return_fill:
        return rgb, a, b, fill
    return rgb, a, b
