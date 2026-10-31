"""Original background music (synthesised): warm pad + bass + pluck arpeggio + lo-fi drums, mood follows the story."""
import numpy as np
from scipy import signal

SR = 48000
BPM = 96
BEAT = 60.0 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(11)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'low'); return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high'); return signal.lfilter(b, a, x, axis=0)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), f2 / (SR / 2)], 'band'); return signal.lfilter(b, a, x)


MINOR = [  # Am  F  C  G
    (45, [57, 60, 64, 67]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
MAJOR = [  # C  G  Am  F
    (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67]), (45, [57, 60, 64, 69]), (41, [53, 57, 60, 65])]


def add(buf, x, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= buf.shape[0] or i < 0: return
    n = min(len(x), buf.shape[0] - i)
    l = gain * np.cos((pan + 1) * np.pi / 4); r = gain * np.sin((pan + 1) * np.pi / 4)
    buf[i:i + n, 0] += x[:n] * l; buf[i:i + n, 1] += x[:n] * r


def pad_note(m, d):
    t = np.arange(int((d + 1.0) * SR)) / SR; f = mtof(m); y = 0
    for det in (-0.07, 0.0, 0.07):
        ff = f * 2 ** (det / 12)
        y = y + signal.sawtooth(2 * np.pi * ff * t, .5) * .33 + np.sin(2 * np.pi * ff * t) * .2
    e = np.minimum(1, t / .7) * np.where(t < d, 1.0, np.exp(-(t - d) / .35))
    return lp(y * e, 1500)


def bass_note(m, d):
    t = np.arange(int((d + .2) * SR)) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * 2 * f * t)
    e = np.minimum(1, t / .01) * np.where(t < d, np.exp(-t / 1.4), 0) * np.where(t < d, 1, 0)
    e *= np.minimum(1, (d - t) / .08).clip(0, 1)
    return y * e


def pluck(m, d=1.2):
    t = np.arange(int(d * SR)) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / .26) + .38 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .14) + .16 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / .07)
    y[:int(.003 * SR)] *= np.linspace(0, 1, int(.003 * SR))
    return y


def kick():
    t = np.arange(int(.45 * SR)) / SR; f = 45 + 90 * np.exp(-t / .035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .13) + .25 * np.exp(-t / .004) * rng.standard_normal(len(t))


def snare():
    n = rng.standard_normal(int(.3 * SR)); t = np.arange(len(n)) / SR
    return bp(n, 1500, 7500) * np.exp(-t / .07) * .9 + np.sin(2 * np.pi * 190 * t) * np.exp(-t / .05) * .4


def hat(open_=False):
    n = rng.standard_normal(int(.25 * SR)); t = np.arange(len(n)) / SR
    return hp(n, 7000) * np.exp(-t / (.07 if open_ else .018))


def make(total, scene_marks, energies, out_fx=4.0, major_scene=4):
    """scene_marks: list of start times of each scene; energies: drum energy per scene (0..1)."""
    N = int((total + 1.0) * SR); buf = np.zeros((N, 2)); drums = np.zeros((N, 2))
    bars = int(total / BAR) + 2
    sc_start = scene_marks + [total + 10]

    def energy_at(t):
        for i in range(len(scene_marks)):
            if sc_start[i] <= t < sc_start[i + 1]: return energies[i]
        return energies[-1]

    major_from = scene_marks[major_scene] if len(scene_marks) > major_scene else 1e9  # story turns bright at scene 5
    for b in range(bars):
        t0 = b * BAR
        prog = MAJOR if t0 + BAR / 2 >= major_from else MINOR
        root, ch = prog[b % 4]
        e = energy_at(t0 + .1)
        # pad
        for m in ch: add(buf, pad_note(m, BAR + .1), t0, .075, 0.0)
        # bass
        if e > 0.05 or True:
            add(buf, bass_note(root, 1.6 * BEAT), t0, .24 if e > 0 else .18)
            add(buf, bass_note(root, .9 * BEAT), t0 + 2 * BEAT, .2)
            if e > .4: add(buf, bass_note(root + 7, .45 * BEAT), t0 + 3.5 * BEAT, .14)
        # pluck arpeggio, 8th notes
        order = [0, 1, 2, 3, 2, 1, 2, 3] if prog is MINOR else [0, 2, 1, 3, 2, 3, 1, 2]
        for k in range(8):
            if e < .05 and k % 2: continue
            m = ch[order[k]] + 12
            add(buf, pluck(m), t0 + k * BEAT / 2, .085 if e > 0 else .07, (-.35 if k % 2 else .35))
        # drums
        if e > .02:
            sw = .06 * BEAT
            for bt in (0, 2): add(drums, kick(), t0 + bt * BEAT, .55 * e)
            if e > .6: add(drums, kick(), t0 + 2.5 * BEAT + sw, .3 * e)
            for bt in (1, 3): add(drums, snare(), t0 + bt * BEAT, .28 * e)
            for k in range(8): add(drums, hat(k == 7), t0 + k * BEAT / 2 + (sw if k % 2 else 0), (.07 if k % 2 else .1) * e, (-.2 if k % 2 else .2))
    # tape-ish echo on the pluck+pad bus
    d = int(BEAT * .75 * SR); echo = np.zeros_like(buf); echo[d:] = buf[:-d] * .32; echo[2 * d:] += buf[:-2 * d] * .14
    echo = lp(echo, 3200)
    mix = buf + echo + drums
    mix = np.tanh(mix * 1.5) / 1.5
    mix = lp(mix, 11000)
    # gentle fade in/out
    fi = int(.8 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(out_fx * SR); end = int(total * SR); mix[end - fo:end] *= np.linspace(1, 0, fo)[:, None]; mix[end:] = 0
    return mix.astype(np.float32)
