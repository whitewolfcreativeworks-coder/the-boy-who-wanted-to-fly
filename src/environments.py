"""Reusable illustrated environments. Each draws in world coordinates and
expects the camera to be applied by the caller (or applies parallax itself
when given a Cam)."""
import math, random
import skia
from engine import *
from characters import INK

GROUND = 900  # world y where characters stand in the yard

# ================================================================== skies
SKY = {
 "day":    ["#7ec3ef", "#bfe3f5", "#fdf1d6"],
 "golden": ["#6f8fcf", "#f6b56a", "#ffe2a0"],
 "sunset": ["#4a4f9c", "#e9776a", "#ffc070"],
 "dusk":   ["#1f2660", "#5a3f86", "#d9786a"],
 "night":  ["#0b1033", "#1b2560", "#3a3f80"],
 "dawn":   ["#5d6fb8", "#f3a3a0", "#ffe0b0"],
 "dream":  ["#140b3a", "#3b1f78", "#8a4fb0"],
}

def sky(c, mode="day", mode2=None, u=0.0, sun=None, t=0.0):
    a = SKY[mode]; b = SKY[mode2] if mode2 else a
    cols = [mix_c(rgb(x), rgb(y), u) for x, y in zip(a, b)]
    c.drawPaint(paint(shader=lin((0, 0), (0, H), cols, [0, .6, 1])))
    if sun:
        sx, sy, sr, scol = sun
        c.drawCircle(sx, sy, sr * 4, paint(scol, a=.25, blur=sr * 2))
        c.drawCircle(sx, sy, sr * 1.6, paint(scol, a=.5, blur=sr * .6))
        c.drawCircle(sx, sy, sr, paint("#fff6d0"))

def sky_clouds(c, t, a=1.0, tint="#ffffff", shade="#d8c8e8", speed=6, y0=120, n=5, seed=4, scale=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(-300, W + 300) + t * speed * rnd.uniform(.6, 1.4)) % (W + 600) - 300
        y = y0 + rnd.uniform(0, 220)
        cloud(c, x, y, rnd.uniform(60, 110) * scale, tint, a * rnd.uniform(.6, .95), seed=i + seed, shade=shade)

def moon(c, x, y, r, a=1.0, glow=1.0):
    c.drawCircle(x, y, r * 3.2, paint("#fff3c8", a=.18 * a * glow, blur=r * 1.4))
    c.drawCircle(x, y, r * 1.5, paint("#fff3c8", a=.35 * a * glow, blur=r * .4))
    c.drawCircle(x, y, r, paint("#fff4d6", a=a))
    for dx, dy, rr in ((-.3, -.2, .18), (.25, .3, .13), (.35, -.35, .09), (-.1, .45, .1)):
        c.drawCircle(x + dx * r, y + dy * r, rr * r, paint("#e8d8b0", a=.6 * a))

# ================================================================== yard pieces
def hills(c, t, color_far="#d9a77a", color_near="#c98a5a", tint=None):
    p = skia.Path(); p.moveTo(-800, 700)
    for i in range(0, 45):
        x = -800 + i * 120; p.lineTo(x, 610 + 40 * math.sin(i * .7) + 25 * math.sin(i * 1.9))
    p.lineTo(4600, 1200); p.lineTo(-800, 1200); p.close()
    c.drawPath(p, paint(color_far))
    rnd = random.Random(2)
    for i in range(40):  # distant autumn tree dots
        x = rnd.uniform(-800, 4400); y = 640 + rnd.uniform(-10, 60)
        c.drawCircle(x, y, rnd.uniform(18, 40), paint(rnd.choice(["#c8502c", "#e0882c", "#d9a33a", "#a8462a", "#b8703a"]), a=.85))

def tree(c, x, y, h, t, seed=1, wind=1.0, bare=0.0, colors=None, a=1.0):
    """Autumn maple. bare: 0 full canopy, 1 mostly fallen."""
    rnd = random.Random(seed)
    colors = colors or ["#d9452b", "#f07d2a", "#f5b432", "#e8607a", "#c9781e", "#b5402a"]
    sway = 3 * math.sin(t * .8 + seed) * wind
    # trunk
    tw = h * .07
    trunk = poly([(x - tw, y), (x - tw * .6, y - h * .55), (x + tw * .6, y - h * .55), (x + tw, y)])
    outline(c, trunk, "#6b4128", width=5)
    for ang, ln in ((-35, .35), (30, .3), (-10, .38)):
        bx, by = x, y - h * .5
        ex, ey = bx + math.sin(math.radians(ang + sway)) * h * ln, by - math.cos(math.radians(ang)) * h * ln
        c.drawLine(bx, by, ex, ey, paint(INK, stroke=tw * .9)); c.drawLine(bx, by, ex, ey, paint("#6b4128", stroke=tw * .7))
    cx, cy = x + sway * 3, y - h * .78
    k = int(26 * (1 - bare * .75))
    for i in range(k):
        dx, dy = rnd.gauss(0, h * .24), rnd.gauss(0, h * .15)
        r = h * rnd.uniform(.09, .16)
        colr = colors[rnd.randrange(len(colors))]
        jig = 4 * math.sin(t * 1.5 + i) * wind
        c.drawPath(blob(cx + dx + jig, cy + dy, r, seed=seed * 100 + i, jitter=.15), paint(mix_c(rgb(colr), (60, 20, 10), .25), a=a))
    for i in range(k):
        rnd2 = random.Random(seed * 1000 + i)
        dx, dy = rnd2.gauss(0, h * .22), rnd2.gauss(0, h * .14) - h * .02
        r = h * rnd2.uniform(.07, .13)
        colr = colors[rnd2.randrange(len(colors))]
        jig = 5 * math.sin(t * 1.7 + i * .7) * wind
        c.drawPath(blob(cx + dx + jig, cy + dy - 6, r, seed=seed * 300 + i, jitter=.15), paint(colr, a=a))
        c.drawCircle(cx + dx + jig - r * .3, cy + dy - 6 - r * .35, r * .35, paint("#fff4c0", a=.18 * a))

def house(c, x, y, t, lights=0.0, chimney_smoke=0.0, door_open=0.0, mom=None):
    """Family house. (x,y) = bottom-left at ground. ~860 wide incl. garage."""
    # main body
    body = poly([(x, y), (x, y - 330), (x + 560, y - 330), (x + 560, y)])
    outline(c, body, "#f4e3c4", width=6)
    for i in range(12):  # siding
        c.drawLine(x + 4, y - 25 - i * 26, x + 556, y - 25 - i * 26, paint("#d9c4a0", stroke=2))
    roof = poly([(x - 40, y - 320), (x + 280, y - 540), (x + 600, y - 320)])
    outline(c, roof, "#8a3b33", width=6)
    for i in range(1, 6):
        yy = y - 320 - i * 36; w = (i * 36) * 320 / 220
        c.drawLine(x - 40 + w * .99, yy, x + 600 - w * .99, yy, paint("#6e2c26", stroke=3))
    # chimney
    ch = poly([(x + 420, y - 400), (x + 420, y - 500), (x + 480, y - 500), (x + 480, y - 360)])
    outline(c, ch, "#a8553f", width=5)
    if chimney_smoke > 0:
        for i in range(7):
            u = ((t * .25 + i / 7) % 1.0)
            c.drawCircle(x + 450 + 60 * u + 15 * math.sin(t + i), y - 520 - u * 260, 18 + u * 40, paint("#e8e0e8", a=chimney_smoke * .55 * (1 - u), blur=12))
    # windows
    for wx, wy in ((x + 70, y - 270), (x + 380, y - 270), (x + 70, y - 140)):
        window(c, wx, wy, 120, 100, lights, t)
    # attic round window
    c.drawCircle(x + 280, y - 420, 34, paint(INK)); c.drawCircle(x + 280, y - 420, 29, paint(mix_c((120, 160, 200), (255, 210, 120), lights)))
    # door + porch
    dx = x + 250
    c.drawPath(rrect(dx - 20, y - 220, 140, 220, 8), paint("#6e3d2a"))
    door = rrect(dx, y - 200, 100, 200, 10)
    outline(c, door, "#2f6a6a", width=5)
    if door_open > 0:
        c.drawPath(rrect(dx, y - 200, 100, 200, 10), paint("#ffd890", a=door_open))
        c.save(); c.translate(dx, 0); c.scale(1 - door_open * .8, 1)
        outline(c, rrect(0, y - 200, 100, 200, 10), "#2f6a6a", width=5); c.restore()
    c.drawCircle(dx + 82, y - 100, 6, paint("#f2c94c"))
    c.drawPath(rrect(dx - 40, y - 8, 180, 18, 4), paint("#b8a080"))
    # garage
    gx = x + 560
    g = poly([(gx, y), (gx, y - 260), (gx + 300, y - 260), (gx + 300, y)])
    outline(c, g, "#efdcbc", width=6)
    groof = poly([(gx - 10, y - 255), (gx + 150, y - 330), (gx + 320, y - 255)])
    outline(c, groof, "#8a3b33", width=6)
    gd = rrect(gx + 30, y - 200, 240, 200, 6)
    outline(c, gd, "#e9e2d6", width=5)
    for i in range(1, 5):
        c.drawLine(gx + 32, y - 200 + i * 40, gx + 268, y - 200 + i * 40, paint("#c8bea8", stroke=3))
    # porch pumpkins + apple basket
    for i, (px, pr) in enumerate(((dx - 70, 30), (dx - 30, 22), (dx + 150, 26))):
        pumpkin(c, px, y + 4, pr, t)
    # bushes
    for bx in (x - 30, x + 160, x + 520):
        c.drawPath(blob(bx, y - 20, 55, seed=int(bx), jitter=.2, sy=.7), paint("#5f7a3a"))
        c.drawPath(blob(bx - 8, y - 30, 40, seed=int(bx) + 1, jitter=.2, sy=.7), paint("#7a9648"))

def window(c, x, y, w, h, lights, t):
    outline(c, rrect(x, y, w, h, 6), "#ffffff", width=6)
    glass = mix_c((150, 190, 220), (255, 205, 110), lights)
    c.drawPath(rrect(x + 8, y + 8, w - 16, h - 16, 3), paint(glass))
    if lights > 0:
        c.drawPath(rrect(x - 20, y - 20, w + 40, h + 40, 20), paint("#ffcf70", a=.25 * lights, blur=25))
    else:
        c.drawLine(x + 18, y + h - 20, x + w * .5, y + 18, paint("#ffffff", a=.4, stroke=5))
    c.drawLine(x + w / 2, y + 6, x + w / 2, y + h - 6, paint("#ffffff", stroke=5))
    c.drawLine(x + 6, y + h / 2, x + w - 6, y + h / 2, paint("#ffffff", stroke=5))
    c.drawPath(rrect(x - 12, y + h - 4, w + 24, 14, 4), paint("#ffffff")); c.drawPath(rrect(x - 12, y + h - 4, w + 24, 14, 4), paint(INK, stroke=3))

def pumpkin(c, x, y, r, t=0):
    for dx in (-.45, .45, 0):
        c.drawPath(oval(x + dx * r, y - r * .8, r * .65, r * .8), paint("#e87a20")); c.drawPath(oval(x + dx * r, y - r * .8, r * .65, r * .8), paint(INK, stroke=3, a=.7))
    c.drawLine(x, y - r * 1.55, x + 4, y - r * 1.95, paint("#5a6a2a", stroke=6))

def fence(c, x0, x1, y, color="#fbf6ee"):
    c.drawRect(skia.Rect.MakeLTRB(x0, y - 70, x1, y - 60), paint(color))
    c.drawRect(skia.Rect.MakeLTRB(x0, y - 35, x1, y - 25), paint(color))
    x = x0
    while x < x1:
        p = poly([(x, y), (x, y - 90), (x + 10, y - 102), (x + 20, y - 90), (x + 20, y)])
        outline(c, p, color, width=3); x += 42

def tele_pole(c, x, y, h=560):
    c.drawRect(skia.Rect.MakeLTRB(x - 11, y - h, x + 11, y), paint("#5e4030"))
    c.drawRect(skia.Rect.MakeLTRB(x - 11, y - h, x - 4, y), paint("#7a5640"))
    c.drawRect(skia.Rect.MakeLTRB(x - 90, y - h + 40, x + 90, y - h + 54), paint("#5e4030"))
    for dx in (-75, -25, 25, 75):
        c.drawPath(oval(x + dx, y - h + 34, 7, 10), paint("#7fb0b8"))

def wire(c, x0, y0, x1, y1, sag=50, a=1.0, width=3):
    p = skia.Path(); p.moveTo(x0, y0); p.quadTo((x0 + x1) / 2, (y0 + y1) / 2 + sag * 2, x1, y1)
    c.drawPath(p, paint("#2a2026", a=a, stroke=width))

def wire_y(x0, y0, x1, y1, sag, x):
    u = clamp((x - x0) / (x1 - x0)); return (1 - u) ** 2 * y0 + 2 * (1 - u) * u * ((y0 + y1) / 2 + sag * 2) + u * u * y1

def hanging_shoes(c, x, y, t, colr="#e0352b", sole="#fbf3e6", lace="#ffffff", swing=1.0, s=1.0, seed=0):
    """A pair of sneakers tied together, hanging over a wire at (x,y)."""
    for k, side in enumerate((-1, 1)):
        ang = (14 * side + 10 * math.sin(t * 1.6 + seed + k * .6) * swing)
        c.save(); c.translate(x, y); c.rotate(ang)
        L = 70 * s
        c.drawLine(0, 0, 0, L, paint(lace, stroke=3 * s)); c.drawLine(0, 0, 0, L, paint("#c0b8b0", stroke=1 * s, a=.6))
        c.translate(0, L); c.rotate(-80 * side if side < 0 else 80)
        body = rrect(-12 * s, -16 * s, 52 * s, 26 * s, 13 * s)
        outline(c, body, colr, width=4)
        c.drawPath(rrect(-12 * s, 4 * s, 52 * s, 8 * s, 4 * s), paint(sole))
        for i in range(3):
            c.drawLine((4 + i * 9) * s, -14 * s, (8 + i * 9) * s, -4 * s, paint(lace, stroke=3 * s))
        c.drawCircle(32 * s, -6 * s, 5 * s, paint("#ffffff"))
        c.restore()

def lawn(c, x0, x1, top, bottom, t, leaves=0.6, light="#9cc25a", dark="#79a043"):
    c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, bottom), paint(shader=lin((0, top), (0, bottom), [light, dark])))
    rnd = random.Random(5)
    n = int(420 * leaves)
    for i in range(n):  # carpet of fallen leaves
        x = rnd.uniform(x0, x1); y = rnd.uniform(top + 10, bottom - 5)
        leaf_shape(c, x, y, rnd.uniform(6, 11) * (0.6 + (y - top) / (bottom - top)), rnd.uniform(0, 360), LEAF_COLORS[rnd.randrange(8)], .9)
    for i in range(140):
        x = rnd.uniform(x0, x1); y = rnd.uniform(top, bottom)
        c.drawLine(x, y, x + rnd.uniform(-4, 4), y - rnd.uniform(8, 16), paint(dark, stroke=2, a=.6))

def street(c, x0, x1, top, t):
    c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, top + 40), paint("#d8d0c4"))      # sidewalk
    for x in range(int(x0), int(x1), 90): c.drawLine(x, top, x, top + 40, paint("#bdb4a6", stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(x0, top + 40, x1, top + 52), paint("#a8a094"))  # curb
    c.drawRect(skia.Rect.MakeLTRB(x0, top + 52, x1, top + 400), paint("#5b5866"))  # road
    for x in range(int(x0), int(x1), 160): c.drawRect(skia.Rect.MakeLTRB(x, top + 170, x + 80, top + 180), paint("#e8d890"))

def yard_world(c, cam, t, light=0.0, wind=1.0, house_lights=0.0, smoke=0.0, door=0.0, leaves_on_ground=0.7,
               mode="day", mode2=None, u=0.0, sun=None, pile=None, extra=None, ladder=None, far_cam=True):
    """Front-yard world, house at left, yard to the right, street at the bottom.
    Draws with parallax. Returns nothing; caller draws characters with cam.apply(c)."""
    sky(c, mode, mode2, u, sun, t)
    sky_clouds(c, t, a=.9 - .5 * light, tint=mix_c((255, 255, 255), (255, 200, 170), light), shade=mix_c((216, 200, 232), (200, 130, 150), light), speed=8)
    cam.apply(c, .25, t); hills(c, t, mix_c((217, 167, 122), (170, 110, 120), light), None); cam.done(c)
    cam.apply(c, .55, t)
    for i, hx in enumerate(range(-400, 4200, 520)):
        hh = 140 + (i * 37) % 60
        outline(c, poly([(hx, 760), (hx, 760 - hh), (hx + 90, 760 - hh - 70), (hx + 180, 760 - hh), (hx + 180, 760)]), mix_c((214, 190, 170), (150, 120, 140), light), width=3)
        window(c, hx + 60, 760 - hh + 30, 50, 40, house_lights * .8, t)
    for i, tx in enumerate(range(-300, 4300, 380)): tree(c, tx, 770, 260, t, seed=40 + i, wind=wind * .6, a=.95)
    cam.done(c)
    cam.apply(c, 1.0, t)
    lawn(c, -600, 4200, 800, 1000, t, leaves=leaves_on_ground)
    fence(c, -600, 120, 820)
    house(c, 160, 830, t, house_lights, smoke, door)
    tree(c, 1450, 840, 620, t, seed=7, wind=wind)
    tree(c, 2450, 830, 700, t, seed=12, wind=wind)
    tree(c, 3350, 840, 560, t, seed=21, wind=wind)
    tele_pole(c, 3000, 1010, 820)
    wire(c, -800, 205, 3000, 205, 60); wire(c, 3000, 205, 5200, 210, 60)
    wire(c, -800, 245, 3000, 245, 55); wire(c, 3000, 245, 5200, 250, 55)
    if ladder: ladder_draw(c, *ladder)
    if pile: leaf_pile(c, *pile)
    street(c, -800, 5200, 990, t)
    if extra: extra(c)
    cam.done(c)
    if light > 0:
        c.drawPaint(paint("#ff9a50", a=.16 * light, blend="multiply"))
        c.drawPaint(paint("#ffb070", a=.10 * light))

def leaf_pile(c, x, y, w, h, t, burst=0.0, seed=3):
    rnd = random.Random(seed)
    base = smooth_path([(x - w / 2, y), (x - w * .4, y - h * .6), (x - w * .1, y - h), (x + w * .2, y - h * .9), (x + w * .45, y - h * .5), (x + w / 2, y)], True, .8)
    c.drawPath(base, paint("#b8501f"))
    for i in range(160):
        a = rnd.uniform(0, math.pi); rr = rnd.uniform(0, 1) ** .6
        lx = x + math.cos(a) * w * .48 * rr; ly = y - math.sin(a) * h * .95 * rr
        leaf_shape(c, lx, ly, rnd.uniform(9, 16), rnd.uniform(0, 360), LEAF_COLORS[rnd.randrange(8)])

def leaf_burst(c, x, y, t0, t, n=70, seed=9, power=1.0):
    """Leaves exploding upward from a point at time t0."""
    if t < t0: return
    dt = t - t0
    rnd = random.Random(seed)
    for i in range(n):
        vx = rnd.uniform(-420, 420) * power; vy = rnd.uniform(-900, -350) * power
        drag = 1.0 / (1 + dt * 1.2)
        px = x + vx * dt * drag + 30 * math.sin(dt * 3 + i)
        py = y + vy * dt * drag + 260 * dt * dt
        if py > y + 20 or dt > 4.5: continue
        leaf_shape(c, px, py, rnd.uniform(9, 16), dt * 300 * rnd.uniform(.5, 1.5) + i * 40, LEAF_COLORS[i % 8], clamp(3.5 - dt))

def ladder_draw(c, x, y, h, a=1.0, lean=0.0):
    c.save(); c.translate(x, y); c.rotate(lean)
    for dx in (-38, 38):
        c.drawLine(dx, 0, dx * .8, -h, paint(INK, stroke=16, a=a)); c.drawLine(dx, 0, dx * .8, -h, paint("#c9a06a", stroke=11, a=a))
    for i in range(1, int(h / 55) + 1):
        yy = -i * 55; w = 38 * (1 - .2 * i * 55 / h)
        c.drawLine(-w, yy, w, yy, paint(INK, stroke=11, a=a)); c.drawLine(-w, yy, w, yy, paint("#b08850", stroke=7, a=a))
    c.restore()

def rake(c, x, y, ang, s=1.0):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.drawLine(0, 0, 0, 200, paint(INK, stroke=10)); c.drawLine(0, 0, 0, 200, paint("#b8864a", stroke=6))
    p = poly([(0, 195), (-45, 240), (45, 240)])
    c.drawPath(p, paint("#4a8a3a")); c.drawPath(p, paint(INK, stroke=3))
    for i in range(-4, 5): c.drawLine(i * 10, 238, i * 11, 258, paint("#3a6a2a", stroke=3))
    c.restore()

# ================================================================== interiors
def garage_interior(c, t, bulb=1.0):
    c.drawPaint(paint(shader=lin((0, 0), (0, H), ["#5a4636", "#7a604a"])))
    # pegboard wall
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 760), paint("#8a6c50"))
    for x in range(40, W, 44):
        for y in range(40, 700, 44): c.drawCircle(x, y, 3, paint("#6a5038"))
    for tx, ty, kind in ((260, 220, "hammer"), (380, 240, "saw"), (1560, 230, "wrench"), (1690, 200, "hammer")):
        tool(c, tx, ty, kind)
    # shelves with boxes
    c.drawRect(skia.Rect.MakeLTRB(1180, 300, 1900, 318), paint("#5a3c26"))
    for i, bx in enumerate((1200, 1340, 1480, 1640)):
        box(c, bx, 300, 120 + (i % 2) * 20, 90 + (i % 3) * 15, i)
    # floor
    c.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), paint(shader=lin((0, 760), (0, H), ["#9a8a78", "#7a6c5c"])))
    c.drawPath(oval(900, 900, 500, 60), paint("#5a4a3a", a=.25, blur=20))  # oil stain
    # workbench
    c.drawRect(skia.Rect.MakeLTRB(120, 560, 1060, 600), paint("#a8754a")); c.drawRect(skia.Rect.MakeLTRB(120, 560, 1060, 600), paint(INK, stroke=4))
    for lx in (150, 1020): c.drawRect(skia.Rect.MakeLTRB(lx, 600, lx + 22, 820), paint("#7a5236"))
    # big cardboard boxes on floor
    box(c, 1250, 900, 260, 190, 7); box(c, 1500, 900, 200, 150, 8); box(c, 1150, 900, 150, 110, 9)
    # bulb + light cone
    c.drawLine(960, 0, 960, 120, paint("#2a2a2a", stroke=3))
    sw = math.sin(t * 1.3) * 3
    c.drawCircle(960 + sw, 140, 22, paint("#fff3c0"))
    c.drawCircle(960 + sw, 140, 140, paint("#ffd890", a=.35 * bulb, blur=60))
    c.drawPath(poly([(960 + sw, 140), (300, H), (1620, H)]), paint("#ffe0a0", a=.08 * bulb, blur=40))

def box(c, x, y, w, h, seed=0, open_flaps=True):
    p = poly([(x, y), (x, y - h), (x + w, y - h), (x + w, y)])
    outline(c, p, "#c99a62", width=4)
    c.drawLine(x + w * .1, y - h * .5, x + w * .9, y - h * .5, paint("#d8d4c8", stroke=10, a=.8))
    if open_flaps:
        c.drawPath(poly([(x, y - h), (x - w * .15, y - h - h * .25), (x + w * .35, y - h - h * .2), (x + w * .45, y - h)]), paint("#b88a52"))
        c.drawPath(poly([(x + w, y - h), (x + w * 1.12, y - h - h * .22), (x + w * .6, y - h - h * .2), (x + w * .55, y - h)]), paint("#d4a870"))
    c.drawPath(poly([(x + w * .3, y - h * .3), (x + w * .38, y - h * .4), (x + w * .46, y - h * .3)], False), paint("#7a5236", stroke=3))

def tool(c, x, y, kind):
    if kind == "hammer":
        c.drawLine(x, y, x, y + 130, paint("#b8864a", stroke=12)); c.drawPath(rrect(x - 35, y - 10, 70, 26, 5), paint("#7a7a86"))
    elif kind == "saw":
        c.drawPath(poly([(x, y), (x + 170, y + 20), (x + 170, y + 60), (x, y + 70)]), paint("#c8ccd4")); c.drawPath(rrect(x - 40, y, 50, 70, 12), paint("#b03a2a"))
    else:
        c.drawLine(x, y, x, y + 120, paint("#8a8e98", stroke=12)); c.drawCircle(x, y, 18, paint("#8a8e98")); c.drawCircle(x, y, 8, paint("#8a6c50"))

def scissors(c, x, y, ang=0, open_=0.3, s=1.0):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    for sgn in (-1, 1):
        c.save(); c.rotate(sgn * open_ * 20)
        c.drawPath(poly([(0, -4), (70, -2), (70, 2), (0, 4)]), paint("#c8ccd4")); c.drawPath(poly([(0, -4), (70, -2), (70, 2), (0, 4)]), paint(INK, stroke=2))
        c.drawPath(oval(-22, sgn * 10, 16, 11), paint("#e0352b", stroke=7))
        c.restore()
    c.restore()

def tape_roll(c, x, y, s=1.0):
    c.drawCircle(x, y, 26 * s, paint("#d8d4c8")); c.drawCircle(x, y, 26 * s, paint(INK, stroke=3)); c.drawCircle(x, y, 13 * s, paint("#8a6c50"))

def kitchen(c, t, light="morning", food=None, food_amt=1.0):
    warm = light == "evening"
    c.drawPaint(paint(shader=lin((0, 0), (0, H), ["#f6dfb8", "#efc996"] if not warm else ["#e8b880", "#c98a5a"])))
    # wallpaper pattern
    for x in range(0, W + 60, 80):
        for y in range(0, 640, 80):
            c.drawCircle(x + (40 if (y // 80) % 2 else 0), y + 30, 5, paint("#e6c48c" if not warm else "#c08850", a=.7))
    # window
    wx, wy, ww, wh = 760, 140, 400, 300
    outline(c, rrect(wx, wy, ww, wh, 10), "#ffffff", width=8)
    glass = ["#9fd3f0", "#fdf1c8"] if not warm else ["#3a3f80", "#d9786a"]
    c.drawPath(rrect(wx + 12, wy + 12, ww - 24, wh - 24, 4), paint(shader=lin((0, wy), (0, wy + wh), glass)))
    tree(c, wx + 120, wy + wh + 150, 300, t, seed=3, wind=.5, a=.9) if False else None
    c.save(); c.clipPath(rrect(wx + 12, wy + 12, ww - 24, wh - 24, 4), doAntiAlias=True)
    for i in range(6): c.drawPath(blob(wx + 60 + i * 70, wy + wh - 30, 50, seed=i, jitter=.2), paint(["#e0702a", "#d94a2a", "#f2b030"][i % 3], a=.85))
    c.restore()
    c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, paint("#ffffff", stroke=8))
    c.drawLine(wx, wy + wh / 2, wx + ww, wy + wh / 2, paint("#ffffff", stroke=8))
    # curtains
    for sx in (wx - 60, wx + ww - 10):
        c.drawPath(smooth_path([(sx, wy - 30), (sx + 70, wy - 30), (sx + 60 + 5 * math.sin(t), wy + wh + 40), (sx + 10, wy + wh + 50)], True, .5), paint("#e86a5a"))
    # counter + cabinets left/right
    c.drawRect(skia.Rect.MakeLTRB(0, 560, 560, 760), paint("#7aa8a0")); c.drawRect(skia.Rect.MakeLTRB(0, 540, 580, 566), paint("#f4f0e6"))
    for x in (40, 300): outline(c, rrect(x, 590, 220, 150, 8), "#8ab8b0", width=4)
    c.drawRect(skia.Rect.MakeLTRB(1380, 560, W, 760), paint("#7aa8a0")); c.drawRect(skia.Rect.MakeLTRB(1360, 540, W, 566), paint("#f4f0e6"))
    # sink with faucet
    c.drawPath(rrect(180, 520, 220, 30, 8), paint("#c8ccd4")); c.drawLine(290, 520, 290, 470, paint("#9a9ea8", stroke=10)); c.drawLine(290, 472, 330, 472, paint("#9a9ea8", stroke=10))
    # floor
    c.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), paint("#c98a5a"))
    for x in range(0, W, 120):
        for y in range(760, H, 60): c.drawRect(skia.Rect.MakeLTRB(x + (60 if (y // 60) % 2 else 0), y, x + 58 + (60 if (y // 60) % 2 else 0), y + 58), paint("#d89a6a"))
    if warm:
        c.drawCircle(960, 120, 300, paint("#ffd890", a=.25, blur=120))

def table(c, x, y, w=700, food=None, amt=1.0, t=0.0, settings=3):
    c.drawPath(oval(x, y + 20, w * .55, 30), paint("#000000", a=.12, blur=10))
    c.drawPath(rrect(x - w / 2, y - 20, w, 40, 14), paint("#a8754a")); c.drawPath(rrect(x - w / 2, y - 20, w, 40, 14), paint(INK, stroke=4))
    c.drawPath(rrect(x - w / 2 + 6, y - 24, w - 12, 16, 8), paint("#f4f0e6"))  # tablecloth edge
    for lx in (x - w * .42, x + w * .42): c.drawRect(skia.Rect.MakeLTRB(lx - 12, y + 18, lx + 12, y + 180), paint("#7a5236"))
    if food:
        for i in range(settings):
            px = x - w * .3 + i * w * .3
            plate(c, px, y - 26, food, amt, t, i)

def plate(c, x, y, food, amt, t, seed=0):
    c.drawPath(oval(x, y, 80, 18), paint("#ffffff")); c.drawPath(oval(x, y, 80, 18), paint(INK, stroke=3))
    if amt <= 0: return
    if food == "spaghetti":
        c.drawPath(oval(x, y - 10, 60 * amt, 22 * amt), paint("#f2d27a"))
        for i in range(10):
            a = i * .6 + seed
            c.drawPath(oval(x + math.cos(a) * 30 * amt, y - 12 + math.sin(a) * 8 * amt, 22 * amt, 7 * amt), paint("#e8c060", stroke=3))
        c.drawPath(oval(x, y - 18, 40 * amt, 12 * amt), paint("#c83a2a"))
        for dx in (-18, 0, 18): c.drawCircle(x + dx * amt, y - 24, 11 * amt, paint("#7a3a22"))
        for i in range(3):  # steam
            u = (t * .4 + i / 3) % 1
            c.drawCircle(x - 20 + i * 20 + 8 * math.sin(t * 2 + i), y - 40 - u * 80, 10 + u * 10, paint("#ffffff", a=.35 * (1 - u), blur=6))
    elif food == "pancakes":
        n = max(1, int(4 * amt + .5))
        for i in range(n):
            c.drawPath(oval(x, y - 8 - i * 12, 56, 14), paint("#d99a4a")); c.drawPath(oval(x, y - 10 - i * 12, 54, 12), paint("#f0bf6a"))
        top = y - 10 - (n - 1) * 12
        for dx, dy in ((-20, 0), (0, -4), (18, 2), (-6, 4), (10, -2)): c.drawCircle(x + dx, top + dy, 6, paint("#3a3a8a"))
        c.drawPath(oval(x + 4, top - 2, 28, 6), paint("#ffe9a0", a=.9))

def chair(c, x, y, face=1, tip=0.0):
    c.save(); c.translate(x, y); c.rotate(tip * face); c.scale(face, 1)
    c.drawRect(skia.Rect.MakeLTRB(-50, -110, 50, -96), paint("#8a5a36"))
    for lx in (-44, 36): c.drawRect(skia.Rect.MakeLTRB(lx, -96, lx + 10, 0), paint("#7a4a2a"))
    c.drawRect(skia.Rect.MakeLTRB(-52, -280, -38, -96), paint("#7a4a2a"))
    for yy in (-260, -210, -160): c.drawRect(skia.Rect.MakeLTRB(-52, yy, -20, yy + 12), paint("#7a4a2a"))
    c.restore()

def stairs_hall(c, t, light=1.0):
    c.drawPaint(paint(shader=lin((0, 0), (0, H), ["#efd6a8", "#dfbb88"])))
    for x in range(0, W, 140): c.drawLine(x, 0, x, 760, paint("#e2c490", stroke=10))
    # framed family pictures
    for i, (fx, fy) in enumerate(((300, 200), (480, 160), (1500, 260))):
        outline(c, rrect(fx, fy, 130, 100, 6), "#fff6e0", width=8)
        c.drawCircle(fx + 65, fy + 50, 26, paint(["#f3c9a2", "#e9b58f", "#dca27b"][i]))
    # staircase rising to the right
    for i in range(12):
        x = 700 + i * 80; y = 960 - i * 62
        c.drawRect(skia.Rect.MakeLTRB(x, y, x + 1300, y + 62), paint("#b87a4a" if i % 2 else "#a86a3a"))
        c.drawRect(skia.Rect.MakeLTRB(x, y, x + 1300, y + 10), paint("#d89a6a"))
    for i in range(12):
        x = 720 + i * 80; y = 960 - i * 62
        c.drawLine(x, y, x, y - 150, paint("#fff6e0", stroke=8))
    c.drawLine(700, 820, 1660, 70, paint("#8a4a2a", stroke=20))
    c.drawRect(skia.Rect.MakeLTRB(0, 960, W, H), paint("#a86a3a"))
    c.drawPath(rrect(80, 980, 520, 80, 20), paint("#c84a3a", a=.8))  # rug

def stair_pos(u):
    """Feet position on the staircase, u in [0,1] bottom->top."""
    i = u * 11.5
    return 720 + i * 80, 960 - math.floor(i) * 62 - 62 * smooth(i - math.floor(i)) * 0.0

# ================================================================== bedroom
def bedroom(c, t, mode="night", lamp=1.0, poster_anim=1.0, branch_tap=0.0, moon_a=1.0):
    night = mode == "night"
    wall = ["#3e4a86", "#2c3566"] if night else ["#a8d0e8", "#88b8d8"]
    c.drawPaint(paint(shader=lin((0, 0), (0, H), wall)))
    # dotted star wallpaper
    rnd = random.Random(8)
    for i in range(70):
        star4(c, rnd.uniform(0, W), rnd.uniform(0, 720), 3, "#ffffff", .25 if night else .35)
    # window with branch
    wx, wy, ww, wh = 1280, 120, 400, 380
    outline(c, rrect(wx, wy, ww, wh, 12), "#f4f0e6", width=10)
    c.save(); c.clipPath(rrect(wx + 14, wy + 14, ww - 28, wh - 28, 4), doAntiAlias=True)
    c.drawPaint(paint(shader=lin((0, wy), (0, wy + wh), ["#101640", "#2a3070"] if night else ["#8fd0f5", "#fdf0c8"])))
    if night:
        moon(c, wx + 270, wy + 110, 50, moon_a)
        for i in range(12): c.drawCircle(wx + rnd.uniform(20, 380), wy + rnd.uniform(20, 300), 2, paint("#ffffff", a=.8))
    bt = branch_tap
    bp = skia.Path(); bp.moveTo(wx + ww + 40, wy + 60); bp.quadTo(wx + 260, wy + 120 + bt * 10, wx + 40 + bt * 30, wy + 220 + bt * 12)
    c.drawPath(bp, paint("#2a1a14" if night else "#6b4128", stroke=14))
    for i in range(6):
        lx = wx + 80 + i * 55; ly = wy + 160 - i * 12 + bt * 6
        leaf_shape(c, lx, ly, 14, 30 * i + bt * 20, "#5a2a3a" if night else LEAF_COLORS[i], 1)
    c.restore()
    c.drawLine(wx + ww / 2, wy + 10, wx + ww / 2, wy + wh - 10, paint("#f4f0e6", stroke=10))
    c.drawLine(wx + 10, wy + wh / 2, wx + ww - 10, wy + wh / 2, paint("#f4f0e6", stroke=10))
    # posters
    posters(c, t, night, poster_anim)
    # floor + rug
    c.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), paint("#8a5a3a" if not night else "#4a3048"))
    c.drawPath(oval(900, 900, 420, 80), paint("#e8a050" if not night else "#7a5070"))
    c.drawPath(oval(900, 900, 330, 58), paint("#f2c060" if not night else "#8a6080"))
    # moonlight beam on floor
    if night:
        c.drawPath(poly([(wx + 20, wy + wh), (wx + ww, wy + wh), (wx + ww - 300, H), (wx - 500, H)]), paint("#c8d8ff", a=.12 * moon_a, blur=20))
    # nightstand + lamp
    c.drawPath(rrect(240, 600, 180, 180, 10), paint("#a8754a")); c.drawPath(rrect(240, 600, 180, 180, 10), paint(INK, stroke=4))
    c.drawLine(330, 600, 330, 520, paint("#8a6a4a", stroke=8))
    c.drawPath(poly([(280, 520), (380, 520), (360, 450), (300, 450)]), paint("#f2c94c")); c.drawPath(poly([(280, 520), (380, 520), (360, 450), (300, 450)]), paint(INK, stroke=3))
    if lamp > 0:
        c.drawCircle(330, 500, 260, paint("#ffcf70", a=.35 * lamp, blur=100))
    if night: c.drawPaint(paint("#1a2060", a=.18 * (1 - lamp * .5), blend="multiply"))

def posters(c, t, night, anim=1.0):
    dim = .7 if night else 1.0
    # airplane poster
    x, y = 120, 150
    outline(c, rrect(x, y, 300, 220, 8), "#fbf3e0", width=5)
    c.drawPath(rrect(x + 12, y + 12, 276, 196, 4), paint("#8fc8ef", a=dim))
    px = x + 150 + 40 * math.sin(t * .6) * anim; py = y + 110 + 10 * math.sin(t * 1.2) * anim
    c.drawPath(rrect(px - 70, py - 12, 140, 24, 12), paint("#e8eef2")); c.drawPath(poly([(px - 10, py), (px - 40, py + 50), (px + 20, py + 50), (px + 30, py)]), paint("#e0352b"))
    c.drawPath(poly([(px - 60, py), (px - 80, py - 35), (px - 55, py - 35), (px - 40, py)]), paint("#e0352b"))
    # bird poster
    x, y = 470, 120
    outline(c, rrect(x, y, 240, 300, 8), "#fbf3e0", width=5)
    c.drawPath(rrect(x + 12, y + 12, 216, 276, 4), paint("#f8d890", a=dim))
    for i in range(3):
        bx = x + 60 + i * 60; by = y + 100 + i * 40 + 6 * math.sin(t * 3 + i) * anim
        f = math.sin(t * 6 + i) * anim
        bp = skia.Path(); bp.moveTo(bx - 30, by - 10 * f); bp.quadTo(bx - 12, by - 20, bx, by); bp.quadTo(bx + 12, by - 20, bx + 30, by - 10 * f)
        c.drawPath(bp, paint("#3a2a4a", stroke=6))
    # superhero poster (original design: caped kid + star, no third-party marks)
    x, y = 760, 160
    outline(c, rrect(x, y, 260, 330, 8), "#fbf3e0", width=5)
    c.drawPath(rrect(x + 12, y + 12, 236, 306, 4), paint(shader=lin((0, y), (0, y + 330), ["#3050c0", "#80c0ff"])))
    c.save(); c.clipPath(rrect(x + 12, y + 12, 236, 306, 4))
    for i in range(10):
        a = i * .628 + t * .1 * anim
        c.drawPath(poly([(x + 130, y + 170), (x + 130 + math.cos(a) * 400, y + 170 + math.sin(a) * 400), (x + 130 + math.cos(a + .2) * 400, y + 170 + math.sin(a + .2) * 400)]), paint("#ffffff", a=.12))
    hy = y + 170 + 8 * math.sin(t * 1.5) * anim
    c.drawPath(poly([(x + 110, hy - 30), (x + 40, hy + 40), (x + 60, hy + 80), (x + 140, hy)]), paint("#e53a3a"))
    c.drawPath(rrect(x + 105, hy - 40, 60, 110, 26), paint("#f2c94c"))
    c.drawCircle(x + 135, hy - 62, 26, paint("#f3c9a2")); c.drawPath(oval(x + 135, hy - 78, 26, 12), paint("#2a1a10"))
    star4(c, x + 135, hy, 9, "#e53a3a", 1)
    c.drawLine(x + 150, hy - 30, x + 205, hy - 85, paint("#f2c94c", stroke=14))
    c.restore()
    # small kite pennant
    x, y = 1080, 200
    c.drawPath(poly([(x, y), (x + 140, y + 40), (x, y + 80)]), paint("#f2873a")); c.drawPath(poly([(x, y), (x + 140, y + 40), (x, y + 80)]), paint(INK, stroke=3))

def bed(c, x, y, t, cover=1.0, phase="front", blanket="#e86a5a"):
    """Bed in the corner; returns pillow position. phase 'front' = blanket drawn later."""
    c.drawPath(rrect(x - 40, y - 330, 40, 360, 10), paint("#a8754a")); c.drawPath(rrect(x - 40, y - 330, 40, 360, 10), paint(INK, stroke=4))
    c.drawPath(rrect(x, y - 120, 640, 120, 16), paint("#a8754a")); c.drawPath(rrect(x, y - 120, 640, 120, 16), paint(INK, stroke=4))
    c.drawPath(rrect(x + 10, y - 160, 620, 60, 26), paint("#f8f4ec"))
    c.drawPath(rrect(x + 20, y - 215, 190, 80, 34), paint("#ffffff")); c.drawPath(rrect(x + 20, y - 215, 190, 80, 34), paint(INK, stroke=3))
    return (x + 120, y - 175)

def blanket(c, x, y, t, cover=1.0, breathe=0.0, color="#e86a5a"):
    top = y - 170 - 12 * breathe
    p = smooth_path([(x + 225, top + 5), (x + 380, top - 15 + 4 * math.sin(t)), (x + 560, top - 5), (x + 650, y - 110), (x + 640, y - 60), (x + 205, y - 60), (x + 200, y - 120)], True, .5)
    c.drawPath(p, paint(color)); c.drawPath(p, paint(INK, stroke=4))
    c.save(); c.clipPath(p, doAntiAlias=True)
    for i in range(7): c.drawRect(skia.Rect.MakeLTRB(x + 210 + i * 66, top - 40, x + 240 + i * 66, y), paint("#f2a040", a=.5))
    c.restore()
    c.drawPath(rrect(x + 200, top - 6, 110, 30, 14), paint("#f8f4ec"))

# ================================================================== coop
def coop_scene(c, t):
    sky(c, "day")
    sky_clouds(c, t, speed=5)
    hills(c, t)
    c.drawRect(skia.Rect.MakeLTRB(0, 740, W, H), paint(shader=lin((0, 740), (0, H), ["#c9b070", "#a89050"])))
    rnd = random.Random(4)
    for i in range(300):
        x = rnd.uniform(0, W); y = rnd.uniform(750, H)
        c.drawLine(x, y, x + rnd.uniform(-10, 10), y - rnd.uniform(4, 10), paint("#e8d090", stroke=2.5, a=.8))
    # coop building
    x, y = 1100, 760
    outline(c, poly([(x, y), (x, y - 380), (x + 600, y - 380), (x + 600, y)]), "#c8502c", width=6)
    for i in range(1, 8): c.drawLine(x + i * 75, y - 375, x + i * 75, y - 5, paint("#a8402a", stroke=3))
    outline(c, poly([(x - 40, y - 370), (x + 300, y - 560), (x + 640, y - 370)]), "#5a4a3a", width=6)
    outline(c, rrect(x + 230, y - 220, 140, 220, 70), "#3a2418", width=0)
    c.drawPath(poly([(x + 230, y), (x + 120, y + 60), (x + 260, y + 60), (x + 370, y)]), paint("#b8864a"))
    for i in range(5): c.drawLine(x + 250 - i * 25, y + 10 + i * 10, x + 350 - i * 25, y + 10 + i * 10, paint("#8a6030", stroke=4))
    outline(c, rrect(x + 60, y - 300, 110, 80, 6), "#f4e3c4", width=4)
    text(c, "COOP", x + 470, y - 280, 44, "#fff1d0", weight=700, shadow=False)
    # wire fence
    for fx in range(0, 1080, 160):
        c.drawRect(skia.Rect.MakeLTRB(fx, 520, fx + 14, 800), paint("#8a6a4a"))
    for i in range(0, 1080, 26):
        c.drawLine(i, 540, i + 26, 790, paint("#c0c4c8", stroke=1.5, a=.7)); c.drawLine(i + 26, 540, i, 790, paint("#c0c4c8", stroke=1.5, a=.7))
    # scattered feathers on the ground
    for i in range(18):
        fx = rnd.uniform(200, 1800); fy = rnd.uniform(800, 1040)
        feather(c, fx, fy, rnd.uniform(0, 360), rnd.choice(["#ffffff", "#b5562a", "#f2e2c6", "#8a4a22"]), 1.0)

def feather(c, x, y, ang, color, s=1.0, a=1.0):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    f = skia.Path(); f.moveTo(0, -24); f.quadTo(10, 0, 0, 24); f.quadTo(-10, 0, 0, -24)
    c.drawPath(f, paint(color, a=a)); c.drawPath(f, paint(INK, stroke=2, a=.6 * a)); c.drawLine(0, -22, 0, 28, paint("#7a6050", stroke=1.5, a=a))
    c.restore()

# ================================================================== trucks
def garbage_truck(c, x, y, t, moving=0.0, s=1.0, face=-1):
    c.save(); c.translate(x, y); c.scale(s * face, s)
    bounce = 3 * math.sin(t * 20) * moving
    c.translate(0, bounce)
    c.drawPath(oval(0, 10, 460, 30), paint("#000000", a=.2, blur=12))
    # body (rear compactor at -x, cab at +x)
    body = rrect(-440, -330, 560, 290, 22)
    outline(c, body, "#3f9a5a", width=6)
    for i in range(5): c.drawLine(-420 + i * 110, -310, -420 + i * 110, -60, paint("#2f7a46", stroke=6))
    c.drawPath(rrect(-470, -300, 60, 240, 12), paint("#2f7a46")); c.drawPath(rrect(-470, -300, 60, 240, 12), paint(INK, stroke=4))
    c.save(); c.scale(face, 1); text(c, "CITY", -170 * face, -170, 64, "#f2f2e6", weight=700, shadow=False); c.restore()
    # cab
    cab = smooth_path([(130, -40), (130, -300), (290, -300), (360, -170), (380, -40)], True, .2)
    outline(c, cab, "#f2f2e6", width=6)
    c.drawPath(poly([(150, -280), (275, -280), (330, -170), (150, -170)]), paint("#9fcfe8")); c.drawPath(poly([(150, -280), (275, -280), (330, -170), (150, -170)]), paint(INK, stroke=4))
    c.drawPath(rrect(330, -130, 60, 30, 8), paint("#ffe9a0"))
    c.drawPath(rrect(120, -60, 280, 30, 8), paint("#9a9ea8"))
    # wheels
    for wx in (-320, -170, 260):
        c.save(); c.translate(wx, -20); c.rotate(-t * 360 * moving)
        c.drawCircle(0, 0, 62, paint("#2a2a30")); c.drawCircle(0, 0, 30, paint("#a8acb4"))
        for k in range(5): c.drawLine(0, 0, 26 * math.cos(k * 1.256), 26 * math.sin(k * 1.256), paint("#6a6e76", stroke=5))
        c.restore()
    # beacon
    on = 0.5 + 0.5 * math.sin(t * 10)
    c.drawPath(rrect(180, -330, 50, 26, 10), paint("#ffb020")); c.drawCircle(205, -320, 40, paint("#ffb020", a=.4 * on, blur=20))
    c.restore()

# ================================================================== dream worlds
def dream_sky(c, t, intensity=1.0, swirl=0.0, hue=0.0):
    a = ["#140b3a", "#3b1f78", "#8a4fb0"]; b = ["#0a1450", "#2050a0", "#40a0c0"]
    cols = [mix_c(rgb(x), rgb(y), hue) for x, y in zip(a, b)]
    c.drawPaint(paint(shader=lin((0, 0), (0, H), cols, [0, .6, 1])))
    for i in range(5):  # soft aurora ribbons
        y = 260 + i * 90 + 30 * math.sin(t * .3 + i)
        p = skia.Path(); p.moveTo(-100, y)
        for x in range(-100, W + 200, 200): p.lineTo(x, y + 60 * math.sin(x * .004 + t * .4 + i))
        c.drawPath(p, paint(["#ff9ad8", "#9affe0", "#ffe39a", "#a0b0ff", "#ffb0a0"][i], a=.14 * intensity, stroke=90, blur=40))
    if swirl > 0:
        for i in range(60):
            a = i * .37 + t * .5; r = 80 + i * 14
            c.drawCircle(W / 2 + math.cos(a) * r, H / 2 + math.sin(a) * r * .6, 3 + i * .08, paint("#fff3c0", a=.6 * swirl * (1 - i / 60)))

def honey_field(c, t, ripple_x=960):
    c.drawPaint(paint(shader=lin((0, 0), (0, H), ["#3a1f5a", "#a0507a", "#f2a050"])))
    for i in range(30):
        x = (i * 151) % W; y = 80 + (i * 97) % 360
        c.drawCircle(x, y, 2, paint("#fff3c0", a=.6))
    for k in range(3):  # honey hills
        y0 = 620 + k * 110
        p = skia.Path(); p.moveTo(-50, H)
        for x in range(-50, W + 100, 80): p.lineTo(x, y0 + 40 * math.sin(x * .004 + k + t * .2))
        p.lineTo(W + 50, H); p.close()
        c.drawPath(p, paint(["#e0901a", "#f0a828", "#f8c040"][k]))
        c.drawPath(p, paint("#fff0a0", a=.25, stroke=6))
    # honey drips & glossy blobs
    for i in range(14):
        x = 70 + i * 140; L = 60 + 40 * math.sin(i * 2.1 + t * .8)
        c.drawPath(rrect(x, 940, 26, L, 13), paint("#f8c040"))
        c.drawCircle(x + 13, 940 + L, 18, paint("#f8c040"))
        c.drawCircle(x + 8, 950, 5, paint("#ffffff", a=.6))
    for r in range(4):
        u = ((t * .5 + r / 4) % 1)
        c.drawPath(oval(ripple_x, 960, 80 + 300 * u, 16 + 50 * u), paint("#fff0a0", a=.5 * (1 - u), stroke=5))

def pool_memory(c, t, a=1.0):
    c.saveLayerAlpha(None, int(255 * a))
    c.drawPaint(paint(shader=lin((0, 0), (0, H), ["#bfe8ff", "#fff2c8"])))
    sun = (1500, 180)
    c.drawCircle(*sun, 240, paint("#fff6c0", a=.6, blur=80)); c.drawCircle(*sun, 80, paint("#fffbe0"))
    c.drawRect(skia.Rect.MakeLTRB(0, 560, W, H), paint("#f0e0c0"))
    pool = rrect(160, 620, 1600, 380, 60)
    c.drawPath(pool, paint("#ffffff")); c.drawPath(rrect(190, 650, 1540, 320, 40), paint(shader=lin((0, 650), (0, 970), ["#40c0e0", "#1a80c0"])))
    c.save(); c.clipPath(rrect(190, 650, 1540, 320, 40))
    for i in range(30):
        x = (i * 211 + t * 30) % 1700 + 150; y = 670 + (i * 53) % 290
        c.drawPath(oval(x, y, 40, 6), paint("#ffffff", a=.35))
    c.restore()
    # friends splashing (simple silhouettes, warm memory)
    for i, (fx, colr) in enumerate(((520, "#ff8a5a"), (900, "#ffd04a"), (1300, "#7ad07a"))):
        bob = 12 * math.sin(t * 3 + i * 2)
        c.drawCircle(fx, 760 + bob, 46, paint(["#f3c9a2", "#c98e68", "#e9b58f"][i])); c.drawPath(oval(fx, 730 + bob, 48, 26), paint(["#2a1a10", "#f2c060", "#5a2a1a"][i]))
        c.drawPath(oval(fx, 815 + bob, 70, 20), paint(colr, a=.9))
        for k in range(6):
            u = ((t * 1.2 + k / 6 + i * .3) % 1)
            ang = -math.pi / 2 + (k - 2.5) * .45
            c.drawCircle(fx + math.cos(ang) * 120 * u, 800 + math.sin(ang) * 160 * u + 200 * u * u, 8 * (1 - u) + 2, paint("#ffffff", a=.8 * (1 - u)))
        arm = math.sin(t * 5 + i) * 30
        c.drawLine(fx - 40, 790 + bob, fx - 80, 730 + bob + arm, paint(["#f3c9a2", "#c98e68", "#e9b58f"][i], stroke=18))
    c.drawPaint(paint(shader=rad((W / 2, H / 2), W * .7, [(255, 255, 255, 0), (255, 255, 255, 0), (255, 240, 220, 200)], [0, .5, 1])))
    c.restore()

def night_town(c, cam, t, lights=1.0, density=1.0, scroll=0.0, seed=1, y0=900, tint=0.0):
    """Night neighbourhood seen from above-ish: rows of houses w/ glowing windows."""
    rnd = random.Random(seed)
    for row in range(3):
        depth = .45 + row * .3
        cam.apply(c, depth, t)
        base = y0 + row * 90
        x = -1400 + (row * 170)
        while x < 7000:
            w = rnd.uniform(170, 260); h = rnd.uniform(120, 200)
            colr = mix_c((60, 50, 100), (40, 35, 80), row / 2)
            p = poly([(x, base), (x, base - h), (x + w / 2, base - h - 80), (x + w, base - h), (x + w, base)])
            c.drawPath(p, paint(colr)); c.drawPath(p, paint("#1a1030", stroke=3))
            for k in range(2):
                if rnd.random() < .75 * lights:
                    wx = x + 25 + k * (w - 90)
                    c.drawPath(rrect(wx, base - h + 40, 40, 36, 4), paint("#ffd27a"))
                    c.drawPath(rrect(wx - 20, base - h + 20, 80, 76, 20), paint("#ffcf70", a=.2, blur=16))
            if rnd.random() < .5:
                tree(c, x + w + 30, base, 150 + rnd.uniform(0, 80), t, seed=int(x) % 97, wind=.4,
                     colors=["#6a3a5a", "#8a4a5a", "#a8604a", "#5a3a6a"])
            x += w + rnd.uniform(40, 120)
        c.drawRect(skia.Rect.MakeLTRB(-2000, base, 8000, base + 400), paint(mix_c((40, 30, 70), (30, 25, 60), row / 2)))
        cam.done(c)

def speed_lines(c, t, a=1.0, n=40, cx=W / 2, cy=H / 2, seed=5, color="#ffffff"):
    rnd = random.Random(seed)
    for i in range(n):
        ang = rnd.uniform(0, 2 * math.pi)
        u = ((t * rnd.uniform(1.5, 3.0) + rnd.random()) % 1)
        r0 = 200 + u * 1200; r1 = r0 + 120 + 300 * u
        c.drawLine(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, cx + math.cos(ang) * r1, cy + math.sin(ang) * r1, paint(color, a=a * (1 - u) * .8, stroke=2 + 4 * u))

def horizontal_streaks(c, t, a=1.0, n=30, seed=6, color="#ffffff", speed=2.0):
    rnd = random.Random(seed)
    for i in range(n):
        y = rnd.uniform(0, H); L = rnd.uniform(150, 500)
        x = W + 300 - ((t * speed * rnd.uniform(800, 1600) + rnd.uniform(0, W)) % (W + 900))
        c.drawLine(x, y, x + L, y, paint(color, a=a * rnd.uniform(.3, .8), stroke=rnd.uniform(2, 5)))
