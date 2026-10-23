#!/bin/sh
# VO + music: music sits low and ducks under narration; master to -16 LUFS / -1 dBTP.
S=$1
ffmpeg -nostdin -v error -y -i $S/vo_track.wav -i $S/music.wav -filter_complex "
[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[vo][sc];
[1:a]aresample=48000,volume=0.62[mu];
[mu][sc]sidechaincompress=threshold=0.015:ratio=8:attack=40:release=450:makeup=1[duck];
[vo][duck]amix=inputs=2:normalize=0:duration=longest,
loudnorm=I=-16:TP=-1.5:LRA=11[out]" -map "[out]" -ar 48000 -c:a pcm_s24le $S/mix.wav
