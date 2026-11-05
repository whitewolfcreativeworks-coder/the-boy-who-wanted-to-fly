"""Scene renderer: timing from the narration manifest, frames piped to FFmpeg.

  python3 src/render.py --scenes 1 2 3          # render scene clips to build/scenes
  python3 src/render.py --all --jobs 2          # everything, in parallel
  python3 src/render.py --still 7 12.5          # one PNG for review
  python3 src/render.py --contact 7             # contact sheet of a scene
"""
import argparse, json, math, os, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
import skia
sys.path.insert(0, os.path.dirname(__file__))
from engine import *

BUILD = os.path.join(ROOT, "build")
MANIFEST = os.path.join(BUILD, "audio", "lines", "manifest.json")

LEAD = {1: 1.6, 10: 1.4, 12: 1.5, 14: 0.8, 15: 1.0, 16: 0.8}
TAIL = {7: 1.5, 8: 1.2, 9: 1.4, 14: 1.6, 15: 2.4, 16: 2.0, 17: 1.0}
FADE = {}  # per-scene fade colour overrides
FIXED = {0: 9.0, 18: 26.0}  # title / credits durations

class Beat:
    def __init__(self, d, start):
        self.__dict__.update(d); self.start = start; self.end = start + d["dur"]

class Ctx:
    def __init__(self, sid, manifest=None):
        self.sid = sid; self.t = 0.0; self.beats = []
        if sid in FIXED:
            self.dur = FIXED[sid]; return
        items = sorted([v for v in manifest.values() if v["scene"] == sid], key=lambda v: v["idx"])
        cur = LEAD.get(sid, 0.9)
        for v in items:
            b = Beat(v, cur); self.beats.append(b); cur = b.end + v["pause"]
        self.dur = cur + TAIL.get(sid, 0.8)
        self.tags = {b.tag: b for b in self.beats}
    def b(self, tag): return self.tags[tag]
    def s(self, tag): return self.tags[tag].start
    def e(self, tag): return self.tags[tag].end
    def u(self, tag, f=lambda x: x):
        bt = self.tags[tag]; return f(inv(bt.start, bt.end, self.t))
    def since(self, tag): return self.t - self.tags[tag].start
    def at(self, tag, off=0.0): return self.t >= self.tags[tag].start + off
    def talking(self, spk):
        return any(b.speaker == spk and b.start <= self.t <= b.end for b in self.beats)
    def mouth(self, spk, default="smile"):
        return "talk" if self.talking(spk) else default
    def phase(self, tags):
        """Name of the latest tag that has started."""
        cur = None
        for tg in tags:
            if self.t >= self.tags[tg].start: cur = tg
        return cur

def load_manifest():
    return json.load(open(MANIFEST))

def scene_fn(sid):
    import scenes
    return getattr(scenes, f"scene_{sid:02d}")

def draw_frame(c, sid, ctx):
    c.save()
    scene_fn(sid)(c, ctx)
    c.restore()
    # page-turn dips
    fc = FADE.get(sid, "#000000")
    fade(c, 1 - ramp(ctx.t, 0, .45), fc)
    fade(c, ramp(ctx.t, ctx.dur - .45, ctx.dur), fc)

def render_scene(sid):
    manifest = load_manifest()
    ctx = Ctx(sid, manifest)
    os.makedirs(os.path.join(BUILD, "scenes"), exist_ok=True)
    out = os.path.join(BUILD, "scenes", f"s{sid:02d}.mp4")
    n = int(round(ctx.dur * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-threads", "1", out], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    t0 = time.time()
    for i in range(n):
        ctx.t = i / FPS
        c.clear(skia.ColorBLACK)
        draw_frame(c, sid, ctx)
        ff.stdin.write(surf.makeImageSnapshot().tobytes())
    ff.stdin.close(); ff.wait()
    dt = time.time() - t0
    print(f"scene {sid:02d}: {n} frames, {ctx.dur:.1f}s, {dt:.0f}s wall ({1000*dt/max(n,1):.0f} ms/frame)", flush=True)
    return sid, ctx.dur

def still(sid, t, out=None):
    ctx = Ctx(sid, load_manifest() if sid not in FIXED else None); ctx.t = t
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK)
    draw_frame(c, sid, ctx)
    out = out or os.path.join(BUILD, "stills", f"s{sid:02d}_{t:06.2f}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    surf.makeImageSnapshot().save(out, skia.kPNG); return out

def contact(sid, n=12, out=None):
    ctx = Ctx(sid, load_manifest() if sid not in FIXED else None)
    cols = 4; rows = math.ceil(n / cols); tw, th = W // cols, H // cols
    sheet = skia.Surface(tw * cols, th * rows); sc = sheet.getCanvas(); sc.clear(skia.ColorBLACK)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    for k in range(n):
        ctx.t = (k + .5) / n * ctx.dur
        c.clear(skia.ColorBLACK); draw_frame(c, sid, ctx)
        img = surf.makeImageSnapshot()
        x, y = (k % cols) * tw, (k // cols) * th
        sc.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw, th), skia.SamplingOptions(skia.FilterMode.kLinear))
        text(sc, f"{ctx.t:.1f}s", x + 40, y + 30, 22, "#ffff80", shadow=True)
    out = out or os.path.join(BUILD, "stills", f"contact_s{sid:02d}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.makeImageSnapshot().save(out, skia.kPNG); return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", type=int, nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--still", type=float, nargs=2)
    ap.add_argument("--contact", type=int)
    ap.add_argument("--n", type=int, default=12)
    a = ap.parse_args()
    if a.still: print(still(int(a.still[0]), a.still[1]))
    elif a.contact is not None: print(contact(a.contact, a.n))
    else:
        ids = list(range(0, 19)) if a.all else a.scenes
        # longest-first for better packing
        with ProcessPoolExecutor(a.jobs) as ex:
            for sid, d in ex.map(render_scene, ids): pass
