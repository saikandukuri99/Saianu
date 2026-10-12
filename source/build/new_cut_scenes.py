def scene0(c, t, lt, G):
    return


def scene1(c, t, lt, G):
    k = 1
    heading(c, lt, "SOLIX ENTERPRISE FOUNDATION", "Step One: AI-Ready", G)
    t1 = lc(k, 1, "Common Data")
    t2 = lc(k, 2, "Enterprise Content")
    t3 = lc(k, 3, "Enterprise Data Governance")
    pills = [("Common Data Platform", "Structured and unstructured data, together", t1, "db"),
             ("Enterprise Content Services", "Governs documents and email", t2, "doc"),
             ("Enterprise Data Governance", "Enforces policy wherever data is used", t3, "shield")]
    act = -1
    for j, p in enumerate(pills):
        if lt >= p[2]:
            act = j
    for j, (ti, sub, tk, ic) in enumerate(pills):
        a = vis(lt, 0.5 + 0.15 * j) * G
        callout(c, 92, 262 + j * 116, j + 1, ti, sub, 540, a, active=(j == act), ico=ic)
        if j == 2 and a > 0:
            bdg = new_badge()
            ba = vis(lt, t3 + 0.2, None, 0.4) * G
            put_scaled(c, bdg, 92 + 540 - bdg.width / 2 - 6, 262 + 2 * 116 - 4, 0.8 + 0.2 * back((lt - t3 - 0.2) / 0.5), ba)
    chips = [("STRUCTURED + UNSTRUCTURED", lc(k, 1, "structured")), ("DOCUMENTS + EMAIL", lc(k, 2, "documents")),
             ("INCLUDING BY AI", lc(k, 3, "including by AI"))]
    for j, (lab, tk) in enumerate(chips):
        im = text(lab, "bold", 18, KICK if j < 2 else (255, 120, 120), 3)
        put(c, im, 92 + (1 - ease((lt - tk) / 0.5)) * 24, 650 + j * 40, vis(lt, tk, None, 0.5) * G)
    items = [(0.55, "scroll", "cdp"), (t2, "still", "ecs"), (t3, "scroll", "edg")]
    im = card_switch(c, lt, items, 680, 262, 1160, 600, G)
    if lt >= t3 and im is not None:
        bdg = new_badge()
        put_scaled(c, bdg, 680 + im.width - bdg.width / 2 - 24, 262 + 76, 0.8 + 0.2 * back((lt - t3 - 0.5) / 0.5), vis(lt, t3 + 0.5, None, 0.4) * G)


def scene2(c, t, lt, G):
    k = 2
    heading(c, lt, "STEP TWO: AI-ACTIVATED", "Solix Enterprise AI", G)
    chain = [("DATA SENSE", lc(k, 5, "Data Sense", lead=0.3)), ("DATA ASK", lc(k, 6, "Data Ask", lead=0.3)),
             ("AI WAREHOUSE", lc(k, 7, "AI Warehouse", lead=0.3)), ("AGENTS", lc(k, 8, "agents", lead=0.3))]
    info = [("Understand", "Application Knowledge Graph", "spark"), ("Answer", "Cited answers in plain English", "chat"),
            ("Build", "Teams build on it", "warehouse"), ("Act", "Agents act with confidence", "agent")]
    tB = chain[0][1] - 0.3
    if lt < tB + 0.6:
        g = G * (1 - eio((lt - tB + 0.1) / 0.6))
        cx, cy = W / 2, 560
        hub_center(c, cx, cy, 170, lt - 0.3, t, vis(lt, 0.3) * g)
        labs = [("Understand", "Data Sense", "spark", -1, -1), ("Answer", "Data Ask", "chat", -1, 1),
                ("Build", "AI Warehouse", "warehouse", 1, -1), ("Act", "Agents", "agent", 1, 1)]
        for j, (lab, sub, ic, sx, sy) in enumerate(labs):
            t0 = 0.5 + 0.25 * j
            aa = vis(lt, t0) * g
            if aa <= 0:
                continue
            ex = cx + sx * 470
            pts = bez((cx + sx * 140, cy + sy * 30), (cx + sx * 280, cy + sy * 30), (cx + sx * 300, cy + sy * 160), (ex, cy + sy * 160))
            connector(c, pts, ease((lt - t0) / 0.7), aa, t + j * 0.25)
            callout(c, ex + 10 if sx > 0 else ex - 470, cy + sy * 160 - 48, j + 1, lab, sub, 460, aa, ico=ic)
    if lt < tB:
        return
    act = 0
    for j, (_, tk) in enumerate(chain):
        if lt >= tk:
            act = j
    x = 92
    for j, (lab, _) in enumerate(chain):
        im = pill_img(lab, j == act, 16, 20, 44, 1, dim=j > act)
        a = vis(lt, tB + 0.1 * j) * G
        put(c, im, x, 236 + (1 - a) * 12, a)
        if j < 3:
            put(c, text("→", "bold", 24, RED if j < act else (200, 170, 170)), x + im.width + 9, 241, a)
            x += im.width + 46
    items = [(tB + 0.15, "still", "datasense"),
             (lc(k, 5, "Application Knowledge", lead=0.3), "scroll", "akg"),
             (chain[1][1], "still", "dataask"), (chain[2][1], "still", "aiwh"), (chain[3][1], "still", "agentic")]
    card_switch(c, lt, items, 92, 318, 1180, 590, G, align="left")
    lab, sub, ic = info[act]
    a = vis(lt, chain[act][1] + 0.25, None, 0.5) * G
    put_scaled(c, node(ic, 150), 1560, 470, max(0.05, back((lt - chain[act][1] - 0.1) / 0.6)), a)
    callout(c, 1330, 600, act + 1, lab, sub, 470, a)


def scene3(c, t, lt, G):
    k = 3
    heading(c, lt, "DATA LIFECYCLE & ARCHIVING", "Move It Once. Access It Always.", G)
    tIntro, tG1, tG2, tEnd = [cue(i) - SC[3]["start"] - 0.3 for i in SC[3]["lines"]]
    labels = ["Application Retirement", "Data Preservation", "SAP", "Oracle", "Mainframe", "Email", "File", "Database", "Active Archiving"]
    phrases = [(10, "Retiring legacy"), (10, "preserving records"), (11, "SAP"), (11, "Oracle"), (11, "mainframe"),
               (11, "email"), (11, "file"), (11, "database"), (11, "database")]
    tl_ = [lc(k, i, ph, lead=0.25) for i, ph in phrases]
    tl_[8] += 0.4
    x = 92
    for j, lab in enumerate(labels):
        on = lt >= tl_[j]
        im = pill_img(lab.upper(), on and lt < tEnd, 14, 16, 38, 1, dim=not on)
        a = vis(lt, 0.5 + 0.04 * j) * G
        put(c, im, x, 236 + (1 - a) * 10, a)
        x += im.width + 10
    # intro: lifecycle ring
    if lt < tG1 + 0.5:
        g = G * (1 - eio((lt - tG1) / 0.5))
        cx, cy = W / 2, 590
        a = vis(lt, 0.3) * g
        hub_center(c, cx, cy, 150, lt - 0.3, t, a)
        stages = [("RETIRE", "cycle"), ("PRESERVE", "shield"), ("ARCHIVE", "db"), ("ACTIVATE", "spark")]
        R = 300
        for j, (lab, ic) in enumerate(stages):
            t0 = 0.5 + 0.25 * j
            aa = vis(lt, t0) * g
            if aa <= 0:
                continue
            ang = -math.pi / 2 + j * math.pi / 2 + 0.25
            a0 = math.degrees(ang) + 14
            ImageDraw.Draw(c).arc((cx - R * 1.35, cy - R * 0.78, cx + R * 1.35, cy + R * 0.78), a0, a0 + 62 * ease((lt - t0) / 0.7), fill=mix(BGC, RED, aa), width=4)
            nx, ny = cx + R * 1.35 * math.cos(ang), cy + R * 0.78 * math.sin(ang)
            put_scaled(c, node(ic, 110), nx, ny, max(0.05, back((lt - t0) / 0.6)), aa)
            tlab = text(lab, "bold", 20, TXT, 3)
            put(c, tlab, nx - tlab.width / 2, ny + 66, aa)
    # retire + preserve
    tS = tl_[2] - 0.1
    if tG1 <= lt < tS + 0.5:
        l = lt - tG1
        g = G * (1 - eio((lt - tS) / 0.5))
        for j, (nm, lab, tj) in enumerate([("appret", "APPLICATION RETIREMENT", 0.0), ("datapres", "DATA PRESERVATION", tl_[1] - tG1)]):
            im = still(nm, 840, 520, l - tj, tS - tG1 - tj)
            x0 = 92 + j * 900
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.6)) * 100, 330, a)
            put(c, pill_img(lab, True, 15, 18, 40, 2), x0 + 20, 300 + (1 - a) * 10, a)
    # SAP / Oracle / Mainframe
    tE = tl_[5] - 0.1
    if tS <= lt < tE + 0.5:
        l = lt - tS
        g = G * (1 - eio((lt - tE) / 0.5))
        for j, (nm, lab) in enumerate([("sap", "SAP"), ("oracle", "ORACLE"), ("mainframe", "MAINFRAME")]):
            tj = max(0.0, tl_[2 + j] - tS)
            im = still(nm, 760, 380, l - tj, tE - tS - tj)
            x0, y0 = 92 + j * 300, 330 + j * 120
            a = vis(l, tj) * g
            draw_card(c, im, x0 + (1 - ease((l - tj) / 0.6)) * 120, y0, a)
            put(c, pill_img(lab, True, 16, 20, 42, 2), x0 + 18, y0 - 26, a)
    # Email / File / Database / Active archiving
    if tE <= lt < tEnd + 0.5:
        l = lt - tE
        g = G * (1 - eio((lt - tEnd) / 0.5))
        cells = [("email", "EMAIL"), ("file", "FILE"), ("database", "DATABASE"), ("active", "ACTIVE ARCHIVING")]
        for j, (nm, lab) in enumerate(cells):
            tj = max(0.0, tl_[5 + j] - tE)
            cx0, cy0 = 92 + (j % 2) * 880, 320 + (j // 2) * 316
            im = still(nm, 840, 290, l - tj, tEnd - tE - tj)
            a = vis(l, tj) * g
            draw_card(c, im, cx0 + (840 - im.width) / 2, cy0 + 22 + (1 - ease((l - tj) / 0.6)) * 40, a)
            put(c, pill_img(lab, True, 15, 18, 40, 2), cx0 + 10, cy0 - 2, a)
    # closing statement
    if lt >= tEnd:
        l = lt - tEnd
        a = G * ease(l / 0.5)
        t1 = text("THAT HISTORY BECOMES", "black", 64, TXT, 2)
        put(c, t1, (W - t1.width) / 2, 430 + (1 - ease(l / 0.6)) * 24, a)
        t2 = text("AI-READY,", "black", 84, (255, 255, 255), 2)
        t3 = text("NOT DEAD WEIGHT.", "black", 84, TXT, 2)
        tw = t2.width + 40 + t3.width + 24
        x0 = (W - tw) / 2
        sp = eio((l - 0.4) / 0.5)
        if sp > 0:
            pl = Image.new("RGBA", (t2.width + 40, t2.height + 8), (0, 0, 0, 0))
            ImageDraw.Draw(pl).rounded_rectangle((0, 0, int((t2.width + 40) * sp), t2.height + 7), 14, fill=BLUE + (255,))
            put(c, pl, x0, 528, a)
        put(c, t2, x0 + 20, 532, G * ease((l - 0.6) / 0.4))
        put(c, t3, x0 + t2.width + 64, 532 + (1 - ease((l - 0.8) / 0.5)) * 20, G * ease((l - 0.8) / 0.5))


def scene5(c, t, lt, G):
    k = 5
    heading(c, lt, "TRUSTED BY GLOBAL ENTERPRISES", "Trusted by Leading Enterprises", G)
    dur = SC[5]["end"] - SC[5]["start"]
    draw_card(c, clip("logos", lt * 1.6, 1100, 620, 1.0), 92 + (1 - ease((lt - 0.2) / 0.7)) * 80, 262, vis(lt, 0.2) * G)
    tf = lc(k, 13, "Fortune", lead=0.3)
    a = vis(lt, tf) * G
    if a > 0:
        cnt = int(round(2000 * ease((lt - tf) / 1.2) / 10)) * 10
        put(c, text("FORTUNE", "bold", 22, KICK, 6), 1270, 380 + (1 - a) * 10, a)
        put(c, text(f"{cnt}", "black", 140, TXT), 1258, 410 + (1 - a) * 10, a)
        put(c, text("ORGANIZATIONS", "bold", 22, TXT2, 4), 1270, 580, a)


def scene6(c, t, lt, G):
    k = 6
    heading(c, lt, "RECOGNIZED BY INDUSTRY EXPERTS", "Recognized by Leading Research Firms", G)
    items = [(0.2, "still", "recog")]
    card_switch(c, lt, items, 92, 262, 1100, 590, G)
    firms = [("Gartner", "Gartner"), ("IDC", "I D C"), ("Forrester", "Forrester"), ("Bloor Research", "Bloor")]
    for j, (nm, ph) in enumerate(firms):
        tk = lc(k, 14, ph, lead=0.25)
        a = vis(lt, tk) * G
        if a <= 0:
            continue
        put(c, firm_img(nm), 1250 + (1 - a) * 40, 330 + j * 110, a)
