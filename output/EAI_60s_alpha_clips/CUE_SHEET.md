# Cue sheet: Solix Enterprise AI, 60-second teaser

Frame rate **30 fps**, size **1920 x 1080**. The voice-over is one female file, `audio/EAI_60s_VO_narration.wav` (62.3 s), fitted to the original timing: every sentence starts at the same moment as before, so clips and voice match one-to-one. Put it on A1 at 00:00:00:00, then drop each clip on its **start timecode** below and it will sit exactly on the words.

| # | Clip (in `clips/`) | Place at (V1) | Length | Voice-over on this clip | On screen |
|---|---|---|---|---|---|
| S01 | `S01_Hook__start_TC_00-00-00-00.mov` | **00:00:00:00** (0.0 s) | 3.3 s | Put AI in the hands of your business. | Headline 'Put AI in the hands of your business' + role chips (Finance, Sales, Operations, Supply chain). |
| S02 (1/2) | `S02a_Problem_Data_part1__start_TC_00-00-03-03.mov` | **00:00:03:03** (3.1 s) | 3.6 s | But your enterprise data isn't usable by AI. Cryptic tables. Disconnected systems. No governance. | **3D AI chip** (left) + three ERP/app tables with cryptic column names. Red markers: Cryptic tables, Disconnected systems, No governance. |
| S02 (2/2) | `S02b_Problem_Data_part2__start_TC_00-00-06-21.mov` | **00:00:06:21** (6.7 s) | 3.6 s | (continues, put it straight after part 1) | Same shot as part 1: red markers land on Cryptic tables, Disconnected systems, No governance. |
| S03 | `S03_Solix_Lockup__start_TC_00-00-10-06.mov` | **00:00:10:06** (10.2 s) | 4.1 s | Solix Enterprise AI makes your data AI-activated. | Flat Solix logo + SOLIX / ENTERPRISE AI lockup. Scan beam turns cryptic tables into Journal lines, Work orders, Purchase orders. |
| S04 | `S04_Four_Services__start_TC_00-00-14-06.mov` | **00:00:14:06** (14.2 s) | 7.3 s | That unlocks Enterprise AI. Answer from it. Build on it. Activate it. Four services. One framework. | Data Sense bar over three service cards (Data Ask, AI Warehouse, Agentic) in 3D tilt, then 'Four services. One framework.' |
| S05 | `S05_Data_Sense__start_TC_00-00-21-12.mov` | **00:00:21:12** (21.4 s) | 5.5 s | Data Sense maps your ERPs and cloud platforms, so AI understands your data. | Cryptic table IDs become Suppliers / Materials / Customer orders / Work orders, joined by the AKG node. Value-stream chips. |
| S06 | `S06_Knowledge_Graph_XKG__start_TC_00-00-26-27.mov` | **00:00:26:27** (26.9 s) | 5.5 s | The Cross-Application Knowledge Graph connects finance, manufacturing and supply chain. | Three systems (Supplier / Vendor / Vendor ID) join one **3D XKG orb**. One question, one answer. |
| S07 | `S07_Data_Ask__start_TC_00-00-32-12.mov` | **00:00:32:12** (32.4 s) | 5.1 s | Data Ask answers in plain language, with sources cited. If unsure, it asks. | Question -> Conversation Router -> Structured / Hybrid / Unstructured lanes -> cited answer. Chips: Sources cited, Asks if unsure. |
| S08 | `S08_AI_Warehouse__start_TC_00-00-37-12.mov` | **00:00:37:12** (37.4 s) | 4.5 s | AI Warehouse is where your people build their own AI applications. | **3D stack of governed data layers** + four-step flow (Describe, Data Sense, AI Warehouse, Your AI application). |
| S09 | `S09_Agentic__start_TC_00-00-41-27.mov` | **00:00:41:27** (41.9 s) | 5.7 s | Agentic lets experts describe an app in plain language. AI agents build and run it. | Domain expert prompt, agents orbit (Build, Test, Fix), supplier follow-up workflow runs and ticks off. |
| S10 | `S10_Open_Platform__start_TC_00-00-47-15.mov` | **00:00:47:15** (47.5 s) | 4.1 s | Any data platform. Any LLM. Any deployment. | **3D chip hub** with Any data platform (left), Any LLM (top), Any deployment (right). |
| S11 | `S11_Trust__start_TC_00-00-51-18.mov` | **00:00:51:18** (51.6 s) | 6.2 s | AI your business can trust. Every answer cited. Humans in the loop. Governed from day one. | 'AI your business can trust.' + three proof cards: Every answer cited, Humans in the loop, Governed from day one. |
| S12 | `S12_End_Card__start_TC_00-00-57-21.mov` | **00:00:57:21** (57.7 s) | 4.6 s | Solix Enterprise AI. Put AI in the hands of your business. | Flat Solix logo, SOLIX ENTERPRISE AI, gradient line, 'Put AI in the hands of your business.' |

S02 is cut into two back-to-back pieces only because GitHub rejects files over 100 MB; put part 2 directly after part 1 (no gap, frame-exact).

Clips overlap by 0.1 to 0.2 s at the joins. Each clip eases out over its last 0.3 s, so you can cut straight, dissolve, or trim the tails yourself.

## Voice-over sentence timings (for captions, sound design, music hits)
See `audio/EAI_60s_subtitles.srt` (28 lines). Import it in Premiere (File > Import) to get native editable captions, or use the pre-styled caption clips in `captions/` (same start timecodes as the clips, one per voice-over line).

| Time (s) | Words |
|---|---|
| 0.45 | Put AI in the hands of your business. |
| 3.21 | But your enterprise data isn't usable by AI. |
| 6.34 / 7.51 / 9.00 | Cryptic tables. / Disconnected systems. / No governance. |
| 10.38 | Solix Enterprise AI makes your data AI-activated. |
| 14.28 | That unlocks Enterprise AI. |
| 16.25 / 17.24 / 18.20 | Answer from it. / Build on it. / Activate it. |
| 19.13 / 20.31 | Four services. / One framework. |
| 21.58 | Data Sense maps your ERPs and cloud platforms, so AI understands your data. |
| 27.00 | The Cross-Application Knowledge Graph connects finance, manufacturing and supply chain. |
| 32.47 / 35.93 | Data Ask answers in plain language, with sources cited. / If unsure, it asks. |
| 37.53 | AI Warehouse is where your people build their own AI applications. |
| 42.01 / 45.64 | Agentic lets experts describe an app in plain language. / AI agents build and run it. |
| 47.67 / 49.12 / 50.28 | Any data platform. / Any LLM. / Any deployment. |
| 51.67 / 53.50 / 54.87 / 56.11 | AI your business can trust. / Every answer cited. / Humans in the loop. / Governed from day one. |
| 57.86 / 59.64 | Solix Enterprise AI. / Put AI in the hands of your business. |
