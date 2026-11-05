"""All scene compositions. scene_NN(c, ctx) draws one frame at ctx.t.
Scenes 1-8: the waking world.  Scenes 9-17: night & dreams (scenes_dream.py).
"""
import math, random
import skia
from engine import *
from characters import *
from environments import *

# ------------------------------------------------------------------ helpers
def cross(c, t, ts, d, fa, fb, color=None):
    """Dissolve from shot A to shot B starting at ts over d seconds."""
    if t < ts: fa(); return
    if t >= ts + d: fb(); return
    u = smooth((t - ts) / d)
    if color:  # dip through a colour
        if u < .5: fa(); fade(c, u * 2, color)
        else: fb(); fade(c, (1 - u) * 2, color)
        return
    fa(); c.saveLayerAlpha(None, int(255 * u)); fb(); c.restore()

def lying(c, who, x, y, s=1.0, head_left=True, **pose):
    """Character lying on their back; (x,y) = where their back meets the ground at the hips."""
    c.save(); c.translate(x, y); c.rotate(-90 if head_left else 90)
    st = STYLES[who]; hip = (st["leg"][0] + st["leg"][1]) * .96 * s
    if not pose.pop("keep_arms", False):
        pose["armF"] = (6, 14); pose["armB"] = (2, 14)
    draw_person(c, who, x=-28 * s if head_left else 28 * s, y=hip, s=s, face=1 if head_left else -1, **pose)
    c.restore()

SIT = dict(legF=(84, 4), legB=(80, 10))
def sit_pose(s=1.0, who="orion"):
    st = STYLES[who]; return dict(SIT, bob=(st["leg"][0] + st["leg"][1]) * .96 * s - 22 * s)

def chair_sit(s=1.0, who="orion"):
    st = STYLES[who]; return dict(legF=(84, 80), legB=(80, 84), bob=(st["leg"][0]) * s * .95)

def bubble(c, x, y, r, t, a, content, tail=(0, 0)):
    """Thought bubble at (x,y) with a trail of puffs toward tail point."""
    if a <= 0.01: return
    c.saveLayerAlpha(None, int(255 * clamp(a)))
    tx, ty = tail
    for k, rr in enumerate((10, 16, 24)):
        u = (k + 1) / 4
        c.drawCircle(lerp(tx, x, u), lerp(ty, y, u), rr, paint("#ffffff")); c.drawCircle(lerp(tx, x, u), lerp(ty, y, u), rr, paint(INK, stroke=3))
    b = blob(x, y, r, seed=5, n=11, jitter=.12, t=t, wob=.03)
    c.drawPath(b, paint("#ffffff")); c.drawPath(b, paint(INK, stroke=4))
    c.save(); c.clipPath(b, doAntiAlias=True); content(c, x, y, r); c.restore()
    c.restore()

def lightbulb(c, x, y, s, a, t):
    if a <= 0: return
    c.drawCircle(x, y, 90 * s, paint("#fff3a0", a=.45 * a, blur=40 * s))
    for i in range(8):
        ang = i * math.pi / 4 + t
        c.drawLine(x + math.cos(ang) * 50 * s, y + math.sin(ang) * 50 * s, x + math.cos(ang) * 75 * s, y + math.sin(ang) * 75 * s, paint("#ffd84a", a=a, stroke=6 * s))
    c.drawCircle(x, y, 32 * s, paint("#ffe866", a=a)); c.drawCircle(x, y, 32 * s, paint(INK, stroke=4 * s, a=a))
    c.drawPath(rrect(x - 14 * s, y + 26 * s, 28 * s, 22 * s, 5 * s), paint("#9a9ea8", a=a))

def birds(c, t, x0, y0, n=5, speed=120, s=1.0, color="#3a2a4a", seed=2, a=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x = x0 + t * speed + i * 70 + rnd.uniform(-20, 20); y = y0 + i * 26 * ((-1) ** i) + 10 * math.sin(t * 1.4 + i)
        f = math.sin(t * 7 + i * 1.3)
        p = skia.Path(); p.moveTo(x - 22 * s, y - 10 * f * s); p.quadTo(x - 8 * s, y - 14 * s, x, y); p.quadTo(x + 8 * s, y - 14 * s, x + 22 * s, y - 10 * f * s)
        c.drawPath(p, paint(color, stroke=4.5 * s, a=a))

def sweat(c, x, y, t, a=1.0):
    for i in range(2):
        u = (t * 1.2 + i * .5) % 1
        c.drawPath(heart_path(0, 0, 1), paint("#000000", a=0))  # noop keeps API warm
        dx = x + i * 30; dy = y + u * 40
        p = skia.Path(); p.moveTo(dx, dy - 14); p.quadTo(dx + 9, dy, dx, dy + 6); p.quadTo(dx - 9, dy, dx, dy - 14)
        c.drawPath(p, paint("#9fd8ff", a=a * (1 - u))); c.drawPath(p, paint(INK, a=a * (1 - u) * .6, stroke=2))

def zzz(c, x, y, t, a=1.0):
    for i in range(3):
        u = (t * .35 + i / 3) % 1
        text(c, "z", x + u * 60 + 10 * math.sin(t + i), y - u * 120, 34 + 26 * u, "#fff6d8", a=a * math.sin(u * math.pi), shadow=False, weight=700)

def grade(c, color, a, mode="multiply"):
    c.drawPaint(paint(color, a=a, blend=mode))

def dust(c, x, y, t, a=1.0, seed=0):
    rnd = random.Random(seed + int(t * 4))
    for i in range(4):
        c.drawCircle(x + rnd.uniform(-30, 30), y - rnd.uniform(0, 20), rnd.uniform(8, 18), paint("#d8c8a0", a=.5 * a, blur=4))

LEAVES_A = Particles(70, 1, (-200, -100, W + 200, H + 50))
LEAVES_B = Particles(40, 2, (-200, -100, W + 200, H + 50))
STARS_A = Particles(220, 3, (0, 0, W, H))
SPARK_A = Particles(40, 4, (0, 0, W, H))

def post(c, t, leaves=1.0, grain=True, vig=.35):
    if leaves: falling_leaves(c, t, LEAVES_A, wind=1.0, size=13, a=leaves)
    if vig: vignette(c, vig)
    if grain: paper_grain(c, t, .035)

# ================================================================== TITLE (0)
def scene_00(c, ctx):
    t = ctx.t
    sky(c, "golden", "sunset", .5, sun=(1450, 640, 70, "#ffd080"), t=t)
    sky_clouds(c, t, a=.8, tint="#ffe8d8", shade="#e8a0a0", speed=10)
    cam = Cam(960, 560, 1.0 + .03 * t / 9)
    cam.apply(c, .3, t); hills(c, t, "#d08a6a", None); cam.done(c)
    cam.apply(c, 1.0, t)
    hill = smooth_path([(-300, 1200), (-300, 900), (500, 820), (960, 800), (1500, 860), (2300, 940), (2300, 1200)], True, .5)
    c.drawPath(hill, paint(shader=lin((0, 780), (0, 1100), ["#a8b85a", "#6a8a3a"])))
    tree(c, 1560, 870, 560, t, seed=7, wind=1.2)
    flap = flap_pose(t, 1.2) if t > 2.5 else dict(armF=(20, 10), armB=(10, 10))
    draw_person(c, "orion", x=760, y=812, s=.8, t=t, wings="card", mouth="smile", look=(.3, -.8), **flap)
    cam.done(c)
    birds(c, t, -200, 300, n=5, speed=110, s=.9)
    a = ramp(t, 1.0, 3.0)
    c.save(); c.translate(0, 18 * (1 - ease_out(inv(1.0, 3.0, t))))
    text(c, "The Boy Who", W / 2, 270, 104, "#fff6e6", a=a, weight=700, glow="#ff9a50")
    text(c, "Wanted to Fly", W / 2, 395, 132, "#fff6e6", a=a, weight=700, glow="#ff9a50")
    c.restore()
    text(c, "Story by Jason Whitewolf", W / 2, 480, 46, "#fff0d8", a=ramp(t, 3.2, 4.8), weight=600)
    falling_leaves(c, t, LEAVES_A, 1.2, 14)
    vignette(c, .4); paper_grain(c, t, .035)

# ================================================================== SCENE 1
def scene_01(c, ctx):
    t = ctx.t
    def yard_shot():
        # pan down from the sky (birds) to Orion lying on the lawn
        up = ctx.s("thought")
        cam = cam_path(t, [(0, 1800, 140, 1.0), (5.0, 1800, 520, 1.15), (up, 1760, 640, 1.45), (ctx.s("garage"), 1500, 600, 1.2)])
        yard_world(c, cam, t, light=0, wind=1.0)
        cam.apply(c, 1.0, t)
        ph = ctx.phase(["intro", "thought", "idea"])
        if ph != "idea":
            if ph == "thought":
                u = ctx.u("thought", ease_out)
                draw_person(c, "orion", x=1760, y=GROUND, s=1.0, t=t, look=(.4, -.6), mouth="o", **sit_pose(1.0),
                            armF=(60, 30), armB=(50, 30), lean=-6) if u > .5 else lying(c, "orion", 1820, GROUND - 4, 1.0, t=t, eyes="open", look=(0, -1), mouth="smile", armF=(150, 40), armB=(140, 40))
            else:
                lying(c, "orion", 1820, GROUND - 4, 1.0, t=t, look=(0, -1), mouth="smile", armF=(150, 40), armB=(140, 40), legF=(10, 20), legB=(-5, 10))
        else:
            run = inv(ctx.e("idea") - .3, ctx.s("garage") + .2, t)
            x = lerp(1760, 1150, ease_in(run))
            pose = run_pose(t) if run > 0 else dict(armF=(198, -8), armB=(-10, 10))
            draw_person(c, "orion", x=x, y=GROUND, s=1.0, t=t, face=-1 if run > 0 else 1, mouth=ctx.mouth("O", "grin"), eyes="wide", **pose)
            lightbulb(c, 1770, 520, 1.0, ramp(t, ctx.s("idea"), ctx.s("idea") + .4) * (1 - ramp(t, ctx.e("idea"), ctx.e("idea") + .4)), t)
        cam.done(c)
        birds(c, t, -300, 220 - (cam.y - 140) * .3, n=6, speed=140)
        if ph == "thought":
            def content(cc, x, y, r):
                cc.drawPaint(paint("#bfe3f5"))
                draw_person(cc, "orion", x=x - 40, y=y + 40, s=.42, t=t, **fly_pose(t, "superman"), outfit="day")
                birds(cc, t * .5, x - 160, y - 60, n=3, speed=40, s=.6)
            bubble(c, 1300, 260, 170, t, ramp(t, ctx.s("thought") + .3, ctx.s("thought") + .8), content, tail=(980, 470))
        post(c, t, .9)
    def garage_shot():
        tg = t - ctx.s("garage")
        cam = cam_path(t, [(ctx.s("garage"), 900, 560, 1.0), (ctx.s("build"), 720, 640, 1.45), (ctx.dur, 700, 620, 1.6)])
        cam.apply(c, 1.0, t)
        garage_interior(c, t)
        building = ctx.at("build")
        # cardboard being cut on the bench
        if not building:
            box(c, 420, 560, 170, 120, 3)
            x = lerp(1300, 700, ease_out(inv(0, 2.0, tg)))
            fp = walk_pose(t) if tg < 2.0 else dict(armF=(70, 40), armB=(60, 30))
            draw_person(c, "orion", x=x, y=880, s=1.0, face=-1, t=t, mouth="smile", look=(-.2, .3), **fp)
            if tg > 2.0:
                scissors(c, 560, 540, -20, abs(math.sin(t * 6)) * .6 + .1, 1.1)
                tape_roll(c, 860, 545)
        else:
            u = ctx.u("build")
            for i in range(4):  # cut wing pieces on the bench
                if u < .4 + i * .1:
                    c.drawPath(poly([(240 + i * 150, 556), (340 + i * 150, 556), (300 + i * 150, 520)]), paint("#c99a62")); c.drawPath(poly([(240 + i * 150, 556), (340 + i * 150, 556), (300 + i * 150, 520)]), paint(INK, stroke=3))
            tape_roll(c, 860, 545); scissors(c, 980, 548, 10, .1)
            proud = u > .55
            pose = dict(armF=(lerp(40, 95, ramp(u, .5, .7)), 0), armB=(lerp(30, 85, ramp(u, .5, .7)), 0), mouth="grin" if proud else "smile", eyes="happy" if u > .8 else "open")
            draw_person(c, "orion", x=700, y=880, s=1.0, face=1, t=t, wings="card" if u > .25 else None, **pose)
            if u > .55:
                sparkles(c, t, SPARK_A, a=ramp(u, .55, .7) * .6, size=5)
        cam.done(c)
        vignette(c, .5); paper_grain(c, t, .03)
    cross(c, t, ctx.s("garage") - .3, .8, yard_shot, garage_shot)

# ================================================================== SCENE 2
def scene_02(c, ctx):
    t = ctx.t
    def yard_shot():
        rest, sun_t, call = ctx.s("rest"), ctx.s("sunset"), ctx.s("call")
        lt = ramp(t, rest + 1, ctx.s("scent"), smooth)
        lt2 = ramp(t, ctx.s("scent"), ctx.e("call"))
        mode, mode2, uu = ("day", "golden", lt) if lt2 <= 0 else ("golden", "sunset", lt2)
        sun = (lerp(1700, 1500, lt + lt2), lerp(-200, 760, lt * .5 + lt2 * .5), 80, "#ffd080")
        cam = cam_path(t, [(0, 1750, 600, 1.0), (rest, 1750, 600, 1.05), (sun_t, 1800, 460, 1.0), (ctx.s("scent"), 1300, 520, .95),
                            (call, 700, 600, 1.1), (ctx.e("call") + .5, 700, 620, 1.15)])
        yard_world(c, cam, t, light=.5 * lt + .5 * lt2, house_lights=lt2, smoke=ramp(t, ctx.s("scent"), ctx.s("scent") + 1), mode=mode, mode2=mode2, u=uu, sun=sun,
                   door=ramp(t, call - .5, call))
        cam.apply(c, 1.0, t)
        if t < rest:
            # run back and forth across the yard flapping, with hops
            ph = t * .23
            x = 1800 + 520 * math.sin(ph * 2 * math.pi)
            face = 1 if math.cos(ph * 2 * math.pi) > 0 else -1
            hop = max(0, math.sin(t * 2 * math.pi * .7)) ** 3
            frustrated = t > ctx.s("fail")
            pose = run_pose(t, 1.0, flap=True)
            pose["bob"] -= hop * 70
            draw_person(c, "orion", x=x, y=GROUND, s=1.0, face=face, t=t, wings="card",
                        mouth="open" if not frustrated else ("frown" if hop < .2 else "open"), eyes="open", brow=.8 if frustrated else .3, **pose)
            if hop < .05: dust(c, x - face * 40, GROUND, t, .8)
        else:
            st = ctx.s("rest")
            sitting_t = t - st
            u = ease_out(inv(0, .8, sitting_t))
            pose = sit_pose(1.0)
            sighing = sitting_t < 3
            if t < call:
                draw_person(c, "orion", x=1820, y=GROUND, s=1.0, t=t, wings="card" if t < call else None, look=(.3, -.5),
                            mouth="frown" if sighing else "smile", eyes="sleepy" if sighing else "open", armF=(40, 30), armB=(30, 30), **pose)
                if sighing: sweat(c, 1890, 580, t, 1 - ramp(sitting_t, 2, 3))
            else:
                # stands, waves, walks toward the house
                wu = inv(ctx.e("call"), ctx.e("call") + 4.0, t)
                x = lerp(1820, 640, ease_io(wu))
                pp = walk_pose(t) if 0 < wu < 1 else dict(armF=(198, -8), armB=(-5, 10))
                draw_person(c, "orion", x=x, y=GROUND, s=1.0, face=-1, t=t, mouth="grin", wings="card" if wu < .6 else None, **pp)
            if t >= call - .5:
                wave = math.sin(t * 8) * 25
                c.save(); c.translate(0, 0)
                draw_person(c, "mom", x=462, y=828, s=.72, face=1, t=t, mouth=ctx.mouth("M", "smile"), armF=(160 + wave, 10), armB=(10, 20))
                c.restore()
        cam.done(c)
        post(c, t, 1.0 - .4 * lt2)
    def dinner_shot():
        cam = cam_path(t, [(ctx.s("dinner"), 960, 640, 1.3), (ctx.dur, 960, 660, 1.45)])
        cam.apply(c, 1.0, t)
        kitchen(c, t, "evening")
        draw_person(c, "dad", x=1350, y=860, s=.9, face=-1, t=t, mouth="smile", armF=(70, 40), armB=(60, 30), **chair_sit(.9, "dad"))
        draw_person(c, "mom", x=560, y=860, s=.9, face=1, t=t, mouth="smile", armF=(70, 40), armB=(60, 30), **chair_sit(.9, "mom"))
        chew = math.sin(t * 9)
        draw_person(c, "orion", x=950, y=880, s=.9, face=1, t=t, mouth="grin" if chew > 0 else "smile", eyes="happy",
                    armF=(80 + 15 * chew, 50), armB=(60, 40), **chair_sit(.9))
        table(c, 960, 760, 1000, "spaghetti", 1.0 - .5 * inv(ctx.s("dinner") + 1, ctx.dur, t), t)
        cam.done(c)
        grade(c, "#ffc890", .15, "multiply"); vignette(c, .45); paper_grain(c, t, .03)
    cross(c, t, ctx.s("dinner") - .4, .9, yard_shot, dinner_shot)

# ================================================================== SCENE 3
def scene_03(c, ctx):
    t = ctx.t
    def dishes():
        cam = Cam(640, 620, 1.35 + .01 * t)
        cam.apply(c, 1.0, t)
        kitchen(c, t, "evening")
        draw_person(c, "dad", x=300, y=900, s=.95, face=1, t=t, mouth="smile", armF=(75 + 10 * math.sin(t * 5), 50), armB=(65, 40))
        draw_person(c, "orion", x=640, y=920, s=1.0, face=-1, t=t, mouth="smile", armF=(70 + 20 * math.sin(t * 4), 70), armB=(60, 60))
        # plate being dried with a towel
        hx, hy = 560, 690 + 12 * math.sin(t * 4)
        c.drawPath(oval(hx, hy, 40, 40), paint("#ffffff")); c.drawPath(oval(hx, hy, 40, 40), paint(INK, stroke=3))
        c.drawPath(rrect(hx - 20 + 10 * math.sin(t * 8), hy - 30, 50, 60, 10), paint("#5aa8d8"))
        draw_person(c, "mom", x=1020, y=900, s=.95, face=-1, t=t, mouth="smile", armF=(150, 20), armB=(20, 20))
        for i in range(6):  # soap bubbles
            u = (t * .3 + i / 6) % 1
            c.drawCircle(260 + 40 * math.sin(i * 2 + t), 560 - u * 300, 8 + 6 * math.sin(i), paint("#ffffff", a=.6 * (1 - u), stroke=2))
        cam.done(c)
        grade(c, "#ffc890", .12); vignette(c, .45); paper_grain(c, t, .03)
    def climb():
        st = ctx.s("stairs")
        u = inv(st + .3, st + 4.5, t)
        cam = cam_path(t, [(st, 1000, 700, 1.0), (st + 4.5, 1350, 380, 1.05)])
        cam.apply(c, 1.0, t)
        stairs_hall(c, t)
        i = u * 11
        x = 760 + i * 80; y = 960 - math.floor(i + .5) * 62
        draw_person(c, "orion", x=x, y=y, s=1.0, face=1, t=t, mouth="smile", look=(.4, -.3), **walk_pose(t, .8, .8))
        cam.done(c)
        grade(c, "#ffc890", .12); vignette(c, .45); paper_grain(c, t, .03)
    def room():
        wt, bt = ctx.s("walls"), ctx.s("bed")
        lamp = 1 - .85 * ramp(t, ctx.s("sleep") + 1.5, ctx.s("sleep") + 3.5)
        cam = cam_path(t, [(ctx.s("stairs") + 4.8, 960, 540, 1.0), (wt, 560, 420, 1.25), (wt + 4, 900, 460, 1.25), (bt, 960, 560, 1.0),
                           (ctx.s("sleep"), 980, 640, 1.35), (ctx.dur, 1000, 660, 1.5)])
        cam.apply(c, 1.0, t)
        bedroom(c, t, "night", lamp=lamp)
        bx, by = 380, 900
        bed(c, bx, by, t)
        if t < bt:
            draw_person(c, "orion", x=1000, y=960, s=1.0, face=-1, t=t, mouth="smile", eyes="open", look=(-.3, -.8), head_tilt=-6)
        else:
            u = inv(bt, bt + 1.2, t)
            if u < 1:
                draw_person(c, "orion", x=lerp(1000, 720, u), y=960, s=1.0, face=-1, t=t, outfit="pajama", mouth="smile", **walk_pose(t, .7, .6))
            else:
                sl = ctx.at("sleep", .8)
                lying(c, "orion", bx + 270, by - 195, 1.0, t=t, outfit="pajama", eyes="closed" if sl else "open", mouth="smile",
                      armF=(150, 30), armB=(140, 30))
                blanket(c, bx, by, t, breathe=.5 + .5 * math.sin(t * 1.4))
                if sl: zzz(c, bx + 200, by - 330, t, ramp(t, ctx.s("sleep") + 1.5, ctx.s("sleep") + 2.5))
        cam.done(c)
        vignette(c, .55); paper_grain(c, t, .03)
    def a():
        cross(c, t, ctx.s("stairs") - .3, .7, dishes, climb)
    cross(c, t, ctx.s("stairs") + 4.6, .7, a, room)

# ================================================================== SCENE 4
def scene_04(c, ctx):
    t = ctx.t
    def morning_room():
        cam = cam_path(t, [(0, 980, 640, 1.4), (ctx.s("run"), 900, 560, 1.1)])
        cam.apply(c, 1.0, t)
        bedroom(c, t, "day", lamp=0)
        light_rays(c, 1480, 150, t, a=.12, ang0=125)
        bx, by = 380, 900
        bed(c, bx, by, t)
        up = ease_out(inv(.4, 1.2, t))
        if t < ctx.s("run"):
            # pops up sitting in bed, eyes wide
            draw_person(c, "orion", x=bx + 210, y=by - 40 - 6 * up, s=1.0, face=1, t=t, outfit="pajama",
                        mouth=ctx.mouth("O", "grin"), eyes="wide" if up > .5 else "closed",
                        armF=(lerp(20, 198, ramp(t, ctx.s("idea"), ctx.s("idea") + .4)), -8), armB=(30, 20), squash=lerp(.6, 1.0, up))
            blanket(c, bx, by, t)
            def content(cc, x, y, r):
                cc.drawPaint(paint("#fff6e0"))
                for i in range(7): feather(cc, x - 80 + i * 26, y + 10 + 20 * math.sin(i), -30 + i * 10, ["#ffffff", "#b5562a", "#f2e2c6"][i % 3], 1.5)
                c2 = cc; c2.drawPath(poly([(x - 120, y - 40), (x + 110, y - 40), (x + 80, y - 5), (x - 100, y - 5)]), paint("#c99a62"))
            bubble(c, bx + 520, by - 520, 150, t, ramp(t, ctx.s("idea"), ctx.s("idea") + .4), content, tail=(bx + 300, by - 380))
        cam.done(c)
        vignette(c, .4); paper_grain(c, t, .03)
    def stairs_down():
        rs = ctx.s("run")
        mom_t = ctx.s("mom")
        slow = t > mom_t + .4
        u = inv(rs, mom_t + .4, t) * .75 + (inv(mom_t + .4, ctx.e("yes") + .8, t) * .25 if slow else 0)
        cam = cam_path(t, [(rs, 1350, 400, 1.0), (mom_t, 1000, 600, .95)])
        cam.apply(c, 1.0, t)
        stairs_hall(c, t)
        i = (1 - u) * 11
        x = 760 + i * 80; y = 960 - math.floor(i + .5) * 62
        if not slow:
            draw_person(c, "orion", x=x, y=y, s=1.0, face=-1, t=t, mouth=ctx.mouth("O", "grin"), eyes="wide", **run_pose(t, 1.2))
        else:
            draw_person(c, "orion", x=x, y=y, s=1.0, face=-1, t=t, mouth=ctx.mouth("O", "flat"), brow=-.4, **walk_pose(t, .5, .5))
        ma = ramp(t, mom_t - .5, mom_t)
        if ma > 0:
            draw_person(c, "mom", x=lerp(80, 250, ma), y=1000, s=1.0, face=1, t=t, mouth=ctx.mouth("M", "flat"),
                        armF=(30, 120), armB=(30, 120), brow=-.5)
        cam.done(c)
        vignette(c, .4); paper_grain(c, t, .03)
    def breakfast():
        ps = ctx.s("pancakes")
        cam = cam_path(t, [(ps, 960, 620, 1.3), (ctx.s("groan"), 920, 600, 1.25), (ctx.s("eat"), 960, 620, 1.3), (ctx.s("leap"), 1060, 600, 1.15)])
        cam.apply(c, 1.0, t)
        kitchen(c, t, "morning")
        light_rays(c, 960, 140, t, a=.1)
        leap = ctx.s("leap")
        lu = t - leap
        tip = 0
        if lu > 0:
            tip = 35 * math.sin(min(lu * 5, math.pi)) if lu < 1.5 else 0
        chair(c, 900, 860, face=1, tip=tip if lu < 1.5 else 0)
        draw_person(c, "mom", x=1320, y=880, s=.95, face=-1, t=t, mouth=ctx.mouth("M", "smile"),
                    armF=(lerp(70, 40, ramp(t, ctx.s("eat"), ctx.s("eat") + 1)), 40), armB=(30, 30))
        eat_u = inv(ctx.s("eat"), ctx.e("eat"), t)
        if lu < .2:
            chew = math.sin(t * 10) if eat_u > 0 and eat_u < 1 else 0
            mouth = ctx.mouth("O", "frown" if ctx.at("groan") and not ctx.at("eat") else "smile")
            if 0 < eat_u < 1: mouth = "grin" if chew > 0 else "smile"
            draw_person(c, "orion", x=950, y=870, s=.95, face=1, t=t, mouth=mouth, eyes="happy" if ctx.at("yes2") else "open",
                        brow=.6 if ctx.at("groan") and not ctx.at("eat") else 0, armF=(80 + 20 * chew, 60), armB=(60, 40), **chair_sit(.95))
        else:
            # leaps up, fixes chair, then dashes out to the right
            ru = inv(leap + 1.6, ctx.dur - .3, t)
            if lu < 1.6:
                draw_person(c, "orion", x=1000, y=860, s=.95, face=-1 if lu > .6 else 1, t=t, mouth="o" if lu < .8 else "smile",
                            armF=(60, 40) if lu > .6 else (200, -10), armB=(50, 40) if lu > .6 else (190, -10), bob=-40 * math.sin(min(lu * 4, math.pi)))
            else:
                draw_person(c, "orion", x=lerp(1000, 2200, ease_in(ru)), y=860, s=.95, face=1, t=t, mouth="grin", **run_pose(t, 1.2))
        table(c, 960, 760, 900, "pancakes", 1.0 - eat_u, t, settings=3)
        cam.done(c)
        vignette(c, .4); paper_grain(c, t, .03)
    def a(): cross(c, t, ctx.s("run") - .3, .6, morning_room, stairs_down)
    cross(c, t, ctx.s("pancakes") - .3, .7, a, breakfast)

# ================================================================== SCENE 5
def scene_05(c, ctx):
    t = ctx.t
    tape, out = ctx.s("tape"), ctx.s("out")
    cam = cam_path(t, [(0, 960, 520, 1.0), (ctx.s("peck"), 820, 640, 1.35), (tape, 900, 600, 1.2), (ctx.s("work"), 860, 560, 1.35), (out, 960, 540, 1.0)])
    cam.apply(c, 1.0, t)
    coop_scene(c, t)
    # background chickens wandering
    for i, (cx0, colr) in enumerate(((1250, "#ffffff"), (1480, "#f2e2c6"), (1650, "#ffffff"), (300, "#c8743a"))):
        x = cx0 + 60 * math.sin(t * .4 + i * 2)
        face = 1 if math.cos(t * .4 + i * 2) > 0 else -1
        peck = max(0, math.sin(t * 3 + i * 1.7)) ** 4
        chicken(c, x, 960 - (i % 2) * 40, .95, t, face, peck, colr, seed=i)
    if t < tape:
        # gathering feathers: bending down, picking up
        u = inv(0, tape, t)
        x = lerp(500, 820, u)
        bend = max(0, math.sin(t * 2.2)) ** 2
        draw_person(c, "orion", x=x, y=980, s=1.0, face=1, t=t, mouth="grin" if ctx.at("peck") else "smile",
                    eyes="happy" if ctx.at("peck") and math.sin(t * 3) > 0 else "open",
                    lean=28 * bend, armF=(30 + 60 * bend, 20), armB=(10, 40), look=(.2, .6 * bend))
        for k in range(int(u * 6)):
            feather(c, x - 50 + k * 8, 780 + 4 * k, -50 + k * 15, ["#ffffff", "#b5562a", "#f2e2c6"][k % 3], .8)
        # mischievous chicken sneaking up and pecking at shoes
        if ctx.at("peck"):
            pk = max(0, math.sin(t * 6)) ** 6
            chicken(c, x - 120, 990, 1.0, t, 1, pk * .9, "#c8743a", seed=9)
    else:
        # sitting on an upturned bucket taping feathers onto the wings
        x = 820
        c.drawPath(rrect(x - 60, 922, 120, 62, 12), paint("#7a8a9a")); c.drawPath(rrect(x - 60, 922, 120, 62, 12), paint(INK, stroke=4))
        u = inv(tape, ctx.s("work"), t)
        working = t < ctx.s("work")
        armF = (95 + 15 * math.sin(t * 6), 20) if working else (198, -8)
        draw_person(c, "orion", x=x, y=980, s=1.0, face=1, t=t, mouth=ctx.mouth("O", "grin"), eyes="open",
                    wings="feather" if u > .35 or not working else "card", armF=armF, armB=(70, 30), bob=33, legF=(80, 80), legB=(75, 85))
        if working: tape_roll(c, x + 150, 760)
        # chicken tugging the hem of his shirt
        tug = math.sin(t * 7)
        chicken(c, x - 140 + 6 * tug, 990, 1.0, t, 1, .5 + .4 * tug, "#c8743a", seed=9)
        c.drawLine(x - 100 + 6 * tug, 930, x - 50, 880, paint("#f2873a", stroke=6))
        if t > out:
            pass
    cam.done(c)
    if t > out:
        fade(c, 0)
    vignette(c, .35); paper_grain(c, t, .03)

# ================================================================== SCENE 6
def scene_06(c, ctx):
    t = ctx.t
    col_t, spark, lad = ctx.s("collapse"), ctx.s("spark"), ctx.s("ladder")
    cam = cam_path(t, [(0, 1100, 600, 1.2), (ctx.s("run"), 1400, 600, 1.05), (col_t, 2000, 650, 1.35), (lad, 1800, 620, 1.2), (lad + 3, 1500, 600, 1.0), (ctx.dur, 1700, 600, 1.0)])
    yard_world(c, cam, t, light=.1)
    cam.apply(c, 1.0, t)
    rs = ctx.s("run")
    if t < rs:
        crouch = ramp(t, .2, ctx.e("go"))
        draw_person(c, "orion", x=1100, y=GROUND, s=1.0, face=1, t=t, wings="feather", mouth=ctx.mouth("O", "grin"), brow=.6,
                    lean=15 * crouch, legF=(25 * crouch, 50 * crouch), legB=(-25 * crouch, 60 * crouch), bob=25 * crouch, armF=(-30, 20), armB=(-40, 20))
    elif t < col_t:
        u = inv(rs, col_t, t)
        x = 1100 + 1100 * u
        pose = run_pose(t, 1.2, flap=True)
        hop = max(0, math.sin(t * 2 * math.pi * .9)) ** 3
        pose["bob"] -= hop * 60
        draw_person(c, "orion", x=x, y=GROUND, s=1.0, face=1, t=t, wings="feather", mouth="open", brow=.9, **pose)
        rnd = random.Random(1)
        for k in range(14):  # feathers coming loose and drifting behind
            ft = t - rs - k * .45
            if ft > 0:
                fx = 1100 + 1100 * inv(rs, col_t, rs + k * .45) - ft * 60
                fy = GROUND - 260 + ft * 80 + 30 * math.sin(ft * 3 + k)
                if fy < GROUND: feather(c, fx, fy, ft * 120 + k * 30, ["#ffffff", "#b5562a", "#f2e2c6"][k % 3], .9)
        if u > .5: sweat(c, x + 30, GROUND - 340, t)
        if hop < .05: dust(c, x - 40, GROUND, t)
    elif t < lad:
        x = 2200
        if t < spark:
            lying(c, "orion", x + 40, GROUND - 4, 1.0, t=t, wings="feather", eyes="closed", mouth="open", armF=(170, 10), armB=(150, 10))
            sweat(c, x - 200, GROUND - 80, t)
        else:
            draw_person(c, "orion", x=x, y=GROUND, s=1.0, face=1, t=t, wings="feather", mouth=ctx.mouth("O", "grin"), eyes="wide",
                        armF=(198, -8), armB=(30, 20), bob=-30 * math.sin(min(1, (t - spark) * 3) * math.pi))
            lightbulb(c, x + 20, GROUND - 450, 1.1, ramp(t, spark, spark + .3) * (1 - ramp(t, lad - .5, lad)), t)
    else:
        u = inv(lad, lad + 2.2, t)
        u2 = inv(lad + 2.6, ctx.dur - .5, t)
        if u < 1:
            draw_person(c, "orion", x=lerp(2200, 900, ease_in(u)), y=GROUND, s=1.0, face=-1, t=t, wings="feather", mouth="grin", **run_pose(t, 1.2))
        else:
            x = lerp(900, 1900, ease_out(u2))
            draw_person(c, "orion", x=x, y=GROUND, s=1.0, face=1, t=t, wings="feather", mouth="grin", armF=(160, -30), armB=(150, -30), **{k: v for k, v in walk_pose(t, 1.3).items() if k.startswith("leg") or k == "bob"})
            ladder_draw(c, x - 20, GROUND - 330, 360, lean=90)
            rake(c, x + 40, GROUND - 300, -60, .8)
    cam.done(c)
    post(c, t, .8)

# ================================================================== SCENE 7
PILE_X, LADDER_X, LADDER_H = 2120, 1860, 430
def scene_07(c, ctx):
    t = ctx.t
    rk, jp, sp, ag = ctx.s("rake"), ctx.s("jump"), ctx.s("splash"), ctx.s("again")
    pile_u = ramp(t, rk, ctx.e("rake") - 1.5)
    cam = cam_path(t, [(0, 900, 400, .85), (rk - .5, 2300, 420, .9), (rk + .5, 2000, 620, 1.05), (jp, 1990, 520, .95), (sp, 2040, 560, 1.0), (ag, 2000, 560, .95), (ctx.dur, 2020, 560, 1.05)])
    ladder = (LADDER_X, GROUND, LADDER_H) if t > ctx.e("rake") - 1.2 else None
    yard_world(c, cam, t, light=.15, wind=1.3, leaves_on_ground=1.0 - .5 * pile_u,
               pile=(PILE_X, GROUND + 10, 140 + 300 * pile_u, 40 + 150 * pile_u, t) if pile_u > 0 else None, ladder=ladder)
    cam.apply(c, 1.0, t)
    top_y = GROUND - LADDER_H + 20
    start1 = ctx.e("rake") - 1.2
    # jump cycles: (start, run_back, climb, flap, jump, sit)
    cycles = []; cs = start1
    first = True
    while cs < ctx.dur:
        parts = (0.0, 2.6, 1.4, .9, 2.2) if first else (.8, 2.0, 1.0, .9, 1.6)
        cycles.append((cs, parts)); cs += sum(parts); first = False
    if t < rk:
        draw_person(c, "orion", x=1650, y=GROUND, s=1.0, face=1, t=t, wings="feather", mouth="smile", look=(.3, -.8), head_tilt=-8)
    elif t < start1:
        sw = math.sin(t * 4)
        x = PILE_X - 260 + 40 * sw
        draw_person(c, "orion", x=x, y=GROUND, s=1.0, face=1, t=t, wings="feather", mouth="smile", armF=(55 + 25 * sw, 30), armB=(45 + 25 * sw, 30), lean=10)
        rake(c, x + 50, GROUND - 200, -40 - 25 * sw, .9)
    else:
        for cs, (rb, cl, fl, jp_, sit) in cycles:
            lt = t - cs
            if lt < 0 or lt >= rb + cl + fl + jp_ + sit: continue
            if lt < rb:
                draw_person(c, "orion", x=lerp(PILE_X, LADDER_X - 10, lt / rb), y=GROUND, s=1.0, face=-1, t=t, wings="feather", mouth="laugh", **run_pose(t))
            elif lt < rb + cl:
                u = (lt - rb) / cl
                step = math.sin(lt * 9)
                draw_person(c, "orion", x=LADDER_X - 10, y=lerp(GROUND, top_y, u), s=1.0, face=1, t=t, wings="feather", mouth="grin",
                            armF=(165 + 15 * step, -20), armB=(165 - 15 * step, -20), legF=(30 + 30 * step, 60), legB=(30 - 30 * step, 60))
            elif lt < rb + cl + fl:
                draw_person(c, "orion", x=LADDER_X, y=top_y, s=1.0, face=1, t=t, wings="feather", mouth="grin", brow=.5, **flap_pose(t, 3))
            elif lt < rb + cl + fl + jp_:
                u = (lt - rb - cl - fl) / jp_
                x = lerp(LADDER_X, PILE_X, u); y = lerp(top_y, GROUND - 40, u) - 160 * math.sin(u * math.pi)
                draw_person(c, "orion", x=x, y=y, s=1.0, face=1, t=t, wings="feather", mouth="open", eyes="wide", lean=40 * u, **flap_pose(t, 5))
            else:
                l4 = lt - rb - cl - fl - jp_
                draw_person(c, "orion", x=PILE_X - 20, y=GROUND - 30, s=1.0, face=1, t=t, wings="feather", eyes="happy", mouth="laugh",
                            armF=(200, -10), armB=(190, -10), lean=14 * math.sin(l4 * 6), **sit_pose(1.0))
        for cs, (rb, cl, fl, jp_, sit) in cycles:
            leaf_burst(c, PILE_X, GROUND - 60, cs + rb + cl + fl + jp_, t, n=80, seed=int(cs * 10))
    cam.done(c)
    falling_leaves(c, t, LEAVES_A, 1.3, 14); falling_leaves(c, t * 1.2, LEAVES_B, 1.0, 18)
    vignette(c, .35); paper_grain(c, t, .03)

# ================================================================== SCENE 8
def scene_08(c, ctx):
    t = ctx.t
    tr, kn, lv, pr = ctx.s("truck"), ctx.s("kneel"), ctx.s("leave"), ctx.s("promise")
    stop_t = tr + 3.2
    truck_x = lerp(4400, 2800, ease_out(inv(tr, stop_t, t))) if t < lv + 1.5 else lerp(2800, -600, ease_in(inv(lv + 1.5, pr + 3, t)))
    moving = 1.0 if (t < stop_t - .3 or t > lv + 1.5) else 0.0
    # driver walking: truck -> Orion -> truck
    walk_in = inv(stop_t + .2, kn + 2.5, t); walk_out = inv(lv, lv + 1.4, t)
    dx = lerp(2700, 2330, ease_io(walk_in)) if walk_out <= 0 else lerp(2330, 2700, ease_io(walk_out))
    talking_cam = {"ask": (2200, 640, 1.8), "reply": (2130, 700, 1.9), "dreams": (2260, 620, 1.7), "how": (2120, 700, 2.0), "practice": (2260, 630, 1.8)}
    keys = [(0, 2300, 650, .8), (tr + 1, 2600, 650, .8), (stop_t, 2400, 650, .9), (kn + 2, 2250, 680, 1.2)]
    for tag in ("ask", "reply", "chuckle", "dreams", "how", "practice"):
        x, y, z = talking_cam.get(tag, (2220, 660, 1.5))
        keys.append((ctx.s(tag) + .2, x, y, z))
    keys += [(lv, 2400, 650, .9), (pr, 2140, 700, 1.5), (pr + 4.5, 2140, 520, 1.25), (ctx.dur, 2140, 380, 1.1)]
    cam = cam_path(t, keys)
    yard_world(c, cam, t, light=.2, pile=(PILE_X, GROUND + 10, 440, 190, t))
    cam.apply(c, 1.0, t)
    kneeling = kn + 2.5 < t < lv
    talk = ctx.talking("G")
    if walk_in > 0 and (walk_out < 1):
        if kneeling:
            draw_person(c, "driver", x=dx, y=GROUND + 4, s=.92, face=-1, t=t, mouth=ctx.mouth("G", "smile"), eyes="open",
                        legF=(80, 90), legB=(-10, 100), bob=60, armF=(70 + (15 * math.sin(t * 3) if talk else 0), 40), armB=(40, 40), lean=-5)
        else:
            wp = walk_pose(t, .8)
            if walk_out > .3: wp["armF"] = (160 + 20 * math.sin(t * 8), 0)
            draw_person(c, "driver", x=dx, y=GROUND + 4, s=.92, face=-1 if walk_out <= 0 else 1, t=t, mouth="smile", **wp)
    # Orion sitting in the leaf pile
    if t < pr:
        draw_person(c, "orion", x=PILE_X - 40, y=GROUND - 30, s=1.0, face=1, t=t, wings="feather", mouth=ctx.mouth("O", "smile"),
                    eyes="wide" if ctx.at("dreams") and not ctx.at("practice") else "open", look=(.4, -.3),
                    armF=(lerp(40, 198, ramp(t, lv + .8, lv + 1.2)) + (20 * math.sin(t * 9) if lv + .8 < t < pr else 0), 20), armB=(40, 30), **sit_pose(1.0))
    else:
        lying(c, "orion", PILE_X + 10, GROUND - 60, 1.0, t=t, wings="feather", look=(0, -1), mouth="smile", armF=(160, 40), armB=(150, 40))
    c.restore() if False else None
    # truck on the street in front
    cam.done(c)
    cam.apply(c, 1.0, t)
    garbage_truck(c, truck_x, 1118, t, moving, .72, face=-1)
    cam.done(c)
    if t > pr:
        birds(c, t - pr, 200, 300, n=4, speed=90, s=1.0, a=ramp(t, pr + 1.5, pr + 3))
    falling_leaves(c, t, LEAVES_B, .8, 14)
    vignette(c, .35); paper_grain(c, t, .03)

from scenes_dream import *  # noqa: E402,F401,F403
