# Voice-over for the 108.5 s teaser. Voice: Kokoro af_sarah (sid 9), the closest local match to the Application Retirement video voice.
# Each cue starts at its script time; speed is fitted to the cue window within 0.95..1.25 so the pace stays natural.
import sherpa_onnx, soundfile as sf, numpy as np, json, subprocess, sys
sys.path.insert(0,'vo')
from cues import A,B_INTRO,TOTAL
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg);SID=9;SR=24000;LO,HI=0.95,1.25;cache={}
def gen(txt,sp):
    k=(txt,round(sp,2))
    if k not in cache:
        a=np.array(tts.generate(txt,sid=SID,speed=round(sp,2)).samples);sf.write("vo/_a.wav",a,SR)
        subprocess.run(["ffmpeg","-y","-v","error","-i","vo/_a.wav","-af","silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse","vo/_b.wav"],check=True)
        cache[k]=sf.read("vo/_b.wav")[0]
    return cache[k]
def build(cues,end,name,base=1.08,cap=1.2,maxslip=0.45):
    y=np.zeros(int(TOTAL*SR));out=[];prev_end=-9
    for i,(t,txt) in enumerate(cues):
        nxt=cues[i+1][0] if i+1<len(cues) else end
        cont=txt.rstrip().endswith(',') or txt.startswith(('Ready-made','build on'))
        gap=0.12 if cont else 0.3
        st=max(t,prev_end+gap)
        sp=base;win=nxt-st-(0.05 if cont else 0.2)
        # one steady pace; only speed up (to the cap) when this cue would run into the next script cue
        while len(gen(txt,sp))/SR>win and sp<cap-1e-9: sp=min(cap,round(sp+0.02,2))
        a=gen(txt,sp);s0=int(st*SR);y[s0:s0+len(a)]+=a;prev_end=st+len(a)/SR
        out.append(dict(script_start=t,start=round(st,2),end=round(prev_end,2),speed=round(sp,2),window=round(nxt-t,2),text=txt))
        print(name,t,'->',round(st,2),round(prev_end,2),'speed',round(sp,2),'SLIP %.2f'%(st-t) if st-t>0.05 else '')
    sf.write(f"vo/{name}_raw.wav",y,SR);json.dump(out,open(f"vo/{name}_cues.json","w"),indent=1)
build(A,TOTAL-0.6,'A');build(B_INTRO,10.3,'B_intro',cap=1.3)
