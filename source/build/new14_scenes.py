def scene1(c, t, lt, G):
    k = 1
    t1 = lc(k, 1, "Common Data")
    t2 = lc(k, 1, "Content Services")
    t3 = lc(k, 2, "Enterprise Data Governance")
    pills = [("Common Data Platform", "Structured and unstructured data, together", t1, "db"),
             ("Enterprise Content Services", "Governs documents and email", t2, "doc"),
             ("Enterprise Data Governance", "Enforces policy everywhere, including AI", t3, "shield")]
    act = -1
    for j, p in enumerate(pills):
        if lt >= p[2]:
            act = j
    for j, (ti, sub, tk, ic) in enumerate(pills):
        a = vis(lt, 0.4 + 0.15 * j) * G
        callout(c, 92, 262 + j * 116, j + 1, ti, sub, 540, a, active=(j == act), ico=ic)
        if j == 2 and a > 0:
            bdg = new_badge()
            ba = vis(lt, t3 + 0.2, None, 0.4) * G
            put_scaled(c, bdg, 92 + 540 - bdg.width / 2 - 6, 262 + 2 * 116 - 4, 0.8 + 0.2 * back((lt - t3 - 0.2) / 0.5), ba)
    chips = [("STRUCTURED + UNSTRUCTURED", lc(k, 1, "structured")), ("DOCUMENTS + EMAIL", lc(k, 1, "documents")),
             ("POLICY EVERYWHERE, INCLUDING AI", lc(k, 2, "including AI"))]
    for j, (lab, tk) in enumerate(chips):
        im = text(lab, "bold", 18, KICK if j < 2 else (255, 120, 120), 3)
        put(c, im, 92 + (1 - ease((lt - tk) / 0.5)) * 24, 650 + j * 40, vis(lt, tk, None, 0.5) * G)
    items = [(0.45, "scroll", "cdp"), (t2, "still", "ecs"), (t3, "scroll", "edg")]
    im = card_switch(c, lt, items, 680, 262, 1160, 600, G)
    if lt >= t3 and im is not None:
        bdg = new_badge()
        put_scaled(c, bdg, 680 + im.width - bdg.width / 2 - 24, 262 + 76, 0.8 + 0.2 * back((lt - t3 - 0.5) / 0.5), vis(lt, t3 + 0.5, None, 0.4) * G)


def scene2(c, t, lt, G):
    k = 2
    chain = [("DATA SENSE", lc(k, 4, "Data Sense", lead=0.3)), ("DATA ASK", lc(k, 4, "Data Ask", lead=0.3)),
             ("AI WAREHOUSE", lc(k, 4, "AI Warehouse", lead=0.3)), ("AGENTS", lc(k, 4, "agents", lead=0.3))]
    info = [("Understand", "Application Knowledge Graph", "spark"), ("Answer", "Cited answers in plain English", "chat"),
            ("Build", "Teams build on it", "warehouse"), ("Act", "Agents act with confidence", "agent")]
    tB = chain[0][1] - 0.3
    if lt < tB + 0.6:
        g = G * (1 - eio((lt - tB + 0.1) / 0.6))
        cx, cy = W / 2, 560
        hub_center(c, cx, cy, 170, lt - 0.2, t, vis(lt, 0.2) * g)
        labs = [("Understand", "Data Sense", "spark", -1, -1), ("Answer", "Data Ask", "chat", -1, 1),
                ("Build", "AI Warehouse", "warehouse", 1, -1), ("Act", "Agents", "agent", 1, 1)]
        for j, (lab, sub, ic, sx, sy) in enumerate(labs):
            t0 = 0.4 + 0.2 * j
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
    items = [(tB + 0.15, "still", "datasense"), (chain[1][1], "still", "dataask"), (chain[2][1], "still", "aiwh"), (chain[3][1], "still", "agentic")]
    card_switch(c, lt, items, 92, 318, 1180, 590, G, align="left")
    lab, sub, ic = info[act]
    a = vis(lt, chain[act][1] + 0.25, None, 0.5) * G
    put_scaled(c, node(ic, 150), 1560, 470, max(0.05, back((lt - chain[act][1] - 0.1) / 0.6)), a)
    callout(c, 1330, 600, act + 1, lab, sub, 470, a)


def scene3(c, t, lt, G):
    k = 3
    tEnd = lc(k, 6, lead=0.3)
    labels = ["Application Retirement", "Data Preservation", "SAP", "Oracle", "Mainframe", "Email", "File", "Database", "Active Archiving"]
    phrases = [(5, "retires legacy"), (5, "applications"), (5, "SAP"), (5, "Oracle"), (5, "mainframe"),
               (5, "email"), (5, "file"), (5, "database"), (5, "database")]
    tl_ = [lc(k, i, ph, lead=0.25) for i, ph in phrases]
    tl_[8] += 0.4
    tG1 = min(tl_[0], 0.35)
    x = 92
    for j, lab in enumerate(labels):
        on = lt >= tl_[j]
        im = pill_img(lab.upper(), on and lt < tEnd, 14, 16, 38, 1, dim=not on)
        a = vis(lt, 0.3 + 0.04 * j) * G
        put(c, im, x, 236 + (1 - a) * 10, a)
        x += im.width + 10
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
    draw_card(c, clip("logos", lt * 1.6, 1100, 620, 1.0), 92 + (1 - ease((lt - 0.15) / 0.7)) * 80, 262, vis(lt, 0.15) * G)
    tf = lc(k, 11, "Fortune", lead=0.3)
    a = vis(lt, tf) * G
    if a > 0:
        cnt = int(round(2000 * ease((lt - tf) / 1.2) / 10)) * 10
        put(c, text("FORTUNE", "bold", 22, KICK, 6), 1270, 380 + (1 - a) * 10, a)
        put(c, text(f"{cnt}", "black", 140, TXT), 1258, 410 + (1 - a) * 10, a)
        put(c, text("ENTERPRISES", "bold", 22, TXT2, 4), 1270, 580, a)


def scene6(c, t, lt, G):
    k = 6
    items = [(0.15, "still", "recog")]
    card_switch(c, lt, items, 92, 262, 1100, 590, G)
    firms = [("Gartner", "Gartner"), ("IDC", "I D C"), ("Forrester", "Forrester"), ("Bloor Research", "Bloor")]
    for j, (nm, ph) in enumerate(firms):
        tk = lc(k, 12, ph, lead=0.25)
        a = vis(lt, tk) * G
        if a <= 0:
            continue
        put(c, firm_img(nm), 1250 + (1 - a) * 40, 330 + j * 110, a)


def scene7(c, t, lt, G):
    k = 7
    tg = lc(k, 13, "From governance", lead=0.25)
    tE = lc(k, 14, lead=0.3)
    tAg = lc(k, 14, "The Agentic", lead=0.2)
    SC_LOCAL[7] = {"tE": tE}
    if lt < tE + 0.6:
        g = G * (1 - eio((lt - tE + 0.5) / 0.5))
        grey1 = ease((lt - tg) / 0.6)
        c1 = mix(TXT, (96, 90, 160), grey1)
        c1r = mix(RED, (120, 60, 120), grey1)
        X = 150
        t0 = 0.3
        put(c, text("FROM", "bold", 22, KICK, 4), X + 8, 312, vis(lt, t0) * g)
        put(c, text("DATA", "black", 104, c1), X, 336 + (1 - ease((lt - t0) / 0.7)) * 30, vis(lt, t0) * g)
        tt = lc(k, 13, "to intelligence", lead=0.2)
        put(c, text("TO", "bold", 22, KICK, 4), X + 560, 312, vis(lt, tt) * g)
        put(c, text("INTELLIGENCE", "black", 104, c1r), X + 552, 336 + (1 - ease((lt - tt) / 0.7)) * 30, vis(lt, tt) * g)
        put(c, text("FROM", "bold", 22, KICK, 4), X + 8, 532, vis(lt, tg) * g)
        put(c, text("GOVERNANCE", "black", 104, TXT), X, 556 + (1 - ease((lt - tg) / 0.7)) * 30, vis(lt, tg) * g)
        ta = lc(k, 13, "to action", lead=0.2)
        put(c, text("TO", "bold", 22, KICK, 4), X + 860, 532, vis(lt, ta) * g)
        put(c, text("ACTION", "black", 104, RED), X + 852, 556 + (1 - ease((lt - ta) / 0.7)) * 30, vis(lt, ta) * g)
    if lt >= tE + 0.15:
        l = lt - tE - 0.15
        cx = W / 2
        hub_glow = glow(260, 40)
        put(c, hub_glow, cx - hub_glow.width / 2, 300 - hub_glow.height / 2 + 120, vis(l, 0) * G)
        lw = 700
        put_scaled(c, logo(lw), cx, 230 + (1 - ease(l / 0.8)) * 30, 0.92 + 0.08 * ease(l / 1.2), vis(l, 0, None, 0.8) * G)
        t1 = text("SOLIX EMPOWER 2026", "black", 112, TXT)
        put(c, t1, (W - t1.width) / 2, 345 + (1 - ease((l - 0.3) / 0.7)) * 30, vis(l, 0.3) * G)
        la = tAg - tE
        t2 = text("THE AGENTIC ENTERPRISE", "xbold", 70, RED, 2)
        put(c, t2, (W - t2.width) / 2, 485 + (1 - ease((l - la) / 0.7)) * 30, vis(l, la) * G)
        ln = int(260 * ease((l - la - 0.2) / 0.7))
        if ln > 0:
            ImageDraw.Draw(c).rectangle(((W - ln) // 2, 592, (W + ln) // 2, 595), fill=RED)
        t3 = text("Where Data, AI and Industry Come Together.", "med", 36, TXT2)
        put(c, t3, (W - t3.width) / 2, 624, vis(l, la + 0.6) * G)


def academy_phase(c, t, l, a):
    """Solix Academy: 3D AI-journey wheel straight away (no title, no learning path)."""
    tA = SC_LOCAL[4]["tA"]
    segt = [0.35, max(0.9, lc(4, 10, "organizations", lead=0.35) - tA), lc(4, 10, "AI-ready", lead=0.35) - tA]
    wheel3d(c, 900, 540, l, t, a * ease(l / 0.4), segt)
    items = [("AI-READY DATA", "Solix CDP"), ("AI-READY PEOPLE", "Solix Academy"), ("AI-READY ENTERPRISE", "Solix EAI")]
    for j, (t1_, t2_) in enumerate(items):
        ia = a * ease((l - segt[j] - 0.2) / 0.5)
        if ia <= 0:
            continue
        y_ = 360 + j * 130
        ImageDraw.Draw(c).rectangle((1450, y_ + 4, 1455, y_ + 82), fill=mix(BGC, RED, ia))
        put(c, text(t1_, "black", 30, TXT, 1), 1474 + (1 - ia) * 24, y_, ia)
        put(c, text(t2_, "semi", 24, KICK), 1476 + (1 - ia) * 24, y_ + 44, ia)


def scene4(c, t, lt, G):
    k = 4
    tF = lc(k, 8, lead=0.55)
    tC = lc(k, 9, lead=0.5)
    tLock = lc(k, 10, lead=0.5)
    SC_LOCAL[4] = {"tF": tF, "tC": tC, "tL": tLock, "tA": tLock + 0.2}
    if lt < tF + 0.5:
        pharma_phase(c, t, lt, G * phase_alpha(lt, 0.0, tF, 0.4, 0.5))
    if tF <= lt < tC + 0.5:
        foundation_phase(c, t, lt - tF, G * phase_alpha(lt, tF, tC, 0.3, 0.5))
    if tC <= lt < tLock + 0.5:
        platform_phase(c, t, lt - tC, G * phase_alpha(lt, tC, tLock, 0.3, 0.5))
    if lt >= tLock + 0.2:
        academy_phase(c, t, lt - tLock - 0.2, G * ease((lt - tLock - 0.2) / 0.5))
