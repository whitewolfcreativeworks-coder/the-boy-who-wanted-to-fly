"""Core 2.5D vector rendering helpers (skia-python).

Everything in the film is drawn procedurally from code, so every character
and environment is perfectly consistent across shots and fully re-renderable.
"""
import math, os, random
import skia

W, H, FPS = 1920, 1080, 24
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

# ------------------------------------------------------------------ math
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def inv(a, b, x): return clamp((x - a) / (b - a)) if b != a else (1.0 if x >= b else 0.0)
def smooth(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in(t): t = clamp(t); return t ** 3
def ease_io(t): t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def back_out(t, s=1.7): t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1
def ramp(t, a, b, f=smooth): return f(inv(a, b, t))
def wave(t, freq=1.0, ph=0.0): return math.sin(2 * math.pi * (t * freq + ph))

def noise1(x, seed=0):
    """Cheap smooth 1D value noise in [-1,1]."""
    i = math.floor(x); f = x - i
    def h(n):
        n = (n * 374761393 + seed * 668265263) & 0xffffffff
        n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
        return ((n ^ (n >> 16)) & 0xffff) / 32767.5 - 1
    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u

def mix_c(c1, c2, t):
    t = clamp(t)
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

# ------------------------------------------------------------------ color
def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

def col(c, a=None):
    if isinstance(c, str): c = hexc(c)
    if len(c) == 3: c = (*c, 255)
    if a is not None: c = (c[0], c[1], c[2], int(clamp(a, 0, 1) * 255) if isinstance(a, float) else a)
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(c[3]))

def rgb(c):
    return hexc(c)[:3] if isinstance(c, str) else tuple(c[:3])

def paint(c="#000000", a=None, stroke=0, blur=0, cap="round", shader=None, blend=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(col(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None: p.setShader(shader)
    if blend == "add": p.setBlendMode(skia.BlendMode.kPlus)
    elif blend == "screen": p.setBlendMode(skia.BlendMode.kScreen)
    elif blend == "multiply": p.setBlendMode(skia.BlendMode.kMultiply)
    return p

def lin(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [col(c) for c in colors], pos)

def rad(c, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*c), max(r, 0.1), [col(x) for x in colors], pos)

# ------------------------------------------------------------------ paths
def poly(pts, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p

def smooth_path(pts, close=True, tension=0.5):
    """Catmull-Rom spline through points -> organic shapes."""
    n = len(pts); p = skia.Path()
    if n < 3: return poly(pts, close)
    P = pts + pts[:3] if close else [pts[0]] + pts + [pts[-1]]
    p.moveTo(*P[1] if close else P[1])
    rng = range(1, n + 1) if close else range(1, n)
    for i in rng:
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2] if i + 2 < len(P) else P[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        p.cubicTo(*c1, *c2, *p2)
    if close: p.close()
    return p

def blob(cx, cy, r, seed=0, n=9, jitter=0.18, t=0.0, wob=0.0, sx=1.0, sy=1.0):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + rnd.uniform(-jitter, jitter) + wob * math.sin(t * 2 + i * 1.7 + seed))
        pts.append((cx + math.cos(a) * rr * sx, cy + math.sin(a) * rr * sy))
    return smooth_path(pts, True, 0.9)

def rrect(x, y, w, h, r):
    p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p

def oval(cx, cy, rx, ry):
    p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)); return p

def circle(cx, cy, r): return oval(cx, cy, r, r)

def line(c, x1, y1, x2, y2, p): c.drawLine(x1, y1, x2, y2, p)

def outline(c, path, fill, ink="#3a2418", width=5, a=1.0):
    """Storybook look: fill + soft dark outline."""
    c.drawPath(path, paint(fill, a=a if a < 1 else None))
    if width: c.drawPath(path, paint(ink, a=0.85 * a, stroke=width))

# ------------------------------------------------------------------ text
_fonts = {}
def typeface(name="Fredoka", weight=600):
    """Static instances baked from the OFL variable fonts (see assets/fonts)."""
    key = (name, weight)
    if key not in _fonts:
        avail = {"Fredoka": [400, 600, 700], "Nunito": [600, 800]}[name]
        w = min(avail, key=lambda a: abs(a - weight))
        _fonts[key] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, f"{name}-{w}.ttf"))
    return _fonts[key]

def text(c, s, x, y, size, color="#ffffff", a=1.0, name="Fredoka", weight=600,
         align="center", shadow=True, glow=None):
    f = skia.Font(typeface(name, weight), size)
    w = f.measureText(s)
    xx = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    if glow:
        c.drawString(s, xx, y, f, paint(glow, a=a * 0.8, blur=size * 0.25))
    if shadow:
        c.drawString(s, xx + size * 0.04, y + size * 0.05, f, paint("#1a0f2a", a=a * 0.45, blur=size * 0.05))
    c.drawString(s, xx, y, f, paint(color, a=a))
    return w

# ------------------------------------------------------------------ camera
class Cam:
    """Virtual camera. World units are pixels of a 1920x1080 'stage'.
    (x,y) is the world point at screen centre; z zooms; rot in degrees."""
    def __init__(self, x=W / 2, y=H / 2, z=1.0, rot=0.0, shake=0.0):
        self.x, self.y, self.z, self.rot, self.shake = x, y, z, rot, shake
    def apply(self, c, depth=1.0, t=0.0):
        """depth: 1 = main plane; <1 far (moves less); >1 near (moves more)."""
        c.save()
        c.translate(W / 2, H / 2)
        if self.rot: c.rotate(self.rot * depth)
        z = 1 + (self.z - 1) * depth
        c.scale(z, z)
        sx = self.shake * noise1(t * 9, 3) if self.shake else 0
        sy = self.shake * noise1(t * 9, 7) if self.shake else 0
        c.translate(-(W / 2 + (self.x - W / 2) * depth) + sx, -(H / 2 + (self.y - H / 2) * depth) + sy)
    def done(self, c): c.restore()

def cam_path(t, keys):
    """keys: list of (time, x, y, z[, rot]) -> Cam with eased interpolation."""
    if t <= keys[0][0]: k = keys[0]; return Cam(k[1], k[2], k[3], k[4] if len(k) > 4 else 0)
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = ease_io(inv(a[0], b[0], t))
            ra = a[4] if len(a) > 4 else 0; rb = b[4] if len(b) > 4 else 0
            return Cam(lerp(a[1], b[1], u), lerp(a[2], b[2], u), lerp(a[3], b[3], u), lerp(ra, rb, u))
    k = keys[-1]; return Cam(k[1], k[2], k[3], k[4] if len(k) > 4 else 0)

# ------------------------------------------------------------------ post FX
def vignette(c, strength=0.45, color="#1a0d20"):
    c.drawPaint(paint(shader=rad((W / 2, H / 2), W * 0.75,
        [(*rgb(color), 0), (*rgb(color), 0), (*rgb(color), int(255 * strength))], [0, 0.55, 1.0])))

def paper_grain(c, t, a=0.05):
    """Subtle drifting paper texture so flat vector art reads as illustration."""
    rnd = random.Random(int(t * 6))
    for _ in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        c.drawCircle(x, y, rnd.uniform(40, 160), paint("#fff8e8" if rnd.random() < .5 else "#4a3020", a=a * rnd.uniform(.2, 1), blur=50))

def fade(c, a, color="#000000"):
    if a > 0.001: c.drawPaint(paint(color, a=clamp(a)))

def light_rays(c, x, y, t, color="#fff2c0", a=0.15, n=7, spread=50, length=1600, ang0=100):
    for i in range(n):
        ang = math.radians(ang0 + (i - n / 2) * spread / n + 2 * math.sin(t * .3 + i))
        w = 40 + 30 * math.sin(i * 2.3 + t * .5)
        p = poly([(x, y), (x + math.cos(ang - .03) * length, y + math.sin(ang - .03) * length),
                  (x + math.cos(ang + .03) * length, y + math.sin(ang + .03) * length)])
        c.drawPath(p, paint(color, a=a * (0.6 + 0.4 * math.sin(t + i)), blur=w))

# ------------------------------------------------------------------ particles
class Particles:
    """Deterministic particle fields: same seed + t -> same frame (restartable renders)."""
    def __init__(self, n, seed, area=(0, 0, W, H)):
        r = random.Random(seed)
        self.p = [dict(x=r.uniform(area[0], area[2]), y=r.uniform(area[1], area[3]),
                       s=r.uniform(.5, 1.5), ph=r.uniform(0, 6.28), sp=r.uniform(.6, 1.4),
                       k=r.randrange(1 << 30)) for _ in range(n)]
        self.area = area

def leaf_shape(c, x, y, size, ang, color, a=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    p = skia.Path(); p.moveTo(0, -size); p.quadTo(size * .8, -size * .2, 0, size); p.quadTo(-size * .8, -size * .2, 0, -size)
    c.drawPath(p, paint(color, a=a))
    c.drawLine(0, -size * .8, 0, size * .9, paint("#5a2a10", a=.35 * a, stroke=max(1, size * .08)))
    c.restore()

LEAF_COLORS = ["#d9452b", "#f07d2a", "#f5b432", "#e8607a", "#b5502a", "#c9781e", "#f2c94c", "#a8381f"]

def falling_leaves(c, t, ps, wind=1.0, size=14, a=1.0, fall=60):
    x0, y0, x1, y1 = ps.area
    hgt = y1 - y0; wid = x1 - x0
    for q in ps.p:
        y = y0 + ((q["y"] - y0) + t * fall * q["sp"]) % hgt
        x = x0 + ((q["x"] - x0) + t * 40 * wind * q["sp"] + 40 * math.sin(t * q["sp"] + q["ph"])) % wid
        ang = 60 * math.sin(t * 1.5 * q["sp"] + q["ph"]) + t * 30 * q["sp"]
        leaf_shape(c, x, y, size * q["s"], ang, LEAF_COLORS[q["k"] % len(LEAF_COLORS)], a)

def stars(c, t, ps, a=1.0, color="#fff6d8", size=2.5, twinkle=1.0):
    for q in ps.p:
        tw = 0.55 + 0.45 * math.sin(t * 2.2 * q["sp"] * twinkle + q["ph"])
        r = size * q["s"]
        c.drawCircle(q["x"], q["y"], r, paint(color, a=a * tw))
        if q["s"] > 1.35:
            c.drawCircle(q["x"], q["y"], r * 4, paint(color, a=a * tw * .25, blur=r * 3))
            pl = paint(color, a=a * tw * .6, stroke=1.4)
            c.drawLine(q["x"] - r * 5, q["y"], q["x"] + r * 5, q["y"], pl)
            c.drawLine(q["x"], q["y"] - r * 5, q["x"], q["y"] + r * 5, pl)

def sparkles(c, t, ps, a=1.0, color="#fff1b0", size=6):
    x0, y0, x1, y1 = ps.area
    for q in ps.p:
        life = (t * .4 * q["sp"] + q["ph"]) % 1.0
        x = q["x"] + 30 * math.sin(t + q["ph"]); y = y0 + ((q["y"] - y0) - t * 30 * q["sp"]) % (y1 - y0)
        al = a * math.sin(life * math.pi)
        r = size * q["s"] * (0.5 + life)
        c.drawCircle(x, y, r * 2.5, paint(color, a=al * .35, blur=r * 2))
        star4(c, x, y, r, color, al)

def star4(c, x, y, r, color, a=1.0):
    p = skia.Path(); p.moveTo(x, y - r * 2); p.quadTo(x, y, x + r * 2, y); p.quadTo(x, y, x, y + r * 2); p.quadTo(x, y, x - r * 2, y); p.quadTo(x, y, x, y - r * 2)
    c.drawPath(p, paint(color, a=a))

def heart_path(cx, cy, s):
    p = skia.Path()
    p.moveTo(cx, cy + s * .9)
    p.cubicTo(cx - s * 1.3, cy + s * .05, cx - s * .95, cy - s * 1.0, cx, cy - s * .35)
    p.cubicTo(cx + s * .95, cy - s * 1.0, cx + s * 1.3, cy + s * .05, cx, cy + s * .9)
    p.close(); return p

def cloud(c, x, y, s, color="#ffffff", a=1.0, seed=0, shade="#c9b8e0", t=0.0):
    rnd = random.Random(seed)
    puffs = [(rnd.uniform(-1.1, 1.1), rnd.uniform(-.35, .15), rnd.uniform(.35, .6)) for _ in range(7)]
    for dx, dy, r in puffs:
        c.drawCircle(x + dx * s, y + dy * s + s * .12, r * s, paint(shade, a=a * .9))
    for dx, dy, r in puffs:
        c.drawCircle(x + dx * s - s * .04, y + dy * s, r * s * .96, paint(color, a=a))
    c.drawPath(rrect(x - 1.3 * s, y, 2.6 * s, .32 * s, .16 * s), paint(shade, a=a * .9))
