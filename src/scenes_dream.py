"""Scenes 9-17 (night and dreams) plus closing credits (18)."""
import math, random
import skia
from engine import *
from characters import *
from environments import *
import scenes as S

DREAM_SPARK = Particles(60, 21, (0, 0, W, H))
DREAM_STARS = Particles(260, 22, (0, 0, W, H))
DEEP_STARS = Particles(420, 23, (-400, -400, W + 400, H + 400))

def dream_post(c, t, a=1.0, vig=.45):
    sparkles(c, t, DREAM_SPARK, a=.5 * a, size=4)
    vignette(c, vig, "#0a0420"); paper_grain(c, t, .025)

def trail(c, pts, color="#fff3c0", width=18, a=1.0):
    if len(pts) < 2: return
    for i in range(1, len(pts)):
        u = i / len(pts)
        c.drawLine(*pts[i - 1], *pts[i], paint(color, a=a * u * .7, stroke=width * u, blur=3))

# ================================================================== SCENE 9
def scene_09(c, ctx):
    t = ctx.t
    pa, sl = ctx.s("parents"), ctx.s("sleep")
    lamp = 1 - .9 * ramp(t, sl + 2.5, sl + 4.5)
    cam = cam_path(t, [(0, 900, 620, 1.2), (pa, 960, 560, 1.0), (ctx.s("ask"), 820, 520, 1.45), (ctx.s("dad"), 1050, 450, 1.4), (sl, 900, 620, 1.2), (ctx.dur, 760, 700, 1.8)])
    cam.apply(c, 1.0, t)
    bedroom(c, t, "night", lamp=lamp)
    bx, by = 380, 900
    bed(c, bx, by, t)
    asleep = t > sl + 3.0
    S.lying(c, "orion", bx + 270, by - 195, 1.0, t=t, outfit="pajama", eyes="closed" if asleep else ("happy" if ctx.at("dad") else "open"),
            mouth=ctx.mouth("O", "smile"), look=(.5, 0), armF=(150, 30), armB=(140, 30))
    S.blanket(c, bx, by, t, breathe=.5 + .5 * math.sin(t * 1.3)) if hasattr(S, "blanket") else blanket(c, bx, by, t, breathe=.5 + .5 * math.sin(t * 1.3))
    # parents come in from the right, kiss, smile, and slip out
    enter = ease_out(inv(pa, pa + 2.2, t)); leave = ease_in(inv(sl + 1.8, sl + 4.0, t))
    if enter > 0 and leave < 1:
        mx = lerp(1900, 760, enter) + leave * 1300; dxp = lerp(2100, 1060, enter) + leave * 1300
        kiss = ramp(t, pa + 2.4, pa + 3.2) * (1 - ramp(t, pa + 4.2, pa + 5))
        draw_person(c, "mom", x=mx, y=960, s=1.0, face=-1, t=t, mouth="smile", eyes="happy" if kiss > .5 else "open",
                    lean=-38 * kiss, armF=(60 + 40 * kiss, 30), armB=(40, 30), hair_wind=-.5 * kiss)
        if kiss > .3:
            for k in range(3):
                u = (t * .7 + k / 3) % 1
                c.drawPath(heart_path(mx - 180 + 20 * k, 560 - u * 120, 12), paint("#ff7a9a", a=(1 - u) * kiss))
        draw_person(c, "dad", x=dxp, y=960, s=1.0, face=-1, t=t, mouth=ctx.mouth("D", "smile"), eyes="happy" if ctx.at("sleep") else "open",
                    armF=(30, 40), armB=(20, 30))
    if asleep: S.zzz(c, bx + 220, by - 330, t, ramp(t, sl + 3, sl + 4))
    cam.done(c)
    # dreamy swirl as he drifts off
    sw = ramp(t, ctx.dur - 3.0, ctx.dur)
    if sw > 0:
        c.drawPaint(paint("#3b1f78", a=.5 * sw, blend="screen"))
        sparkles(c, t, DREAM_SPARK, a=sw, size=6)
    vignette(c, .55); paper_grain(c, t, .03)

# ================================================================== SCENE 10
def scene_10(c, ctx):
    t = ctx.t
    rm, hn, st, pl = ctx.s("remember"), ctx.s("honey"), ctx.s("stuck"), ctx.s("pool")
    def window_shot():
        tap = max(0, math.sin(t * 2 * math.pi * .9)) ** 8
        cam = cam_path(t, [(0, 1480, 330, 2.2), (rm, 1300, 420, 1.6)])
        cam.apply(c, 1.0, t)
        bedroom(c, t, "night", lamp=.1, branch_tap=tap)
        bx, by = 380, 900
        bed(c, bx, by, t)
        S.lying(c, "orion", bx + 270, by - 195, 1.0, t=t, outfit="pajama", eyes="closed", mouth="smile" if tap < .5 else "flat",
                brow=.4 * tap, armF=(150, 30), armB=(140, 30))
        blanket(c, bx, by, t)
        cam.done(c)
        if tap > .3: S.text(c, "tap", 1180 + 80 * math.sin(t * 3), 300, 60, "#fff6d8", a=tap, weight=700) if hasattr(S, "text") else text(c, "tap", 1180, 300, 60, "#fff6d8", a=tap, weight=700)
        # wind streaks
        for i in range(6):
            u = (t * .5 + i / 6) % 1
            c.drawLine(W * u - 300, 200 + i * 120, W * u, 180 + i * 120, paint("#c8d0ff", a=.25 * math.sin(u * math.pi), stroke=4))
        vignette(c, .6); paper_grain(c, t, .03)
    def honey_shot():
        tt = t - rm
        sink = ramp(t, hn, hn + 2)
        speed = lerp(1.0, .28, ramp(t, hn, hn + 1.5))
        cam = cam_path(t, [(rm, 960, 520, 1.0), (hn, 960, 560, 1.1), (st, 900, 640, 1.6), (pl, 900, 600, 1.3)])
        if t < hn:
            dream_sky(c, t)
            S.stars(c, t, DREAM_STARS, a=.8)
            c.drawRect(skia.Rect.MakeLTRB(0, 820, W, H), paint(shader=lin((0, 820), (0, H), ["#5a3a9a", "#2a1a5a"])))
        else:
            honey_field(c, t, 960)
        cam.apply(c, 1.0, t)
        x = (960 + 60 * math.sin(tt * .5)) if t > hn else lerp(600, 960, ease_out(inv(rm, rm + 2, t)))
        pose = S.run_pose(t, speed, flap=True) if hasattr(S, "run_pose") else run_pose(t, speed, flap=True)
        pose["bob"] = pose["bob"] * (1 - sink) + 50 * sink
        draw_person(c, "orion", x=x, y=900, s=1.0, face=1, t=t, outfit="pajama", mouth="open" if t < st else "frown", brow=.4 + .6 * sink,
                    eyes="open", **pose)
        if t > hn:
            # sticky honey around his legs + strands
            c.drawPath(oval(x, 948, 140, 40), paint("#f0a828")); c.drawPath(oval(x, 948, 140, 40), paint("#fff0a0", a=.5, stroke=4))
            for k in range(4):
                sx = x - 60 + k * 40; stretch = 40 + 30 * math.sin(t * 2 + k)
                c.drawLine(sx, 948, sx + 10, 948 - stretch, paint("#f8c040", stroke=8))
            S.sweat(c, x + 40, 520, t, sink) if hasattr(S, "sweat") else None
        cam.done(c)
        dream_post(c, t)
    def pool_shot():
        pool_memory(c, t, 1.0)
        c.drawPaint(paint("#ffb0e0", a=.12, blend="screen"))
        sparkles(c, t, DREAM_SPARK, a=.6, size=5)
        vignette(c, .5, "#3a2050"); paper_grain(c, t, .03)
    def a(): cross_dream(c, t, rm - .4, 1.2, window_shot, honey_shot)
    S.cross(c, t, pl - .2, 1.4, a, pool_shot)

def cross_dream(c, t, ts, d, fa, fb):
    """Dreamy dissolve: bloom of light between shots."""
    S.cross(c, t, ts, d, fa, fb)
    m = 1 - abs(inv(ts, ts + d, t) * 2 - 1) if ts < t < ts + d else 0
    if m > 0:
        c.drawPaint(paint("#ffe8ff", a=.5 * m, blend="screen")); sparkles(c, t, DREAM_SPARK, a=m, size=8)

# ================================================================== SCENE 11
def scene_11(c, ctx):
    t = ctx.t
    sl = ctx.s("sleep")
    def morning():
        cam = cam_path(t, [(0, 900, 600, 1.2), (ctx.s("think"), 760, 520, 1.5), (ctx.s("cape"), 820, 480, 1.4)])
        cam.apply(c, 1.0, t)
        bedroom(c, t, "day", lamp=0)
        light_rays(c, 1480, 150, t, a=.1, ang0=125)
        bx, by = 380, 900
        bed(c, bx, by, t)
        thinking = ctx.at("think") and not ctx.at("cape")
        draw_person(c, "orion", x=bx + 210, y=by - 46, s=1.0, face=1, t=t, outfit="pajama", mouth=ctx.mouth("O", "flat" if thinking else "smile"),
                    look=(.5, -.6) if thinking else (0, 0), armF=(160, 150) if thinking else ((150, 10) if ctx.at("cape") else (40, 30)), armB=(30, 30),
                    head_tilt=-8 if thinking else 0)
        blanket(c, bx, by, t)
        def content(cc, x, y, r):
            cc.drawPaint(paint("#bfe3f5"))
            draw_person(cc, "orion", x=x - 10, y=y + 30, s=.45, t=t, outfit="pajama", **fly_pose(t, "superman"))
        S.bubble(c, bx + 560, by - 520, 160, t, ramp(t, ctx.s("cape") - .4, ctx.s("cape") + .2), content, tail=(bx + 320, by - 380))
        cam.done(c)
        vignette(c, .4); paper_grain(c, t, .03)
    def night():
        lt = t - sl
        cam = cam_path(t, [(sl, 960, 560, 1.0), (sl + 2.5, 900, 600, 1.1), (ctx.dur, 800, 680, 1.6)])
        cam.apply(c, 1.0, t)
        bedroom(c, t, "night", lamp=1 - ramp(lt, 3.5, 5))
        bx, by = 380, 900
        bed(c, bx, by, t)
        if lt < 2.6:
            # hero pose with the cape, fists on hips
            draw_person(c, "orion", x=1000, y=960, s=1.0, face=-1, t=t, outfit="pajama", cape=True, cape_flow=.15 + .1 * math.sin(t * 2), cape_flutter=.6,
                        mouth="grin", armF=(25, 110), armB=(25, 110), brow=.5)
            sparkles(c, t, S.SPARK_A, a=.4, size=4)
        else:
            S.lying(c, "orion", bx + 270, by - 195, 1.0, t=t, outfit="pajama", eyes="closed" if lt > 4 else "open", mouth="smile", armF=(150, 30), armB=(140, 30))
            c.drawPath(poly([(bx + 330, by - 140), (bx + 160, by - 80), (bx + 240, by - 70)]), paint("#d8303a"))  # cape peeking out
            blanket(c, bx, by, t, breathe=.5 + .5 * math.sin(t * 1.3))
            if lt > 4.5: S.zzz(c, bx + 220, by - 330, t)
        cam.done(c)
        vignette(c, .55); paper_grain(c, t, .03)
    S.cross(c, t, sl - .4, .9, morning, night)

# ================================================================== dream sky stage
def dream_stage(c, cam, t, hue=0.0, town=True, ground=False, moon_pos=(1500, 230, 90)):
    dream_sky(c, t, hue=hue)
    cam.apply(c, .1, t); S.stars(c, t, DREAM_STARS, a=.9); moon(c, *moon_pos); cam.done(c)
    cam.apply(c, .3, t)
    for i in range(6): cloud(c, -400 + i * 700, 380 + 80 * math.sin(i * 2), 120, "#c8b0f0", .55, seed=60 + i, shade="#8a70c0")
    cam.done(c)
    if town: night_town(c, cam, t, y0=1000)

# ================================================================== SCENE 12
def scene_12(c, ctx):
    t = ctx.t
    jp, fl, bb = ctx.s("jump"), ctx.s("fly"), ctx.s("bubble")
    cam = cam_path(t, [(0, 960, 600, 1.0), (ctx.s("cape"), 900, 620, 1.35), (jp, 960, 600, 1.1), (fl, 960, 460, 1.0), (bb, 980, 420, 1.15), (ctx.dur, 1000, 420, 1.2)])
    dream_stage(c, cam, t)
    cam.apply(c, 1.0, t)
    # a soft glowing dream hill (rooftop of his house)
    roof = poly([(500, 880), (960, 760), (1420, 880), (1420, 1200), (500, 1200)])
    c.drawPath(roof, paint("#5a3060")); c.drawPath(roof, paint("#ffb0e0", a=.4, stroke=6))
    for i in range(8): c.drawLine(560 + i * 110, 870 - (i if i < 4 else 7 - i) * 28, 560 + i * 110, 1200, paint("#4a2850", stroke=4))
    feet_y = 760 + 0
    if t < jp + .3:
        crouch = ramp(t, jp - .4, jp + .2) * (1 - ramp(t, jp + .2, jp + .3))
        draw_person(c, "orion", x=960, y=feet_y, s=1.0, face=1, t=t, outfit="dream", cape=True, cape_flow=.3 + .2 * math.sin(t), cape_flutter=.8,
                    mouth="grin", brow=.5, lean=12 * crouch, legF=(20 * crouch, 50 * crouch), legB=(-20 * crouch, 60 * crouch), bob=28 * crouch,
                    armF=(-20, 20), armB=(-30, 20), look=(.4, -.6))
    else:
        up = t - jp - .3
        rise = 300 * ease_out(inv(0, 2.5, up)) + 40 * math.sin(up * .8) * ramp(up, 2.5, 4)
        wob = ramp(t, bb, bb + 1)
        x = 960 + 80 * math.sin(up * .9) * wob
        rot = 25 * math.sin(up * 1.3) * wob
        c.save(); c.translate(x, feet_y - rise - 150); c.rotate(rot); c.translate(-x, -(feet_y - rise - 150))
        draw_person(c, "orion", x=x, y=feet_y - rise, s=1.0, face=1, t=t, outfit="dream", eyes="wide" if t < bb else "open",
                    mouth="o" if t < fl + 1 else ("grin" if t < bb + 1.5 else "open"), brow=.4 * wob, **fly_pose(t, "float"))
        c.restore()
        if t > fl:  # bubble shimmer around him
            ba = ramp(t, fl, fl + 1)
            bx, byy = x, feet_y - rise - 150
            c.drawCircle(bx, byy, 230, paint("#bfe8ff", a=.12 * ba))
            c.drawCircle(bx, byy, 230, paint(shader=lin((bx - 230, byy - 230), (bx + 230, byy + 230), ["#ffb0f0", "#b0f0ff", "#fff0b0"]), a=.6 * ba, stroke=5))
            c.drawPath(oval(bx - 100, byy - 130, 60, 28), paint("#ffffff", a=.45 * ba))
    cam.done(c)
    dream_post(c, t)

# ================================================================== SCENE 13
def scene_13(c, ctx):
    t = ctx.t
    hd, wb, th, zp, nope = ctx.s("hands"), ctx.s("wobble"), ctx.s("thumbs"), ctx.s("zip"), ctx.s("nope")
    cam = cam_path(t, [(0, 960, 500, 1.0), (hd, 1000, 480, 1.35), (wb, 960, 500, 1.1), (th, 1040, 470, 1.4), (zp, 960, 520, .95), (nope, 980, 500, 1.2), (ctx.dur, 960, 500, 1.1)])
    dream_stage(c, Cam(cam.x, cam.y + 400, cam.z), t, hue=.1)
    cam.apply(c, 1.0, t)
    x, y, rot = 960, 640, 0
    hist = []
    if t < th:
        wobble = ramp(t, wb, wb + .6) * (1 - ramp(t, th - .4, th))
        x = 960 + 40 * math.sin(t * 2.0) * (1 + 3 * wobble)
        y = 640 + 30 * math.sin(t * 2.7) * (1 + 3 * wobble)
        rot = 6 * math.sin(t * 1.3) + 22 * math.sin(t * 4.1) * wobble
        pose = fly_pose(t, "superman"); pose["mouth"] = ctx.mouth("O", "o" if wobble > .3 else "grin"); pose["brow"] = .6 * wobble
        if ctx.at("hands"):  # hands open, fingers spread
            pose["armF"] = (165 + 15 * math.sin(t * 5) * wobble, 0)
    else:
        # thumbs: sharp zips to random points, with motion trails
        zt = t - th
        pts = [(960, 640), (1500, 380), (500, 420), (1300, 820), (700, 300), (1580, 700), (420, 760), (960, 520)]
        seg = .55
        k = int(zt / seg); u = (zt % seg) / seg
        a_, b_ = pts[k % len(pts)], pts[(k + 1) % len(pts)]
        if t < zp: a_, b_, u = pts[0], pts[0], 0  # hovering while thinking about thumbs
        e = ease_out(min(1, u * 3))
        x, y = lerp(a_[0], b_[0], e), lerp(a_[1], b_[1], e)
        ang = math.degrees(math.atan2(b_[1] - a_[1], b_[0] - a_[0])) if t >= zp else 0
        rot = (ang if abs(ang) < 90 else ang - 180 * (1 if ang > 0 else -1)) * .5
        if t > nope: x, y, rot = lerp(x, 960, ramp(t, nope, nope + .6)), lerp(y, 560, ramp(t, nope, nope + .6)), rot * (1 - ramp(t, nope, nope + .6))
        pose = fly_pose(t, "superman"); pose["mouth"] = ctx.mouth("O", "o" if t < nope else "flat"); pose["eyes"] = "wide" if zp < t < nope else "open"
        pose["armF"] = (150, 25); pose["armB"] = (140, 25)
        if zp < t < nope:
            for j in range(10):
                tj = t - j * .03; zj = tj - th; kj = int(zj / seg); uj = (zj % seg) / seg
                aj, bj = pts[kj % len(pts)], pts[(kj + 1) % len(pts)]; ej = ease_out(min(1, uj * 3))
                hist.append((lerp(aj[0], bj[0], ej), lerp(aj[1], bj[1], ej) - 120))
            trail(c, hist[::-1], "#fff3c0", 40)
            S.text(c, ["ZIP!", "WHOOSH!", "ZOOM!"][k % 3], x + 160, y - 330, 64, "#fff3c0", weight=700, glow="#ff9ad8") if hasattr(S, "text") else None
    c.save(); c.translate(x, y - 120); c.rotate(rot); c.translate(-x, -(y - 120))
    draw_person(c, "orion", x=x, y=y, s=1.0, face=1, t=t, outfit="dream", **pose)
    # thumbs-up indicators
    if th < t < nope:
        c.drawCircle(x + 260, y - 260, 26, paint("#ffe08a", a=.8, blur=10))
    c.restore()
    if t > nope:  # dizzy stars
        for i in range(4):
            a = t * 4 + i * 1.57
            star4(c, x + 150 + math.cos(a) * 70, y - 330 + math.sin(a) * 20, 9, "#fff3a0", 1 - ramp(t, ctx.s("persist") + 1, ctx.s("persist") + 2))
    cam.done(c)
    dream_post(c, t)

# ================================================================== SCENE 14 — the heart
def scene_14(c, ctx):
    t = ctx.t
    ct, ste, ns, ht = ctx.s("control"), ctx.s("steer"), ctx.s("nos"), ctx.s("heart")
    glow = ramp(t, ht, ht + 2.0)
    cam = cam_path(t, [(0, 960, 520, 1.2), (ct, 960, 520, 1.0), (ste, 960, 520, .95), (ns, 1000, 470, 1.6), (ht, 1000, 480, 2.0), (ht + 2.5, 990, 500, 1.6), (ctx.dur, 980, 520, 1.3)])
    dream_stage(c, Cam(cam.x, cam.y + 400, cam.z), t, hue=.2 + .4 * glow)
    if glow > 0:
        light_rays(c, W / 2 + 40, H / 2 - 40, t, "#ffd0e0", a=.22 * glow, n=14, spread=360, length=1400, ang0=0)
    cam.apply(c, 1.0, t)
    x, y, rot = 960, 640, 0
    mode = "superman"
    if t < ct:
        mode = "chest"; x = 960 + 20 * math.sin(t)
    elif t < ns:
        mode = "chest"
        u = t - ct
        x = 960 + 420 * math.sin(u * .55); y = 600 + 160 * math.sin(u * 1.1)
        rot = -14 * math.cos(u * .55) + 8 * math.cos(u * 1.1)
        # speed stretch when pushing chest out
        if ctx.at("steer"):
            speed = .5 + .5 * math.sin((t - ste) * 1.5)
            S.horizontal_streaks(c, t, a=.4 * speed, n=14) if hasattr(S, "horizontal_streaks") else horizontal_streaks(c, t, a=.4 * speed, n=14)
    else:
        mode = "chest"
        x = lerp(960 + 420 * math.sin((ns - ct) * .55), 980, ramp(t, ns, ns + 1.2)); y = lerp(600, 640, ramp(t, ns, ns + 1.2))
    pose = fly_pose(t, mode)
    looking_down = ctx.at("nos") and not ctx.at("heart")
    if looking_down: pose["head_tilt"] = -20; pose["look"] = (0, 1); pose["mouth"] = ctx.mouth("O", "flat")
    if ctx.at("heart"):
        pose["mouth"] = "talk" if ctx.talking("O") else "grin"; pose["eyes"] = "wide" if glow < .6 else "happy"
        pose["lean"] = lerp(pose["lean"], 30, glow); pose["head_tilt"] = lerp(pose["head_tilt"], -20, glow)
        pose["armF"] = (lerp(-25, 120, glow), 20); pose["armB"] = (lerp(-35, 110, glow), 20)
    if not looking_down and not ctx.at("heart"): pose["mouth"] = ctx.mouth("O", "grin")
    c.save(); c.translate(x, y - 120); c.rotate(rot); c.translate(-x, -(y - 120))
    draw_person(c, "orion", x=x, y=y, s=1.0, face=1, t=t, outfit="dream", heart=glow * 1.4 + (.25 if looking_down else 0), **pose)
    c.restore()
    if glow > 0:
        # heart sparks spiralling out
        for i in range(24):
            a = i * .26 + t * 1.2; r = 120 + ((t * 120 + i * 37) % 600)
            c.drawPath(heart_path(x + 40 + math.cos(a) * r, y - 180 + math.sin(a) * r * .7, 10 + 6 * (i % 3)), paint(["#ff7a9a", "#ffd0e0", "#fff3c0"][i % 3], a=glow * (1 - r / 720)))
    cam.done(c)
    if glow > 0: c.drawPaint(paint("#ff9ab8", a=.12 * glow * (1 + .3 * math.sin(t * 6)), blend="screen"))
    dream_post(c, t, 1 + glow)

# ================================================================== SCENE 15 — the great flight
def scene_15(c, ctx):
    t = ctx.t
    op, hi, nb, cl, mn, sr, fs = (ctx.s(k) for k in ("open", "higher", "neighborhood", "clouds", "moon", "stars", "faster"))
    def town_flight():
        # side-scrolling over the neighbourhood, gaining height
        scroll = (t - op) * 520 + 200
        alt = 300 * ramp(t, hi, nb) - 150 * ramp(t, nb, nb + 2)
        cam = Cam(960 + scroll, 520 - alt, 1.0)
        dream_sky(c, t, hue=.5)
        S.stars(c, t, DREAM_STARS, a=.9)
        moon(c, 1550, 220, 80)
        cam.apply(c, .3, t)
        for i in range(10): cloud(c, i * 900, 350 + 60 * math.sin(i), 120, "#c8b0f0", .5, seed=80 + i, shade="#8a70c0")
        cam.done(c)
        night_town(c, cam, t, y0=1050)
        px, py = 860, 520 + 40 * math.sin(t * 1.4) - 60 * ramp(t, op, op + 2)
        pose = fly_pose(t, "superman"); pose["mouth"] = "laugh" if ctx.at("higher") else "grin"; pose["eyes"] = "happy" if ctx.at("higher") and math.sin(t * 2) > 0 else "open"
        draw_person(c, "orion", x=px, y=py, s=.95, face=1, t=t, outfit="dream", heart=.6, **pose)
        S.horizontal_streaks(c, t, a=.35, n=18) if hasattr(S, "horizontal_streaks") else horizontal_streaks(c, t, a=.35, n=18)
        dream_post(c, t)
    def through_clouds():
        tt = t - cl
        dream_sky(c, t, hue=.7)
        S.stars(c, t, DREAM_STARS, a=.7)
        rnd = random.Random(5)
        for i in range(24):  # big clouds rushing past (parallax)
            depth = rnd.uniform(.6, 2.2)
            x = (rnd.uniform(0, 3000) - tt * 900 * depth) % 3400 - 700
            y = rnd.uniform(100, 1000)
            if depth < 1.2: cloud(c, x, y, 160 * depth, "#e8dcff", .85, seed=100 + i, shade="#a890d8")
        pose = fly_pose(t, "superman"); pose["mouth"] = "laugh"
        draw_person(c, "orion", x=900, y=560 + 30 * math.sin(t * 1.5), s=1.05, face=1, t=t, outfit="dream", heart=.6, **pose)
        for i in range(24):
            depth = rnd.uniform(.6, 2.2)
            x = (rnd.uniform(0, 3000) - tt * 900 * depth) % 3400 - 700
            y = rnd.uniform(100, 1000)
            if depth >= 1.2: cloud(c, x, y, 160 * depth, "#f4eeff", .9, seed=200 + i, shade="#c0b0e8")
        dream_post(c, t)
    def over_moon():
        tt = t - mn
        dream_sky(c, t, hue=.85)
        S.stars(c, t, DREAM_STARS, a=1)
        mz = 1 + .06 * tt
        moon(c, W / 2, H / 2 + 20, 380 * mz, 1.0, 1.4)
        # Orion silhouette arcing across the moon
        u = inv(mn - .3, sr + .5, t)
        x = lerp(-250, W + 250, u); y = H / 2 + 120 - 260 * math.sin(u * math.pi)
        c.save(); c.translate(x, y); c.rotate(-30 + 60 * u); c.translate(-x, -y)
        draw_person(c, "orion", x=x, y=y + 150, s=.7, face=1, t=t, outfit="dream", **fly_pose(t, "superman"))
        c.restore()
        sparkles(c, t, DREAM_SPARK, a=.6, size=5)
        vignette(c, .4, "#0a0420"); paper_grain(c, t, .02)
    def starfield():
        tt = t - sr
        c.drawPaint(paint(shader=lin((0, 0), (W, H), ["#05061a", "#1a0a40", "#0a2050"])))
        # nebula clouds
        for i, (nx, ny, nc) in enumerate(((400, 300, "#ff6ab0"), (1500, 700, "#6ad0ff"), (1100, 200, "#b07aff"), (300, 850, "#ffd06a"))):
            c.drawCircle(nx + 40 * math.sin(t * .2 + i), ny, 380, paint(nc, a=.18, blur=160))
        sp = ramp(t, fs, fs + 2.5)
        c.save(); c.translate(W / 2, H / 2); c.scale(1 + .2 * tt + sp * 1.5, 1 + .2 * tt + sp * 1.5); c.rotate(tt * 3); c.translate(-W / 2, -H / 2)
        S.stars(c, t, DEEP_STARS, a=1, size=2.2)
        c.restore()
        if sp > 0: speed_lines(c, t, a=sp, n=80)
        pose = fly_pose(t, "superman"); pose["mouth"] = "laugh"; pose["eyes"] = "happy"
        px = 960 + 40 * math.sin(t * 1.1) + 120 * sp; py = 620 + 20 * math.sin(t * 1.7)
        trail(c, [(px - 700 + k * 60, py - 120 + 8 * math.sin(t * 3 + k)) for k in range(12)], "#fff3c0", 60 * (.3 + sp), .8)
        c.save(); c.translate(px, py - 120); c.scale(1 + .1 * sp, 1 - .05 * sp); c.translate(-px, -(py - 120))
        draw_person(c, "orion", x=px, y=py, s=1.0, face=1, t=t, outfit="dream", heart=.8, cape_flutter=1.5 + 2 * sp, **{k: v for k, v in pose.items() if k != "cape_flutter"})
        c.restore()
        if sp > .6: c.drawPaint(paint("#ffffff", a=ramp(t, ctx.dur - 1.0, ctx.dur) * .9))
        sparkles(c, t, DREAM_SPARK, a=.8, size=5)
        vignette(c, .45, "#000010"); paper_grain(c, t, .02)
    def a(): cross_dream(c, t, cl - .5, 1.0, town_flight, through_clouds)
    def b(): cross_dream(c, t, mn - .5, 1.0, a, over_moon)
    cross_dream(c, t, sr - .4, 1.0, b, starfield)
    if t < op + 2.0:  # opening heart flash carried over from scene 14
        c.drawPaint(paint("#ffd0e0", a=.6 * (1 - ramp(t, 0, op + 2.0)), blend="screen"))

# ================================================================== SCENE 16 — shoes on the wire
SHOE_WIRE = (-200, 300, 2400, 310, 70)
def scene_16(c, ctx):
    t = ctx.t
    lo, la, wi, rv = ctx.s("lost"), ctx.s("laces"), ctx.s("wire"), ctx.s("reveal")
    def feet_shot():
        # close on Orion's feet: laces loosen, shoes pop off and tumble away
        c.drawPaint(paint(shader=lin((0, 0), (W, H), ["#0a0a30", "#2a1060"])))
        S.horizontal_streaks(c, t, a=.6, n=40, speed=3.0) if hasattr(S, "horizontal_streaks") else horizontal_streaks(c, t, a=.6, n=40, speed=3.0)
        c.save(); c.translate(W / 2, H / 2); c.scale(2.2, 2.2); c.translate(-W / 2, -H / 2)
        pop = ramp(t, lo + 2.2, lo + 2.6)
        pose = fly_pose(t, "superman"); pose["mouth"] = "o" if pop > 0 else "laugh"; pose["eyes"] = "wide" if pop > 0 else "happy"
        pose["shoes"] = pop <= 0
        draw_person(c, "orion", x=1150, y=520, s=1.0, face=1, t=t, outfit="dream", **pose)
        c.restore()
        if pop > 0:
            dt = t - (lo + 2.4)
            for k in range(2):
                sx = 700 - dt * 900 - k * 60; sy = 520 + k * 60 + dt * dt * 300
                c.save(); c.translate(sx, sy); c.rotate(dt * 500 + k * 90); c.scale(2.0, 2.0)
                outline(c, rrect(-26, -13, 52, 26, 13), "#e0352b", width=4); c.drawPath(rrect(-26, 4, 52, 8, 4), paint("#fbf3e6"))
                c.drawLine(-5, -12, 18, -40 + 10 * math.sin(t * 9), paint("#ffffff", stroke=3)); c.drawLine(5, -12, -14, -38, paint("#ffffff", stroke=3))
                c.restore()
            S.text(c, "Whoops!", 1350, 250, 90, "#fff3c0", a=ramp(t, lo + 2.5, lo + 3) * (1 - ramp(t, la, la + .5)), weight=700, glow="#ff9ad8") if hasattr(S, "text") else None
        vignette(c, .5, "#000010"); paper_grain(c, t, .02)
    def fall_shot():
        # shoes tumbling down through the sky toward a dawn street
        u = inv(la - .2, wi + .4, t)
        mode_u = ramp(t, la, wi)
        sky(c, "dream" if mode_u < .5 else "night", "dawn" if mode_u >= .5 else "night", max(0, mode_u * 2 - 1) if mode_u >= .5 else mode_u * 2, t=t)
        S.stars(c, t, DREAM_STARS, a=1 - mode_u)
        cam = Cam(lerp(960, 1040, ease_io(u)), lerp(-900, 430, ease_io(u)), lerp(1.4, 2.0, ease_io(u)))
        cam.apply(c, .6, t)
        for i in range(6): cloud(c, 200 + i * 340, -500 + i * 60, 110, "#ffe0f0", .7, seed=300 + i, shade="#d8a0c8")
        cam.done(c)
        dawn_street(c, cam, t, 1.0)
        cam.apply(c, 1.0, t)
        # shoes descend in a gentle spiral, laces snag the wire and wrap around
        x0, y0, x1, y1, sag = SHOE_WIRE
        catch = 1040
        wy = wire_y(x0, y0, x1, y1, sag, catch)
        land = ease_out(inv(.0, .9, u))
        if u < .9:
            sx = catch + 220 * math.sin(u * 6) * (1 - u); sy = lerp(-1200, wy, ease_in(u / .9))
            c.save(); c.translate(sx, sy); c.rotate(u * 900)
            outline(c, rrect(-26, -13, 52, 26, 13), "#e0352b", width=4); outline(c, rrect(-10, 10, 52, 26, 13), "#e0352b", width=4)
            c.restore()
        else:
            hanging_shoes(c, catch, wy, t, swing=1.0 + 2 * (1 - ramp(u, .9, 1.0)))
        cam.done(c)
        vignette(c, .35); paper_grain(c, t, .03)
    def reveal_shot():
        rt = t - rv
        z = lerp(1.9, .78, ease_io(inv(-.6, 4.5, rt)))
        cam = Cam(lerp(1040, 1300, ease_io(inv(-.6, 4.5, rt))), lerp(360, 520, ease_io(inv(-.6, 4.5, rt))), z)
        sky(c, "dawn", "day", ramp(rt, 0, 6), sun=(1650, 820 - 200 * ramp(rt, 0, 6), 90, "#ffd090"), t=t)
        sky_clouds(c, t, a=.8, tint="#fff0e8", shade="#f0b8c0", speed=10)
        dawn_street(c, cam, t, 1.0, many=ramp(rt, .5, 3.0))
        cam.apply(c, 1.0, t)
        x0, y0, x1, y1, sag = SHOE_WIRE
        hanging_shoes(c, 1040, wire_y(x0, y0, x1, y1, sag, 1040), t, swing=.6)
        cam.done(c)
        birds(c, rt, -200, 220, n=5, speed=100, s=.9, a=ramp(rt, 1, 3)) if hasattr(S, "birds") is False else S.birds(c, rt, -200, 220, n=5, speed=100, s=.9, a=ramp(rt, 1, 3))
        vignette(c, .35); paper_grain(c, t, .03)
    def a(): S.cross(c, t, la - .3, .8, feet_shot, fall_shot)
    S.cross(c, t, wi + .6, 1.0, a, reveal_shot) if False else None
    S.cross(c, t, rv - .6, 1.2, a, reveal_shot)

OTHER_SHOES = [(-420, "#3a7ad8", "#ffffff"), (520, "#f2c94c", "#5a3a2a"), (1700, "#5ab86a", "#ffffff"), (2300, "#8a5ad8", "#fff0a0"),
               (2900, "#ff8a3a", "#ffffff"), (3500, "#e0e0e8", "#3a3a5a"), (-1100, "#d84a8a", "#ffffff")]
def dawn_street(c, cam, t, light=1.0, many=0.0):
    cam.apply(c, .4, t); hills(c, t, "#c08a8a", None); cam.done(c)
    cam.apply(c, .7, t)
    for i, hx in enumerate(range(-1600, 4600, 420)):
        hh = 160 + (i * 41) % 80
        outline(c, poly([(hx, 860), (hx, 860 - hh), (hx + 120, 860 - hh - 90), (hx + 240, 860 - hh), (hx + 240, 860)]), mix_c((214, 170, 170), (240, 200, 180), .5), width=3)
        window(c, hx + 90, 860 - hh + 40, 60, 46, .7, t)
    for i, tx in enumerate(range(-1500, 4600, 520)): tree(c, tx, 870, 260, t, seed=70 + i, wind=.5)
    cam.done(c)
    cam.apply(c, 1.0, t)
    c.drawRect(skia.Rect.MakeLTRB(-3000, 860, 6000, 960), paint("#9cb25a"))
    street(c, -3000, 6000, 940, t)
    x0, y0, x1, y1, sag = SHOE_WIRE
    for px in (-1400, -200, 2400, 5000):
        tele_pole(c, px, 1020, 760)
    wire(c, -1400, 300, -200, 300, 60); wire(c, x0, y0, x1, y1, sag); wire(c, 2400, 310, 5000, 300, 70)
    wire(c, -1400, 340, -200, 340, 50); wire(c, -200, 340, 2400, 350, 60); wire(c, 2400, 350, 5000, 340, 60)
    if many > 0:
        for i, (sx, colr, lace) in enumerate(OTHER_SHOES):
            if sx < -200: seg = (-1400, 300, -200, 300, 60)
            elif sx < 2400: seg = SHOE_WIRE
            else: seg = (2400, 310, 5000, 300, 70)
            a = clamp(many * 3 - i * .3)
            if a > 0:
                c.saveLayerAlpha(None, int(255 * a))
                hanging_shoes(c, sx, wire_y(*seg[:4], seg[4], sx), t, colr=colr, lace=lace, seed=i * 1.7, swing=.5, s=.9)
                c.restore()
    cam.done(c)
    c.drawPaint(paint("#ffb090", a=.12 * light, blend="multiply"))

# ================================================================== SCENE 17
def scene_17(c, ctx):
    t = ctx.t
    kn, ad, jo, wo, en = (ctx.s(k) for k in ("known", "adventures", "journey", "worth", "end"))
    def morning_yard():
        cam = cam_path(t, [(0, 1700, 600, 1.0), (ad, 1700, 560, 1.2)])
        yard_world(c, cam, t, light=.05, pile=(S.PILE_X, GROUND + 10, 440, 190, t))
        cam.apply(c, 1.0, t)
        draw_person(c, "orion", x=1720, y=GROUND, s=1.0, face=1, t=t, cape=True, cape_flow=.25 + .1 * math.sin(t * 2), cape_flutter=.8,
                    mouth="grin", armF=(25, 110), armB=(25, 110), brow=.4)
        for i in range(3):
            S.chicken(c, 1300 + i * 140 + 30 * math.sin(t + i), 980, .8, t, 1, max(0, math.sin(t * 3 + i)) ** 4, ["#ffffff", "#c8743a", "#f2e2c6"][i], seed=i) if hasattr(S, "chicken") else chicken(c, 1300 + i * 140, 980, .8, t, 1, 0, "#ffffff")
        cam.done(c)
        S.post(c, t, .8)
    def adventures():
        tt = t - ad
        # montage: ocean at sunset, mountains, then flying with birds
        seg = (jo - ad) / 2.0
        k = int(tt / seg)
        if k == 0:
            sky(c, "golden", "sunset", .6, sun=(1400, 620, 90, "#ffc070"), t=t)
            c.drawRect(skia.Rect.MakeLTRB(0, 680, W, H), paint(shader=lin((0, 680), (0, H), ["#e08a6a", "#3a4a8a"])))
            for i in range(14): c.drawLine(0, 700 + i * 28, W, 700 + i * 28, paint("#ffd0a0", a=.2, stroke=2))
            c.drawPath(oval(1400, 700, 260, 14), paint("#fff0c0", a=.5, blur=6))
            S.birds(c, tt, -100, 300, n=5, speed=140, s=1.0)
            draw_person(c, "orion", x=500 + tt * 160, y=520, s=.8, face=1, t=t, outfit="dream", **fly_pose(t, "superman"))
        else:
            sky(c, "day", t=t)
            for i, (mx, mh, mc) in enumerate(((300, 520, "#8a90b8"), (900, 640, "#7078a8"), (1500, 560, "#8a90b8"))):
                c.drawPath(poly([(mx - 520, H), (mx, H - mh - 200), (mx + 520, H)]), paint(mc))
                c.drawPath(poly([(mx - 120, H - mh - 200 + 140), (mx, H - mh - 200), (mx + 120, H - mh - 200 + 140), (mx + 40, H - mh - 200 + 110), (mx - 40, H - mh - 200 + 150)]), paint("#ffffff"))
            S.sky_clouds(c, t, a=.9, speed=40) if hasattr(S, "sky_clouds") else None
            draw_person(c, "orion", x=300 + (tt - seg) * 220, y=480 + 40 * math.sin(t), s=.8, face=1, t=t, outfit="dream", **fly_pose(t, "superman"))
        vignette(c, .35); paper_grain(c, t, .03)
    def journey():
        # storybook memory pages: the wings, the leaf pile, the driver
        c.drawPaint(paint(shader=lin((0, 0), (0, H), ["#3a2a4a", "#1a1030"])))
        tt = t - jo
        frames = [(360, 540, -6), (960, 500, 3), (1560, 540, -3)]
        for i, (fx, fy, rot) in enumerate(frames):
            a = ramp(tt, i * .9, i * .9 + .8)
            if a <= 0: continue
            c.save(); c.translate(fx, fy + 30 * (1 - a)); c.rotate(rot)
            c.drawPath(rrect(-260, -200, 520, 400, 10), paint("#000000", a=.4 * a, blur=20))
            c.drawPath(rrect(-250, -190, 500, 380, 8), paint("#fff8e8", a=a))
            c.save(); c.clipPath(rrect(-230, -170, 460, 300, 4))
            c.saveLayerAlpha(None, int(255 * a))
            if i == 0:
                c.save(); c.scale(.35, .35); c.translate(-W / 2 - 200, -H / 2 - 300)
                garage_interior(c, t); draw_person(c, "orion", x=700, y=880, s=1.0, face=1, t=t, wings="card", armF=(95, 0), armB=(85, 0), mouth="grin")
                c.restore()
            elif i == 1:
                c.save(); c.scale(.3, .3); c.translate(-S.PILE_X - 100, -GROUND + 150)
                sky(c, "day"); lawn(c, 1200, 3000, 800, 1100, t)
                leaf_pile(c, S.PILE_X, GROUND + 10, 440, 190, t)
                draw_person(c, "orion", x=S.PILE_X - 20, y=GROUND - 30, s=1.0, t=t, wings="feather", eyes="happy", mouth="laugh", armF=(150, 20), armB=(140, 20), **S.sit_pose(1.0))
                leaf_burst(c, S.PILE_X, GROUND - 60, 0, (t * .5) % 2 + .3, 50)
                c.restore()
            else:
                c.save(); c.scale(.4, .4); c.translate(-2300, -650)
                sky(c, "day"); lawn(c, 1800, 2800, 800, 1100, t)
                draw_person(c, "driver", x=2330, y=GROUND + 4, s=.92, face=-1, t=t, mouth="smile", legF=(80, 90), legB=(-10, 100), bob=60, armF=(70, 40), armB=(40, 40))
                draw_person(c, "orion", x=2080, y=GROUND - 30, s=1.0, t=t, wings="feather", mouth="smile", eyes="wide", **S.sit_pose(1.0))
                c.restore()
            c.restore(); c.restore()
            text(c, ["Wings", "Leaves", "Practice"][i], 0, 175, 40, "#5a3020", a=a, shadow=False, weight=700)
            c.restore()
        sparkles(c, t, DREAM_SPARK, a=.4, size=4)
        vignette(c, .5); paper_grain(c, t, .03)
    def finale():
        tt = t - wo
        dream_sky(c, t, hue=.6)
        S.stars(c, t, DREAM_STARS, a=1)
        moon(c, W / 2, H / 2 - 20, 330, 1.0, 1.3)
        u = inv(wo - .5, en + 1.5, t)
        x = lerp(-200, W + 200, u); y = H / 2 + 80 - 220 * math.sin(u * math.pi)
        c.save(); c.translate(x, y); c.rotate(-25 + 50 * u); c.translate(-x, -y)
        draw_person(c, "orion", x=x, y=y + 150, s=.75, face=1, t=t, outfit="dream", heart=.6, **fly_pose(t, "superman"))
        c.restore()
        night_town(c, Cam(960 + tt * 40, 540, 1.0), t, y0=1180)
        ea = ramp(t, en, en + 1.0)
        text(c, "The End", W / 2, 230, 150, "#fff6e6", a=ea, weight=700, glow="#ff9ad8")
        sparkles(c, t, DREAM_SPARK, a=.6, size=5)
        vignette(c, .45, "#0a0420"); paper_grain(c, t, .02)
    def a(): S.cross(c, t, ad - .4, .9, morning_yard, adventures)
    def b(): S.cross(c, t, jo - .4, .9, a, journey)
    cross_dream(c, t, wo - .6, 1.2, b, finale)

# ================================================================== CREDITS (18)
CREDITS = [
 ("title", "The Boy Who Wanted to Fly"),
 ("gap", ""),
 ("head", "Story"), ("name", "Jason Whitewolf"),
 ("small", "© 2018 Jason Whitewolf. All rights reserved."),
 ("gap", ""),
 ("head", "Animated adaptation"), ("name", "Produced with Claude (Anthropic)"),
 ("small", "for Jason Whitewolf"),
 ("gap", ""),
 ("head", "Narration & voices"), ("name", "Kokoro TTS  ·  Apache-2.0"),
 ("head", "Animation"), ("name", "Hand-coded vector rig  ·  skia-python"),
 ("head", "Music & sound"), ("name", "Original procedural score"),
 ("head", "Fonts"), ("name", "Fredoka & Nunito  ·  SIL Open Font License"),
 ("head", "Assembly"), ("name", "FFmpeg"),
 ("gap", ""),
 ("small", "Keep practicing — and never give up on your dream."),
 ("gap", ""), ("gap", ""),
 ("name", "Sweet dreams."),
]

def scene_18(c, ctx):
    t = ctx.t
    dream_sky(c, t, hue=.4)
    S.stars(c, t, DREAM_STARS, a=1)
    moon(c, 1500, 260, 110)
    # Orion drifting slowly across in the background
    u = (t / ctx.dur)
    draw_person(c, "orion", x=lerp(-200, W + 200, u), y=780 + 30 * math.sin(t), s=.45, face=1, t=t, outfit="dream", **fly_pose(t, "superman"))
    night_town(c, Cam(960 + t * 30, 540, 1.0), t, y0=1180)
    c.drawPaint(paint("#000010", a=.35))
    y = H + 60 - t * 72
    for kind, s_ in CREDITS:
        size, colr, wt, gap = {"title": (88, "#fff6e6", 700, 140), "head": (34, "#ffd0e0", 600, 52), "name": (54, "#fff6e6", 600, 84),
                                "small": (34, "#e8d8ff", 600, 66), "gap": (0, "#000000", 600, 70)}[kind]
        if kind != "gap" and -100 < y < H + 100:
            text(c, s_, W / 2, y, size, colr, weight=wt, name="Fredoka" if kind in ("title", "name") else "Nunito", glow="#8a4fb0" if kind == "title" else None)
        y += gap
    vignette(c, .45, "#000010"); paper_grain(c, t, .02)
