import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
SR=48000; DUR=172.6; N=int(SR*DUR)
v,sr=sf.read('/home/claude/v7/ref_vocals.wav'); m=v.mean(1)
m=resample_poly(m,480,441)
vo=np.zeros(N); vo[:min(N,len(m))]=m[:N]
B=lambda *a,**k: butter(*a,fs=SR,output='sos',**k)
vo=sosfilt(B(2,75,btype='high'),vo)
# downward expander/gate on residual bleed (threshold -42 dBFS, smooth)
e=np.sqrt(np.convolve(vo**2,np.ones(480)/480,'same')); db=20*np.log10(e+1e-9)
g=np.clip((db+48)/8,0,1)              # 0 below -48, 1 above -40
ctl=g[::48]; sm=np.zeros_like(ctl); s=0
for i,c in enumerate(ctl):
    s+=(0.5 if c>s else 0.02)*(c-s); sm[i]=s
g=np.repeat(sm,48)[:N]; vo=vo*np.maximum(g,0.02)
sf.write('vo7_raw.wav',vo,SR,subtype='FLOAT')
