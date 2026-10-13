# (text, speed, gain_db, pitch, pause_before)
# Tone: S = serious (problem), N = confident/upbeat narration, M = mild stress,
# P = product name (stressed), B = brand name (strongest: slower, louder, higher)
S=lambda t,s=.93,g=0,p=.975,pb=0.0:(t,s,g,p,pb)
N=lambda t,s=1.0,g=0,p=1.02,pb=0.0:(t,s,g,p,pb)
M=lambda t,s=.93,g=1.5,p=1.03,pb=0.0:(t,s,g,p,pb)
P=lambda t,s=.85,g=3.5,p=1.06,pb=0.0:(t,s,g,p,pb)
B=lambda t,s=.83,g=4,p=1.065,pb=0.0:(t,s,g,p,pb)
SPEC=[
 [N("Put AI in the hands of",.97,0,1.015), M("your business.",.9,2,1.03,.08)],
 [S("But your enterprise data",.96), S("isn't usable by AI.",.88,1.5,.97,.2)],
 [S("Cryptic tables.",.88,1,.97)],
 [S("Disconnected systems.",.88,1,.97)],
 [S("No governance.",.86,1.5,.965)],
 [B("Solix Enterprise AI",.82,4,1.065), N("makes your data",1.0,0,1.02,.14), M("AI-activated.",.9,2,1.04,.08)],
 [N("That unlocks",1.0), P("Enterprise AI.",.85,3.5,1.06,.06)],
 [M("Answer from it.")],
 [M("Build on it.")],
 [M("Activate it.")],
 [M("Four services.",.92,2,1.03)],
 [M("One framework.",.9,2.5,1.035)],
 [P("Data Sense",.82,3.5,1.065), N("maps your ERPs and cloud platforms,",1.0,0,1.02,.1), N("so AI understands your data.",1.0,0,1.02,.1)],
 [P("The Cross-Application Knowledge Graph",.87,3,1.05), N("connects finance,",1.0,0,1.02,.12), N("manufacturing and supply chain.",1.0,0,1.02,.08)],
 [P("Data Ask",.82,3.5,1.065), N("answers in plain language,",1.0,0,1.02,.1), N("with sources cited.",.95,1.5,1.03,.12)],
 [N("If unsure,"), N("it asks.",.92,1.5,1.03,.15)],
 [P("AI Warehouse",.82,3.5,1.065), N("is where your people build",1.0,0,1.02,.1), N("their own AI applications.",.97,1,1.025,.1)],
 [P("Agentic",.82,3.5,1.065), N("lets experts describe an app in plain language.",1.0,0,1.02,.1)],
 [N("AI agents",.95,1.5,1.03), N("build and run it.",.97,1,1.025,.08)],
 [M("Any data platform.")],
 [M("Any LLM.")],
 [M("Any deployment.")],
 [N("AI your business"), M("can trust.",.9,2,1.03,.1)],
 [M("Every answer cited.")],
 [M("Humans in the loop.")],
 [M("Governed from day one.")],
 [B("Solix Enterprise AI.",.8,4,1.065)],
 [N("Put AI in the hands of",.95,0,1.015), B("your business.",.84,3.5,1.055,.1)],
]
