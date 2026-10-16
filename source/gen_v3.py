import soundfile as sf, json, numpy as np
from kokoro_onnx import Kokoro
k=Kokoro("kokoro-v1.0.onnx","voices-v1.0.bin")
N="am_michael"
L=[("n5",N,1.0,"Solix, E C S, puts the proof in every plan."),("n10a",N,0.92,"Solix, E C S.")]
def trim(s,sr=24000):
    a=np.abs(s); idx=np.where(a>0.01)[0]; return s[max(0,idx[0]-int(.02*sr)):idx[-1]+int(.06*sr)]
words=json.load(open("lines_v3/words.json")); dur=json.load(open("lines_v3/dur.json"))
for i,v,sp,t in L:
    s,sr=k.create(t,voice=v,speed=sp,lang="en-us"); s=trim(s); sf.write(f"lines_v3/{i}.wav",s,sr); dur[i]=round(len(s)/sr,3)
    w=t.split(); ends=[]
    for j in range(1,len(w)):
        p,_=k.create(" ".join(w[:j]).rstrip(",.?"),voice=v,speed=sp,lang="en-us"); ends.append(len(trim(p))/sr-0.04)
    ends.append(dur[i]-0.06); ends=list(np.maximum.accumulate(ends)); st=[0.0]+ends[:-1]
    words[i]=[[w[j],round(float(st[j]),3),round(float(ends[j]),3)] for j in range(len(w))]
    print(i,dur[i],words[i])
json.dump(words,open("lines_v3/words.json","w")); json.dump(dur,open("lines_v3/dur.json","w"))
