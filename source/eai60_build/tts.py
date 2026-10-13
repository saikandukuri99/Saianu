import sherpa_onnx, soundfile as sf, numpy as np, json, sys
d="tts/kokoro-multi-lang-v1_0/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
 kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d+"model.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",lexicon=d+"lexicon-us-en.txt"),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg)
sid=int(sys.argv[1]); out=sys.argv[2]
lines=json.load(open("script.json"))
for i,l in enumerate(lines,1):
    a=tts.generate(l["text"],sid=sid,speed=float(sys.argv[3]))
    sf.write(f"{out}/L{i:02d}.wav",np.array(a.samples),a.sample_rate)
    print(i,len(a.samples)/a.sample_rate)
