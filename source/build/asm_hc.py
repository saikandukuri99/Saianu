import json, subprocess, numpy as np, soundfile as sf
T90 = json.load(open("timeline_90.json")); THC = json.load(open("timeline_hc.json"))
p90 = {n: (a, b) for n, a, b in T90["parts"]}; phc = {n: (a, b) for n, a, b in THC["parts"]}
order = ["02_Foundation", "03_Enterprise_AI", "04_Data_Lifecycle", "05a_EAI_Pharma", "05b_EAI_Healthcare_Foundation",
         "05c_EAI_Healthcare_Platform", "05c2_EAI_Healthcare_Capabilities", "05d_Solix_Academy", "06_Customers_Recognition",
         "07a_Close_Statement", "07b_End_Lockup"]
HC = {"05b_EAI_Healthcare_Foundation", "05c_EAI_Healthcare_Platform", "05c2_EAI_Healthcare_Capabilities"}
SR = 48000
vo90, _ = sf.read("vo90_full.wav"); vohc, _ = sf.read("vo3_full_hc.wav")
out, t, starts = [], 0.0, {}
for n in order:
    a, b = (phc if n in HC else p90)[n]
    src = vohc if n in HC else vo90
    nf = int(round(b * 30)) - int(round(a * 30)); d = nf / 30
    i0 = int(round(a * 30)) * SR // 30
    seg = src[i0:i0 + int(round(d * SR))]
    seg = np.pad(seg, (0, int(round(d * SR)) - len(seg)))
    sf.write(f"deliver90/audio/{n}_VO.wav", seg, SR, subtype="PCM_24")
    starts[n] = t; out.append(seg); t += d
vo = np.concatenate(out); sf.write("vo_final_full.wav", vo, SR, subtype="PCM_24")
s6 = starts["06_Customers_Recognition"] + (T90["segs"][6]["start"] - p90["06_Customers_Recognition"][0])
segs = [0, 0, starts["03_Enterprise_AI"], starts["04_Data_Lifecycle"], starts["05a_EAI_Pharma"], starts["06_Customers_Recognition"], s6, starts["07a_Close_Statement"]]
json.dump({"total": t, "segs": [{"i": k, "start": s} for k, s in enumerate(segs)], "lines": []}, open("timeline_final.json", "w"))
json.dump({"order": order, "starts": starts}, open("final_order.json", "w"), indent=1)
print("total", round(t, 2))
