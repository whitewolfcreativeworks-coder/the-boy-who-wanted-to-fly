"""Synthesize every screenplay line with Kokoro TTS and write a timing manifest.

Usage: python3 src/narrate.py [--models DIR] [--out build/audio/lines]
Output: one WAV per beat (24 kHz mono) + build/audio/lines/manifest.json
"""
import argparse, json, os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "script"))
from screenplay import SCENES, VOICES
from kokoro_onnx import Kokoro

ap = argparse.ArgumentParser()
ap.add_argument("--models", default=os.path.expanduser("~/models"))
ap.add_argument("--out", default="build/audio/lines")
ap.add_argument("--only", type=int, nargs="*")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
k = Kokoro(os.path.join(a.models, "kokoro-v1.0.onnx"), os.path.join(a.models, "voices-v1.0.bin"))

def style(spec):
    if ":" not in spec: return spec
    v = None
    for part in spec.split(","):
        n, w = part.split(":"); s = k.get_voice_style(n) * float(w)
        v = s if v is None else v + s
    return v

def pitch(path, p):
    if abs(p - 1) < 1e-3: return
    tmp = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-af",
        f"asetrate={int(24000*p)},aresample=24000,atempo={1/p:.5f}", tmp], check=True)
    os.replace(tmp, path)

manifest_path = os.path.join(a.out, "manifest.json")
manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
for sc in SCENES:
    if a.only and sc["id"] not in a.only: continue
    for i, (spk, text, tag, pause) in enumerate(sc["beats"]):
        key = f"s{sc['id']:02d}_{i:02d}_{tag}"
        path = os.path.join(a.out, key + ".wav")
        v = VOICES[spk]
        audio, sr = k.create(text, voice=style(v["voice"]), speed=v["speed"], lang="en-us")
        # gentle fades to avoid clicks
        f = int(sr * 0.01); audio[:f] *= np.linspace(0, 1, f); audio[-f:] *= np.linspace(1, 0, f)
        sf.write(path, audio, sr)
        pitch(path, v["pitch"])
        d = sf.info(path).duration
        manifest[key] = {"scene": sc["id"], "idx": i, "speaker": spk, "tag": tag, "text": text, "dur": round(d, 3), "pause": pause}
        print(key, round(d, 2), flush=True)
        json.dump(manifest, open(manifest_path, "w"), indent=1)
