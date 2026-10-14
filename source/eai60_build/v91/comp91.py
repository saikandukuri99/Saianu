import json,subprocess,sys
M=json.load(open('v91/meta.json'));out=sys.argv[1]
ins=['-f','lavfi','-i','color=c=black@0.0:s=1920x1080:r=30:d=90,format=rgba']
fc='[0:v]format=rgba[b0];';last='[b0]'
for k,(n,m) in enumerate(sorted(M.items(),key=lambda x:int(x[0])),1):
    ins+=['-i',f"new91/S{int(n):02d}_{m['f0']}.mov"]
    fc+=f"[{k}:v]format=rgba,setpts=PTS-STARTPTS+{m['f0']/30:.5f}/TB[c{k}];{last}[c{k}]overlay=eof_action=pass:format=auto[o{k}];";last=f'[o{k}]'
k=len(M)+1
ins+=['-loop','1','-framerate','30','-t','90','-i','build/frames/logo.png']
fc+=f"[{k}:v]format=rgba,fade=t=in:st=0.15:d=0.6:alpha=1,fade=t=out:st=89.6:d=0.4:alpha=1[lg];{last}[lg]overlay=format=auto[final]"
subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',fc,'-map','[final]','-t','90','-c:v','qtrle','-pix_fmt','argb',out],check=True)
