# CDP Booth Loop v6 (white, motion graphics)

`Solix_CDP_Booth_Loop_v6_1080p60.mp4`: 1920 × 1080, 60 fps, 90 s, H.264, **no audio track**. The last frame flows straight into the first, so set the player to loop it.

Built from Storyboard v5 (same 11 frames, same timings, same copy). What changed from the v5 video:
- White background with a slowly drifting tech network (nodes, links and travelling data pulses in Solix blue #0088cf and red #ee2424). The network moves on a 90-second cycle, so the loop point is invisible.
- Headline highlights use #0088cf, #ee2424 and #30267b; headlines are larger for reading from across the hall.
- Motion: headline words rise in behind a mask, kicker lines wipe on, supporting lines fade up, and each frame exits with a soft lift and fade. A thin blue/red light sweep marks each frame change.
- Banner: the active tab lights in Solix blue with a red underline, covered tabs stay softly lit and upcoming tabs stay dim. On the Governed frame the Built-in governance bar lights with a moving sheen and links to every tab.
- Each frame's visual is animated as described in the storyboard (tiles dropping onto the foundation, blocks archiving, records leaving the legacy app before it switches off, the document scan, search typing, the shield drawing on, scan-and-mask, the Data Lake+ fill, governance check-ins, the AI answer with citations, and the QR end card).
- The QR code points to the UTM-tagged CDP page from v5 (`utm_campaign=cdp_booth_loop`). The scan line over it runs only briefly so phones can read it.

Source: `source/cdp_loop/loop.html` (scenes) and `source/cdp_loop/render.js` (renderer). To re-render: `NODE_PATH=$(npm root -g) node source/cdp_loop/render.js video out.mp4 4 60`.
