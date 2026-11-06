# Version 3 — production report (first complete cut)

**Film:** `build/v3/The_Boy_Who_Wanted_to_Fly_V3.mp4`. It is 12 min 13 s, 1920×1080, 24 fps, H.264/AAC, with soft English subtitles. All 17 scenes are included, plus the title and credits.

The file (206 MB) is too large for ordinary git, so it is not committed. It was delivered directly to the author. Rebuild it with the steps in `README.md`.

## What was made
- **Key images.** 46 images in a modern 3D animated-feature style, generated locally with the open Z-Image Turbo model (Apache-2.0), on CPU at about 18 minutes each.
  - Every shot was checked by eye.
  - Five were rejected and regenerated:
    - a stray boy beside Mom (s02e);
    - the wrong shirt (s03a);
    - a kiss in the wrong place, which the story puts on the forehead (s09b);
    - an extra child in the window shot, three attempts (s10a).
- **2.5D animation.** Each image gets a depth map and is animated with a parallax camera move: push, pan, rise, or a flight with bobbing. On top sit falling leaves, dust motes, dream sparkles, the heart glow and speed streaks. Shots cross-dissolve, and scenes dip to black between them.
- **Sound.** Version 1's narration and character voices (Kokoro), original score and sound effects, timed to the same beat manifest. Each scene's picture length is locked to the soundtrack's frame offsets, so there is no drift.

## Consistency
- No character LoRA was needed.
- Orion, Mom, Dad, the driver and the house are described in identical words in every prompt (`shots.py`).
- Orion's look held across all 46 images: hair, freckles, striped shirt, red sneakers, pajamas and cape.
- Shots with no people use a separate environment-only style. The character words in the shared style kept summoning children into those shots.

## Known limitations (first cut)
- **Limited character movement.** Characters don't walk or lip-sync. The life comes from camera, depth, effects and sound. Full character animation (Wan 2.2) needs a GPU.
- **Long holds.** Some shots stay on screen 15–20 s, for example the opening house shot and the honey dream. 15 enrichment shots (`p=2` in `shots.py`) will break these up.
- **Small mismatches with the text:**
  - Orion's eyes are open in the "fell asleep" shot (s03e).
  - He looks calm rather than struggling in the honey dream (s10b).
  - He is barefoot in the flight shots before his sneakers come off.
- **Music.** The music is Version 1's procedural score, which is pleasant but simple. An open music model (ACE-Step 1.5, Apache-2.0) could score it properly; on this CPU-only machine that wasn't attempted.

## Review before commercial release
See `LICENSES.md`: protection of AI-generated imagery, the "Superman" wording in the narration (no Superman imagery appears on screen), and disclosure of the synthetic voices.
