f=89.4/76.35
G=[("L01",0.05,3.2),("L02",3.55,10.35),("L03",10.55,13.4),("L04",13.5,18.3),("L06",18.7,26.3),("L07",26.6,33.4),("L08",33.7,42.1),("L09",42.4,48.8),("L10",49.1,56.3),("L11",56.6,62.6),("L12a",63.2,66.8),("L12b",67.05,71.45),("L13",71.95,76.35)]
W={k:(round(a*f,2),round(b*f,2)) for k,a,b in G}
# longer narration gap before Data Sense (L06 now starts at 22.6 s); later lines re-fitted to still end at ~89.4 s
_o=W['L06'][0];_sc=(89.4-22.6)/(89.4-_o);_after=False
for k,_,_ in G:
    if k=='L06': _after=True
    if _after: W[k]=(round(22.6+(W[k][0]-_o)*_sc,2),round(22.6+(W[k][1]-_o)*_sc,2))
TXT={
 "L01":[(0,"Put AI, in the hands of your business.")],
 "L02":[(1,"Your enterprise data isn't usable by AI."),(2,"Cryptic tables."),(3,"Disconnected systems."),(None,"No semantic layer."),(4,"No governance.")],
 "L03":[(5,"Solix Enterprise AI, makes your data AI-activated.")],
 "L04":[(6,"That unlocks Enterprise AI."),(7,"Answer from it."),(8,"Build on it."),(9,"Activate it.")],
 "L06":[(12,"Data Sense maps your ERPs and cloud platforms, their tables and relationships, so AI understands what your data means.")],
 "L07":[(13,"The Cross-Application Knowledge Graph connects data across all your business applications, so AI understands the full picture.")],
 "L08":[(14,"Data Ask answers in plain language, across structured and unstructured data, with sources cited."),(15,"If unsure, it asks."),(None,"It never guesses.")],
 "L09":[(16,"AI Warehouse is where your people build their own AI applications, on governed, quality-checked, AI-activated data.")],
 "L10":[(17,"Agentic lets your domain experts describe an application in plain language."),(18,"AI agents build, test and run it.")],
 "L11":[(19,"Any data platform."),(20,"Any LLM."),(21,"Any deployment."),(None,"No migration, and your experts stay in command.")],
 "L12a":[(22,"With Solix Enterprise AI, your AI can be trusted.")],
 "L12b":[(23,"Every answer cited."),(24,"Humans in the loop."),(25,"Governed from day one.")],
 "L13":[(26,"Solix Enterprise AI."),(27,"Put AI in the hands of your business.")],
}
GAP={"L02":.3,"L04":.4,"L08":.4,"L10":.4,"L11":.45,"L12b":.6,"L13":.5}
