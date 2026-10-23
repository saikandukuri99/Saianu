# Direct Kokoro inference (onnxruntime) with espeak phonemes, so word stress can be corrected (e.g. "Agentic" -> ay-JEN-tik).
import re,numpy as np,onnxruntime as ort,espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library(espeakng_loader.get_library_path());EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
from phonemizer import phonemize
D="tts/kokoro-multi-lang-v1_0/"
sess=ort.InferenceSession(D+"model.onnx",providers=['CPUExecutionProvider'])
TOK={}
for l in open(D+"tokens.txt",encoding='utf8'):
    p=l.rstrip('\n').rsplit(' ',1)
    if len(p)==2: TOK[p[0]]=int(p[1])
VOICES=np.fromfile(D+"voices.bin",dtype=np.float32).reshape(54,510,256)
E2M=[('aɪ','I'),('aʊ','W'),('dʒ','ʤ'),('eɪ','A'),('tʃ','ʧ'),('ɔɪ','Y'),('oʊ','O'),('əʊ','O'),('ɚ','əɹ'),('ɜːɹ','ɜɹ'),('ʲ',''),('r','ɹ'),('x','k'),('ç','k'),('ɐ','ə'),('ɬ','l'),('ʔ','t'),('ː',''),('̩',''),('̯',''),('-',' ')]
FIX={'eɪdʒˈɛntɪk':'ˌeɪdʒˈɛntɪk'}   # espeak leaves the first syllable unstressed -> weak "jentic"
def phon(text):
    ph=phonemize(text,language='en-us',backend='espeak',with_stress=True,preserve_punctuation=True,strip=True)
    for a,b in FIX.items(): ph=ph.replace(a,b)
    for a,b in E2M: ph=ph.replace(a,b)
    return ph
def synth(text,sid=9,speed=1.0):
    ph=phon(text);ids=[TOK[c] for c in ph if c in TOK]
    ids=ids[:508];style=VOICES[sid][len(ids)][None,:]
    out=sess.run(None,{'tokens':np.array([[0]+ids+[0]],dtype=np.int64),'style':style.astype(np.float32),'speed':np.array([speed],dtype=np.float32)})[0]
    return out.astype(np.float32),ph
