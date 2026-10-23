# 4K (3840x2160) RGB-alpha, whole video + voice-over

QuickTime Animation (RGB + alpha), 30 fps, 102.3 s, voice-over embedded. About 3 GB, so GitHub needs it as 32 byte-chunks (`parts/`).
Join them into ONE file: run `join_4k.sh` (Mac/Linux) or `join_4k.bat` (Windows, copy /b). No ffmpeg needed.
Result: `EAI_4K_RGBA_with_VO.mov`. `parts.sha256` lets you check the download. Separate voice-over: `../audio/EAI_final_VO_narration_synced.wav`.
