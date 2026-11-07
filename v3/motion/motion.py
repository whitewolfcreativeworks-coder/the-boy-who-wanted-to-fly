"""Controller for the motion pass (runs here, needs only network access to huggingface.co).

    export HF_TOKEN=...                      # the author's token, never written to disk or git
    python3 v3/motion/motion.py plan                       # show segments and a cost estimate
    python3 v3/motion/motion.py prepare USER/REPO          # private dataset repo + keyframes + plan + job script
    python3 v3/motion/motion.py submit  USER/REPO [--only s02a] [--max 1] [--flavor a100-large] [--timeout 6h]
    python3 v3/motion/motion.py watch   JOB_ID             # stream logs until it ends
    python3 v3/motion/motion.py fetch   USER/REPO          # download clips -> build/v3/clips/
    python3 v3/motion/motion.py cancel  JOB_ID
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.dirname(HERE)
ROOT = os.path.dirname(V3)
sys.path.insert(0, V3)
from motion_prompts import MOTION, NEG
from shots import SHOTS

IMAGE = "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel"
DEPS = "diffusers>=0.35 transformers accelerate peft ftfy sentencepiece imageio imageio-ffmpeg huggingface_hub>=0.34"
SEC_PER_SEG = {"a100-large": 150, "l40sx1": 240, "h200": 90}     # rough guesses until the test shot measures it
PRICE = {"a100-large": 2.50, "l40sx1": 1.80, "h200": 5.00}


def segments():
    out = []
    for i, s in enumerate(SHOTS):
        m = MOTION[s["id"]]
        m = m if isinstance(m, list) else [m]
        for j, p in enumerate(m):
            out.append({"shot": s["id"], "seg": j, "of": len(m), "prompt": p, "seed": 1000 + 10 * i + j})
    return out


def cmd_plan(a):
    seg = segments()
    print(f"{len(SHOTS)} shots, {len(seg)} segments of 81 frames (5.06 s at 16 fps) = {len(seg) * 81 / 16 / 60:.1f} min of motion")
    for f in SEC_PER_SEG:
        h = len(seg) * SEC_PER_SEG[f] / 3600 + 0.3      # + model download/load
        print(f"  {f:11s} ~{h:4.1f} h  ~${h * PRICE[f]:5.2f}  (estimate)")


def cmd_prepare(a):
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", private=True, exist_ok=True)
    plan = {"negative": NEG, "segments": segments()}
    p = os.path.join(ROOT, "build", "v3", "motion_plan.json"); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(plan, open(p, "w"), indent=1)
    api.upload_file(path_or_fileobj=p, path_in_repo="plan.json", repo_id=a.repo, repo_type="dataset")
    api.upload_file(path_or_fileobj=os.path.join(HERE, "motion_job.py"), path_in_repo="motion_job.py",
                    repo_id=a.repo, repo_type="dataset")
    api.upload_folder(folder_path=os.path.join(V3, "keyframes"), path_in_repo="keyframes", repo_id=a.repo,
                      repo_type="dataset", allow_patterns=["*.jpg"])
    print(f"prepared https://huggingface.co/datasets/{a.repo} (private)")


def cmd_submit(a):
    from huggingface_hub import run_job
    env = {"MOTION_REPO": a.repo, "ONLY": a.only or "", "MAX_SEGMENTS": str(a.max or 0),
           "HF_HUB_ENABLE_HF_TRANSFER": "0"}
    boot = ("pip install -q " + DEPS + " && python -c \"from huggingface_hub import hf_hub_download as d; "
            f"exec(open(d('{a.repo}','motion_job.py',repo_type='dataset')).read())\"")
    job = run_job(image=IMAGE, command=["bash", "-c", boot], flavor=a.flavor, timeout=a.timeout,
                  env=env, secrets={"HF_TOKEN": os.environ["HF_TOKEN"]})
    print("JOB", job.id, job.url)


def cmd_watch(a):
    from huggingface_hub import fetch_job_logs, inspect_job
    for line in fetch_job_logs(job_id=a.job):
        print(line, flush=True)
    print("STATUS", inspect_job(job_id=a.job).status.stage)


def cmd_cancel(a):
    from huggingface_hub import cancel_job
    cancel_job(job_id=a.job); print("cancelled", a.job)


def cmd_fetch(a):
    from huggingface_hub import snapshot_download
    out = os.path.join(ROOT, "build", "v3", "clips_repo")
    snapshot_download(a.repo, repo_type="dataset", allow_patterns=["clips/*.mp4"], local_dir=out)
    n = len([f for f in os.listdir(os.path.join(out, "clips")) if f.endswith(".mp4")])
    print(f"{n} clips in {out}/clips")


ap = argparse.ArgumentParser()
sp = ap.add_subparsers(dest="cmd", required=True)
sp.add_parser("plan")
for c in ("prepare", "fetch"):
    sp.add_parser(c).add_argument("repo")
s = sp.add_parser("submit"); s.add_argument("repo"); s.add_argument("--only"); s.add_argument("--max", type=int)
s.add_argument("--flavor", default="a100-large"); s.add_argument("--timeout", default="6h")
for c in ("watch", "cancel"):
    sp.add_parser(c).add_argument("job")
a = ap.parse_args()
globals()["cmd_" + a.cmd](a)
