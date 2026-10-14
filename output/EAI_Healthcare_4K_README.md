# EAI Healthcare – 4K (FemaleVO HyperBeat)

`Solix_EAI_Healthcare_FemaleVO_HyperBeat_4K.mp4` – 3840×2160, 30 fps, 1:18.7, H.264.

Made from `Solix_EAI_Healthcare_FemaleVO_HyperBeat_1080p.mp4` with only these changes:

1. **Unified Governance:** the Revenue Cycle Intelligence ₹ icon is replaced with a rising-graph icon (same orange circle).
2. **Six Pillars:** the diagram is the supplied six-pillar artwork (`source/assets_hc/six_pillars.png`) with
   **AI Clinical Intelligence** (upper-right) and **Intelligent Imaging & Radiology** (middle-right) swapped.
   Each pillar still turns red when the voice names it, in narration order.

Unchanged: voice-over and background music (audio stream copied bit-for-bit), all other scenes,
background, titles, logo and timing (same 2362 frames as the 1080p original).
The 4K picture is a Lanczos upscale of the 1080p original.

Build: `source/build/hc_chunk.py` (renders the two changed scenes), then ffmpeg concat + 4K encode.
