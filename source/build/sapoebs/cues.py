# Voice-over cue times: phrase -> absolute time (s).
# Script punctuation is snapped to the real pauses in the voice track (align.py -> vo_align.json);
# words inside a clause are timed proportionally to their characters.
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
VO = json.load(open(os.path.join(HERE, "vo_timing.json")))
AL = json.load(open(os.path.join(HERE, "vo_align.json")))
import re
def weights(txt):
    """per-character time weights; isolated spelled letters ("S A P") take ~2.6 chars of time each."""
    w = [0.55 if ch == " " else (0.0 if ch in ",.?" else 1.0) for ch in txt]
    for m in re.finditer(r"(?<![A-Za-z])[A-Z](?![A-Za-z'])", txt): w[m.start()] = 2.6
    return w
def cue(i, phrase, end=False):
    txt = VO[i]["text"]; k = txt.lower().find(phrase.lower())
    assert k >= 0, (i, phrase)
    if end: k += len(phrase)
    for sp in AL[i]:
        if sp["c0"] <= k < sp["c1"] or sp is AL[i][-1]:
            ws = weights(txt)[sp["c0"]:sp["c1"]]; seg = txt[sp["c0"]:sp["c1"]]; cum = [0.0]
            for x in ws: cum.append(cum[-1] + x)
            kk = max(0, min(len(seg), k - sp["c0"]))
            return sp["t0"] + (sp["t1"] - sp["t0"]) * cum[kk] / max(1e-9, cum[-1])
def line_t(i): return VO[i]["start"], VO[i]["end"]
