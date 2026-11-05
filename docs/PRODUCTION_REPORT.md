# Production report — The Boy Who Wanted to Fly

## What was produced
A complete 12-minute animated storybook film of Jason Whitewolf's story: all 17 manuscript scenes in order, an opening title card, and closing credits.

- **File:** `The_Boy_Who_Wanted_to_Fly.mp4` (GitHub Release `v1.0`)
- **Format:** 1920×1080, 24 fps, H.264 (CRF 18), AAC 192 kb/s stereo, loudness-normalized to −16 LUFS, soft English subtitles
- **Also produced:** character reference sheet, full reproducible source pipeline, adaptation notes, license record

## How it was made
The production machine had **2 CPU cores and no GPU**, which rules out diffusion image/video models (ComfyUI, Wan 2.2, LTX) at any useful quality or speed. Rather than ship a slideshow of inconsistent stills, the film is a **hand-coded 2.5D vector animation**:

| Stage | Technology |
|---|---|
| Characters | One shared puppet rig (`src/characters.py`) — every human is the same jointed skeleton with its own proportions and palette, so Orion is pixel-identical in every shot. Expressions, blinks, talking mouths, wings, cape physics. |
| Environments | Procedural illustrated sets with multi-layer parallax: yard (house, maple trees, telephone wires), garage, kitchen, stairs, bedroom with posters, chicken coop, honey dream, pool memory, night town, clouds, moon, star field, dawn street |
| Animation | Eased camera paths, walk/run/flap/fly cycles, falling-leaf and sparkle particle systems, leaf-pile bursts, light rays, paper-grain and vignette finishing |
| Narration | Kokoro-82M TTS (Apache-2.0) — narrator `af_heart`; Orion a blended, pitch-raised child voice; Mom, Dad and the driver each cast separately |
| Score & SFX | Fully original, synthesized in NumPy/SciPy: a main theme and a 3/4 lullaby, mood cues per scene (playful marimba, music-box bedtime, Lydian dream pads, driving flight arpeggios), plus synthesized wind, birds, leaves, tape, clucks, truck engine, branch taps, heartbeats, whooshes, pops |
| Sync | Scene timing is computed from the recorded narration lengths, so picture, sound, and subtitles line up automatically |
| Assembly | FFmpeg: per-scene clips → concat → loudnorm → mux with subtitles |

## What worked particularly well
- **Character consistency is perfect by construction** — the rig makes it impossible for Orion to drift.
- **The waking world vs. the dream world** read as two different places: warm saturated autumn and paper texture by day; deep violet skies, aurora ribbons, and sparkles in the dreams.
- **The heart moment (scene 14):** the camera pushes in as a glowing heart appears on Orion's chest, rays and floating hearts spiral out, and the music turns from wonder into the main theme with a heartbeat underneath.
- **The flight (scene 15)** is staged phrase-by-phrase — over the neighborhood, through clouds, silhouetted across a giant moon, into a star field, then a speed-line rush.
- **The ending (scene 16):** shoes pop off ("Whoops!"), tumble down through a dawn sky, snag on the telephone wire, and the camera pulls back to reveal many pairs hanging along the street. The telephone wires are visible in every daytime yard shot as quiet foreshadowing, and the red sneakers are established from the first frame.
- **Narration clarity:** music ducks automatically under speech (~13 dB below the voice).

## Remaining limitations
- **Animation is puppet-style, not full character animation.** Limbs are rigid two-segment tubes; there is no squash-and-stretch acting or hand-drawn in-betweening. Bodies are always in profile/three-quarter view.
- **Lip-sync is approximate** (mouth flaps while a character is speaking; no phoneme shapes).
- **Synthetic voices.** Kokoro is clear and warm, but Orion's voice is an adult voice pitched up, and delivery is even rather than acted.
- **The score is synthesized**, so it sounds like a gentle chiptune/music-box hybrid rather than an orchestra.
- **A few staging simplifications:** adults sit on implied chairs at the dinner table; the friends in the pool memory are simple shapes; the pool and honey scenes don't show Orion's friends in detail.
- The final film was reviewed by sampling frames and contact sheets and by measuring audio levels; it was not watched in real time with sound by a human.

## Licensing items to review before commercial distribution
See `docs/LICENSES.md`. In short: the narration says **"Superman"** (author's text, kept as written; visuals use only original designs). Consider swapping to a generic phrase before monetizing — it's a one-line change per beat and a re-render.

## Suggestions for a refinement pass
1. **Voice:** record a real child and narrator, or try a newer expressive TTS; swap files in `build/audio/lines/` and re-run `audio.py` + `assemble.py` (timing re-flows automatically if lengths change and scenes are re-rendered).
2. **Music:** replace the procedural score with a recorded or commissioned score (the cue map in `src/audio.py` `PLAN` already defines where each mood starts).
3. **Character acting:** add bendy limbs (3-segment splines), more expressions, and phoneme-based mouth shapes driven by Kokoro's timing output.
4. **With a GPU:** use these rendered frames as structure guides for image-to-video stylization (e.g. a painterly pass) while keeping the rig's consistency.
5. **Superman wording:** decide whether to keep or genericize before release.
