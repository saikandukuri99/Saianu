# v4 (content edits): `Solix_SAP_OEBS_v4_*`
Oracle portion now comes before the SAP portion (voice and visuals swapped); "planning a move to the cloud" (S/4HANA removed, voice regenerated); opening headline shows "Oracle E-Business Suite" as one unit, underline first, then the module chips; Oracle circle first and "SOLIX" only on the 20+ slide; result slide reads "Legacy databases", "DATABASE" and "Modernization application"; "AI-activated data" with the network inside its own screen; only "dead weight" struck through. Both music versions: `..._v4_1080p/4K-UHD.mp4` (ambient) and `..._v4_CorporateMusic_*`.

# v3 (roomier boxes + music options): `Solix_SAP_OEBS_v3_*`
Highlight boxes now have more padding with the text centred, and the two end-slide boxes ("Built for SAP." / "Built for Oracle.") no longer touch. Same film, two music beds:
- `Solix_SAP_OEBS_v3_1080p.mp4` / `_4K-UHD.mp4`: original ambient bed
- `Solix_SAP_OEBS_v3_CorporateMusic_1080p.mp4` / `_4K-UHD.mp4`: corporate bed (100 bpm, piano, strings, light drums)
- `Solix_corporate_music_only.wav`: the corporate bed on its own

# v2 (Data Ask insert): `Solix_SAP_OEBS_v2_DataAsk_*.mp4`, 74.8 s
Adds the Data Ask scene (43.5 s to 54 s) between the policy scene and "The result?". Changes from v1: padded and centred highlight boxes, smooth policy-to-archive glide, hard cuts (no transitions), no sound effects, darker background with the AI network at 30 % opacity, and "The result?" held for 2 s (everything after it starts 0.9 s later than the v2 script timecodes). v1 files are kept below.

# SOLIXCloud for SAP + Oracle E-Business Suite: Empower 2026 film (63.9 s)

| File | What it is |
|---|---|
| `Solix_SAP_OEBS_1080p.mp4` | Master, 1920×1080, 30 fps, voice-over + music + SFX (−16 LUFS) |
| `Solix_SAP_OEBS_4K-UHD.mp4` | Same film, 3840×2160 (Lanczos upscale of the 1080p render) |
| `Solix_SAP_OEBS_VO_only.wav` | Voice-over alone, 48 kHz 24-bit, placed on the script timecodes |

Everything on screen is newly built (no clips from the reference video): a dark-blue Solix background with a live AI-network of connected light nodes, brand colours #0088cf (blue), #ee2424 (red) and #30267b (indigo), and the Solix logo fixed top-right for the whole film. The speedometer from the reference is replaced by a shrinking-database visual.

## Structure (Head / Body / Tail), matched to the voice-over

| Part | Time | Voice-over | On screen |
|---|---|---|---|
| **Head** | 0:00 | SAP and Oracle E-Business Suite run the business. | Opening headline: "SAP" (blue chip) / "Oracle" (red chip) / "run the business." with a blue→red underline, ERP module chips |
| | 0:03.5 | Years of inactive data … S/4HANA or the cloud. | Production DB bloating year by year, Bloating / Slowing / Costs cards, S/4HANA · Cloud destination |
| | 0:13 | SOLIXCloud brings 20+ years … to both. | SOLIXCloud wordmark, 20+ counter, beams to SAP and Oracle nodes |
| **Body** | 0:18.4 | For SAP … Archive Development Kit … Finance, Materials, Sales and more. | "For SAP." SAP → ADK → SOLIXCloud pipeline, archive-object cards (FI / MM / SD / more) |
| | 0:29 | For Oracle E-Business Suite … certified … archiving and application retirement. | "For EBS." Certified-by-Oracle badge, Archiving and Application-retirement cards |
| | 0:36.6 | Inactive data moves out on policy … searchable, reportable, under legal hold. | Policy gate moving records production → archive, three highlighted capability badges, retention timeline |
| **Tail** | 0:44 | The result? | Punch title |
| | 0:45.2 | Leaner production systems, cleaner migrations, SAP databases 30 to 60% smaller. | DB slab-stack shrinking, S/4HANA cloud-ready card, big 30–60% number |
| | 0:52.3 | Your ERP history becomes AI-ready data, not dead weight. | Archive records stream into a glowing AI network, "not dead weight" struck out |
| | 0:57 | SOLIXCloud. Built for SAP. Built for Oracle. | Wordmark, "Built for SAP." / "Built for Oracle." then the full Solix logo end card (solix.com, trademark notice) |

Every highlight is timed to the spoken word: clause breaks are snapped to the real pauses in the voice track (`source/build/sapoebs/align.py`).

## Rebuild
`source/build/sapoebs/`: `vo.py` (Kokoro `af_heart` voice, one take per script line) → `polish.py` (studio voice chain) → `assemble_vo.py` → `align.py` → `render.py video` → `audio.py` → mux with ffmpeg. Storyboard and animation: `scenes.py`, primitives: `lib.py`.
