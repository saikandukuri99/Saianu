import json
C={}
for k,w,a,b in json.load(open('timing3.json'))['words']: C.setdefault(k,[]).append((a,b))
# (line key, first word idx, last word idx, text)
CH=[("c1",0,3,"Who opened this file?"),("c2",0,3,"What's on legal hold?"),("c3",0,3,"Who approved this deletion?"),
("n1",0,7,"Every regulated team gets asked to prove it."),
("n2a",0,6,"Most teams pay a tax to answer."),("n2b",0,5,"A premium tier for legal hold."),("n2c",0,4,"A separate portal for clients."),
("n2d",0,4,"Maintenance on an old archive,"),("n2d",5,8,"kept alive for retention."),
("n3",0,7,"And now, every file kept past its schedule"),("n3",8,14,"is something an AI assistant can find."),
("n4a",0,5,"You shouldn't have to pay extra"),("n4b",0,6,"to prove you did the right thing."),
("n5",0,9,"SOLIX ECS puts the proof in every plan."),
("n6",0,5,"Share with clients through secure links,"),("n6",6,13,"and every view lands in the audit trail."),
("n7",0,5,"Keep it on your retention schedule,"),("n7",6,8,"under legal hold,"),("n7",9,15,"with deletion that waits for an approver."),
("n8",0,8,"Retire old Exchange mailboxes and PST files"),("n8",9,13,"to their owners, under hold,"),("n8",14,19,"then switch the old archive off."),
("n9a",0,1,"Published pricing."),("n9b",0,2,"A thirty-day trial."),("n10a",0,3,"SOLIX ECS."),("n10b",0,2,"Keep the proof.")]
ev=[]
for i,(k,a,b,txt) in enumerate(CH):
    s=C[k][a][0]-0.05; e=C[k][b][1]+0.35; ev.append([round(s,2),round(e,2),txt])
for i in range(len(ev)-1):
    if ev[i][1]>ev[i+1][0]-0.04: ev[i][1]=round(ev[i+1][0]-0.04,2)
ev[-1][1]=60.0
def tc(x):
    ms=int(round(x*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
open('out/ECS_KeepTheProof_v3_Captions.srt','w').write("\n".join(f"{i+1}\n{tc(s)} --> {tc(e)}\n{t}\n" for i,(s,e,t) in enumerate(ev)))
open('capdata3.js','w').write('const CAPS='+json.dumps(ev)+';')
print(len(ev)); print(open('out/ECS_KeepTheProof_v3_Captions.srt').read()[:400])
