#!/bin/bash
# 4K (3840x2160) master: Lanczos upscale of the 1080p render with light sharpening, HEVC, sized to stay under 95 MB.
set -e
B=$(cd "$(dirname "$0")" && pwd)
OUT="$B/../../output/Solix_Application_Retirement_4K.mp4"
ffmpeg -nostdin -v error -y -i "$B/ar_video.mp4" -i "$B/mix_norm.wav" -map 0:v -map 1:a \
  -vf "scale=3840:2160:flags=lanczos,unsharp=5:5:0.45:5:5:0" \
  -c:v libx265 -preset medium -b:v 10200k -maxrate 13000k -bufsize 20000k -pix_fmt yuv420p -tag:v hvc1 \
  -x265-params log-level=error -c:a aac -b:a 192k -movflags +faststart "$OUT"
ls -la "$OUT"
