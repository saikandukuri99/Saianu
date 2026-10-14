# Solix EAI teaser: 1:30 (90 s), version 2

Changes from version 1:
1. The AI icon (chip) is now flat, with no 3D animation (problem scene and platform scene).
2. The Solix logo sits in the top-right corner for the whole video.
3. A longer narration gap before Data Sense: "Activate it. Four services. One framework." now holds on screen, the voice pauses (about 1.2 s), and Data Sense starts at about 22.6 s.
4. The XKG frame is flat, with no 3D animation.
Everything else is unchanged, and the voice-over was regenerated with the same voice and wording, so the video and voice are in sync.

| File | What |
|---|---|
| `EAI_90s_v2_VO_narration.wav` | The single voice-over, 90.0 s, 48 kHz stereo |
| `video_parts/EAI_90s_v2_RGBA_partNNof09__start_TC_*.mov` | The single 90 s video, RGB + alpha (QuickTime Animation, 1920x1080, 30 fps, 2700 frames) in 9 back-to-back pieces (GitHub rejects files over 100 MB). Lossless and frame-exact. |
| `join_parts.sh` / `join_parts.bat` + `list.txt` | Makes one file `EAI_90s_v2_RGBA_with_VO.mov` (video + voice-over together) with ffmpeg, no re-encoding |
| `EAI_90s_v2_subtitles.srt` | Optional captions |

## In Premiere Pro
1. New sequence 1920x1080, 30 fps. Voice-over on A1 at 00:00:00:00.
2. Video on V1 at 00:00:00:00: import the joined file, or drag the 9 pieces onto V1 in name order (they sit back-to-back, each start timecode is in its file name).
3. Alpha is straight; put your own background underneath. No music in the files.
