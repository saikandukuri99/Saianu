# Cut the AI hub graphic out of its baked white/checkerboard background.
# alpha = how far each pixel is pulled below the light background; small enclosed
# light areas (the "AI" letters, robot face, highlights) stay opaque.
import sys, numpy as np
from PIL import Image
from scipy import ndimage
src, dst = sys.argv[1], sys.argv[2]
c = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
H, W, _ = c.shape
# background: brightest neighbourhood value per pixel (checker cells are near white)
bg = ndimage.maximum_filter(c.max(2), size=25)
bg = np.maximum(bg, 225)[..., None]
a = np.clip(((bg - c) / bg).max(2) * 1.15, 0, 1)
# keep enclosed light details opaque: small low-alpha islands not touching the border
low = a < .5
lab, n = ndimage.label(low)
sizes = ndimage.sum(low, lab, range(1, n + 1))
border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
fill = np.zeros_like(low)
for i, s in enumerate(sizes, 1):
    if i not in border and s < 0.012 * H * W:
        isl = lab == i
        ring = ndimage.binary_dilation(isl, iterations=2) & ~isl
        if a[ring].mean() > .8:          # enclosed by solid graphic, not by soft glow
            fill |= isl
fill = ndimage.binary_dilation(fill, iterations=1)
a = np.where(fill, 1.0, a)
# un-premultiply against the light background
f = np.where(a[..., None] > 1e-3, (c - (1 - a[..., None]) * bg) / np.maximum(a[..., None], 1e-3), 0)
f = np.where(fill[..., None], c, f)
# checkerboard leftovers are colourless: fade out low-saturation partial pixels
sat = f.max(2) - f.min(2)
grey = (~fill) & (a < .85) & (sat < 60)
a = np.where(grey, a * np.clip(sat / 60, 0, 1) ** 2, a)
out = np.dstack([np.clip(f, 0, 255), a * 255]).astype(np.uint8)
im = Image.fromarray(out, 'RGBA')
im = im.resize((W * 2, H * 2), Image.LANCZOS)
im.save(dst)
print(im.size)
