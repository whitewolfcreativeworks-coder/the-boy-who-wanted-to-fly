# Version 3 — dependency and license record

The film is made from: AI-generated key images (open model, run locally), depth-based 2.5D animation, and Version 1's narration, score and sound effects.

| Component | Used for | License | Commercial use |
|---|---|---|---|
| *The Boy Who Wanted to Fly* (story) | Everything | © 2018 Jason Whitewolf, all rights reserved | Owner's work, untouched in `manuscript/` |
| **Z-Image Turbo** (Tongyi-MAI / Alibaba), GGUF quantisation by leejet | Every key image | Apache-2.0 | Yes |
| Qwen3-4B-Instruct-2507 (GGUF by unsloth) | Text encoder for Z-Image | Apache-2.0 | Yes |
| FLUX autoencoder `ae.safetensors` (via Comfy-Org/Z-Image-Turbo) | Image decoder for Z-Image | Apache-2.0 (FLUX.1-schnell release) | Yes |
| stable-diffusion.cpp | Runs the image model on CPU | MIT | Yes |
| **Depth Anything V2 Small** (ONNX, onnx-community) | Depth maps for parallax | Apache-2.0 (the Small model only; Base/Large are CC-BY-NC) | Yes |
| onnxruntime, OpenCV, NumPy, Pillow | Inference, warping, effects, text | MIT / Apache-2.0 / BSD / HPND | Yes |
| Kokoro-82M + kokoro-onnx | Narration and character voices (Version 1 pipeline) | Apache-2.0 / MIT | Yes |
| Original procedural score and SFX (`src/audio.py`) | Music and sound | Written for this production | Yes |
| Fredoka, Nunito | Title and credits | SIL Open Font License | Yes |
| FFmpeg / libx264 | Encoding | LGPL / GPL (tool use) | Yes |

## Items to review before commercial release
- **AI-generated imagery.** In the US, purely AI-generated images may not be protected by copyright on their own. The story, script, edit and selection are the author's or the production's, but check how this affects any distribution deal.
- **Superman wording.** The narration keeps the manuscript's "Superman" lines (as Version 1 did). The images avoid any logo or costume, and the cape is plain red. A trademark review is advisable before commercial release.
- **Synthetic voices.** The narration is synthetic (Kokoro). Some platforms require disclosure of AI-generated media.
- **Prompting.** Prompts describe a generic "3D animated feature film style" and never name a studio, film or character.
