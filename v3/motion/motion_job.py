"""Runs ON the rented GPU (Hugging Face Jobs). Animates each approved key image with
Wan 2.2 I2V-A14B (Apache-2.0) + the Wan2.2-Lightning 4-step LoRA (Apache-2.0), chaining
segments for long shots (each segment starts from the previous segment's last frame).

Inputs come from a private dataset repo (env MOTION_REPO): keyframes/*.jpg and plan.json.
Every finished clip is uploaded straight back to clips/<shot>_<seg>.mp4, so a job that is
stopped or times out loses at most one clip, and a rerun skips what is already there.

Env: MOTION_REPO, HF_TOKEN (secret), ONLY (comma list of shot ids, optional),
     MAX_SEGMENTS (optional), WIDTH/HEIGHT (default 1280x720), FRAMES (default 81).
"""
import json, os, sys, tempfile, time
import numpy as np
import torch
from PIL import Image
from huggingface_hub import HfApi, snapshot_download, hf_hub_download
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
from diffusers.utils import export_to_video

REPO = os.environ["MOTION_REPO"]
W, H = int(os.environ.get("WIDTH", 1280)), int(os.environ.get("HEIGHT", 720))
FRAMES = int(os.environ.get("FRAMES", 81))           # 4k+1; 81 frames = 5.06 s at 16 fps
ONLY = set(filter(None, os.environ.get("ONLY", "").split(",")))
MAXSEG = int(os.environ.get("MAX_SEGMENTS", 0))
api = HfApi()

local = snapshot_download(REPO, repo_type="dataset", allow_patterns=["keyframes/*", "plan.json"])
plan = json.load(open(os.path.join(local, "plan.json")))
done = {f for f in api.list_repo_files(REPO, repo_type="dataset") if f.startswith("clips/")}
work = [s for s in plan["segments"] if (not ONLY or s["shot"] in ONLY)]
print(f"{len(work)} segments planned, {len(done)} clips already in the repo", flush=True)

t0 = time.time()
mid = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"
vae = AutoencoderKLWan.from_pretrained(mid, subfolder="vae", torch_dtype=torch.float32)
pipe = WanImageToVideoPipeline.from_pretrained(mid, vae=vae, torch_dtype=torch.bfloat16)
steps, g1, g2 = 40, 3.5, 3.5
try:
    lr = "lightx2v/Wan2.2-Lightning"
    sub = "Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1"
    pipe.load_lora_weights(lr, weight_name=f"{sub}/high_noise_model.safetensors", adapter_name="light")
    pipe.load_lora_weights(lr, weight_name=f"{sub}/low_noise_model.safetensors", adapter_name="light2",
                           load_into_transformer_2=True)
    steps, g1, g2 = 4, 1.0, 1.0
    print("Lightning LoRA loaded: 4 steps", flush=True)
except Exception as e:                                  # fall back to the full 40-step sampler
    try:
        pipe.unload_lora_weights()
    except Exception:
        pass
    print(f"Lightning LoRA not loaded ({e}); using {steps} steps", flush=True)
mem = torch.cuda.get_device_properties(0).total_memory / 2**30
pipe.enable_model_cpu_offload()      # two 14B experts + text encoder exceed 80 GB with 720p activations
print(f"GPU {torch.cuda.get_device_name()} {mem:.0f} GB, models ready in {time.time() - t0:.0f}s", flush=True)

tmp = tempfile.mkdtemp()
last = {}
made = 0
for s in work:
    name = f"clips/{s['shot']}_{s['seg']}.mp4"
    lastpng = f"clips/{s['shot']}_{s['seg']}_last.png"
    if name in done:
        if s["seg"] + 1 < s["of"]:          # need its last frame to continue the chain
            last[(s["shot"], s["seg"])] = Image.open(hf_hub_download(REPO, lastpng, repo_type="dataset")).convert("RGB")
        continue
    if MAXSEG and made >= MAXSEG:
        break
    if s["seg"] == 0:
        img = Image.open(os.path.join(local, "keyframes", s["shot"] + ".jpg")).convert("RGB")
    else:
        img = last[(s["shot"], s["seg"] - 1)]
    img = img.resize((W, H), Image.LANCZOS)
    t = time.time()
    g = torch.Generator("cuda").manual_seed(s["seed"])
    frames = pipe(image=img, prompt=s["prompt"], negative_prompt=plan["negative"], height=H, width=W,
                  num_frames=FRAMES, num_inference_steps=steps, guidance_scale=g1, guidance_scale_2=g2,
                  generator=g).frames[0]
    mp4 = os.path.join(tmp, f"{s['shot']}_{s['seg']}.mp4")
    export_to_video(frames, mp4, fps=16)
    lf = Image.fromarray((np.clip(frames[-1], 0, 1) * 255).astype(np.uint8)) if isinstance(frames[-1], np.ndarray) else frames[-1]
    lfp = os.path.join(tmp, "last.png"); lf.save(lfp)
    last[(s["shot"], s["seg"])] = lf
    api.upload_file(path_or_fileobj=mp4, path_in_repo=name, repo_id=REPO, repo_type="dataset")
    api.upload_file(path_or_fileobj=lfp, path_in_repo=lastpng, repo_id=REPO, repo_type="dataset")
    made += 1
    print(f"CLIP {name} {time.time() - t:.0f}s", flush=True)
print(f"DONE {made} clips in {time.time() - t0:.0f}s", flush=True)
