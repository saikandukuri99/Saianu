# Estimate cumulative vertical scroll per frame for a screen recording (row-profile matching).
import sys, subprocess, numpy as np
f = sys.argv[1]
W, H = 320, 0
p = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",f],capture_output=True,text=True).stdout.strip().split(",")
w0,h0 = int(p[0]), int(p[1]); H = int(h0*W/w0)//2*2
raw = subprocess.run(["ffmpeg","-nostdin","-v","error","-i",f,"-vf",f"fps=10,scale={W}:{H},format=gray","-f","rawvideo","-"],capture_output=True).stdout
fr = np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(float)
pos=[0.0]
for i in range(1,len(fr)):
    a=fr[i-1].mean(1); b=fr[i].mean(1)
    best=(1e18,0)
    for s in range(-60,61):
        if s>=0: d=a[s:]-b[:H-s] if s else a-b
        else: d=a[:H+s]-b[-s:]
        e=(d*d).mean()
        if e<best[0]: best=(e,s)
    pos.append(pos[-1]+best[1]*h0/H)
pos=np.array(pos)
print("dur",len(fr)/10)
for t in range(0,len(pos),5): print(f"{t/10:5.1f}s y={pos[t]:7.0f}")
