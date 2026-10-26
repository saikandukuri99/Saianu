import json
C=json.load(open('cues_abs.json')); LL=json.load(open('lines7.json'))
ev=[]
for key,t,cap in LL:
    W=C[key]; cw=cap.split(); n=len(W); m=len(cw)
    tw=lambda i: W[min(n-1,round(i*(n-1)/max(1,m-1)))] if m>1 else W[0]
    chunks=[(0,m-1)]
    if len(cap)>48:
        cands=[i for i,w in enumerate(cw[:-1]) if w[-1] in ',:.']
        if cands:
            if len(cap)>90 and len(cands)>=2:
                best=sorted(cands,key=lambda i:abs(len(' '.join(cw[:i+1]))-len(cap)/3))[0]
                rest=[i for i in cands if i>best+1]
                b2=sorted(rest,key=lambda i:abs(len(' '.join(cw[:i+1]))-2*len(cap)/3))[0] if rest else None
                chunks=[(0,best),(best+1,b2),(b2+1,m-1)] if b2 else [(0,best),(best+1,m-1)]
            else:
                best=min(cands,key=lambda i:abs(len(' '.join(cw[:i+1]))-len(cap)/2)); chunks=[(0,best),(best+1,m-1)]
    for a,b in chunks: ev.append([round(tw(a)[1]-0.05,2),round(min(tw(b)[2],tw(b)[1]+1.0)+0.3,2),' '.join(cw[a:b+1])])
ev.sort()
for i in range(len(ev)-1):
    if ev[i][1]>ev[i+1][0]-0.04: ev[i][1]=round(ev[i+1][0]-0.04,2)
ev[-1][1]=171.0
def tc(x):
    ms=int(round(x*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
open('SolixECS_FourMoves_v5_Captions.srt','w').write("\n".join(f"{i+1}\n{tc(s)} --> {tc(e)}\n{t}\n" for i,(s,e,t) in enumerate(ev)))
open('capdata7.js','w').write('const CAPS='+json.dumps(ev)+';')
for e in ev[-14:]: print(e)
