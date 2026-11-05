"""Orion's front yard, late autumn, golden hour (scenes 2, 6, 7, 8).

Layout (metres): Orion's lawn is around the origin. House + garage stand behind (+Y),
the street and the telephone pole run along the front (-Y side, y≈-9), maples flank the lawn.
"""
import math
import random

import bpy
from mathutils import Vector

import common as C

LEAF_COLS = ["#b8241a", "#d4421c", "#e86a1f", "#f2a02a", "#e9c046", "#9b5a2a", "#c4572a", "#7a3d1e"]


# ------------------------------------------------------------ atmosphere (cheap aerial perspective)
def fog_group():
    if "aerial" in bpy.data.node_groups:
        return bpy.data.node_groups["aerial"]
    g = bpy.data.node_groups.new("aerial", "ShaderNodeTree")
    g.interface.new_socket("Shader", in_out="INPUT", socket_type="NodeSocketShader")
    g.interface.new_socket("Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
    gi = g.nodes.new("NodeGroupInput"); go = g.nodes.new("NodeGroupOutput")
    cam = g.nodes.new("ShaderNodeCameraData")
    # fog = 1 - exp(-max(d - start, 0) / k)
    sub = g.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = 6.0
    mx = g.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; mx.inputs[1].default_value = 0.0
    dv = g.nodes.new("ShaderNodeMath"); dv.operation = "DIVIDE"; dv.inputs[1].default_value = -55.0
    ex = g.nodes.new("ShaderNodeMath"); ex.operation = "EXPONENT"
    inv = g.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    cl = g.nodes.new("ShaderNodeMath"); cl.operation = "MULTIPLY"; cl.inputs[1].default_value = 0.85
    em = g.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = C.hexc("#f2b779")
    em.inputs["Strength"].default_value = 1.0
    em.name = "fogcolor"
    mix = g.nodes.new("ShaderNodeMixShader")
    L = g.links.new
    L(cam.outputs["View Distance"], sub.inputs[0]); L(sub.outputs[0], mx.inputs[0])
    L(mx.outputs[0], dv.inputs[0]); L(dv.outputs[0], ex.inputs[0]); L(ex.outputs[0], inv.inputs[1])
    L(inv.outputs[0], cl.inputs[0]); L(cl.outputs[0], mix.inputs[0])
    L(gi.outputs[0], mix.inputs[1]); L(em.outputs[0], mix.inputs[2]); L(mix.outputs[0], go.inputs[0])
    return g


def add_fog_everywhere(skip=("o_eye",)):
    g = fog_group()
    for m in bpy.data.materials:
        if not m.use_nodes or m.name in skip or m.get("fogged"):
            continue
        nt = m.node_tree
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if not out or not out.inputs["Surface"].links:
            continue
        src = out.inputs["Surface"].links[0].from_socket
        gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = g
        nt.links.new(src, gn.inputs[0]); nt.links.new(gn.outputs[0], out.inputs["Surface"])
        m["fogged"] = True


# ------------------------------------------------------------ leaves
def leaf_mesh(name, coll, curl=0.25, lobes=5, size=0.07):
    pts = []
    n = 40
    for i in range(n):
        a = math.pi / 2 + 2 * math.pi * i / n
        lobe = 0.55 + 0.45 * abs(math.cos(lobes / 2 * (a - math.pi / 2)))
        r = size * lobe * (0.75 if math.sin(a) < -0.6 else 1.0)
        pts.append((math.cos(a) * r, math.sin(a) * r * 0.95))
    verts = [(0, 0, 0)] + [(x, y, curl * (x * x) / size) for x, y in pts]
    faces = [(0, i + 1, (i + 1) % n + 1) for i in range(n)]
    ob = C.mesh_obj(name, verts, faces=faces, coll=coll)
    C.smooth(ob)
    return ob


def leaf_material():
    m = C.principled("leaf", "#e86a1f", rough=0.55, sss=0.0, spec=0.35)
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    rp = nt.nodes.new("ShaderNodeValToRGB"); cr = rp.color_ramp; cr.interpolation = "CONSTANT"
    cr.elements[0].color = C.hexc(LEAF_COLS[0]); cr.elements[1].position = 0.999
    cr.elements[1].color = C.hexc(LEAF_COLS[-1])
    for i, c in enumerate(LEAF_COLS[1:-1]):
        e = cr.elements.new((i + 1) / (len(LEAF_COLS) - 1)); e.color = C.hexc(c)
    C.link(nt, oi.outputs["Random"], rp.inputs["Fac"])
    # vein darkening toward the stem, a touch of translucency for backlight
    tc = nt.nodes.new("ShaderNodeTexCoord"); grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = "SPHERICAL"
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (9, 9, 9)
    C.link(nt, tc.outputs["Object"], mp.inputs[0]); C.link(nt, mp.outputs[0], grad.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.35
    inv = nt.nodes.new("ShaderNodeInvert"); C.link(nt, grad.outputs["Fac"], inv.inputs["Color"])
    C.link(nt, rp.outputs["Color"], mix.inputs["A"]); C.link(nt, inv.outputs["Color"], mix.inputs["B"])
    C.link(nt, mix.outputs["Result"], p.inputs["Base Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent"); C.link(nt, mix.outputs["Result"], tr.inputs["Color"])
    ms = nt.nodes.new("ShaderNodeMixShader"); ms.inputs[0].default_value = 0.3
    out = nt.nodes["Material Output"]
    C.link(nt, p.outputs[0], ms.inputs[1]); C.link(nt, tr.outputs[0], ms.inputs[2])
    C.link(nt, ms.outputs[0], out.inputs["Surface"])
    return m


def scatter(target, inst_coll, density, scale=(0.7, 1.3), tilt=0.35, seed=0, name="scatter",
            mask_attr=None, max_count=None):
    """Geometry-nodes scatter of a collection's objects over `target`'s surface."""
    g = bpy.data.node_groups.new(name, "GeometryNodeTree")
    g.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    g.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = g.nodes.new; L = g.links.new
    gi = N("NodeGroupInput"); go = N("NodeGroupOutput")
    dist = N("GeometryNodeDistributePointsOnFaces")
    dist.inputs["Density"].default_value = density
    dist.inputs["Seed"].default_value = seed
    if mask_attr:
        na = N("GeometryNodeInputNamedAttribute"); na.data_type = "FLOAT"
        na.inputs["Name"].default_value = mask_attr
        dfac = next(i for i in dist.inputs if i.identifier == "Density Factor")
        L(na.outputs["Attribute"], dfac)
    ci = N("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = inst_coll
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    iop = N("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    rr = N("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"
    rr.inputs["Min"].default_value = (-tilt, -tilt, 0); rr.inputs["Max"].default_value = (tilt, tilt, 6.283)
    rr.inputs["Seed"].default_value = seed + 1
    rs = N("FunctionNodeRandomValue"); rs.data_type = "FLOAT"
    rs.inputs["Min"].default_value = scale[0]; rs.inputs["Max"].default_value = scale[1]
    rs.inputs["Seed"].default_value = seed + 2
    ri = N("FunctionNodeRandomValue"); ri.data_type = "INT"
    ri.inputs["Min"].default_value = 0; ri.inputs["Max"].default_value = 64
    ri.inputs["Seed"].default_value = seed + 3
    jn = N("GeometryNodeJoinGeometry")
    L(gi.outputs[0], dist.inputs["Mesh"]); L(dist.outputs["Points"], iop.inputs["Points"])
    L(ci.outputs[0], iop.inputs["Instance"]); L(rr.outputs["Value"], iop.inputs["Rotation"])
    L(rs.outputs["Value"], iop.inputs["Scale"]); L(ri.outputs["Value"], iop.inputs["Instance Index"])
    L(iop.outputs[0], jn.inputs[0]); L(gi.outputs[0], jn.inputs[0])
    L(jn.outputs[0], go.inputs[0])
    md = target.modifiers.new(name, "NODES"); md.node_group = g
    return md


# ------------------------------------------------------------ build
def build_yard(coll=None, seed=7, leaf_density=420.0):
    random.seed(seed)
    coll = coll or bpy.context.scene.collection
    lib = bpy.data.collections.new("leaf_lib")
    bpy.context.scene.collection.children.link(lib)
    lib.hide_render = True
    lm = leaf_material()
    for i in range(6):
        lf = leaf_mesh(f"leaf{i}", lib, curl=0.15 + 0.12 * i, lobes=5 if i % 3 else 3, size=0.06 + 0.008 * i)
        C.assign(lf, lm)
        lf.location = (i * 0.3, 50, 0)
    # ----- lawn
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=160, y_subdivisions=160, size=70, location=(0, 0, 0))
    ground = bpy.context.object; ground.name = "lawn"
    for v in ground.data.vertices:
        x, y = v.co.x, v.co.y
        v.co.z = 0.05 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.025 * math.sin(x * 0.9 + y * 0.6)
        if y < -7.3:                          # flatten into the street level
            v.co.z = -0.12
    C.smooth(ground)
    grass = C.principled("grass", "#6f7a2e", rough=0.95, bump=(300.0, 0.6), spec=0.15)
    C.noise_color(grass, "#55642a", "#a39a44", scale=0.6, lo=0.3, hi=0.75)
    C.assign(ground, grass)
    # leaf-carpet density mask: dense on the lawn, thinning toward the street
    at = ground.data.attributes.new("leafmask", "FLOAT", "POINT")
    for i, v in enumerate(ground.data.vertices):
        x, y = v.co.x, v.co.y
        m = 1.0 if -7.0 < y < 7 else 0.0
        m *= max(0.0, 0.25 + 0.75 * math.sin(x * 0.55 + 2.0) * math.cos(y * 0.45 + 0.3))
        m *= max(0.0, 1.0 - math.hypot(x, y * 1.3) / 14.0) ** 0.5
        if abs(x) > 16: m = 0.0
        at.data[i].value = max(0.0, m)
    scatter(ground, lib, leaf_density, scale=(0.42, 0.78), tilt=0.4, seed=seed, name="leafcarpet",
            mask_attr="leafmask")

    # ----- street, curb, sidewalk
    road = C.cube("street", (90, 7.0, 0.2), (0, -11.5, -0.22))
    asph = C.principled("asphalt", "#3b3a3d", rough=0.85, bump=(80.0, 0.3))
    C.noise_color(asph, "#2f2e31", "#4a4848", scale=3, lo=0.3, hi=0.7); C.assign(road, asph)
    side = C.cube("sidewalk", (90, 1.6, 0.18), (0, -7.6, -0.08), bevel=0.02, seg=2)
    conc = C.principled("concrete", "#b8b0a2", rough=0.8, bump=(30.0, 0.15)); C.assign(side, conc)
    curb = C.cube("curb", (90, 0.25, 0.25), (0, -8.45, -0.12), bevel=0.03, seg=2); C.assign(curb, conc)
    for i in range(-20, 21):
        j = C.cube(f"joint{i}", (0.03, 1.62, 0.005), (i * 2.0, -7.6, 0.012))
        C.assign(j, C.principled("jointmat", "#8d867a", rough=0.9)) if i == -20 else C.assign(j, bpy.data.materials["jointmat"])

    # ----- house + attached garage (behind the lawn)
    siding = C.principled("siding", "#d9cdb4", rough=0.75, bump=(4.0, 0.05))
    nt = siding.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"; wv.bands_direction = "Z"; wv.inputs["Scale"].default_value = 3.2
    wv.wave_profile = "SAW"
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.4
    C.link(nt, tc.outputs["Object"], wv.inputs["Vector"]); C.link(nt, wv.outputs["Fac"], bp.inputs["Height"])
    C.link(nt, bp.outputs["Normal"], p.inputs["Normal"])
    trim = C.principled("trim", "#f4efe6", rough=0.5)
    roofm = C.principled("roof", "#5a4340", rough=0.85, bump=(14.0, 0.5))
    C.noise_color(roofm, "#4a3533", "#6e5450", scale=6, lo=0.35, hi=0.7)
    glass = C.principled("window", "#2a2f3a", rough=0.08, emit="#ffb866", emit_str=1.4, spec=0.9)
    hx, hy = -2.5, 12.0
    house = C.cube("house", (11, 8, 5.6), (hx, hy, 2.8)); C.assign(house, siding)
    # gable roof prism
    rv = [(-6, -4.6, 5.6), (6, -4.6, 5.6), (6, 4.6, 5.6), (-6, 4.6, 5.6), (-6, 0, 8.6), (6, 0, 8.6)]
    rv = [(x + hx, y + hy, z) for x, y, z in rv]
    roof = C.mesh_obj("roof", rv, faces=[(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)], coll=coll)
    sol = roof.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.25; C.assign(roof, roofm)
    gx = hx + 9.0
    garage = C.cube("garage", (6.5, 7.5, 3.6), (gx, hy + 0.2, 1.8)); C.assign(garage, siding)
    groof = C.cube("garage_roof", (7.2, 8.2, 0.3), (gx, hy + 0.2, 3.7), bevel=0.05); C.assign(groof, roofm)
    gdoor = C.cube("garage_door", (5.0, 0.12, 2.9), (gx, hy - 3.55, 1.45)); C.assign(gdoor, trim)
    for k in range(5):
        pn = C.cube(f"gd_panel{k}", (4.9, 0.05, 0.03), (gx, hy - 3.63, 0.4 + k * 0.58)); C.assign(pn, siding)
    # windows (warm interior glow — dinner is nearly ready)
    for wx, wz in ((-6.0, 1.7), (-3.4, 1.7), (1.0, 1.7), (-6.0, 4.3), (-2.5, 4.3), (1.0, 4.3)):
        fr = C.cube("wframe", (1.5, 0.16, 1.5), (hx + wx + 2.5, hy - 4.04, wz)); C.assign(fr, trim)
        gl = C.cube("wglass", (1.25, 0.1, 1.25), (hx + wx + 2.5, hy - 4.1, wz)); C.assign(gl, glass)
        mu = C.cube("mullion", (0.06, 0.12, 1.25), (hx + wx + 2.5, hy - 4.14, wz)); C.assign(mu, trim)
    door = C.cube("door", (1.1, 0.14, 2.2), (hx - 1.2, hy - 4.05, 1.1))
    C.assign(door, C.principled("door", "#7b2e25", rough=0.45, coat=0.3))
    for k in range(3):
        st = C.cube(f"step{k}", (2.2, 0.45, 0.18), (hx - 1.2, hy - 4.3 - k * 0.42, 0.09 + (2 - k) * 0.18), bevel=0.02)
        C.assign(st, conc)
    walk = C.cube("walk", (1.3, 7.5, 0.06), (hx - 1.2, hy - 9.0, 0.02)); C.assign(walk, conc)
    drive = C.cube("driveway", (5.2, 12.5, 0.06), (gx, hy - 10.0, 0.0)); C.assign(drive, conc)

    # ----- maples: curve-tube branches + leaf-instanced crowns
    bark = C.principled("bark", "#4d3a2e", rough=0.95, bump=(18.0, 1.0))
    C.noise_color(bark, "#3a2b22", "#6a5444", scale=25, lo=0.35, hi=0.7)
    crown_mat = C.principled("crownhide", "#000000")
    for ti, (tx, ty, s) in enumerate(((-9.0, 3.5, 1.15), (8.5, 2.0, 1.0), (-15.0, 14.0, 1.3), (17.0, 13.0, 1.1))):
        base = Vector((tx, ty, -0.05))
        trunk = C.curve_tube(f"trunk{ti}", [base, base + Vector((0.2, 0.1, 2.5 * s)), base + Vector((0.1, -0.2, 4.8 * s))],
                             radius=0.28 * s, taper=[1.25, 0.8, 0.45], coll=coll)
        trunk.data.materials.append(bark)
        tops = []
        for b in range(7):
            a = b / 7 * 6.283 + ti
            h0 = (2.6 + 0.35 * b % 3) * s
            st = base + Vector((0.15, 0, h0))
            tip = st + Vector((math.cos(a) * 2.4 * s, math.sin(a) * 2.0 * s, (1.6 + 0.4 * (b % 2)) * s))
            mid = st.lerp(tip, 0.5) + Vector((0, 0, 0.5 * s))
            br = C.curve_tube(f"branch{ti}_{b}", [st, mid, tip], radius=0.11 * s, taper=[1.0, 0.6, 0.15], coll=coll)
            br.data.materials.append(bark); tops.append(tip)
        # crown shells (hidden at render through the leaves' join; the shell itself is dark interior)
        for k, tp in enumerate(tops + [base + Vector((0, 0, 5.6 * s))]):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=(1.5 + 0.3 * (k % 3)) * s, location=tp)
            cr = bpy.context.object; cr.name = f"crown{ti}_{k}"
            for v in cr.data.vertices:
                v.co *= 1.0 + 0.18 * math.sin(v.co.x * 3 + k) * math.cos(v.co.z * 2.5)
                v.co.z *= 0.8
            C.assign(cr, crown_mat)
            cr.visible_camera = True
            md = scatter(cr, lib, 45.0 if ti < 2 else 18.0, scale=(1.2, 1.8), tilt=3.1, seed=ti * 11 + k,
                         name=f"crownleaves{ti}_{k}")
    crown_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = C.hexc("#3b1a0c")

    # ----- telephone pole + wires along the street (they matter at the very end of the film)
    wood = C.principled("polewood", "#5b4636", rough=0.9, bump=(20.0, 0.6))
    wire_m = C.principled("wire", "#141414", rough=0.4)
    poles = [(-14.0, -8.9), (16.0, -8.9)]
    for pi, (px, py) in enumerate(poles):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=10.5, location=(px, py, 5.0), vertices=16)
        pl = bpy.context.object; pl.name = f"pole{pi}"; C.smooth(pl); C.assign(pl, wood)
        arm_ = C.cube(f"crossarm{pi}", (0.14, 2.4, 0.14), (px, py, 9.4)); C.assign(arm_, wood)
    for wi, off in enumerate((-1.0, -0.35, 0.35, 1.0)):
        pts = []
        for k in range(13):
            t = k / 12
            x = poles[0][0] + (poles[1][0] - poles[0][0]) * t
            sag = 0.9 * 4 * t * (1 - t)
            pts.append(Vector((x, poles[0][1] + off, 9.5 - sag)))
        w = C.curve_tube(f"wire{wi}", pts, radius=0.012, coll=coll); w.data.materials.append(wire_m)

    # ----- neighbour houses across the street (silhouettes in haze)
    for k in range(5):
        nx = -30 + k * 15
        nh = C.cube(f"nbr{k}", (9, 7, 5), (nx, -22.0, 2.5)); C.assign(nh, siding)
        nr = C.cube(f"nbrroof{k}", (9.8, 7.6, 0.4), (nx, -22.0, 5.2)); C.assign(nr, roofm)
    # pumpkins on the porch steps (manuscript: "ripe apples and pumpkins")
    pk = C.principled("pumpkin", "#e0731d", rough=0.5, bump=(10.0, 0.2))
    for k, (px, py, pz, r) in enumerate(((hx - 2.6, hy - 4.6, 0.55, 0.26), (hx + 0.2, hy - 4.2, 0.55, 0.2), (hx - 2.2, hy - 5.2, 0.2, 0.32))):
        p_ = C.uv_sphere(f"pumpkin{k}", r, (px, py, pz + r * 0.8), (1, 1, 0.78), 24, 12)
        for v in p_.data.vertices:
            a = math.atan2(v.co.y, v.co.x)
            v.co *= 1.0 + 0.06 * math.cos(a * 8)
        C.smooth(p_, 1); C.assign(p_, pk)
    return dict(ground=ground, lib=lib, leafmat=lm)


def golden_hour(scene, sun_elev_deg=5.0, sun_az_deg=-160.0, strength=0.9):
    w = bpy.data.worlds.new("sky"); scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(sun_elev_deg)
    sky.sun_rotation = math.radians(sun_az_deg)
    try:
        sky.air_density = 1.6; sky.aerosol_density = 3.0
    except Exception:
        pass
    C.link(nt, sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = strength
    scene.view_settings.exposure = -0.9
    # warm key sun aligned with the sky's sun
    bpy.ops.object.light_add(type="SUN")
    sun = bpy.context.object; sun.name = "sun"
    sun.data.energy = 6.5; sun.data.angle = math.radians(1.5)
    sun.data.color = C.hexc("#ffb36b")[:3]
    el, az = math.radians(sun_elev_deg), math.radians(sun_az_deg)
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun.rotation_mode = "QUATERNION"; sun.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
    return sun, d
