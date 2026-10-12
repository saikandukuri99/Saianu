import re
src = open("render13.py").read()
new = open("new14_scenes.py").read()
tail = open("tail14.py").read()
# timeline
src = src.replace('LINES = json.load(open(f"{B}/lines_cut.json"))\nFIRST = 0.75      # first VO line start\nSCENE_PAD = 0.7   # extra air at scene changes\nPRE = 0.75        # scene starts this long before its first line\nTAIL = 3.0',
                  'LINES = json.load(open(f"{B}/lines_90.json"))\nFIRST = 0.5       # first VO line start\nSCENE_PAD = 0.35  # extra air at scene changes\nPRE = 0.6         # scene starts this long before its first line\nTAIL = 2.2')
assert "lines_90" in src
src = src.replace('f"{B}/vocut/{i:02d}.wav"', 'f"{B}/vo90/{i:02d}.wav"')
# heading -> removed (client adds headings in Premiere)
src = src.replace("def heading(c, lt, kicker, title, G, x=92, y=96, tout=None, size=58):\n",
                  "def heading(c, lt, kicker, title, G, x=92, y=96, tout=None, size=58):\n    return\n", 1)
# drop old scene defs that are replaced
def drop(name):
    global src
    m = re.search(rf"\n(@lru_cache\(None\)\n)?def {name}\(.*?(?=\n(?:@lru_cache\(None\)\n)?def |\n[A-Z_]+ = |\nSCENES = )", src, re.S)
    assert m, name
    src = src[:m.start()] + "\n" + src[m.end():]
for nm in ["scene1", "scene2", "scene3", "academy_phase", "scene4", "scene5", "scene6", "scene7"]:
    drop(nm)
# industry: remap line indices (17,18,19 -> 7,8,9)
for a, b in (("lc(4, 17,", "lc(4, 7,"), ("lc(4, 18,", "lc(4, 8,"), ("lc(4, 19,", "lc(4, 9,")):
    src = src.replace(a, b)
# remove section headings in pharma / healthcare
for ln in ['    put(c, text("INDUSTRY SOLUTIONS", "bold", 20, KICK, 6), 120 - (1 - ease(l / 0.6)) * 30, 300, a * ease(l / 0.6))\n',
           '    e = kin_word(c, "EAI", 112, 330, 128, RED, a, 0.15, l)\n',
           '    kin_word(c, "PHARMA", 112 + e.width + 26, 330, 128, TXT, a, 0.3, l)\n',
           '    put_scaled(c, bolt_sphere(120), x0 - 90, 255, max(0.05, back((l - 0.1) / 0.6)), a)\n',
           '    kin_word(c, "EAI", x0, 200, 96, RED, a, 0.15, l)\n',
           '    kin_word(c, "HEALTHCARE", x0 + e.width + 24, 200, 96, TXT, a, 0.3, l)\n',
           '    put(c, k_, (W - k_.width) / 2, 160, a * ease((l - 0.3) / 0.5))\n']:
    assert ln in src, ln
    src = src.replace(ln, "", 1)
# pharma red underline under the (removed) title
ul = "    ln = int(520 * ease((l - 0.6) / 0.8))\n    if ln > 0:\n        ImageDraw.Draw(c).rectangle((120, 492, 120 + ln, 496), fill=mix(BGC, RED, a))\n"
assert ul in src; src = src.replace(ul, "", 1)
i = src.index("\nSCENES = [")
src = src[:i] + "\n\n" + new + "\n\n" + tail
open("render14.py", "w").write(src)
print("written", len(src.splitlines()))
