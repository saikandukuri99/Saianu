# Original slow ambient score (royalty-free, procedural): warm pads, sparse felt piano,
# sub swell, shimmer. Dips to pad-only at the switch-off and lifts into the sign-off.
import json, os, numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
B = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(f"{B}/timeline.json")); T = TL["total"]; SR = 48000
N = int(T*SR); t = np.arange(N)/SR
rng = np.random.default_rng(7)
def hz(m): return 440*2**((m-69)/12)
# progression (MIDI), ~8.75 s per chord: Am9, Fmaj7, Cadd9, Gsus/G, ...
CH = [[45,57,60,64,71],[41,57,60,64,69],[48,55,62,64,67],[43,55,59,62,67]]
CL = 8.75
L = np.zeros(N); R = np.zeros(N)
def env_at(i0, i1, a=2.5, r=3.0):
    n = i1-i0; e = np.ones(n); na=min(n,int(a*SR)); nr=min(n,int(r*SR))
    e[:na] = np.sin(np.linspace(0, np.pi/2, na))**2; e[-nr:] *= np.cos(np.linspace(0, np.pi/2, nr))**2
    return e
k = 0; s = 0.0
while s < T:
    ch = CH[k % 4]; i0 = int(s*SR); i1 = min(N, int((s+CL+3)*SR))
    tt = t[i0:i1]; e = env_at(i0, i1)
    for j, m in enumerate(ch):
        f = hz(m)
        for det, pan in ((-0.12, .3), (0.12, .7)):
            ff = f*2**(det/12/8)
            w = (np.sin(2*np.pi*ff*tt) + .35*np.sin(2*np.pi*2*ff*tt+.3) + .12*np.sin(2*np.pi*3*ff*tt))
            w *= (0.06 if j else 0.09) * e * (1+.15*np.sin(2*np.pi*.11*tt+j))
            L[i0:i1] += w*(1-pan); R[i0:i1] += w*pan
    # felt piano: slow arpeggio, one note every ~2.2 s
    for n_, m in enumerate([ch[2]+12, ch[3]+12, ch[4]+12, ch[3]+12]):
        ns = s + .4 + n_*2.2
        if ns >= T-1: break
        a0 = int(ns*SR); a1 = min(N, a0+int(4*SR)); tt2 = (np.arange(a1-a0))/SR; f = hz(m)
        p = (np.sin(2*np.pi*f*tt2)+.3*np.sin(2*np.pi*2*f*tt2)*np.exp(-tt2*3)+.08*np.sin(2*np.pi*3*f*tt2)*np.exp(-tt2*5))
        p *= np.exp(-tt2*1.1)*(1-np.exp(-tt2*80))*0.05
        pan = .35 + .3*(n_ % 2); L[a0:a1] += p*(1-pan); R[a0:a1] += p*pan
    k += 1; s += CL
# sub swell
sub = 0.05*np.sin(2*np.pi*hz(33)*t)*(.5+.5*np.sin(2*np.pi*t/17.5-np.pi/2))
L += sub; R += sub
# airy shimmer: band-passed noise
sos = butter(2, [3000, 9000], btype="band", fs=SR, output="sos")
sh = sosfilt(sos, rng.standard_normal(N))*0.006*(.6+.4*np.sin(2*np.pi*t/11))
L += sh; R += np.roll(sh, 900)
# reverb: exponential noise IR
ir_n = int(3.2*SR); irt = np.arange(ir_n)/SR
irL = rng.standard_normal(ir_n)*np.exp(-irt*2.0); irR = rng.standard_normal(ir_n)*np.exp(-irt*2.0)
irL[0] = irR[0] = 0; irL /= np.abs(irL).sum()/12; irR /= np.abs(irR).sum()/12
L = .6*L + .4*fftconvolve(L, irL)[:N]; R = .6*R + .4*fftconvolve(R, irR)[:N]
# arrangement envelope
lines = {l["id"]: l for l in TL["lines"]}
g = np.ones(N)
def ramp(a, b, v0, v1):
    i0, i1 = int(a*SR), int(b*SR); g[i0:i1] = np.linspace(v0, v1, i1-i0); g[i1:] = v1
ramp(0, 3, 0, .8); ramp(16, 19, .8, 1.0)
ramp(lines["dark"]["start"]-.5, lines["dark"]["start"]+1.5, 1.0, .55)
ramp(lines["access"]["start"]-1, lines["access"]["start"]+1, .55, 1.0)
ramp(lines["sign"]["start"]-1.5, lines["sign"]["start"]+.5, 1.0, 1.25)
ramp(T-3.2, T, 1.25, 0)
L *= g; R *= g
m = np.stack([L, R], 1); m *= 10**(-1/20)/np.abs(m).max()
sf.write(f"{B}/music.wav", m, SR); print("music", round(T, 2))
