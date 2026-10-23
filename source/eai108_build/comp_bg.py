# Final flat 4K MP4: looped background video + scene clips + logo + synced voice-over (no music).
import json,subprocess,sys
S='/tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad'
BG='/root/.claude/uploads/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/3671be6a-Background_video.mp4'
sc=json.load(open('vo/scenes_new.json'));T=json.load(open('vo/T_cues.json'))['total'];total=int(round(T*30))
old,new=json.load(open('vo/tmap.json'))
def ip(x):
    for i in range(len(old)-1):
        if old[i]<=x<=old[i+1]: return new[i]+(new[i+1]-new[i])*(x-old[i])/(old[i+1]-old[i])
lin,lout=ip(5.4),ip(102.9)
out,dur,codec=sys.argv[1],float(sys.argv[2]),sys.argv[3]
items=sorted((v['f0'],k) for k,v in sc.items())
ins=['-stream_loop','-1','-i',BG]
fc='[0:v]fps=30,scale=3840:2160:flags=bicubic,format=yuv420p,format=rgba[b0];';last='[b0]'
for k,(f0,n) in enumerate(items,1):
    ins+=['-i',f'{S}/out4k/{n}.mov']
    fc+=f"[{k}:v]format=rgba,setpts=PTS-STARTPTS+{f0/30:.5f}/TB[c{k}];{last}[c{k}]overlay=eof_action=pass:format=auto[o{k}];";last=f'[o{k}]'
k=len(items)+1
ins+=['-loop','1','-framerate','30','-t',f'{T:.3f}','-i',f'{S}/out4k/logo.png','-i','vo/VO_T.wav']
fc+=f"[{k}:v]format=rgba,fade=t=in:st={lin:.2f}:d=0.5:alpha=1,fade=t=out:st={lout:.2f}:d=0.4:alpha=1[lg];{last}[lg]overlay=format=auto,format=yuv420p[final]"
enc=['-c:v','libx265','-crf','14','-preset','fast','-tag:v','hvc1','-x265-params','log-level=error'] if codec=='hevc' else ['-c:v','libx264','-crf','19','-preset','medium']
subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',fc,'-map','[final]','-map',f'{k+1}:a','-t',str(dur),*enc,'-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','256k','-movflags','+faststart',out],check=True)
print('done',out)
