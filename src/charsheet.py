"""Render the character reference sheet (assets/character_sheets/)."""
import os, sys, skia
sys.path.insert(0, os.path.dirname(__file__))
from engine import *
from characters import *
s = skia.Surface(W, H); c = s.getCanvas()
c.drawPaint(paint(shader=lin((0, 0), (0, H), ["#fff4e0", "#f6d9b0"])))
text(c, "THE BOY WHO WANTED TO FLY — character reference", W/2, 70, 46, "#5a3020", shadow=False)
g = 900
for x in range(0, W, 60): pass
c.drawLine(0, g, W, g, paint("#c9a070", stroke=3))
draw_person(c, "orion", x=170, y=g, s=1.15, t=0.4, mouth="grin")
draw_person(c, "orion", x=400, y=g, s=1.15, face=-1, t=1.0, eyes="happy", mouth="laugh", armF=(150, 10), armB=(140, 10))
draw_person(c, "orion", x=620, y=g, s=1.15, t=2, wings="card", **flap_pose(0.1))
draw_person(c, "orion", x=860, y=g, s=1.15, t=2, wings="feather", **flap_pose(0.3))
draw_person(c, "orion", x=1080, y=g, s=1.15, t=2, outfit="pajama", mouth="smile")
draw_person(c, "mom", x=1290, y=g, s=1.0, t=0.2, face=-1)
draw_person(c, "dad", x=1470, y=g, s=1.0, t=0.7, face=-1)
draw_person(c, "driver", x=1700, y=g, s=1.0, t=0.9, face=-1)
for i,(x,lab) in enumerate([(170,"Orion"),(400,"joy"),(620,"cardboard wings"),(860,"feather wings"),(1080,"pajamas"),(1290,"Mom"),(1470,"Dad"),(1700,"Driver")]):
    text(c, lab, x, g+60, 30, "#5a3020", shadow=False)
chicken(c, 260, 1040, 0.9, seed=1); chicken(c, 420, 1040, 0.9, face=-1, color="#c8743a", peck=.6)
draw_person(c, "orion", x=1000, y=520, s=.9, t=3, outfit="dream", **fly_pose(3, "superman"))
draw_person(c, "orion", x=600, y=520, s=.9, t=3, outfit="dream", heart=1.0, **fly_pose(3, "chest"))
out = sys.argv[1] if len(sys.argv) > 1 else "assets/character_sheets/characters.png"
s.makeImageSnapshot().save(out, skia.kPNG)
print(out)
