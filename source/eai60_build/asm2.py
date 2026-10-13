import soundfile as sf, numpy as np, json, subprocess
SR=24000;S=json.load(open("sents.json"))
gaps={1:.55,2:.35,3:.5,4:.3,5:.3,6:.3,7:.3,8:.3,9:.3,10:.3,11:.5}
t=0.4;out=[np.zeros(int(.4*SR))];anch=[]
for i,(txt,oa,ob,ln) in enumerate(S):
    subprocess.run(["ffmpeg","-y","-v","error","-i",f"vof/3/s{i:02d}.wav","-af","silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,afade=t=in:d=0.01","-ar",str(SR),f"vof/t{i:02d}.wav"],check=True)
    a,_=sf.read(f"vof/t{i:02d}.wav");d=len(a)/SR
    anch.append(dict(text=txt,line=ln,old_a=oa,old_b=ob,new_a=round(t,3),new_b=round(t+d,3)));out.append(a)
    nxt=S[i+1][3] if i+1<len(S) else None
    g=0.22 if nxt==ln else gaps.get(ln,0)
    out.append(np.zeros(int(g*SR)));t+=d+g
y=np.concatenate(out+[np.zeros(int(.5*SR))]);sf.write("vof/raw.wav",y,SR)
json.dump(anch,open("anchors.json","w"),indent=1);print("total",len(y)/SR,"last end",anch[-1]["new_b"])
