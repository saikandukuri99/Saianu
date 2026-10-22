# Composite the scene clips (+ logo) into the full RGB-alpha video and cut it into <100 MB pieces.
# usage: comp108.py A|B_intro outdir
import subprocess,sys,os
S='/tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad/out108'
mode,outdir=sys.argv[1],sys.argv[2]
if mode=='A':
    items=[('s01',0),('s02',159),('s03',300),('s04',588),('s05',876),('s06',1341),('s07',1785),('s08',2115),('s09',2430),('s10',2745),('s11',3096)]
    total=3255;seg=240;logo_in=5.4;logo_out=102.9
else:
    items=[('b12',0),('s02b',210),('s03',300)];total=309;seg=240;logo_in=0.15;logo_out=None
ins=['-f','lavfi','-i',f'color=c=black@0.0:s=1920x1080:r=30:d={total/30:.4f},format=rgba']
fc='[0:v]format=rgba[b0];';last='[b0]'
for k,(n,f0) in enumerate(items,1):
    ins+=['-i',f'{S}/{n}.mov']
    fc+=f"[{k}:v]format=rgba,setpts=PTS-STARTPTS+{f0/30:.5f}/TB[c{k}];{last}[c{k}]overlay=eof_action=pass:format=auto[o{k}];";last=f'[o{k}]'
k=len(items)+1
ins+=['-loop','1','-framerate','30','-t',f'{total/30:.3f}','-i',f'{S}/logo.png']
lg=f"[{k}:v]format=rgba,fade=t=in:st={logo_in}:d=0.5:alpha=1"+(f",fade=t=out:st={logo_out}:d=0.4:alpha=1" if logo_out else "")+"[lg]"
fc+=lg+f";{last}[lg]overlay=format=auto[final]"
cuts=','.join(str(i) for i in range(seg,total,seg))
os.makedirs(outdir,exist_ok=True)
cmd=['ffmpeg','-y','-v','error',*ins,'-filter_complex',fc,'-map','[final]','-frames:v',str(total),'-c:v','qtrle','-pix_fmt','argb']
if total>seg: cmd+=['-f','segment','-segment_format','mov','-segment_frames',cuts,'-reset_timestamps','1',f'{outdir}/part%02d.mov']
else: cmd+=[f'{outdir}/part00.mov']
subprocess.run(cmd,check=True)
print('done',mode)
