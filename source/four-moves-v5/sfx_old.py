import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; DUR=130.9; N=int(SR*DUR)
rng=np.random.default_rng(11)
C=json.load(open('cues_old.json'))
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
# ---------- events ----------
# Q01 windows light up
for k,i in [(0,0),(1,1),(2,1),(3,2),(4,3),(5,4)]:
    put(ping(1175+80*k),ws('q01b',i)+(0.15 if k==2 else 0),0.8,(-0.5+0.2*k))
# Q02 four chimes + tiles shrink
for i,f in enumerate([1174.7,1480,1760,2349]): put(bell(f,1.2,0.9),9.25+i*0.09,1.0,-0.45+0.3*i)
put(whoosh(0.5),10.35,0.5)
# problems: pings + error tone, risers into snaps, impacts on snaps
for i in range(7): put(ping(1047),11.3+i*0.22,0.7,-0.6+0.2*i)
put(error(),13.7,1.0)
for i in range(14): put(ping(1047+(i%3)*90),36.1+i*0.24,0.55,0.4)
put(error(),39.3,1.0)
for tt in (65.9,66.6,67.3): put(ping(990),tt,0.7)
put(error(),68.0,1.0)
for i in range(12): put(key(),95.6+i*0.24,0.8,0.2)
put(error(),96.9,1.0)
for s0 in (15.6,41.0,69.7,98.8):
    put(riser(1.0),s0-1.0,0.75); put(impact(),s0,0.9); put(whoosh(0.4),s0-0.05,0.5)
put(shimmer(),98.9,0.8)
# Move 01
put(whoosh(0.6),18.2,0.6,0.4); put(thud(),18.95,0.9)
for i in range(10): put(pop(650+i*25),19.2+i*0.08,0.5,-0.3+0.06*i)
put(success(),19.85,0.8)
put(whoosh(0.35),20.4,0.45); put(click(),21.55,1.0); put(whoosh(0.4),21.8,0.5,0.5)
for i in range(3): put(pop(800),22.0+i*0.2,0.7,0.6)
put(success(),22.85,0.7,0.5); put(whoosh(0.5),22.95,0.55,-0.2)
put(whoosh(0.35),23.55,0.45); put(click(),ws('q07',3)-0.05,1.0)
ps=ws('q07',6)-0.1; put(whoosh(0.5,up=False),ps-0.4,0.5)
for i in range(22): put(tick(),ps+i*0.07,0.8,0.3)
put(whoosh(0.35),27.75,0.45)
for tt in (ws('q08',1),ws('q08',2)+0.1,ws('q08',5)+0.1): put(click(),tt,1.0); put(pop(900),tt+0.05,0.5)
put(success(),31.5,0.8)
put(whoosh(0.4),32.4,0.45)
for i in range(7): put(whoosh(0.5),32.55+i*0.08,0.18,-0.8+0.27*i)
put(impact()[:int(0.9*SR)],33.6,0.45)
for i in range(3): put(pop(700+i*120),ws('q09',6)+i*0.15,0.6)
# Move 02
put(whoosh(0.35),44.7,0.45)
for i in range(9): put(key(),45.0+i*0.09,0.8)
for i in range(3): put(ping(1568),ws('q12',2)+i*0.35,0.5,0.3)
put(whoosh(0.35),48.7,0.45); put(pop(600),ws('q13',4),0.6)
put(thud()*0.6,ws('q13',8)-0.05,0.6); put(thud()*0.6,ws('q13',8)+0.25,0.6)
put(whoosh(0.35),52.8,0.45); put(click(),ws('q14',6),0.9); put(click(),ws('q14',8),0.9); put(click(),56.6,1.0); put(whoosh(0.4),56.8,0.5,0.4)
put(whoosh(0.35),57.8,0.45); put(pop(750),ws('q15',1),0.6); put(pop(850),ws('q15',1)+0.15,0.6)
put(click(),ws('q15',5),1.0); put(scratch(0.8),60.2,1.0,0.6); put(success(),61.1,0.8,0.5)
for i in range(6): put(whoosh(0.3),62.6+i*0.1,0.12)
put(bell(1568,1.2),63.5,0.9); put(bell(2093,1.2),63.58,0.6)
# Move 03
put(whoosh(0.35),73.1,0.45); put(whoosh(0.6),73.35,0.5,0.5); put(thud(),74.1,0.8)
ap=ws('q19',4)+0.1; put(click(),ap,1.0)
for k,tt in enumerate((ap+0.15,ap+0.7,ap+1.3)): put(pop(700+k*140),tt,0.6)
put(success(),ap+0.25,0.6,0.5)
put(whoosh(0.35),77.5,0.45)
for i in range(3): put(bell(1760+i*220,0.8,0.6),78.3+i*0.2,0.8,0.5)
put(stamp(),ws('q20',5)+0.2,0.9)
put(whoosh(0.35),82.3,0.45); put(lock(),ws('q21',2)-0.05,1.0)
for i in range(5): put(tick()*1.5,ws('q21',2)+0.1+i*0.12,0.9,0.3)
put(whoosh(0.35),85.1,0.45)
for wi in (0,1,3): put(pop(800),ws('q22',wi)+0.05,0.7,0.5)
for j in range(3): put(click()*0.6,ws('q22',0)+0.6+j*0.15,0.8)
put(whoosh(0.4),90.55,0.45)
for i in range(8): put(tick(),91.0+i*0.17,1.0,-0.2)
put(click(),ws('q23',8),1.0); put(thud(),ws('q23',8)+0.45,0.8,0.5)
# Move 04
put(whoosh(0.35),101.2,0.45)
for i in range(4): put(tick()*1.3,ws('q26',3)+i*0.32,1.0); put(pop(900+i*80),ws('q26',3)+i*0.32+0.25,0.4)
put(whoosh(0.35),105.6,0.45); put(click(),106.0,1.0)
for i in range(5): put(ping(1760),106.25+i*0.08,0.35,0.3)
put(whoosh(0.35),107.7,0.45); put(shimmer(),ws('q28',3)-0.05,0.6)
put(click(),108.95,1.0);put(whoosh(0.4),109.0,0.5,0.4);put(pop(700),ws('q28',7)-0.15,0.6); put(pop(800),ws('q28',9)+0.2,0.6); put(pop(700),ws('q28',10)-0.05,0.6)
put(bell(1318.5,1.4,1.0),ws('q28',14)+0.1,0.8); put(bell(1975.5,1.4,0.6),ws('q28',14)+0.18,0.6)
for i in range(3): put(pop(950+i*100),ws('q28',20)-0.1+i*0.12,0.6,0.5)
# recap flips + end
for i,k in enumerate(('q29a','q29b','q29c','q29d')):
    put(flip(),st(k)-0.05,0.8,-0.4+0.27*i); put(bell([1174.7,1480,1760,2349][i],1.2),st(k)+0.12,0.7)
put(riser(1.0),122.2,0.7); put(impact(),123.2,0.85)
for i,f in enumerate([587.3,880,1174.7]): put(bell(f,2.6,1.3),123.3+i*0.12,0.9,-0.2+0.2*i)
# short room
def rev(x):
    n=int(0.9*SR); t=np.arange(n)/SR; ir=rng.standard_normal(n)*np.exp(-t/0.15); ir=lp(ir,7000); ir/=np.sqrt((ir**2).sum())
    return fftconvolve(x,ir)[:N]
L=L+0.18*rev(L); R=R+0.18*rev(R)
mix=np.stack([L,R],1)
sf.write('sfx_old.wav',mix.astype(np.float32),SR,subtype='FLOAT'); print('sfx ok')
