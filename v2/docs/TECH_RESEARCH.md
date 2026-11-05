# Version 2 — technology research and pipeline decision

*Session of 5 Nov 2026. Everything below was measured or verified in this session, not assumed.*

## 1. The production machine

| Resource | Measured |
|---|---|
| CPU | 2 cores |
| RAM | 7.8 GB, no swap |
| GPU | **none** (no `nvidia-smi`, CUDA libs fail to load) |
| Disk | ~31 GB free |
| Network | package registries + GitHub only (other hosts return proxy 403) |

This single fact shapes every decision below.

## 2. AI video generation (Wan, LTX, ComfyUI)

| Option | Status here | Notes |
|---|---|---|
| **Wan 2.2 TI2V-5B** | ✗ not runnable | Released under Apache-2.0. Officially targets a 24 GB GPU (~9 min per 5-second 720p clip on an RTX 4090); community offloading gets it onto ~8 GB of **VRAM**. There is no CPU path at usable speed, and 7.8 GB of system RAM can't hold the weights plus activations. |
| **Wan 2.2 A14B** | ✗ | 80 GB VRAM unquantized; FP8/GGUF variants need a 16–24 GB GPU. |
| **LTX-2 / LTX-2.x** | ✗ | GPU-only. Weights are under Lightricks' own open-weights license (not OSI open source) — the actual LICENSE text must be reviewed for commercial terms before use; do not assume. |
| **ComfyUI** | installable, but pointless without a GPU | It's an orchestrator; the models above are the bottleneck. |

**Conclusion:** generative video can't be used on this machine, so it is not used — nothing in Version 2 claims otherwise.

**Realistic free route for a later pass:** Kaggle Notebooks offer free T4/P100 GPUs (commonly reported ~30 GPU-hours/week, 12-hour sessions); Colab's free tier gives a T4 with no published quota. Wan 2.2 TI2V-5B with offloading fits a 16 GB T4. That needs the owner's own Kaggle/Google account — I did not create accounts or incur costs. The strongest use of it would be the hybrid approach in the brief: render consistent 3D shots here, then use Wan's video-to-video / reference conditioning for a controlled finishing pass, keeping the 3D character as ground truth for consistency.

## 3. 3D production — chosen

| Option | Result |
|---|---|
| **Blender 5.2.3 LTS** via `pip install bpy` (Python module, GPL-3.0) | ✓ installs from PyPI, runs headless |
| Cycles on CPU | ✓ works. Trivial scene: 27 s/frame @720p. Full yard + character: **52 s/frame @540p, 92 s @720p** (12 samples + denoise) |
| EEVEE | ✓ renders via software EGL, but ~60 s/frame even for a trivial scene — slower than Cycles without a GPU |
| Character base | **MakeHuman hm08 base mesh, child morph targets, default skeleton and skin weights** — all explicitly released **CC0** (Sept 2020), fetched from GitHub. Only data files are used, no MakeHuman code (AGPL). |
| Clothing, hair, eyes, set, props | built procedurally in Python — no third-party assets |

### Why the first character attempt was discarded
I first built Orion from Blender skin-modifier primitives. The look-dev turnaround (`v2/review/lookdev_v0_primitive.png`) showed a mannequin: tube limbs, spiky hair, no real anatomy — the "simplistic" look the brief rejects. Switching to the CC0 MakeHuman base gave real child anatomy, proper topology for deformation, and production-grade skin weights. That was the single biggest quality jump of the session.

## 4. Render budget — the hard constraint

The full story narrated runs ~12 minutes = ~17,000 frames at 24 fps.

| Quality setting | Per frame | Full film |
|---|---|---|
| 960×540, 12 spp (test setting) | ~55 s | **~11 days** of continuous rendering |
| 1280×720 | ~92 s | ~18 days |
| 1920×1080 | ~3–4 min (est.) | ~6–8 weeks |

So a complete 3D Version 2 at this quality **cannot be rendered on this machine** in one night, or in a week. Options, in order of value:
1. **A GPU** (even one consumer card): Cycles on an RTX-class GPU is typically 20–50× faster than 2 CPU cores, bringing the full film to roughly a day of rendering at 1080p — and EEVEE becomes real-time-ish, making it hours.
2. Render the film in Cycles here over a long period (weeks), scene by scene — the pipeline is resumable.
3. Reduce look cost (fewer leaf instances, simpler shading) — trades away exactly the quality the brief asks for.

## 5. Narration and sound

Version 1's Kokoro-82M narration (Apache-2.0) and the procedural score are reusable and scene-timed; the brief identifies visuals, not audio, as V1's failure, so audio work was deliberately deferred until the visual pipeline passes its gate.
