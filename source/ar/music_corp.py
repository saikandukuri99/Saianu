# Original corporate score (royalty-free, procedural): 104 BPM, bright piano chords, plucked arpeggios,
# soft kick/clap/shaker groove, bass and pad. Follows the film: gentle intro, builds through the triggers,
# full groove from "One engine", drops back at the switch-off, lifts into the sign-off and rings out.
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
B = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(f"{B}/timeline.json")); T = TL["total"]; SR = 48000
LNS = {l["id"]: l for l in TL["lines"]}
N = int(T*SR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
BPM = 104; BEAT = 60/BPM; BAR = 4*BEAT
def hz(m): return 440*2**((m-69)/12)
# C - G/B - Am - F (two bars each), uplifting corporate cadence
PROG = [([48, 60, 64, 67, 72], 36), ([47, 59, 62, 67, 71], 43), ([45, 57, 60, 64, 69], 33), ([41, 57, 60, 65, 69], 29)]
def chord_at(t): return PROG[int(t // (2*BAR)) % 4]

def add(buf_l, buf_r, t0, sig, pan=.5, gain=1.0):
    i0 = int(t0*SR)
    if i0 >= N or i0 + len(sig) <= 0: return
    s = sig[:max(0, N - i0)]
    buf_l[i0:i0+len(s)] += s*gain*(1-pan)*2**.5*.7; buf_r[i0:i0+len(s)] += s*gain*pan*2**.5*.7

def env(n, a=.004, d=.4):
    t = np.arange(n)/SR; return (1 - np.exp(-t/a))*np.exp(-t/d)
def piano(f, dur=1.6, vel=1.0):
    n = int(dur*SR); t = np.arange(n)/SR
    s = sum(np.sin(2*np.pi*f*k*t*(1 + .0004*k))*(.6/k**1.3)*np.exp(-t*(1.2 + .9*k)) for k in range(1, 7))
    return s*(1 - np.exp(-t/.003))*vel*.22
def pluck(f, dur=.32):
    n = int(dur*SR); t = np.arange(n)/SR
    s = (2*((f*t) % 1) - 1)*.5 + np.sin(2*np.pi*f*t)*.5
    sos = butter(2, min(9000, f*6), fs=SR, output="sos"); s = sosfilt(sos, s)
    return s*env(n, .002, .09)*.12
def bass(f, dur):
    n = int(dur*SR); t = np.arange(n)/SR
    s = np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t) + .12*(2*((f*t) % 1) - 1)
    return s*(1 - np.exp(-t/.004))*np.exp(-t/max(.05, dur*1.4))*.22
def kick():
    n = int(.35*SR); t = np.arange(n)/SR
    f = 48 + 90*np.exp(-t*28); ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)*.55
_hp = butter(2, [1200, 7000], btype="band", fs=SR, output="sos")
def clap():
    n = int(.22*SR); t = np.arange(n)/SR
    s = sosfilt(_hp, rng.standard_normal(n))
    e = np.exp(-t*22) + .6*np.exp(-np.maximum(0, t - .012)*30)*(t > .012) + .4*np.exp(-np.maximum(0, t - .024)*30)*(t > .024)
    return s*e*.16
_hs = butter(2, 7000, btype="high", fs=SR, output="sos")
def shaker():
    n = int(.07*SR); t = np.arange(n)/SR
    return sosfilt(_hs, rng.standard_normal(n))*np.exp(-t*60)*.05
def crash():
    n = int(2.5*SR); t = np.arange(n)/SR
    return sosfilt(_hs, rng.standard_normal(n))*np.exp(-t*1.6)*.09

# arrangement markers from the narration timeline
t_trig, t_one, t_dark, t_access, t_sign = LNS["t1"]["start"] - .2, LNS["one"]["start"] + 1.0, LNS["dark"]["start"], LNS["access"]["start"] - .3, LNS["sign"]["start"] - .3
def section(t):
    if t < t_trig: return "intro"
    if t < t_one: return "build"
    if t_dark <= t < t_access: return "drop"
    if t >= t_sign: return "outro"
    return "full"

PL, PR = np.zeros(N), np.zeros(N)
nb = int(T/BEAT) + 1
end_hit = T - 4.2
for b in range(nb):
    t = b*BEAT
    if t > end_hit + .01: break
    sec = section(t); beat_in_bar = b % 4; notes, broot = chord_at(t)
    # piano: chord on beat 1, syncopated stabs on the "and" of 2 and on beat 4
    if beat_in_bar == 0:
        for k, m in enumerate(notes[1:]): add(L, R, t + k*.012, piano(hz(m), 2.2, .9), pan=.35 + .1*k)
    if sec in ("build", "full", "outro") and beat_in_bar in (1, 3):
        off = .5*BEAT if beat_in_bar == 1 else 0
        for k, m in enumerate(notes[2:]): add(L, R, t + off, piano(hz(m + 12), .8, .45), pan=.6)
    # plucked 16th-note arpeggio
    if sec in ("build", "full", "outro"):
        pat = [notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[2] + 12]
        for s in range(4):
            m = pat[(b*4 + s) % 4] + (12 if (b + s) % 8 == 7 else 0)
            add(L, R, t + s*BEAT/4, pluck(hz(m)), pan=.3 if s % 2 else .7, gain=.8 if sec == "build" else 1.0)
    # rhythm section
    if sec in ("full", "outro"):
        add(L, R, t, kick() if beat_in_bar in (0, 2) else np.zeros(1), .5)
        if beat_in_bar in (1, 3): add(L, R, t, clap(), .5)
        for s in range(4): add(L, R, t + s*BEAT/4, shaker(), .65, .6 if s % 2 == 0 else 1.0)
        for e in range(2): add(L, R, t + e*BEAT/2, bass(hz(broot), BEAT/2*.95), .5)
    elif sec == "build":
        if beat_in_bar == 0: add(L, R, t, kick()*.6, .5)
        add(L, R, t, bass(hz(broot), BEAT*.95)*.7, .5)
    elif sec == "drop":
        if beat_in_bar == 0: add(L, R, t, bass(hz(broot), BAR*.9)*.8, .5)
    # pad (sustained) every 2 bars
    if b % 8 == 0:
        n = int(2*BAR*SR); tt = np.arange(n)/SR
        e = np.minimum(1, tt/.6)*np.minimum(1, (2*BAR - tt)/.6)
        for k, m in enumerate(notes[1:4]):
            for det in (-.06, .06):
                f = hz(m)*2**(det/12)
                s = (np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*2*f*tt))*e*.035
                add(PL, PR, t, s, .3 if det < 0 else .7)
# lifts: crash at "One engine", after the drop, and at the sign-off
for tc in (t_one, t_access, t_sign): add(L, R, tc, crash(), .5)
# final sustained chord rings out
for k, m in enumerate([48, 60, 64, 67, 72, 76]): add(L, R, end_hit + k*.015, piano(hz(m), 4.2, 1.0), .35 + .06*k)
add(L, R, end_hit, crash(), .5)
L += PL; R += PR
# light room reverb
ir = rng.standard_normal(int(1.4*SR))*np.exp(-np.arange(int(1.4*SR))/SR*3.2); ir[0] = 0; ir /= np.abs(ir).sum()/6
L = .82*L + .18*fftconvolve(L, ir)[:N]; R = .82*R + .18*fftconvolve(R, np.roll(ir, 97))[:N]
# overall shape: fade-in, softer during the drop, fade-out
g = np.ones(N); tt = np.arange(N)/SR
g *= np.clip(tt/1.5, 0, 1); g *= np.clip((T - tt)/1.2, 0, 1)
m = np.stack([L*g, R*g], 1); m *= 10**(-1/20)/np.abs(m).max()
sf.write(f"{B}/music.wav", m, SR); print("corporate score", round(T, 2), "s")
