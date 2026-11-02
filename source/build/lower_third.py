"""Animated lower third (RGB + alpha) in Solix colours.

Usage:  python3 lower_third.py "Janu Jethani" "AI Product Innovation & Platform Leader at Accenture" OUT_BASENAME
Writes OUT_BASENAME.mov (QuickTime Animation, RGB+Alpha, 1920x1080, 30 fps)
and OUT_BASENAME.png (full-frame still with alpha).
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
DUR = 7.0                      # in ~1.2 s (+ shine), hold, out 0.7 s
RED = (238, 36, 36)            # Solix red  #ee2424
BLUE = (48, 38, 123)           # Solix dark blue/indigo #30267b
BLUE_D = (28, 22, 82)
CYAN = (0, 136, 207)           # Solix brand blue #0088cf
WHITE = (255, 255, 255)
F = "/usr/share/fonts/opentype/inter/"

name = sys.argv[1] if len(sys.argv) > 1 else "Janu Jethani"
title = sys.argv[2] if len(sys.argv) > 2 else "AI Product Innovation & Platform Leader at Accenture"
out = sys.argv[3] if len(sys.argv) > 3 else "lower_third"

f_name = ImageFont.truetype(F + "InterDisplay-Bold.otf", 58)
f_title = ImageFont.truetype(F + "Inter-Medium.otf", 30)

# ---- layout ----
X0, BAR = 110, 12                 # left edge, red accent bar width
PADX = 34
NAME_H, TITLE_H, GAP = 92, 58, 0
nb = f_name.getbbox(name); tb = f_title.getbbox(title)
NAME_W = max(nb[2] - nb[0] + 2 * PADX, 460)
TITLE_W = max(tb[2] - tb[0] + 2 * PADX, 300)
Y_TITLE_BOTTOM = 960
Y_TITLE = Y_TITLE_BOTTOM - TITLE_H
Y_NAME = Y_TITLE - GAP - NAME_H
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


def text_layer(txt, font, w, h, color):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bb = font.getbbox(txt)
    y = (h - (bb[3] - bb[1])) // 2 - bb[1]
    ImageDraw.Draw(im).text((PADX, y), txt, font=font, fill=color + (255,))
    return im


name_txt = text_layer(name, f_name, NAME_W, NAME_H, WHITE)
title_txt = text_layer(title, f_title, TITLE_W, TITLE_H, WHITE)


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
            # #0088cf line that races ahead of the plate along its top
            lw = int((w + 40) * ease_out(seg(t, 0.05, 0.55)) * (1 - ease_in(seg(t, out_t, out_t + 0.45))))
            if lw > 0:
                d.rectangle([PX, y - 6, PX + lw, y - 2], fill=CYAN + (255,))

    # light shine sweeping across both plates once they are in
    st = seg(t, 1.25, 2.0)
    if 0 < st < 1:
        x1, y1 = PX, Y_NAME - 6
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
