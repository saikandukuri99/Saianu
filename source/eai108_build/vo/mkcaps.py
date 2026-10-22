# One caption page per narration cue (text of the cue, bar style as in the earlier teaser), start/end taken from the generated voice-over.
import json,textwrap
def wrap(t,n=58):
    if len(t)<=n: return t
    w=textwrap.wrap(t,width=(len(t)//2)+8);return '<br>'.join(w[:2]) if len(w)<=2 else '<br>'.join(textwrap.wrap(t,width=n))
H='<!doctype html><html><head><meta charset=utf-8><link rel=stylesheet href=../lib/common.css><script src=../lib/common.js></script><style>.cp{position:absolute;left:0;width:1920px;bottom:46px;display:flex;justify-content:center}.cp div{font-size:42px;font-weight:700;line-height:1.25;text-align:center;padding:12px 32px 14px;border-radius:14px;background:rgba(7,14,56,.74);border:1.5px solid rgba(0,136,207,.35);text-shadow:0 2px 10px rgba(0,10,50,.7)}</style></head><body><div id=stage><div class=cp><div>%s</div></div></div><script>window.SCENE={VS:0,VE:1,N:1,nofade:true};window.ready=true;</script></body></html>'
A=json.load(open('vo/A_cues.json'));B=json.load(open('vo/B_intro_cues.json'))
def span(cues,i):
    c=cues[i];nxt=cues[i+1]['start'] if i+1<len(cues) else 108.5
    return max(0,c['start']-0.05),min(c['end']+0.35,nxt-0.08)
out={'A':[],'B':[]}
for name,cues in (('A',A),('B',B[:3]+[c for c in A if c['script_start']>=10.3])):
    for i,c in enumerate(cues):
        a,b=span(cues,i);fn=f"cap_{name}{i:02d}";open(f'scenes/{fn}.html','w').write(H%wrap(c['text']))
        out[name].append(dict(file=fn,start=round(a,2),end=round(b,2),text=c['text']))
json.dump(out,open('vo/caps.json','w'),indent=1)
with open('vo/subtitles_A.srt','w') as f:
    def ts(x):h=int(x//3600);m=int(x%3600//60);s=x%60;return '%02d:%02d:%06.3f'%(h,m,s)
    for n in ('A','B'):
        with open(f'vo/subtitles_{n}.srt','w') as f:
            for i,c in enumerate(out[n],1): f.write(f"{i}\n{ts(c['start']).replace('.',',')} --> {ts(c['end']).replace('.',',')}\n{c['text']}\n\n")
print(len(out['A']),len(out['B']))
