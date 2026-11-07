# The Boy Who Wanted to Fly — Version 3 (modern cartoon)

Branch `version-3-cartoon`. Version 1 (`main`, tag `v1.0-final`) and Version 2 (`version-2-cinematic`) are untouched.

**The look:** a modern 3D animated-feature style, designed and approved with the author (`review/`), used throughout. The dream sequences get magical lighting rather than a style change, so Orion stays recognisably himself.

**How it's made**

1. **Key images.** `shots.py` lists 61 shots. Each one is generated with the open Z-Image Turbo model, running on CPU through stable-diffusion.cpp. Every prompt describes the characters, clothes and house in the same words, which keeps them consistent.
2. **Animation.** `animate.py` estimates a depth map for every image (Depth Anything V2 Small). The camera then pushes, pans, rises or flies with real parallax. Characters bob and breathe slightly, and atmospheric layers sit on top: falling leaves, dust in sunbeams, dream sparkles, the heart glow and speed streaks. `edit.py` decides which shot plays on which line of narration.
3. **Sound.** Version 1's narration (Kokoro voices), original score, sound effects and mix are reused unchanged. The picture is timed to the same beat manifest, so everything stays in sync.
4. **Titles and assembly.** `titles.py` makes the opening title and the credits; `assemble.py` produces the MP4 (1080p H.264, AAC, soft English subtitles).

## Rebuild
```bash
pip install kokoro-onnx soundfile scipy skia-python onnxruntime opencv-python pillow
# image model runner
git clone --recursive https://github.com/leejet/stable-diffusion.cpp && cmake -S stable-diffusion.cpp -B sd/build -DCMAKE_BUILD_TYPE=Release && cmake --build sd/build -j --target sd-cli
# models (all Apache-2.0) -> ~/models
HF=https://huggingface.co
curl -L -o ~/models/z_image_turbo-Q4_K.gguf $HF/leejet/Z-Image-Turbo-GGUF/resolve/main/z_image_turbo-Q4_K.gguf
curl -L -o ~/models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf $HF/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/main/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
curl -L -o ~/models/ae.safetensors $HF/Comfy-Org/Z-Image-Turbo/resolve/main/split_files/vae/ae.safetensors
curl -L -o ~/models/depth_anything_v2_small.onnx $HF/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx
curl -L -o ~/models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o ~/models/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

python3 v3/tools/gen_shots.py sd/build/bin/sd-cli ~/models build/v3/keyframes   # key images (~17 min each on 2 CPU cores; seconds on a GPU build)
python3 src/narrate.py --models ~/models                                        # voices
python3 src/audio.py                                                            # score, SFX, mix, subtitles
python3 v3/animate.py && python3 v3/titles.py                                   # picture
python3 v3/assemble.py                                                          # -> build/v3/The_Boy_Who_Wanted_to_Fly_V3.mp4
```
Set `V3_DEPTH_MODEL` if the depth model isn't at `~/models/depth_anything_v2_small.onnx`. Every step is resumable. Change a prompt in `shots.py`, delete that image, and rerun to replace one shot.

## Files
| Path | Contents |
|---|---|
| `shots.py` | Shot list and prompts (characters, wardrobe, sets) |
| `edit.py` | Which shot plays on which narration beat, camera move, effects |
| `animate.py` | Depth, parallax camera, effects, scene rendering |
| `titles.py`, `assemble.py` | Title, credits, final film |
| `keyframes/` | The generated key images |
| `review/` | Design rounds approved by the author |
| `LICENSES.md` | Models, software and items to review before release |

## Motion pass (real character animation, needs a rented GPU)
`motion/` turns every approved key image into moving footage with **Wan 2.2 I2V-A14B** (Apache-2.0) and the **Wan2.2-Lightning** 4-step LoRA (Apache-2.0), on Hugging Face Jobs (billed per minute, prepaid credits).
- `motion_prompts.py` says what moves in each shot. Long shots are split into chained 5-second segments (105 in all), each one starting from the last frame of the one before.
- `motion/motion_job.py` runs on the GPU and uploads each clip as soon as it is done, so the job can be resumed.
- `motion/motion.py` is the controller: `plan`, `prepare`, `submit`, `watch`, `fetch`, `cancel`.
- `animate.py` plays a shot's clips wherever they exist (slowed to at most 0.7× if a shot is longer, then a hold), and uses the 2.5D still everywhere else. The timing is unchanged, so the narration, music and subtitles still line up.

```bash
export HF_TOKEN=hf_...                                   # write token; never commit it
python3 v3/motion/motion.py prepare USER/boy-who-wanted-to-fly-motion
python3 v3/motion/motion.py submit  USER/boy-who-wanted-to-fly-motion --only s02a --max 1 --timeout 1h   # test shot
python3 v3/motion/motion.py submit  USER/boy-who-wanted-to-fly-motion --timeout 6h                      # everything
python3 v3/motion/motion.py fetch   USER/boy-who-wanted-to-fly-motion
python3 v3/animate.py && python3 v3/titles.py && python3 v3/assemble.py
```
Estimated cost for all 105 segments on an A100 is about $12 (`motion.py plan`). The test shot gives the real per-clip time.
