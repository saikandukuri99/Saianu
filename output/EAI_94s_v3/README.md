# Solix EAI teaser v3: 94 s, RGB alpha (Data Sense: structured + unstructured)

Built from "Storyboard and Narration v3", the new 4 s Content Library frame and the draft full video. The visuals of all earlier scenes (flat AI chip, flat XKG, Solix logo top-right, 3D AI Warehouse stack) are kept as in the 90 s v2.

## What changed
| Scene (v3 time) | Status | What I did |
|---|---|---|
| 1 Hook (0:00 to 0:03.5) | no change | unchanged |
| 2 Problem (0:03.5 to 0:12) | **CHANGED** | 4th chip "No semantic layer"; row of three document tiles under the table cards (Contract_v7.pdf, Re: Supplier dispute, Scan_0042.pdf) with red "?" badges and the label "Unstructured, just as hard to use" |
| 3 "makes your data AI-activated" (0:12 to 0:15.6) | **CHANGED** | row "And your documents": Contract 2214, Policy document, Email thread, each with a blue "tagged" dot |
| 4 Overview (0:15.8 to 0:22.3) | **CHANGED** | subline "Makes structured and unstructured data AI-activated."; chips tagged Structured / Unstructured; Data Ask card "Grounded in Data Sense. Always cited." |
| 5 Data Sense · AKG (0:22.5 to 0:31.6) | **CHANGED** (picture + voice) | title "DATA SENSE · AKG", new subline, "STRUCTURED DATA" label |
| 6 Data Sense · Content Library (0:31.65 to 0:35.65) | **NEW** | cloud storage / file shares / email archives send documents into the semantic content library; meaning tags pop in; caption "Wherever it lives in your data estate" |
| 7 Data Sense · XKG (0:35.65 to 0:43.7) | **CHANGED** (picture + voice), moved +4 s | caption "One shared meaning across structured and unstructured data." |
| 8 Data Ask (0:43.9 to 0:53.7) | **CHANGED**, moved +4 s | Unstructured tile subline "From the content library" |
| 9 AI Warehouse, 10 Agentic, 11 Platform, 12 Close | moved +4 s only | unchanged |

Narration: only L06, L06b (new) and L07 are re-recorded (same voice and tone). Every other line is the same read as in v2, 4.0 s later. 94.0 s in total.

## Files
| Folder / file | What |
|---|---|
| `audio/EAI_94s_v3_VO_narration.wav` | The single voice-over, 94.0 s, 48 kHz stereo |
| `audio/rerecorded_lines/` | The three changed lines on their own (L06, L06b, L07), named with their start time |
| `audio/EAI_94s_v3_subtitles.srt` | Optional captions |
| `video_parts/` | The full 94 s video, RGB + alpha (QuickTime Animation, 1920x1080, 30 fps, 2820 frames) in 11 back-to-back pieces (GitHub rejects files over 100 MB). Lossless, frame-exact. |
| `changed_scene_clips/` | Separate RGB-alpha clips for every scene that changed or is new (scenes 2, 3, 4, 5 (two halves), 6 NEW, 7, 8). Start timecode is in each name. Scenes 9 to 12 only moved +4 s and are in the full video. |
| `join_parts.sh` / `join_parts.bat` + `list.txt` | One command that makes a single file `EAI_94s_v3_RGBA_with_VO.mov` (video + voice-over), needs ffmpeg |

## In Premiere Pro
1. Sequence 1920x1080, 30 fps. Voice-over on A1 at 00:00:00:00.
2. Either put the 11 video pieces on V1 from 00:00:00:00 in name order (they sit back-to-back), or import the joined file. Or place the individual `changed_scene_clips/` at their start timecodes over your earlier clips (everything after 0:31.65 moves 4 s later). Alpha is straight, no music is included.

## Open items from the storyboard (not changed here)
- Content Intelligence and Intelligent Classification are tagged "Unstructured" on the overview card (best guess, as in the storyboard).
- The closing headline still reads "AI your business can trust" and "Four services. One framework." is still on screen at the overview, while the narration moved away from both.
- The hold on "Four services. One framework." now lasts through the pause before Data Sense.
