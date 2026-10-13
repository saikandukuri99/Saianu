import sherpa_onnx, soundfile as sf, numpy as np, json, sys
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg)
sid=int(sys.argv[1]);out=sys.argv[2];sp=float(sys.argv[3])
S=json.load(open("sents.json"));tot=0
for i,s in enumerate(S):
    a=tts.generate(s[0],sid=sid,speed=sp);sf.write(f"{out}/s{i:02d}.wav",np.array(a.samples),a.sample_rate);tot+=len(a.samples)/a.sample_rate
print("speech total",tot)
