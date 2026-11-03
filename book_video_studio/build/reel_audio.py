#!/usr/bin/env python3
"""Cut the processed ep2 voice-over to the reel plan, add music (ducked), sfx cues -> reel_audio.wav"""
import json, os, sys, subprocess
import numpy as np, soundfile as sf
from scipy import signal
sys.path.insert(0, os.path.dirname(__file__)); import sfx, music
SR = 48000; EP = 'episodes/ep02_one_car'
plan = json.load(open(f'{EP}/reel_plan.json')); total = plan['total']; N = int((total + .5) * SR)
cues = json.load(open(f'{EP}/reel_cues.json'))
vp, _ = sf.read(f'{EP}/mix/vo_proc.wav', dtype='float32')
if vp.ndim > 1: vp = vp.mean(1)
vo = np.zeros(N, np.float32); F = int(.03 * SR)
for s in plan['segs']:
    a, b = int(s['o0'] * SR), int(s['o1'] * SR); x = vp[a:b].copy(); x[:F] *= np.linspace(0, 1, F); x[-F:] *= np.linspace(1, 0, F)
    i = int(s['n0'] * SR); n = min(len(x), N - i); vo[i:i + n] += x[:n]
marks = [0.0, [s for s in plan['segs'] if s['id'] == '3.3'][0]['n0']]
mus = music.make(total, marks, [.7, .9], out_fx=3.0, major_scene=1)
mus = np.pad(mus, ((0, max(0, N - len(mus))), (0, 0)))[:N]
env = np.abs(vo); b, a = signal.butter(1, 12 / (SR / 2)); env = signal.filtfilt(b, a, env)
thr = max(1e-4, np.percentile(env[env > 1e-4], 40) * .8); gate = np.clip(env / thr, 0, 1)
hop = SR // 200; nf = N // hop; gf = gate[:nf * hop].reshape(nf, hop).max(1); df = np.zeros(nf); g = 0.
at, rl = np.exp(-1 / (.04 * 200)), np.exp(-1 / (.45 * 200))
for i in range(nf):
    v = gf[i]; g = v + (g - v) * (at if v > g else rl); df[i] = g
duck = np.interp(np.arange(N) / hop - .5, np.arange(nf), df); mus = mus * (1 - .68 * duck)[:, None]
bus = np.zeros((N, 2), np.float32); rs = np.random.default_rng(5); cache = {}
for c in cues:
    n_ = c['n']
    if n_ not in sfx.LIB: continue
    if n_ not in cache: cache[n_] = sfx.LIB[n_]()
    x = cache[n_]; i = int(c['t'] * SR)
    if i >= N: continue
    n = min(len(x), N - i); pan = rs.uniform(-.25, .25); gn = c.get('v', 1) * .62
    bus[i:i + n, 0] += x[:n] * gn * np.cos((pan + 1) * np.pi / 4); bus[i:i + n, 1] += x[:n] * gn * np.sin((pan + 1) * np.pi / 4)
mix = np.stack([vo, vo], 1) + mus * .85 + bus * .8
os.makedirs(f'{EP}/mix', exist_ok=True); sf.write(f'{EP}/mix/reel_raw.wav', mix, SR, subtype='PCM_24')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{EP}/mix/reel_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-ar', '48000', f'{EP}/reel_audio.wav'], check=True)
print('ok', total)
