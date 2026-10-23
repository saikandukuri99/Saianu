#!/bin/sh
# Joins the parts into ONE file: EAI_4K_RGBA_with_VO.mov (3840x2160, RGB+alpha, voice-over embedded). No ffmpeg needed.
cd "$(dirname "$0")"
cat parts/EAI_4K_RGBA_with_VO.mov.part* > EAI_4K_RGBA_with_VO.mov && echo "Done: EAI_4K_RGBA_with_VO.mov"
