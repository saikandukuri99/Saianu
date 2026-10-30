#!/bin/bash
# Resume the 3D frame render: removes truncated JPEGs, then renders only the missing frames with N parallel workers.
# usage: build/resume_render.sh <framesDir> <totalFrames> [workers]
set -e
OUT="$1"; T="$2"; N="${3:-4}"
cd "$(dirname "$0")"
export NODE_PATH=$(npm root -g)
mkdir -p "$OUT" "$OUT/../logs3"
python3 - "$OUT" <<'PY'
import os, sys
d = sys.argv[1]; bad = 0
for f in os.listdir(d):
    p = os.path.join(d, f)
    with open(p, 'rb') as fh: b = fh.read()
    if len(b) < 30000 or b[-2:] != b'\xff\xd9':
        os.remove(p); bad += 1
print('removed truncated frames:', bad)
PY
step=$(( (T + N - 1) / N ))
for i in $(seq 0 $((N-1))); do
  a=$((i*step)); b=$(((i+1)*step)); [ $b -gt $T ] && b=$T
  nohup node render3d.js frames "$OUT" $a $b > "$OUT/../logs3/w$i.log" 2>&1 &
done
echo "started $N workers"
