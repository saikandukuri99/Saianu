"""Animated lower third (RGB + alpha) in Solix colours.

Usage:  python3 lower_third.py "Janu Jethani" "AI Product Innovation & Platform Leader at Accenture" OUT_BASENAME [--reel]
Writes OUT_BASENAME.mov (QuickTime Animation, RGB+Alpha, 1920x1080 or 1080x1920 with --reel, 30 fps)
The title wraps automatically; use '|' to force line breaks. Add --center to centre it in the frame.
and OUT_BASENAME.png (full-frame still with alpha).
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REEL = "--reel" in sys.argv          # 1080x1920 vertical (Instagram/YouTube Reels, Shorts)
CENTER = "--center" in sys.argv      # whole graphic centred in frame, equal-width plates, centred text
args = [a for a in sys.argv[1:] if a not in ("--reel", "--center")]
W, H, FPS = (1080, 1920, 30) if REEL else (1920, 1080, 30)
DUR = 7.0                      # in ~1.2 s (+ shine), hold, out 0.7 s
RED = (238, 36, 36)            # Solix red  #ee2424
BLUE = (48, 38, 123)           # Solix dark blue/indigo #30267b
BLUE_D = (28, 22, 82)
CYAN = (0, 136, 207)           # Solix brand blue #0088cf
WHITE = (255, 255, 255)
F = "/usr/share/fonts/opentype/inter/"

name = args[0] if len(args) > 0 else "Janu Jethani"
title = args[1] if len(args) > 1 else "AI Product Innovation & Platform Leader at Accenture"
out = args[2] if len(args) > 2 else "lower_third"

f_name = ImageFont.truetype(F + "InterDisplay-Bold.otf", 66 if REEL else 58)
f_title = ImageFont.truetype(F + "Inter-Medium.otf", 36 if REEL else 30)

# ---- layout ----
X0, BAR = (64, 12) if REEL else (110, 12)   # left edge, red accent bar width
PADX = 30 if REEL else 34
MAXW = W - 2 * X0 - BAR - 6                 # widest a plate may be


def wrap(txt, font, maxw):
    """Split on '|' if given, otherwise word-wrap to fit maxw."""
    if "|" in txt:
        return [l.strip() for l in txt.split("|")]
    lines, cur = [], ""
    for w_ in txt.split():
        trial = (cur + " " + w_).strip()
        if font.getlength(trial) + 2 * PADX <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w_
    return lines + [cur]


title_lines = wrap(title, f_title, MAXW)
LINE_H = int(f_title.size * 1.32)
NAME_H = 104 if REEL else 92
TITLE_H = LINE_H * len(title_lines) + (26 if REEL else 16)
GAP = 0
nb = f_name.getbbox(name)
NAME_W = max(nb[2] - nb[0] + 2 * PADX + 8, 420)
TITLE_W = int(max(f_title.getlength(l) for l in title_lines) + 2 * PADX)
# Reels: sit above the caption/UI zone at the bottom of the screen
Y_TITLE_BOTTOM = 1500 if REEL else 960
Y_TITLE = Y_TITLE_BOTTOM - TITLE_H
Y_NAME = Y_TITLE - GAP - NAME_H
if CENTER:
    NAME_W = TITLE_W = max(NAME_W, TITLE_W)
    X0 = (W - (BAR + 6 + NAME_W)) // 2
    Y_NAME = (H - (NAME_H + GAP + TITLE_H)) // 2
    Y_TITLE = Y_NAME + NAME_H + GAP
    Y_TITLE_BOTTOM = Y_TITLE + TITLE_H
PX = X0 + BAR + 6                 # plates start right of the bar


def ease_out(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3
def ease_in(t): t = min(max(t, 0), 1); return t ** 3
def seg(t, a, b): return (t - a) / (b - a)


def plate(w, h, top, bot):
    """Vertical gradient plate with a soft top highlight."""
    g = np.linspace(0, 1, h)[:, None, None]
    c = np.array(top)[None, None] * (1 - g) + np.array(bot)[None, None] * g
    a = np.full((h, w, 1), 255)
    img = np.concatenate([np.broadcast_to(c, (h, w, 3)), a], 2).astype(np.uint8)
    im = Image.fromarray(img, "RGBA")
    d = ImageDraw.Draw(im)
    d.line([(0, 0), (w, 0)], fill=(255, 255, 255, 50), width=2)
    return im


name_plate = plate(NAME_W, NAME_H, (62, 50, 150), BLUE_D)
title_plate = plate(TITLE_W, TITLE_H, (246, 52, 52), (206, 26, 26))


def text_layer(lines, font, w, h, color, line_h=None):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if line_h is None:
        bb = font.getbbox(lines[0])
        x = (w - 8 - font.getlength(lines[0])) / 2 if CENTER else PADX
        d.text((x, (h - (bb[3] - bb[1])) // 2 - bb[1]), lines[0], font=font, fill=color + (255,))
        return im
    asc, desc = font.getmetrics()
    y0 = (h - line_h * len(lines)) // 2 + (line_h - asc - desc) // 2
    for i, l in enumerate(lines):
        x = (w - font.getlength(l)) / 2 if CENTER else PADX
        d.text((x, y0 + i * line_h), l, font=font, fill=color + (255,))
    return im


name_txt = text_layer([name], f_name, NAME_W, NAME_H, WHITE)
title_txt = text_layer(title_lines, f_title, TITLE_W, TITLE_H, WHITE, LINE_H)


def frame(t):
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out_t = DUR - 0.7
    o = ease_in(seg(t, out_t, DUR))            # 0 -> 1 during the exit

    # red accent bar grows from its centre
    total_h = NAME_H + GAP + TITLE_H
    bh = int(total_h * ease_out(seg(t, 0.0, 0.35)) * (1 - ease_in(seg(t, out_t + 0.35, DUR))))
    if bh > 0:
        cy = Y_NAME + total_h // 2
        ImageDraw.Draw(fr).rectangle([X0, cy - bh // 2, X0 + BAR - 1, cy - bh // 2 + bh], fill=RED + (255,))

    # plates wipe right out of the bar; on exit they wipe back in
    for pl, tx, y, a, b, ta, tb_, oa in (
        (name_plate, name_txt, Y_NAME, 0.18, 0.80, 0.45, 1.00, 0.0),
        (title_plate, title_txt, Y_TITLE, 0.35, 0.95, 0.65, 1.20, 0.08),
    ):
        w = pl.width
        vis = ease_out(seg(t, a, b)) * (1 - ease_in(seg(t, out_t + oa, out_t + oa + 0.5)))
        cw = int(w * vis)
        if cw <= 0:
            continue
        layer = pl.copy()
        # text slides in from the left inside the plate and fades
        k = ease_out(seg(t, ta, tb_)) * (1 - ease_in(seg(t, out_t, out_t + 0.3)))
        if k > 0:
            tl = tx.copy()
            al = tl.getchannel("A").point(lambda v: int(v * k))
            tl.putalpha(al)
            layer.alpha_composite(tl, (int(-40 * (1 - k)), 0))
        layer = layer.crop((w - cw, 0, w, pl.height))   # reveal: content travels with the edge
        fr.alpha_composite(layer, (PX, y))
        if pl is name_plate:
            d = ImageDraw.Draw(fr)
            # #0088cf tab riding the leading edge of the name plate
            d.rectangle([PX + cw - 8, y, PX + cw - 1, y + pl.height - 1], fill=CYAN + (255,))

    # light shine sweeping across both plates once they are in
    st = seg(t, 1.25, 2.0)
    if 0 < st < 1:
        x1, y1 = PX, Y_NAME
        x2, y2 = PX + max(NAME_W, TITLE_W) + 40, Y_TITLE_BOTTOM
        a = np.asarray(fr.crop((x1, y1, x2, y2))).astype(np.float32)
        hh, ww = a.shape[:2]
        xx, yy = np.meshgrid(np.arange(ww), np.arange(hh))
        pos = -200 + (ww + 400) * ease_out(st)
        band = np.clip(1 - np.abs(xx + 0.45 * yy - pos) / 70, 0, 1) * 0.35
        band *= a[..., 3] / 255
        a[..., :3] += (255 - a[..., :3]) * band[..., None]
        fr.paste(Image.fromarray(a.astype(np.uint8), "RGBA"), (x1, y1))
    return fr


def main():
    n = int(DUR * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", "-pix_fmt", "argb", out + ".mov"], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    frame(3.0).save(out + ".png")


if __name__ == "__main__":
    main()
