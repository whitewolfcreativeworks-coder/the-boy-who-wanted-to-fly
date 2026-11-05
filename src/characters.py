"""Rigged vector characters.

All humans share one puppet rig (`draw_person`) driven by a pose dict, so a
character looks identical in every shot. Styles define proportions/palettes.
Local coordinates: origin = between the feet on the ground, facing +x, y down.
"""
import math, random
import skia
from engine import *

INK = "#3a2418"

STYLES = {
 "orion": dict(leg=(50, 48), torso=98, head_r=64, shoulder=16, hip=11, body_w=(46, 40),
               arm=(44, 42), limb_w=(25, 19), skin="#f3c9a2", blush="#f29b86",
               hair="#4b2b19", hair_style="orion", eye="#3a2a20",
               shirt="#f2873a", shirt2="#fff0d2", stripes=True, pants="#3f5f93",
               shoe="#e0352b", sole="#fbf3e6", lace="#ffffff", sleeve_long=True),
 "mom":   dict(leg=(78, 74), torso=128, head_r=50, shoulder=22, hip=14, body_w=(50, 52),
               arm=(62, 58), limb_w=(22, 17), skin="#e9b58f", blush="#e48f7c",
               hair="#3a2016", hair_style="long", eye="#2e2018",
               shirt="#2f8f86", shirt2="#2f8f86", stripes=False, pants="#4b3f64",
               shoe="#6b3a2a", sole="#3a2418", lace=None, sleeve_long=True, lips="#c0504a"),
 "dad":   dict(leg=(82, 78), torso=138, head_r=50, shoulder=26, hip=16, body_w=(60, 56),
               arm=(66, 62), limb_w=(26, 20), skin="#dca27b", blush="#d6876c",
               hair="#5a3820", hair_style="short", eye="#2e2018", beard="#5a3820", glasses=True,
               shirt="#b23a33", shirt2="#4a1f1f", plaid=True, stripes=False, pants="#34507a",
               shoe="#4a3020", sole="#2a1a10", lace=None, sleeve_long=True),
 "driver":dict(leg=(92, 86), torso=150, head_r=54, shoulder=34, hip=20, body_w=(84, 74),
               arm=(74, 68), limb_w=(34, 26), skin="#c98e68", blush="#c4785e",
               hair="#3a2a20", hair_style="cap", eye="#2e2018", stubble=True,
               shirt="#6c7680", shirt2="#6c7680", vest="#ff7a1a", stripes=False, pants="#3b4250",
               shoe="#3a2a1e", sole="#1e140c", lace="#c9a070", sleeve_long=False, boots=True),
}

OUTFITS = {
 "pajama": dict(shirt="#2d3f7d", shirt2="#2d3f7d", stripes=False, pj_stars=True, pants="#2d3f7d"),
 "dream":  dict(shirt="#2d3f7d", shirt2="#2d3f7d", stripes=False, pj_stars=True, pants="#2d3f7d"),
}

def default_pose():
    return dict(x=0, y=0, s=1.0, face=1, lean=0.0, armF=(10, 15), armB=(-8, 15),
                legF=(4, 0), legB=(-4, 0), head_tilt=0.0, look=(0.0, 0.0),
                eyes="open", mouth="smile", t=0.0, outfit="day", wings=None,
                cape=False, cape_flow=0.0, shoes=True, hair_wind=0.0, blink=True,
                bob=0.0, hand_open=False, heart=0.0, flap=0.0, squash=1.0)

def _dir(a): r = math.radians(a); return math.sin(r), math.cos(r)

def limb(c, p0, a1, a2, l1, l2, w1, w2, color, ink=INK):
    """Two-segment limb. Angles in degrees, 0 = straight down, + = forward."""
    d1 = _dir(a1); e = (p0[0] + d1[0] * l1, p0[1] + d1[1] * l1)
    d2 = _dir(a1 + a2); h = (e[0] + d2[0] * l2, e[1] + d2[1] * l2)
    path = skia.Path(); path.moveTo(*p0); path.lineTo(*e); path.lineTo(*h)
    c.drawPath(path, paint(ink, stroke=w1 + 6))
    c.drawPath(path, paint(color, stroke=w1))
    return e, h, a1 + a2

def limb_geom(p0, a1, a2, l1, l2):
    d1 = _dir(a1); e = (p0[0] + d1[0] * l1, p0[1] + d1[1] * l1)
    d2 = _dir(a1 + a2); return e, (e[0] + d2[0] * l2, e[1] + d2[1] * l2)

def shoe(c, x, y, ang, st, s=1.0):
    c.save(); c.translate(x, y); c.rotate(-ang * 0.6)
    L = 30 * s if not st.get("boots") else 36 * s
    body = rrect(-L * .45, -12 * s, L * 1.35, 22 * s, 11 * s)
    outline(c, body, st["shoe"], width=4)
    c.drawPath(rrect(-L * .45, 4 * s, L * 1.35, 7 * s, 3.5 * s), paint(st["sole"]))
    if st.get("lace"):
        for i in range(3):
            c.drawLine(L * (.05 + i * .17), -10 * s, L * (.12 + i * .17), -2 * s, paint(st["lace"], stroke=3 * s))
        c.drawCircle(L * .62, -6 * s, 4 * s, paint("#ffffff"))  # toe cap
    c.restore()

def hand(c, x, y, st, r=11):
    c.drawCircle(x, y, r + 3, paint(INK, a=.85)); c.drawCircle(x, y, r, paint(st["skin"]))

# ------------------------------------------------------------------ wings / cape
def wing(c, sh, el, hd, kind, t, side=1, flap=0.0, s=1.0):
    """Cardboard wing strapped along the arm, trailing edge hanging below."""
    ax, ay = sh; bx, by = el; cx_, cy_ = hd
    dx, dy = cx_ - ax, cy_ - ay; L = math.hypot(dx, dy) + 1e-3
    nx, ny = -dy / L, dx / L
    if (-nx + ny) < 0: nx, ny = -nx, -ny   # trailing edge points back/down from the arm
    depth = 70 * s
    tip = (cx_ + dx / L * 38 * s, cy_ + dy / L * 38 * s)
    pts = [(ax - dx / L * 6, ay - dy / L * 6), (bx, by), (cx_, cy_), tip,
           (tip[0] + nx * depth * .45, tip[1] + ny * depth * .45),
           (bx + nx * depth * .95, by + ny * depth * .95),
           (ax + nx * depth * .8, ay + ny * depth * .8)]
    path = poly(pts)
    outline(c, path, "#c99a62", width=4)
    # corrugation lines + scalloped edge
    for i in range(1, 6):
        u = i / 6
        p1 = (lerp(ax, tip[0], u), lerp(ay, tip[1], u))
        c.drawLine(*p1, p1[0] + nx * depth * .7 * (1 - u * .4), p1[1] + ny * depth * .7 * (1 - u * .4), paint("#a87a48", stroke=2))
    # tape
    for u in (.25, .6):
        p1 = (lerp(ax, cx_, u), lerp(ay, cy_, u))
        c.drawPath(poly([(p1[0] - dx / L * 9 - nx * 12, p1[1] - dy / L * 9 - ny * 12), (p1[0] + dx / L * 9 - nx * 12, p1[1] + dy / L * 9 - ny * 12),
                         (p1[0] + dx / L * 9 + nx * 26, p1[1] + dy / L * 9 + ny * 26), (p1[0] - dx / L * 9 + nx * 26, p1[1] - dy / L * 9 + ny * 26)]),
                     paint("#d8d4c8", a=.92))
    if kind == "feather":
        rnd = random.Random(7 + side)
        cols = ["#ffffff", "#f6efe2", "#b5562a", "#8a4a22", "#f2e2c6", "#d8743a"]
        for i in range(16):
            u = (i + .5) / 16
            base = (lerp(ax + nx * depth * .5, tip[0], u), lerp(ay + ny * depth * .5, tip[1], u))
            ang = math.degrees(math.atan2(ny, nx)) - 90 + rnd.uniform(-20, 20) + 8 * math.sin(t * 6 + i) * (0.3 + flap)
            fl = (34 + rnd.uniform(-6, 10)) * s * (1 - u * .25)
            c.save(); c.translate(*base); c.rotate(ang)
            f = skia.Path(); f.moveTo(0, 0); f.quadTo(fl * .32, fl * .5, 0, fl * 1.1); f.quadTo(-fl * .32, fl * .5, 0, 0)
            outline(c, f, cols[rnd.randrange(len(cols))], width=2.5)
            c.drawLine(0, 2, 0, fl, paint("#7a6050", a=.5, stroke=1.5))
            c.restore()

def cape_back(c, st, t, flow, face_sign, s=1.0, flutter=None):
    """Red cape behind the body, fluttering. Drawn in the body's local frame."""
    sh_y = -st["leg"][0] - st["leg"][1] - st["torso"] + 10
    top_l, top_r = (-st["body_w"][0] * .55, sh_y), (st["body_w"][0] * .45, sh_y)
    length = 150 * s
    # flow: 0 hangs down; 1 streams straight back (-x)
    ang = lerp(0, 82, flow)
    fa = (0.3 + flow) if flutter is None else flutter
    pts_l, pts_r = [top_l], [top_r]
    for i in range(1, 6):
        u = i / 5
        a = math.radians(ang + 10 * math.sin(t * 7 - u * 4) * fa)
        w = lerp(1.0, 1.5, u)
        bx, by = -math.sin(a) * length * u, math.cos(a) * length * u
        flut = 12 * math.sin(t * 9 - u * 6) * u * fa
        pts_l.append((top_l[0] * w + bx - flut, sh_y + by + flut))
        pts_r.append((top_r[0] * w + bx + flut * .5, sh_y + by - flut * .4 + 8 * u))
    path = smooth_path(pts_l + pts_r[::-1], True, .4)
    c.drawPath(path, paint(INK, stroke=9, a=.85))
    c.drawPath(path, paint(shader=lin(top_l, pts_l[-1], ["#e53a3a", "#b51f2a"])))
    # sheen
    c.drawPath(smooth_path([top_l, pts_l[2], pts_l[4], pts_r[4], pts_r[2]], True, .4), paint("#ff8a7a", a=.18))

# ------------------------------------------------------------------ hair & face
def draw_head(c, st, P, hx, hy, r):
    t = P["t"]; skin = st["skin"]
    hw = P.get("hair_wind", 0)
    # back hair (long)
    if st["hair_style"] == "long":
        hp = smooth_path([(hx - r * 1.05, hy - r * .2), (hx - r * 1.2 - hw * 20, hy + r * 1.4), (hx - r * .2 - hw * 10, hy + r * 1.6),
                          (hx + r * .9, hy + r * 1.3), (hx + r * 1.05, hy - r * .3), (hx, hy - r * 1.15)], True, .7)
        outline(c, hp, st["hair"], width=4)
    # ear
    c.drawCircle(hx - r * .62, hy + r * .1, r * .2, paint(INK, a=.85)); c.drawCircle(hx - r * .62, hy + r * .1, r * .16, paint(skin))
    # head
    head = oval(hx, hy, r, r * .96)
    outline(c, head, skin, width=5)
    if st.get("stubble"):
        c.drawPath(smooth_path([(hx - r * .7, hy + r * .2), (hx + r * .95, hy + r * .1), (hx + r * .6, hy + r * .85), (hx - r * .3, hy + r * .9)], True, .8), paint("#5a4636", a=.28))
    if st.get("beard"):
        bp = smooth_path([(hx - r * .75, hy + r * .05), (hx + r * .98, hy), (hx + r * .7, hy + r * 1.05), (hx + r * .1, hy + r * 1.25), (hx - r * .55, hy + r * .85)], True, .8)
        outline(c, bp, st["beard"], width=4)
    # hair front
    hs = st["hair_style"]
    if hs == "orion":
        rnd = random.Random(3)
        tufts = []
        for i in range(11):
            a = math.radians(200 + i * 16)
            rr = r * (1.06 + .1 * rnd.random())
            tufts.append((hx + math.cos(a) * rr - hw * 6 * (i / 10), hy + math.sin(a) * rr * 1.02))
        cap = [(hx + r * .95, hy - r * .4), (hx + r * .72, hy - r * .52), (hx + r * .5, hy - r * .4), (hx + r * .25, hy - r * .62), (hx, hy - r * .48),
               (hx - r * .28, hy - r * .6), (hx - r * .5, hy - r * .25), (hx - r * .68, hy + r * .12), (hx - r * .98, hy + r * .02)]
        path = smooth_path(tufts + cap, True, .6)
        outline(c, path, st["hair"], width=4)
        # cowlick
        ck = skia.Path(); ck.moveTo(hx - r * .05, hy - r * 1.05)
        ck.cubicTo(hx - r * .1 - hw * 10, hy - r * 1.55, hx + r * .35 - hw * 20, hy - r * 1.55, hx + r * .25 - hw * 22, hy - r * 1.3)
        c.drawPath(ck, paint(INK, stroke=11)); c.drawPath(ck, paint(st["hair"], stroke=6))
        c.drawPath(smooth_path([(hx - r * .3, hy - r * .85), (hx + r * .2, hy - r * .95), (hx + r * .5, hy - r * .7)], False, .6), paint("#7a4a2a", a=.6, stroke=5))
    elif hs == "long":
        path = smooth_path([(hx + r * 1.0, hy - r * .05), (hx + r * .4, hy - r * .55), (hx - r * .3, hy - r * .35), (hx - r * .95, hy + r * .3),
                            (hx - r * 1.08, hy - r * .4), (hx - r * .5, hy - r * 1.08), (hx + r * .45, hy - r * 1.05)], True, .7)
        outline(c, path, st["hair"], width=4)
    elif hs == "short":
        path = smooth_path([(hx + r * .92, hy - r * .3), (hx + r * .3, hy - r * .55), (hx - r * .55, hy - r * .1), (hx - r * .95, hy + r * .1),
                            (hx - r * 1.02, hy - r * .55), (hx - r * .4, hy - r * 1.06), (hx + r * .5, hy - r * 1.0)], True, .7)
        outline(c, path, st["hair"], width=4)
    elif hs == "cap":
        capp = smooth_path([(hx - r * 1.0, hy - r * .15), (hx - r * .85, hy - r * .8), (hx, hy - r * 1.08), (hx + r * .85, hy - r * .75), (hx + r * .95, hy - r * .2)], True, .6)
        outline(c, capp, "#2f6a4a", width=4)
        c.drawPath(rrect(hx + r * .3, hy - r * .32, r * 1.05, r * .22, r * .1), paint(INK, a=.9))
        c.drawPath(rrect(hx + r * .32, hy - r * .3, r * 1.0, r * .16, r * .08), paint("#25553b"))
        c.drawPath(rrect(hx - r * 1.02, hy - r * .3, r * .5, r * .5, r * .2), paint(st["hair"]))
    # face (3/4 view toward +x)
    lx, ly = P["look"]
    ex1, ex2 = hx + r * .12 + lx * r * .06, hx + r * .6 + lx * r * .06
    ey = hy + r * .02 + ly * r * .05
    er = r * (.17 if st is STYLES["orion"] else .12)
    eyes = P["eyes"]
    if P.get("blink") and eyes == "open":
        ph = (t * .31 + hx * .001) % 1.0
        if ph < .035: eyes = "closed"
    for i, ex in enumerate((ex1, ex2)):
        k = .82 if i == 0 else 1.0
        if eyes in ("open", "wide"):
            sc = 1.25 if eyes == "wide" else 1.0
            c.drawPath(oval(ex, ey, er * .85 * k * sc, er * 1.1 * sc), paint("#ffffff"))
            c.drawPath(oval(ex, ey, er * .85 * k * sc, er * 1.1 * sc), paint(INK, stroke=2.5))
            px, py = ex + lx * er * .25 + er * .1, ey + ly * er * .25
            c.drawCircle(px, py, er * .58 * sc, paint(st["eye"]))
            c.drawCircle(px + er * .2, py - er * .25, er * .2, paint("#ffffff"))
        elif eyes == "happy":
            a = skia.Path(); a.moveTo(ex - er * .8, ey + er * .2); a.quadTo(ex, ey - er * 1.0, ex + er * .8, ey + er * .2)
            c.drawPath(a, paint(INK, stroke=4.5))
        elif eyes == "sleepy":
            c.drawPath(oval(ex, ey + er * .3, er * .8 * k, er * .45), paint("#ffffff"))
            c.drawCircle(ex + er * .1, ey + er * .35, er * .4, paint(st["eye"]))
            c.drawLine(ex - er * .9, ey, ex + er * .9, ey, paint(INK, stroke=4))
        else:  # closed
            a = skia.Path(); a.moveTo(ex - er * .8, ey); a.quadTo(ex, ey + er * .7, ex + er * .8, ey)
            c.drawPath(a, paint(INK, stroke=4))
    # brows
    bro = P.get("brow", 0.0)  # + worried/determined
    for i, ex in enumerate((ex1, ex2)):
        sgn = -1 if i == 0 else 1
        c.drawLine(ex - er * .7, ey - er * 1.55 - bro * sgn * er * .3, ex + er * .7, ey - er * 1.6 + bro * sgn * er * .3, paint(st["hair"] if st["hair_style"] != "cap" else "#3a2a20", stroke=r * .07))
    if st.get("glasses"):
        for ex in (ex1, ex2):
            c.drawCircle(ex, ey, er * 1.55, paint("#2a2a2a", stroke=3.5))
        c.drawLine(ex1 + er * 1.5, ey, ex2 - er * 1.5, ey, paint("#2a2a2a", stroke=3))
    # nose
    c.drawPath(oval(hx + r * .45, hy + r * .32, r * .09, r * .07), paint("#d08a6a", a=.8))
    # blush
    if st is STYLES["orion"] or P.get("blush"):
        c.drawCircle(hx + r * .03, hy + r * .42, r * .14, paint(st["blush"], a=.5, blur=4))
        c.drawCircle(hx + r * .8, hy + r * .4, r * .1, paint(st["blush"], a=.45, blur=4))
    # mouth
    mx, my = hx + r * .42, hy + r * .58
    m = P["mouth"]; mw = r * .26
    mp = paint(INK, stroke=4)
    if m == "smile":
        a = skia.Path(); a.moveTo(mx - mw, my - 2); a.quadTo(mx, my + mw * .8, mx + mw, my - 4); c.drawPath(a, mp)
    elif m in ("grin", "laugh"):
        a = skia.Path(); a.moveTo(mx - mw * 1.1, my - 4); a.quadTo(mx, my + mw * 1.5, mx + mw * 1.1, my - 6); a.close()
        c.drawPath(a, paint("#7a2a2a")); c.drawPath(a, paint(INK, stroke=3.5))
        c.drawPath(oval(mx, my + mw * .55, mw * .5, mw * .25), paint("#f07a7a"))
    elif m == "open":
        c.drawPath(oval(mx, my + 3, mw * .55, mw * .65), paint("#7a2a2a")); c.drawPath(oval(mx, my + 3, mw * .55, mw * .65), paint(INK, stroke=3))
    elif m == "o":
        c.drawPath(oval(mx, my + 3, mw * .35, mw * .42), paint("#7a2a2a")); c.drawPath(oval(mx, my + 3, mw * .35, mw * .42), paint(INK, stroke=3))
    elif m == "frown":
        a = skia.Path(); a.moveTo(mx - mw, my + 6); a.quadTo(mx, my - mw * .5, mx + mw, my + 4); c.drawPath(a, mp)
    elif m == "talk":
        o = .5 + .5 * abs(math.sin(t * 13))
        c.drawPath(oval(mx, my + 2, mw * .6, mw * .2 + mw * .45 * o), paint("#7a2a2a")); c.drawPath(oval(mx, my + 2, mw * .6, mw * .2 + mw * .45 * o), paint(INK, stroke=3))
    else:
        c.drawLine(mx - mw * .8, my, mx + mw * .8, my, mp)
    if st.get("lips") and m in ("smile", "flat"):
        pass

# ------------------------------------------------------------------ torso
def draw_torso(c, st, P, hip_y, neck_y):
    bw0, bw1 = st["body_w"]
    t = P["t"]
    path = smooth_path([(-bw1 * .55, hip_y + 6), (bw1 * .55, hip_y + 6), (bw0 * .55, neck_y + 18), (bw0 * .3, neck_y), (-bw0 * .3, neck_y), (-bw0 * .6, neck_y + 18)], True, .35)
    outline(c, path, st["shirt"], width=5)
    c.save(); c.clipPath(path, doAntiAlias=True)
    if st.get("stripes"):
        for i in range(6):
            y = neck_y + 14 + i * 17
            c.drawRect(skia.Rect.MakeLTRB(-80, y, 80, y + 8), paint(st["shirt2"]))
    if st.get("plaid"):
        for i in range(-4, 5):
            c.drawRect(skia.Rect.MakeLTRB(i * 18 - 4, neck_y, i * 18 + 4, hip_y + 10), paint(st["shirt2"], a=.45))
        for j in range(9):
            y = neck_y + j * 18
            c.drawRect(skia.Rect.MakeLTRB(-90, y, 90, y + 7), paint(st["shirt2"], a=.4))
    if st.get("pj_stars"):
        rnd = random.Random(11)
        for i in range(7):
            star4(c, rnd.uniform(-bw0 * .5, bw0 * .5), rnd.uniform(neck_y + 10, hip_y), 3.5, "#ffd84a", .95)
    if st.get("vest"):
        c.drawRect(skia.Rect.MakeLTRB(-100, neck_y, -bw0 * .12, hip_y + 10), paint(st["vest"]))
        c.drawRect(skia.Rect.MakeLTRB(bw0 * .12, neck_y, 100, hip_y + 10), paint(st["vest"]))
        for y in (neck_y + (hip_y - neck_y) * .45, neck_y + (hip_y - neck_y) * .75):
            c.drawRect(skia.Rect.MakeLTRB(-100, y, 100, y + 10), paint("#e8eef0"))
    c.restore()
    if P.get("heart", 0) > 0:
        h = P["heart"]; hy = neck_y + (hip_y - neck_y) * .32
        c.drawCircle(bw0 * .15, hy, 70 * h, paint("#ff6b8a", a=.35 * min(1, h), blur=40 * h + 5))
        c.drawPath(heart_path(bw0 * .15, hy, 15 * (0.7 + .3 * h) * (1 + .08 * math.sin(t * 8))), paint("#ff4d6d", a=min(1, h)))
        c.drawPath(heart_path(bw0 * .15, hy, 15 * (0.7 + .3 * h)), paint("#fff0f0", a=.5 * min(1, h), stroke=2))

# ------------------------------------------------------------------ the rig
def draw_person(c, who, pose=None, **kw):
    P = default_pose()
    if pose: P.update(pose)
    P.update(kw)
    st = dict(STYLES[who])
    if who == "orion" and P["outfit"] in OUTFITS:
        st.update(OUTFITS[P["outfit"]])
    t = P["t"]
    l1, l2 = st["leg"]
    hip_y = -(l1 + l2) * .96
    neck_y = hip_y - st["torso"]
    head_r = st["head_r"]
    c.save()
    c.translate(P["x"], P["y"] + P["bob"])
    c.scale(P["s"] * P["face"], P["s"] * P["squash"])
    if P["lean"]:
        c.translate(0, hip_y); c.rotate(P["lean"]); c.translate(0, -hip_y)
    sh_y = neck_y + 18
    # --- cape (behind everything)
    if P["cape"]: cape_back(c, st, t, P["cape_flow"], P["face"], flutter=P.get("cape_flutter"))
    # --- back arm
    shB = (-st["shoulder"] * .4, sh_y)
    eB, hB, _ = limb(c, shB, P["armB"][0], P["armB"][1], st["arm"][0], st["arm"][1], st["limb_w"][1], st["limb_w"][1] * .9,
                     mix_c(rgb(st["shirt"] if st["sleeve_long"] else st["skin"]), (40, 30, 30), .18))
    hand(c, *hB, st, st["limb_w"][1] * .55)
    if P["wings"]: wing(c, shB, eB, hB, P["wings"], t, -1, P["flap"])
    # --- back leg
    hpB = (-st["hip"], hip_y)
    kB, fB, aB = limb(c, hpB, P["legB"][0], -P["legB"][1], l1, l2, st["limb_w"][0], st["limb_w"][0], mix_c(rgb(st["pants"]), (20, 20, 30), .2))
    if P["shoes"]: shoe(c, fB[0], fB[1] + 4, aB, st)
    else:
        c.drawPath(oval(fB[0] + 6, fB[1] + 2, 15, 9), paint(INK, a=.8)); c.drawPath(oval(fB[0] + 6, fB[1] + 2, 12, 7), paint("#ffffff"))
    # --- front leg
    hpF = (st["hip"] * .6, hip_y)
    kF, fF, aF = limb(c, hpF, P["legF"][0], -P["legF"][1], l1, l2, st["limb_w"][0], st["limb_w"][0], st["pants"])
    if P["shoes"]: shoe(c, fF[0], fF[1] + 4, aF, st)
    else:
        c.drawPath(oval(fF[0] + 6, fF[1] + 2, 15, 9), paint(INK, a=.8)); c.drawPath(oval(fF[0] + 6, fF[1] + 2, 12, 7), paint("#ffffff"))
    # --- front wing goes behind torso/head so it never hides the face
    shF = (st["shoulder"] * .5, sh_y)
    if P["wings"]:
        eF0, hF0 = limb_geom(shF, P["armF"][0], P["armF"][1], st["arm"][0], st["arm"][1])
        wing(c, shF, eF0, hF0, P["wings"], t, 1, P["flap"])
    # --- torso
    draw_torso(c, st, P, hip_y, neck_y)
    # --- head
    hx, hy = 6, neck_y - head_r * .78
    c.save(); c.translate(0, neck_y); c.rotate(P["head_tilt"]); c.translate(0, -neck_y)
    c.drawRect(skia.Rect.MakeLTRB(-8, neck_y - 14, 14, neck_y + 6), paint(st["skin"]))
    draw_head(c, st, P, hx, hy, head_r)
    c.restore()
    # --- front arm
    eF, hF, _ = limb(c, shF, P["armF"][0], P["armF"][1], st["arm"][0], st["arm"][1], st["limb_w"][1], st["limb_w"][1] * .9,
                     st["shirt"] if st["sleeve_long"] else st["skin"])
    if st.get("vest") and not st["sleeve_long"]:
        pass
    hand(c, *hF, st, st["limb_w"][1] * .55)
    c.restore()
    return dict(hand_front=hF, head=(hx, hy))

# ------------------------------------------------------------------ motion helpers
def walk_pose(t, speed=1.0, amp=1.0):
    ph = t * 2 * math.pi * 1.4 * speed
    s = math.sin(ph)
    return dict(legF=(28 * s * amp, max(0, -s) * 30 * amp + 6), legB=(-28 * s * amp, max(0, s) * 30 * amp + 6),
                armF=(-24 * s * amp, 20), armB=(24 * s * amp, 20), bob=-abs(math.cos(ph)) * 6 * amp)

def run_pose(t, speed=1.0, flap=False):
    ph = t * 2 * math.pi * 2.2 * speed
    s = math.sin(ph)
    p = dict(legF=(45 * s, max(0, -s) * 70 + 15), legB=(-45 * s, max(0, s) * 70 + 15),
             lean=10, bob=-abs(math.cos(ph)) * 18)
    if flap:
        f = math.sin(t * 2 * math.pi * 3.2)
        p.update(armF=(110 + 55 * f, -10 - 15 * f), armB=(105 + 55 * f, -10 - 15 * f), flap=abs(f))
    else:
        p.update(armF=(-50 * s, 60), armB=(50 * s, 60))
    return p

def flap_pose(t, rate=3.0):
    f = math.sin(t * 2 * math.pi * rate)
    return dict(armF=(108 + 62 * f, -8 - 12 * f), armB=(100 + 62 * f, -8 - 12 * f), flap=abs(f))

def fly_pose(t, mode="superman"):
    if mode == "superman":
        return dict(lean=74, head_tilt=-58, armF=(168, 4), armB=(160, 8), legF=(-8, 14), legB=(-18, 28), cape=True, cape_flow=.4,
                    cape_flutter=1.6, hair_wind=1.0, bob=6 * math.sin(t * 2))
    if mode == "chest":
        return dict(lean=66, head_tilt=-50, armF=(-25, 20), armB=(-35, 20), legF=(-10, 22), legB=(-25, 34), cape=True, cape_flow=.45,
                    cape_flutter=1.5, hair_wind=1.0, bob=6 * math.sin(t * 2))
    if mode == "float":
        return dict(lean=8 * math.sin(t * 1.3), armF=(70 + 20 * math.sin(t * 2), 20), armB=(60 + 20 * math.sin(t * 2 + 1), 20),
                    legF=(10 + 8 * math.sin(t * 1.7), 25), legB=(-10 + 8 * math.sin(t * 1.5), 35), cape=True, cape_flow=.25,
                    bob=14 * math.sin(t * 1.6))
    return {}

# ------------------------------------------------------------------ chickens
def chicken(c, x, y, s=1.0, t=0.0, face=1, peck=0.0, color="#ffffff", seed=0, hop=0.0):
    c.save(); c.translate(x, y - abs(math.sin(hop)) * 20 * s); c.scale(s * face, s)
    rnd = random.Random(seed)
    # legs
    for dx in (-8, 8):
        c.drawLine(dx, -28, dx + 2, 0, paint("#e8a020", stroke=4))
        c.drawLine(dx + 2, 0, dx + 12, 2, paint("#e8a020", stroke=3))
    body = smooth_path([(-42, -50), (-30, -78), (5, -70), (30, -55), (28, -30), (-10, -22), (-40, -32)], True, .8)
    outline(c, body, color, width=4)
    # tail
    for i in range(3):
        c.drawPath(oval(-44 - i * 5, -66 + i * 8, 10, 18), paint(mix_c(rgb(color), (120, 70, 40), .25)))
    # wing
    c.drawPath(oval(-6, -48, 22, 13), paint(mix_c(rgb(color), (100, 60, 30), .2))); c.drawPath(oval(-6, -48, 22, 13), paint(INK, stroke=2.5, a=.6))
    # neck/head
    c.save(); c.translate(22, -60); c.rotate(70 * peck)
    c.drawPath(oval(10, -18, 15, 17), paint(color)); c.drawPath(oval(10, -18, 15, 17), paint(INK, stroke=3))
    c.drawPath(smooth_path([(2, -33), (6, -44), (12, -36), (17, -45), (22, -32)], True, .6), paint("#e0352b"))
    c.drawPath(poly([(24, -20), (36, -16), (24, -12)]), paint("#f2a81d"))
    c.drawPath(oval(22, -6, 4, 6), paint("#e0352b"))
    c.drawCircle(15, -22, 3.2, paint("#1a1010"))
    c.restore()
    c.restore()
