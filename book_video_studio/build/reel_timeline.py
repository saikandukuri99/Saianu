#!/usr/bin/env python3
"""Cut a short vertical reel out of episode 2: picks sentences, remaps times contiguously.
writes renderer_reel/timeline.js and episodes/ep02_one_car/reel_plan.json"""
import json, subprocess, os
EP = os.environ.get('EP','episodes/ep02_one_car'); SRC = os.environ.get('SRC','renderer_ep2'); OUT = os.environ.get('OUT','renderer_reel')
PICKS = os.environ.get('PICKS','1.1,1.3,1.4,2.1,2.4,3.3,3.4,3.5,3.8,4.1,4.3,4.5').split(',')
TL = json.loads(subprocess.check_output(['node', '-e', "global.window={};eval(require('fs').readFileSync('"+SRC+"/timeline.js','utf8'));console.log(JSON.stringify(window.TL))"]))
by = {s['id']: s for s in TL['sentences']}
out, segs, t = [], [], 0.0
for pid in PICKS:
    s = dict(by[pid]); o0 = s['start']; o1 = s['end']
    if pid == PICKS[-1]: o1 = min(s['end'], s['ve'] + .55)
    d = o1 - o0; sh = t - o0
    s['start'], s['end'], s['dur'] = round(t, 3), round(t + d, 3), round(d, 3)
    for k in ('vs', 've'): s[k] = round(s[k] + sh, 3)
    s['chunks'] = [dict(c, t0=round(c['t0'] + sh, 3), t1=round(min(c['t1'], o1) + sh, 3)) for c in s['chunks']]
    s['trans'] = 'fade'
    out.append(s); segs.append({'id': pid, 'o0': o0, 'o1': o1, 'n0': t}); t += d
TL2 = {'fps': 30, 'total': round(t, 3), 'brand': '', 'sentences': out}
open(OUT+'/timeline.js', 'w').write('window.TL=' + json.dumps(TL2, ensure_ascii=False) + ';')
json.dump({'total': TL2['total'], 'segs': segs}, open(f'{EP}/reel_plan.json', 'w'), indent=1)
print('reel length', TL2['total'])
