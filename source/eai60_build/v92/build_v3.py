import json,re,math,os
old=json.load(open('sents.json'));new=json.load(open('v92/sents_new.json'));prev=json.load(open('v91/sents_new.json'))
xs=[0.0];ys=[0.0]
def add(o,n):
    if o>xs[-1]+1e-6 and n>ys[-1]+1e-6: xs.append(o);ys.append(round(n,3))
    else: raise SystemExit(f"non-monotonic anchor {o} {n}")
sem=[s for s in new if s['old'] is None and 'semantic layer' in s['text']][0]
l06=[s for s in new if s['old']==12][0]
for s in new:
    if s['old'] is None: continue
    o=old[s['old']]
    if s['old']==4: add(8.86,sem['new_a']);add(8.93,sem['new_b'])
    add(o[1],s['new_a'])
    if s['old']==12: add(21.75,s['new_a']+0.12)
    add(o[2],s['new_b'])
    if s['old']==9:
        ea=s['new_b'];gap=l06['new_a']-ea
        add(old[10][1],ea+0.12);add(old[10][2],ea+0.12+gap*0.28);add(old[11][1],ea+0.12+gap*0.34);add(old[11][2],ea+0.12+gap*0.62)
    if s['old']==12: add(26.72,31.62);add(26.95,35.60)
json.dump([xs,ys],open('v92/tmap.json','w'))
open('build/web/lib/timemap.js','w').write(f"const TM_OLD={json.dumps(xs)},TM_NEW={json.dumps(ys)};\n")
def interp(x):
    if x<=xs[0]: return ys[0]+(x-xs[0])
    if x>=xs[-1]: return ys[-1]+(x-xs[-1])
    for i in range(len(xs)-1):
        if xs[i]<=x<=xs[i+1]: return ys[i]+(ys[i+1]-ys[i])*(x-xs[i])/(xs[i+1]-xs[i])
pm=json.load(open('v91/meta.json'))
names={1:'Hook',2:'Problem_Data',3:'Solix_Lockup',4:'Four_Services',5:'Data_Sense_AKG',6:'Data_Sense_XKG',7:'Data_Ask',8:'AI_Warehouse',9:'Agentic',10:'Open_Platform',11:'Trust',12:'End_Card'}
meta={};jobs=[];reuse={}
os.makedirs('new92',exist_ok=True)
for n,nm in names.items():
    s=open(f'build/web/scenes/s{n:02d}.html').read()
    vs=float(re.search(r'VS:([\d.]+)',s).group(1));ve=float(re.search(r'VE:([\d.]+)',s).group(1))
    f0=max(0,math.floor(interp(vs)*30+1e-6));f1=math.ceil(interp(ve)*30-1e-6)
    p=pm[str(n)];meta[str(n)]=dict(name=nm,f0=f0,f1=f1)
    same_len=(f1-f0)==(p['f1']-p['f0'])
    if n==1 or (n>=8 and n!=7 and f0-p['f0']==120 and same_len): reuse[n]=f"new91/S{n:02d}_{p['f0']}.mov"; os.system(f"cp {reuse[n]} new92/S{n:02d}_{f0}.mov")
    else: jobs.append(f"s{n:02d} /tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad/new92/S{n:02d}_{f0}.mov")
    print(n,nm,round(f0/30,2),round(f1/30,2),'REUSE' if n in reuse else 'render')
meta['cl']=dict(name='Data_Sense_ContentLibrary',f0=948,f1=1074)
jobs.append("cl /tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad/new92/CL_948.mov")
open('build/jobs7.txt','w').write('\n'.join(jobs)+'\n');json.dump(meta,open('v92/meta.json','w'))
