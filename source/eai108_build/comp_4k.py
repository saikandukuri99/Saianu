# Composite the re-timed scene clips + logo + voice-over into ONE RGB-alpha file (QuickTime Animation video + PCM audio).
import json,subprocess
S='/tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad/out4k'
sc=json.load(open('vo/scenes_new.json'));T=json.load(open('vo/T_cues.json'))['total'];total=int(round(T*30))
old,new=json.load(open('vo/tmap.json'))
def ip(x):
    for i in range(len(old)-1):
        if old[i]<=x<=old[i+1]: return new[i]+(new[i+1]-new[i])*(x-old[i])/(old[i+1]-old[i])
lin,lout=ip(5.4),ip(102.9)
items=sorted((v['f0'],k) for k,v in sc.items())
ins=['-f','lavfi','-i',f'color=c=black@0.0:s=3840x2160:r=30:d={total/30:.4f},format=rgba']
fc='[0:v]format=rgba[b0];';last='[b0]'
for k,(f0,n) in enumerate(items,1):
    ins+=['-i',f'{S}/{n}.mov']
    fc+=f"[{k}:v]format=rgba,setpts=PTS-STARTPTS+{f0/30:.5f}/TB[c{k}];{last}[c{k}]overlay=eof_action=pass:format=auto[o{k}];";last=f'[o{k}]'
k=len(items)+1
ins+=['-loop','1','-framerate','30','-t',f'{total/30:.3f}','-i','/tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad/out4k/logo.png','-i','vo/VO_T.wav']
fc+=f"[{k}:v]format=rgba,fade=t=in:st={lin:.2f}:d=0.5:alpha=1,fade=t=out:st={lout:.2f}:d=0.4:alpha=1[lg];{last}[lg]overlay=format=auto[final]"
import sys
out=sys.argv[1]
subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',fc,'-map','[final]','-map',f'{k+1}:a','-frames:v',str(total),'-c:v','qtrle','-pix_fmt','argb','-c:a','pcm_s16le','-t',f'{total/30:.3f}',out],check=True)
print('done',out,total)
