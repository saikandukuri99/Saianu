# v3 rev2 voice-over: same Kokoro voice (af_heart), but a steady natural pace instead of stretching every line to its window.
# Each sentence keeps its v92 start time (so the visuals stay in sync); speed per line is fitted to the window but kept in 0.92..1.10.
import sherpa_onnx, soundfile as sf, numpy as np, json, subprocess, sys
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg);SID=3;SR=24000;LO,HI=0.92,1.10
cache={}
def gen(txt,sp):
    k=(txt,round(sp,2))
    if k not in cache:
        a=np.array(tts.generate(txt,sid=SID,speed=round(sp,2)).samples);sf.write("v93/_a.wav",a,SR)
        subprocess.run(["ffmpeg","-y","-v","error","-i","v93/_a.wav","-af","silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse","v93/_b.wav"],check=True)
        cache[k]=sf.read("v93/_b.wav")[0]
    return cache[k]
S=[s for s in json.load(open("v92/sents_new.json")) if s["text"]!="It never guesses."]
lines={}
for s in S: lines.setdefault(s["line"],[]).append(s)
y=np.zeros(int(94.0*SR));out=[];rep=[]
for lid,ss in lines.items():
    win=sum(s["new_b"]-s["new_a"] for s in ss)
    sp_of=lambda x:sum(len(gen(s["text"],x)) for s in ss)/SR
    lo,hi=LO,HI
    if sp_of(lo)<=win: sp=lo
    elif sp_of(hi)>=win: sp=hi
    else:
        for _ in range(6):
            mid=(lo+hi)/2
            if sp_of(mid)>win: lo=mid
            else: hi=mid
        sp=hi
    for i,s in enumerate(ss):
        a=gen(s["text"],sp);t=s["new_a"]
        if i and t<out[-1]["new_b"]+0.12: t=out[-1]["new_b"]+0.12   # never run into the previous sentence
        n=min(len(a),len(y)-int(t*SR));y[int(t*SR):int(t*SR)+n]+=a[:n]
        out.append(dict(line=lid,old=s["old"],text=s["text"],new_a=round(t,3),new_b=round(t+len(a)/SR,3)))
    rep.append((lid,round(sp,2),round(win,2),round(sp_of(sp),2)))
sf.write("v93/raw.wav",y,SR);json.dump(out,open("v93/sents_new.json","w"),indent=1)
print(*rep,sep="\n")
