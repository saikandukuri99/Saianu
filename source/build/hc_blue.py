"""v13 white-ECG video -> same video on a Solix-blue (#0088cf) background.

Only the background changes: white areas become Solix blue; translucent
parts (glows, particles, the ECG line) are re-lit smoothly from white to
blue; solid elements and white cards/screenshots stay exactly as they are.
Audio is copied unchanged.

usage: python3 hc_blue.py VIDEO OUT.mp4 [test_frames]
"""
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hc_alpha import read_frames  # noqa: E402
from hc_matte import matte_frame  # noqa: E402

FPS = 30
BLUE = np.float32([0x00, 0x88, 0xcf])


def process(fr):
    c = fr.astype(np.float32)
    _, a, b, fill = matte_frame(c, True, True, return_fill=True)
    if fill is not None:
        a = np.maximum(a, cv2.GaussianBlur(fill.astype(np.float32), (0, 0), 1.0))
    a = cv2.GaussianBlur(a, (0, 0), 0.8)
    w = np.clip((a - 0.86) / 0.12, 0, 1)
    w = (w * w * (3 - 2 * w))[..., None]
    mapped = c * (BLUE / np.maximum(b, 1.0))
    out = w * c + (1 - w) * mapped
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    video, out = sys.argv[1:3]
    test = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    if test:
        for k, fr in enumerate(read_frames(video)):
            if k in test:
                cv2.imwrite(f"{out}_{k}.png", process(fr)[:, :, ::-1])
            if k > max(test):
                break
        return
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS),
        "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, img in enumerate(pool.imap(process, read_frames(video), chunksize=2)):
            enc.stdin.write(img.tobytes())
            if k % 300 == 0:
                print("frame", k, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
