import json, soundfile as sf, os
B=os.path.dirname(os.path.abspath(__file__))
LEAD=0.7; GAP=0.5; TAIL=3.2
def build():
    t=LEAD; segs=[]
    for i in range(8):
        d=sf.info(f"{B}/vo_{i}.wav").duration
        segs.append({"i":i,"vo_start":t,"vo_dur":d})
        t+=d+GAP
    total=segs[-1]["vo_start"]+segs[-1]["vo_dur"]+TAIL
    for k,s in enumerate(segs):
        s["start"]=0.0 if k==0 else s["vo_start"]-0.3
        s["end"]=segs[k+1]["vo_start"]-0.3 if k<7 else total
    return {"total":total,"segs":segs}
if __name__=="__main__":
    tl=build(); json.dump(tl,open(f"{B}/timeline.json","w"),indent=1)
    print(round(tl["total"],2)); [print(s["i"],round(s["start"],2),round(s["end"],2)) for s in tl["segs"]]
