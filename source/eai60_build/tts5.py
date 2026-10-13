import sherpa_onnx, soundfile as sf, numpy as np, json, subprocess, sys
from spec import SPEC
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg);SID=3;SR=24000
S=json.load(open("sents.json"));assert len(S)==len(SPEC)
def trim(x):
    sf.write("vof2/_a.wav",x,SR)
    subprocess.run(["ffmpeg","-y","-v","error","-i","vof2/_a.wav","-af","silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse","vof2/_b.wav"],check=True)
    return sf.read("vof2/_b.wav")[0]
def build(spec,k):
    parts=[]
    for (txt,sp,g,pi,pb) in spec:
        a=trim(np.array(tts.generate(txt,sid=SID,speed=min(1.5,sp*k)).samples))
        sf.write("vof2/_c.wav",a,SR)
        af=[]
        if pi!=1.0: af.append(f"asetrate={int(SR*pi)},aresample={SR},atempo={1/pi:.5f}")
        if g: af.append(f"volume={g}dB")
        if af:
            subprocess.run(["ffmpeg","-y","-v","error","-i","vof2/_c.wav","-af",",".join(af),"vof2/_d.wav"],check=True);a=sf.read("vof2/_d.wav")[0]
        parts.append(np.zeros(int(pb/k*SR)));parts.append(a)
    return np.concatenate(parts)
res=[]
for i,(sent,spec) in enumerate(zip(S,SPEC)):
    T=(S[i+1][1]-0.1-sent[1]) if i+1<len(S) else (sent[2]-sent[1]+0.25)
    T=min(T,(sent[2]-sent[1])+0.55)
    k=1.0
    for it in range(3):
        y=build(spec,k);L=len(y)/SR
        if abs(L/T-1)<0.03: break
        k=min(1.4,max(0.9,k*L/T))
    r=L/T
    sf.write("vof2/_e.wav",y,SR)
    rr=min(1.25,max(0.8,r))
    subprocess.run(["ffmpeg","-y","-v","error","-i","vof2/_e.wav","-af",f"atempo={rr:.5f}",f"vof2/f{i:02d}.wav"],check=True)
    res.append((i,round(L,2),round(T,2),round(k,2),round(r,3)))
print(*res,sep="\n")
