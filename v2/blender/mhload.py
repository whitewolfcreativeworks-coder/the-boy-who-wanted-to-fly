"""Load the CC0 MakeHuman hm08 base mesh into Blender, morph it with CC0 targets,
and rig it with the CC0 default skeleton + weights. No MakeHuman *code* (AGPL) is used —
only its data files, which were explicitly released as CC0 (Sept 2020).

Data location: env MH_DATA (…/makehuman/data). Fetch with
  git clone --depth 1 --filter=blob:none --sparse https://github.com/makehumancommunity/makehuman.git
  git sparse-checkout set makehuman/data/3dobjs makehuman/data/rigs makehuman/data/targets
"""
import json
import os
from collections import defaultdict

import bpy
from mathutils import Vector

MH = os.environ.get("MH_DATA", "")


def _p(*a):
    return os.path.join(MH, *a)


def read_obj():
    verts, uvs, faces, fuv, groups = [], [], [], [], []
    g = None
    with open(_p("3dobjs", "base.obj")) as f:
        for ln in f:
            if ln.startswith("v "):
                verts.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("vt "):
                uvs.append([float(x) for x in ln.split()[1:3]])
            elif ln.startswith("g "):
                g = ln.split()[1]
            elif ln.startswith("f "):
                idx = [p.split("/") for p in ln.split()[1:]]
                faces.append([int(i[0]) - 1 for i in idx])
                fuv.append([int(i[1]) - 1 if len(i) > 1 and i[1] else 0 for i in idx])
                groups.append(g)
    return verts, uvs, faces, fuv, groups


def read_target(rel):
    d = {}
    with open(_p("targets", rel)) as f:
        for ln in f:
            if ln[:1] in "#\n" or not ln.strip():
                continue
            a = ln.split()
            d[int(a[0])] = (float(a[1]), float(a[2]), float(a[3]))
    return d


def apply_targets(verts, targets):
    out = [list(v) for v in verts]
    for rel, w in targets:
        if not w:
            continue
        for i, (dx, dy, dz) in read_target(rel).items():
            out[i][0] += dx * w; out[i][1] += dy * w; out[i][2] += dz * w
    return out


def to_blender(v, scale):
    # MakeHuman: Y up, +Z forward (decimetres). Blender: Z up, character facing -Y.
    return Vector((v[0] * scale, -v[2] * scale, v[1] * scale))


def build_human(name, targets, height_m, coll, groups_keep=("body",), lash=True):
    verts, uvs, faces, fuv, fgroups = read_obj()
    mverts = apply_targets(verts, targets)
    keep_f = [i for i, g in enumerate(fgroups)
              if g in groups_keep or (lash and g and "eyelashes" in g)]
    used = sorted({v for i in keep_f for v in faces[i]})
    remap = {o: n for n, o in enumerate(used)}
    ys = [mverts[i][1] for i in used]
    scale = height_m / (max(ys) - min(ys))
    floor = min(ys) * scale
    bv = [to_blender(mverts[i], scale) - Vector((0, 0, floor)) for i in used]
    bf = [[remap[v] for v in faces[i]] for i in keep_f]
    me = bpy.data.meshes.new(name)
    me.from_pydata(bv, [], bf)
    uvl = me.uv_layers.new(name="UVMap")
    li = 0
    for fi, i in enumerate(keep_f):
        for k in range(len(faces[i])):
            uvl.data[li].uv = uvs[fuv[i][k]]
            li += 1
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob["lash_faces"] = [fi for fi, i in enumerate(keep_f) if fgroups[i] and "eyelashes" in fgroups[i]]

    # helper: morphed position of ANY original vertex (incl. helpers) for joints/eyes
    def P(i):
        return to_blender(mverts[i], scale) - Vector((0, 0, floor))

    # ---- skeleton
    sk = json.load(open(_p("rigs", "default.mhskel")))
    joints = sk["joints"]

    def J(key):
        vs = joints[key]
        return sum((P(i) for i in vs), Vector()) / len(vs)

    ad = bpy.data.armatures.new(name + "_rig")
    arm = bpy.data.objects.new(name + "_rig", ad)
    coll.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    bones = sk["bones"]
    for bn, b in bones.items():
        eb = ad.edit_bones.new(bn)
        eb.head = J(b["head"]); eb.tail = J(b["tail"])
        if (eb.tail - eb.head).length < 1e-4:
            eb.tail = eb.head + Vector((0, 0, 0.01))
    for bn, b in bones.items():
        if b.get("parent"):
            ad.edit_bones[bn].parent = ad.edit_bones[b["parent"]]
    # consistent rolls: local Z faces forward (-Y) so local X is the lateral hinge axis
    for eb in ad.edit_bones:
        d = (eb.tail - eb.head).normalized()
        ref = Vector((0, -1, 0)) if abs(d.y) < 0.8 else Vector((0, 0, 1))
        eb.align_roll(ref)
    bpy.ops.object.mode_set(mode="OBJECT")

    # ---- weights
    W = json.load(open(_p("rigs", sk.get("weights_file", "default_weights.mhw"))))["weights"]
    for bn, pairs in W.items():
        vg = ob.vertex_groups.new(name=bn)
        for i, w in pairs:
            if i in remap:
                vg.add([remap[i]], w, "REPLACE")
    md = ob.modifiers.new("rig", "ARMATURE")
    md.object = arm
    md.use_deform_preserve_volume = True
    ob.parent = arm
    info = dict(scale=scale, floor=floor, P=P, J=J, remap=remap, used=used)
    return ob, arm, info
