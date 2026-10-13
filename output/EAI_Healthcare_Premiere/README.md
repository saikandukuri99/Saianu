# EAI Healthcare – RGB+Alpha clips for Premiere Pro

Total timeline: **78.8 s @ 30 fps, 1920×1080** (same as the finalized video).
Put the clips one after another starting at 00:00:00:00 and they rebuild the
original timing exactly; the VO, music and subtitles line up with them from 0.

## `alpha/` – QuickTime Animation (.mov), RGB + Alpha, no audio
Background removed, so you can put your own background underneath.
Premiere usually detects the alpha automatically; if not:
right-click ▸ Modify ▸ Interpret Footage ▸ Alpha Channel: *Straight*.

GitHub caps files at 100 MB, so busy scenes are split into `_piece1`, `_piece2`, …
Place the pieces back to back (exact frames, no gaps, lossless).

| # | Clip | Starts at (mm:ss:ff) | Length | File(s) |
|---|---|---|---|---|
| 01 | Intro EAI Healthcare Platform | 00:00:00 | 3.57 s (107 fr) | `01_Intro_EAI_Healthcare_Platform.mov` |
| 02 | Fragmented Data to Outcomes | 00:03:17 | 7.00 s (210 fr) | `02_Fragmented_Data_to_Outcomes_piece1.mov`<br>`02_Fragmented_Data_to_Outcomes_piece2.mov` |
| 03 | AI Ready Unified Governance | 00:10:17 | 9.00 s (270 fr) | `03_AI_Ready_Unified_Governance_piece1.mov`<br>`03_AI_Ready_Unified_Governance_piece2.mov` |
| 04 | Six Pillars | 00:19:17 | 14.77 s (443 fr) | `04_Six_Pillars.mov` |
| 05 | AI Patient 360 Title | 00:34:10 | 2.50 s (75 fr) | `05_AI_Patient_360_Title.mov` |
| 06 | Multi Agentic Every Specialty | 00:36:25 | 14.23 s (427 fr) | `06_Multi_Agentic_Every_Specialty_piece1.mov`<br>`06_Multi_Agentic_Every_Specialty_piece2.mov`<br>`06_Multi_Agentic_Every_Specialty_piece3.mov` |
| 07 | Findings with Evidence | 00:51:02 | 8.63 s (259 fr) | `07_Findings_with_Evidence_piece1.mov`<br>`07_Findings_with_Evidence_piece2.mov` |
| 08 | Clinician Validation | 00:59:21 | 8.00 s (240 fr) | `08_Clinician_Validation_piece1.mov`<br>`08_Clinician_Validation_piece2.mov` |
| 09 | Built for Global Healthcare | 01:07:21 | 6.90 s (207 fr) | `09_Built_for_Global_Healthcare_piece1.mov`<br>`09_Built_for_Global_Healthcare_piece2.mov`<br>`09_Built_for_Global_Healthcare_piece3.mov` |
| 10 | End EAI Healthcare Platform | 01:14:18 | 4.20 s (126 fr) | `10_End_EAI_Healthcare_Platform.mov` |

## Changes in this version (visuals otherwise untouched)
* **Unified Governance:** the Revenue Cycle Intelligence icon is now a
  rising-graph icon instead of the rupee sign.
* **Six Pillars:** the diagram is replaced with the supplied six-pillar artwork,
  with points 4 and 5 swapped: **AI Clinical Intelligence** now sits upper-right
  (4th) and **Intelligent Imaging & Radiology** middle-right (5th). It animates
  like before (logo, then pillars one by one, then each pillar highlights red as
  the voice names it).

## `audio/` – 48 kHz / 24-bit WAV, full timeline (start at 0)
* `VO_Female_full.wav` – the female voice-over (same as the last version).
* `BGM_HyperBeat_full.wav` – the hyper-beat music, already dipped under the voice.
* `Mix_VO_BGM_full.wav` – both together, as in the last delivered video.

## `subtitles/`
* `EAI_Healthcare_full.srt` – whole timeline.
* `<clip>.srt` – per clip, times relative to the clip start.

## `reference/`
* `EAI_Healthcare_alpha_reference.mp4` – all clips over the original background
  with the mix, for checking timing.
