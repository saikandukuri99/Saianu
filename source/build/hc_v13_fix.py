"""v13 (white ECG) video: Revenue Cycle Intelligence rupee -> rising-graph icon,
and the audio replaced by the previous female voice-over + hyper-beat music.
Every other pixel is left exactly as it is (only the icon disc is touched).

usage: python3 hc_v13_fix.py VIDEO AUDIO.wav OUT.mp4 [test_frames]
"""
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hc_alpha import _trend_icon, read_frames  # noqa: E402

FPS = 30
T0, T1 = 13.8, 19.6                  # Unified Governance scene, icon visible
BAND = (1330, 490, 1520, 630)        # x0, y0, x1, y1 search band
K = np.float32([249, 113, 20])       # icon orange


def fix(fr):
    x0, y0, x1, y1 = BAND
    roi = fr[y0:y1, x0:x1].astype(np.float32)
    o = np.clip((255.0 - roi[..., 2]) / (255.0 - K[2]), 0, 1) * (roi[..., 0] - roi[..., 2] > 6)
    if o.max() < 0.04:
        return fr
    m = cv2.morphologyEx((o > 0.5 * o.max()).astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2:
        return fr
    i = 1 + int(np.argmax(st[1:, 4]))
    bx, by, bw, bh, area = st[i]
    if area < 150 or not (0.75 < bw / max(bh, 1) < 1.33):
        return fr
    cx, cy = bx + bw / 2, by + bh / 2
    r = max(bw, bh) / 2
    yy, xx = np.mgrid[0:roi.shape[0], 0:roi.shape[1]]
    d = np.hypot(xx - cx, yy - cy)
    inner = d < r * 0.74
    ring = (d > r * 0.58) & (d < r * 0.85)
    omed = np.median(o[ring])
    glyph = inner & (o < 0.8 * omed)
    glyph = cv2.dilate(glyph.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (d < r * 0.78)
    col = np.median(roi[ring & ~glyph], axis=0)
    roi[glyph] = col
    size = int(round(r * 1.08))
    ic = _trend_icon(size)[..., None]
    gx, gy = int(round(cx - size / 2)), int(round(cy - size / 2))
    sub = roi[gy:gy + size, gx:gx + size]
    icw = ic[:sub.shape[0], :sub.shape[1]]
    sub[:] = sub * (1 - icw) + 255.0 * icw
    out = fr.copy()
    out[y0:y1, x0:x1] = np.clip(roi, 0, 255).astype(np.uint8)
    return out


def main():
    video, audio, out = sys.argv[1:4]
    test = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
    if test:
        for k, fr in enumerate(read_frames(video)):
            if k in test:
                f = fix(fr) if T0 * FPS <= k <= T1 * FPS else fr
                cv2.imwrite(f"{out}_{k}.png", np.concatenate([fr, f], 1)[480:640, 1300:1900][:, :, ::-1]
                            if False else np.concatenate([fr[480:640, 1300:1900], f[480:640, 1300:1900]], 0)[:, :, ::-1])
            if k > max(test):
                break
        return
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS),
        "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    for k, fr in enumerate(read_frames(video)):
        if T0 * FPS <= k <= T1 * FPS:
            fr = fix(fr)
        enc.stdin.write(fr.tobytes())
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
