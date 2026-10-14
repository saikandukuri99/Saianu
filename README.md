# Solix Application Retirement, 60-second film (Empower 2026)

**Deliverable:** `output/Solix_Application_Retirement_60s_1080p.mp4` is 1920×1080, 30 fps, 1:10, with voice-over, music and on-screen captions.

- **v7 (current):** the 3D particle layer is removed from the whole film, along with the soft background light spots, so nothing is blurry. The background is dark Solix blue with the AI network lines at low opacity. In place of every particle shape there are crisp, After Effects-style vector animations (`mg_ar.py`), drawn supersampled with stroke draw-ons, ring wipes, overshoot pop-ins, dashed rotating rings and flowing data dots:
  - an icon badge for each trigger (Cost $, Risk shield, M&A merge, Old archive drawers, AI chip), plus a 5-step tracker under the word
  - the five triggers converging into a Solix Engine hub with a shockwave ring
  - six source nodes (ERP, Mainframe, Custom apps, SaaS, Files, Email) wiring into the hub with data flowing
  - a Preservation Zone vault (lock plus data rows filling) with packets dropping in from the source window, which moves aside and stays lit at the switch-off
  - a light stage line under the Access documents
  - a crisp knowledge graph for Data Ask (Supplier, Invoice and Payment light up, with pulses along the links)
  - an AI-readiness ring whose missing segments fill with governed history
  - dashed orbit rings around the end-card logo

  The screens, cards, text, voice-over, music and timing are unchanged.
- **v6, colour theme only:** a dark navy-blue background with light network lines (drifting connected nodes) and a soft brand-blue glow behind each 3D subject, replacing the red/indigo field. Red is kept as an accent only: the Solix logo, the Risk alert, the PAID stamp and the switch-off. Everything else is identical to v5: animation, screens, text, captions, VO, music and timing.
- **v5 changes:** the Migrate & Validate and switch-off beats now follow the script's "Real" direction with realistic 3D screens:
  - **Migrate & Validate:** the legacy Finance ERP window (the source) hovers above the governed Preservation Zone vault while data streams down into it. A Validation Report counts the archive rows up to match the source (✓ on each row, then "Validation passed"). A Governance Policy screen follows, with 10-year retention, 4 of 4 quality checks and the legal-hold switch flipping on.
  - **Switch-off:** the ERP window moves to the front and powers off like an old monitor, collapsing into a line of light. The Licenses, Servers and Unpatched risk tags fall away. An Application Inventory screen then flips Finance ERP R11 from Active to Retired, with its data preserved, while the vault stays lit.
- **v4 changes:** following the reference video, each of the five triggers now has a realistic 3D notification screen that flies in beside its extruded word, with a small animation inside (`screens_ar.py`, fictional data):
  - **Cost:** a maintenance renewal amount counting up to $480,000 a year, due in 14 days.
  - **Risk:** a flashing critical security alert with a CVSS 9.8 badge, for an unpatched server.
  - **M&A:** "Acquisition closed", with inherited systems (ERP, CRM, HR, Billing and more) stacking in.
  - **Old archive:** an archive renewal date circled on the calendar.
  - **AI:** historical-data bars filling, with dashed empty slots marking the missing history.

  The particle shape for each trigger moves behind the screen, to the upper right, for depth. "Applications you've moved on from." now sits under three realistic legacy windows floating in 3D: a finance ERP ledger, a green-screen mainframe terminal and a custom maintenance app. Each has a pulsing "Still running" light and a short stat ($1.2M a year to keep it running, 3 users a month, last patched in 2017).
- **v3 changes:** the film opens on a main title: the original Solix logo and an extruded 3D "Application Retirement" (with EMPOWER 2026) over the legacy-screens fly-in, before the narration starts. The Access beat now follows the script's "Real" direction, built as realistic 3D documents (`docs_ar.py`, fictional demo data):
  1. Solix Search types the vendor and shows its records.
  2. Purchase order, goods receipt, invoice and payment (with a PAID stamp) fly in one by one in perspective and settle into a row labelled Ordered, Received, Invoiced and Paid.
  3. Glowing arcs draw between the four documents to form an Enterprise Business Record.
  4. A standard report (Invoices by vendor, FY2019) flies forward for "Users get the reports they know."
- **v2 changes (after review):** the original Solix logo (red disc, white bolt) is used unaltered. The palette is Solix red #ee2424 as the key light behind every subject, indigo #30267b framing the edges and the text side, and blue #0088cf for highlights (key words, check marks, data streams, lit nodes, the active step). The film opens on a 3D camera fly-in through glowing legacy screens, so frame 1 is full. The 3D reads more clearly: particles are lit with a key light and depth-graded in size and haze, objects get a floor reflection, the camera orbit and pitch are deeper, and the five trigger words and "Enable AI" use extruded 3D type.
- **Look:** no boxes, cards or rules. Kinetic typography: words rise and sharpen into place one by one.
- **3D motion graphics:** a procedural particle engine with perspective, depth of field, bloom and soft bokeh. One particle system re-forms beat by beat:
  dormant dot-matrix legacy apps → Cost (coin), Risk (glitching sphere), M&A (absorbed sphere), Old archive (straining stack), AI (sphere with a missing wedge) → everything collapses to a point and bursts into the Solix engine → six sources stream in (ERP, Mainframe, Custom apps, SaaS, Files, Email) → a lattice Preservation Zone fills bottom-up with four checks → the application shell powers down and falls away while the vault stays lit → linked record graph (Invoice, PO, Receipt, Payment) → Data Ask knowledge graph with a typed question → the AI sphere's missing wedge fills with governed history (a callback to the AI trigger) → a halo around the Solix mark for the sign-off.
- **Narration:** the script's voice-over, trimmed to fit about 60 seconds (Kokoro `af_heart`, studio voice chain). The "150+ source types" claim is left out until it is verified, as the script's claims check asks.
- **Music:** an original, slow ambient score (pads, sparse felt piano, sub swell), royalty-free. It ducks under the voice, dips at the switch-off and lifts into the sign-off. Loudness is −16 LUFS.
- **Build** (`source/ar/`): `vo_ar.py` → `timeline_ar.py` → `music_ar.py` → `render_ar.py` → `mix_ar.py`. Use `python3 render_ar.py preview 12 30 45` to render single frames.

---

# Solix Empower 2026 – AV ("The Agentic Enterprise")

**Current (v7):** `output/Solix_Empower_2026_AV_v7_1080p.mp4` is the 1080p master (3:00); `output/Solix_Empower_2026_AV_v7_preview.mp4` is a single-file preview. A 4K version follows once v7 is approved.

### Changes in v7: new EAI Pharma / EAI Healthcare section (pure motion graphics)
- New narration for this section (four lines from the updated script). The screenshot and the 3D body are removed.
- **EAI Pharma:** title reveal and a rotating 3D molecule with research-data tags (compounds, assays, genomics, trials) linked by animated AI connections. DATA + AI merges into ACCELERATE DRUG DISCOVERY, followed by "Research → Intelligent Insights".
- **EAI Healthcare foundation:** Trusted Data Foundation → Collaborative AI Intelligence → Actionable Healthcare Outcomes as a horizontal flow with moving data along the links.
- **Platform:** the infographic rebuilt as motion graphics. Points converge into the big glossy Solix bolt, then the six capability nodes and the dotted ring appear. Patient 360 Analytics, AI Clinical Intelligence and Intelligent Imaging & Radiology highlight in sequence, with a gentle camera drift.
- **Capabilities:** AI Clinical Assistant, Preventive Care, Revenue Cycle Intelligence and AI-Powered Documentation, each appearing as icon → title → a small animated visual. The section ends on an EAI Healthcare lockup.
- The section's code is in `source/build/scene4_v7.py` (it is merged into `render7.py`).

### Changes in v6
- Simple animated text beside the screens replaces the boxed callouts.
- Subtitles are plain text with a soft shadow, with no box.
- Background: the grid lines and rings are removed and replaced with depth effects: soft out-of-focus light particles in three layers and floating glossy glass spheres. The icon circles have glossy 3D shading.
- The CDP, EDG and Application Knowledge Graph recordings are stitched into full-page images (`stitch.py`). The camera now moves strictly from top to bottom, with no back-scrolling.
- Zoom: none on the low-resolution screenshots, a gentler zoom (at most 1.22×) on the sharp ones, and a lighter dim, so text stays readable.
- EAI Healthcare: a rotating 3D holographic human body (`human3d.py`) with EHR, imaging, billing, pharmacy and lab nodes orbiting in depth.

### Changes in v5
- New narration script approved by management, with matching on-screen text:
  - Step One: AI-Ready (CDP, ECS, EDG), with a NEW AT EMPOWER tag on EDG.
  - Step Two: AI-Activated (Understand, Answer, Build, Act).
  - Move It Once. Access It Always.
  - Enterprise AI, Built for Industry (EAI Pharma, AI Healthcare Platform).
- A more natural voice-over:
  - Kokoro's top-rated voice (af_heart) at natural speed, generated one sentence at a time with real pauses and no time-squeezing.
  - Studio voice processing: EQ, de-essing, gentle compression and light room tone (`source/build/polish.py`).
- `output/voice_options_sample.m4a` has the same line in four voices, in order: af_heart (used), af_bella, am_fenrir, bm_george.

**Deliverable (v4):** `output/Solix_Empower_2026_AV_v4_1080p.mp4` is the master; `output/Solix_Empower_2026_AV_v4_preview.mp4` is a single-file preview under 30 MB. Both are 1920×1080, 30 fps, 2:55.

### Changes in v4: animated product screens
- Every product screenshot and recording plays inside a browser window that shows its solix.com product URL.
- Screenshots build up section by section: content blocks are detected automatically and revealed in sequence. EAI Healthcare uses a radial build; Data Sense and Agentic use a left-to-right build.
- The camera pushes in to key areas with a spotlight, a red outline, a label tag, a cursor glide and a click ripple, then pulls back out.
- Headline keywords land on a blue #0088cf highlight pill.
- The engine is `source/build/screens.py`; the renderer is `render4.py`.

### Changes in v3
- Event theme: deep indigo #30267b background, brand-blue #0088cf glows and kickers, red #ee2424 accents, a white Solix logo, and white product cards.
- Sharper screen recordings: extracted at full source resolution and scaled with Lanczos.
- Enterprise Content Services: the blurry screenshot is replaced by a crisp, natively rendered panel with an animated graphic.
- Analysts: a trimmed snippet from the end of the Analysts recording, then a crisp rebuild of the Analyst Recognitions section, with the two Bloor Research entries highlighted.
- The build is `source/build/render3.py`.

### Changes in v2
- No stock footage. The opening and every other scene use motion graphics; the only stock clip left is EAI Pharma.
- Product screens come from the new uploads: the CDP, EDG, Application Knowledge Graph and Analyst screen recordings, plus the new Active Archiving, Database, Email, Mainframe, File and EAI Healthcare screenshots.
- The archiving section is slower and grouped: (1) Application Retirement and Data Preservation, (2) SAP, Oracle and Mainframe, (3) Email, File, Database and Active Archiving, then the benefits.
- The narration opens with a welcome to the audience and closes with an invitation to connect.
- Branded diagonal sweep transitions with the Solix bolt, a drifting data-network background, and a slow zoom on every product card.
- The background music sits lower and ducks further under the voice.
- The build is `source/build/render2.py`, `vo2.py`, `music.py` (`TL=timeline2.json OUT=music2.wav`) and `mix2.py`.

## Style (matched to the EAI Healthcare reference video)
- Light white-to-blush/coral gradient background with a faint grid and soft rings.
- Small `SOLIX EMPOWER 2026` eyebrow label at top left and the Solix logo at top right.
- Red tracked kicker and a bold black InterDisplay headline on every scene.
- White rounded product cards with soft shadows, plus red numbered callouts and tabs.
- White caption pill at bottom center and a red progress line along the bottom edge.

## Scenes (following the script)
| # | Time | Scene |
|---|------|-------|
| 1 | 0:00 | Solix logo, 20+ years, data/AI montage |
| 2 | 0:13 | Enterprise Foundation (CDP, EDG, ECS) |
| 3 | 0:28 | Enterprise AI hub: Understand, Answer, Build, Activate, then Data Sense → Agentic |
| 4 | 0:47 | Data lifecycle & archiving (9 solutions), then the benefits |
| 5 | 1:06 | Industry: EAI Healthcare, EAI Pharma, Solix Academy |
| 6 | 1:27 | Trusted by global enterprises (logo wall + industries) |
| 7 | 1:45 | Recognized by Gartner, IDC, Forrester, Bloor Research |
| 8 | 2:00 | From data to intelligence / governance to action, then the Solix Empower 2026 lockup |

## Audio
- **Voice-over:** local neural TTS (Kokoro `am_michael`), one file per script line in `source/audio/vo_*.wav`.
  To use a different voice (for example Higgsfield "Fraser"), replace the `vo_*.wav` files and re-run `timeline.py` → `music.py` → `render.py video` → `mix.py` → mux. Scene timing follows the voice-over automatically.
- **Music:** an original, procedurally generated 124 BPM electronic event track (`source/audio/music.wav`), so it is royalty-free. It ducks under the voice.
