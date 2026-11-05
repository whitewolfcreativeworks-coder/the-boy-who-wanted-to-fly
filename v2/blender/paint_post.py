"""Painterly post pass on a rendered frame (OpenCV, CPU, ~seconds per frame).

    python3 paint_post.py IN.png OUT.png [--lift 1.18]

Brush-stroke abstraction (oil-paint filter + edge-preserving stylization), soft
paper grain and a gentle vignette. A stand-in for Blender's Kuwahara compositor
node or a GPU AI restyle; it shows the direction, not the final quality.
"""
import argparse
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--lift", type=float, default=1.3)
a = ap.parse_args()

img = cv2.imread(a.inp, cv2.IMREAD_COLOR)
f = img.astype(np.float32) / 255.0
f = np.clip(f ** (1 / a.lift), 0, 1)                     # gentle exposure lift
img = (f * 255).astype(np.uint8)

paint = cv2.xphoto.oilPainting(img, 3, 1)               # small brush clumping
paint = cv2.edgePreservingFilter(paint, flags=cv2.RECURS_FILTER, sigma_s=12, sigma_r=0.25)
paint = cv2.addWeighted(paint, 0.65, img, 0.35, 0)        # keep faces and detail readable

h, w = paint.shape[:2]
rng = np.random.default_rng(3)
grain = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.2)
grain = (grain / grain.std()) * 0.025
yy, xx = np.mgrid[0:h, 0:w]
vig = 1 - 0.18 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.4
p = paint.astype(np.float32) / 255.0
p = np.clip(p * (1 + grain)[..., None] * vig[..., None], 0, 1)
cv2.imwrite(a.out, (p * 255).astype(np.uint8))
print("PAINT ->", a.out)
