# 3D toolkit (Three.js + Blender)

## Three.js (used for the final video)
* `renderer3d/core3d.js`: renderer, image-based lighting, 3-point lights, shader sky + animated grid floor + bokeh dust,
  bloom, film grain, chromatic aberration, whip/zoom-blur transitions, keyframed camera rig (`evalCam`/`setCamera`).
* `renderer3d/kit3d.js`: 3D props (coins, bank, piggy bank, globe, bulb, gears, puzzle pieces, thumbs-up, bell, ...),
  toy-style characters, extruded Telugu 3D text (`text3d`, `words3d`) and glass cards.
* `renderer3d/v3d_*.js`: one shot per sentence: camera keys, lighting, choreography and sound-effect cues.
* `renderer3d/showcase.html`: standalone real-time demo. Serve the folder (`python3 -m http.server`) and open
  `http://localhost:8000/renderer3d/showcase.html` in a desktop browser. Edit the `SHOT` array to direct your own camera.
* `build/render3d.js`: frame-by-frame capture for offline rendering (software WebGL here; much faster on a GPU).

## Blender
* `blender/cinematic_money_scene.py`: builds a cinematic scene with bpy (PBR gold, glass, emissive neon, 3-point lighting,
  volumetric spot, bezier orbit camera with depth of field, compositor bloom/vignette/aberration) and renders MP4.
  `blender -b -P blender/cinematic_money_scene.py -- --engine CYCLES --samples 48 --frames 180 --out ./render/money.mp4`
