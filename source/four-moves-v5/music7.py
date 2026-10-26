import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; DUR=172.6; N=int(SR*DUR)
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
BPM=122; BEAT=60/BPM; BAR=4*BEAT
def mtof(m): return 440*2**((m-69)/12)
def lp(x,f,o=2): return sosfilt(butter(o,f,fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,btype='high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],btype='band',fs=SR,output='sos'),x)
def put(sig,t,g=1.0,pan=0.0,bus=None):
    i=int(t*SR)
    if i>=N: return
    s=sig[:N-i]*g; lg=np.sqrt(0.5*(1-pan)); rg=np.sqrt(0.5*(1+pan))
    (bus[0] if bus else L)[i:i+len(s)]+=s*lg; (bus[1] if bus else R)[i:i+len(s)]+=s*rg
def env(n,a,d):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-t/d); return e
# ---------- instruments ----------
def kick(g=1.0):
    n=int(.45*SR); t=np.arange(n)/SR
    f=45+85*np.exp(-t/0.035); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t/0.16)
    s+=0.25*hp(rng.standard_normal(n),3000)*np.exp(-t/0.004)
    return np.tanh(1.6*s)*0.9*g
def clap():
    n=int(.35*SR); t=np.arange(n)/SR; x=bp(rng.standard_normal(n),900,5000)
    e=np.zeros(n)
    for o in (0,0.009,0.018): e+=np.where(t>=o,np.exp(-(t-o)/0.006),0)*0.6
    e+=np.where(t>=0.026,np.exp(-(t-0.026)/0.09),0)
    return x*e*0.5
def hat(open_=False):
    n=int((.25 if open_ else .06)*SR); t=np.arange(n)/SR
    return hp(rng.standard_normal(n),7000)*np.exp(-t/(0.07 if open_ else 0.014))*0.22
def shaker():
    n=int(.08*SR); t=np.arange(n)/SR
    return bp(rng.standard_normal(n),5000,11000)*np.minimum(1,t/0.01)*np.exp(-t/0.03)*0.12
def saw(f,n):
    t=np.arange(n)/SR; return 2*((f*t)%1)-1
def supersaw(m,n,det=(-0.12,-0.05,0,0.05,0.12)):
    s=np.zeros(n)
    for d in det: s+=saw(mtof(m+d),n)
    return s/len(det)
def pad(notes,dur,cut=2200):
    n=int(dur*SR); s=np.zeros(n)
    for m in notes: s+=supersaw(m,n)
    s=lp(s,cut,2)*np.minimum(1,np.arange(n)/(0.08*SR))*np.minimum(1,(n-np.arange(n))/(0.15*SR))
    return s*0.16
def bass(m,dur):
    n=int(dur*SR); t=np.arange(n)/SR; f=mtof(m)
    s=0.8*np.sin(2*np.pi*f*t)+0.35*lp(saw(f,n),900)
    return s*np.minimum(1,t/0.005)*np.exp(-t/0.35)*0.55
def pluck(m,d=0.22):
    n=int(.6*SR); t=np.arange(n)/SR; f=mtof(m)
    s=np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.05)+0.2*lp(saw(f,n),3500)
    return s*np.minimum(1,t/0.002)*np.exp(-t/d)*0.12
def bell(m):
    n=int(2.0*SR); t=np.arange(n)/SR; f=mtof(m)
    s=sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/dd) for a,r,dd in ((1,1,1.2),(.5,2.76,.5),(.25,5.4,.25),(.2,2,.8)))
    return s*np.minimum(1,t/0.003)*0.13
def riser(dur):
    n=int(dur*SR); t=np.arange(n)/SR; x=rng.standard_normal(n); out=np.zeros(n)
    seg=int(0.05*SR)
    for i in range(0,n,seg):
        p=i/n; fc=400+7000*p**2
        out[i:i+seg]=bp(x[i:i+seg],fc*0.7,min(fc*1.3,20000))
    tone=np.sin(2*np.pi*np.cumsum(200+600*(t/dur)**2)/SR)*0.15
    return (out*0.35+tone)*(t/dur)**2.2
def impact():
    n=int(2.2*SR); t=np.arange(n)/SR
    boom=np.sin(2*np.pi*np.cumsum(38+60*np.exp(-t/0.08))/SR)*np.exp(-t/0.6)
    crash=hp(rng.standard_normal(n),2500)*np.exp(-t/0.7)*0.25
    return np.tanh(1.3*boom)*0.85+crash
# ---------- harmony ----------
PROG_MAJ=[(38,[62,66,69]),(33,[61,64,69]),(35,[62,66,71]),(31,[62,67,71])]   # D A Bm G
PROG_TEN=[(35,[59,62,66]),(35,[59,62,66]),(31,[59,62,67]),(30,[61,66,69])]   # Bm Bm G F#
PADL=[np.zeros(N),np.zeros(N)]; PLK=[np.zeros(N),np.zeros(N)]; SC=np.ones(N)
def section(t0,t1,mode,level=1.0,arp=False,perc=False,strings=False):
    prog=PROG_MAJ if mode=='full' else PROG_TEN
    nb=int(np.ceil((t1-t0)/BEAT))
    for b in range(nb):
        tb=t0+b*BEAT
        if tb>=t1-0.02: break
        bar=b//4; bi=b%4; root,ch=prog[bar%4]
        if mode=='full':
            put(kick(),tb,0.95*level)
            k=int(tb*SR); n=int(BEAT*SR); tt=np.arange(min(n,N-k))/SR
            SC[k:k+len(tt)]=np.minimum(SC[k:k+len(tt)],1-0.55*np.exp(-tt/0.11))
            if bi in (1,3): put(clap(),tb,0.8*level,0.0)
            for h in range(4):
                put(hat(open_=(h==2)),tb+h*BEAT/4,(0.9 if h==2 else 0.55)*level,0.25)
            for e in range(2): put(bass(root+(12 if e==1 and bi%2 else 0),BEAT/2),tb+e*BEAT/2,0.9*level)
            if perc:
                for h in range(4): put(shaker(),tb+h*BEAT/4+0.01,level,-0.4)
        else:  # tension: muted pulse
            if bi==0 or bi==2: put(lp(kick(),300),tb,0.7*level)
            for h in range(2): put(hat(),tb+h*BEAT/2+BEAT/4,0.35*level,0.3)
            put(lp(bass(root,BEAT*0.9),400),tb,0.7*level)
        if bi==0:
            put(pad(ch+[c-12 for c in ch[:1]],BAR,cut=2600 if mode=='full' else 900),tb,level*(1.0 if mode=='full' else 0.9),bus=PADL)
            if strings: put(pad([c+12 for c in ch],BAR,cut=4500),tb,0.5*level,bus=PADL)
        if arp and mode=='full':
            seq=[ch[0]+12,ch[1]+12,ch[2]+12,ch[1]+12]
            for s in range(4): put(pluck(seq[(b*4+s)%4]),tb+s*BEAT/4,level,(-0.35 if s%2 else 0.35),bus=PLK)
# ---------- arrangement ----------
O=41.7
section(0.0,12.7,'ten',0.5)
section(12.7,23.6,'ten',0.8)
section(23.6,47.5,'full',1.0,arp=True,perc=True)
section(47.5,57.3,'ten',0.75)
section(15.6+O,35.8+O,'full',0.9,arp=False)
section(35.8+O,41.0+O,'ten',0.75)
section(41.0+O,64.8+O,'full',0.95,arp=True)
section(64.8+O,69.7+O,'ten',0.75)
section(69.7+O,94.8+O,'full',1.0,arp=True,perc=True)
section(94.8+O,98.8+O,'ten',0.75)
section(98.8+O,117.7+O,'full',1.0,arp=True,perc=True,strings=True)
section(117.7+O,123.2+O,'full',1.05,arp=True,perc=True,strings=True)
put(pad([50,57,62,66,69,74],7.7,cut=3200)*np.exp(-np.arange(int(7.7*SR))/SR/3.3),123.2+O,1.6,bus=PADL)
for b in range(8):
    tb=123.2+O+b*BEAT; put(lp(kick(),400),tb,0.45*(1-b/8))
# ---------- buses ----------
def rev(x,dur=1.8):
    n=int(dur*SR); t=np.arange(n)/SR; ir=rng.standard_normal(n)*np.exp(-t/(dur/5)); ir=lp(ir,6000); ir/=np.sqrt((ir**2).sum())
    return fftconvolve(x,ir)[:N]
for bus,wet in ((PADL,0.35),(PLK,0.45)):
    for c,(src,dst) in enumerate(((bus[0],L),(bus[1],R))):
        s=src*SC
        if bus is PLK:  # dotted-eighth delay
            d=int(0.75*BEAT*SR); dl=np.zeros(N); dl[d:]=s[:-d]*0.35; s=s+ (dl if c==0 else np.roll(dl,int(0.01*SR)))
        dst+=s+wet*rev(s)
# bass & low end pump
mix=np.stack([L,R])
mix=hp(mix,30)
peak=np.abs(mix).max(); mix=mix/peak*0.9
sf.write('music7.wav',mix.T,SR,subtype='FLOAT')
print('done',mix.shape)
# SFX removed: 