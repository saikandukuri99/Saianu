"""EAI Healthcare: apply only the two approved edits to the finished video and
export it (1080p or 4K). Everything else (visuals, VO, music) passes through.

1. Unified Governance: the Revenue Cycle Intelligence rupee icon becomes a
   rising-graph icon for the whole scene, including the slide-in and the
   fade-out (no rupee flash at the end).
2. Six Pillars: the diagram is the supplied artwork in its own colours, with
   AI Clinical Intelligence and Intelligent Imaging & Radiology swapped.

usage: python3 hc_final.py VIDEO ANALYSIS_JSON OUT.mp4 [WIDTHxHEIGHT]
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hc_alpha import PILLAR_ZONE, _trend_icon, read_frames, swap_rupee  # noqa: E402
from hc_matte import background_plate, degrid, matte_frame  # noqa: E402
from hc_pillars import Pillars  # noqa: E402

FPS = 30
GOV, PIL = 2, 3          # scene indexes
ICON_BOX = (1360, 495, 1490, 625)


class IconFix:
    """Fixed-position glyph swap for the settled Revenue Cycle icon."""

    def __init__(self, ref):
        x0, y0, x1, y1 = ICON_BOX
        roi = ref[y0:y1, x0:x1]
        r, g, b = roi[..., 0], roi[..., 1], roi[..., 2]
        orange = (r - b > 120) & (g > 60) & (g < 175) & (r > 150)
        ys, xs = np.nonzero(orange)
        self.cy, self.cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
        self.rad = (ys.max() - ys.min()) / 2
        yy, xx = np.mgrid[0:roi.shape[0], 0:roi.shape[1]]
        d = np.hypot(yy - self.cy, xx - self.cx)
        self.inner = d < self.rad * 0.72
        self.ann = (d > self.rad * 0.55) & (d < self.rad * 0.85)
        self.orange = np.median(roi[self.ann], axis=0)
        glyph = self.inner & (g > self.orange[1] + 18)
        self.mask = cv2.dilate(glyph.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & self.inner
        size = int(round(self.rad * 1.08))
        self.icon = _trend_icon(size)
        self.gy, self.gx = int(round(self.cy - size / 2)), int(round(self.cx - size / 2))

        x0, y0, x1, y1 = ICON_BOX
        plate = background_plate(ref)
        self.templ = (ref[y0:y1, x0:x1] - plate[y0:y1, x0:x1])[int(self.cy - self.rad):int(self.cy + self.rad),
                                                               int(self.cx - self.rad):int(self.cx + self.rad)]

    def locate(self, c):
        """Horizontal offset of the (possibly sliding, fading) icon vs. the settled one."""
        x0, y0, x1, y1 = ICON_BOX
        plate = background_plate(c)
        r = int(self.rad)
        band = (c - plate)[int(y0 + self.cy) - r:int(y0 + self.cy) + r, x0 - 120:x1 + 160]
        res = cv2.matchTemplate(band.astype(np.float32), self.templ.astype(np.float32), cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(res)
        dx = (x0 - 120 + loc[0]) - (x0 + int(self.cx - self.rad))
        return int(dx), score

    def apply(self, c, dx=0):
        if dx:
            sh = np.roll(c, -dx, axis=1)            # bring the icon to its settled place
            out = self.apply(sh, 0)
            x0, y0, x1, y1 = ICON_BOX
            res = c.copy()
            res[y0:y1, x0 + dx:x1 + dx] = out[y0:y1, x0:x1]
            return res
        x0, y0, x1, y1 = ICON_BOX
        roi = c[y0:y1, x0:x1].copy()
        ring = self.ann & ~self.mask
        circ = np.median(roi[ring], axis=0)
        bg = background_plate(c)[int(y0 + self.cy), int(x0 + self.cx)]
        den = bg - self.orange
        o = float(np.clip(np.dot(bg - circ, den) / max(np.dot(den, den), 1.0), 0, 1))
        if o < 0.02:
            return c
        roi[self.mask] = circ                       # remove the rupee
        s = self.icon.shape[0]
        sub = roi[self.gy:self.gy + s, self.gx:self.gx + s]
        sub += self.icon[: sub.shape[0], : sub.shape[1], None] * o * (255.0 - self.orange)
        out = c.copy()
        out[y0:y1, x0:x1] = np.clip(roi, 0, 255)
        return out


def main():
    video, ana_path, out = sys.argv[1:4]
    size = sys.argv[4] if len(sys.argv) > 4 else "3840x2160"
    W, H = map(int, size.split("x"))
    ana = json.load(open(ana_path))
    cuts = ana["cuts"]
    fades = ana["fades"]
    pfade = fades[str(PIL)] if str(PIL) in fades else fades[PIL]
    pillars = Pillars(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets_hc", "six_pillars.png"),
                      original=True)
    ref = None
    for k, fr in enumerate(read_frames(video)):
        if k == int(16.0 * FPS):
            ref = fr.astype(np.float32)
            break
    fix = IconFix(ref)
    settle = int(14.45 * FPS)

    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS),
        "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a", "-vf", f"scale={W}:{H}:flags=lanczos",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-c:a", "copy", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for k, fr in enumerate(read_frames(video)):
        if cuts[GOV] <= k < cuts[GOV + 1]:
            c = fr.astype(np.float32)
            if k < settle:
                dx, score = fix.locate(c)
                if score > 0.45:
                    c = fix.apply(c, dx)
            else:
                c = fix.apply(c)
            fr = np.clip(c, 0, 255).astype(np.uint8)
        elif cuts[PIL] <= k < cuts[PIL + 1]:
            t = k / FPS
            o = pfade[k - cuts[PIL]]
            c = degrid(fr.astype(np.float32))
            _, _, b = matte_frame(c)
            y0, y1 = PILLAR_ZONE
            pm = pillars.render(t) * (o if t > 31.5 else 1.0)
            new = pm[..., :3] + b * (1 - pm[..., 3:4])
            zone = fr.astype(np.float32).copy()
            zone[y0:y1] = new[y0:y1]
            # soft seam at the top/bottom of the replaced band
            for i in range(12):
                w = (i + 1) / 13
                zone[y0 + i] = fr[y0 + i] * (1 - w) + new[y0 + i] * w
                zone[y1 - 1 - i] = fr[y1 - 1 - i] * (1 - w) + new[y1 - 1 - i] * w
            fr = np.clip(zone, 0, 255).astype(np.uint8)
        enc.stdin.write(fr.tobytes())
        if k % 300 == 0:
            print("frame", k, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
