# Solix Enterprise AI – Teaser (Storyline A, 4K)

**v10 (final):** the Solix logo (bolt with SOLIX) sits beside "Solix Enterprise AI" on the "Open by design" platform card, centred. Everything else is as in v9.

**v9:** fixes a voice-over glitch at about 1:32, where part of "and" played twice. Where one recorded phrase is split into two script lines, the clips now meet in the middle of the pause instead of overlapping (`el_split.py`). The corrected clips are placed at the same cue times (`vo_place.py`), so the picture is identical to v8 and only the soundtrack changed.

**v8:** the voice-over is the supplied ElevenLabs recording ("Hale"). It is cut into the 37 script lines (`el_split.py`, split at its natural pauses) and placed on the storyboard cues, so every animation stays in sync. The runtime is 2:12. The background music is the supplied track. The "Open by design" platform card now shows only "Solix Enterprise AI", centred. Four 4K files: dark and white, each with and without captions.

**v7 (`*_BGM.mp4`):** the same four v6 videos with the supplied background music ("Top Flow – Ambient Corporation, loop 01 intro") replacing the generated score. The 16.6-second loop is repeated with crossfaded seams, faded in at the top and out over the end card (`bgm_bed.py`), and ducked under the voice-over at -16 LUFS (`mix_bgm.sh`). The picture is unchanged (stream copy). The v6 files with the original score are kept for comparison.

**v6:** same as v5, plus:
- "Agentic" is pronounced ay-JEN-tik in the two Agentic lines (forced phonemes in `vo.py`).
- The client's AI artwork replaces the sparkle at the centre of the Agentic loop. On the white background it sits in a dark medallion.
- The "AI" chip cropped from that artwork replaces the icon above the problem screen.

**v5:** four 4K files, dark and white backgrounds, each with and without captions. Changes:
- XKG scene rewritten per the change-request guide: "CROSS-APPLICATION INTELLIGENCE / One governed answer / Across your enterprise applications". The strip reads "Each application answers through its own governed knowledge graph", the cards read "Governed application answer", and the VO says "One governed answer across all your enterprise applications." No migration or no-copy wording remains.
- Editor's on-screen text: "But is your data AI-ready?", "Ask questions. Get answers.", "Build your own AI applications.", "Describe. Build. Run." (no separate "Run it.").
- An AI chip icon replaces the sparkle on the problem screen.
- The Solix bolt never appears without the SOLIX name: logos reveal as one piece, and the platform card shows SOLIX under the bolt.
- A different female voice (Kokoro `af_bella`), so this video sounds distinct from the other Solix videos.
- White-background variant (`LIGHT=1 node render.mjs ...`, `web/theme.js`).

**v4:** the opening AI hub now uses the client-supplied artwork (robot, network and database around an AI chip; cut out to transparent by `cutout.py` into `web/assets/ai_hub.png`). It comes in two versions, with and without captions (`NOCAP=1 node render.mjs ...`).

**v3:** same as v2, but with no scene transitions: each scene cuts straight to the next, with no crossfade, blur/zoom or light sweep.

**v2:** follows the final Flow script, which opens with "AI is transforming how enterprises run and grow." The background is more corporate: deep navy-to-indigo gradient, fine faint grid, slow blue and red light ribbons, and a sparser low-opacity AI network. The animation is otherwise the same as v1.

**Deliverables in `output/EAI_Teaser_4K/`** (3840×2160, 30 fps, H.264 High with AAC stereo):
- `Solix_Enterprise_AI_Teaser_v10_4K_dark_with_captions.mp4` / `..._dark_no_captions.mp4`
- `Solix_Enterprise_AI_Teaser_v10_4K_white_with_captions.mp4` / `..._white_no_captions.mp4`
- `Solix_EAI_Teaser_captions.srt` and `Solix_EAI_Teaser_VO.wav`

**How it is built** (`source/eai_teaser/`):
- **Structure:** a 6-second title opening ("Solix Enterprise AI"), then the 37-line narration following the Variant A storyboard (Hub → Problem → AI-Activated Data → Data Sense → Cross-application knowledge graph → Data Ask → AI Warehouse → Agentic → Open by design → end card).
- **Voice:** female neural TTS (Kokoro `af_bella` from v5; earlier versions used `af_heart`), one line at a time, with the studio polish chain (`polish.py`). `vo_track.py` places each line at its storyboard cue, adding a natural pause where a line runs long.
- **Visuals:** a keyframed motion-graphics composition in HTML/JS (`web/`). The background is the Solix palette (#30267b indigo, #0088cf blue and #ee2424 red glows) with a low-opacity animated AI network of red and blue nodes and pulses.
- **Rendering:** `render.mjs` renders every frame in headless Chromium at device scale 2 (3840×2160).
- **Music:** `music.py` is an original procedural score, so it is royalty-free. `mix.sh` ducks the music under the voice and masters to -16 LUFS.
- **Rebuild steps:** `python3 vo.py af_heart 1.0 <raw>` → `polish.py <raw> <pol>` → `vo_track.py <pol> vo_track.wav` → `music.py music.wav` → `mix.sh <dir>` → `node render.mjs frames <dir> 2 30 <w> 4` → ffmpeg.

---

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
