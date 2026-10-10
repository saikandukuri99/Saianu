# compress internal pauses longer than maxgap
import sys, numpy as np, soundfile as sf
for f in sys.argv[1:]:
    a,sr=sf.read(f); win=int(sr*0.01)
    env=np.array([np.abs(a[i:i+win]).max() for i in range(0,len(a),win)])
    voiced=env>0.01
    idx=np.where(voiced)[0]; a=a[idx[0]*win:(idx[-1]+1)*win]; voiced=voiced[idx[0]:idx[-1]+1]
    out=[];i=0;n=len(voiced);maxgap=int(0.22/0.01)
    while i<n:
        j=i
        while j<n and voiced[j]==voiced[i]: j+=1
        seg=a[i*win:j*win]
        if not voiced[i] and (j-i)>maxgap:
            k=maxgap*win//2; seg=np.concatenate([seg[:k],seg[-k:]])
        out.append(seg); i=j
    b=np.concatenate(out); sf.write(f,b,sr); print(f.split('/')[-1], round(len(b)/sr,2))
