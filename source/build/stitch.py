# Stitch a downward-scrolling screen recording segment into one tall page image.
import sys, subprocess, numpy as np
from PIL import Image
f, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
p = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",f],capture_output=True,text=True).stdout.strip().split(",")
w, h = int(p[0]), int(p[1])
raw = subprocess.run(["ffmpeg","-nostdin","-v","error","-ss",str(t0),"-t",str(t1-t0),"-i",f,"-vf","fps=15","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr = np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
g = fr.astype(float).mean(axis=3)[:, :, w//8: w*7//8]
# canvas grows; each frame is matched against the canvas built so far, only new rows are appended
can = [fr[0]]
canH = h
cang = g[0].copy()
last = 0
for i in range(1, len(fr)):
    best = (1e18, last)
    for s in range(last, min(last + 220, canH)):
        ov = canH - s
        if ov < h // 3:
            break
        d = cang[s:s + min(ov, h)] - g[i][:min(ov, h)]
        e = (d * d).mean()
        if e < best[0]:
            best = (e, s)
    s = best[1]; last = s
    new = s + h - canH
    if new > 0:
        can.append(fr[i][h - new:])
        cang = np.concatenate([cang, g[i][h - new:]])
        canH += new
img = np.concatenate(can)
Image.fromarray(img).save(out)
print(out, w, canH, "scroll", canH - h)
