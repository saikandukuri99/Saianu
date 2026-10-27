#!/bin/sh
# VO + supplied BGM: music ducks under narration; master to -16 LUFS / -1.5 dBTP.
# usage: mix_bgm.sh <dir with vo_track.wav> <bed.wav> <music gain> <out.wav>
ffmpeg -nostdin -v error -y -i $1/vo_track.wav -i $2 -filter_complex "
[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[vo][sc];
[1:a]aresample=48000,volume=$3[mu];
[mu][sc]sidechaincompress=threshold=0.015:ratio=6:attack=40:release=500:makeup=1[duck];
[vo][duck]amix=inputs=2:normalize=0:duration=first,
loudnorm=I=-16:TP=-1.5:LRA=11[out]" -map "[out]" -ar 48000 -c:a pcm_s24le $4
