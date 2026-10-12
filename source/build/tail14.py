SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7]
MODE = os.environ.get("MODE", "plain")   # plain | alpha


def scenes_on(c, t):
    for k, s in enumerate(SC):
        if s["start"] <= t < s["end"]:
            SCENES[k](c, t, t - s["start"], 1.0)
    return c


def plain_bg(t):
    bg = background()
    ox = 130 + 120 * math.sin(t / 10.0)
    oy = 90 + 80 * math.cos(t / 12.0)
    return bg.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))


def frame_plain(t):
    return scenes_on(plain_bg(t), t)


def frame_rgba(t):
    """Difference matte: render the graphics over black and over white, solve for colour + alpha."""
    b = np.asarray(scenes_on(Image.new("RGB", (W, H), (0, 0, 0)), t), np.float32)
    w = np.asarray(scenes_on(Image.new("RGB", (W, H), (255, 255, 255)), t), np.float32)
    al = np.clip(1.0 - (w - b).mean(axis=2) / 255.0, 0.0, 1.0)
    rgb = np.where(al[..., None] > 1e-3, b / np.maximum(al[..., None], 1e-3), 0.0)
    out = np.dstack([np.clip(rgb, 0, 255), al * 255]).round().astype(np.uint8)
    return out


def frame(t):
    return frame_plain(t)


def render_clip(args):
    name, t0, t1, outdir = args
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/{name}"
    if MODE == "alpha":
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", out + ".mov"]
    else:
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "13", "-tune", "animation", "-pix_fmt", "yuv420p", out + ".mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        im = frame_rgba(f / FPS) if MODE == "alpha" else np.asarray(frame_plain(f / FPS))
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return name


def write_srt(name, t0, t1, outdir):
    def ts(x):
        x = max(0.0, x); h = int(x // 3600); m = int(x % 3600 // 60); s_ = x % 60
        return f"{h:02d}:{m:02d}:{int(s_):02d},{int(round((s_ % 1) * 1000)):03d}".replace(",1000", ",999")
    n = 0; out = []
    for (a, b, txt, i, first) in CAPS:
        if a >= t0 - 0.01 and a < t1:
            n += 1
            out.append(f"{n}\n{ts(a - t0)} --> {ts(min(b, t1) - t0)}\n{txt}\n")
    open(f"{outdir}/{name}.srt", "w").write("\n".join(out))


def part_specs():
    s4 = SC[4]["start"]
    tF = lc(4, 8, lead=0.55); tC = lc(4, 9, lead=0.5); tLock = lc(4, 10, lead=0.5)
    s7 = SC[7]["start"]
    tE = lc(7, 14, lead=0.3)
    return [("02_Foundation", 0.0, SC[2]["start"]),
            ("03_Enterprise_AI", SC[2]["start"], SC[3]["start"]),
            ("04_Data_Lifecycle", SC[3]["start"], SC[4]["start"]),
            ("05a_EAI_Pharma", s4, s4 + tF + 0.25),
            ("05b_EAI_Healthcare_Foundation", s4 + tF + 0.25, s4 + tC + 0.25),
            ("05c_EAI_Healthcare_Platform", s4 + tC + 0.25, s4 + tLock + 0.35),
            ("05d_Solix_Academy", s4 + tLock + 0.35, SC[5]["start"]),
            ("06_Customers_Recognition", SC[5]["start"], SC[7]["start"]),
            ("07a_Close_Statement", s7, s7 + tE + 0.1),
            ("07b_End_Lockup", s7 + tE + 0.1, TOTAL)]


def dump_timeline():
    segs = [{"i": k, "start": SC[k]["start"], "end": SC[k]["end"]} for k in range(8)]
    json.dump({"total": TOTAL, "segs": segs, "lines": [{"start": L["start"], "dur": L["dur"]} for L in LINES],
               "parts": part_specs()}, open(f"{B}/timeline_90.json", "w"), indent=1)


if __name__ == "__main__":
    mode = sys.argv[1]
    dump_timeline()
    if mode == "info":
        print("total", round(TOTAL, 2)); [print(k, round(s["start"], 2), round(s["end"], 2)) for k, s in enumerate(SC)]
        for p in part_specs():
            print(p[0], round(p[1], 3), round(p[2], 3), round(p[2] - p[1], 2))
    elif mode == "still":
        for ts in sys.argv[2:]:
            if MODE == "alpha":
                Image.fromarray(frame_rgba(float(ts)), "RGBA").save(f"{B}/a14_{ts}.png")
            else:
                frame_plain(float(ts)).save(f"{B}/s14_{ts}.jpg", quality=90)
    elif mode == "parts":
        from multiprocessing import Pool
        outdir = sys.argv[2]
        nw = int(sys.argv[3]) if len(sys.argv) > 3 else 4
        only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
        os.makedirs(outdir, exist_ok=True)
        specs = [p for p in part_specs() if only is None or p[0] in only]
        for nm, a, b in specs:
            write_srt(nm, a, b, outdir)
        ext = ".mov" if MODE == "alpha" else ".mp4"
        chunks = []
        for nm, a, b in specs:
            nf = int(round(b * FPS)) - int(round(a * FPS))
            n = max(1, nf // 120)
            fa = int(round(a * FPS))
            for q in range(n):
                f0 = fa + nf * q // n; f1 = fa + nf * (q + 1) // n
                chunks.append((f"{nm}__{q:02d}", f0 / FPS, f1 / FPS, outdir + "/_chunks"))
        with Pool(nw) as pool:
            for r_ in pool.imap_unordered(render_clip, chunks):
                pass
        for nm, a, b in specs:
            nf = int(round(b * FPS)) - int(round(a * FPS))
            n = max(1, nf // 120)
            lst = f"{outdir}/_chunks/{nm}.txt"
            with open(lst, "w") as f:
                for q in range(n):
                    f.write(f"file '{outdir}/_chunks/{nm}__{q:02d}{ext}'\n")
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                            f"{outdir}/{nm}{ext}"], check=True)
            print("PART", nm, round(a, 3), round(b, 3), flush=True)
