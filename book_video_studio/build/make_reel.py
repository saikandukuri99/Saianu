#!/usr/bin/env python3
"""Cut a ~50 s vertical (9:16) reel from an already rendered episode.

  python3 build/make_reel.py <episode_dir> <frames_dir> <out_dir>

Picks sentence ranges (hook -> key ideas -> conclusion), cuts the voice-over and 3D frames, builds a fresh music + SFX mix,
draws big karaoke captions / headline / progress bar for the vertical layout and encodes 1080x1920 H.264.
"""
import json, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import music, sfx

EP, FRAMES, OUT = [os.path.abspath(a) for a in sys.argv[1:4]]
FPS, SR = 30, 48000
os.makedirs(OUT, exist_ok=True)
plan = json.load(open(f'{EP}/voice_plan.json'))
S = {s['id']: s for s in plan['sentences']}
tl = json.loads(open(os.path.join(HERE, '../renderer3d/timeline.js'), encoding='utf-8').read()[len('window.TL='):].rstrip().rstrip(';'))
TL = {s['id']: s for s in tl['sentences']}

# (first sentence, last sentence, headline, extra seconds past the end)
PICKS = [
    ('1.1', '1.5', 'డబ్బు విషయంలో\nఎవరూ పిచ్చివాళ్ళు కాదు!', 0),
    ('3.2', '3.2', 'మన అనుభవాలే\nమన నిర్ణయాలు', 0),
    ('5.3', '5.5', 'ఎవరి లాజిక్\nవాళ్ళది', 0),
    ('8.2', '8.2', 'తప్పు పట్టే ముందు\nఆలోచించండి', 0),
    ('9.1', '9.2', 'డబ్బు = మనసు\n+ అనుభవాలు', 0),
]
END = ('9.6', 4.0)                       # closing line + a short end-card hold
segs = []
off = 0.0
for a, b, head, _ in PICKS:
    t0, t1 = S[a]['start'], S[b]['end']
    segs.append(dict(t0=t0, t1=t1, off=off, head=head)); off += t1 - t0
t0 = S[END[0]]['start']; segs.append(dict(t0=t0, t1=t0 + END[1], off=off, head='ఇదే అసలు పాఠం')); off += END[1]
TOTAL = off
print('reel length', round(TOTAL, 2), 's')


def to_reel(t):
    for g in segs:
        if g['t0'] - 1e-6 <= t < g['t1']:
            return g['off'] + t - g['t0']
    return None


# ------------------------------------------------------------------ audio
vo_full, _ = sf.read(f'{EP}/mix/vo_proc.wav', dtype='float32')
N = int((TOTAL + .6) * SR)
vo = np.zeros(N, dtype=np.float32)
for g in segs:
    a, b = int(g['t0'] * SR), int(g['t1'] * SR)
    x = vo_full[a:b].copy(); n = len(x); f = int(.04 * SR)
    x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    i = int(g['off'] * SR); vo[i:i + n] += x[:N - i]
cues = []
for c in json.load(open(f'{EP}/cues.json')):
    r = to_reel(c['t'])
    if r is not None:
        cues.append(dict(t=r, n=c['n'], v=c['v']))
marks = [0, segs[1]['off'], segs[2]['off'], segs[3]['off'], segs[4]['off']]
mus = music.make(TOTAL, marks, [.75, .7, .85, .8, 1.0], out_fx=2.5)
mus = np.pad(mus, ((0, max(0, N - len(mus))), (0, 0)))[:N]
env = np.abs(vo); b_, a_ = signal.butter(1, 12 / (SR / 2)); env = signal.filtfilt(b_, a_, env)
thr = max(1e-4, np.percentile(env[env > 1e-4], 40) * .8)
gate = np.clip(env / thr, 0, 1); hop = SR // 200; nf = N // hop
gf = gate[:nf * hop].reshape(nf, hop).max(1); df = np.zeros(nf); g_ = 0.0
at, rl = np.exp(-1 / (.04 * 200)), np.exp(-1 / (.45 * 200))
for i in range(nf):
    v = gf[i]; g_ = v + (g_ - v) * (at if v > g_ else rl); df[i] = g_
duck = np.interp(np.arange(N) / hop - .5, np.arange(nf), df)
mus = mus * (1 - .68 * duck)[:, None]
bus = np.zeros((N, 2), dtype=np.float32); cache = {}; rs = np.random.default_rng(5)
for c in cues:
    if c['n'] not in sfx.LIB: continue
    cache.setdefault(c['n'], sfx.LIB[c['n']]())
    x = cache[c['n']]; i = int(c['t'] * SR)
    if i >= N: continue
    n = min(len(x), N - i); pan = rs.uniform(-.25, .25); gn = c['v'] * .62
    bus[i:i + n, 0] += x[:n] * gn * np.cos((pan + 1) * np.pi / 4); bus[i:i + n, 1] += x[:n] * gn * np.sin((pan + 1) * np.pi / 4)
mix = np.stack([vo, vo], 1) + mus * .85 + bus * .8
sf.write(f'{OUT}/reel_mix_raw.wav', mix.astype(np.float32), SR, subtype='PCM_24')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{OUT}/reel_mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-ar', '48000', f'{OUT}/reel_audio.wav'], check=True)

# ------------------------------------------------------------------ frames: symlink the cut list, then overlay graphics
src = f'{OUT}/src'; ov = f'{OUT}/ov'
for d in (src, ov):
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d): os.remove(os.path.join(d, f))
NF = int(round(TOTAL * FPS)); k = 0
for g in segs:
    a = int(round(g['t0'] * FPS)); n = int(round((g['t1'] - g['t0']) * FPS))
    for j in range(n):
        if k >= NF: break
        os.symlink(f'{FRAMES}/f_{a + j:06d}.jpg', f'{src}/{k:05d}.jpg'); k += 1
NF = k
print('frames', NF)

FB = os.path.join(HERE, '../fonts/NotoSansTelugu-Bold.ttf')
fnt = lambda s: ImageFont.truetype(FB, s, layout_engine=ImageFont.Layout.RAQM)
F_HEAD, F_CAP, F_TAG, F_CTA = fnt(92), fnt(66), fnt(44), fnt(50)
GOLD, WHITE = (255, 214, 107, 255), (255, 255, 255, 255)
W, H = 1080, 1920


def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3


# caption chunks mapped to reel time
chunks = []
for sid in TL:
    for ch in TL[sid]['chunks']:
        r0, r1 = to_reel(ch['t0'] + 1e-4), to_reel(ch['t1'] - 1e-4)
        if r0 is not None and r1 is not None:
            chunks.append((r0, r1, ch['text']))


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(' '), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur); return lines


probe = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
for fi in range(NF):
    t = fi / FPS
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # tag chip (top)
    d.rounded_rectangle((60, 120, 60 + 470, 120 + 78), 39, fill=(255, 200, 87, 255))
    d.text((60 + 235, 120 + 39), 'డబ్బు సైకాలజీ', font=F_TAG, fill=(42, 27, 0, 255), anchor='mm')
    # headline of the current segment (slides up + fades in)
    seg = [g for g in segs if g['off'] <= t < g['off'] + (g['t1'] - g['t0'])][-1]
    lt = t - seg['off']; a = ease(lt / .35)
    lay = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    y = 30
    for line in seg['head'].split('\n'):
        ld.text((W // 2, y + 55), line, font=F_HEAD, fill=WHITE, anchor='mm', stroke_width=9, stroke_fill=(27, 15, 74, 255)); y += 130
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    im.alpha_composite(lay, (0, int(250 + (1 - a) * 40)))
    # karaoke caption (below the video band)
    for r0, r1, text in chunks:
        if r0 - .02 <= t <= r1 + .15:
            fade = min(1, (t - r0 + .02) / .12) * (1 if t <= r1 else max(0, 1 - (t - r1) / .15))
            lines = wrap(probe, text, F_CAP, 940)
            words_all = text.split(' '); tot = sum(len(w) for w in words_all); acc = 0; fr = {}
            for i, w in enumerate(words_all): fr[i] = acc / tot; acc += len(w)
            prog = max(0, min(1, (t - r0) / max(.2, (r1 - r0) * .94)))
            bh = len(lines) * 100 + 40; by = 1235
            cap = Image.new('RGBA', (W, bh + 20), (0, 0, 0, 0)); cd = ImageDraw.Draw(cap)
            mw = max(probe.textlength(l, font=F_CAP) for l in lines)
            cd.rounded_rectangle((W / 2 - mw / 2 - 40, 0, W / 2 + mw / 2 + 40, bh), 40, fill=(7, 9, 34, 170), outline=(255, 255, 255, 50), width=2)
            wi = 0
            for li, line in enumerate(lines):
                lw = probe.textlength(line, font=F_CAP); x = W / 2 - lw / 2
                for w in line.split(' '):
                    ww = probe.textlength(w, font=F_CAP)
                    cd.text((x + ww / 2, 20 + li * 100 + 50), w, font=F_CAP, fill=GOLD if prog >= fr[wi] else WHITE, anchor='mm'); x += ww + probe.textlength(' ', font=F_CAP); wi += 1
            cap.putalpha(cap.getchannel('A').point(lambda v: int(v * fade)))
            im.alpha_composite(cap, (0, by)); break
    # progress bar + closing call to action
    d.rounded_rectangle((60, 1790, W - 60, 1802), 6, fill=(255, 255, 255, 60))
    d.rounded_rectangle((60, 1790, 60 + (W - 120) * t / TOTAL, 1802), 6, fill=GOLD)
    if t > TOTAL - 4.0:
        ca = ease((t - (TOTAL - 4.0)) / .4)
        cta = Image.new('RGBA', (W, 130), (0, 0, 0, 0)); cdr = ImageDraw.Draw(cta)
        cdr.rounded_rectangle((90, 10, W - 90, 120), 55, fill=(229, 35, 43, 255))
        cdr.text((W / 2, 65), 'ఇలాంటి మరిన్ని వీడియోల కోసం ఫాలో అవ్వండి', font=fnt(40), fill=WHITE, anchor='mm')
        cta.putalpha(cta.getchannel('A').point(lambda v: int(v * ca))); im.alpha_composite(cta, (0, 1560))
    im.save(f'{ov}/{fi:05d}.png', compress_level=1)

# ------------------------------------------------------------------ encode
vf = ('[0:v]split=2[a][b];'
      '[a]scale=-2:1920,crop=1080:1920,boxblur=40:6,eq=brightness=-0.10:saturation=1.2[bg];'
      '[b]crop=1920:830:0:0,scale=1080:-2[fg];'
      '[bg][fg]overlay=(W-w)/2:690[v1];[v1][1:v]overlay=0:0:format=auto[v]')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{src}/%05d.jpg', '-framerate', str(FPS), '-i', f'{ov}/%05d.png',
                '-i', f'{OUT}/reel_audio.wav', '-filter_complex', vf, '-map', '[v]', '-map', '2:a', '-t', f'{TOTAL:.3f}',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '256k',
                '-movflags', '+faststart', f'{OUT}/ep01_reel_50s_9x16.mp4'], check=True)
print('done', f'{OUT}/ep01_reel_50s_9x16.mp4')
