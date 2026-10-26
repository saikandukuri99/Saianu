import json, re, difflib
old=json.load(open('/home/claude/v6/build/lines6.json'))
NEW=[("q00a","Eighty percent of enterprise data is unstructured.","80% of enterprise data is unstructured."),
("q00b","Documents, emails, scans and images: no rows, no columns, no rules.","Documents, emails, scans and images: no rows, no columns, no rules."),
("q01a","And with no rules, it goes wherever people put it.","And with no rules, it goes wherever people put it."),
("q01b","So yours is everywhere: inboxes, drives, old servers, someone's laptop.","So yours is everywhere: inboxes, drives, old servers, someone's laptop."),
("q02a","Four moves change that.","Four moves change that."),
("q02b","Unify content: every source, one place, one set of rules.","Unify content: every source, one place, one set of rules."),
("q02c","Find and collaborate: search, share, and sign, safely.","Find and collaborate: search, share, and sign, safely."),
("q02d","Automate and govern: work that routes itself, and rules that keep themselves.","Automate and govern: work that routes itself, and rules that keep themselves."),
("q02e","Make content intelligent: Document A I, and the Solix A I Assistant.","Make content intelligent: Document AI, and the Solix AI Assistant."),
("q03","The problem: data sprawl. One project's files, in every version and format, scattered across multiple places and locations.","The problem: data sprawl. One project's files, in every version and format, scattered across multiple places and locations.")]
LL=NEW+[tuple(x) for x in old if x[0] not in ('q01a','q01b','q02','q03')]
A=json.load(open('asr_words.json'))
num={'1':'one','2':'two','3':'three','4':'four','to':'to'}
def nz(w): w=re.sub(r"[^a-z0-9']","",w.lower()); return num.get(w,w)
aw=[]
for w,a,b in A:
    parts=[p for p in re.split(r'[-\s]',w) if p]; d=(b-a)/max(1,len(parts))
    for i,p in enumerate(parts):
        n=nz(p)
        if n=='ai': aw+=[('a',a+i*d,a+i*d+d/2),('i',a+i*d+d/2,a+(i+1)*d)]; continue
        if n=='ecs': aw+=[('e',a+i*d,a+i*d+d/3),('c',a+i*d+d/3,a+i*d+2*d/3),('s',a+i*d+2*d/3,a+(i+1)*d)]; continue
        aw.append((n,a+i*d,a+(i+1)*d))
sw=[]
for key,t,cap in LL:
    for i,w in enumerate(t.split()): sw.append([key,i,w,nz(w),None,None])
sm=difflib.SequenceMatcher(a=[x[3] for x in sw],b=[x[0] for x in aw],autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size): s=sw[blk.a+k]; a=aw[blk.b+k]; s[4],s[5]=a[1],a[2]
for i,s in enumerate(sw):
    if s[4] is None:
        j=i-1
        while j>=0 and sw[j][4] is None: j-=1
        k=i+1
        while k<len(sw) and sw[k][4] is None: k+=1
        pa=sw[j][5] if j>=0 else 0; nb=sw[k][4] if k<len(sw) else pa+0.4; n=k-j
        s[4]=pa+(nb-pa)*(i-j)/n; s[5]=pa+(nb-pa)*(i-j+1)/n
C={}
for key,i,w,n,a,b in sw: C.setdefault(key,[]).append([w,round(a,3),round(b,3)])
OFF=41.7
CO={k:[[w,round(a-OFF,3),round(b-OFF,3)] for w,a,b in v] for k,v in C.items()}
# old code also references removed keys in guarded blocks; give placeholders
for k in ('q01a','q01b','q02','q03'):
    CO[k]=[[w,-100+i*0.1,-100+i*0.1+0.1] for i,w in enumerate(dict((x[0],x[1]) for x in old)[k].split())]
json.dump(C,open('cues_abs.json','w')); json.dump(LL,open('lines7.json','w'))
open('cues7.js','w').write('const CUES='+json.dumps(CO)+';\nconst CUESA='+json.dumps(C)+';')
un=[(s[0],s[2]) for s in sw if s[3] not in set(x[0] for x in aw)]
print('unmatched',un)
for k in ['q00a','q00b','q01a','q01b','q02a','q02b','q02c','q02d','q02e','q03','q04','q28','q29a','q30a','q30b']: print(k,C[k][0][1],C[k][-1][2])
