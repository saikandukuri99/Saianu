import numpy as np, soundfile as sf
SR=48000
vo,_=sf.read('vo7_norm.wav'); mu,_=sf.read('music7.wav'); fx,_=sf.read('sfx7.wav')
n=min(len(vo),len(mu),len(fx)); vo=vo[:n]; mu=mu[:n]; fx=fx[:n]
ref,_=sf.read('/home/claude/v4/music_raw.wav')
def r(x,a,b): s=x[int(a*SR):int(b*SR)]; return np.sqrt((s**2).mean())
k=np.mean([r(ref,a,b)/r(mu,a+41.7,b+41.7) for a,b in [(20,34),(45,63),(75,93)]])*10**(-3.33/20); mu=mu*k
e=np.abs(vo); win=int(0.02*SR); e=np.convolve(e,np.ones(win)/win,'same')
on=(e>10**(-40/20)).astype(float); la=int(0.06*SR); on=np.maximum(on,np.r_[on[la:],np.zeros(la)])
ctl=on[::48]; sm=np.zeros_like(ctl); s=0
ka=1-np.exp(-1/(0.04*1000)); kr=1-np.exp(-1/(0.35*1000))
for i,c in enumerate(ctl): s+=(ka if c>s else kr)*(c-s); sm[i]=s
g=np.repeat(sm,48)[:n]; duck=10**((-7*g)/20); lvl=10**(1/20); fxg=10**(-5/20)*10**((-3*g)/20)
music=mu*lvl*duck[:,None]; sfx=fx*fxg[:,None]
sf.write('out/SolixECS_FourMoves_v5_MUSIC_only_48k24.wav',(mu*lvl).astype(np.float32),SR,subtype='PCM_24')
sf.write('out/SolixECS_FourMoves_v5_SFX_only_48k24.wav',(fx*10**(-5/20)).astype(np.float32),SR,subtype='PCM_24')
sf.write('out/SolixECS_FourMoves_v5_VO_48k24.wav',np.stack([vo,vo],1).astype(np.float32),SR,subtype='PCM_24')
sf.write('mix7_raw.wav',(np.stack([vo,vo],1)+music+sfx).astype(np.float32),SR,subtype='FLOAT')
def rr(x): return round(20*np.log10(np.sqrt((x**2).mean())+1e-12),1)
for a,b,nm in [(30,44,'trailer'),(60,62,'move1'),(115.3,119.2,'move3'),(160,164.5,'recap')]:
    i,j=int(a*SR),int(b*SR); print(nm,'VO',rr(vo[i:j]),'music',rr(music[i:j].mean(1)),'sfx',rr(sfx[i:j].mean(1)))
