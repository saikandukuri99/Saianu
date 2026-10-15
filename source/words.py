import json, numpy as np, re, importlib.util
spec=importlib.util.spec_from_file_location("g","gen.py")
src=open("gen.py").read(); N="am_michael"; L=eval(src[src.index("L=[")+2:src.index("]\nout")+1])
from kokoro_onnx import Kokoro
k=Kokoro("kokoro-v1.0.onnx","voices-v1.0.bin")
dur=json.load(open("lines/dur.json"))
def tl(s,sr=24000):
    a=np.abs(s); idx=np.where(a>0.01)[0]; return (idx[-1]-max(0,idx[0]-480)+1440)/sr
res={}
for i,v,sp,t in L:
    w=t.split(); ends=[]
    for j in range(1,len(w)):
        pre=" ".join(w[:j]).rstrip(",.?")
        s,_=k.create(pre,voice=v,speed=sp,lang="en-us"); ends.append(tl(s)-0.04)
    ends.append(dur[i]-0.06)
    ends=list(np.maximum.accumulate(ends))
    st=[0.0]+ends[:-1]
    res[i]=[[w[j],round(st[j],3),round(ends[j],3)] for j in range(len(w))]
    print(i,res[i])
json.dump(res,open("lines/words.json","w"))
