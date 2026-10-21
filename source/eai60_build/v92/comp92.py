import json,subprocess,sys,glob
M=json.load(open('v92/meta.json'));out=sys.argv[1]
items=[]
for k,m in M.items():
    f=glob.glob(f"new92/{'CL' if k=='cl' else 'S%02d'%int(k)}_{m['f0']}.mov")[0];items.append((m['f0'],f))
items.sort()
ins=['-f','lavfi','-i','color=c=black@0.0:s=1920x1080:r=30:d=94,format=rgba']
fc='[0:v]format=rgba[b0];';last='[b0]'
for k,(f0,f) in enumerate(items,1):
    ins+=['-i',f]
    fc+=f"[{k}:v]format=rgba,setpts=PTS-STARTPTS+{f0/30:.5f}/TB[c{k}];{last}[c{k}]overlay=eof_action=pass:format=auto[o{k}];";last=f'[o{k}]'
k=len(items)+1
ins+=['-loop','1','-framerate','30','-t','94','-i','build/frames/logo.png']
fc+=f"[{k}:v]format=rgba,fade=t=in:st=0.15:d=0.6:alpha=1,fade=t=out:st=93.6:d=0.4:alpha=1[lg];{last}[lg]overlay=format=auto[final]"
subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',fc,'-map','[final]','-t','94','-c:v','qtrle','-pix_fmt','argb',out],check=True)
