# EAI 60 s teaser: build notes
- Scenes are plain HTML driven by `render(t)`; `render.js` serves them via `python3 -m http.server 8123` from this folder (add `three` from npm to `lib/`, and `lib/jsm/environments/RoomEnvironment.js`), takes a frame per 1/30 s with Playwright (transparent background) and pipes them to ffmpeg.
- Usage: `node render.js s05 out.mov 8` (ProRes 4444) ; clips were then re-encoded to QuickTime Animation: `ffmpeg -i in.mov -c:v qtrle -pix_fmt argb out.mov`.
- Voice: `tts3.py` (Kokoro via sherpa-onnx, speaker 3 = af_heart, per sentence from `sents.json`) then `asm2.py` joins them. `lib/timemap.js` maps the original cue times in the scenes onto the final voice timing (anchors.json).
