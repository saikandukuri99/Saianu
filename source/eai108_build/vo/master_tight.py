import subprocess,re,json
import soundfile as sf
total=json.load(open('vo/T_cues.json'))['total']
chain="highpass=f=70,acompressor=threshold=-22dB:ratio=2:attack=15:release=150:makeup=2"
r=subprocess.run(['ffmpeg','-nostats','-i','vo/T_raw.wav','-af',chain+',ebur128','-f','null','-'],capture_output=True,text=True).stderr
I=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1]);gain=-16.0-I;print('integrated',I,'gain',round(gain,2))
subprocess.run(['ffmpeg','-y','-v','error','-i','vo/T_raw.wav','-af',f'{chain},volume={gain:.2f}dB,aresample=48000,pan=stereo|c0=c0|c1=c0,alimiter=limit=0.89,apad=whole_dur={total}','-t',str(total),'-c:a','pcm_s16le','vo/VO_T.wav'],check=True)
# captions timing + subtitles for the tight track (cap_A*.html pages are reused, same text)
cues=json.load(open('vo/T_cues.json'))['cues'];caps=[]
def ts(x):h=int(x//3600);m=int(x%3600//60);s=x%60;return '%02d:%02d:%06.3f'%(h,m,s)
with open('vo/subtitles_T.srt','w') as f:
    for i,c in enumerate(cues):
        nxt=cues[i+1]['start'] if i+1<len(cues) else total
        a=max(0,c['start']-0.05);b=min(c['end']+0.35,nxt-0.06)
        caps.append(dict(file=f'cap_A{i:02d}',start=round(a,2),end=round(b,2),text=c['text']))
        f.write(f"{i+1}\n{ts(a).replace('.',',')} --> {ts(b).replace('.',',')}\n{c['text']}\n\n")
json.dump(caps,open('vo/caps_T.json','w'),indent=1);print('ok',len(caps))
