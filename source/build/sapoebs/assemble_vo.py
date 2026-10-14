# Place polished lines on the script timecodes -> one 48k stereo VO track + timing json for the visuals.
import sys, json, numpy as np, soundfile as sf, subprocess
src, meta_p, out_wav, out_json = sys.argv[1:5]
meta = json.load(open(meta_p)); SR = 48000; T = 63.87
buf = np.zeros(int(T*SR)); timing = []
for m in meta:
    p = f"{src}/{m['i']:02d}.wav"
    tmp = p + ".48.wav"
    subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",p,"-ar",str(SR),"-ac","1",tmp],check=True)
    a, _ = sf.read(tmp)
    st = m["start"] - (0.35 if m["i"] == 0 else 0.05)   # line 0 would otherwise touch line 1
    i0 = int(st*SR); buf[i0:i0+len(a)] += a
    timing.append(dict(i=m["i"], start=round(st,3), end=round(st+len(a)/SR,3), text=m["text"]))
buf = buf/ max(1e-9, np.abs(buf).max()) * 0.89
sf.write(out_wav, np.stack([buf,buf],1), SR, subtype="PCM_24")
json.dump(timing, open(out_json,"w"), indent=1)
for t in timing: print(t["i"], t["start"], t["end"])
