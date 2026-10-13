# Editing elements for Premiere: the finished film's graphics as transparent (RGB + alpha)
# ProRes 4444 clips, one per scene, with the background, ambient bokeh, vignette, grain and
# burned-in captions left out. Nothing else changes: every frame is rendered by render_ar.py.
# Alpha is recovered by rendering each frame over black and over white (difference matte),
# which reproduces normal, screen and glow blends exactly when laid over any background.
# Also writes the VO / BGM stems, the reference mix and the captions as SRT.
import os, sys, json, subprocess, numpy as np, soundfile as sf
import render_ar as R
R.NO_BOKEH = True
B = R.B
OUT = os.path.join(B, "..", "..", "output", "AR_editing_elements")
NAMES = dict(hook="01_Title_and_Hook", t1="02_Cost", t2="03_Risk", t3="04_M&A", t4="05_Old_Archive", t5="06_AI_Gap",
             one="07_Many_Reasons_One_Engine", connect="08_Connect", migrate="09_Migrate_Validate",
             dark="10_Goes_Dark", access="11_Access_Records", ask="12_Data_Ask", ai="13_Enable_AI", sign="14_Signoff")
FPS = R.FPS; NF = int(R.T*FPS)

def tc(sec):
    f = int(round(sec*FPS)); return f"{f//(FPS*60):02d}-{(f//FPS) % 60:02d}-{f % FPS:02d}"
def clips():
    out = []
    for k, sid in enumerate(R.ORDER):
        f0 = int(round(R.SC[sid]*FPS)); f1 = NF if k+1 == len(R.ORDER) else int(round(R.SC[R.ORDER[k+1]]*FPS))
        out.append((sid, f0, f1, f"{NAMES[sid].replace('&', 'and')}_TC{tc(f0/FPS)}.mov"))
    return out

def frame_rgba(t):
    to = R.word_time("one", "One engine")
    flash = 2.5*np.exp(-(t - to)*2.2) if t > to else 0.0
    g = R.glow_layer(t, flash)
    lit = 1 - np.exp(-g*.9)
    hot = np.clip((g.max(-1, keepdims=True) - 1.6)/3.5, 0, 1)
    Bk = (lit + (1 - lit)*hot*.7).astype(np.float32)
    Wh = np.ones_like(Bk)
    R.overlays(Bk, t); R.overlays(Wh, t)
    a = np.clip(1 - (Wh - Bk), 0, 1).max(-1, keepdims=True)
    col = np.clip(Bk/np.maximum(a, 1e-4), 0, 1)
    fo = 1 - float(R.ease((t - (R.T - .9))/.9))
    a = a*fo
    return np.concatenate([(col*65535 + .5).astype(np.uint16), (a*65535 + .5).astype(np.uint16)], -1)

def render_clip(f0, f1, path):
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba64le", "-s", f"{R.W}x{R.H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                          "-alpha_bits", "16", "-vendor", "apl0", "-qscale:v", os.environ.get("Q", "6"), path], stdin=subprocess.PIPE)
    for i in range(f0, f1): p.stdin.write(frame_rgba(i/FPS).tobytes())
    p.stdin.close(); p.wait()

def srt():
    LS = R.TL["lines"]; out = []; n = 0
    def ts(x):
        ms = int(round(x*1000)); return f"{ms//3600000:02d}:{ms//60000 % 60:02d}:{ms//1000 % 60:02d},{ms % 1000:03d}"
    for i, L in enumerate(LS):
        if L["id"] == "sign": continue      # the end card carries this line on screen, as in the film
        t0, t1 = L["start"] - .1, L["end"] + .3
        if i + 1 < len(LS): t1 = min(t1, LS[i+1]["start"] - .35)
        n += 1; out.append(f"{n}\n{ts(t0)} --> {ts(t1)}\n{L['caption']}\n")
    open(os.path.join(OUT, "Solix_AR_captions.srt"), "w").write("\n".join(out))

def audio():
    vo, sr = sf.read(f"{B}/vo.wav"); mu, _ = sf.read(f"{B}/music.wav")
    n = min(len(vo), len(mu)); vo = vo[:n]; mu = mu[:n]
    win = int(.05*sr); env = np.sqrt(np.convolve(vo**2, np.ones(win)/win, "same"))
    act = (env > .01).astype(float); k = int(.35*sr); act = np.convolve(act, np.ones(k)/k, "same")
    duck = 1 - .5*np.clip(act*1.5, 0, 1)
    vo2 = np.stack([vo, vo], 1); bgm = mu*.42*duck[:, None]
    mix = vo2 + bgm; g = .9/np.abs(mix).max()
    # same gain as the film's mix; the film's final loudness pass is applied to the full mix only
    sf.write(os.path.join(OUT, "Solix_AR_VO.wav"), vo2*g, sr, subtype="PCM_24")
    sf.write(os.path.join(OUT, "Solix_AR_BGM_ducked.wav"), bgm*g, sr, subtype="PCM_24")
    sf.write(os.path.join(OUT, "Solix_AR_BGM_clean.wav"), mu*.42*g, sr, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{B}/mix_norm.wav", "-c:a", "pcm_s24le",
                    os.path.join(OUT, "Solix_AR_full_mix.wav")], check=True)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1:2] == ["clip"]:
        i = int(sys.argv[2]); sid, f0, f1, name = clips()[i]
        render_clip(f0, f1, os.path.join(OUT, name)); print("done", name, flush=True); sys.exit()
    if sys.argv[1:2] == ["test"]:
        from PIL import Image
        for ts_ in sys.argv[2:]:
            a = (frame_rgba(float(ts_)) >> 8).astype(np.uint8)
            Image.fromarray(a, "RGBA").save(f"{B}/preview/alpha_{float(ts_):05.1f}.png")
        sys.exit()
    srt(); audio()
    with open(os.path.join(OUT, "Clip_list.txt"), "w") as f:
        f.write("Place each clip on the timeline at its start time (30 fps). Clips butt together with no gaps.\n\n")
        for sid, f0, f1, name in clips():
            f.write(f"{name:52s} start {f0/FPS:6.2f}s  end {f1/FPS:6.2f}s  ({f1-f0} frames)\n")
    print("\n".join(c[3] for c in clips()))
