import numpy as np, soundfile as sf, onnxruntime as ort, sys
from scipy.signal import resample_poly
NFFT=7680; HOP=1024; DIMF=3072; DIMT=256; COMP=1.021
CH=HOP*(DIMT-1); TRIM=NFFT//2; GEN=CH-2*TRIM
win=np.hanning(NFFT+1)[:-1].astype(np.float32)
def stft(x):  # x: [2, CH]
    p=np.pad(x,((0,0),(NFFT//2,NFFT//2)),mode='reflect')
    fr=1+(p.shape[1]-NFFT)//HOP
    idx=np.arange(NFFT)[None,:]+HOP*np.arange(fr)[:,None]
    F=np.fft.rfft(p[:,idx]*win,axis=2)          # [2, frames, bins]
    F=F.transpose(0,2,1)                          # [2, bins, frames]
    out=np.stack([F.real,F.imag],1)               # [2, 2, bins, frames]
    return out.reshape(4,F.shape[1],fr)[:,:DIMF].astype(np.float32)
def istft(s):  # s: [4, DIMF, DIMT]
    nb=NFFT//2+1; full=np.zeros((4,nb,DIMT),np.float32); full[:,:DIMF]=s
    full=full.reshape(2,2,nb,DIMT); C=full[:,0]+1j*full[:,1]   # [2,bins,frames]
    fr=C.shape[2]; frames=np.fft.irfft(C.transpose(0,2,1),n=NFFT,axis=2)*win  # [2,fr,NFFT]
    L=NFFT+HOP*(fr-1); y=np.zeros((2,L)); w=np.zeros(L)
    for i in range(fr): y[:,i*HOP:i*HOP+NFFT]+=frames[:,i]; w[i*HOP:i*HOP+NFFT]+=win**2
    y/=np.maximum(w,1e-8); return y[:,NFFT//2:NFFT//2+CH]
a,sr=sf.read(sys.argv[1]); a=a.T
if sr!=44100: a=resample_poly(a,441,int(sr/100),axis=1); sr=44100
n=a.shape[1]; pad=GEN-n%GEN
mix=np.concatenate([np.zeros((2,TRIM)),a,np.zeros((2,pad)),np.zeros((2,TRIM))],1).astype(np.float32)
sess=ort.InferenceSession(sys.argv[3] if len(sys.argv)>3 else 'voc_ft.onnx')
outs=[]
for i in range(0,n+pad,GEN):
    w=mix[:,i:i+CH]; spec=stft(w)[None]
    o=sess.run(None,{'input':spec})[0][0]
    o2=sess.run(None,{'input':-spec})[0][0]    # denoise trick
    y=(istft(o)-istft(o2))*0.5*COMP
    outs.append(y[:,TRIM:-TRIM]); print('chunk',i//GEN,flush=True)
voc=np.concatenate(outs,1)[:,:n]
sf.write(sys.argv[2],voc.T,sr,subtype='FLOAT')
sf.write(sys.argv[2].replace('.wav','_inst.wav'),(a-voc).T,sr,subtype='FLOAT')
