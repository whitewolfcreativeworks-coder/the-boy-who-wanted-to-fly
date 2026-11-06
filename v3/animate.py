"""Version 3 animation engine: brings each key image to life as a 2.5D shot.

A depth map (Depth Anything V2 Small, Apache-2.0, ONNX on CPU) splits every
image into near and far; the virtual camera then pushes, pans, rises or flies
with real parallax (near things move more than far ones), characters in flight
bob on the air, and atmospheric layers (falling leaves, dust motes, sparkles,
heart glow, speed streaks) are drawn on top. Timing comes from Version 1's
narration manifest, so picture, voice, music and sound effects stay in sync.

    python3 v3/animate.py --scenes 1 2 ...   -> build/v3/scenes/sNN.mp4
    python3 v3/animate.py --still s02c 0.5    -> one frame for review
"""
import argparse, math, os, subprocess, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "src"))
from edit import PLAN

W, H, FPS = 1920, 1080, 24
BUILD = os.path.join(ROOT, "build", "v3")
KEYS = os.environ.get("V3_KEYFRAMES", os.path.join(BUILD, "keyframes"))
DEPTH_MODEL = os.environ.get("V3_DEPTH_MODEL", os.path.expanduser("~/models/depth_anything_v2_small.onnx"))
XFADE = 0.7        # cross-dissolve between shots (s)
DIP = 0.45         # dip to black at scene edges (s)


# ------------------------------------------------------------------ timing
def scene_timing(sid, manifest):
    """Scene duration and beat start/end, using Version 1's timing rules (render.Ctx)."""
    from render import Ctx
    c = Ctx(sid, manifest)
    return c


def frame_count(sid, dur):
    """Frames for scene `sid`, taken from the soundtrack's cumulative offsets so the
    picture never drifts from the audio (no per-scene rounding error)."""
    import json
    p = os.path.join(ROOT, "build", "audio", "offsets.json")
    if os.path.exists(p):
        o = json.load(open(p)); nxt = o.get(str(sid + 1), o["total"])
        return int(round(nxt * FPS)) - int(round(o[str(sid)] * FPS))
    return int(round(dur * FPS))


def at_time(ctx, spec):
    tag, _, frac = spec.partition("+")
    b = ctx.b(tag)
    return b.start + (float(frac) if frac else 0.0) * (b.end - b.start)


def scene_shots(sid, ctx):
    """[(shot_id, start, end, cam, fx)] for shots whose key image exists."""
    rows = [(sid_, at_time(ctx, spec), cam, fx) for sid_, spec, cam, fx in PLAN[sid]
            if os.path.exists(os.path.join(KEYS, sid_ + ".png"))]
    if not rows:
        return []
    rows[0] = (rows[0][0], 0.0, rows[0][2], rows[0][3])
    out = []
    for i, (k, st, cam, fx) in enumerate(rows):
        en = rows[i + 1][1] if i + 1 < len(rows) else ctx.dur
        out.append((k, st, en, cam, fx))
    return out


# ------------------------------------------------------------------ assets
_depth_sess = None


def depth_map(img):
    global _depth_sess
    import onnxruntime as ort
    if _depth_sess is None:
        so = ort.SessionOptions(); so.intra_op_num_threads = 2
        _depth_sess = ort.InferenceSession(DEPTH_MODEL, so)
    x = cv2.resize(img, (518, 294), interpolation=cv2.INTER_AREA)[:, :, ::-1].astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    d = _depth_sess.run(None, {"pixel_values": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    lo, hi = np.percentile(d, 2), np.percentile(d, 98)
    d = np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)
    d = cv2.GaussianBlur(d, (0, 0), 2.0)
    return cv2.resize(d, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)


def load_shot(k):
    """Upscaled image (float32 BGR 0..1) and smoothed depth (1 = near), cached."""
    cache = os.path.join(BUILD, "cache"); os.makedirs(cache, exist_ok=True)
    src = cv2.imread(os.path.join(KEYS, k + ".png"))
    img = cv2.resize(src, (W, H), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(img, (0, 0), 1.2)
    img = cv2.addWeighted(img, 1.35, blur, -0.35, 0)            # gentle sharpen after upscale
    dp = os.path.join(cache, k + "_depth.npy")
    if os.path.exists(dp) and os.path.getmtime(dp) > os.path.getmtime(os.path.join(KEYS, k + ".png")):
        d = np.load(dp)
    else:
        d = depth_map(src); np.save(dp, d)
    return img.astype(np.float32) / 255, d


# ------------------------------------------------------------------ camera
def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def camera(cam, u, t):
    """zoom, pan (x, y in fraction of frame), parallax translation (x, y), dolly, bob."""
    e = ease(u)
    z, px, py, tx, ty, dolly, bob = 1.06, 0, 0, 0, 0, 0, 0
    if cam == "push":
        z = 1.05 + 0.09 * e; dolly = 0.045 * e; tx = 0.008 * e
    elif cam == "pull":
        z = 1.15 - 0.09 * e; dolly = 0.045 * (1 - e); tx = -0.008 * e
    elif cam == "pan_l":
        z = 1.10; px = 0.035 - 0.07 * e; tx = 0.014 - 0.028 * e
    elif cam == "pan_r":
        z = 1.10; px = -0.035 + 0.07 * e; tx = -0.014 + 0.028 * e
    elif cam == "rise":
        z = 1.10 + 0.03 * e; py = 0.035 - 0.07 * e; ty = 0.012 - 0.024 * e
    elif cam == "sink":
        z = 1.10 + 0.03 * e; py = -0.035 + 0.07 * e; ty = -0.012 + 0.024 * e
    elif cam == "drift":
        z = 1.07 + 0.04 * e; px = -0.012 + 0.024 * e; tx = -0.015 + 0.03 * e; dolly = 0.03 * e
    elif cam == "float":
        z = 1.09 + 0.03 * e; tx = 0.02 * math.sin(t * 0.6); dolly = 0.03 * e; bob = 1.0
    elif cam == "fly":
        z = 1.08 + 0.07 * e; px = 0.02 * math.sin(t * 0.35); tx = -0.025 + 0.05 * e; dolly = 0.06 * e; bob = 1.4
    elif cam == "zigzag":
        z = 1.12; zz = math.sin(t * 2.2); px = 0.02 * np.sign(zz) * abs(zz) ** 0.3; tx = 0.04 * px / 0.02; bob = 0.6
    elif cam == "zoomfast":
        z = 1.05 + 0.18 * u ** 2; dolly = 0.12 * u ** 2; bob = 0.8
    return z, px, py, tx, ty, dolly, bob


_grid = None


def warp(img, d, cam, u, t):
    global _grid
    if _grid is None:
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        _grid = ((xs - W / 2) / W, (ys - H / 2) / W)            # normalized, aspect-correct (by width)
    gx, gy = _grid
    z, px, py, tx, ty, dolly, bob = camera(cam, u, t)
    near = d - 0.45                                           # >0 in front of the focal plane
    s = z * (1 + dolly * near)                                # near layers grow more when dollying in
    by = 0.0035 * bob * math.sin(t * 1.7) * np.clip(d - 0.35, 0, None) * 2.2   # foreground bobs on the air
    breathe = 1 + 0.0025 * math.sin(t * 2.1) * np.clip(d - 0.55, 0, None)      # subtle life in near subjects
    sx = gx / (s * breathe) + px - tx * near
    sy = gy / (s * breathe) + py - ty * near - by
    mapx = sx * W + W / 2; mapy = sy * W + H / 2
    return cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ------------------------------------------------------------------ effects
LEAF_COLS = [(40, 70, 210), (30, 110, 230), (40, 150, 235), (60, 60, 170), (90, 140, 200), (50, 90, 190)]


def leaf_poly(cx, cy, r, ang):
    pts = []
    for i in range(14):
        a = i / 14 * 2 * math.pi
        rr = r * (1.0 if i % 2 == 0 else 0.82) * (1.35 if i == 0 else 1.0)
        pts.append((cx + rr * math.cos(a + ang), cy + rr * 0.8 * math.sin(a + ang)))
    return np.array(pts, np.int32)


def fx_leaves(frame, t, seed, n=26):
    rng = np.random.default_rng(seed)
    ov = np.zeros_like(frame); al = np.zeros(frame.shape[:2], np.float32)
    big = np.zeros_like(frame); bal = np.zeros(frame.shape[:2], np.float32)
    for i in range(n):
        x0, sp, r, ph, col = rng.uniform(-0.1, 1.1), rng.uniform(0.05, 0.12), rng.uniform(7, 22), rng.uniform(0, 99), LEAF_COLS[i % 6]
        y = ((ph * 0.37 + t * sp) % 1.25 - 0.12) * H
        x = (x0 + 0.04 * math.sin(t * 1.3 + ph) + t * 0.012) % 1.2 * W - 0.1 * W
        target, a = (big, bal) if r > 17 else (ov, al)
        poly = leaf_poly(x, y, r, t * 1.6 + ph)
        cv2.fillPoly(target, [poly], tuple(c / 255 for c in col), cv2.LINE_AA)
        cv2.fillPoly(a, [poly], 0.92, cv2.LINE_AA)
    big = cv2.GaussianBlur(big, (0, 0), 3); bal = cv2.GaussianBlur(bal, (0, 0), 3)   # out-of-focus foreground leaves
    frame = frame * (1 - al[..., None]) + ov
    return frame * (1 - bal[..., None]) + big


def fx_points(frame, t, seed, n, col, size, speed, twinkle):
    rng = np.random.default_rng(seed)
    ov = np.zeros(frame.shape[:2], np.float32)
    for i in range(n):
        x = (rng.uniform(0, 1) + speed * t * rng.uniform(-1, 1)) % 1 * W
        y = (rng.uniform(0, 1) - speed * t * rng.uniform(0.3, 1)) % 1 * H
        b = 0.5 + 0.5 * math.sin(t * twinkle * rng.uniform(0.5, 1.5) + rng.uniform(0, 6.28))
        cv2.circle(ov, (int(x), int(y)), int(rng.uniform(1, size)), float(b), -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(ov, (0, 0), 3) * 1.6 + cv2.GaussianBlur(ov, (0, 0), 1)
    return frame + glow[..., None] * np.array(col, np.float32) * 0.5


def fx_glow(frame, t, strength=0.22):
    pulse = 0.65 + 0.35 * math.sin(t * 2.4)
    yy, xx = np.ogrid[0:H, 0:W]
    r = np.sqrt(((xx - W * 0.5) / (W * 0.45)) ** 2 + ((yy - H * 0.5) / (H * 0.55)) ** 2)
    g = np.clip(1 - r, 0, 1) ** 2 * strength * pulse
    return frame + g[..., None] * np.array([0.35, 0.75, 1.0], np.float32)


def fx_speed(frame, t, seed):
    rng = np.random.default_rng(seed)
    ov = np.zeros(frame.shape[:2], np.float32)
    for i in range(28):
        y = int(rng.uniform(0, H)); ln = rng.uniform(120, 420)
        x = ((rng.uniform(0, 1) - t * rng.uniform(0.6, 1.4)) % 1.3) * W - 0.15 * W
        cv2.line(ov, (int(x), y), (int(x + ln), y), float(rng.uniform(0.25, 0.6)), 2, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 1.5)
    return frame + ov[..., None] * 0.45


def fx_splash(frame, t, u):
    """Burst of leaves flying up at the start of the leaf-pile shot."""
    if u > 0.55:
        return frame
    k = u / 0.55
    rng = np.random.default_rng(5)
    for i in range(60):
        ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05); sp = rng.uniform(0.25, 0.75)
        x = W * 0.5 + math.cos(ang) * sp * W * 0.55 * k
        y = H * 0.62 + math.sin(ang) * sp * H * 0.9 * k + 0.9 * H * k * k
        poly = leaf_poly(x, y, rng.uniform(8, 20), t * 4 + i)
        a = np.zeros(frame.shape[:2], np.float32); cv2.fillPoly(a, [poly], 1.0, cv2.LINE_AA)
        c = np.array(LEAF_COLS[i % 6], np.float32) / 255 * (1 - k * 0.3)
        frame = frame * (1 - a[..., None] * (1 - k)) + a[..., None] * (1 - k) * c
    return frame


def apply_fx(frame, fx, t, u, seed):
    for f in fx:
        if f == "leaves":
            frame = fx_leaves(frame, t, seed)
        elif f == "motes":
            frame = fx_points(frame, t, seed, 45, (0.55, 0.85, 1.0), 3, 0.015, 1.0)
        elif f == "sparkle":
            frame = fx_points(frame, t, seed, 70, (1.0, 0.95, 0.85), 3, 0.01, 3.0)
        elif f == "bubbles":
            frame = fx_points(frame, t, seed + 1, 18, (1.0, 0.9, 0.8), 6, 0.04, 0.8)
        elif f == "honey":
            frame = fx_points(frame, t, seed, 30, (0.3, 0.75, 1.0), 4, 0.006, 0.6)
        elif f == "glow":
            frame = fx_glow(frame, t)
        elif f == "speed":
            frame = fx_speed(frame, t, seed)
        elif f == "splash":
            frame = fx_splash(frame, t, u)
        elif f == "wind":
            frame = fx_leaves(frame, t * 2.5, seed, n=18)
    return frame


def finish(frame):
    """Vignette + very light grain, to bind every shot into one film look."""
    global _vig
    if "_vig" not in globals():
        yy, xx = np.ogrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _vig = (1 - 0.22 * np.clip(r - 0.35, 0, None) ** 1.5)[..., None].astype(np.float32)
    return frame * _vig


# ------------------------------------------------------------------ render
def shot_frame(k, cache, cam, fx, st, en, t, seed):
    img, d = cache[k]
    u = (t - st) / max(en - st, 1e-3)
    f = warp(img, d, cam, u, t)
    return apply_fx(f, fx, t - st, u, seed)


def render_scene(sid, manifest, out):
    ctx = scene_timing(sid, manifest)
    shots = scene_shots(sid, ctx)
    if not shots:
        print(f"scene {sid}: no key images yet"); return False
    cache = {k: load_shot(k) for k, *_ in shots}
    n = frame_count(sid, ctx.dur)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in range(n):
        t = fi / FPS
        i = max(j for j, s in enumerate(shots) if s[1] <= t + 1e-6)
        k, st, en, cam, fx = shots[i]
        frame = shot_frame(k, cache, cam, fx, st, en + XFADE, t, sid * 100 + i)
        if i + 1 < len(shots) and t > en - XFADE / 2:          # dissolve into the next shot
            k2, st2, en2, cam2, fx2 = shots[i + 1]
            w = (t - (en - XFADE / 2)) / XFADE
            frame = frame * (1 - w) + w * shot_frame(k2, cache, cam2, fx2, st2 - XFADE / 2, en2, t, sid * 100 + i + 1)
        if i > 0 and t < st + XFADE / 2:
            k0, st0, en0, cam0, fx0 = shots[i - 1]
            w = 0.5 - (t - st) / XFADE
            frame = frame * (1 - w) + w * shot_frame(k0, cache, cam0, fx0, st0, en0 + XFADE, t, sid * 100 + i - 1)
        frame = finish(frame)
        dip = min(1.0, t / DIP, (ctx.dur - t) / DIP)
        frame = frame * max(dip, 0)
        p.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    print(f"scene {sid}: {len(shots)} shots, {ctx.dur:.1f}s -> {out}", flush=True)
    return True


def main():
    import json
    from render import load_manifest
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", type=int, nargs="*", default=list(range(1, 18)))
    ap.add_argument("--still", nargs=2, metavar=("SHOT", "U"))
    a = ap.parse_args()
    man = load_manifest()
    if a.still:
        k, u = a.still[0], float(a.still[1])
        sid = int(k[1:3]); ctx = scene_timing(sid, man)
        row = next(s for s in scene_shots(sid, ctx) if s[0] == k)
        cache = {k: load_shot(k)}
        t = row[1] + u * (row[2] - row[1])
        f = finish(shot_frame(k, cache, row[3], row[4], row[1], row[2], t, 1))
        out = os.path.join(BUILD, "stills", f"{k}_{u:.2f}.jpg"); os.makedirs(os.path.dirname(out), exist_ok=True)
        cv2.imwrite(out, (np.clip(f, 0, 1) * 255).astype(np.uint8)); print(out)
        return
    for sid in a.scenes:
        render_scene(sid, man, os.path.join(BUILD, "scenes", f"s{sid:02d}.mp4"))


if __name__ == "__main__":
    main()
