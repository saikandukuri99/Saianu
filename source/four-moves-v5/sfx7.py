import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; DUR=172.6; N=int(SR*DUR)
rng=np.random.default_rng(11)
C=json.load(open('cues_abs.json'))
ws=lambda k,i: C[k][i][1]
st=lambda k: C[k][0][1]
L=np.zeros(N); R=np.zeros(N)
def lp(x,f): return sosfilt(butter(2,f,fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,btype='high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],btype='band',fs=SR,output='sos'),x)
def T(d): return np.arange(int(d*SR))/SR
def put(sig,t,g=1.0,pan=0.0):
    i=int(t*SR)
    if i<0 or i>=N: return
    s=sig[:N-i]*g; L[i:i+len(s)]+=s*np.sqrt(0.5*(1-pan)); R[i:i+len(s)]+=s*np.sqrt(0.5*(1+pan))
# ---------- sound design ----------
def whoosh(d=0.45,up=True):
    t=T(d); x=rng.standard_normal(len(t)); out=np.zeros(len(t)); seg=int(0.02*SR)
    for i in range(0,len(t),seg):
        p=i/len(t); p=p if up else 1-p; fc=500+5000*p
        out[i:i+seg]=bp(x[i:i+seg],fc*0.6,min(fc*1.4,20000))
    e=np.sin(np.pi*np.clip(t/d,0,1))**2
    return out*e*0.5
def impact():
    t=T(2.0); boom=np.sin(2*np.pi*np.cumsum(38+70*np.exp(-t/0.07))/SR)*np.exp(-t/0.55)
    crash=hp(rng.standard_normal(len(t)),2500)*np.exp(-t/0.6)*0.22
    return np.tanh(1.4*boom)*0.8+crash
def riser(d=1.0):
    t=T(d); x=rng.standard_normal(len(t)); out=np.zeros(len(t)); seg=int(0.04*SR)
    for i in range(0,len(t),seg):
        p=i/len(t); fc=400+7000*p**2; out[i:i+seg]=bp(x[i:i+seg],fc*0.7,min(fc*1.3,20000))
    tone=np.sin(2*np.pi*np.cumsum(220+700*(t/d)**2)/SR)*0.12
    return (out*0.35+tone)*(t/d)**2.2
def bell(f,d=1.4,g=1.0):
    t=T(d); s=sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/dd) for a,r,dd in ((1,1,0.9),(.45,2.76,.35),(.2,5.4,.18),(.25,2,.6)))
    return s*np.minimum(1,t/0.003)*0.12*g
def ping(f=1568):
    t=T(0.5); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*np.exp(-t/0.09)*np.minimum(1,t/0.002)*0.10
def click():
    t=T(0.06); return bp(rng.standard_normal(len(t)),1500,6000)*np.exp(-t/0.006)*0.35+np.sin(2*np.pi*2200*t)*np.exp(-t/0.01)*0.08
def pop(f0=700):
    t=T(0.12); f=f0*np.exp(-t/0.05)+f0*0.45; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.04)*0.16
def thud():
    t=T(0.4); return (np.sin(2*np.pi*np.cumsum(55+90*np.exp(-t/0.03))/SR)*np.exp(-t/0.12)*0.55+lp(rng.standard_normal(len(t)),900)*np.exp(-t/0.03)*0.2)
def tick():
    t=T(0.025); return hp(rng.standard_normal(len(t)),3500)*np.exp(-t/0.004)*0.18
def key():
    t=T(0.05); return (bp(rng.standard_normal(len(t)),1800,5000)*np.exp(-t/0.008)*0.25+np.sin(2*np.pi*180*t)*np.exp(-t/0.01)*0.1)
def stamp():
    o=thud()*1.1; k=bp(rng.standard_normal(int(0.15*SR)),400,2000)*np.exp(-T(0.15)/0.03)*0.4; i=int(0.005*SR); o[i:i+len(k)]+=k; return o
def lock():
    t=T(0.6); a=np.r_[click()*1.4,np.zeros(int(0.07*SR)),click()*1.8]
    res=np.sin(2*np.pi*1850*t)*np.exp(-t/0.12)*0.12+np.sin(2*np.pi*2730*t)*np.exp(-t/0.08)*0.06
    out=np.zeros(len(t)); out[:len(a)]+=a; out+=res; out[:int(0.4*SR)]+=thud()[:int(0.4*SR)]*0.8; return out
def success():
    a=bell(1318.5,0.9,0.8); b=bell(1760,1.1,0.8); out=np.zeros(len(b)+int(0.09*SR)); out[:len(a)]+=a; out[int(0.09*SR):]+=b; return out
def error():
    t=T(0.5); s=np.sin(2*np.pi*233*t)+0.6*np.sin(2*np.pi*277*t); return lp(s*np.exp(-t/0.18)*np.minimum(1,t/0.01),1500)*0.12
def scratch(d=0.8):
    t=T(d); x=bp(rng.standard_normal(len(t)),2500,7000); m=0.5+0.5*np.sin(2*np.pi*9*t)**2
    return x*m*np.sin(np.pi*t/d)*0.08
def shimmer():
    out=np.zeros(int(1.6*SR))
    for i,f in enumerate([1760,2217,2637,3520]): s=bell(f,1.3,0.6); k=int(i*0.05*SR); out[k:k+len(s)]+=s[:len(out)-k]
    return out
def flip():
    w=whoosh(0.25); out=np.zeros(len(w)+int(0.3*SR)); out[:len(w)]+=w*0.7; p=pop(500); out[int(0.18*SR):int(0.18*SR)+len(p)]+=p; return out
def rev0(x):
    n=int(0.9*SR); t=np.arange(n)/SR; ir=rng.standard_normal(n)*np.exp(-t/0.15); ir=lp(ir,7000); ir/=np.sqrt((ir**2).sum())
    return fftconvolve(x,ir)[:N]
# ---------- NEW OPENING EVENTS (absolute) ----------
put(riser(1.9),0.25,0.55)
for k in range(10): put(tick(),0.45+k*0.14,0.6,-0.4+0.08*k)
c0=ws('q00a',0); put(impact(),c0,0.75)
for k in range(24): put(ping(880+k*25)[:int(0.12*SR)],c0+0.12+k*0.065,0.25,0.2)
for g,wi in enumerate([0,1,2,4]): put(pop(650+g*90),ws('q00b',wi)-0.02,0.7,0.4)
for j,wi in enumerate([5,7,9]): put(stamp(),ws('q00b',wi)+0.05,1.0,-0.2+0.2*j)
put(error(),ws('q00b',10)+0.45,0.8)
put(whoosh(0.9),ws('q01a',3)-0.1,0.5); put(whoosh(1.3,up=False),ws('q01a',4),0.45,0.3)
for g,wi in enumerate([4,3,5,7]): put(whoosh(0.5),ws('q01b',wi),0.35,-0.5+0.3*g); put(ping(1175+g*120),ws('q01b',wi)+0.45,0.8,-0.5+0.3*g)
tt=21.9
for i,iv in enumerate([0.42,0.36,0.3,0.25,0.21,0.17,0.14,0.12,0.1]): put(ping(1320+(i%3)*110),tt,0.6+0.05*i,(-0.6+0.15*i)); tt+=iv
put(whoosh(0.6,up=False),22.95,0.7); put(riser(1.1),22.65,0.7)
s0=ws('q02a',0); put(impact(),s0,0.95); put(whoosh(0.4),s0-0.05,0.5)
for i,f in enumerate([1174.7,1480,1760,2349]): put(bell(f,0.9,0.6),s0+0.5+i*0.25,0.6,-0.45+0.3*i)
BK=['q02b','q02c','q02d','q02e']
for i,k in enumerate(BK):
    a=ws(k,0); put(whoosh(0.45),a-0.4,0.55); put(impact()[:int(0.8*SR)],a-0.02,0.45)
    for j in range(7 if i<3 else 4): put(pop(700+j*60),a+0.9+j*0.12,0.45,0.3)
    if i==0:
        for j in range(16): put(whoosh(0.35),a+0.2+j*0.12,0.12,-0.8+0.1*j)
    if i==1:
        for j in range(3): put(ping(660),a+j*1.1,0.5,0.0)
        put(scratch(0.8),ws(k,min(5,len(C[k])-1)),0.8,0.5)
    if i==2:
        for j in range(4): put(click(),a+0.6+j*0.3,0.9,0.4)
        for j in range(3): put(lock(),a+2.2+j*0.2,0.5,0.5)
    if i==3:
        put(shimmer(),a+0.1,0.6)
        for j in range(4): put(tick()*1.3,a+0.6+j*0.3,1.0)
    nxt=ws(BK[i+1],0)-0.35 if i<3 else 45.0
    put(thud()*0.7,nxt-0.15,0.6)
for i,f in enumerate([587.3,740,880,1174.7]): put(bell(f,1.6,0.9),45.25+i*0.08,0.7,-0.3+0.2*i)
put(whoosh(0.5),46.75,0.5,0.6)
for i in range(7): put(ping(1047),48.6+i*0.16,0.6,-0.6+0.2*i)
for i in range(4): put(ping(880),50.2+i*0.2,0.3,0.6)
put(error(),54.6,1.0)
L=L+0.18*rev0(L); R=R+0.18*rev0(R)
# carried-over SFX for Move 01 onward (shifted 41.7 s)
old,_=sf.read('sfx_old.wav'); o=int(41.7*SR); cut=int(14.5*SR)
seg=old[cut:]; i0=o+cut; n=min(len(seg),N-i0)
fade=np.ones(n); fade[:int(0.05*SR)]=np.linspace(0,1,int(0.05*SR))
L[i0:i0+n]+=seg[:n,0]*fade; R[i0:i0+n]+=seg[:n,1]*fade

mix=np.stack([L,R],1); mix=mix/np.abs(mix).max()*0.9
sf.write('sfx7.wav',mix.astype(np.float32),SR,subtype='FLOAT'); print('sfx7 ok')
