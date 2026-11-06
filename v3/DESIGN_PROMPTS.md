# Version 3 — modern cartoon: character design brief and prompts

The story is unchanged (`manuscript/`). This file defines how the characters and world look, and gives ready-to-run prompts for the first step: designing Orion.

**Production stack** (all usable commercially):
- ComfyUI (GPL-3) to run the models;
- Qwen-Image 2.0 or Z-Image Turbo (Apache-2.0) for character design and key frames;
- a character LoRA so Orion stays consistent;
- Wan 2.2 (Apache-2.0) for animation;
- Chatterbox (MIT) or Kokoro for voices;
- ACE-Step 1.5 (Apache-2.0) for music.

The models need a GPU. A 24 GB card is ideal; 16 GB works with quantised models.

## Styles under test
- **A. 3D animated-feature look** (primary). Soft, rounded, appealing proportions, expressive eyes, subsurface skin, warm cinematic lighting. Chosen first because open video models animate this look most reliably.
- **B. Painterly storybook.** A hand-painted gouache world, visible brush texture and glowing autumn light. Considered as the look for the whole film, or for the dreams only.

Describe styles generically; never name a studio, film or character in a prompt.

## Orion — design spec (carried over from Version 1)
**Kept from the story:**
- a young boy with a big dream;
- an autumn setting;
- cardboard wings taped to his arms.

**Kept from the V1 design:**
- messy brown hair with a cowlick that sticks up;
- an orange-and-cream striped long-sleeve shirt;
- blue jeans;
- red sneakers. These matter for the ending: his shoes end up on the telephone wire.

**Assumed:** about 7–8 years old (the manuscript says only "a young boy"). The author should confirm.

**Personality to read in the face:** determined, curious, hopeful. Big eyes. A gap-toothed grin when he's happy.

## Prompts — character sheet (run each with 4–8 seeds)

**A1 — 3D, turnaround**
> Character design turnaround sheet of a 7-year-old boy for a modern 3D animated feature film. Messy chestnut-brown hair with a cowlick sticking up at the crown, big expressive hazel eyes, light freckles, round friendly face. Long-sleeve shirt with horizontal orange and cream stripes, blue jeans, red canvas sneakers. Front view, three-quarter view, side view, back view, standing in a neutral pose. Soft stylized proportions, subsurface scattering skin, soft studio lighting, clean light-grey background, high detail, appealing, warm.

**A2 — 3D, expressions**
> Expression sheet of the same boy (chestnut hair with a cowlick, orange-and-cream striped shirt), modern 3D animated feature style: determined, frustrated, tired, hopeful, amazed, joyful laughing, sleepy. Head-and-shoulders portraits in a grid, consistent design, soft studio lighting, light background.

**A3 — 3D, hero frame (Scene 2)**
> Modern 3D animated feature film still. A 7-year-old boy with messy chestnut hair and a cowlick, in an orange-and-cream striped shirt, jeans and red sneakers, runs across a front lawn covered in red and orange maple leaves, flapping homemade cardboard wings held on his arms with tape. Golden-hour sunset, a warm suburban house and maple trees behind him, leaves swirling in the air, cinematic low camera angle, shallow depth of field, volumetric light, joyful determination.

**B1 — painterly storybook, hero frame (Scene 2)**
> Hand-painted gouache storybook illustration, visible brush strokes and paper texture, rich autumn palette. A young boy with messy brown hair and a cowlick, in an orange-and-cream striped shirt, jeans and red sneakers, runs across a lawn full of fallen maple leaves, flapping cardboard wings taped to his arms. A cozy house glows in the golden sunset, leaves drifting through the warm light. Whimsical, cinematic composition, soft glowing light.

**B2 — painterly, dream flight (Scene 15)**
> Hand-painted gouache storybook illustration. A young boy in striped pajamas and a small cape flies joyfully over a sleeping autumn neighborhood at night, arms out, a huge glowing moon behind him, drifting clouds lit silver, rooftops and maple trees far below, stars, a sense of wonder and freedom.

**Negative prompt** (for models that use one):
> photorealistic, uncanny, creepy, distorted hands, extra fingers, deformed face, text, watermark, logo

## Next steps after the design pass
1. The author picks Orion's design.
2. Generate 20–30 consistent images of him (angles, expressions, outfits: day clothes, pajamas, pajamas with cape).
3. Train the Orion LoRA.
4. Do the same for Mom, Dad and the truck driver.
5. Generate one key frame per shot, following `v2/docs/PRODUCTION_PLAN.md`; the shot list carries over.
6. Animate each shot with Wan 2.2 image-to-video, then score and assemble.
