# Solix Enterprise AI teaser, 108.5 s (Storyline A main, Storyline B intro)

New teaser built from "EAI Teaser - Storyline A narration script" (main) and "Storyline B" (only the first 10 s differ). 1920x1080, 30 fps, RGB with straight alpha (QuickTime Animation). No background and no music are baked in.

## What you get
| Folder | What |
|---|---|
| `A_video_parts/` | **Version A, the full 108.5 s video** (3255 frames), 14 back-to-back pieces (GitHub rejects files over 100 MB). Scenes + Solix logo top-right. Place them on V1 in name order from 00:00:00:00. |
| `A_scene_clips/` | The same video as separate scene clips (S01 to S11, S05 in two halves). Start timecode is in each name. No logo in these. |
| `B_intro/` | **Version B**, only the part that is different (0:00 to 0:10.3). `video_parts/` = the finished intro (2 pieces, with logo), `clips/` = its two scenes. From 0:10.3 Version B is identical to Version A, so use A from that point. |
| `captions/` | Caption bar as its own RGB-alpha layer for A and B (cues timed to the voice-over), so you can switch it off. |
| `audio/` | Voice-over for A (108.5 s), for B (108.5 s) and the B intro on its own (0:00 to 0:10.3), plus SRT subtitles for both. 48 kHz stereo, about -16 LUFS. |
| `logo/` | The top-right Solix mark as an RGBA still. In A it fades in at 0:05.4 and out at 0:102.9, in B from 0:00.15. |
| `previews/` | Ready-to-watch MP4s (with animated background, captions and voice-over) for A and B, and the background on its own. For review only. |

## Starting heading
The video opens with a title card in the same style as the Application Retirement video: Solix logo, "OVERVIEW", **Enterprise AI**, and UNDERSTAND · ASK · BUILD · ACTIVATE (A, 0:00 to 0:05.5). Version B starts with "Overview / Enterprise AI" as a heading over the question-and-answer screen.

## Scenes (Version A, times from the script)
| Time | Scene |
|---|---|
| 0:00 | Title card (starting heading) |
| 0:05.5 | "Your AI is only as ready as your enterprise data is" |
| 0:10.3 | Problem: cryptic tables, systems that don't talk, unindexed documents, "So your AI can't use it" |
| 0:19.8 | Solix Enterprise AI gets your data ready for AI; Understand, Ask, Build, Put to work |
| 0:29.3 | Data Sense: structured and unstructured, drafted meaning reviewed by experts, ready-made knowledge graphs in minutes, content library |
| 0:44.8 | What sets Solix apart: one knowledge graph, one record you can trust, one shared meaning, no migration |
| 0:59.8 | Data Ask: plain language, structured and unstructured, grounded in business context, every answer cited |
| 1:10.8 | AI Warehouse: the people who know your business describe the app, built on governed, version-tracked data |
| 1:21.3 | Agentic: describe the work, AI builds, tests and runs it, less manual work |
| 1:31.8 | Works with what you already have: any LLM, any application, any data platform |
| 1:43.4 | Close: Solix Enterprise AI. Put AI in the hands of your business. |

Version B first 10 s: "Your teams are asking AI real business questions." (a question typed to the AI), "But it can't give a complete answer." (a partial answer marked incomplete), then the same "ready" screen as A.

## Voice
The Application Retirement video's voice is not one of the voices available in this build and cannot be cloned here, so I picked the closest match by pitch and tone (female, about 190 Hz median, similar warmth). It is a text-to-speech voice, so it will sound similar to the Application Retirement video but not identical. If you can tell me which tool made that voice (or send the voice-only audio and its script), I can match it more closely.
Each narration cue starts at its script time. One steady pace (about 1.1x) is used for all lines; a few long cues are slightly faster and a few start up to 0.5 s after their script time so they do not overlap the previous line.

## In Premiere Pro
Sequence 1920x1080, 30 fps. Voice-over on A1 at 00:00:00:00. A video pieces on V1 in order (or the scene clips at their start timecodes), captions on V2, your background underneath. Alpha is straight.
`join_parts.sh` / `join_parts.bat` (needs ffmpeg) joins the A pieces and the voice-over into one file `EAI_108s_A_RGBA_with_VO.mov`.
