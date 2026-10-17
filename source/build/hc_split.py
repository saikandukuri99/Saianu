"""Split alpha .mov clips into back-to-back pieces under GitHub's 100 MB limit
(lossless: QuickTime Animation re-encode of exact frame ranges).

usage: python3 hc_split.py ALPHA_DIR [limit_mb]
"""
import glob
import math
import os
import subprocess
import sys


def frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_frames", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", path], capture_output=True, text=True)
    return int(out.stdout.strip())


def main():
    d = sys.argv[1]
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 92.0
    for mov in sorted(glob.glob(f"{d}/*.mov")):
        if "_piece" in mov:
            continue
        size = os.path.getsize(mov) / 1e6
        if size <= limit:
            continue
        n = frames(mov)
        parts = math.ceil(size / limit * 1.08)
        per = math.ceil(n / parts)
        base = mov[:-4]
        for p in range(parts):
            a, b = p * per, min(n, (p + 1) * per) - 1
            if a > b:
                break
            out = f"{base}_piece{p + 1}.mov"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mov, "-vf",
                            f"select=between(n\\,{a}\\,{b}),setpts=N/30/TB", "-r", "30",
                            "-c:v", "qtrle", "-pix_fmt", "argb", out], check=True)
            print(os.path.basename(out), b - a + 1, "frames", round(os.path.getsize(out) / 1e6, 1), "MB")
        os.remove(mov)


if __name__ == "__main__":
    main()
