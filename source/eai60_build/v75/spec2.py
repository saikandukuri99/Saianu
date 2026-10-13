from spec import S,N,M,P,B
# (id, start, end, gaps between sentences, [ (old_idx or None, [phrases]) ])
LINES=[
 ("L01",0.05,3.2,[],[(0,[N("Put AI",.97,0,1.015),M("in the hands of your business.",.93,1.5,1.03,.3)])]),
 ("L02",3.55,10.35,[.2,.2,.2,.2],[(1,[S("Your enterprise data",1.0),S("isn't usable by AI.",.94,1.5,.97,.1)]),(2,[S("Cryptic tables.",.95,1,.97)]),(3,[S("Disconnected systems.",.95,1,.97)]),(None,[S("No semantic layer.",.95,1,.97)]),(4,[S("No governance.",.93,1.5,.965)])]),
 ("L03",10.55,13.4,[],[(5,[B("Solix Enterprise AI",.9,4,1.065),N("makes your data",1.0,0,1.02,.08),M("AI-activated.",.95,2,1.04,.05)])]),
 ("L04",13.5,18.3,[.28,.28,.28],[(6,[N("That unlocks",1.0),P("Enterprise AI.",.85,3.5,1.06,.06)]),(7,[M("Answer from it.")]),(8,[M("Build on it.")]),(9,[M("Activate it.")])]),
 ("L06",18.7,26.3,[],[(12,[P("Data Sense",.82,3.5,1.065),N("maps your ERPs and cloud platforms,",1.0,0,1.02,.1),N("their tables and relationships,",1.0,0,1.02,.1),N("so AI understands what your data means.",1.0,0,1.02,.1)])]),
 ("L07",26.6,33.4,[],[(13,[P("The Cross-Application Knowledge Graph",.87,3,1.05),N("connects data across all your business applications,",1.0,0,1.02,.12),N("so AI understands the full picture.",1.0,0,1.02,.1)])]),
 ("L08",33.7,42.1,[.3,.3],[(14,[P("Data Ask",.82,3.5,1.065),N("answers in plain language,",1.0,0,1.02,.1),N("across structured and unstructured data,",1.0,0,1.02,.1),N("with sources cited.",.95,1.5,1.03,.12)]),(15,[N("If unsure,"),N("it asks.",.92,1.5,1.03,.15)]),(None,[M("It never guesses.",.92,2,1.03)])]),
 ("L09",42.4,48.8,[],[(16,[P("AI Warehouse",.82,3.5,1.065),N("is where your people build their own AI applications,",1.0,0,1.02,.1),N("on governed, quality-checked, AI-activated data.",.97,1,1.025,.1)])]),
 ("L10",49.1,56.3,[.3],[(17,[P("Agentic",.82,3.5,1.065),N("lets your domain experts describe an application in plain language.",1.0,0,1.02,.1)]),(18,[N("AI agents",.95,1.5,1.03),N("build, test and run it.",.97,1,1.025,.08)])]),
 ("L11",56.6,62.6,[.3,.3,.5],[(19,[M("Any data platform.")]),(20,[M("Any LLM.")]),(21,[M("Any deployment.")]),(None,[N("No migration,"),N("and your experts stay in command.",.97,1,1.025,.1)])]),
 ("L12a",63.2,66.8,[],[(22,[N("With",1.0),B("Solix Enterprise AI,",.84,3.5,1.06,.05),N("your AI can be",1.0,0,1.02,.1),M("trusted.",.85,2,1.03,.12)])]),
 ("L12b",67.05,71.45,[.45,.45],[(23,[M("Every answer cited.")]),(24,[M("Humans in the loop.")]),(25,[M("Governed from day one.")])]),
 ("L13",71.95,76.35,[.35],[(26,[B("Solix Enterprise AI.",.8,4,1.065)]),(27,[N("Put AI in the hands of",.95,0,1.015),B("your business.",.84,3.5,1.055,.1)])]),
]
