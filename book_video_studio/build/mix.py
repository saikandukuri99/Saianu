#!/usr/bin/env python3
"""voice_plan.json + cues.json + scene mp3s -> final_audio.wav (voice, music with ducking, sound effects, loudness-normalised)."""
import json, os, subprocess, sys
import numpy as np
from scipy import signal
import soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
import sfx, music

SR = 48000
EP = os.path.abspath(sys.argv[1]); OUT = EP + '/mix'; os.makedirs(OUT, exist_ok=True)
plan = json.load(open(f'{EP}/voice_plan.json')); total = plan['total']
cues = json.load(open(f'{EP}/cues.json')) if os.path.exists(f'{EP}/cues.json') else []
N = int((total + 1.0) * SR)


def decode(path):
    wav = f'{OUT}/{os.path.basename(path)}.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), wav], check=True)
    x, _ = sf.read(wav, dtype='float32'); return x


# ---- voice bus
vo = np.zeros(N, dtype=np.float32)
for sc in plan['scenes']:
    if not sc['file']: continue
    x = decode(sc['file']); i = int(sc['offset'] * SR); n = min(len(x), N - i); vo[i:i + n] += x[:n]
sf.write(f'{OUT}/vo_raw.wav', vo, SR)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{OUT}/vo_raw.wav', '-af',
                'highpass=f=75,equalizer=f=220:t=q:w=1.1:g=-1.5,equalizer=f=3200:t=q:w=1:g=2.4,equalizer=f=9000:t=h:w=1:g=-1.5,'
                'acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4,alimiter=limit=0.9', f'{OUT}/vo_proc.wav'], check=True)
vo, _ = sf.read(f'{OUT}/vo_proc.wav', dtype='float32')
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]

# ---- music
sc_marks = [s['start'] for s in plan['sentences'] if s['id'].endswith('.1')]
sc_marks[0] = 0.0
energies = [float(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else [.55, .6, .6, 0.0, .9, .6, .5, .75, 1.0]
major = int(sys.argv[3]) if len(sys.argv) > 3 else 4
mus = music.make(total, sc_marks, energies[:len(sc_marks)], major_scene=major)
mus = np.pad(mus, ((0, max(0, N - len(mus))), (0, 0)))[:N]
# loud finale on the title reveal (sentence 1.5): small lift via gain envelope
# ---- ducking
env = np.abs(vo)
b, a = signal.butter(1, 12 / (SR / 2)); env = signal.filtfilt(b, a, env)
thr = max(1e-4, np.percentile(env[env > 1e-4], 40) * .8) if np.any(env > 1e-4) else 1
gate = np.clip(env / thr, 0, 1)
# attack/release smoothing at 200 Hz control rate
hop = SR // 200
nf = N // hop
gf = gate[:nf * hop].reshape(nf, hop).max(1)
df = np.zeros(nf); g = 0.0
at, rl = np.exp(-1 / (.04 * 200)), np.exp(-1 / (.45 * 200))
for i in range(nf):
    v = gf[i]; g = v + (g - v) * (at if v > g else rl); df[i] = g
duck = np.interp(np.arange(N) / hop - .5, np.arange(nf), df)
depth = .68
mus_g = (1 - depth * duck)[:, None]
mus = mus * mus_g

# ---- sfx
cache = {}
sfx_bus = np.zeros((N, 2), dtype=np.float32)
rs = np.random.default_rng(5)
for c in cues:
    name = c['n']
    if name not in sfx.LIB: print('unknown sfx', name); continue
    if name not in cache: cache[name] = sfx.LIB[name]()
    x = cache[name]; i = int(c['t'] * SR)
    if i < 0 or i >= N: continue
    n = min(len(x), N - i); pan = rs.uniform(-.25, .25); gain = c.get('v', 1.0) * .62
    sfx_bus[i:i + n, 0] += x[:n] * gain * np.cos((pan + 1) * np.pi / 4)
    sfx_bus[i:i + n, 1] += x[:n] * gain * np.sin((pan + 1) * np.pi / 4)

# ---- mix: voice centre, music wide, sfx
MUS, SFX, VOX = .85, .80, 1.0
mix = np.stack([vo, vo], 1) * VOX + mus * MUS + sfx_bus * SFX
def db(x): return 20 * np.log10(np.sqrt(np.mean(np.square(x)) + 1e-12))
voiced = np.abs(vo) > .02
print(f'levels while voice active (dBFS rms): voice {db(vo[voiced]):.1f}  music {db((mus * MUS)[voiced]):.1f}  sfx {db((sfx_bus * SFX)[voiced]):.1f} | music in gaps {db((mus * MUS)[~voiced][:SR * 20]):.1f}')
sf.write(f'{OUT}/mix_raw.wav', mix.astype(np.float32), SR, subtype='PCM_24')
# loudness normalise to YouTube-ish -14 LUFS
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{OUT}/mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-ar', '48000', f'{EP}/final_audio.wav'], check=True)
sf.write(f'{OUT}/music_only.wav', (mus / max(1e-6, np.abs(mus).max()) * .8).astype(np.float32), SR)
print('mix done', total, 's;', len(cues), 'cues;', len(cache), 'distinct effects')
