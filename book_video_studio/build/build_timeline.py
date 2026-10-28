#!/usr/bin/env python3
"""Episode JSON + per-scene voice-over mp3 -> renderer/timeline.js, build/voice_plan.json, SRT.

Sentence boundaries inside a scene are found from the pauses in the narration audio: choose the K-1 pauses
that best match the expected position (by character share) and favour longer pauses.
"""
import json, os, re, subprocess, sys

EP = os.path.abspath(sys.argv[1])
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ep = json.load(open(f'{EP}/episode.json', encoding='utf-8'))
LEAD, GAP, HOLD = ep.get('lead', .35), ep.get('scene_gap', .5), ep.get('end_hold', 4.5)
PUNCT = re.compile(r'[\s,.?!"“”:;…\-]')


def nchars(s):
    return max(1, len(PUNCT.sub('', s)))


def probe(path):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], text=True)
    return float(out.strip())


def silences(path):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'silencedetect=noise=-36dB:d=0.15', '-f', 'null', '-'], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', p.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', p.stderr)]
    if len(ends) < len(starts):
        ends.append(None)
    return list(zip(starts, ends))


def align(chars, sil, total):
    """Return list of (voice_start, voice_end, boundary_center) per sentence, scene-local seconds."""
    k = len(chars)
    lead, tail = 0.0, total
    cand = []
    for s, e in sil:
        e = total if e is None else e
        if s < .06:
            lead = e
        elif e > total - .06:
            tail = s
        else:
            cand.append((s, e))
    if k == 1:
        return [(lead, tail, None)]
    voice = tail - lead
    tot = float(sum(chars))
    expect = []
    acc = 0
    for i in range(k - 1):
        acc += chars[i]
        expect.append(lead + voice * acc / tot)
    tol = max(.6, .07 * voice)
    INF = 1e18
    n = len(cand)
    # dp[i][j] = best cost placing boundary i at candidate j
    dp = [[INF] * n for _ in range(k - 1)]
    bk = [[-1] * n for _ in range(k - 1)]
    for j, (s, e) in enumerate(cand):
        c = (s + e) / 2
        dp[0][j] = ((c - expect[0]) / tol) ** 2 - 5 * (e - s)
    for i in range(1, k - 1):
        for j, (s, e) in enumerate(cand):
            c = (s + e) / 2
            base = ((c - expect[i]) / tol) ** 2 - 5 * (e - s)
            for jj in range(j):
                if dp[i - 1][jj] < INF and dp[i - 1][jj] + base < dp[i][j]:
                    dp[i][j] = dp[i - 1][jj] + base
                    bk[i][j] = jj
    if n < k - 1 or min(dp[k - 2]) >= INF:
        # fall back to proportional
        cuts = [(expect[i] - .1, expect[i] + .1) for i in range(k - 1)]
    else:
        j = min(range(n), key=lambda x: dp[k - 2][x])
        idx = []
        for i in range(k - 2, -1, -1):
            idx.append(j)
            j = bk[i][j]
        idx.reverse()
        cuts = [cand[x] for x in idx]
    out = []
    prev = lead
    for i in range(k):
        if i < k - 1:
            s, e = cuts[i]
            out.append((prev, s, (s + e) / 2))
            prev = e
        else:
            out.append((prev, tail, None))
    return out


def split_chunks(text, vs, ve, maxc=62):
    clauses = [c.strip() for c in re.split(r'(?<=[,?!.:])\s+', text) if c.strip()]
    chunks, cur = [], ''
    for c in clauses:
        if cur and nchars(cur + ' ' + c) > maxc:
            chunks.append(cur)
            cur = c
        else:
            cur = (cur + ' ' + c).strip()
    if cur:
        chunks.append(cur)
    tot = float(sum(nchars(c) for c in chunks))
    out, t = [], vs
    for c in chunks:
        d = (ve - vs) * nchars(c) / tot
        out.append({'t0': round(t, 3), 't1': round(t + d, 3), 'text': c})
        t += d
    return out


# calibrate seconds per char from the scenes that exist
have = []
for sc in ep['scenes']:
    p = f"{EP}/audio/{sc['audio']}"
    if os.path.exists(p):
        have.append((probe(p), sum(nchars(s['text']) for s in sc['sentences'])))
spc = sum(d for d, _ in have) / sum(c for _, c in have) if have else .17
print(f'audio scenes: {len(have)}/{len(ep["scenes"])}, {spc:.3f} s/char')

sentences, plan = [], []
cursor = LEAD
for si, sc in enumerate(ep['scenes']):
    chars = [nchars(s['text']) for s in sc['sentences']]
    p = f"{EP}/audio/{sc['audio']}"
    real = os.path.exists(p)
    total = probe(p) if real else sum(chars) * spc + .3
    if real:
        al = align(chars, silences(p), total)
    else:
        tot = float(sum(chars)); acc = 0; al = []
        for i, c in enumerate(chars):
            a0 = acc / tot * (total - .2); acc += c; a1 = acc / tot * (total - .2)
            al.append((a0 + .1, a1 + .1 - (.12 if i < len(chars) - 1 else 0), (a1 + .1) if i < len(chars) - 1 else None))
    off = cursor
    plan.append({'scene': si + 1, 'file': p if real else None, 'offset': round(off, 3), 'dur': round(total, 3)})
    for i, s in enumerate(sc['sentences']):
        vs, ve, bc = al[i]
        s2 = dict(s)
        s2.update({'scene': si + 1, 'vs': round(off + vs, 3), 've': round(off + ve, 3), 'bnd': None if bc is None else round(off + bc, 3), 'real': real})
        sentences.append(s2)
    cursor = off + total + GAP

# visual spans: boundary = pause centre inside scene, scene-to-scene boundary in the middle of the gap
for i, s in enumerate(sentences):
    s['start'] = 0.0 if i == 0 else (sentences[i - 1]['bnd'] if sentences[i - 1]['bnd'] is not None else None)
for i in range(1, len(sentences)):
    if sentences[i]['start'] is None:
        prev_end = plan[sentences[i - 1]['scene'] - 1]['offset'] + plan[sentences[i - 1]['scene'] - 1]['dur']
        sentences[i]['start'] = round(prev_end + GAP / 2, 3)
for i, s in enumerate(sentences):
    s['end'] = sentences[i + 1]['start'] if i + 1 < len(sentences) else round(s['ve'] + .35 + HOLD, 3)
    s['dur'] = round(s['end'] - s['start'], 3)
    s['chunks'] = split_chunks(s['text'], s['vs'], s['ve'])
total = sentences[-1]['end']

tl = {'fps': 30, 'total': round(total, 3), 'brand': ep.get('brand', ''), 'sentences': [
    {k: v for k, v in s.items() if k in ('id', 'scene', 'text', 'start', 'end', 'dur', 'vs', 've', 'visual', 'theme', 'trans', 'txt', 'chunks')} for s in sentences]}
open(f'{ROOT}/renderer/timeline.js', 'w', encoding='utf-8').write('window.TL=' + json.dumps(tl, ensure_ascii=False) + ';\n')
json.dump({'total': tl['total'], 'scenes': plan, 'sentences': [{'id': s['id'], 'vs': s['vs'], 've': s['ve'], 'start': s['start'], 'end': s['end']} for s in sentences]}, open(f'{EP}/voice_plan.json', 'w'), indent=1)


def srt_time(t):
    h, r = divmod(t, 3600); m, r = divmod(r, 60)
    return f'{int(h):02d}:{int(m):02d}:{int(r):02d},{int(round((r - int(r)) * 1000)):03d}'


with open(f'{EP}/subtitles_te.srt', 'w', encoding='utf-8') as f:
    n = 1
    for s in sentences:
        for c in s['chunks']:
            f.write(f"{n}\n{srt_time(c['t0'])} --> {srt_time(c['t1'])}\n{c['text']}\n\n")
            n += 1

print(f'total {total:.1f}s')
for s in sentences:
    print(f"{s['id']:>4} {s['start']:7.2f} -> {s['end']:7.2f} ({s['dur']:5.2f}s) voice {s['vs']:7.2f}-{s['ve']:7.2f} {'' if s['real'] else '(est)'} {s['visual']}")
