# Keep the artwork's own dark background, masked to a soft-edged circle (medallion
# for the white theme).
import sys, numpy as np
from PIL import Image
src, dst, scale = sys.argv[1], sys.argv[2], int(sys.argv[3])
crop = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
im = Image.open(src).convert('RGB')
if crop: im = im.crop(crop)
W, H = im.size
yy, xx = np.mgrid[0:H, 0:W]
R = min(W, H) / 2
r = np.hypot(xx - W / 2, yy - H / 2) / R
a = np.clip((1.0 - r) / .1, 0, 1)
out = np.dstack([np.asarray(im), (a * 255).astype(np.uint8)])
Image.fromarray(out, 'RGBA').resize((W * scale, H * scale), Image.LANCZOS).save(dst)
