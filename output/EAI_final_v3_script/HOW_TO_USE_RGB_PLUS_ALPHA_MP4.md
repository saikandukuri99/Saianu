# Using EAI_final_1080p_RGB_plus_ALPHA_side_by_side.mp4 in Premiere Pro
One MP4 (3840x1080): LEFT half = colour picture, RIGHT half = transparency (white = visible, black = transparent). Voice-over is embedded.
1. New sequence 1920x1080, 30 fps. Drag the MP4 to V1; keep it at 100 % scale. Alt-drag a copy to V2 (same start).
2. V1 clip (picture): Effect Controls > Crop > Right = 50 %; Motion > Position = 1920, 540.
3. V2 clip (matte): Crop > Left = 50 %; Motion > Position = 0, 540. (This clip stays visible only as a matte.)
4. Select the V1 clip: Effects > Video Effects > Keying > Track Matte Key. Matte = Video 2, Composite Using = Matte Luma.
5. Put your background below (V0 / lower track) - the Solix graphics now sit on it with transparency. Mute the audio of the V2 copy.
Tip: select V1+V2 > right-click > Nest, and you can use the nest like a normal alpha clip.
