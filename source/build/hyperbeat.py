"""Synthesises a high-energy ("hyper beat") electronic music bed.

128 BPM, A minor / C major (Am-F-C-G), so it sits with the key of the
existing soft bed in the finalized healthcare cut. Writes a 48 kHz stereo WAV.

usage: python3 hyperbeat.py OUT.wav DURATION_SECONDS END_HIT_SECONDS
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 128
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def env(n, a, d, sustain=0.0):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1.0) * (sustain + (1 - sustain) * np.exp(-t / d))
    return e


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def onepole_hp(x, cutoff):
    return x - lowpass(x, cutoff)


def kick():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 48 + 140 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    click = rng.standard_normal(n) * np.exp(-t / 0.004) * 0.35
    return np.tanh(1.8 * (body + click))


def clap():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = onepole_hp(rng.standard_normal(n), 900)
    e = np.zeros(n)
    for o in (0.0, 0.011, 0.022):
        s = int(o * SR)
        e[s:] += np.exp(-(t[: n - s]) / 0.012)
    e += 0.6 * np.exp(-t / 0.09)
    return noise * e * 0.5


def hat(length):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = onepole_hp(onepole_hp(x, 7000), 7000)
    return x * np.exp(-t / (length / 4))


def saw(freq, n, detune=(0.0,)):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in detune:
        ph = (t * freq * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / len(detune)


def add(buf, x, start, gain=1.0, pan=0.0):
    s = int(round(start * SR))
    if s >= buf.shape[1] or s + len(x) <= 0:
        return
    x = x[: buf.shape[1] - s]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[0, s : s + len(x)] += x * gain * l * 1.414
    buf[1, s : s + len(x)] += x * gain * r * 1.414


def main():
    out_path, dur, end_hit = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    total = int(dur * SR)
    drums = np.zeros((2, total))
    music = np.zeros((2, total))

    start = BAR  # bar 0 is the riser intro
    nbars = int(round((end_hit - start) / BAR))
    end_hit = start + nbars * BAR

    K, C, CH, OH = kick(), clap(), hat(0.05), hat(0.22)
    # Am - F - C - G, one chord per bar
    prog = [(57, [69, 72, 76]), (53, [69, 72, 77]), (48, [67, 72, 76]), (55, [67, 71, 74])]

    for b in range(nbars):
        t0 = start + b * BAR
        root, chord = prog[b % 4]
        fill = b % 8 == 7
        build = b < 2  # first two bars: lighter, kick + hats only
        for q in range(4):
            tb = t0 + q * BEAT
            add(drums, K, tb, 0.95)
            if not build:
                if q in (1, 3):
                    add(drums, C, tb, 0.55, 0.05)
                add(drums, OH, tb + BEAT / 2, 0.22, 0.25)
            for s16 in range(4):
                v = 0.16 if s16 % 2 else 0.10
                add(drums, CH, tb + s16 * BEAT / 4, v, -0.3)
        if fill:  # snare-roll style clap fill into the next 8-bar phrase
            for i in range(8):
                add(drums, C, t0 + 2 * BEAT + i * BEAT / 4, 0.18 + 0.05 * i, 0.0)

        # Pulsing 16th-note bass (side-chained to the kick by its own envelope)
        n16 = int(BEAT / 4 * SR)
        for i in range(16):
            if i % 4 == 0:
                continue  # leave room for the kick
            note = root - 12 if i % 4 != 3 else root
            x = saw(midi(note), n16, (-0.004, 0.004)) * env(n16, 0.003, 0.06, 0.2)
            add(music, lowpass(x, 900), t0 + i * BEAT / 4, 0.42 if not build else 0.25)

        # Off-beat supersaw chord stabs
        if not build:
            n8 = int(BEAT * 0.45 * SR)
            for q in range(4):
                for j, nt in enumerate(chord):
                    x = saw(midi(nt), n8, (-0.012, -0.005, 0.0, 0.006, 0.013))
                    x = lowpass(x * env(n8, 0.004, 0.08, 0.15), 3200)
                    add(music, x, t0 + q * BEAT + BEAT / 2, 0.075, (-0.5, 0.5, 0.0)[j])

        # Arp sparkle on the second half of every 4-bar phrase
        if not build and b % 4 >= 2:
            na = int(BEAT / 4 * SR)
            arp = chord + [chord[0] + 12]
            for i in range(16):
                nt = arp[i % 4] + 12
                t = np.arange(na) / SR
                x = np.sign(np.sin(2 * np.pi * midi(nt) * t)) * env(na, 0.002, 0.05)
                add(music, lowpass(x, 5000), t0 + i * BEAT / 4, 0.05, 0.6 if i % 2 else -0.6)

    # Intro riser (noise sweep + rising tone) over bar 0
    n = int(BAR * SR)
    t = np.arange(n) / SR
    sweep = onepole_hp(rng.standard_normal(n), 2000) * (t / BAR) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2 * t / BAR)) / SR) * (t / BAR) ** 2
    add(music, sweep * 0.18 + tone * 0.06, 0.0)
    # Mini risers before every 8-bar phrase
    for b in range(7, nbars, 8):
        n = int(BAR * SR)
        r = onepole_hp(rng.standard_normal(n), 3000) * (np.arange(n) / n) ** 3
        add(music, r * 0.12, start + b * BAR)

    # Final impact + decaying chord tail
    add(drums, K, end_hit, 1.0)
    n = total - int(end_hit * SR)
    if n > 0:
        t = np.arange(n) / SR
        boom = np.sin(2 * np.pi * 45 * t) * np.exp(-t / 0.8)
        crash = onepole_hp(rng.standard_normal(n), 4000) * np.exp(-t / 1.2)
        pad = sum(saw(midi(nt), n, (-0.01, 0.0, 0.01)) for nt in (57, 64, 69, 72, 76))
        pad = lowpass(pad, 1800) * np.exp(-t / 1.6) * 0.05
        add(music, boom * 0.6 + crash * 0.15 + pad, end_hit)

    # Kick-keyed pump on the music bus for the "hyper" pumping feel
    pump = np.ones(total)
    pn = int(BEAT * SR)
    shape = 1 - 0.65 * np.exp(-np.arange(pn) / (0.07 * SR))
    for b in range(nbars * 4):
        s = int((start + b * BEAT) * SR)
        pump[s : s + pn] = shape[: max(0, min(pn, total - s))]
    music *= pump

    mix = drums + music
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix /= np.abs(mix).max() / 0.89
    pcm = (mix.T * 32767).astype("<i2")
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main()
