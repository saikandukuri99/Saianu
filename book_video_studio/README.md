# Book video studio (Telugu)

Pipeline for a repeatable "book summary" YouTube format.

1. `episodes/<ep>/episode.json`: scenes -> sentences (Telugu VO text, visual id, theme, on-screen text).
2. Voice-over: one ElevenLabs take per scene (voice: Maddy, `eleven_v4`) saved as `episodes/<ep>/audio/sceneNN.mp3`.
3. `python3 build/build_timeline.py episodes/<ep>`: finds sentence boundaries from narration pauses, writes `renderer/timeline.js`, `voice_plan.json`, `subtitles_te.srt`.
4. `node build/render.js cues episodes/<ep>/cues.json`, then `python3 build/mix.py episodes/<ep>`: voice + synthesised music (ducked) + synthesised SFX -> `final_audio.wav`.
5. `node build/render.js frames <dir> <from> <to>` (run several in parallel), then ffmpeg encodes the JPEG frames with the audio.

Visuals live in `renderer/visuals*.js` (SVG, driven by time), shared illustration parts in `renderer/assets.js`.
All graphics, music and sound effects are generated in code, so there are no third-party copyright issues.
