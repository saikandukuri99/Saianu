import sys, soundfile as sf
from kokoro_onnx import Kokoro
D, out = sys.argv[1], sys.argv[2]
k = Kokoro(D + "/kokoro.onnx", D + "/voices.bin")
a, sr = k.create("For more than two decades, Solix Technologies has helped enterprises transform their data into a strategic advantage.",
                 voice="af_heart", speed=1.0, lang="en-us")
sf.write(out, a, sr)
