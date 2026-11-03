# Lower thirds: Janu Jethani, Suresh Mani, Arvind Sathi (Solix red, dark blue, blue)

The `LowerThird_Suresh_Mani*` and `LowerThird_Arvind_Sathi*` files come in the same set of formats as the Janu Jethani files listed below.

| File | Size | Use |
|---|---|---|
| `LowerThird_Janu_Jethani_Reel.mov` | 1080×1920 (Reels/Shorts) | RGB + Alpha, use this in Premiere |
| `LowerThird_Janu_Jethani_Reel_ProRes4444.mov` | 1080×1920 | RGB + Alpha in ProRes 4444, works best in Premiere, Final Cut and After Effects |
| `LowerThird_Janu_Jethani_Reel.png` | 1080×1920 | transparent still |
| `LowerThird_Janu_Jethani_Reel_preview.mp4` | 1080×1920 | preview over grey only |
| `LowerThird_Janu_Jethani.mov` | 1920×1080 (16:9) | RGB + Alpha, use this in Premiere |
| `LowerThird_Janu_Jethani_ProRes4444.mov` | 1920×1080 | RGB + Alpha in ProRes 4444 |
| `LowerThird_Janu_Jethani.png` | 1920×1080 | transparent still |
| `LowerThird_Janu_Jethani_preview.mp4` | 1920×1080 | preview over grey only |

- Every .mov is QuickTime Animation, 30 fps, 7 s, with no audio. The alpha is Straight.
- **Colours:** dark blue #30267b on the name panel, red #ee2424 on the title strip and the left accent bar, a blue #0088cf strip on the right edge of the name panel, and white Inter text.
- **Animation:** the red bar grows in, the name and title panels slide out with their text, a light shine sweeps across, it holds, then everything slides back out over the last 0.7 s.
- **Reel placement:** the graphic sits at the left, with its bottom edge at y = 1500, so it stays clear of the caption and buttons at the bottom of the screen. The title is on two lines.
- **Another speaker:** the title wraps automatically, and `|` forces a line break. Run this and it writes the .mov and .png:
  `python3 source/build/lower_third.py "Name" "Title line 1 | line 2" output/lower_third/LowerThird_Name --reel`
  Leave off `--reel` to get the 16:9 version.

**Where is the alpha?** Every `.mov` here has RGB + alpha, and the `_preview.mp4` files do not. A phone or a basic player shows the transparent area as black because it can't display alpha. Import the .mov into an editor to see it transparent.
