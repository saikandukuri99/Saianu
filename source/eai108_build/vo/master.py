# Master the raw Kokoro tracks: high-pass, gentle compression, loudness matched to the Application Retirement video (-16 LUFS), 48 kHz stereo.
import subprocess,re,sys
import numpy as np, soundfile as sf
SR=24000
A,_=sf.read('vo/A_raw.wav');B,_=sf.read('vo/B_intro_raw.wav')
# Version B = its own 0:00-0:10.3 intro + the same narration as A from 0:10.3
cut=int(10.3*SR);fade=int(0.02*SR)
Bf=A.copy();Bf[:cut]=B[:cut]
Bf[cut-fade:cut]*=np.linspace(1,0,fade) if False else 1
sf.write('vo/A_full.wav',A,SR);sf.write('vo/B_full.wav',Bf,SR);sf.write('vo/B_intro_only.wav',B[:cut],SR)
chain="highpass=f=70,acompressor=threshold=-22dB:ratio=2:attack=15:release=150:makeup=2"
def measure(f):
    r=subprocess.run(['ffmpeg','-nostats','-i',f,'-af',chain+',ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1])
I=measure('vo/A_full.wav');gain=-16.0-I;print('A integrated',I,'gain',round(gain,2))
for src,dst in [('A_full','VO_A'),('B_full','VO_B'),('B_intro_only','VO_B_intro')]:
    subprocess.run(['ffmpeg','-y','-v','error','-i',f'vo/{src}.wav','-af',f'{chain},volume={gain:.2f}dB,aresample=48000,pan=stereo|c0=c0|c1=c0,alimiter=limit=0.89','-c:a','pcm_s16le',f'vo/{dst}.wav'],check=True)
print('done')
