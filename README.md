# Solix Empower 2026 – AV ("The Agentic Enterprise")

**Current (v5):** `output/Solix_Empower_2026_AV_v5_1080p.mp4` is the 1080p master (2:47); `output/Solix_Empower_2026_AV_v5_preview.mp4` is a single-file preview. A 4K version follows once v5 is approved.

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
