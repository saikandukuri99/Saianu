import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
T=json.load(open('lines/timing.json')); SR=48000; DUR=126.3
mix=np.zeros(int(SR*DUR))
for k,v in T.items():
    a,sr=sf.read(f'lines/{k}.wav'); a=resample_poly(a,2,1)
    a=sosfilt(butter(2,90,btype="high",fs=SR,output="sos"),a)
    f=int(.008*SR); a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f)
    i=int(v['start']*SR); mix[i:i+len(a)]+=a[:len(mix)-i]
mix=mix+0.30*sosfilt(butter(2,[140,420],btype="band",fs=SR,output="sos"),mix)
mix=mix-0.22*sosfilt(butter(2,[2400,4800],btype="band",fs=SR,output="sos"),mix)
mix=mix-0.35*sosfilt(butter(2,6500,btype="high",fs=SR,output="sos"),mix)
mix=sosfilt(butter(2,70,btype="high",fs=SR,output="sos"),mix)
sf.write('vo_raw.wav',mix,SR,subtype='FLOAT')
C={k:v['words'] for k,v in T.items()}
open('cues.js','w').write('const CUES='+json.dumps(C)+';')
