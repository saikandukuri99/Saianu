import json
src = open("cue90.py").read()
SCREEN = {}
exec(src[src.index("SCREEN = {"):src.index("def mmss")])
SCREEN[1] = SCREEN[1].replace("ECS page", "Enterprise Content Services page")
HCS = {18: "Subtitle + Care Creates Data | Data Accelerates Cure; TRUSTED DATA FOUNDATION → COLLABORATIVE INTELLIGENCE → ACTIONABLE OUTCOMES",
       19: "Six-pillar EAI Healthcare platform (static); pillars 3, 5, 4, 6 highlight on the spoken names",
       20: "Capabilities appear in order: AI-Powered Documentation, AI Clinical Assistant, Preventive Care, Revenue Cycle Intelligence"}
T90 = json.load(open("timeline_90.json")); L90 = json.load(open("lines_90.json"))
THC = json.load(open("timeline_hc.json")); L3 = json.load(open("lines3b.json"))
F = json.load(open("final_order.json"))
p90 = {n: (a, b) for n, a, b in T90["parts"]}; phc = {n: (a, b) for n, a, b in THC["parts"]}
def mmss(x): return f"{int(x//60):02d}:{x%60:05.2f}"
tot = sum((phc.get(n) or p90[n])[1] - (phc.get(n) or p90[n])[0] for n in F["order"])
out = ["# Solix Empower 2026 – short version: cue sheet", "",
       f"Parts total **{tot:.1f}s**, plus your own Scene 1 (7.1 s VO) in front.",
       "EAI Healthcare (05b, 05c, 05c2) uses the full original voice-over and visuals. All section headings are removed. Times are relative to the start of each clip.", ""]
for n in F["order"]:
    hc = n in phc
    a, b = phc[n] if hc else p90[n]
    T, L, S = (THC, L3, HCS) if hc else (T90, L90, SCREEN)
    out += [f"### {n.replace('_', ' ')}  ({b - a:.2f}s)", f"`{n}.mp4` / `{n}.mov`", "", "| Clip time | Narration | On screen |", "|---|---|---|"]
    for i, ln in enumerate(T["lines"]):
        if a - 0.01 <= ln["start"] < b:
            out.append(f"| {mmss(ln['start'] - a)} | {L[i]['cap']} | {S.get(i, '')} |")
    out.append("")
open("deliver90/CUE_SHEET.md", "w").write("\n".join(out))
