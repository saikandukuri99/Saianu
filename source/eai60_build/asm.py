import soundfile as sf, numpy as np, json, subprocess
SR=24000
gaps={1:0.55,2:0.35,3:0.5,4:0.3,5:0.3,6:0.3,7:0.3,8:0.3,9:0.3,10:0.3,11:0.5}
t=0.4; out=[np.zeros(int(0.4*SR))]; tl=[]
for i in range(1,13):
    subprocess.run(["ffmpeg","-y","-v","error","-i",f"vo/L{i:02d}.wav","-af","silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,afade=t=in:d=0.01","-ar",str(SR),f"vo/t{i:02d}.wav"],check=True)
    a,_=sf.read(f"vo/t{i:02d}.wav"); d=len(a)/SR
    tl.append({"line":i,"start":round(t,2),"end":round(t+d,2)}); out.append(a)
    g=gaps.get(i,0); out.append(np.zeros(int(g*SR))); t+=d+g
y=np.concatenate(out+[np.zeros(int(0.5*SR))]); sf.write("vo/raw.wav",y,SR)
json.dump(tl,open("vo/timeline.json","w"),indent=1); print(tl, len(y)/SR)
