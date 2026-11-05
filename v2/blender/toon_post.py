"""Cel-shade + ink a Cycles pass EXR written by `style_test.py --style toon`.

    python3 toon_post.py IN.exr OUT.png

Light is quantised into three bands (cool violet shadow, warm half-tone, lit),
multiplied by the flat albedo; emission/sky/translucency pass through. Ink lines
come from object-index, depth and normal discontinuities, only on the character
and architecture (pass_index > 0), so the leaf carpet stays line-free.
"""
import sys
import cv2
import numpy as np
import OpenEXR

inp, out = sys.argv[1], sys.argv[2]
f = OpenEXR.File(inp, separate_channels=True)
ch = {}
for p in f.parts:
    for k, v in p.channels.items():
        ch[k.replace("ViewLayer.", "")] = v.pixels.astype(np.float32)


def rgb(name):
    return np.stack([ch[f"{name}.R"], ch[f"{name}.G"], ch[f"{name}.B"]], -1)


def lum(x):
    return x @ np.array([0.2126, 0.7152, 0.0722], np.float32)


dcol = rgb("Diffuse Color")
light = rgb("Diffuse Direct") + rgb("Diffuse Indirect")
irr = lum(light) / np.maximum(lum(dcol), 1e-4)
emit = rgb("Emission") if "Emission.R" in ch else 0
env = rgb("Environment") if "Environment.R" in ch else 0
trans = rgb("Transmission Direct") + rgb("Transmission Indirect")

lit_ref = np.percentile(irr[lum(dcol) > 0.01], 92)          # "fully lit" level in this frame
t = irr / max(lit_ref, 1e-4)
shadow = np.array([0.42, 0.40, 0.62], np.float32)            # cool violet
half = np.array([0.78, 0.66, 0.70], np.float32)
lit = np.array([1.06, 0.98, 0.88], np.float32)
band = np.where((t < 0.28)[..., None], shadow, np.where((t < 0.62)[..., None], half, lit))
# soften band edges by one pixel so they don't alias
band = cv2.GaussianBlur(band, (0, 0), 0.7)
base = dcol * band * 0.92
img = base + emit + env + trans * 0.6

# display transform: exposure + gentle shoulder + sRGB
img = img * 1.05
img = img / (1 + 0.25 * img)
img = np.clip(img, 0, 1) ** (1 / 2.2)

# ---- ink
idx = ch["Object Index.X"]
z = ch["Depth.Z"]
n = np.stack([ch["Normal.X"], ch["Normal.Y"], ch["Normal.Z"]], -1)
inked = idx > 0.5


def diff_any(a, thr):
    dx = np.abs(np.diff(a, axis=1, append=a[:, -1:]))
    dy = np.abs(np.diff(a, axis=0, append=a[-1:, :]))
    return (dx > thr) | (dy > thr)


e_idx = diff_any(idx, 0.5)
zl = np.log(np.maximum(z, 1e-3))
e_z = diff_any(zl, 0.035)
nd = np.zeros(idx.shape, bool)
for ax in (0, 1):
    n2 = np.roll(n, -1, axis=ax)
    nd |= (np.sum(n * n2, -1) < 0.55)
near_inked = cv2.dilate(inked.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
ink = (e_idx | e_z | (nd & inked)) & near_inked
ink = cv2.GaussianBlur(ink.astype(np.float32), (0, 0), 0.6)
ink = np.clip(ink * 1.6, 0, 1)[..., None]
ink_col = np.array([0.20, 0.13, 0.10], np.float32)
img = img * (1 - ink * 0.85) + ink_col * ink * 0.85

cv2.imwrite(out, (np.clip(img, 0, 1)[..., ::-1] * 255).astype(np.uint8))
print("TOON ->", out, "lit_ref", round(float(lit_ref), 3))
