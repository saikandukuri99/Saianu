import sherpa_onnx, soundfile as sf, numpy as np, json, sys
from scipy.signal import resample_poly
d='sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'
rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{d}/encoder.int8.onnx',decoder=f'{d}/decoder.int8.onnx',joiner=f'{d}/joiner.int8.onnx',tokens=f'{d}/tokens.txt',model_type='nemo_transducer',num_threads=2)
v,sr=sf.read(sys.argv[1]); m=v.mean(1) if v.ndim>1 else v
m=resample_poly(m,16000,sr).astype(np.float32); sr=16000
segs=json.load(open(sys.argv[2]))
out=[]
for a,b in segs:
    s=rec.create_stream(); x=m[int(max(0,a-0.15)*sr):int((b+0.15)*sr)]
    s.accept_waveform(sr,x); rec.decode_stream(s); r=s.result
    toks=list(r.tokens); ts=[float(t)+max(0,a-0.15) for t in r.timestamps]
    out.append({'a':a,'b':b,'text':r.text.strip(),'tokens':toks,'ts':ts})
    print(f'{a:7.2f}-{b:7.2f} | {r.text.strip()}',flush=True)
json.dump(out,open(sys.argv[3],'w'))
