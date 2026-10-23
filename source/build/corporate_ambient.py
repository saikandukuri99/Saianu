"""Corporate ambient music bed for the EAI Healthcare video.

Warm, positive and unobtrusive: 100 BPM in C major (Cmaj9 - Am9 - Fmaj9 - Gsus),
lush evolving pads, a soft felt-piano arpeggio, a round sub bass, gentle
pulse/percussion and a long hall reverb. The structure follows the video:
intro swell, arpeggio from the first scene, light pulse once the platform
story starts, a lift for the Patient 360 reveal and a resolved ending chord.

usage: python3 corporate_ambient.py OUT.wav DURATION_SECONDS END_SECONDS [steady]

"steady": one constant, even bed for the whole video (no build-ups, swells,
breathing filter or ending hit) - only a short fade in and out.
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(23)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


# chord per two bars: (bass root, voicing)
CHORDS = [
    (36, [60, 64, 67, 71, 74]),   # Cmaj9
    (45, [57, 60, 64, 67, 71]),   # Am9
    (41, [57, 60, 64, 65, 69]),   # Fmaj9 (add #11 colour avoided, kept warm)
    (43, [55, 60, 62, 67, 71]),   # Gsus / G6
]


def chord_at(t):
    return CHORDS[int(t // (2 * BAR)) % len(CHORDS)]


STEADY = len(sys.argv) > 4 and sys.argv[4] == "steady"


def pad(dur, end):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    seg = 2 * BAR
    k = 0
    while k * seg < dur:
        t0 = k * seg
        root, notes = CHORDS[k % 4]
        if t0 >= end:                 # hold the final tonic chord
            root, notes = CHORDS[0]
        a = int(max(t0 - 0.6, 0) * SR)
        b = int(min(t0 + seg + 1.6, dur) * SR)
        tt = t[a:b] - t0
        env = smooth((tt + 0.6) / 1.4) * smooth((seg + 1.6 - tt) / 1.6)
        for i, m in enumerate(notes):
            f = midi(m)
            for det, pan in ((-0.07, 0.25), (0.0, 0.5), (0.08, 0.75)):
                ff = f * 2 ** (det / 12)
                ph = rng.uniform(0, 6.28)
                # soft saw-ish tone: few harmonics, slow vibrato
                vib = 1 + 0.0018 * np.sin(2 * np.pi * 0.23 * (tt + i))
                w = sum(np.sin(2 * np.pi * ff * h * vib * tt + ph * h) / h ** 1.6 for h in (1, 2, 3, 4))
                out[a:b, 0] += w * env * (1 - pan) * 0.045
                out[a:b, 1] += w * env * pan * 0.045
        k += 1
        if t0 >= end:
            break
    # slow filter movement (breathing): crossfade a darker and a brighter version
    m = (0.5 + 0.5 * np.sin(2 * np.pi * t / 19.0))[:, None] * (0 if STEADY else 1) + (0.5 if STEADY else 0)
    dark = np.column_stack([lp(out[:, c], 850) for c in range(2)])
    bright = np.column_stack([lp(out[:, c], 1900) for c in range(2)])
    return dark * (1 - m) + bright * m


def piano(dur, start, end):
    """Felt-piano style arpeggio: 8th notes over the chord tones."""
    n = int(dur * SR)
    out = np.zeros((n, 2))
    patt = [0, 2, 1, 3, 2, 4, 3, 1]
    step = BEAT / 2
    i = 0
    t = start
    while t < end - 0.05:
        root, notes = chord_at(t)
        m = notes[patt[i % 8]] + 12
        f = midi(m)
        L = int(2.2 * SR)
        a = int(t * SR)
        tt = np.arange(min(L, n - a)) / SR
        env = (1 - np.exp(-tt / 0.004)) * np.exp(-tt / 0.55)
        w = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.2)
             + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt) * np.exp(-tt / 0.1))
        vel = 0.75 + 0.25 * (1 if i % 2 == 0 else 0.6) + rng.uniform(-0.05, 0.05)
        pan = 0.5 + 0.28 * np.sin(i * 0.9)
        out[a:a + len(tt), 0] += w * env * vel * (1 - pan) * 0.11
        out[a:a + len(tt), 1] += w * env * vel * pan * 0.11
        t += step
        i += 1
    # dotted-eighth echo, darker
    d = int(BEAT * 0.75 * SR)
    echo = np.zeros_like(out)
    echo[d:, 0] = out[:-d, 1] * 0.32
    echo[d:, 1] = out[:-d, 0] * 0.32
    echo = np.column_stack([lp(echo[:, 0], 2500), lp(echo[:, 1], 2500)])
    return np.column_stack([lp(out[:, 0], 6000), lp(out[:, 1], 6000)]) + echo


def bass(dur, start, end):
    n = int(dur * SR)
    out = np.zeros(n)
    t = start
    while t < end:
        root, _ = chord_at(t)
        f = midi(root)
        for off in (0.0, 2 * BEAT, 4 * BEAT, 6 * BEAT):
            a = int((t + off) * SR)
            if a >= n:
                break
            L = int(2 * BEAT * SR)
            tt = np.arange(min(L, n - a)) / SR
            env = (1 - np.exp(-tt / 0.012)) * np.exp(-tt / 1.0) * smooth((2 * BEAT - tt) / 0.08)
            out[a:a + len(tt)] += (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(4 * np.pi * f * tt)) * env * 0.16
        t += 2 * BAR
    return lp(out, 220)


def drums(dur, start, end, level):
    """Soft pulse: gentle kick, brushed hats/shaker, light snap on 2 & 4."""
    n = int(dur * SR)
    out = np.zeros((n, 2))
    t = start
    b = 0
    while t < end:
        g = level(t)
        if g > 0.01:
            a = int(t * SR)
            if b % 2 == 0:  # kick on 1 and 3
                L = int(0.35 * SR)
                tt = np.arange(min(L, n - a)) / SR
                f = 52 + 70 * np.exp(-tt / 0.03)
                k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12)
                out[a:a + len(tt)] += (k * 0.30 * g)[:, None]
            else:           # soft snap on 2 and 4
                L = int(0.25 * SR)
                tt = np.arange(min(L, n - a)) / SR
                s = hp(rng.normal(0, 1, len(tt)), 1800) * np.exp(-tt / 0.06) * np.minimum(tt / 0.002, 1)
                out[a:a + len(tt)] += (s * 0.03 * g)[:, None]
            for q in range(4):  # 16th shaker
                aa = int((t + q * BEAT / 4) * SR)
                L = int(0.07 * SR)
                if aa + L >= n:
                    continue
                tt = np.arange(L) / SR
                sh = hp(rng.normal(0, 1, L), 5000) * np.exp(-tt / 0.025) * np.minimum(tt / 0.003, 1) * (0.8 if q % 2 else 0.45)
                pan = 0.62 if q % 2 else 0.4
                out[aa:aa + L, 0] += sh * 0.02 * g * (1 - pan)
                out[aa:aa + L, 1] += sh * 0.02 * g * pan
        t += BEAT
        b += 1
    return np.column_stack([lp(out[:, 0], 10000), lp(out[:, 1], 10000)])


def reverb(x, secs=3.2, mix=0.32):
    L = int(secs * SR)
    t = np.arange(L) / SR
    out = np.zeros_like(x)
    for c in range(2):
        ir = rng.normal(0, 1, L) * np.exp(-t / (secs / 6.9) * 1.0)
        ir = lp(ir, 5000)
        ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, c] = fftconvolve(x[:, c], ir)[: len(x)]
    return x * (1 - mix) + out * mix * 1.6


def swell(dur, t0, t1):
    """Filtered noise swell (soft riser) into a section change."""
    n = int(dur * SR)
    out = np.zeros((n, 2))
    a, b = int(t0 * SR), int(min(t1, dur) * SR)
    tt = np.linspace(0, 1, b - a)
    nz = rng.normal(0, 1, (b - a, 2))
    for c in range(2):
        out[a:b, c] = lp(hp(nz[:, c], 900), 6000) * (tt ** 2.2) * 0.05
    return out


def main():
    out_path = sys.argv[1]
    dur = float(sys.argv[2])
    end = float(sys.argv[3])          # final chord from here
    n = int(dur * SR)
    mix = np.zeros((n, 2))
    if STEADY:
        mix += pad(dur, dur + 60)
        mix += piano(dur, 0.2, dur) * 0.9
        b = bass(dur, 0.0, dur)
        mix += np.column_stack([b, b])
        mix += drums(dur, 0.0, dur, lambda t: 0.55)
        mix = reverb(mix)
        mix = np.column_stack([hp(mix[:, 0], 35), hp(mix[:, 1], 35)])
        t = np.arange(n) / SR
        mix *= smooth(t / 1.5)[:, None] * smooth((dur - t) / 2.2)[:, None]
        mix /= np.max(np.abs(mix)) + 1e-9
        mix *= 10 ** (-1.0 / 20)
        write(out_path, mix)
        return
    mix += pad(dur, end) * 1.0
    mix += piano(dur, 3.5, end + 1.2) * smoothstep_env(n, [(3.3, 0.0), (4.2, 0.85), (10.4, 0.85), (11.0, 1.0)])
    b = bass(dur, 10.4, end + 2 * BAR)
    mix += np.column_stack([b, b]) * smoothstep_env(n, [(10.3, 0.0), (11.2, 1.0)])

    def drum_level(t):
        if t < 10.5 or t >= end:
            return 0.0
        if 36.0 <= t < 38.5:   # Patient 360 reveal: breathe
            return 0.35
        return 0.75 if t < 19.3 else 1.0
    mix += drums(dur, 10.5, end, drum_level)
    mix += swell(dur, 34.6, 36.1) + swell(dur, 74.9, 76.45)
    # ending: tonic chord + bell
    a = int(end * SR)
    tt = np.arange(n - a) / SR
    for m in (72, 76, 79, 84):
        f = midi(m)
        bell = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2.76 * f * tt) * np.exp(-tt / 0.4)) \
            * np.exp(-tt / 2.4) * 0.05
        mix[a:, 0] += bell
        mix[a:, 1] += bell
    mix = reverb(mix)
    mix = np.column_stack([hp(mix[:, 0], 35), hp(mix[:, 1], 35)])
    # fades
    t = np.arange(n) / SR
    mix *= smooth(t / 1.2)[:, None] * smooth((dur - t) / 2.2)[:, None]
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 10 ** (-1.0 / 20)
    write(out_path, mix)


def write(path, mix):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())


def smoothstep_env(n, pts):
    """Piecewise smooth gain envelope from (time, gain) points (2-D column for stereo use)."""
    t = np.arange(n) / SR
    g = np.full(n, pts[0][1], np.float64)
    for (t0, g0), (t1, g1) in zip(pts, pts[1:]):
        m = (t >= t0) & (t < t1)
        g[m] = g0 + (g1 - g0) * smooth((t[m] - t0) / (t1 - t0))
    g[t >= pts[-1][0]] = pts[-1][1]
    return g[:, None]


if __name__ == "__main__":
    main()
