SOLIX APPLICATION RETIREMENT: EDITING ELEMENTS

The final film's graphics as separate elements. The content is unchanged: same animation, same VO, same music.
Removed: the background (red/indigo gradient, ambient bokeh, vignette, grain) and the burned-in captions (now in the SRT).

VIDEO  1920x1080, 30 fps, Apple ProRes 4444 with alpha (straight), one clip per scene.
       Scenes longer than about 2 s are cut into parts so every file stays under 100 MB. Parts butt together frame-accurately.
       Each file name ends with its timeline start timecode (TC mm-ss-ff); Clip_list.txt gives the start time of each.
       In Premiere, put your background on V1 and the clips on V2 at their start times. Blend mode: Normal.
       If the alpha looks wrong, right-click the clip > Modify > Interpret Footage > Alpha Channel: "Straight".

AUDIO  48 kHz, 24-bit WAV, all the full length of the film (start at 00:00:00):
       Solix_AR_VO.wav            voice-over, at its level in the film's mix
       Solix_AR_BGM_ducked.wav    music exactly as heard in the film (dips under the voice)
       Solix_AR_BGM_clean.wav     the same music without the ducking, if you want to do your own
       Solix_AR_full_mix.wav      the film's final mix (loudness -16 LUFS), for reference

CAPTIONS  Solix_AR_captions.srt: the same lines and timings as the film's captions.
