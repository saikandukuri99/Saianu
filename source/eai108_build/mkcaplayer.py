# Caption layer as its own RGB-alpha clip (cues timed to the voice-over); fades 0.2 s in/out.
import json,subprocess,sys
from PIL import Image
S='/tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad/out108'
caps=json.load(open('vo/caps.json'))
for name,total in (('A',108.5),('B',108.5)):
    ins=['-f','lavfi','-i',f'color=c=black@0.0:s=1920x1080:r=30:d={total},format=rgba'];fc='[0:v]format=rgba[b0];';last='[b0]'
    for k,c in enumerate(caps[name],1):
        im=Image.open(f"{S}/caps/{c['file']}.png").convert('RGBA').crop((0,860,1920,1040));p=f"{S}/caps/{c['file']}_crop.png";im.save(p)
        ins+=['-loop','1','-framerate','30','-t',str(total),'-i',p]
        fc+=f"[{k}:v]format=rgba,fade=t=in:st={c['start']}:d=0.2:alpha=1,fade=t=out:st={c['end']-0.2:.2f}:d=0.2:alpha=1[c{k}];{last}[c{k}]overlay=y=860:format=auto:shortest=0[o{k}];";last=f'[o{k}]'
    fc=fc.rstrip(';')
    subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',fc,'-map',last,'-frames:v',str(int(total*30)),'-c:v','qtrle','-pix_fmt','argb',f'{S}/captions_{name}.mov'],check=True)
    print('done',name)
