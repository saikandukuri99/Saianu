src = open("render12c.py").read()
for ln in ['    put_scaled(c, bolt_sphere(120), x0 - 90, 255, max(0.05, back((l - 0.1) / 0.6)), a)\n',
           '    kin_word(c, "EAI", x0, 200, 96, RED, a, 0.15, l)\n',
           '    kin_word(c, "HEALTHCARE", x0 + e.width + 24, 200, 96, TXT, a, 0.3, l)\n',
           '    put(c, k_, (W - k_.width) / 2, 160, a * ease((l - 0.3) / 0.5))\n',
           '    put(c, text("HEALTHCARE CAPABILITIES", "bold", 20, KICK, 6), 120, 230, a * ease(l / 0.5))\n']:
    assert ln in src, ln
    src = src.replace(ln, "", 1)
src = src.replace("def heading(c, lt, kicker, title, G, x=92, y=96, tout=None, size=58):\n",
                  "def heading(c, lt, kicker, title, G, x=92, y=96, tout=None, size=58):\n    return\n", 1)
tail = open("tail14.py").read()
i = tail.index("def part_specs():")
j = tail.index("def dump_timeline():")
tail = tail[:i] + '''def part_specs():
    s4 = SC[4]["start"]
    tF = lc(4, 18, lead=0.7); tC = lc(4, 19, lead=0.6); tL = lc(4, 20, lead=0.5); tLock = lc(4, 21, lead=0.55)
    return [("05b_EAI_Healthcare_Foundation", s4 + tF + 0.25, s4 + tC + 0.25),
            ("05c_EAI_Healthcare_Platform", s4 + tC + 0.25, s4 + tL + 0.25),
            ("05c2_EAI_Healthcare_Capabilities", s4 + tL + 0.25, s4 + tLock + 0.35)]


''' + tail[j:]
tail = tail.replace("timeline_90.json", "timeline_hc.json")
i = src.index("\nSCENES = [")
src = src[:i] + "\n\n" + tail
open("render12d.py", "w").write(src); print("ok")
