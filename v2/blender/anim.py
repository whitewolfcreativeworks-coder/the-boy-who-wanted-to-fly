"""Procedural character animation on the MakeHuman rig.

Bone rotation axes are *calibrated* numerically (which axis/sign moves a bone's tail toward a
desired direction in rest space), so poses are written in intent terms: swing-forward, bend,
raise — not guessed Euler signs.
"""
import math

import bpy
from mathutils import Euler, Vector


class Rig:
    def __init__(self, arm):
        self.arm = arm
        self.cal = {}
        for pb in arm.pose.bones:
            pb.rotation_mode = "XYZ"

    def _tail(self, bone):
        bpy.context.view_layer.update()
        pb = self.arm.pose.bones[bone]
        return (pb.tail - pb.head)

    def calibrate(self, bone, want):
        """Return (axis, sign) whose +0.3 rad rotation best moves the tail along `want`."""
        key = (bone, tuple(want))
        if key in self.cal:
            return self.cal[key]
        saved = {p.name: tuple(p.rotation_euler) for p in self.arm.pose.bones}
        for p in self.arm.pose.bones:
            p.rotation_euler = (0, 0, 0)
        pb = self.arm.pose.bones[bone]
        twist = key in getattr(self, "_twist", set())
        def probe():
            bpy.context.view_layer.update()
            if twist:      # bone's local Z axis (aligned forward at rig build) in armature space
                return Vector(pb.matrix.col[2][:3]).normalized()
            return (pb.tail - pb.head).normalized()
        base = probe()
        best = None
        for ax in ((1,) if twist else range(3)):
            for sg in (1, -1):
                e = Euler((0, 0, 0)); e[ax] = 0.3 * sg
                pb.rotation_euler = e
                d = probe() - base
                score = d.dot(Vector(want).normalized())
                if best is None or score > best[0]:
                    best = (score, ax, sg)
        for p in self.arm.pose.bones:
            p.rotation_euler = saved[p.name]
        self.cal[key] = (best[1], best[2])
        return self.cal[key]

    def pose(self, bone, **intents):
        """intents: name=(want_vector, radians). Sums calibrated rotations."""
        pb = self.arm.pose.bones[bone]
        e = [0.0, 0.0, 0.0]
        for name, (want, ang) in intents.items():
            if name == "turn":
                self._twist = getattr(self, "_twist", set()) | {(bone, tuple(want))}
            ax, sg = self.calibrate(bone, want)
            e[ax] += sg * ang
        pb.rotation_euler = e

    def key(self, frame, bones=None):
        for pb in self.arm.pose.bones:
            if bones is None or pb.name in bones:
                pb.keyframe_insert("rotation_euler", frame=frame)

    def reset(self):
        for pb in self.arm.pose.bones:
            pb.rotation_euler = (0, 0, 0)
            pb.location = (0, 0, 0)


FWD = (0, -1, 0)
BACK = (0, 1, 0)
UP = (0, 0, 1)
DOWN = (0, 0, -1)


def side(s):
    return (1, 0, 0) if s == "L" else (-1, 0, 0)


def arm_side(rig, s):
    """Which world X sign the character's arm .s is on in rest pose."""
    b = rig.arm.data.bones[f"upperarm01.{s}"]
    return (1 if b.tail_local.x > 0 else -1, 0, 0)


# --------------------------------------------------------------- poses
def run_pose(rig, p, flap_q, effort=1.0, flap_amp=0.8, lean=0.22):
    """Run cycle at stride phase p (radians) with arms flapping at phase flap_q."""
    for s, ph in (("L", p), ("R", p + math.pi)):
        th = 0.72 * math.sin(ph)
        knee = 0.15 + 1.25 * max(0.0, math.cos(ph)) ** 2 + 0.25 * max(0.0, -math.sin(ph))
        rig.pose(f"upperleg01.{s}", swing=(FWD, th))
        rig.pose(f"lowerleg01.{s}", bend=(BACK, knee))
        rig.pose(f"foot.{s}", flex=(UP, 0.25 * math.sin(ph) - 0.1))
    tw = 0.10 * math.sin(p)
    rig.pose("spine05", lean=(FWD, lean * 0.4))
    rig.pose("spine03", lean=(FWD, lean * 0.35))
    rig.pose("spine01", lean=(FWD, lean * 0.25))
    rig.pose("neck01", up=(BACK, lean * 0.55))
    rig.pose("head", up=(BACK, 0.12 + 0.03 * math.sin(2 * p)))
    for s in ("L", "R"):
        out = arm_side(rig, s)
        a = flap_amp * math.sin(flap_q) * effort
        abd = (out[0] * 0.8, 0, 0.6)
        rig.pose(f"upperarm01.{s}", raise_=(abd, 0.55 + a), back=(BACK, 0.18))
        rig.pose(f"lowerarm01.{s}", bend=(UP, 0.12 - 0.22 * math.sin(flap_q - 0.9)))
        rig.pose(f"wrist.{s}", lag=(UP, -0.35 * math.sin(flap_q - 1.4)))
        rig.pose(f"shoulder01.{s}", shrug=(UP, 0.12 * math.sin(flap_q)))


def sit_pose(rig, breathe=0.0, look_up=0.0, turn=0.0):
    for s in ("L", "R"):
        rig.pose(f"upperleg01.{s}", swing=(FWD, 1.30), splay=(side(s), 0.18))
        rig.pose(f"lowerleg01.{s}", bend=(BACK, 1.55))
        rig.pose(f"foot.{s}", flex=(UP, 0.35))
        rig.pose(f"upperarm01.{s}", back=(BACK, 0.75), raise_=((arm_side(rig, s)[0] * 0.8, 0, 0.6), -0.1))
        rig.pose(f"lowerarm01.{s}", bend=(FWD, 0.15))
        rig.pose(f"wrist.{s}", flat=(UP, 0.9))
    rig.pose("spine01", lean=(BACK, 0.38))
    rig.pose("spine03", lean=(FWD, 0.10 + 0.03 * breathe))
    rig.pose("spine05", lean=(FWD, 0.10 - 0.02 * breathe))
    rig.pose("neck01", up=(BACK, 0.02 + 0.10 * look_up), turn=(side("L"), turn * 0.5))
    rig.pose("head", up=(BACK, 0.02 + 0.16 * look_up), turn=(side("L"), turn * 0.6))
