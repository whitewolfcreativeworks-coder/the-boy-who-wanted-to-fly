"""Shared helpers for the Version 2 Blender pipeline (Blender 5.2 as a Python module).

Everything is procedural: no downloaded models or textures, so there are no third-party
asset licenses to clear. Run scripts with `python3 v2/blender/<script>.py`.
"""
import math
import bpy
from mathutils import Vector


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def hexc(h, a=1.0):
    """sRGB hex -> linear RGBA for Blender colour sockets."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, a)


def link(nt, a, b):
    nt.links.new(a, b)


def principled(name, color, rough=0.6, sss=0.0, sheen=0.0, coat=0.0, emit=None, emit_str=0.0,
               spec=0.5, bump=None):
    """A Principled material. `color` may be a hex string or a node socket factory."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    if isinstance(color, str):
        p.inputs["Base Color"].default_value = hexc(color)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = spec
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        p.inputs["Subsurface Scale"].default_value = 0.01
    if sheen:
        p.inputs["Sheen Weight"].default_value = sheen
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    if emit:
        p.inputs["Emission Color"].default_value = hexc(emit)
        p.inputs["Emission Strength"].default_value = emit_str
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = bump[0]
        nz.inputs["Detail"].default_value = 6
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump[1]
        link(nt, tc.outputs["Object"], nz.inputs["Vector"])
        link(nt, nz.outputs["Fac"], bp.inputs["Height"])
        link(nt, bp.outputs["Normal"], p.inputs["Normal"])
    return m


def noise_color(m, c1, c2, scale=8.0, coord="Object", detail=4, lo=0.35, hi=0.65):
    """Drive a Principled material's base colour with a 2-colour noise ramp."""
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = lo
    ramp.color_ramp.elements[1].position = hi
    ramp.color_ramp.elements[0].color = hexc(c1)
    ramp.color_ramp.elements[1].color = hexc(c2)
    link(nt, tc.outputs[coord], nz.inputs["Vector"])
    link(nt, nz.outputs["Fac"], ramp.inputs["Fac"])
    link(nt, ramp.outputs["Color"], p.inputs["Base Color"])
    return m


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def smooth(obj, subsurf=0, render_levels=None):
    for f in obj.data.polygons:
        f.use_smooth = True
    if subsurf:
        md = obj.modifiers.new("subd", "SUBSURF")
        md.levels = subsurf
        md.render_levels = render_levels if render_levels is not None else subsurf
    return obj


def mesh_obj(name, verts, edges=(), faces=(), coll=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], list(edges), list(faces))
    me.update()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def uv_sphere(name, r=1.0, loc=(0, 0, 0), scale=(1, 1, 1), seg=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=rings)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    return ob


def cube(name, size=(1, 1, 1), loc=(0, 0, 0), bevel=0.0, seg=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        md = ob.modifiers.new("bev", "BEVEL")
        md.width = bevel
        md.segments = seg
    return ob


def parent_to_bone(ob, arm, bone):
    """Parent `ob` to `bone` while keeping its current world transform."""
    from mathutils import Matrix
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    ob.parent = arm
    ob.parent_type = "BONE"
    ob.parent_bone = bone
    ob.matrix_parent_inverse = Matrix.Identity(4)
    bpy.context.view_layer.update()
    ob.matrix_world = mw


def curve_tube(name, pts, radius=0.01, taper=None, coll=None, res=8):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    cu.resolution_u = res
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        w = taper[i] if taper else 1.0
        sp.points[i].co = (*p, 1.0)
        sp.points[i].radius = w
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    ob = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def setup_cycles(scene, w=1280, h=720, samples=24, fps=24):
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.03
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 4
    scene.cycles.transparent_max_bounces = 8
    scene.cycles.volume_bounces = 0
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.cycles.blur_glossy = 1.0
    scene.render.use_persistent_data = True
    scene.render.resolution_x = w
    scene.render.resolution_y = h
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"


def look_at(ob, target, roll=0.0):
    d = Vector(target) - ob.location
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("-Z", "Y")
    if roll:
        from mathutils import Quaternion
        ob.rotation_quaternion = ob.rotation_quaternion @ Quaternion((0, 0, 1), roll)


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)
