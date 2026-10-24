# Solix Empower 2026 – 90-second version (no headings)

* **Parts total: 97.7 s**, plus your own Scene 1 in front.
* **EAI Healthcare uses the full original voice-over and visuals** (same as the long version, normal speed):
  `05b_EAI_Healthcare_Foundation`, `05c_EAI_Healthcare_Platform` and `05c2_EAI_Healthcare_Capabilities`, with the capabilities line and its four graphics back in.
* All main section headings are removed so you can add your own in Premiere. The `07b_End_Lockup` clip holds the end title; drop it if you're building your own.
* `CUE_SHEET.md` lists every narration line, its time inside each clip, and what is on screen.

## Version 1 – `plain/` (H.264 .mp4, with VO + music)
Plain gradient background. No bubbles, particles or glass orbs.

## Version 2 – `alpha/` (QuickTime Animation .mov, RGB + Alpha, silent)
Transparent background, so you can put your own background underneath in Premiere.
Import, then Modify ▸ Interpret Footage ▸ Alpha Channel: *Straight* (usually automatic).
GitHub caps files at 100 MB, so two parts are split into back-to-back pieces (exact frames, lossless). Put them one after another on the timeline:
* `02_Foundation_piece1…4.mov` (4 × 107 frames)
* `03_Enterprise_AI_piece1…2.mov`

## `audio/`
* `<part>_VO.wav`: voice-over for each part (48 kHz / 24-bit), aligned to clip start.
* `<part>.srt`: subtitles for each part.
* `VO_full_sequence.wav` and `Music_Bed_full_sequence.wav`: the full sequence (parts placed back-to-back).

`00_Assembled_Reference.mp4`: every plain part joined with the VO and music, for timing reference.
