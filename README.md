# Solix Empower 2026 – AV ("The Agentic Enterprise")

**Current: 90-second cut, delivered as separate parts for Premiere Pro.** Everything is in `output/90s_cut_parts/`:
- `02_Foundation`, `03_Enterprise_AI`, `04_Data_Lifecycle`, `05a`–`05e` (EAI Pharma / Healthcare / Academy, approved), `06_Customers_Recognition`, `07_Close`. Each part comes as:
  - `.mp4`: 1080p video with the voice-over only, no subtitles burned in;
  - `_VO.wav`: the voice-over alone, 48 kHz 24-bit;
  - `.srt`: subtitles.
- `Music_Bed_full_sequence.wav`: the music bed for the whole sequence, in the order above.
- `00_Assembled_Reference_cut.mp4`: all parts assembled with music, for reference (2:14).
- `CUE_SHEET.md`: which screen or recording plays on which narration line, with clip timecodes.
- Screens are plain browser windows with a gentle push-in: no red highlight boxes, cursor or labels. There are no transition sweeps or progress bar, so transitions are done in Premiere.

**Current (v11):** `output/Solix_Empower_2026_AV_v11_1080p.mp4` is the 1080p master (3:18); `output/Solix_Empower_2026_AV_v11_preview.mp4` is a single-file preview. A 4K version follows once v11 is approved.

### Changes in v11
- The 3D AI-journey wheel now has narration: "Your AI journey starts here: AI-ready data with Solix CDP, AI-ready people with Solix Academy, and an AI-ready enterprise with Solix EAI." Each segment animates in as it is spoken.

### Changes in v10
- Narration: "a trusted data foundation and collaborative intelligence together, for actionable outcomes". On screen: "Collaborative Intelligence".
- Pillar 6 (Purpose-Built Healthcare Models) is now spoken and highlighted, with the subtext "Specialty-specific multi-agentic intelligence".
- Solix Academy: after the learning path, a 3D extruded wheel animates in (`wheel3d.py`): AI-Ready Data / Solix CDP, AI-Ready People / Solix Academy, AI-Ready Enterprise / Solix EAI, around "Your AI Journey Starts Here".

### Changes in v9
- The narration now says "actionable outcomes" and "Patient three sixty".
- The 6-pillar subtexts are shown in full (wrapped, never cut off). Pillar 6 reads "Specialty multi-agentic intelligence".

### Changes in v8 (healthcare section)
- Under EAI HEALTHCARE: "Accelerated Care by empowering clinicians for intelligent outcomes." and "Care Creates Data | Data Accelerates Cure".
- The third foundation step now reads "Actionable Outcomes".
- The 6-pillar diagram has three pillars on the left, three on the right and the Solix sphere in the centre, with no camera movement; labels are fitted inside the frame.
- Capability order: AI-Powered Documentation → AI Clinical Assistant → Preventive Care → Revenue Cycle Intelligence, with the narration re-recorded in the same order.
- The EAI Healthcare end screen is removed. Solix Academy is added (narration and an animated learning path: Data → Governance → Enterprise AI → Agentic, "Build the skills for an AI-ready enterprise").

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

---

## EAI Booth Loop: white edition (silent, seamless)

`output/EAI_Booth_Loop_White/Solix_EAI_Booth_Loop_White_1080p.mp4`: 1920×1080, 30 fps, 1:30, H.264, **no audio**. The last frame flows straight into the first, so it can play on repeat at the booth.

- **Look:** a white background with a slowly drifting tech network (nodes and links in #0088cf and #ee2424, with data pulses moving along the links). Headlines are #30267b, the key phrase in each is #0088cf with a #ee2424 underline that sweeps in, and the kickers are #0088cf letter-spaced caps after a red dash.
- **Flow (follows the storyboard):** Solix logo build → "Enterprise AI for real business impact." + product chips → Data Sense → Curation → Data Ask → XKG (PREVIEW) → AI Warehouse → Agentic (ANNOUNCED) → Open by design (5 cards) → clean network, which loops back to the start.
- **Motion:** the logo icon spins and pops in and the wordmark wipes in, then the logo flies to the corner. Headline words rise from behind a mask, one after another, and body lines fade up. Product screens play in a floating browser card (with the solix.com URL) that slides in, pushes in slowly and floats gently. Between scenes there's an angled blue and red wipe with a light sweep. The bottom nav shows the active product, with a blue→red progress bar. The "Live demo at this stand" pill pulses.
- The product screens are re-used from the v4 booth loop (cropped so the clideo watermark is gone).
- The build is `source/build/booth_loop.py` (skia-python + ffmpeg): `python3 booth_loop.py <v4_loop.mp4> out.mp4 [--frames a:b]`.

### v6 (corrected on-screen text)
`output/EAI_Booth_Loop_White_v6/Solix_EAI_Booth_Loop_White_v6_1080p.mp4` uses the same format as above, updated to `EAI_Booth_Loop_Onscreen_Text_v6.txt` (copied into the same folder):
- XKG headline: "One meaning across every application." The XKG line is unchanged: "Each application answers through its own AKG. XKG combines results using certified business meaning."
- Opening products: Data Sense · Data Ask · AI Warehouse · Agentic. The bottom navigation still lists all five sections.

---

## XKG Booth Loop: white edition (silent, seamless)

`output/XKG_Booth_Loop_White/Solix_XKG_Booth_Loop_White_1080p.mp4`: 1920×1080, 30 fps, 1:30, H.264, **no audio**, plays on repeat without a visible jump. It has the same look as the EAI white edition and follows `XKG_Booth_Loop_Onscreen_Text.txt` (copied into the same folder).

- **Product screens** play in the floating browser card, without the clideo watermark: the AI Assistant question, golden records with steward review, certified terms with the Edit/binding flow, and the governed answer ($875,500).
- **Rebuilt natively in white:** the diagram scenes. These are "Why it fails" (three app cards, ≠ markers, three failure chips), "Introducing Solix XKG" (the semantic-layer hub feeding three apps, each "Governed by its AKG", no PREVIEW tag), and "How it works" (a 3-step stepper, the golden record, the certified term, contributions counting up to the governed result of $875,500). Also "One layer, many questions" (Suppliers / Customers / Materials, plus the three pills), "What it unlocks" (4 tiles) and the end card: Solix icon + "Solix XKG" (tagline, "Ask us for a live demo", "A Solix Data Sense capability · Governed by Solix EDG").
- **Bottom nav:** The question · Why it fails · Solix XKG · In the product · What it unlocks.
- The build is `source/build/xkg_loop.py`, which reuses `booth_loop.py`: `python3 xkg_loop.py <xkg_loop.mp4> out.mp4 [--frames a:b]`.
