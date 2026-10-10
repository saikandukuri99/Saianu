import sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
D=sys.argv[1]; voice=sys.argv[2]; speed=float(sys.argv[3])
k=Kokoro(D+"/kokoro.onnx", D+"/voices.bin")
segs=[
"For more than two decades, Solix Technologies has helped enterprises transform their data into a strategic advantage, bringing together data management, governance, content services, and AI on a unified foundation.",
"At the foundation is the Solix Enterprise Platform, combining the Common Data Platform, Enterprise Data Governance, and Enterprise Content Services to discover, manage, secure, govern, and activate enterprise information across environments.",
"Building on this foundation, Solix Enterprise AI brings intelligence to enterprise data. Data Sense delivers semantic understanding. Data Ask enables natural-language interaction. Application Knowledge Graphs connect business context, while AI Warehouse and Solix Agentic help organizations build and activate governed AI.",
"Solix also delivers comprehensive data lifecycle solutions, from application retirement and data preservation to SAP, Oracle, mainframe, email, file, database, and active archiving. Enterprises can reduce complexity, control costs, and preserve valuable information without costly migration.",
"Purpose-built solutions extend this platform across industries. E A I Healthcare brings data and AI capabilities to healthcare, delivering Patient 360 and governed clinical intelligence, while E A I Pharma advances data and AI capabilities for pharmaceutical innovation, and Solix Academy helps organizations build the skills needed for an AI-ready enterprise.",
"Today, Solix technology supports leading enterprises across industries, including organizations within the Fortune two thousand. From healthcare and pharma to financial services, manufacturing, and technology, customers rely on Solix to solve complex data challenges at enterprise scale.",
"Solix's innovation has also earned recognition from leading technology research and market intelligence organizations, including Gartner, I D C, Forrester, and Bloor Research, reinforcing its position in enterprise data management and AI.",
"From data to intelligence, from governance to action, Solix is helping enterprises build the agentic future. Solix Empower 2026. The Agentic Enterprise.",
]
out=sys.argv[4]
for i,t in enumerate(segs):
    a,sr=k.create(t, voice=voice, speed=speed, lang="en-us")
    sf.write(f"{out}/vo_{i}.wav", a, sr); print(i, round(len(a)/sr,2))
