import json,sys
sys.path.insert(0,'.')
from lines import L
T=json.load(open('lines/timing.json'))
ev=[]
for key,s0,s1,sp,t,cap in L:
    W=T[key]['words']; cw=cap.split()
    # map caption words to spoken words proportionally (spoken may have spelled acronyms)
    n=len(W); m=len(cw)
    def tw(i): return W[min(n-1,round(i*(n-1)/max(1,m-1)))] if m>1 else W[0]
    chunks=[(0,m-1)]
    if len(cap)>48:
        best=None
        for i,w in enumerate(cw[:-1]):
            if w.endswith(',') or w.endswith(':'):
                l=len(' '.join(cw[:i+1])); sc=abs(l-len(cap)/2)
                if best is None or sc<best[0]: best=(sc,i)
        if best: chunks=[(0,best[1]),(best[1]+1,m-1)]
    for a,b in chunks:
        ev.append([round(tw(a)[1]-0.05,2),round(tw(b)[2]+0.35,2),' '.join(cw[a:b+1])])
for i in range(len(ev)-1):
    if ev[i][1]>ev[i+1][0]-0.04: ev[i][1]=round(ev[i+1][0]-0.04,2)
def tc(x):
    ms=int(round(x*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
open('out/SolixECS_FourMoves_Captions.srt','w').write("\n".join(f"{i+1}\n{tc(s)} --> {tc(e)}\n{t}\n" for i,(s,e,t) in enumerate(ev)))
open('capdata.js','w').write('const CAPS='+json.dumps(ev)+';')
print(len(ev)); [print(e) for e in ev if len(e[2])>50]
