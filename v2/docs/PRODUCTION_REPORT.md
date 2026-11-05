# Version 2 — production report

*Overnight session, 5 Nov 2026. Branch `version-2-cinematic` (Version 1 untouched on `main`, tag `v1.0-final` → `65a6ba4`).*

**Bottom line:** Version 2 is at its **quality gate**, not finished. A real 3D pipeline is built and proven: a rigged, dimensional Orion in a lit, dimensional autumn yard, animated and rendered with depth of field and atmosphere. It produced a 7.5-second test reel of two Scene 2 shots. **The full 17-scene film was not rendered.** The machine has no GPU, and at this quality a full render would take about 11 days of CPU time (§7).

## 1. Pipeline chosen
**Blender 5.2.3 (Cycles) driven entirely from Python.**
- **Character:** the CC0 MakeHuman child base mesh, skeleton and skin weights.
- **Costume, hair, eyes, wings, set, lighting, animation:** written as procedural code in `v2/blender/`.
- **Output:** each shot is a real 3D scene, with camera, lens, depth of field, sun, sky and aerial haze, saved as a `.blend` and rendered frame by frame.

## 2. Why this instead of Version 1's approach
- **V1 was a flat illustrated storybook:** 2D layers with camera moves. The brief rejects that look.
- **What 3D gives:** real volume, real light and shadow on the character, parallax, and lens behaviour. Most importantly, it gives *guaranteed consistency*: Orion is a single model, so he cannot drift between shots.
- **Why not AI video:** generative video (Wan 2.2, LTX-2) was the brief's other candidate. It can't run on this machine (§3).

## 3. Tools actually used
- Blender 5.2.3 `bpy`, Cycles on CPU with OIDN denoising.
- MakeHuman hm08 **data files** (CC0). No MakeHuman code was used.
- FFmpeg / libx264 for encoding.
- Python and NumPy.

**Researched but not used:** Wan 2.2, LTX-2 and ComfyUI. All three need a GPU; the machine has 2 CPU cores, 7.8 GB of RAM and no GPU. EEVEE was tested and ran slower than Cycles here. Details are in `TECH_RESEARCH.md`.

## 4. Visual improvements over Version 1
- **Orion:** a fully dimensional character with real child anatomy, subsurface-scattered skin, cloth shells with a striped shirt, sculpted hair with his cowlick, glossy eyes with lashes and brows, and cardboard-and-tape wings.
- **The yard:** golden-hour sun and a physical sky, thousands of instanced leaves, maple crowns, the house and garage, and aerial perspective.
- **The camera:** a tracking camera with a lens push and shallow depth of field. A low, intimate 50 mm close-up for the sitting beat.
- **Setup for the ending:** the telephone pole and wires that pay off in Scene 16 are already in the set.

## 5. How consistency is maintained
- **Orion:** one model and one rig (`orion2.py`), with one set of materials for every shot.
- **Poses:** written against bone axes that are calibrated numerically (`anim.py`). The same pose code therefore produces the same body language anywhere.
- **The world:** sets are built by code from seeds, so the yard is identical in every shot that uses it.

## 6. Scenes completed
**Scene 2, two shots:**
- **Shot A (108 frames):** Orion runs flapping his wings, crouches, leaps, hangs for a moment and lands.
- **Shot B (84 frames):** he sits catching his breath, looks up at the sky, then turns toward the house.

**Every other scene:** planned shot by shot in `PRODUCTION_PLAN.md`, but not built.

## 7. Was the full film rendered?
**No.** The measured cost is ~55 s/frame at 960×540. The film is ~17,000 frames, which is ~11 days of continuous rendering. 1080p would take weeks.

On one consumer GPU, the same `.blend` files render roughly 20–50× faster. That brings the full film down to about a day.

## 8. Where things are
| What | Where |
|---|---|
| Test reel | `v2/review/v2_test_reel_scene2.mp4` |
| Look-dev and test stills | `v2/review/*.png` |
| Pipeline code | `v2/blender/` |
| Docs | `v2/docs/` (research, plan, licenses, this report) |
| How to rebuild | `v2/README.md` |
| Character data | not in the repo; fetched by `v2/tools/fetch_makehuman_data.sh` |

## 9. Honest limitations
**Quality**
- The look is closer to good TV or game-cinematic CG than to a feature film.
- The sky overexposes to near-white. The house is a simple box with no trim, siding or gutters.
- **The close-up (shot B) is the weakest moment:** Orion's face is stiff and mannequin-like, and his shoulders and torso read too broad for a young child. A character modeller's sculpt and a face rig are the fix.
- The hair is a sculpted cap: it reads at a distance, but looks helmet-like up close.
- There is no blinking, no facial animation and no lip-sync yet.
- The run, flap and sit animations are procedural cycles, not hand-keyed performance. They read clearly but lack the weight and nuance of feature work.

**Missing**
- Mom, Dad, the garbage-truck driver, the chickens, and every set except the yard.
- Narration and music in the reel. It has only a quiet procedural wind bed: V1's narration audio isn't in the repo, and audio was deferred until the visuals pass the gate.

**Delivery**
- The branch couldn't be pushed from this session. GitHub access was read-only, so the branch is delivered as a git bundle.

## Style exploration (after the test)
After the test reel, the same frame was re-rendered in four looks to choose a direction (`v2/review/style_test_options.jpg`):
- current;
- cinematic lighting (painted sky with clouds, `style_test.py --style cinema`);
- painterly post filter (`paint_post.py`);
- ink lines and cel shading (`style_test.py --style toon` + `toon_post.py`).

The ink/cel look is the strongest on this hardware: it hides the simple modelling and costs no more to render. The painterly filter is weak, and real painted styling needs a GPU AI restyle. EEVEE runs out of memory here, so the cel look is built from Cycles render passes plus a post step.

## 10. Next iteration
1. **Get a GPU.** Your own machine, or free Kaggle/Colab sessions under your account. This is the single change that makes the full film possible.
2. **Look pass:**
   - a sky with real clouds and graded exposure;
   - house detail (siding, trim, porch);
   - hair cards in place of the shell;
   - a face rig with blinks, brows and mouth shapes driven by the narration.
3. **Build the remaining cast** on the same MakeHuman base (Mom, Dad, the driver), each with their own costume, plus pajamas and a cape for Orion.
4. **Build the remaining sets** in plan order: garage, kitchen and stairs, bedroom, coop, dream sky.
5. **Scenes 12–15 (the flight):** cape cloth simulation, volumetric clouds and a free-flying camera.
6. **Audio:** reattach V1's Kokoro narration (regenerable from `audio/narration/screenplay.py`), then score and sound effects.
7. **Optional finishing pass:** Wan 2.2 (Apache-2.0) as a video-to-video pass on the 3D renders, with the 3D character kept as ground truth.
