# Solix EAI teaser: 1:30 (90 s), one voice-over + one continuous RGB-alpha video

Same content and visuals as before, stretched to 90 seconds with a new, more natural female voice-over.

| File | What |
|---|---|
| `EAI_90s_VO_narration.wav` | The single voice-over, 90.0 s, 48 kHz stereo. Female, natural read (full sentences, no pitch tricks), based on the revised narration guide. |
| `video_parts/EAI_90s_RGBA_partNNofNN__start_TC_*.mov` | The single 90 s video, RGB + alpha (QuickTime Animation, 1920x1080, 30 fps, 2700 frames), delivered in 14 back-to-back pieces because GitHub rejects files over 100 MB. Lossless and frame-exact. |
| `join_parts.sh` / `join_parts.bat` | **Double-click / one command to make the single file `EAI_90s_RGBA_with_VO.mov`**: the 90 s RGB-alpha video and the voice-over together in one file (about 940 MB, needs ffmpeg). Takes under a minute, no re-encoding. |
| `EAI_90s_subtitles.srt` | Optional captions for the voice-over. |

## In Premiere Pro
1. New sequence 1920x1080, 30 fps. Put `EAI_90s_VO_narration.wav` on A1 at 00:00:00:00.
2. Put the video on V1 at 00:00:00:00. Either:
   - import the joined `EAI_90s_RGBA_with_VO.mov` (one clip with video + voice-over; just drop it on a sequence), or
   - select the 14 parts in name order and drag them onto V1; they sit back-to-back with no gaps (each part's start timecode is in its file name).
3. Alpha is straight; put your own background underneath. No music in the files.

## Joining the parts yourself
Mac/Linux: `./join_parts.sh`   Windows: `join_parts.bat`

Why parts: GitHub rejects any file over 100 MB (and refused large-file storage for this repo), and one 90 s lossless alpha video is about 900 MB. The joined file is bit-for-bit the same frames.
