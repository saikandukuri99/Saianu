import json,subprocess,os,math,glob
S='/tmp/claude-0/-home-user-Saianu/8dd9dd7e-6cc6-54e8-bd08-a2168bab399f/scratchpad'
OUT='/home/user/Saianu/output/EAI_final_v3_script/scene_clips_1080p';os.makedirs(OUT,exist_ok=True)
sc=json.load(open('vo/scenes_new.json'));total=json.load(open('vo/T_cues.json'))['total']
def tc(f):return '%02d-%02d-%02d-%02d'%(f//108000,f//1800%60,f//30%60,f%30)
def mk(src,name,f0,n):
    tmp=f'{S}/_t.mov'
    vf="format=gbrap,premultiply=inplace=1,scale=1920:1080:flags=lanczos,unpremultiply=inplace=1,format=argb"
    subprocess.run(['ffmpeg','-y','-v','error','-i',src,'-vf',vf,'-c:v','qtrle','-pix_fmt','argb',tmp],check=True)
    size=os.path.getsize(tmp);k=max(1,math.ceil(size/88e6))
    if k==1: os.replace(tmp,f'{OUT}/{name}__start_TC_{tc(f0)}.mov');return
    seg=math.ceil(n/k/30*1000)/1000
    subprocess.run(['ffmpeg','-y','-v','error','-i',tmp,'-c','copy','-f','segment','-segment_time',str(seg),'-reset_timestamps','1',f'{S}/_seg%02d.mov'],check=True)
    segs=sorted(glob.glob(f'{S}/_seg*.mov'));cur=f0
    for i,p in enumerate(segs):
        dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True).stdout)
        os.replace(p,f'{OUT}/{name}_part{i+1}of{len(segs)}__start_TC_{tc(cur)}.mov');cur+=round(dur*30)
    os.remove(tmp)
for i,k in enumerate(sorted(sc),1):
    mk(f'{S}/out4k/{k}.mov',f'EAI_Scene{i:02d}',sc[k]['f0'],sc[k]['n']);print(k,flush=True)
