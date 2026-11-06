"""Generate Orion design images with Z-Image Turbo (Apache-2.0) via stable-diffusion.cpp.

    python3 gen_design.py SD_CLI MODELS_DIR OUTDIR [ids...] [--seeds 1,2] [--size 1024x576]

Runs on CPU (slow, a few minutes per image) or on any GPU build of sd-cli.
Prompts are the ones in v3/DESIGN_PROMPTS.md. Existing outputs are skipped.
"""
import argparse, os, subprocess, time

STYLE_3D = ("modern 3D animated feature film style, soft stylized appealing proportions, "
            "subsurface scattering skin, expressive eyes, cinematic lighting, high detail")
STYLE_PAINT = ("hand-painted gouache storybook illustration, visible brush strokes and paper texture, "
               "rich autumn palette, soft glowing light, whimsical")
ORION = ("a 7-year-old boy with messy chestnut-brown hair and a cowlick sticking up at the crown, "
         "big expressive hazel eyes, light freckles, round friendly face, long-sleeve shirt with "
         "horizontal orange and cream stripes, blue jeans, red canvas sneakers")

PROMPTS = {
    "A1_turnaround": (f"Character design turnaround sheet for {STYLE_3D}: {ORION}. Front view, three-quarter "
                      "view, side view and back view side by side, neutral standing pose, clean light-grey "
                      "background, soft studio lighting, appealing and warm.", "1024x576"),
    "A2_expressions": (f"Expression sheet, {STYLE_3D}: head-and-shoulders portraits in a grid of the same boy, "
                       f"{ORION}, showing determined, frustrated, tired, hopeful, amazed and joyful laughing "
                       "expressions, consistent design, light background, soft studio lighting.", "1024x576"),
    "A3_hero_run": (f"Film still, {STYLE_3D}. {ORION}, runs across a front lawn covered in red and orange maple "
                    "leaves, flapping homemade cardboard wings held on his arms with tape. Golden-hour sunset, "
                    "a cozy suburban house and maple trees behind him, leaves swirling in the air, low camera "
                    "angle, shallow depth of field, volumetric light, joyful determination.", "1024x576"),
    "A4_portrait": (f"Close-up portrait, {STYLE_3D}. {ORION}, sitting on autumn grass catching his breath, "
                    "looking up at the sunset sky with hope, warm rim light, shallow depth of field.", "1024x576"),
    "B1_hero_run": (f"{STYLE_PAINT}. {ORION}, runs across a lawn full of fallen maple leaves, flapping cardboard "
                    "wings taped to his arms. A cozy house glows in the golden sunset, leaves drifting through "
                    "the warm light, cinematic composition.", "1024x576"),
    "B2_dream_flight": (f"{STYLE_PAINT}. A young boy with messy chestnut-brown hair in striped pajamas and a "
                        "small red cape flies joyfully over a sleeping autumn neighborhood at night, arms "
                        "out, a huge glowing moon behind him, drifting silver clouds, rooftops and maple trees "
                        "far below, stars, wonder and freedom.", "1024x576"),
    "A5_dream_flight": (f"Film still, {STYLE_3D}. A young boy with messy chestnut-brown hair in striped pajamas "
                        "and a small red cape flies joyfully over a sleeping autumn neighborhood at night, "
                        "arms out, a huge glowing moon behind him, silver clouds, rooftops far below, stars, "
                        "wonder and freedom.", "1024x576"),
}

ap = argparse.ArgumentParser()
ap.add_argument("sd"); ap.add_argument("models"); ap.add_argument("out")
ap.add_argument("ids", nargs="*")
ap.add_argument("--seeds", default="1")
ap.add_argument("--size", default=None)
ap.add_argument("--steps", type=int, default=8)
ap.add_argument("--threads", type=int, default=2)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
for pid in a.ids or list(PROMPTS):
    prompt, size = PROMPTS[pid]
    w, h = (a.size or size).split("x")
    for seed in a.seeds.split(","):
        out = os.path.join(a.out, f"{pid}_s{seed}.png")
        if os.path.exists(out):
            continue
        cmd = [a.sd, "--diffusion-model", os.path.join(a.models, "z_image_turbo-Q4_K.gguf"),
               "--vae", os.path.join(a.models, "ae.safetensors"),
               "--llm", os.path.join(a.models, "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"),
               "-p", prompt, "--cfg-scale", "1.0", "--steps", str(a.steps), "-W", w, "-H", h,
               "-s", seed, "-t", str(a.threads), "--vae-tiling", "--mmap", "-o", out]
        t = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(f"{pid} seed {seed}: {'ok' if r.returncode == 0 else 'FAILED'} {time.time() - t:.0f}s", flush=True)
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-1500:], flush=True)
