@echo off
rem Needs ffmpeg. Makes ONE file: Version A RGB-alpha video + voice-over.
cd /d "%~dp0"
(for %%f in (A_video_parts\*.mov) do @echo file '%%f') > list_A.txt
ffmpeg -y -f concat -safe 0 -i list_A.txt -i audio\EAI_108s_A_VO_narration.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s24le -t 108.5 EAI_108s_A_RGBA_with_VO.mov
echo Done: EAI_108s_A_RGBA_with_VO.mov
pause
