import soundfile as sf, json, numpy as np
from kokoro_onnx import Kokoro
k=Kokoro("kokoro-v1.0.onnx","voices-v1.0.bin")
N="am_michael"
L=[
("c1","af_heart",1.0,"Who opened this file?"),
("c2","am_fenrir",0.98,"What's on legal hold?"),
("c3","am_puck",1.0,"Who approved this deletion?"),
("n1",N,0.95,"Every regulated team gets asked to prove it."),
("n2a",N,0.95,"Most teams pay a tax to answer."),
("n2b",N,0.95,"A premium tier for legal hold."),
("n2c",N,0.95,"A separate portal for clients."),
("n2d",N,0.95,"Maintenance on an old archive, kept alive for retention."),
("n3",N,1.06,"And now, every file kept past its schedule is something an AI assistant can find."),
("n4a",N,0.9,"You shouldn't have to pay extra"),
("n4b",N,0.88,"to prove you did the right thing."),
("n5",N,1.0,"Solix Cloud, E C S, puts the proof in every plan."),
("n6",N,1.06,"Share with clients through secure links, and every view lands in the audit trail."),
("n7",N,1.1,"Keep it on your retention schedule, under legal hold, with deletion that waits for an approver."),
("n8",N,1.12,"Retire old Exchange mailboxes and P S T files to their owners, under hold, then switch the old archive off."),
("n9a",N,0.95,"Published pricing."),
("n9b",N,0.95,"A thirty-day trial."),
("n10a",N,0.92,"Solix Cloud, E C S."),
("n10b",N,0.88,"Keep the proof."),
]
out={}
for i,v,sp,t in L:
    s,sr=k.create(t,voice=v,speed=sp,lang="en-us")
    # trim silence
    a=np.abs(s); idx=np.where(a>0.01)[0]; s=s[max(0,idx[0]-int(.02*sr)):idx[-1]+int(.06*sr)]
    sf.write(f"lines/{i}.wav",s,sr); out[i]=round(len(s)/sr,3); print(i,out[i],t)
json.dump(out,open("lines/dur.json","w"))
