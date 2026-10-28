"""Copyright-free sound effects, synthesised from scratch (numpy/scipy). Every function returns mono float32 at SR."""
import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(SR * d)) / SR


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def adsr(n, a=.005, r=.05):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR / 2 - 100) / (SR / 2), 'low'); return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high'); return signal.lfilter(b, a, x)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), min(f2, SR / 2 - 100) / (SR / 2)], 'band'); return signal.lfilter(b, a, x)


def noise(d):
    return _rng.standard_normal(int(SR * d)).astype(np.float64)


def norm(x, peak=.8):
    m = np.max(np.abs(x)) + 1e-9
    return (x / m * peak).astype(np.float32)


def sweep_filter(x, f0, f1, q=1.0):
    """time-varying low-pass via block processing"""
    out = np.zeros_like(x); n = len(x); blk = 512
    zi = None
    for i in range(0, n, blk):
        fc = f0 * (f1 / f0) ** (i / max(1, n))
        b, a = signal.butter(2, min(fc, SR / 2 - 200) / (SR / 2), 'low')
        seg = x[i:i + blk]
        if zi is None or len(zi) != 2: zi = signal.lfilter_zi(b, a) * 0
        y, zi = signal.lfilter(b, a, seg, zi=zi)
        out[i:i + blk] = y
    return out


def sine(f, d, ph=0):
    t = t_(d); return np.sin(2 * np.pi * f * t + ph)


def glide(f0, f1, d, curve=1.0):
    t = np.linspace(0, 1, int(SR * d)); f = f0 * (f1 / f0) ** (t ** curve)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def fit(x, n):
    x = np.asarray(x)[:n]
    return np.pad(x, (0, n - len(x)))


def whoosh(d=.55, up=True):
    n = noise(d); y = sweep_filter(n, 300, 6000) if up else sweep_filter(n, 6000, 300)
    e = np.sin(np.linspace(0, np.pi, len(y))) ** 1.5
    return norm(y * e, .55)


def pop(d=.14):
    y = glide(700, 220, d, .6) * env_exp(int(SR * d), .035) + .3 * hp(noise(d), 3000) * env_exp(int(SR * d), .004)
    return norm(y, .6)


def ding(f=1318.5, d=.9):
    t = t_(d); y = np.sin(2 * np.pi * f * t) * np.exp(-t / .18) + .5 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t / .12) + .35 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t / .08)
    y[:int(.002 * SR)] *= np.linspace(0, 1, int(.002 * SR))
    return norm(y, .5)


def tick(d=.05):
    y = hp(noise(d), 2500) * env_exp(int(SR * d), .006) + .4 * sine(1900, d) * env_exp(int(SR * d), .01)
    return norm(y, .45)


def key(d=.04):
    y = lp(noise(d), 4000) * env_exp(int(SR * d), .004) + .3 * sine(900, d) * env_exp(int(SR * d), .008)
    return norm(y, .35)


def click(d=.2):
    a = tick(.03); b = np.zeros(int(SR * d), dtype=np.float32); b[:len(a)] += a; off = int(.09 * SR); b[off:off + len(a)] += a * .8
    return b


def riser(d=1.8):
    n = noise(d); y = sweep_filter(n, 200, 9000); t = np.linspace(0, 1, len(y)); y *= t ** 2.2
    s = glide(180, 1400, d, 2.0) * t ** 2 * .25
    return norm(y + s, .6)


def impact(d=1.2):
    n = int(SR * d); y = glide(75, 32, d, .35) * env_exp(n, .38) * 1.0 + lp(noise(d), 900) * env_exp(n, .09) * .7
    y += .3 * hp(noise(d), 2000) * env_exp(n, .02)
    return norm(y, .85)


def thud(d=.4):
    n = int(SR * d); y = glide(110, 45, d, .4) * env_exp(n, .1) + .4 * lp(noise(d), 500) * env_exp(n, .03)
    return norm(y, .8)


def stamp():
    a = thud(.35); b = tick(.06); o = np.zeros(len(a), dtype=np.float32); o += a; o[:len(b)] += b * .9
    return norm(o, .8)


def error(d=.4):
    t = t_(d); y = (np.sign(np.sin(2 * np.pi * 150 * t)) * .5 + np.sign(np.sin(2 * np.pi * 158 * t)) * .5) * np.exp(-t / .22)
    return norm(lp(y, 1200), .5)


def flip(d=.35):
    n = int(SR * d); return norm(fit(whoosh(d), n) * .7 + fit(np.pad(tick(.05), (int(.14 * SR), 0)), n), .55)


def sparkle(d=.9):
    out = np.zeros(int(SR * d))
    for i, f in enumerate([2093, 2637, 3136, 3951, 4699, 5588, 6272]):
        off = int(i * .06 * SR); t = t_(.35); s = np.sin(2 * np.pi * f * t) * np.exp(-t / .09) * (.9 ** i)
        out[off:off + len(s)] += s[:len(out) - off]
    return norm(out, .4)


def tada(d=1.6):
    out = np.zeros(int(SR * d))
    for i, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
        off = int(i * .07 * SR); t = t_(1.2); s = (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t / .5)
        out[off:off + len(s)] += s[:len(out) - off] * .5
    return norm(out + fit(np.pad(sparkle(.9), (int(.25 * SR), 0)), len(out)) * .5, .55)


def coins(d=1.2):
    out = np.zeros(int(SR * d)); r = np.random.default_rng(3)
    for _ in range(14):
        off = int(r.random() * (d - .35) * SR); f = r.choice([1568, 1760, 2093, 2349, 2637]); t = t_(.3)
        s = (np.sin(2 * np.pi * f * t) * np.exp(-t / .07) + .3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .04)) * (.4 + .5 * r.random())
        out[off:off + len(s)] += s[:len(out) - off]
    return norm(out, .45)


def coinflip(d=1.0):
    out = np.zeros(int(SR * d)); gaps = np.cumsum(np.linspace(.07, .16, 7));
    for i, g in enumerate(gaps):
        off = int(g * SR - .07 * SR); t = t_(.25); s = np.sin(2 * np.pi * 2400 * t) * np.exp(-t / .05) * .6
        if off + len(s) < len(out): out[off:off + len(s)] += s
    out += fit(np.pad(whoosh(.5), (int(.05 * SR), 0)), len(out)) * .35
    return norm(out, .5)


def crash(d=1.5):
    n = int(SR * d); y = hp(noise(d), 1500) * env_exp(n, .45) + lp(noise(d), 300) * env_exp(n, .6) * .8
    return norm(y, .6)


def melt(d=.8):
    n = int(SR * d); vib = 1 + .03 * np.sin(2 * np.pi * 9 * t_(d)); y = glide(900, 180, d, 1.0) * vib * np.linspace(1, 0, n) ** 1.3
    return norm(y, .4)


def ping(d=.5):
    t = t_(d); y = np.sin(2 * np.pi * 1568 * t) * np.exp(-t / .12) + .3 * np.sin(2 * np.pi * 3136 * t) * np.exp(-t / .05)
    return norm(y, .4)


def switch(d=.3):
    a = tick(.04); y = np.zeros(int(SR * d)); y[:len(a)] += a; t = t_(.25); y[int(.04 * SR):int(.04 * SR) + len(t)] += (np.sin(2 * np.pi * 1000 * t) * np.exp(-t / .08) * .4)[:len(y) - int(.04 * SR)]
    return norm(y, .45)


def zoom(d=.7):
    n = int(SR * d); return norm(fit(whoosh(d, True), n) * .8 + .3 * fit(glide(300, 1200, d, 1.5), n) * np.sin(np.linspace(0, np.pi, n)), .5)


def snap(d=.25):
    a = tick(.05); b = thud(.2); y = np.zeros(int(SR * d)); y[:len(b)] += b * .8; y[:len(a)] += a
    return norm(y, .7)


def alarm(d=.7):
    out = np.zeros(int(SR * d))
    for i in range(3):
        off = int(i * .22 * SR); t = t_(.14); f = 880 if i % 2 == 0 else 660
        s = np.sign(np.sin(2 * np.pi * f * t)) * .4 * adsr(len(t), .004, .03)
        out[off:off + len(s)] += s
    return norm(lp(out, 3500), .4)


def gear(d=.8):
    out = np.zeros(int(SR * d))
    for i in range(10):
        off = int(i * .075 * SR); a = tick(.04); out[off:off + len(a)] += a[:len(out) - off] * (.5 + .1 * (i % 2))
    return norm(out, .35)


def scratch(d=.45):
    n = noise(d); f = 400 + 3000 * np.abs(np.sin(np.linspace(0, 5 * np.pi, len(n))))
    y = np.zeros_like(n); blk = 256; zi = np.zeros(2)
    for i in range(0, len(n), blk):
        b, a = signal.butter(2, f[i] / (SR / 2), 'low'); y[i:i + blk] = signal.lfilter(b, a, n[i:i + blk])
    return norm(y * np.sin(np.linspace(0, np.pi, len(y))) ** .5, .55)


def bell(d=1.6):
    t = t_(d); y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau) for f, a, tau in [(880, 1, .6), (2217, .5, .4), (3010, .35, .3), (4180, .2, .2)])
    return norm(y, .45)


def bell_ring(d=1.2):  # alias
    return bell(d)


LIB = {
    'whoosh': whoosh, 'pop': pop, 'ding': ding, 'tick': tick, 'key': key, 'click': click, 'riser': riser, 'impact': impact,
    'thud': thud, 'stamp': stamp, 'error': error, 'flip': flip, 'sparkle': sparkle, 'tada': tada, 'coins': coins,
    'coinflip': coinflip, 'crash': crash, 'melt': melt, 'ping': ping, 'switch': switch, 'zoom': zoom, 'snap': snap,
    'alarm': alarm, 'gear': gear, 'scratch': scratch, 'bell': bell,
}
