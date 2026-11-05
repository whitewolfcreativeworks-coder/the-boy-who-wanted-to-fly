"""Quality-gate test: two shots from Scene 2 (golden-hour yard).

  A  tracking shot — Orion runs across the lawn flapping his cardboard wings, leaps, lands, fails
  B  low close shot — he sits in the leaves, catching his breath, looks up at the sunset sky,
     then turns toward the house (Mom calling him in for dinner)

usage: python3 shot_test.py OUTDIR [--shot A|B] [--still FRAME] [--res 1280x720] [--samples N]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector

import anim as A
import common as C
import orion2 as O
import yard as Y


def arg(name, default=None, cast=str):
    if name in sys.argv:
        return cast(sys.argv[sys.argv.index(name) + 1])
    return default


OUT = sys.argv[1]
SHOT = arg("--shot", "A")
STILL = arg("--still", None, int)
RES = arg("--res", "1280x720")
SAMPLES = arg("--samples", 20, int)
os.makedirs(OUT, exist_ok=True)

C.reset()
sc = bpy.context.scene
w, h = (int(x) for x in RES.split("x"))
C.setup_cycles(sc, w, h, samples=SAMPLES)
Y.build_yard(leaf_density=float(arg("--leaves", 150.0)))
sun, sun_dir = Y.golden_hour(sc, sun_elev_deg=8.0, sun_az_deg=72.0)
o = O.build_orion(wings=True)
arm = o["arm"]
rig = A.Rig(arm)

bpy.ops.object.camera_add()
cam = bpy.context.object; sc.camera = cam
cam.data.dof.use_dof = True
cam.data.sensor_width = 36

# a soft bounce from the warm lawn + a cool sky fill so faces never go dead in backlight
bpy.ops.object.light_add(type="AREA")
fill = bpy.context.object; fill.data.energy = 60; fill.data.size = 4; fill.data.color = C.hexc("#ffcf9e")[:3]


def heading(vec):
    """Armature Z rotation so the character (rest-facing -Y) faces `vec` (2D)."""
    return math.atan2(vec[0], -vec[1])


def track_target():
    bpy.context.view_layer.update()
    return arm.matrix_world @ arm.pose.bones["spine05"].head


if SHOT == "A":
    F0, F1 = 1, 108
    sc.frame_start, sc.frame_end = F0, F1
    start, end = Vector((6.5, -2.2, 0)), Vector((-5.5, -0.6, 0))
    dirv = (end - start).normalized()
    arm.rotation_euler = (0, 0, heading(dirv))
    jump0, jump1, stop = 68, 86, 100
    stride_hz, flap_hz = 2.6, 3.2
    for f in range(F0, F1 + 1):
        t = (f - F0) / 24.0
        # travel: running speed, airborne carry, then a skidding stop
        if f <= stop:
            u = min(1.0, (f - F0) / (stop - F0))
            u = u - 0.08 * C.ease((f - jump1) / (stop - jump1)) * (f > jump1)
            pos = start.lerp(end, u)
        z = 0.0
        p = 2 * math.pi * stride_hz * t
        q = 2 * math.pi * flap_hz * t
        rig.reset()
        if f < jump0 - 4:
            A.run_pose(rig, p, q, effort=1.0)
            z = -0.035 * math.cos(2 * p) + 0.005
        elif f < jump0:                                   # crouch to spring
            k = (f - (jump0 - 4)) / 4
            A.run_pose(rig, p, q, effort=0.6)
            for s in "LR":
                rig.pose(f"upperleg01.{s}", swing=(A.FWD, 0.5 * k))
                rig.pose(f"lowerleg01.{s}", bend=(A.BACK, 0.9 * k))
            z = -0.10 * k
        elif f < jump1:                                    # airborne, flapping hard
            k = (f - jump0) / (jump1 - jump0)
            z = 0.55 * 4 * k * (1 - k)
            A.run_pose(rig, 0.0, q * 1.7, effort=1.25, flap_amp=1.0, lean=0.1)
            for s in "LR":
                rig.pose(f"upperleg01.{s}", swing=(A.FWD, 0.55 + 0.25 * math.sin(k * 3)))
                rig.pose(f"lowerleg01.{s}", bend=(A.BACK, 1.1))
            rig.pose("head", up=(A.BACK, 0.35))                # looking up: hope
        else:                                              # land, absorb, sag
            k = C.ease((f - jump1) / 10)
            z = -0.16 * math.sin(min(1, (f - jump1) / 8) * math.pi) * (1 - 0.5 * k)
            for s in "LR":
                rig.pose(f"upperleg01.{s}", swing=(A.FWD, 0.55 * (1 - k) + 0.12))
                rig.pose(f"lowerleg01.{s}", bend=(A.BACK, 1.0 * (1 - k) + 0.18))
                rig.pose(f"upperarm01.{s}", raise_=((A.arm_side(rig, s)[0] * 0.8, 0, 0.6), 0.9 * (1 - k) - 0.25))
                rig.pose(f"lowerarm01.{s}", bend=(A.UP, 0.15))
            rig.pose("spine03", lean=(A.FWD, 0.15 + 0.15 * k))
            rig.pose("head", up=(A.BACK, -0.05 - 0.15 * k))  # head drops: it didn't work
            rig.pose("neck01", up=(A.BACK, -0.1 * k))
        arm.location = (pos.x, pos.y, z)
        arm.keyframe_insert("location", frame=f)
        rig.key(f)
        # camera: low dolly tracking alongside, slight lead, gentle push-in on the landing
        tgt = Vector((pos.x - 0.6, pos.y, 0.85 + 0.6 * max(0.0, z)))
        push = C.ease((f - jump1) / 20) if f > jump1 else 0.0
        cam.location = Vector((pos.x - 3.4 + 1.6 * push, -5.6 + 1.4 * push, 0.66 + 0.12 * push))
        C.look_at(cam, tgt)
        cam.data.lens = 30 + 8 * push
        cam.data.dof.focus_distance = (tgt - cam.location).length
        cam.data.dof.aperture_fstop = 2.2
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_quaternion", frame=f)
        cam.data.keyframe_insert("lens", frame=f); cam.data.dof.keyframe_insert("focus_distance", frame=f)
        fill.location = cam.location + Vector((0.5, 0.6, -0.4)); C.look_at(fill, tgt)
        fill.keyframe_insert("location", frame=f); fill.keyframe_insert("rotation_quaternion", frame=f)
else:
    F0, F1 = 1, 84
    sc.frame_start, sc.frame_end = F0, F1
    spot = Vector((-5.2, -0.4, 0))
    arm.rotation_euler = (0, 0, heading((-0.55, -1.0)))
    for f in range(F0, F1 + 1):
        t = (f - F0) / 24.0
        br = math.sin(2 * math.pi * 0.62 * t)          # still catching his breath
        look = C.ease((f - 10) / 26) - C.ease((f - 56) / 14) * 0.7
        turn = C.ease((f - 58) / 14)                   # toward the house: Mom is calling
        rig.reset()
        A.sit_pose(rig, breathe=br, look_up=look, turn=-0.9 * turn)
        arm.location = (spot.x, spot.y, -0.47 + 0.004 * br)
        arm.keyframe_insert("location", frame=f)
        rig.key(f)
        bpy.context.view_layer.update()
        head = arm.matrix_world @ arm.pose.bones["head"].head
        tgt = head + Vector((0, 0, -0.06))
        drift = t / 3.5
        cam.location = spot + Vector((-0.95 - 0.12 * drift, -1.75 + 0.15 * drift, 0.42))
        C.look_at(cam, tgt)
        cam.data.lens = 50
        cam.data.dof.focus_distance = (tgt - cam.location).length
        cam.data.dof.aperture_fstop = 1.8
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_quaternion", frame=f)
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
        fill.location = cam.location + Vector((0.3, 0.3, 0.2)); C.look_at(fill, head)
        fill.data.energy = 25
        fill.keyframe_insert("location", frame=f); fill.keyframe_insert("rotation_quaternion", frame=f)

Y.add_fog_everywhere()
sc.render.filepath = f"{OUT}/{SHOT}_"
if STILL is not None:
    import time
    sc.frame_set(STILL)
    sc.render.filepath = f"{OUT}/{SHOT}_still_{STILL:04d}.png"
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print("RENDER_SECONDS", round(time.time() - t0, 1))
else:
    bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/shot_{SHOT}.blend")
    import time
    for f in range(sc.frame_start, sc.frame_end + 1):
        fp = f"{OUT}/{SHOT}_{f:04d}.png"
        if os.path.exists(fp):
            continue
        sc.frame_set(f)
        sc.render.filepath = fp
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print("FRAME", f, round(time.time() - t0, 1), flush=True)
