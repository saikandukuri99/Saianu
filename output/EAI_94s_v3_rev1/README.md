# Solix EAI teaser v3, revision 1 (94 s, RGB alpha)

Same video, same timing, same length (94.0 s, 2820 frames, 30 fps). Only the four changes below were made; every other frame is bit-identical to `EAI_94s_v3`.

## The four changes
| # | Where (v3 time) | Change |
|---|---|---|
| 1 | Services overview, 0:21.5 to 0:22.9 (frames 646 to 675) | Removed the thin red bracket line and the text "FOUR SERVICES. ONE FRAMEWORK." The four service cards are untouched. |
| 2 | Data Sense AKG, pills visible 0:28.8 to 0:31.6 (frames 863 to 948) | The pills "Procure-to-Pay / Plan-to-Produce / Order-to-Cash / Record-to-Report" moved up from y=900 to y=866, so they sit just under the AKG panel (which ends at y=850) and clear of the two-line caption bar (starts at y=930). Nothing else in the scene changed. |
| 3 | End card, 0:91.0 to 0:94.0 (frames 2730 to 2820) | Caption bar copy "Put AI in the hands of your business." removed (subtitle cue 30 and the caption layer `cap12`). The line under the SOLIX Enterprise AI logo stays. The caption bar was never inside the video file; it only exists as subtitle/caption layer, so the video frames of this scene are unchanged. |
| 4 | Data Ask, 0:50.7 to 0:54.0 | (a) Voice-over line "It never guesses." (0:52.5 to 0:53.67) silenced; the gap is left in place so the cut into AI Warehouse stays at 0:54.0. (b) Its caption removed (subtitle cue 17 and the caption layer `cap07`). (c) The red pill "Asks if unsure" now reads "Human in the loop" (same icon and style, visible from about 0:50.7 to the end of the scene). "Sources cited" and the caption "If unsure, it asks." are unchanged. |

## What is in this folder
| File / folder | What |
|---|---|
| `video_parts/` | Full 94 s RGB-alpha video in 11 back-to-back pieces (QuickTime Animation, 1920x1080, 30 fps). **Changed pieces: 03, 05, 06, 08.** The other seven are copies of the v3 pieces. |
| `changed_scene_clips/` | Single-scene RGB-alpha clips (no logo). **Changed: S04, S05 part 1 and 2, S08.** S02, S03, S06, S07 are unchanged copies. |
| `audio/EAI_94s_v3_rev1_VO_narration.wav` | Voice-over, 94.0 s, 48 kHz stereo. Identical to v3 except 0:52.35 to 0:53.85, which is now silent. |
| `audio/EAI_94s_v3_rev1_subtitles.srt` | Subtitles with the two removed cues (28 cues left). |
| `join_parts.sh` / `join_parts.bat` + `list.txt` | One command that joins the pieces plus the voice-over into `EAI_94s_v3_rev1_RGBA_with_VO.mov` (needs ffmpeg). |

Source changes are in `source/eai60_build/scenes/` (`s04.html`, `s05.html`, `s07.html`, `cap07.html`, `cap12.html`).

## Frame check against v3
Frames 0 to 645, 676 to 862, 949 to 1517 and 1618 to 2819 are identical. Inside the changed ranges only the edited elements and their soft drop shadows differ.
