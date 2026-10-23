@echo off
cd /d "%~dp0"
(for %%f in (video_parts\*.mov) do @echo file '%%f') > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -i audio\EAI_final_VO_narration_synced.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le -t 102.33 EAI_final_RGBA_with_VO.mov
pause
