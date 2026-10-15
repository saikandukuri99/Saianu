# SOLIXCloud ECS — Keep the Proof (SOLIXEmpower 2026)

60 s · 3840×2160 · 30 fps · transparent graphics for Premiere Pro.

## deliverables/
| File | What |
|---|---|
| ECS_KeepTheProof_PREVIEW_1080p.mp4 | Review cut (graphics + VO + captions over sample navy bg) |
| ECS_GFX_4K_FILL_part0.mp4 / part1.mp4 | Graphics fill (part1 starts at frame 914 = 00:00:30:14) |
| ECS_GFX_4K_MATTE.mp4 | Graphics alpha matte (luma) |
| ECS_Captions_4K_FILL.mp4 / ECS_Captions_4K_MATTE.mp4 | Caption layer fill + matte |
| ECS_KeepTheProof_VO_48k24.wav | Voice-over, timed to picture |
| ECS_KeepTheProof_Captions.srt | Editable captions |
| ECS_KeepTheProof_Premiere.xml | Timeline with everything placed |

## Premiere setup
1. Keep all deliverables in one folder, import `ECS_KeepTheProof_Premiere.xml`.
2. V1 = your background. V2 graphics fill, V3 graphics matte, V4 caption fill, V5 caption matte, A1 VO.
3. Track Matte Key on V2 → Matte: Video 3, Composite using: Matte Luma. Same on V4 → Video 5.

## source/
HTML/JS motion timeline (`index.html`, `seek(t)`), Playwright renderer (`render.js` → ProRes 4444 alpha),
Kokoro TTS VO scripts (`gen.py`, `words.py`, `vo.py`), captions (`caps.py`), XML (`mkxml2.py`).
