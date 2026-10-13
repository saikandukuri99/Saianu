# EAI 60 s teaser: build notes
- Scenes are plain HTML driven by `render(t)`; `render.js` serves them via `python3 -m http.server 8123` from this folder (add `three` from npm to `lib/`, and `lib/jsm/environments/RoomEnvironment.js`), takes a frame per 1/30 s with Playwright (transparent background) and pipes them to ffmpeg.
- Usage: `node render.js s05 out.mov 8` (ProRes 4444) ; clips were then re-encoded to QuickTime Animation: `ffmpeg -i in.mov -c:v qtrle -pix_fmt argb out.mov`.
- Voice: `tts.py` (Kokoro via sherpa-onnx, speaker 16, speed 1.05) then `asm.py` joins the lines with set pauses. Text is in `script.json`.
