import sherpa_onnx, soundfile as sf, numpy as np, json, subprocess, sys
from spec3 import W,TXT,GAP
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg);SID=int(sys.argv[1]) if len(sys.argv)>1 else 3;SR=24000
def gen(txt,sp):
    a=np.array(tts.generate(txt,sid=SID,speed=sp).samples);sf.write("v91/_a.wav",a,SR)
    subprocess.run(["ffmpeg","-y","-v","error","-i","v91/_a.wav","-af","silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse","v91/_b.wav"],check=True)
    return sf.read("v91/_b.wav")[0]
TOT=90.0;y=np.zeros(int(TOT*SR));out=[];rep=[]
for lid,sents in TXT.items():
    st,en=W[lid];T=(en-st)*0.995;g=GAP.get(lid,0.0);ng=len(sents)-1;sp=0.88
    tgt=T-g*ng
    def speech_at(x): return sum(len(gen(t,x)) for _,t in sents)/SR
    lo,hi=0.78,1.12
    if speech_at(lo)<=tgt: sp=lo
    elif speech_at(hi)>=tgt: sp=hi
    else:
        for it in range(7):
            mid=(lo+hi)/2
            if speech_at(mid)>tgt: lo=mid
            else: hi=mid
        sp=hi
    aud=[gen(t,sp) for _,t in sents];speech=sum(len(a) for a in aud)/SR
    gg=g
    if speech<T-g*ng-0.05 and ng>0: gg=(T-speech)/ng   # spread leftover as pause
    gg=min(gg,1.2)
    t=st
    for i,(oi,txt) in enumerate(sents):
        a=aud[i];s0=int(t*SR);y[s0:s0+len(a)]+=a
        out.append(dict(line=lid,old=oi,text=txt,new_a=round(t,3),new_b=round(t+len(a)/SR,3)))
        t+=len(a)/SR+gg
    rep.append((lid,round(speech,2),round(T,2),round(sp,2),round(t-gg,2)))
sf.write("v91/raw.wav",y,SR);json.dump(out,open("v91/sents_new.json","w"),indent=1)
print(*rep,sep="\n")
