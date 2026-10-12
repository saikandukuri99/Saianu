import json
T = json.load(open("timeline_90.json")); L = json.load(open("lines_90.json"))
SCREEN = {
 0: "CDP screen recording starts scrolling (top→bottom); left list: Common Data Platform / Content Services / Data Governance",
 1: "CDP page → ECS page (solix.com/products/enterprise-content-services/); chips STRUCTURED + UNSTRUCTURED, DOCUMENTS + EMAIL",
 2: "EDG screen recording scrolls down + NEW AT EMPOWER tag; chip POLICY EVERYWHERE, INCLUDING AI",
 3: "Four-pillar graphic: Understand / Answer / Build / Act",
 4: "Chain DATA SENSE → DATA ASK → AI WAREHOUSE → AGENTS; Data Sense, Data Ask, AI Warehouse, Agentic pages switch on each name",
 5: "Pill row; Application Retirement + Data Preservation pages → SAP / Oracle / Mainframe → Email / File / Database / Active Archiving",
 6: "Statement: THAT HISTORY BECOMES AI-READY, NOT DEAD WEIGHT.",
 7: "DATA + AI → ACCELERATE DRUG DISCOVERY; molecule; RESEARCH → INTELLIGENT INSIGHTS",
 8: "Subtitle + Care Creates Data | Data Accelerates Cure; TRUSTED DATA FOUNDATION → COLLABORATIVE INTELLIGENCE → ACTIONABLE OUTCOMES",
 9: "Six-pillar EAI Healthcare platform (static); pillars 3, 5, 4, 6 highlight on the spoken names",
 10: "3D wheel: AI-Ready Data / People / Enterprise + right-side list",
 11: "Customer logos screen recording; FORTUNE 2000 counter",
 12: "Analyst recognition page; Gartner, IDC, Forrester, Bloor appear on cue",
 13: "FROM DATA TO INTELLIGENCE / FROM GOVERNANCE TO ACTION",
 14: "End lockup: Solix logo, SOLIX EMPOWER 2026, THE AGENTIC ENTERPRISE",
}
def mmss(x): return f"{int(x//60):02d}:{x%60:05.2f}"
out = ["# Solix Empower 2026 – 90-second version: cue sheet", "",
       f"Parts total **{T['total']:.1f}s** (your Scene 1 goes in front: ~7s keeps the full film at 90s).",
       "All section headings removed so you can add your own. Times are relative to the start of each clip.", ""]
for nm, a, b in T["parts"]:
    out += [f"### {nm.replace('_', ' ')}  ({b - a:.2f}s)", f"`{nm}.mp4` / `{nm}.mov`", "", "| Clip time | Narration | On screen |", "|---|---|---|"]
    for i, ln in enumerate(T["lines"]):
        s = ln["start"]
        if a - 0.01 <= s < b:
            out.append(f"| {mmss(s - a)} | {L[i]['cap']} | {SCREEN[i]} |")
    out.append("")
open("CUE_SHEET_90.md", "w").write("\n".join(out)); print("\n".join(out))
