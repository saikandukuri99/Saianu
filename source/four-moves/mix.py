import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
SR=48000; DUR=126.3; N=int(SR*DUR)
T=json.load(open('lines_f/timing.json'))
vo=np.zeros(N)
for k,v in T.items():
    a,sr=sf.read(f'lines_f/{k}.wav'); a=resample_poly(a,2,1)
    f=int(.008*SR); a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f)
    i=int(v['start']*SR); vo[i:i+len(a)]+=a[:N-i]
B=lambda *a,**k: butter(*a,fs=SR,output='sos',**k)
vo=sosfilt(B(2,80,btype='high'),vo)
vo=vo+0.15*sosfilt(B(2,[180,450],btype='band'),vo)
vo=vo-0.12*sosfilt(B(2,[3000,5000],btype='band'),vo)
vo=vo-0.25*sosfilt(B(2,7500,btype='high'),vo)
sf.write('vo_f_raw.wav',vo,SR,subtype='FLOAT')
C={k:v['words'] for k,v in T.items()}
open('cues_f.js','w').write('const CUES='+json.dumps(C)+';')
