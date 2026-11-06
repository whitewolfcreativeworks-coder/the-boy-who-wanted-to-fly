"""Generate every key image in v3/shots.py, priority 1 first. Resumable (skips existing files).

    python3 gen_shots.py SD_CLI MODELS_DIR OUTDIR [--p 1] [--only s02c,s05a] [--seed 1]
"""
import argparse, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from shots import SHOTS

ap = argparse.ArgumentParser()
ap.add_argument("sd"); ap.add_argument("models"); ap.add_argument("out")
ap.add_argument("--p", type=int, default=2, help="generate priorities up to this number")
ap.add_argument("--only", default="")
ap.add_argument("--seed", default="1")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
repo = os.path.abspath(os.path.join(HERE, "..", ".."))
only = set(filter(None, a.only.split(",")))

queue = sorted((s for s in SHOTS if s["p"] <= a.p and (not only or s["id"] in only)),
               key=lambda s: (s["p"], s["id"]))
for s in queue:
    out = os.path.join(a.out, f"{s['id']}.png")
    if os.path.exists(out):
        continue
    if "reuse" in s:
        shutil.copy(os.path.join(repo, s["reuse"]), out)
        print(f"{s['id']}: reused {s['reuse']}", flush=True)
        continue
    cmd = [a.sd, "--diffusion-model", os.path.join(a.models, "z_image_turbo-Q4_K.gguf"),
           "--vae", os.path.join(a.models, "ae.safetensors"),
           "--llm", os.path.join(a.models, "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"),
           "-p", s["prompt"], "--cfg-scale", "1.0", "--steps", "8", "-W", "1024", "-H", "576",
           "-s", a.seed, "-t", "2", "--vae-tiling", "--mmap", "-o", out + ".tmp.png"]
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and os.path.exists(out + ".tmp.png"):
        os.replace(out + ".tmp.png", out)
        print(f"{s['id']}: ok {time.time() - t:.0f}s", flush=True)
    else:
        print(f"{s['id']}: FAILED rc={r.returncode}\n{r.stderr[-800:]}", flush=True)
