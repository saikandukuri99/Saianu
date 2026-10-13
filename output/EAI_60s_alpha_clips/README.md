# Solix Enterprise AI: 60-second teaser, separate alpha clips for Premiere Pro

Everything here is built from the storyboard in `EAI_Teaser_FINAL_1080p_silent.mp4` and the script in `Solix_EAI_Teaser_Audio_Prompts_v5.docx`. The script is tightened from ~75 s to **62.3 s** so it plays as a 60-second film.

## What is in the folder
| Folder | What | Format |
|---|---|---|
| `clips/` | **12 product-screen clips (S01 to S12)**, one per voice-over line, with real transparency (RGB + alpha). S02 is in two back-to-back pieces (file-size limit) | QuickTime Animation (RGB + alpha, lossless), 1920x1080, 30 fps |
| `captions/` | 12 matching on-screen caption clips (white text on a dark pill, transparent) | QuickTime Animation (RGB + alpha) |
| `3d_loops/` | 4 seamless 6-second 3D loops to drop anywhere: Solix coin, chip, XKG orb, data layers | ProRes 4444, 1080x1080 content centred in a 1920x1080 frame |
| `00_Assembled_Preview.mp4` | Everything laid out on the background with the voice-over and captions, so you can see the intended timing. Reference only. | H.264 |
| `audio/` | **One voice-over file for the whole video**, plus an SRT | WAV 48 kHz stereo (-16 LUFS) |
| `background/` | Optional dark network plate (not alpha). Use it, or put your own underneath | H.264 |
| `CUE_SHEET.md` | Which clip goes on which timecode, with the words spoken | |

No background music anywhere. Add your own bed.

## Putting it together in Premiere
1. New sequence 1920x1080, 30 fps. Drop `EAI_60s_VO_narration.wav` on A1 at 0:00.
2. Drop each `clips/Sxx_*.mov` on V1/V2 at the timecode in its file name (`start_TC_00-00-03-03` = 00:00:03:03). They then sit on the right words. Overlap them for dissolves if you like.
3. Optional: captions on V3 at the same start timecodes, or import the SRT for native Premiere captions.
4. Alpha is **straight**; Premiere reads it automatically. Put your own background or footage underneath.

## Brand and look
- Solix colours: **#0088cf** (highlights, active states), **#ee2424** (problem states, brand red), **#30267b** (depth, gradients). White type, Inter.
- The Solix bolt is the official `icon.png` from `source/assets`. The coin is that artwork on a 3D disc.
- Kept restrained for senior audiences: no robots, brains, glowing neural-net imagery or "AI magic" visuals. "AI" only appears as a plain label (chip, text), as in the storyboard. 3D is used on six moments only.

## Voice-over
Narration is generated with an offline neural text-to-speech voice (Kokoro, "am_michael", calm male, neutral English), lightly compressed and levelled. It is a good working track. For the final film, if you want a studio-grade or cloned brand voice, send the text in `CUE_SHEET.md` to your usual voice tool and keep the same sentence order: the clips are timed to the sentence gaps, so a replacement read at a similar pace will still line up (small timing nudges in Premiere are fine).

## Rebuild / change a scene
Sources are in `source/eai60_build/` (HTML scenes + render script). Edit text or timing in a scene file and re-render that one clip.
