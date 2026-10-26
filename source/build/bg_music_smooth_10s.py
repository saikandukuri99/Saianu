import numpy as np, sys
src,dst=sys.argv[1],sys.argv[2]
x=np.fromfile(src,np.float32).reshape(-1,2).astype(np.float64); sr=48000
def lp(sig,fc,taps=2047):
    n=np.arange(taps)-(taps-1)/2
    h=np.sinc(2*fc/sr*n)*np.blackman(taps); h/=h.sum()
    return np.stack([np.convolve(sig[:,c],h,'same') for c in range(2)],1)
# only process a local window (rest stays bit-identical)
a,b=int(10.30*sr),int(10.70*sr)
seg=x[a:b]
l150=lp(seg,150); l800=lp(seg,800)
b_low=l150; b_mid=l800-l150; b_hi=seg-l800
t=(np.arange(a,b))/sr
def env(t0,t1,floor,fade=0.010):
    g=np.ones_like(t)
    up=lambda u:0.5-0.5*np.cos(np.pi*np.clip(u,0,1))
    g-= (1-floor)*np.minimum(up((t-(t0-fade))/fade), up(((t1+fade)-t)/fade))
    return g[:,None]
t0,t1=10.458,10.502
seg2=b_low + b_mid*env(t0,t1,0.45) + b_hi*env(t0,t1,0.12)
y=x.copy(); y[a:b]=seg2
y.astype(np.float32).tofile(dst)
print("changed samples:", np.count_nonzero(np.abs(y-x).max(1)>1e-6)/sr, "s")
