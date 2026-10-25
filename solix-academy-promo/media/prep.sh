#!/bin/sh
# Extract the frames the film draws from the uploaded clips (frames are generated, not committed).
#   sh media/prep.sh      (run from the project folder)
set -e
cd "$(dirname "$0")"
for n in data people governance; do
  rm -rf "av_$n" && mkdir "av_$n"
  ffmpeg -nostdin -v error -y -i "avatar_$n.mp4" -vf "scale=1280:720:flags=lanczos" -q:v 3 "av_$n/%04d.jpg"
  # each avatar's own voice, loudness-matched to the narration
  ffmpeg -nostdin -v error -y -i "avatar_$n.mp4" -vn -af "highpass=f=70,loudnorm=I=-19:TP=-2:LRA=7,aresample=48000" "avatar_$n.wav"
done
rm -rf rec && mkdir rec
ffmpeg -nostdin -v error -y -i experts_wall.mp4 -q:v 3 "rec/%04d.jpg"
ls av_data | wc -l; ls av_people | wc -l; ls av_governance | wc -l; ls rec | wc -l
