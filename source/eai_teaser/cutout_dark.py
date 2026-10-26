# Lift a glowing graphic off a flat dark background (un-mix against the bg colour),
# so it composites cleanly on both the dark and the white theme.
import sys, numpy as np
from PIL import Image
src, dst, scale = sys.argv[1], sys.argv[2], int(sys.argv[3])
crop = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
im = Image.open(src).convert('RGB')
if crop: im = im.crop(crop)
c = np.asarray(im).astype(np.float64)
H, W, _ = c.shape
edge = np.concatenate([c[:3].reshape(-1, 3), c[-3:].reshape(-1, 3), c[:, :3].reshape(-1, 3), c[:, -3:].reshape(-1, 3)])
B = np.median(edge, 0)
a = np.clip(((c - B) / (255 - B)).max(2), 0, 1)
a = np.clip(a * 1.25, 0, 1)
f = B + (c - B) / np.maximum(a[..., None], 1e-3)
# soft circular fade at the borders so nothing looks boxed in
yy, xx = np.mgrid[0:H, 0:W]
r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
a *= np.clip((1.02 - r) / .12, 0, 1)
out = np.dstack([np.clip(f, 0, 255), a * 255]).astype(np.uint8)
Image.fromarray(out, 'RGBA').resize((W * scale, H * scale), Image.LANCZOS).save(dst)
print(B, W * scale, H * scale)
