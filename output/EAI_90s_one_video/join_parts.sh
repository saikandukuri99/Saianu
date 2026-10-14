#!/bin/sh
cd "$(dirname "$0")"
ffmpeg -y -f concat -safe 0 -i list.txt -c copy EAI_90s_RGBA_alpha.mov && echo done
