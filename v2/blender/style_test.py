"""Style exploration: re-render one frame of a saved shot in different looks.

    python3 style_test.py SHOT.blend FRAME OUTDIR --style cinema|toon [--res 960x540] [--samples 16]

cinema : art-directed lighting pass — painted gradient sky with a cloud layer,
         lower sky glare, stronger key/rim contrast, punchier grade (Cycles).
toon   : Cycles data passes -> toon_post.py: banded cel shading + ink lines.
The painterly look is a post pass on the cinema frame: see paint_post.py.
"""
import argparse, math, os, sys, time
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

ap = argparse.ArgumentParser()
ap.add_argument("blend"); ap.add_argument("frame", type=int); ap.add_argument("outdir")
ap.add_argument("--style", default="cinema")
ap.add_argument("--res", default="960x540")
ap.add_argument("--samples", type=int, default=16)
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

bpy.ops.wm.open_mainfile(filepath=a.blend)
sc = bpy.context.scene
sc.frame_set(a.frame)
w, h = map(int, a.res.split("x"))
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.render.resolution_percentage = 100


def world_painted_sky(zenith="#5d86c2", mid="#f3c48e", horizon="#ffd9a6", cloud_lit="#ffc79a",
                      cloud_shade="#b08aa0", strength=1.0, cloud_cover=0.52):
    """Gradient sky + a plane-projected procedural cloud layer (cheap, art-directable)."""
    wd = bpy.data.worlds.new("painted_sky"); sc.world = wd
    wd.use_nodes = True
    nt = wd.node_tree; N = nt.nodes.new; L = nt.links.new
    bg = nt.nodes["Background"]; bg.inputs[1].default_value = strength
    tc = N("ShaderNodeTexCoord")
    sep = N("ShaderNodeSeparateXYZ"); L(tc.outputs["Generated"], sep.inputs[0])
    # elevation gradient
    ramp = N("ShaderNodeValToRGB"); L(sep.outputs["Z"], ramp.inputs[0])
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = C.hexc(horizon)
    cr.elements[1].position = 0.55; cr.elements[1].color = C.hexc(zenith)
    e = cr.elements.new(0.12); e.color = C.hexc(mid)
    # cloud layer: project direction onto a plane: uv = xy / (z + 0.12)
    add = N("ShaderNodeMath"); add.operation = "ADD"; add.inputs[1].default_value = 0.12
    L(sep.outputs["Z"], add.inputs[0])
    comb = N("ShaderNodeCombineXYZ")
    dx = N("ShaderNodeMath"); dx.operation = "DIVIDE"; L(sep.outputs["X"], dx.inputs[0]); L(add.outputs[0], dx.inputs[1])
    dy = N("ShaderNodeMath"); dy.operation = "DIVIDE"; L(sep.outputs["Y"], dy.inputs[0]); L(add.outputs[0], dy.inputs[1])
    sx = N("ShaderNodeMath"); sx.operation = "MULTIPLY"; sx.inputs[1].default_value = 0.55
    L(dx.outputs[0], sx.inputs[0]); L(sx.outputs[0], comb.inputs[0]); L(dy.outputs[0], comb.inputs[1])
    nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6
    nz.inputs["Detail"].default_value = 8.0; nz.inputs["Roughness"].default_value = 0.62
    L(comb.outputs[0], nz.inputs["Vector"])
    cov = N("ShaderNodeMapRange"); L(nz.outputs["Fac"], cov.inputs["Value"])
    cov.inputs["From Min"].default_value = cloud_cover; cov.inputs["From Max"].default_value = cloud_cover + 0.16
    # fade clouds near the horizon and below it
    hz = N("ShaderNodeMapRange"); L(sep.outputs["Z"], hz.inputs["Value"])
    hz.inputs["From Min"].default_value = 0.02; hz.inputs["From Max"].default_value = 0.16
    cm = N("ShaderNodeMath"); cm.operation = "MULTIPLY"
    L(cov.outputs[0], cm.inputs[0]); L(hz.outputs[0], cm.inputs[1])
    # cloud colour: lit on edges, shaded in the dense core
    ccol = N("ShaderNodeMix"); ccol.data_type = "RGBA"
    core = N("ShaderNodeMapRange"); L(nz.outputs["Fac"], core.inputs["Value"])
    core.inputs["From Min"].default_value = cloud_cover + 0.1; core.inputs["From Max"].default_value = cloud_cover + 0.35
    L(core.outputs[0], ccol.inputs["Factor"])
    ccol.inputs["A"].default_value = C.hexc(cloud_lit); ccol.inputs["B"].default_value = C.hexc(cloud_shade)
    mix = N("ShaderNodeMix"); mix.data_type = "RGBA"
    L(cm.outputs[0], mix.inputs["Factor"]); L(ramp.outputs["Color"], mix.inputs["A"]); L(ccol.outputs["Result"], mix.inputs["B"])
    L(mix.outputs["Result"], bg.inputs[0])
    return wd


def cinema():
    """Art-directed lighting: controlled sky, warmer low key, cool fill, stronger rim."""
    C.setup_cycles(sc, w, h, samples=a.samples)
    world_painted_sky(strength=0.9)
    sun = bpy.data.objects["sun"]
    sun.data.energy = 7.5; sun.data.color = C.hexc("#ffa95c")[:3]; sun.data.angle = math.radians(2.5)
    # cool sky-fill from the opposite side keeps shadows blue instead of grey
    bpy.ops.object.light_add(type="SUN"); f = bpy.context.object
    f.data.energy = 0.9; f.data.color = C.hexc("#7fa6ff")[:3]; f.data.angle = math.radians(40)
    f.rotation_euler = (math.radians(50), 0, math.radians(-120))
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = -0.35
    # pull the aerial haze warmer and a touch denser
    g = bpy.data.node_groups.get("aerial")
    if g:
        g.nodes["fogcolor"].inputs["Color"].default_value = C.hexc("#f6b27a")


def toon():
    """Cel-shading data pass (Cycles). Writes a multilayer EXR with diffuse light/colour,
    emission, environment, depth, normals and object index; toon_post.py turns it into
    banded cel shading with ink lines. (EEVEE + Freestyle runs out of memory without a GPU.)"""
    cinema()                                   # same sky and key light as the cinema look
    sc.cycles.samples = 8
    vl = bpy.context.view_layer
    for attr in ("use_pass_diffuse_direct", "use_pass_diffuse_indirect", "use_pass_diffuse_color",
                 "use_pass_emit", "use_pass_environment", "use_pass_z", "use_pass_normal",
                 "use_pass_object_index", "use_pass_transmission_direct",
                 "use_pass_transmission_indirect", "use_pass_transmission_color"):
        setattr(vl, attr, True)
    skip = ("lawn", "leaf", "crown", "scatter", "grass")
    i = 1
    for ob in sc.objects:
        if ob.type in {"MESH", "CURVE"} and not any(k in ob.name.lower() for k in skip) \
                and not any(md.type == "NODES" for md in ob.modifiers):
            ob.pass_index = i; i += 1
    sc.render.image_settings.media_type = "MULTI_LAYER_IMAGE"
    sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    sc.render.image_settings.color_depth = "32"


{"cinema": cinema, "toon": toon}[a.style]()
os.makedirs(a.outdir, exist_ok=True)
ext = "exr" if a.style == "toon" else "png"
if ext == "png":
    sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(a.outdir, f"style_{a.style}_{a.frame:04d}.{ext}")
t = time.time()
bpy.ops.render.render(write_still=True)
print(f"STYLE {a.style} frame {a.frame} {time.time() - t:.0f}s -> {sc.render.filepath}", flush=True)
