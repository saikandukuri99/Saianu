# Solix Enterprise AI teaser, Version A, tightened and synced (101.4 s)

The voice-over had long empty gaps (28.8 s of silence in total, up to 2 s between lines) because every line was held at its script start time. This version removes them: the voice-over is re-read at one natural pace with short, even pauses (0.4 s between sentences, 0.75 s between sections), and the picture is re-timed to follow the new voice. Every on-screen item still appears on its own line. Length: 101.4 s (3041 frames at 30 fps) instead of 108.5 s.

## Files
| File | What |
|---|---|
| `EAI_108s_A_RGBA_with_VO.mov` | **ONE file: the entire video, RGB with straight alpha, voice-over included** (QuickTime Animation video + 48 kHz stereo PCM audio). 1920x1080, 30 fps. About 750 MB. GitHub rejects files over 100 MB and its large-file service is blocked in this session, so this file is delivered through the Claude app file card, not through GitHub; the GitHub folder has the .webm (same picture and voice-over, 13 MB). Solix logo top-right is included; no background, no captions, no music. |
| `EAI_108s_A_RGBA_with_VO.webm` | The same single file as VP9 with alpha + Opus audio, only 13 MB. Opens directly in browsers and in editors that read WebM alpha; quality is close to the .mov (about 38 to 44 dB PSNR). |
| `audio/EAI_108s_A_VO_narration_synced.wav` | The single voice-over file on its own (same audio as in the .mov), 101.4 s. |
| `audio/EAI_108s_A_subtitles_synced.srt` | Subtitles timed to the new voice-over. |
| `captions/EAI_108s_A_captions_RGBA.mov` | Caption bar as a separate RGB-alpha layer, timed to the new voice-over. |
| `previews/EAI_108s_A_tight_preview_with_VO.mp4` | Ready-to-watch preview with animated background, captions and voice-over. |

Use the .mov (or .webm) and its own audio together; do not add the old voice-over from `EAI_108s_v4`, it has the old timing.
