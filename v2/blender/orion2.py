"""Orion (v2 character): CC0 MakeHuman child base + procedural costume, hair and eyes.

Continuity with Version 1: dark-brown hair with a cowlick, orange/cream striped long-sleeve
shirt, blue jeans, red sneakers with white soles.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import mhload

HEIGHT = 1.30          # metres — a ~9-year-old
AGE_CHILD = 0.8        # blend: 0.8 child (~11y) + 0.2 baby (~1y)  -> reads ~8–9
RACE = {"caucasian": 0.6, "asian": 0.2, "african": 0.2}

PAL = dict(skin="#e8b18e", hair="#3b2416", hair_hi="#6e452b", stripe_a="#e07128",
           stripe_b="#f3e5c9", jeans="#3f5d8e", jeans_hi="#5c7cab", shoe="#c42428",
           sole="#f1eee6", iris="#6b4426", lip="#c07a6c")

SHIRT_BONES = ("spine", "clavicle", "shoulder", "upperarm", "lowerarm", "breast", "neck01")
JEANS_BONES = ("pelvis", "upperleg", "lowerleg", "root")
SHOE_BONES = ("foot", "toe")


def targets():
    t = []
    for race, w in RACE.items():
        t.append((f"macrodetails/{race}-male-child.target", w * AGE_CHILD))
        t.append((f"macrodetails/{race}-male-baby.target", w * (1 - AGE_CHILD)))
    # gentle stylisation: rounder head, a touch larger eyes (feature-animation register)
    t += [("head/head-round.target", 0.35),
          ("eyes/l-eye-scale-incr.target", 0.45), ("eyes/r-eye-scale-incr.target", 0.45)]
    return t


# ------------------------------------------------------------------ materials
def materials():
    M = {}
    M["skin"] = C.principled("o_skin", PAL["skin"], rough=0.48, sss=0.15, spec=0.4)
    # subtle cheek/lip warmth from a noise so the face is not a flat colour
    C.noise_color(M["skin"], "#e3a684", PAL["skin"], scale=9, lo=0.25, hi=0.7)
    sh = C.principled("o_shirt", PAL["stripe_a"], rough=0.88, sheen=0.5, bump=(220.0, 0.10))
    nt = sh.node_tree; p = nt.nodes["Principled BSDF"]
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "restz"
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 1 / 0.034
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    sm = nt.nodes.new("ShaderNodeMapRange"); sm.inputs["From Min"].default_value = 0.52
    sm.inputs["From Max"].default_value = 0.56
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = C.hexc(PAL["stripe_a"]); mix.inputs["B"].default_value = C.hexc(PAL["stripe_b"])
    C.link(nt, at.outputs["Fac"], mul.inputs[0]); C.link(nt, mul.outputs[0], fr.inputs[0])
    C.link(nt, fr.outputs[0], sm.inputs["Value"]); C.link(nt, sm.outputs["Result"], mix.inputs["Factor"])
    C.link(nt, mix.outputs["Result"], p.inputs["Base Color"])
    M["shirt"] = sh
    j = C.principled("o_jeans", PAL["jeans"], rough=0.92, sheen=0.25, bump=(320.0, 0.25))
    C.noise_color(j, PAL["jeans"], PAL["jeans_hi"], scale=45, lo=0.45, hi=0.8)
    M["jeans"] = j
    h = C.principled("o_hair", PAL["hair"], rough=0.45, sheen=0.15, spec=0.45)
    nt = h.node_tree; p = nt.nodes["Principled BSDF"]
    # strand-direction streaks: stretched noise along Z in object space + bump
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (260, 260, 18)
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Detail"].default_value = 3
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = C.hexc("#1c100a"); rp.color_ramp.elements[1].color = C.hexc("#4e2f1c")
    rp.color_ramp.elements[0].position = 0.35; rp.color_ramp.elements[1].position = 0.75
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5
    C.link(nt, tc.outputs["Object"], mp.inputs["Vector"]); C.link(nt, mp.outputs[0], nz.inputs["Vector"])
    C.link(nt, nz.outputs["Fac"], rp.inputs["Fac"]); C.link(nt, rp.outputs["Color"], p.inputs["Base Color"])
    C.link(nt, nz.outputs["Fac"], bp.inputs["Height"]); C.link(nt, bp.outputs["Normal"], p.inputs["Normal"])
    M["hair"] = h
    M["shoe"] = C.principled("o_shoe", PAL["shoe"], rough=0.6, coat=0.15, bump=(400.0, 0.08))
    M["sole"] = C.principled("o_sole", PAL["sole"], rough=0.75)
    # eye: iris/pupil computed in eyeball object space (gaze = rotate the eyeball)
    ey = C.principled("o_eye", "#f4efe8", rough=0.05, coat=1.0, spec=0.8)
    nt = ey.node_tree; p = nt.nodes["Principled BSDF"]; p.inputs["Coat Roughness"].default_value = 0.01
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    C.link(nt, tc.outputs["Object"], sep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    C.link(nt, sep.outputs["X"], comb.inputs["X"]); C.link(nt, sep.outputs["Z"], comb.inputs["Y"])
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; C.link(nt, comb.outputs[0], ln.inputs[0])
    dv = nt.nodes.new("ShaderNodeMath"); dv.operation = "DIVIDE"; dv.inputs[1].default_value = 1.0
    C.link(nt, ln.outputs["Value"], dv.inputs[0])
    front = nt.nodes.new("ShaderNodeMath"); front.operation = "LESS_THAN"; front.inputs[1].default_value = 0.0
    C.link(nt, sep.outputs["Y"], front.inputs[0])
    rp = nt.nodes.new("ShaderNodeValToRGB"); cr = rp.color_ramp; cr.interpolation = "EASE"
    cr.elements[0].position = 0.0; cr.elements[0].color = C.hexc("#080504")
    cr.elements[1].position = 0.24; cr.elements[1].color = C.hexc("#080504")
    for pos, col in ((0.28, "#3d2512"), (0.40, "#8a5a32"), (0.50, PAL["iris"]), (0.54, "#2a180c"), (0.575, "#f4efe8")):
        e = cr.elements.new(pos); e.color = C.hexc(col)
    C.link(nt, dv.outputs[0], rp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["A"].default_value = C.hexc("#f4efe8")
    C.link(nt, front.outputs[0], mix.inputs["Factor"]); C.link(nt, rp.outputs["Color"], mix.inputs["B"])
    C.link(nt, mix.outputs["Result"], p.inputs["Base Color"])
    M["eye"] = ey; M["_eye_div"] = dv
    cb = C.principled("o_cardboard", "#b98a55", rough=0.93, bump=(40.0, 0.3))
    C.noise_color(cb, "#a57646", "#cc9e68", scale=12, lo=0.4, hi=0.7)
    M["cardboard"] = cb
    M["tape"] = C.principled("o_tape", "#ddd6c2", rough=0.3, spec=0.6)
    return M


# ------------------------------------------------------------------ helpers
def dominant_bone(ob):
    names = {g.index: g.name for g in ob.vertex_groups}
    dom = []
    for v in ob.data.vertices:
        best, bw = None, 0.0
        for g in v.groups:
            if g.weight > bw:
                best, bw = names[g.group], g.weight
        dom.append(best or "")
    return dom


def face_sets(ob):
    dom = dominant_bone(ob)
    S = {"shirt": set(), "jeans": set(), "shoe": set()}
    for f in ob.data.polygons:
        bs = [dom[i] for i in f.vertices]
        c = f.center
        def has(prefixes):
            return sum(1 for b in bs if b.startswith(prefixes)) >= len(bs) / 2
        if has(SHOE_BONES) or c.z < 0.075:
            S["shoe"].add(f.index)
        elif ((has(JEANS_BONES) and c.z < 0.80) or c.z < 0.735) and not any(
                b.startswith(("wrist", "finger", "metacarpal", "lowerarm")) for b in bs):
            S["jeans"].add(f.index)
        elif has(SHIRT_BONES) and c.z > 0.70:
            # long sleeves stop at the wrist; collar sits at the base of the neck
            if any(b.startswith("wrist") or b.startswith(("finger", "metacarpal")) for b in bs):
                continue
            if any(b.startswith(("neck02", "neck03", "head")) for b in bs):
                continue
            S["shirt"].add(f.index)
    return S


def shell(body, faces, name, offset, thick, mat, coll):
    me = body.data.copy()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.parent = body.parent
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    kill = [f for f in bm.faces if f.index not in faces]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * offset
    bm.to_mesh(me); bm.free()
    for md in body.modifiers:
        if md.type == "ARMATURE":
            m2 = ob.modifiers.new("rig", "ARMATURE"); m2.object = md.object
            m2.use_deform_preserve_volume = True
    if thick:
        so = ob.modifiers.new("sol", "SOLIDIFY"); so.thickness = thick; so.offset = 1
        so.use_rim = True
    C.smooth(ob, subsurf=1, render_levels=1)
    C.assign(ob, mat)
    return ob


def hide_covered(body, faces):
    bm = bmesh.new(); bm.from_mesh(body.data)
    bm.faces.ensure_lookup_table()
    # keep a one-face margin under hems so no gaps show
    kill = []
    for f in bm.faces:
        if f.index in faces and all(all(lf.index in faces for lf in v.link_faces) for v in f.verts):
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context="FACES_ONLY")
    bm.to_mesh(body.data); bm.free()


# ------------------------------------------------------------------ build
def build_orion(coll=None, wings=True, name="orion"):
    coll = coll or bpy.context.scene.collection
    M = materials()
    body, arm, info = mhload.build_human(name + "_body", targets(), HEIGHT, coll)
    C.assign(body, M["skin"])
    lash = C.principled("o_lash", "#140c08", rough=0.6)
    body.data.materials.append(lash)
    lf = set(body["lash_faces"])
    for f in body.data.polygons:
        if f.index in lf:
            f.material_index = 1
    S = face_sets(body)
    for k in S:
        S[k] -= lf

    shirt = shell(body, S["shirt"], name + "_shirt", 0.006, 0.004, M["shirt"], coll)
    # stripes follow the rest-pose height of the cloth
    at = shirt.data.attributes.new("restz", "FLOAT", "POINT")
    for i, v in enumerate(shirt.data.vertices):
        at.data[i].value = v.co.z
    jeans = shell(body, S["jeans"], name + "_jeans", 0.008, 0.004, M["jeans"], coll)
    shoe = shell(body, S["shoe"], name + "_shoes", 0.014, 0.0, M["shoe"], coll)
    shoe.data.materials.append(M["sole"])
    for f in shoe.data.polygons:
        if f.center.z < 0.03:
            f.material_index = 1
    hide_covered(body, S["shirt"] | S["jeans"] | S["shoe"])

    # ---- eyes: replace the helper eyes with shaded eyeballs on the eye bones
    verts, _, faces, _, groups = mhload.read_obj()
    eyes = []
    for side in ("l", "r"):
        ids = {v for f, g in zip(faces, groups) if g == f"helper-{side}-eye" for v in f}
        pts = [info["P"](i) for i in ids]
        c = sum(pts, Vector()) / len(pts)
        r = max((p - c).length for p in pts) * 0.98
        ey = C.uv_sphere(f"{name}_eye.{side}", r, c, (1, 1, 1), 32, 16)
        C.smooth(ey); C.assign(ey, M["eye"])
        M["_eye_div"].inputs[1].default_value = r * 0.80
        C.parent_to_bone(ey, arm, f"eye.{side.upper()}")
        eyes.append(ey)

    # ---- hair: scalp faces of the head, pushed out + clumped, fringe and cowlick
    hc = arm.data.bones["head"].head_local
    ht = arm.data.bones["head"].tail_local
    hlen = (ht - hc).length
    eye_z = eyes[0].location.z if eyes[0].parent is None else (info["J"]("eye.L____head").z)
    scalp = set()
    for f in body.data.polygons:
        c = f.center
        rel = c - hc
        if rel.z < -0.02:
            continue
        fy = -rel.y                     # forward
        line = eye_z + 0.052 if fy > 0.045 else eye_z + (0.010 if fy > -0.01 else -0.035)
        if c.z > line:
            scalp.add(f.index)
    hair = shell(body, scalp, name + "_hair", 0.010, 0.010, M["hair"], coll)
    tex = bpy.data.textures.new("o_clumps", "VORONOI"); tex.noise_scale = 0.03
    dp = hair.modifiers.new("clump", "DISPLACE"); dp.texture = tex; dp.strength = 0.006
    dp.texture_coords = "OBJECT"; hair.modifiers.move(len(hair.modifiers) - 1, 1)
    top = Vector((hc.x, hc.y, max(v.co.z for v in body.data.vertices)))
    front_y = min(v.co.y for v in body.data.vertices if v.co.z > eye_z + 0.03)
    parts = [hair]
    for i, (x0, sw) in enumerate(((-0.05, 0.035), (-0.018, 0.04), (0.016, 0.042), (0.046, 0.03))):
        pts = [Vector((x0 - 0.01, front_y + 0.06, top.z - 0.012)),
               Vector((x0 + sw * 0.5, front_y + 0.008, top.z - 0.040)),
               Vector((x0 + sw, front_y - 0.004, eye_z + 0.040 + 0.004 * i))]
        cl = C.curve_tube(f"{name}_fringe{i}", pts, radius=0.020, taper=[1.0, 0.8, 0.12], coll=coll)
        cl.data.bevel_resolution = 4; cl.data.use_fill_caps = True
        cl.scale = (1, 1, 1)
        cl.data.materials.append(M["hair"]); parts.append(cl)
    ck = [top + Vector((0, 0.01, 0.004)), top + Vector((0.004, 0.014, 0.034)),
          top + Vector((0.022, 0.022, 0.052)), top + Vector((0.036, 0.012, 0.044)),
          top + Vector((0.030, -0.002, 0.030))]
    cw = C.curve_tube(f"{name}_cowlick", ck, radius=0.0085, taper=[1.0, 0.9, 0.7, 0.45, 0.08], coll=coll)
    cw.data.materials.append(M["hair"]); parts.append(cw)
    for p in parts[1:]:
        C.parent_to_bone(p, arm, "head")

    # ---- brows: thin strips lifted from the skin above each eye
    brows = set()
    for f in body.data.polygons:
        c = f.center
        for e in eyes:
            d = c - e.matrix_world.translation
            if 0.017 < d.z < 0.0225 and abs(d.x) < 0.021 and d.y < 0.0 and c.y < e.matrix_world.translation.y + 0.005:
                brows.add(f.index)
    br = shell(body, brows, name + "_brows", 0.0012, 0.0, M["hair"], coll)

    wing_objs = build_wings(arm, M, coll, name) if wings else []
    return dict(arm=arm, body=body, shirt=shirt, jeans=jeans, shoes=shoe, hair=hair,
                eyes=eyes, wings=wing_objs, M=M, info=info)


def build_wings(arm, M, coll, name):
    """Cardboard wings taped along each arm: two panels per arm, scalloped trailing edge."""
    out = []
    for s in ("L", "R"):
        for bone, depth in ((f"upperarm01.{s}", 0.36), (f"lowerarm01.{s}", 0.32)):
            b = arm.data.bones[bone]
            a = b.head_local.copy()
            end = arm.data.bones[bone.replace("01", "02")].tail_local.copy()
            if bone.startswith("lowerarm"):
                end = arm.data.bones[f"wrist.{s}"].tail_local.copy()
            along = end - a
            down = Vector((0, 0, -1))
            down = (down - along.normalized() * down.dot(along.normalized())).normalized()
            back = along.cross(down).normalized()
            if back.y < 0: back = -back
            n = 8; verts = []
            for i in range(n):
                t = i / (n - 1)
                top = a + along * t + back * 0.03 + down * (-0.01)
                d = depth * (1.0 - 0.3 * t) * (0.85 + 0.15 * math.cos(t * math.pi * 3))
                verts += [top, top + down * d + back * 0.05]
            faces = [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(n - 1)]
            w = C.mesh_obj(f"{name}_wing_{bone}", verts, faces=faces, coll=coll)
            so = w.modifiers.new("sol", "SOLIDIFY"); so.thickness = 0.006
            C.smooth(w); C.assign(w, M["cardboard"])
            C.parent_to_bone(w, arm, bone.replace("01", "02") if bone.startswith("upper") else bone.replace("01", "02"))
            out.append(w)
            for t in (0.3, 0.75):
                c = a + along * t
                bpy.ops.mesh.primitive_torus_add(major_radius=0.042 if "upper" in bone else 0.034,
                                                 minor_radius=0.006, location=c)
                tb = bpy.context.object; tb.name = f"{name}_tape_{bone}_{t}"
                tb.rotation_mode = "QUATERNION"; tb.rotation_quaternion = along.to_track_quat("Z", "Y")
                tb.scale = (1, 1, 2.2)
                C.smooth(tb); C.assign(tb, M["tape"])
                C.parent_to_bone(tb, arm, bone.replace("01", "02"))
                out.append(tb)
    return out
