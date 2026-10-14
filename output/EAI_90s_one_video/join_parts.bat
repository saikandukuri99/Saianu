@echo off
rem Needs ffmpeg. Makes ONE file with the RGB-alpha video + the voice-over together.
cd /d "%~dp0"
ffmpeg -y -f concat -safe 0 -i list.txt -i EAI_90s_VO_narration.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s24le -t 90 EAI_90s_RGBA_with_VO.mov
echo Done: EAI_90s_RGBA_with_VO.mov
pause
