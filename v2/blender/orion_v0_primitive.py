"""Orion — procedural 3D character, rigged.

Design carried from Version 1 so he stays recognisable across versions: dark-brown hair with
a cowlick, orange/cream striped shirt, blue jeans, red sneakers. Proportions are moved away
from V1's preschool look toward an ~8-year-old in a stylised feature-film register
(head ≈ 1/5.3 of height, 1.30 m tall).

build_orion(name) -> dict with 'arm' (armature) and handles for face controls.
Character faces -Y. Rest pose is an A-pose.
"""
import math
import bmesh
import bpy
from mathutils import Vector

import common as C

PAL = dict(
    skin="#e9b08c", skin_shadow="#c98a6c", hair="#3b2416", hair_hi="#6a4129",
    stripe_a="#e8772e", stripe_b="#f4e6cc", jeans="#3d5b8c", jeans_hi="#5878a8",
    shoe="#c8262a", sole="#f2efe8", iris="#5a3a22", lip="#b5655a",
)

# ---------------------------------------------------------------- skeleton (A-pose)
J = {
    "pelvis": (0, 0, 0.70), "spine": (0, 0.005, 0.84), "chest": (0, 0.0, 0.97),
    "neck": (0, 0.01, 1.06), "headbase": (0, 0.01, 1.10), "headtop": (0, 0.01, 1.36),
}
for s, sx in (("L", 1), ("R", -1)):
    J[f"clav.{s}"] = (sx * 0.06, 0.0, 1.015)
    J[f"shoulder.{s}"] = (sx * 0.135, 0.0, 1.005)
    J[f"elbow.{s}"] = (sx * 0.270, 0.012, 0.850)
    J[f"wrist.{s}"] = (sx * 0.385, 0.0, 0.720)
    J[f"handtip.{s}"] = (sx * 0.435, -0.005, 0.665)
    J[f"hip.{s}"] = (sx * 0.072, 0.0, 0.665)
    J[f"knee.{s}"] = (sx * 0.078, -0.012, 0.375)
    J[f"ankle.{s}"] = (sx * 0.080, 0.0, 0.085)
    J[f"toe.{s}"] = (sx * 0.082, -0.13, 0.03)

# skin radii (x, y) per joint
R = {
    "pelvis": (0.118, 0.085), "spine": (0.108, 0.075), "chest": (0.122, 0.082),
    "neck": (0.036, 0.036), "headbase": (0.04, 0.04),
}
for s in "LR":
    R[f"clav.{s}"] = (0.06, 0.06)
    R[f"shoulder.{s}"] = (0.052, 0.052)
    R[f"elbow.{s}"] = (0.038, 0.038)
    R[f"wrist.{s}"] = (0.027, 0.027)
    R[f"handtip.{s}"] = (0.026, 0.017)
    R[f"hip.{s}"] = (0.072, 0.072)
    R[f"knee.{s}"] = (0.052, 0.052)
    R[f"ankle.{s}"] = (0.045, 0.045)

BODY_EDGES = [("pelvis", "spine"), ("spine", "chest"), ("chest", "neck"), ("neck", "headbase")]
for s in "LR":
    BODY_EDGES += [("chest", f"clav.{s}"), (f"clav.{s}", f"shoulder.{s}"),
                   (f"shoulder.{s}", f"elbow.{s}"), (f"elbow.{s}", f"wrist.{s}"),
                   (f"wrist.{s}", f"handtip.{s}"),
                   ("pelvis", f"hip.{s}"), (f"hip.{s}", f"knee.{s}"), (f"knee.{s}", f"ankle.{s}")]

# bones: name -> (head joint, tail joint, parent)
BONES = {
    "root": ("pelvis", None, None),
    "hips": ("pelvis", "spine", "root"),
    "spine": ("spine", "chest", "hips"),
    "chest": ("chest", "neck", "spine"),
    "neck": ("neck", "headbase", "chest"),
    "head": ("headbase", "headtop", "neck"),
}
for s in "LR":
    BONES[f"clav.{s}"] = ("chest", f"shoulder.{s}", "chest")
    BONES[f"upperarm.{s}"] = (f"shoulder.{s}", f"elbow.{s}", f"clav.{s}")
    BONES[f"forearm.{s}"] = (f"elbow.{s}", f"wrist.{s}", f"upperarm.{s}")
    BONES[f"hand.{s}"] = (f"wrist.{s}", f"handtip.{s}", f"forearm.{s}")
    BONES[f"thigh.{s}"] = (f"hip.{s}", f"knee.{s}", "hips")
    BONES[f"shin.{s}"] = (f"knee.{s}", f"ankle.{s}", f"thigh.{s}")
    BONES[f"foot.{s}"] = (f"ankle.{s}", f"toe.{s}", f"shin.{s}")

DEFORM = [b for b in BONES if b != "root" and not b.startswith("foot")]

HEAD_C = Vector((0, -0.005, 1.215))   # cranium centre
HEAD_R = 0.118


# ---------------------------------------------------------------- materials
def materials():
    M = {}
    skin = C.principled("orion_skin", PAL["skin"], rough=0.45, sss=0.12, spec=0.4)
    M["skin"] = skin
    # striped shirt on undeformed (Generated) Z so stripes ride with the cloth
    sh = C.principled("orion_shirt", PAL["stripe_a"], rough=0.85, sheen=0.4,
                      bump=(180.0, 0.12))
    nt = sh.node_tree
    p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 34.0
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    st = nt.nodes.new("ShaderNodeMath"); st.operation = "GREATER_THAN"; st.inputs[1].default_value = 0.58
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = C.hexc(PAL["stripe_a"])
    mix.inputs["B"].default_value = C.hexc(PAL["stripe_b"])
    C.link(nt, tc.outputs["Generated"], sep.inputs[0])
    C.link(nt, sep.outputs["Z"], mul.inputs[0])
    C.link(nt, mul.outputs[0], fr.inputs[0])
    C.link(nt, fr.outputs[0], st.inputs[0])
    C.link(nt, st.outputs[0], mix.inputs["Factor"])
    C.link(nt, mix.outputs["Result"], p.inputs["Base Color"])
    M["shirt"] = sh
    j = C.principled("orion_jeans", PAL["jeans"], rough=0.9, sheen=0.2, bump=(260.0, 0.2))
    C.noise_color(j, PAL["jeans"], PAL["jeans_hi"], scale=60, lo=0.45, hi=0.75)
    M["jeans"] = j
    hair = C.principled("orion_hair", PAL["hair"], rough=0.38, sheen=0.6, spec=0.6,
                        bump=(90.0, 0.35))
    C.noise_color(hair, PAL["hair"], PAL["hair_hi"], scale=22, lo=0.5, hi=0.85)
    M["hair"] = hair
    M["shoe"] = C.principled("orion_shoe", PAL["shoe"], rough=0.55, coat=0.2)
    M["sole"] = C.principled("orion_sole", PAL["sole"], rough=0.7)
    M["lip"] = C.principled("orion_mouth", "#5a2522", rough=0.5)
    M["brow"] = C.principled("orion_brow", "#2f1c11", rough=0.7)
    # eyes: iris/pupil computed in eyeball object space (gaze = rotate the eyeball)
    ey = C.principled("orion_eye", "#f6f1ea", rough=0.05, coat=1.0, spec=0.7)
    nt = ey.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Coat Roughness"].default_value = 0.02
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    C.link(nt, tc.outputs["Object"], sep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    C.link(nt, sep.outputs["X"], comb.inputs["X"]); C.link(nt, sep.outputs["Z"], comb.inputs["Y"])
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    C.link(nt, comb.outputs[0], ln.inputs[0])
    front = nt.nodes.new("ShaderNodeMath"); front.operation = "LESS_THAN"; front.inputs[1].default_value = 0.0
    C.link(nt, sep.outputs["Y"], front.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "EASE"
    cr.elements[0].position = 0.0; cr.elements[0].color = C.hexc("#0b0705")
    cr.elements[1].position = 0.30; cr.elements[1].color = C.hexc("#0b0705")
    e = cr.elements.new(0.34); e.color = C.hexc(PAL["iris"])
    e = cr.elements.new(0.50); e.color = C.hexc("#8a6038")
    e = cr.elements.new(0.58); e.color = C.hexc("#3a2414")
    e = cr.elements.new(0.62); e.color = C.hexc("#f6f1ea")
    div = nt.nodes.new("ShaderNodeMath"); div.operation = "DIVIDE"; div.inputs[1].default_value = 1.0
    C.link(nt, ln.outputs["Value"], div.inputs[0])
    C.link(nt, div.outputs[0], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = C.hexc("#f6f1ea")
    C.link(nt, front.outputs[0], mix.inputs["Factor"])
    C.link(nt, ramp.outputs["Color"], mix.inputs["B"])
    C.link(nt, mix.outputs["Result"], p.inputs["Base Color"])
    M["eye"] = ey
    M["_eye_div"] = div
    cb = C.principled("cardboard", "#b98a55", rough=0.92, bump=(40.0, 0.25))
    C.noise_color(cb, "#a87a48", "#c99a64", scale=14, lo=0.4, hi=0.7)
    M["cardboard"] = cb
    M["tape"] = C.principled("tape", "#d9d2bf", rough=0.35, spec=0.6)
    return M


# ---------------------------------------------------------------- body
def _seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length, t


def build_body(M, coll):
    names = list(J.keys())
    idx = {n: i for i, n in enumerate(names)}
    body_joints = sorted({a for e in BODY_EDGES for a in e}, key=lambda n: idx[n])
    vidx = {n: i for i, n in enumerate(body_joints)}
    ob = C.mesh_obj("orion_body", [J[n] for n in body_joints],
                    [(vidx[a], vidx[b]) for a, b in BODY_EDGES], coll=coll)
    skin = ob.modifiers.new("skin", "SKIN")
    skin.use_smooth_shade = True
    skin.branch_smoothing = 0.6
    for n, i in vidx.items():
        sv = ob.data.skin_vertices[0].data[i]
        sv.radius = R[n]
        sv.use_root = (n == "pelvis")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier="skin")
    # one subdivision baked in, one live at render
    sd = ob.modifiers.new("pre", "SUBSURF"); sd.levels = 1
    bpy.ops.object.modifier_apply(modifier="pre")

    # sculpt pass: chest/belly soft shape, flatten back, broaden pelvis into seat
    for v in ob.data.vertices:
        co = v.co
        if 0.74 < co.z < 1.04 and abs(co.x) < 0.14:
            co.y -= 0.012 * math.sin((co.z - 0.74) / 0.30 * math.pi) * (1 if co.y < 0 else -0.4)
        if 0.6 < co.z < 0.74 and co.y > 0:
            co.y += 0.012

    # materials by region
    for m in ("shirt", "jeans", "skin"):
        ob.data.materials.append(M[m])
    jv = lambda n: Vector(J[n])
    for f in ob.data.polygons:
        c = f.center
        mat = 0
        if c.z < 0.725 and not (abs(c.x) > 0.25):
            mat = 1
        if c.z > 1.035:
            mat = 2
        for s in "LR":
            d, t = _seg_dist(c, jv(f"wrist.{s}"), jv(f"handtip.{s}"))
            wd, wt = _seg_dist(c, jv(f"elbow.{s}"), jv(f"wrist.{s}"))
            if d < 0.06 and t > 0.0 and (c - jv(f"wrist.{s}")).dot(jv(f"handtip.{s}") - jv(f"wrist.{s}")) > -0.004:
                mat = 2
            elif wd < 0.06 and wt > 0.86:      # bare wrist below the sleeve cuff
                mat = 2
        f.material_index = mat
    C.smooth(ob, subsurf=1, render_levels=2)
    return ob


def build_armature(coll):
    arm_d = bpy.data.armatures.new("orion_rig")
    arm = bpy.data.objects.new("orion", arm_d)
    coll.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (h, t, par) in BONES.items():
        b = arm_d.edit_bones.new(name)
        b.head = J[h]
        b.tail = J[t] if t else (J[h][0], J[h][1] + 0.0, J[h][2] - 0.25)
        if name == "root":
            b.tail = (0, 0.25, J[h][2])
        if par:
            b.parent = arm_d.edit_bones[par]
            b.use_connect = False
    # roll so local X is a consistent bend axis on limbs
    for b in arm_d.edit_bones:
        b.roll = 0.0
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.show_in_front = True
    return arm


def weight_body(body, arm):
    """Distance-based skinning, blended between the two nearest bones."""
    segs = {b: (Vector(J[BONES[b][0]]), Vector(J[BONES[b][1]])) for b in DEFORM}
    groups = {b: body.vertex_groups.new(name=b) for b in DEFORM}
    for v in body.data.vertices:
        p = v.co
        ds = []
        for b, (a, c) in segs.items():
            d, t = _seg_dist(p, a, c)
            # keep the arms off the torso and the legs off each other
            side = 1 if p.x > 0 else -1
            if b.endswith(".L") and p.x < 0.02: d += 1.0
            if b.endswith(".R") and p.x > -0.02: d += 1.0
            ds.append((d, b))
        ds.sort()
        (d0, b0), (d1, b1) = ds[0], ds[1]
        w0 = 1.0 / max(d0, 1e-4) ** 6
        w1 = 1.0 / max(d1, 1e-4) ** 6
        s = w0 + w1
        groups[b0].add([v.index], w0 / s, "REPLACE")
        if w1 / s > 0.02:
            groups[b1].add([v.index], w1 / s, "REPLACE")
    md = body.modifiers.new("rig", "ARMATURE")
    md.object = arm
    md.use_deform_preserve_volume = True
    body.modifiers.move(len(body.modifiers) - 1, 0)
    body.parent = arm


# ---------------------------------------------------------------- head & face
def build_head(M, coll):
    parts = []
    bpy.ops.mesh.primitive_uv_sphere_add(radius=HEAD_R, location=HEAD_C, segments=48, ring_count=32)
    head = bpy.context.object
    head.name = "orion_head"
    for v in head.data.vertices:
        p = v.co.copy()
        z = p.z / HEAD_R                       # -1..1 (local, sphere is centred at origin)
        # cranium slightly taller, back of head fuller
        p.z *= 1.05
        if p.y > 0: p.y *= 1.06
        else: p.y *= 0.96
        # jaw taper + soft chin
        if z < 0.05:
            t = (0.05 - z) / 1.05
            p.x *= 1.0 - 0.30 * t ** 1.3
            p.y *= 1.0 - 0.18 * t
            if p.y < 0: p.y -= 0.010 * math.sin(min(1, t * 1.6) * math.pi) * (1 if p.y < -0.05 else 0.3)
            p.z -= 0.016 * t
        # cheeks
        if -0.55 < z < 0.05 and p.y < -0.03 and abs(p.x) > 0.04:
            p.x *= 1.04; p.y -= 0.004
        # eye sockets: very soft depression
        for sx in (1, -1):
            d = math.hypot(p.x - sx * 0.042, p.z - 0.008)
            if p.y < -0.05 and d < 0.035:
                p.y += 0.006 * (1 - d / 0.035)
        v.co = p
    C.smooth(head, subsurf=1, render_levels=2)
    C.assign(head, M["skin"])
    parts.append(head)

    def at(x, y, z):
        return HEAD_C + Vector((x, y, z))

    # ears
    for sx in (1, -1):
        e = C.uv_sphere(f"orion_ear.{'L' if sx > 0 else 'R'}", 0.028, at(sx * 0.114, 0.004, -0.008),
                        (0.42, 0.85, 1.25), 24, 12)
        e.rotation_euler = (0, sx * 0.25, 0)
        C.smooth(e, 1); C.assign(e, M["skin"]); parts.append(e)
    # nose
    n = C.uv_sphere("orion_nose", 0.017, at(0, -0.118, -0.028), (1.0, 0.9, 0.85), 24, 12)
    C.smooth(n, 1); C.assign(n, M["skin"]); parts.append(n)

    # eyes (eyeball radius 0.02, slightly large for appeal, not preschool)
    eyes, lids = [], []
    er = 0.0205
    M["_eye_div"].inputs[1].default_value = er
    for sx, s in ((1, "L"), (-1, "R")):
        loc = at(sx * 0.043, -0.098, 0.006)
        ey = C.uv_sphere(f"orion_eye.{s}", er, loc, (1, 1, 1), 32, 16)
        C.smooth(ey); C.assign(ey, M["eye"]); parts.append(ey); eyes.append(ey)
        # upper lid: hemisphere shell; rotate on X to blink
        bpy.ops.mesh.primitive_uv_sphere_add(radius=er * 1.12, location=loc, segments=32, ring_count=16)
        lid = bpy.context.object; lid.name = f"orion_lid.{s}"
        bm = bmesh.new(); bm.from_mesh(lid.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.001], context="VERTS")
        bm.to_mesh(lid.data); bm.free()
        sol = lid.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.002
        C.smooth(lid, 1); C.assign(lid, M["skin"])
        lid.rotation_euler = (-0.55, 0, 0)       # resting open
        parts.append(lid); lids.append(lid)
        # lower lid hint
        bpy.ops.mesh.primitive_torus_add(major_radius=er * 0.98, minor_radius=0.0025,
                                         location=loc, rotation=(math.pi / 2 + 0.95, 0, 0))
        ll = bpy.context.object; ll.name = f"orion_lowlid.{s}"
        C.smooth(ll); C.assign(ll, M["skin"]); parts.append(ll)
        # brows
        bx = sx * 0.044
        br = C.curve_tube(f"orion_brow.{s}",
                          [at(bx - sx * 0.026, -0.110, 0.034), at(bx, -0.118, 0.042),
                           at(bx + sx * 0.024, -0.110, 0.038)],
                          radius=0.0042, taper=[0.6, 1.0, 0.7], coll=coll)
        br.data.materials.append(M["hair"]); parts.append(br)

    # mouth: soft open "effort" mouth sunk into the face (shape set per shot)
    mo = C.uv_sphere("orion_mouth", 0.019, at(0, -0.106, -0.058), (1.25, 0.55, 0.55), 24, 12)
    C.smooth(mo, 1); C.assign(mo, M["lip"]); parts.append(mo)

    # hair: cap from a sphere shell trimmed at a hairline, lumpy displacement, clumps
    bpy.ops.mesh.primitive_uv_sphere_add(radius=HEAD_R * 1.07, location=HEAD_C, segments=48, ring_count=32)
    cap = bpy.context.object; cap.name = "orion_hair"
    bm = bmesh.new(); bm.from_mesh(cap.data)
    kill = []
    for v in bm.verts:
        x, y, z = v.co
        front = max(0.0, -y / (HEAD_R * 1.07))           # 1 at the face
        side = abs(x) / (HEAD_R * 1.07)
        line = 0.050 * front ** 1.5 - 0.018 * side - 0.062 * max(0.0, y / HEAD_R) - 0.004
        if z < line * 1.0 + (0.016 if (abs(x) > 0.07 and y < 0.02 and abs(z) < 0.05) else 0):
            kill.append(v)
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(cap.data); bm.free()
    for v in cap.data.vertices:
        v.co.z *= 1.05
        if v.co.y > 0: v.co.y *= 1.06
    tex = bpy.data.textures.new("hairclump", "VORONOI")
    tex.noise_scale = 0.035
    dp = cap.modifiers.new("clump", "DISPLACE"); dp.texture = tex; dp.strength = 0.012
    dp.texture_coords = "OBJECT"
    sol = cap.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.012; sol.offset = -1
    C.smooth(cap, 1, 2); C.assign(cap, M["hair"]); parts.append(cap)
    # swept fringe clumps over the forehead
    for i, (x0, sweep) in enumerate(((-0.055, 0.02), (-0.02, 0.025), (0.018, 0.03), (0.05, 0.022))):
        tip = at(x0 + sweep, -0.118, 0.052 - 0.004 * i)
        pts = [at(x0 - 0.01, -0.06, 0.112), at(x0 + sweep * 0.4, -0.108, 0.088), tip]
        cl = C.curve_tube(f"orion_fringe{i}", pts, radius=0.016, taper=[1.0, 0.85, 0.15], coll=coll)
        cl.data.materials.append(M["hair"]); parts.append(cl)
    # the cowlick — Orion's signature curl, kept from Version 1
    ck = [at(0.0, 0.0, 0.128), at(0.004, 0.006, 0.160), at(0.020, 0.016, 0.178),
          at(0.034, 0.008, 0.170), at(0.030, -0.006, 0.156)]
    cw = C.curve_tube("orion_cowlick", ck, radius=0.008, taper=[1.0, 0.9, 0.7, 0.45, 0.1], coll=coll)
    cw.data.materials.append(M["hair"]); parts.append(cw)
    return parts, eyes, lids, mo


def build_shoes(M, coll):
    shoes = {}
    for sx, s in ((1, "L"), (-1, "R")):
        a = Vector(J[f"ankle.{s}"])
        upper = C.cube(f"orion_shoe.{s}", (0.085, 0.19, 0.075), (a.x, a.y - 0.045, 0.048), bevel=0.03, seg=4)
        for v in upper.data.vertices:            # toe rounding + heel lift
            if v.co.y < -0.06: v.co.z -= 0.012 * (abs(v.co.y) - 0.06) / 0.035
        C.smooth(upper, 2); C.assign(upper, M["shoe"])
        sole = C.cube(f"orion_sole.{s}", (0.092, 0.198, 0.022), (a.x, a.y - 0.045, 0.011), bevel=0.008, seg=3)
        C.smooth(sole, 1); C.assign(sole, M["sole"])
        toe = C.uv_sphere(f"orion_toecap.{s}", 0.042, (a.x, a.y - 0.118, 0.03), (1.0, 0.75, 0.55), 24, 12)
        C.smooth(toe, 1); C.assign(toe, M["sole"])
        shoes[s] = [upper, sole, toe]
    return shoes


def build_wings(M, coll):
    """Cardboard wings taped along each arm (scene 1–2): two overlapping panels per arm."""
    wings = {}
    for sx, s in ((1, "L"), (-1, "R")):
        sets = []
        for bone, (j0, j1), depth in (("upperarm", ("shoulder", "elbow"), 0.30),
                                      ("forearm", ("elbow", "handtip"), 0.26)):
            a, b = Vector(J[f"{j0}.{s}"]), Vector(J[f"{j1}.{s}"])
            along = (b - a)
            down = Vector((0, 0, -1))
            down = (down - along.normalized() * down.dot(along.normalized())).normalized()
            n = 7
            verts = []
            for i in range(n):
                t = i / (n - 1)
                top = a + along * t + Vector((0, 0.03, 0))
                # scalloped trailing edge, longer toward the shoulder
                d = depth * (1.0 - 0.35 * t) * (0.86 + 0.14 * math.cos(t * math.pi * 3))
                verts += [top + down * 0.02, top + down * d + Vector((0, 0.04 * t, 0))]
            faces = [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(n - 1)]
            w = C.mesh_obj(f"orion_wing_{bone}.{s}", verts, faces=faces, coll=coll)
            sol = w.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.006
            C.smooth(w); C.assign(w, M["cardboard"])
            sets.append((w, f"{bone}.{s}"))
            # tape bands
            for t in (0.25, 0.75):
                c = a + along * t
                bpy.ops.mesh.primitive_cylinder_add(radius=0.047 if bone == "upperarm" else 0.036,
                                                    depth=0.028, location=c, vertices=20)
                tb = bpy.context.object; tb.name = f"orion_tape_{bone}{t}.{s}"
                tb.rotation_mode = "QUATERNION"
                tb.rotation_quaternion = along.to_track_quat("Z", "Y")
                C.smooth(tb); C.assign(tb, M["tape"])
                sets.append((tb, f"{bone}.{s}"))
        wings[s] = sets
    return wings


def build_orion(coll=None, wings=True):
    coll = coll or bpy.context.scene.collection
    M = materials()
    arm = build_armature(coll)
    body = build_body(M, coll)
    weight_body(body, arm)
    parts, eyes, lids, mouth = build_head(M, coll)
    for p in parts:
        C.parent_to_bone(p, arm, "head")
    # eyes & lids are re-parented so they rotate in place: keep as head children
    shoes = build_shoes(M, coll)
    for s, objs in shoes.items():
        for o in objs:
            C.parent_to_bone(o, arm, f"foot.{s}")
    wing_objs = []
    if wings:
        for s, sets in build_wings(M, coll).items():
            for o, bone in sets:
                C.parent_to_bone(o, arm, bone)
                wing_objs.append(o)
    return dict(arm=arm, body=body, eyes=eyes, lids=lids, mouth=mouth, wings=wing_objs, M=M)


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    C.reset()
    o = build_orion()
    out = sys.argv[-1] if sys.argv[-1].endswith(".blend") else "/tmp/orion.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print("saved", out)
