import soundfile as sf, numpy as np, json
S=json.load(open("sents.json"));SR=24000;N=int(62.31*SR);y=np.zeros(N);ends=[]
for i,s in enumerate(S):
    a,_=sf.read(f"vof2/f{i:02d}.wav");st=int(s[1]*SR)
    if st+len(a)>N: a=a[:N-st]
    y[st:st+len(a)]+=a;ends.append((i,round(s[1],2),round(s[1]+len(a)/SR,2)))
    if i+1<len(S) and s[1]+len(a)/SR>S[i+1][1]: print("OVERLAP",i)
sf.write("vof2/raw.wav",y,SR)
