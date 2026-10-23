import json, re, difflib, sys
sys.path.insert(0,'.')
from lines_v4 import L
Q28S="Then ask the Solix A I assistant. Summarize a file, ask about a whole folder, and every answer comes with its sources."
Q28C="Then ask the Solix AI Assistant. Summarize a file, ask about a whole folder, and every answer comes with its sources."
LL=[]
for key,s0,s1,sp,t,cap in L:
    if key=='q28': t,cap=Q28S,Q28C
    LL.append((key,t,cap))
A=json.load(open('/home/claude/v6/sep/asr_words.json'))
num={'1':'one','2':'two','3':'three','4':'four'}
def nz(w): w=re.sub(r"[^a-z0-9']","",w.lower()); return num.get(w,w)
aw=[]
for w,a,b in A:
    parts=[p for p in re.split(r'[-\s]',w) if p]
    if len(parts)>1 and parts[0].lower()=='ecs': pass
    d=(b-a)/len(parts)
    for i,p in enumerate(parts):
        n=nz(p)
        if n=='ai': aw+= [('a',a+i*d,a+i*d+d/2),('i',a+i*d+d/2,a+(i+1)*d)]; continue
        aw.append((n,a+i*d,a+(i+1)*d))
sw=[]
for key,t,cap in LL:
    for i,w in enumerate(t.split()): sw.append([key,i,w,nz(w),None,None])
sm=difflib.SequenceMatcher(a=[x[3] for x in sw],b=[x[0] for x in aw],autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        s=sw[blk.a+k]; a=aw[blk.b+k]; s[4],s[5]=a[1],a[2]
# interpolate unmatched
for i,s in enumerate(sw):
    if s[4] is None:
        j=i-1
        while j>=0 and sw[j][4] is None: j-=1
        k=i+1
        while k<len(sw) and sw[k][4] is None: k+=1
        pa=sw[j][5] if j>=0 else 0; nb=sw[k][4] if k<len(sw) else pa+0.4
        n=k-j; f=(i-j)/n; s[4]=pa+(nb-pa)*f-0.0; s[5]=pa+(nb-pa)*(i-j+1)/n
miss=sum(1 for s in sw if s[4] is None)
C={}
for key,i,w,n,a,b in sw: C.setdefault(key,[]).append([w,round(a,3),round(b,3)])
json.dump(C,open('cues6.json','w'))
open('cues6.js','w').write('const CUES='+json.dumps(C)+';')
json.dump(LL,open('lines6.json','w'))
um=[(s[0],s[2]) for s in sw if s[3] not in [x[0] for x in aw]]
print('script words',len(sw),'unmatched-ish',um[:20])
for k in ['q03','q09','q10','q15','q16','q17','q22','q23','q24','q28','q29a','q30a','q30b']: print(k,C[k][0][1],C[k][-1][2],' '.join(w for w,_,_ in C[k])[:60])
