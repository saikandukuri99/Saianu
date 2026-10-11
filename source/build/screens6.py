# Screen animation engine: browser window, staged block reveal, camera focus, spotlight, cursor.
import math, os
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

B = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/opentype/inter/"


def _runs(mask1d, min_gap, min_len=3):
    idx = np.where(mask1d)[0]
    if len(idx) == 0:
        return []
    runs, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > min_gap:
            if p - s + 1 >= min_len:
                runs.append((s, p + 1))
            s = i
        p = i
    if p - s + 1 >= min_len:
        runs.append((s, p + 1))
    return runs


@lru_cache(None)
def page_bg(img_key):
    im = _img(img_key)
    a = np.asarray(im).reshape(-1, 3)
    border = np.concatenate([np.asarray(im)[:4].reshape(-1, 3), np.asarray(im)[-4:].reshape(-1, 3),
                             np.asarray(im)[:, :4].reshape(-1, 3), np.asarray(im)[:, -4:].reshape(-1, 3)])
    vals, cnt = np.unique(border, axis=0, return_counts=True)
    return tuple(int(v) for v in vals[cnt.argmax()])


_IMG = {}


def register(key, im):
    _IMG[key] = im.convert("RGB")


def _img(key):
    return _IMG[key]


@lru_cache(None)
def blocks(key):
    """Detect content blocks: horizontal bands split into column segments."""
    im = _img(key)
    a = np.asarray(im).astype(int)
    bg = np.array(page_bg(key))
    diff = np.abs(a - bg).sum(axis=2) > 70
    H, W = diff.shape
    out = []
    bands = _runs(diff.mean(axis=1) > 0.002, max(10, H // 60))
    for (y0, y1) in bands:
        sub = diff[y0:y1]
        segs = _runs(sub.mean(axis=0) > 0.004, max(22, W // 45))
        for (x0, x1) in segs:
            sub2 = diff[y0:y1, x0:x1]
            rows = np.where(sub2.any(axis=1))[0]
            if len(rows) == 0:
                continue
            yy0, yy1 = y0 + rows[0], y0 + rows[-1] + 1
            if (x1 - x0) * (yy1 - yy0) < 400:
                continue
            out.append((int(x0), int(yy0), int(x1), int(yy1)))
    # merge tiny blocks into neighbours by expanding a little padding
    pad = 14
    res = [(max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)) for x0, y0, x1, y1 in out]
    res.sort(key=lambda b: (b[1] // 40, b[0]))
    return tuple(res)


def focus_blocks(key, k=3):
    bl = blocks(key)
    im = _img(key)
    W, H = im.size
    cand = [b for b in bl if (b[2] - b[0]) * (b[3] - b[1]) > 0.03 * W * H and (b[2] - b[0]) < 0.9 * W]
    if not cand:
        cand = sorted(bl, key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))
    cand = sorted(cand, key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))[:k]
    return sorted(cand, key=lambda b: (b[1] // 60, b[0]))


def ease(p):
    p = max(0.0, min(1.0, p)); return 1 - (1 - p) ** 3


def eio(p):
    p = max(0.0, min(1.0, p)); return p * p * (3 - 2 * p)


def page_frame(key, lt, stagger=0.07, dur=0.5, start=0.15):
    """Page with blocks revealed in sequence (fade + rise)."""
    im = _img(key)
    bg = page_bg(key)
    bl = blocks(key)
    total_in = start + stagger * len(bl) + dur
    if lt >= total_in:
        return im
    can = Image.new("RGB", im.size, bg)
    for i, (x0, y0, x1, y1) in enumerate(bl):
        p = ease((lt - start - stagger * i) / dur)
        if p <= 0:
            continue
        crop = im.crop((x0, y0, x1, y1))
        dy = int((1 - p) * 18)
        if p < 0.999:
            m = Image.new("L", crop.size, int(255 * p))
            can.paste(crop, (x0, y0 + dy), m)
        else:
            can.paste(crop, (x0, y0))
    return can


@lru_cache(None)
def _font(name, size):
    return ImageFont.truetype(FD + name, size)


@lru_cache(None)
def window_bar(w, url, h=44):
    bar = Image.new("RGB", (w, h), (243, 244, 248))
    d = ImageDraw.Draw(bar)
    for i, col in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        d.ellipse((18 + i * 22, h / 2 - 6, 30 + i * 22, h / 2 + 6), fill=col)
    uw = min(w - 220, 640)
    ux = (w - uw) // 2
    d.rounded_rectangle((ux, 9, ux + uw, h - 9), 8, fill=(255, 255, 255), outline=(226, 228, 236))
    f = _font("Inter-Medium.otf", 14)
    # lock
    d.rounded_rectangle((ux + 14, h / 2 - 2, ux + 24, h / 2 + 6), 2, fill=(120, 126, 140))
    d.arc((ux + 15, h / 2 - 8, ux + 23, h / 2 + 2), 180, 360, fill=(120, 126, 140), width=2)
    d.text((ux + 34, h / 2), url, font=f, fill=(70, 76, 92), anchor="lm")
    d.line((0, h - 1, w, h - 1), fill=(226, 228, 236))
    return bar


@lru_cache(None)
def rmask(w, h, r):
    ss = 3
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


@lru_cache(None)
def cursor_img(scale=1.0):
    s = 4
    pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    im = Image.new("RGBA", (40 * s, 48 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sh = [(x * s + 6, y * s + 8) for x, y in pts]
    d.polygon(sh, fill=(0, 0, 0, 70))
    im = im.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(im)
    P = [(x * s + 4, y * s + 4) for x, y in pts]
    d.polygon(P, fill=(20, 20, 30, 255))
    inner = [(x * s * 0.8 + 4 + 3 * s * 0.4, y * s * 0.8 + 4 + 5 * s * 0.4) for x, y in pts]
    d.polygon(inner, fill=(255, 255, 255, 255))
    return im.resize((int(40 * scale), int(48 * scale)), Image.LANCZOS)


def camera_rect(W, H, rect, z):
    """Camera window in page coords centred on rect with zoom z (1 = full page)."""
    cw, ch = W / z, H / z
    cx = (rect[0] + rect[2]) / 2
    cy = (rect[1] + rect[3]) / 2
    x0 = min(max(0, cx - cw / 2), W - cw)
    y0 = min(max(0, cy - ch / 2), H - ch)
    return (x0, y0, x0 + cw, y0 + ch)


def lerp_rect(a, b, p):
    return tuple(a[i] + (b[i] - a[i]) * p for i in range(4))


URLS = {
    "cdp": "solix.com/products/solix-common-data-platform/", "edg": "solix.com/products/enterprise-data-governance/",
    "ecs": "solix.com/products/enterprise-content-services/", "datasense": "solix.com/products/data-sense/",
    "dataask": "solix.com/products/data-ask/", "akg": "solix.com/products/pre-built-akg/", "aiwh": "solix.com/products/ai-warehouse/",
    "agentic": "solix.com/products/agentic/", "appret": "solix.com/products/application-retirement-solution/",
    "datapres": "solix.com/solutions/data-preservation/", "sap": "solix.com/solutions/cloud-data-management-for-sap/",
    "oracle": "solix.com/solutions/oracle-ebusiness-suite/", "mainframe": "solix.com/solutions/ibm-zseries-mainframe/",
    "email": "solix.com/products/email-archiving/", "file": "solix.com/products/file-archiving/",
    "database": "solix.com/products/database-archiving/", "active": "solix.com/solutions/active-archiving/",
    "eaihc": "solix.com", "logos": "solix.com", "analysts": "solix.com", "recog": "solix.com", "filecap": "solix.com/products/file-archiving/",
}

# focus regions as fractions of the page + a short tag label
FOCUS = {
    "datasense": [((0.0, 0.06, 1.0, 0.52), "Connect · Load · Profile · Discover · Context"), ((0.0, 0.5, 1.0, 1.0), "Enrich · Curate · Validate · Publish")],
    "dataask": [((0.52, 0.02, 0.99, 0.62), "One question. One synthesized answer.")],
    "aiwh": [((0.0, 0.2, 0.52, 0.62), "Governed lakehouse & ingestion"), ((0.48, 0.2, 1.0, 0.62), "Quality & ML flow")],
    "agentic": [((0.56, 0.04, 0.99, 0.98), "Is your data truly ready for AI?")],
    "appret": [((0.0, 0.3, 0.52, 0.95), "Legacy decommissioning · Security"), ((0.48, 0.3, 1.0, 0.95), "M&A · AI-readiness migration")],
    "datapres": [((0.47, 0.0, 1.0, 0.92), "From legacy archive to activated intelligence")],
    "sap": [((0.0, 0.42, 0.52, 0.98), "Cloud migration · M&A"), ((0.48, 0.42, 1.0, 0.98), "Security · AI value of SAP data")],
    "oracle": [((0.0, 0.4, 1.0, 0.98), "Why EBS retirement matters")],
    "mainframe": [((0.0, 0.25, 1.0, 1.0), "Mainframe-specific economics")],
    "email": [((0.0, 0.55, 1.0, 1.0), "Cloud-native email archiving")],
    "file": [((0.48, 0.0, 1.0, 0.8), "File-archive economics")],
    "database": [((0.0, 0.28, 0.52, 1.0), "Multi-platform · Referential integrity"), ((0.48, 0.28, 1.0, 1.0), "Governed retention · AI access via AKG")],
    "active": [((0.0, 0.22, 0.52, 1.0), "Compliance-driven minimization"), ((0.48, 0.22, 1.0, 1.0), "Cloud ERP economics")],
    "eaihc": [((0.0, 0.0, 0.5, 1.0), "Warehouse · Governance · Patient 360"), ((0.5, 0.0, 1.0, 1.0), "Imaging · Clinical intelligence · Models")],
    "ecs": [((0.0, 0.3, 0.62, 1.0), "Repository · GenAI · Sharing · Compliance"), ((0.6, 0.25, 1.0, 1.0), "Secure, mobile, governed content")],
    "recog": [((0.33, 0.34, 0.67, 0.67), "Bloor · Strong Challenger"), ((0.0, 0.66, 0.67, 1.0), "Bloor · Strong Innovator")],
}
REVEAL = {"eaihc": "radial", "datasense": "wipe", "agentic": "wipe"}
MAXZ = {}


def make_plan(key, dur):
    """Distribute this screen's focus regions over its time on screen."""
    f = FOCUS.get(key, [])
    W, H = _img(key).size
    t0, slot = 1.5, 2.6
    n = max(0, min(len(f), int((dur - t0 - 0.6) // slot)))
    if n == 0 and f and dur > 3.2:
        n = 1
    plan = []
    for i in range(n):
        (fx0, fy0, fx1, fy1), lab = f[i]
        plan.append((t0 + i * max(slot, (dur - t0 - 0.8) / n), (fx0 * W, fy0 * H, fx1 * W, fy1 * H), lab))
    end = (t0 + n * max(slot, (dur - t0 - 0.8) / n)) if n else None
    return plan, end


def reveal_frame(key, lt):
    mode = REVEAL.get(key, "blocks")
    if mode == "blocks":
        return page_frame(key, lt)
    im = _img(key)
    p = eio((lt - 0.1) / 1.3)
    if p >= 1:
        return im
    can = Image.new("RGB", im.size, page_bg(key))
    W, H = im.size
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    if mode == "wipe":
        x = int(W * p)
        d.rectangle((0, 0, x, H), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(30))
    else:
        r = math.hypot(W, H) / 2 * p
        d.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(30))
    can.paste(im, (0, 0), m)
    return can


@lru_cache(None)
def tag_img(label, accent):
    f = _font("Inter-SemiBold.otf", 16)
    tw = int(f.getlength(label))
    im = Image.new("RGBA", (tw + 44, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw + 43, 33), 17, fill=accent + (255,))
    d.ellipse((12, 12, 22, 22), fill=(255, 255, 255, 255))
    d.text((30, 17), label, font=f, fill=(255, 255, 255), anchor="lm")
    return im


def screen_still(key, lt, w, h, dur=6.0, accent=(238, 36, 36), lowres=False, focus=True):
    bar_h = 44 if h > 300 else 32
    ch = h - bar_h
    src = _img(key)
    SW, SH = src.size
    page = reveal_frame(key, lt)
    th_full = SW * ch / w           # page-space height of the view at zoom 1
    full = (0.0, 0.0, float(SW), th_full)
    plan, end = make_plan(key, dur) if focus else ([], None)
    cam, hl = full, None
    maxz = 1.0 if lowres else 1.22
    for i, (tf, r, lab) in enumerate(plan):
        if lt < tf - 0.7:
            break
        rw, rh = r[2] - r[0], r[3] - r[1]
        z = max(1.0, min(maxz, SW / (rw * 1.12), th_full / (rh * 1.12)))
        tw, th = SW / z, th_full / z
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        x0 = min(max(0, cx - tw / 2), SW - tw)
        y0 = min(max(0, cy - th / 2), max(0, SH - th))
        target = (x0, y0, x0 + tw, y0 + th)
        cam = lerp_rect(cam, target, eio((lt - tf + 0.7) / 0.9))
        if lt >= tf - 0.1:
            hl = (r, ease((lt - tf + 0.1) / 0.45), lab)
    if end is not None and lt >= end - 0.2:
        q = eio((lt - end + 0.2) / 0.9)
        cam = lerp_rect(cam, full, q)
        if q > 0.25:
            hl = None
    x0, y0, x1, y1 = cam
    view = page.crop((int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1))))
    if view.size[1] < int(y1 - y0):
        can = Image.new("RGB", (view.size[0], int(y1 - y0) + 1), page_bg(key))
        can.paste(view, (0, 0)); view = can
    view = view.resize((w, ch), Image.LANCZOS)
    sx, sy = w / (x1 - x0), ch / (y1 - y0)
    cur_target = None
    if hl:
        r, p, lab = hl
        rx0, ry0, rx1, ry1 = (r[0] - x0) * sx, (r[1] - y0) * sy, (r[2] - x0) * sx, (r[3] - y0) * sy
        rx0, ry0 = max(8, rx0), max(8, ry0)
        rx1, ry1 = min(w - 8, rx1), min(ch - 8, ry1)
        from PIL import ImageChops
        ov = Image.new("RGBA", (w, ch), (18, 14, 56, int(48 * p)))
        hole = Image.new("L", (w, ch), 0)
        ImageDraw.Draw(hole).rounded_rectangle((rx0, ry0, rx1, ry1), 12, fill=255)
        ov.putalpha(ImageChops.multiply(ov.getchannel("A"), hole.point(lambda v: 255 - v)))
        view = Image.alpha_composite(view.convert("RGBA"), ov)
        d = ImageDraw.Draw(view)
        d.rounded_rectangle((rx0, ry0, rx1, ry1), 12, outline=accent + (int(255 * p),), width=4)
        tg = tag_img(lab, accent)
        ta = tg.getchannel("A").point(lambda v: int(v * p))
        tx = min(max(8, rx0), w - tg.width - 8)
        ty = ry0 - tg.height - 8 if ry0 - tg.height - 8 > 6 else ry0 + 8
        view.paste(tg, (int(tx), int(ty + (1 - p) * 8)), ta)
        cxp, cyp = (rx0 + rx1) / 2, (ry0 + ry1) / 2
        rp = ease(p * 1.3)
        rr = 8 + 40 * rp
        d.ellipse((cxp - rr, cyp - rr, cxp + rr, cyp + rr), outline=(255, 255, 255, int(220 * (1 - rp))), width=3)
        view = view.convert("RGB")
    win = Image.new("RGB", (w, h), (255, 255, 255))
    win.paste(window_bar(w, URLS.get(key, "solix.com"), bar_h), (0, 0))
    win.paste(view, (0, bar_h))
    # cursor glides to each focus region just before it lights up
    if plan and lt >= plan[0][0] - 1.3:
        pos = (w * 0.9, h * 0.95)
        for i, (tf, r, lab) in enumerate(plan):
            if lt < tf - 1.1:
                break
            tx = ((r[0] + r[2]) / 2 - x0) * sx
            ty = ((r[1] + r[3]) / 2 - y0) * sy + bar_h
            tx, ty = min(max(10, tx), w - 40), min(max(bar_h + 10, ty), h - 50)
            pp = eio((lt - tf + 1.1) / 0.95)
            pos = (pos[0] + (tx - pos[0]) * pp, pos[1] + (ty - pos[1]) * pp)
        ca = ease((lt - plan[0][0] + 1.3) / 0.4)
        if end is not None:
            ca *= 1 - ease((lt - end) / 0.5)
        if ca > 0.01:
            cu = cursor_img(0.9)
            win.paste(cu, (int(pos[0]), int(pos[1])), cu.getchannel("A").point(lambda v: int(v * ca)))
    out = win.convert("RGBA")
    out.putalpha(rmask(w, h, 14))
    return out


def screen_clip(frame_img, key, lt, w, h, zoom_to=1.06):
    url = URLS.get(key, "solix.com")
    bar_h = 44 if h > 300 else 32
    ch = h - bar_h
    im = frame_img
    sc = w / im.width
    vis_h = ch / sc
    z = 1 + (zoom_to - 1) * eio(lt / 10)
    cw = im.width / z
    chh = cw * ch / w
    x0 = (im.width - cw) / 2
    y0 = 0
    if chh > im.height:
        chh = im.height; cw = chh * w / ch; x0 = (im.width - cw) / 2
    view = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((w, ch), Image.LANCZOS)
    win = Image.new("RGB", (w, h), (255, 255, 255))
    win.paste(window_bar(w, url, bar_h), (0, 0))
    win.paste(view, (0, bar_h))
    out = win.convert("RGBA")
    out.putalpha(rmask(w, h, 14))
    return out


def screen_scroll(key, lt, w, h, dur=6.0, hold=0.8):
    """Tall stitched page: camera glides strictly top -> bottom."""
    bar_h = 44 if h > 300 else 32
    ch = h - bar_h
    src = _img(key)
    SW, SH = src.size
    vh = SW * ch / w
    maxy = max(0.0, SH - vh)
    p = eio((lt - hold) / max(0.5, dur - hold - 0.4))
    y0 = maxy * p
    view = src.crop((0, int(y0), SW, int(y0 + vh))).resize((w, ch), Image.LANCZOS)
    win = Image.new("RGB", (w, h), (255, 255, 255))
    win.paste(window_bar(w, URLS.get(key, "solix.com"), bar_h), (0, 0))
    win.paste(view, (0, bar_h))
    out = win.convert("RGBA")
    out.putalpha(rmask(w, h, 14))
    return out
