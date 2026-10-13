import sherpa_onnx, soundfile as sf, numpy as np, json, subprocess
from spec2 import LINES
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg);SID=3;SR=24000
def trim(x):
    sf.write("v75/_a.wav",x,SR)
    subprocess.run(["ffmpeg","-y","-v","error","-i","v75/_a.wav","-af","silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse","v75/_b.wav"],check=True)
    return sf.read("v75/_b.wav")[0]
def sent(spec,k):
    parts=[]
    for (txt,sp,g,pi,pb) in spec:
        a=trim(np.array(tts.generate(txt,sid=SID,speed=min(1.5,sp*k)).samples));sf.write("v75/_c.wav",a,SR)
        af=[]
        if pi!=1.0: af.append(f"asetrate={int(SR*pi)},aresample={SR},atempo={1/pi:.5f}")
        if g: af.append(f"volume={g}dB")
        if af:
            subprocess.run(["ffmpeg","-y","-v","error","-i","v75/_c.wav","-af",",".join(af),"v75/_d.wav"],check=True);a=sf.read("v75/_d.wav")[0]
        parts+= [np.zeros(int(pb/k*SR)),a]
    return np.concatenate(parts)
TOT=76.9;y=np.zeros(int(TOT*SR));out=[];report=[]
for (lid,st,en,gaps,sents) in LINES:
    T=(en-st)*0.995;k=1.0
    for it in range(7):
        aud=[sent(sp,k) for (_,sp) in sents];L=sum(len(a) for a in aud)/SR+sum(gaps)
        if abs(L/T-1)<0.02: break
        k=min(1.45,max(0.85,k*(L-sum(gaps))/(T-sum(gaps))))
    t=st
    for i,(oi,sp) in enumerate(sents):
        a=aud[i];s0=int(t*SR);y[s0:s0+len(a)]+=a
        txt=" ".join(p[0] for p in sp)
        out.append(dict(line=lid,old=oi,text=txt,new_a=round(t,3),new_b=round(t+len(a)/SR,3)))
        t+=len(a)/SR+(gaps[i] if i<len(gaps) else 0)
    report.append((lid,round(L,2),round(T,2),round(k,2),round(t-(gaps[-1] if False else 0),2)))
sf.write("v75/raw.wav",y,SR);json.dump(out,open("v75/sents_new.json","w"),indent=1)
print(*report,sep="\n")
