import soundfile as sf, json, numpy as np, sys
sys.path.insert(0,'.')
from lines import L
from kokoro_onnx import Kokoro
k=Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
V="am_michael"
def trim(s,sr=24000):
    a=np.abs(s); idx=np.where(a>0.01)[0]; return s[max(0,idx[0]-int(.02*sr)):idx[-1]+int(.06*sr)]
out={}
for key,s0,s1,sp,t,cap in L:
    slot=s1-s0
    for it in range(4):
        a,sr=k.create(t,voice=V,speed=sp,lang="en-us"); a=trim(a); d=len(a)/sr
        if d<=slot or sp>=1.15: break
        sp=round(min(1.15,sp*d/slot*1.01),3)
    sf.write(f"lines/{key}.wav",a,sr)
    w=t.split(); ends=[]
    for j in range(1,len(w)):
        p,_=k.create(" ".join(w[:j]).rstrip(",.?:"),voice=V,speed=sp,lang="en-us"); ends.append(len(trim(p))/sr-0.04)
    ends.append(d-0.06); ends=list(np.maximum.accumulate(ends)); st=[0.0]+ends[:-1]
    out[key]={"start":s0,"dur":round(d,3),"speed":sp,"words":[[w[j],round(float(s0+st[j]),3),round(float(s0+ends[j]),3)] for j in range(len(w))]}
    print(key,round(d,2),'slot',round(slot,2),'sp',sp,'OVER' if d>slot+0.05 else '')
json.dump(out,open("lines/timing.json","w"))
