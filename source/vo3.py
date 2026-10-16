import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt, fftconvolve
START={"c1":0.35,"c2":1.70,"c3":3.05,"n1":4.70,"n2a":7.95,"n2b":10.25,"n2c":12.50,"n2d":14.70,
"n3":18.95,"n4a":25.00,"n4b":27.30,"n5":29.95,"n6":34.15,"n7":39.15,"n8":45.15,"n9a":53.05,"n9b":54.45,"n10a":56.45,"n10b":58.60}
SR=48000; T=60.0; mix=np.zeros(int(SR*T))
rng=np.random.default_rng(3)
# small room IR for off-mic cold-open voices
ir=np.zeros(int(.35*SR)); ir[0]=1
t=np.arange(len(ir))/SR; ir+= rng.normal(0,1,len(ir))*np.exp(-t/0.07)*0.18
for k,s0 in START.items():
    a,sr=sf.read(f"/home/claude/tts/lines_v3/{k}.wav"); a=resample_poly(a,2,1)
    if k.startswith("c"):
        a=sosfilt(butter(2,90,btype="high",fs=SR,output="sos"),a)*0.95
    f=int(.008*SR); a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f)
    i=int(s0*SR); mix[i:i+len(a)]+=a[:len(mix)-i]
# gentle warmth: low shelf-ish + de-harsh
mix=mix+0.30*sosfilt(butter(2,[140,420],btype="band",fs=SR,output="sos"),mix)   # warmth
mix=mix-0.22*sosfilt(butter(2,[2400,4800],btype="band",fs=SR,output="sos"),mix) # ease presence/harshness
mix=mix-0.35*sosfilt(butter(2,6500,btype="high",fs=SR,output="sos"),mix)        # soften sibilance/air
mix=sosfilt(butter(2,70,btype="high",fs=SR,output="sos"),mix)
sf.write("out/vo3_raw.wav",mix,SR,subtype="FLOAT")
words=json.load(open("/home/claude/tts/lines_v3/words.json"))
W=[]
for k,s0 in START.items():
    for w,a,b in words[k]: W.append([k,w,round(s0+a,3),round(s0+b,3)])
json.dump({"start":START,"words":W},open("timing3.json","w"),indent=0)
