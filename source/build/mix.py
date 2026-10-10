import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from scipy.ndimage import uniform_filter1d
B=__import__('os').path.dirname(__import__('os').path.abspath(__file__))
tl=json.load(open(f"{B}/timeline.json")); SR=44100
m,_=sf.read(f"{B}/music.wav"); N=len(m)
vo=np.zeros(N)
for s in tl["segs"]:
    a,sr=sf.read(f"{B}/vo_{s['i']}.wav"); a=resample_poly(a,147,80)  # 24k->44.1k
    a=a/np.abs(a).max()*0.95
    i=int(s["vo_start"]*SR); vo[i:i+len(a)]+=a[:N-i]
act=uniform_filter1d((np.abs(vo)>0.02).astype(float),int(0.6*SR))
act=np.clip(act*4,0,1); act=uniform_filter1d(act,int(0.25*SR))
gain=0.62*(1-0.55*act)
mix=m*gain[:,None]+vo[:,None]*1.0
mix/=np.abs(mix).max()/0.97
sf.write(f"{B}/mix.wav",mix,SR); print("ok",N/SR)
