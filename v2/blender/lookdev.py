"""Look-dev turnaround of Orion: front, 3/4, profile, face close-up -> contact sheet."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import common as C
import orion2 as O

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/lookdev"
os.makedirs(OUT, exist_ok=True)
C.reset()
sc = bpy.context.scene
C.setup_cycles(sc, 720, 900, samples=16)
o = O.build_orion(wings="--wings" in sys.argv)

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = C.hexc("#c9b8a3"); bg.inputs[1].default_value = 0.6
bpy.ops.mesh.primitive_plane_add(size=20)
C.assign(bpy.context.object, C.principled("floor", "#b5a28c", rough=0.8))
for name, loc, e, size, col in (("key", (1.6, -2.2, 2.6), 300, 1.2, "#fff1de"),
                                ("fill", (-2.4, -1.5, 1.4), 90, 2.0, "#cfdcff"),
                                ("rim", (-0.8, 2.4, 2.2), 260, 0.8, "#ffd9a8")):
    bpy.ops.object.light_add(type="AREA", location=loc)
    L = bpy.context.object; L.data.energy = e; L.data.size = size; L.data.color = C.hexc(col)[:3]
    C.look_at(L, (0, 0, 0.9))
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam

shots = [("front", (0, -3.6, 0.85), (0, 0, 0.72), 50),
         ("three_q", (2.3, -2.8, 1.0), (0, 0, 0.72), 50),
         ("profile", (3.6, 0, 0.85), (0, 0, 0.72), 50),
         ("face", (0.30, -0.85, 1.18), (0, -0.02, 1.15), 85)]
for name, loc, tgt, lens in shots:
    cam.location = loc; C.look_at(cam, tgt); cam.data.lens = lens
    sc.render.filepath = f"{OUT}/{name}.png"
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/orion_lookdev.blend")
print("done")
