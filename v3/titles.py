"""Opening title (9 s, over the establishing shot) and scrolling credits (26 s, over the dream sky).
Durations match Version 1's soundtrack timing (render.FIXED).

    python3 v3/titles.py   -> build/v3/scenes/s00.mp4, s18.mp4
"""
import os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import animate as A

FONTS = os.path.join(A.ROOT, "assets", "fonts")
STYLE = {"title": ("Fredoka-700.ttf", 92, (255, 246, 230), 150), "head": ("Nunito-600.ttf", 34, (255, 208, 224), 52),
         "name": ("Fredoka-600.ttf", 52, (255, 246, 230), 84), "small": ("Nunito-600.ttf", 32, (232, 216, 255), 64),
         "gap": (None, 0, None, 70)}
CREDITS = [
    ("title", "The Boy Who Wanted to Fly"), ("gap", ""),
    ("head", "Story"), ("name", "Jason Whitewolf"), ("small", "© 2018 Jason Whitewolf. All rights reserved."), ("gap", ""),
    ("head", "Animated adaptation"), ("name", "Produced with Claude (Anthropic)"), ("small", "for Jason Whitewolf"), ("gap", ""),
    ("head", "Images"), ("name", "Z-Image Turbo  ·  Apache-2.0"),
    ("head", "Depth & 2.5D animation"), ("name", "Depth Anything V2  ·  OpenCV"),
    ("head", "Narration & voices"), ("name", "Kokoro TTS  ·  Apache-2.0"),
    ("head", "Music & sound"), ("name", "Original procedural score"),
    ("head", "Fonts"), ("name", "Fredoka & Nunito  ·  SIL Open Font License"),
    ("head", "Assembly"), ("name", "FFmpeg"), ("gap", ""),
    ("small", "Keep practicing — and never give up on your dream."), ("gap", ""), ("gap", ""),
    ("name", "Sweet dreams."),
]


def text_layer(lines, width=A.W, glow=True):
    """Render [(kind, text)] centred, top to bottom, into an RGBA float array."""
    h = sum(STYLE[k][3] for k, _ in lines) + 200
    img = Image.new("RGBA", (width, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = 100
    for kind, s in lines:
        font, size, col, gap = STYLE[kind]
        if font:
            f = ImageFont.truetype(os.path.join(FONTS, font), size)
            d.text((width / 2, y), s, font=f, fill=col + (255,), anchor="mm")
        y += gap
    a = np.asarray(img).astype(np.float32) / 255
    if glow:   # soft dark halo so text reads over any image
        sh = np.asarray(img.split()[3].filter(ImageFilter.GaussianBlur(10))).astype(np.float32) / 255
        return a, sh
    return a, None


def comp(frame, layer, shadow, y0, alpha=1.0):
    rgba = layer; Hh = frame.shape[0]
    top, bot = max(0, y0), min(Hh, y0 + rgba.shape[0])
    if bot <= top:
        return frame
    sl = rgba[top - y0:bot - y0]; sh = shadow[top - y0:bot - y0]
    region = frame[top:bot]
    region = region * (1 - 0.55 * sh[..., None] * alpha)
    a = sl[..., 3:4] * alpha
    region = region * (1 - a) + sl[..., 2::-1] * a          # RGB -> BGR
    frame[top:bot] = region
    return frame


def writer(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s",
                             f"{A.W}x{A.H}", "-r", str(A.FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                             "-crf", "18", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)


def pick(*ids):
    return next(k for k in ids if os.path.exists(os.path.join(A.KEYS, k + ".png")))


def title(dur=9.0):
    k = pick("s01a", "s02a"); cache = {k: A.load_shot(k)}
    lay, sh = text_layer([("title", "The Boy Who Wanted to Fly"), ("gap", ""), ("head", "Story by"), ("name", "Jason Whitewolf")])
    p = writer(os.path.join(A.BUILD, "scenes", "s00.mp4"))
    for fi in range(int(dur * A.FPS)):
        t = fi / A.FPS
        f = A.finish(A.shot_frame(k, cache, "rise", ["leaves"], 0, dur, t, 7))
        f = f * (0.78 + 0.22 * min(1, t / 2))
        a = min(1, max(0, (t - 1.2) / 1.2)) * min(1, max(0, (dur - 0.8 - t) / 1.0))
        f = comp(f, lay, sh, int(A.H * 0.36 - lay.shape[0] / 2 + 40), a)
        f *= min(1, t / 0.8, (dur - t) / 0.6)
        p.stdin.write((np.clip(f, 0, 1) * 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait(); print("title done")


def credits(dur=26.0):
    k = pick("s15e", "s17a", "s15d"); cache = {k: A.load_shot(k)}
    lay, sh = text_layer(CREDITS)
    p = writer(os.path.join(A.BUILD, "scenes", "s18.mp4"))
    y_last = lay.shape[0] - 100 - STYLE["name"][3]          # where "Sweet dreams." sits in the layer
    y_end = A.H / 2 - y_last                                  # ...ends centred on screen
    for fi in range(int(dur * A.FPS)):
        t = fi / A.FPS
        f = A.finish(A.shot_frame(k, cache, "float", ["sparkle"], 0, dur, t, 9)) * 0.62
        y = int(A.H + (y_end - A.H) * min(1.0, t / (dur - 3.5)))
        f = comp(f, lay, sh, y)
        f *= min(1, t / 0.6, (dur - t) / 1.2)
        p.stdin.write((np.clip(f, 0, 1) * 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait(); print("credits done")


if __name__ == "__main__":
    title(); credits()
