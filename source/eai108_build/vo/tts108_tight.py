# Tight version of the voice-over: one natural pace (speed 1.0), short even pauses instead of the long script gaps.
# Also writes the time map (script time -> tight time) so the scenes follow the new voice.
import sherpa_onnx, soundfile as sf, numpy as np, json, subprocess, sys
sys.path.insert(0,'vo')
from cues import A
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg);SID=9;SR=24000;SPEED=1.0
def gen(txt):
    a=np.array(tts.generate(txt,sid=SID,speed=SPEED).samples);sf.write("vo/_a.wav",a,SR)
    subprocess.run(["ffmpeg","-y","-v","error","-i","vo/_a.wav","-af","silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse","vo/_b.wav"],check=True)
    return sf.read("vo/_b.wav")[0]
SECTION={5.5,10.3,19.8,29.3,44.8,59.8,70.8,81.3,91.8,103.4}
def gap_before(i):
    t,txt=A[i];prev=A[i-1][1]
    if prev.rstrip().endswith(',') or txt.startswith(('Ready-made','build on')) or prev.startswith('Ready-made'): return 0.12
    if t in SECTION: return 0.75
    return 0.42
T0=0.3;t=T0;out=[];audio=[]
for i,(ts,txt) in enumerate(A):
    if i: t+=gap_before(i)
    a=gen(txt);audio.append((t,a));out.append(dict(script_start=ts,start=round(t,3),end=round(t+len(a)/SR,3),speed=SPEED,text=txt));t+=len(a)/SR
END=round(t+1.8,2)   # hold on the closing card
y=np.zeros(int((END+0.2)*SR))
for st,a in audio: s0=int(st*SR);y[s0:s0+len(a)]+=a
sf.write("vo/T_raw.wav",y,SR)
json.dump(dict(total=END,cues=out),open("vo/T_cues.json","w"),indent=1)
# time map: script (old) time -> tight (new) time. Anchors at every cue start, plus the ends.
old=[0.0]+[c['script_start'] for c in out]+[108.5];new=[0.0]+[c['start'] for c in out]+[END]
for i in range(1,len(old)): assert old[i]>old[i-1] and new[i]>new[i-1],(i,old[i],new[i])
open("lib/timemap.js","w").write(f"const TM_OLD={json.dumps(old)},TM_NEW={json.dumps(new)};\n")
json.dump([old,new],open("vo/tmap.json","w"))
print('speech',round(sum(c['end']-c['start'] for c in out),1),'total',END)
for c in out[:6]+out[-3:]: print(c['script_start'],'->',c['start'],c['end'],c['text'][:40])
