# Lower third: Janu Jethani (Solix red + dark blue)

- `LowerThird_Janu_Jethani.mov`: QuickTime Animation, **RGB + Alpha**, 1920×1080, 30 fps, 7 s, silent.
  The animation runs in for 1.2 s, holds, then runs out for 0.7 s. Put it on a track above your footage in Premiere; the alpha is Straight.
- `LowerThird_Janu_Jethani.png`: the same graphic as a full-frame transparent still (1920×1080).
- Colours: Solix dark blue #30267b (name plate), Solix red #ee2424 (title strip and left accent bar), Solix blue #0088cf (line racing along the top and the tab on the name plate's edge), white Inter text.
- Animation: red bar grows in, the #0088cf line races out, the blue and red plates wipe out with the text sliding in, a light shine sweeps across, it holds, then everything wipes back.
- `LowerThird_Janu_Jethani_preview.mp4`: preview over a grey background (not for editing).
- To make one for another speaker, run this and it writes the .mov and .png:
  `python3 source/build/lower_third.py "Name" "Title" output/lower_third/LowerThird_Name`
