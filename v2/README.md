# The Boy Who Wanted to Fly — Version 2 (cinematic 3D)

Branch `version-2-cinematic`. Version 1 is untouched on `main` (tag `v1.0-final` → `65a6ba4`); nothing outside `v2/` was changed.

**Status: quality-gate test, not a finished film.** Per the brief, the 3D pipeline was proven on a representative test before scaling. The test is two finished shots from Scene 2. The full film is planned (`docs/PRODUCTION_PLAN.md`) but not rendered — see `docs/TECH_RESEARCH.md` §4 for why that needs a GPU.

## What's here
| Path | Contents |
|---|---|
| `blender/common.py` | Material, mesh, curve and render helpers |
| `blender/mhload.py` | Reader for the CC0 MakeHuman base mesh, targets, skeleton and weights |
| `blender/orion2.py` | **Orion**: CC0 child base + procedural costume (striped shirt, jeans, red sneakers), hair with cowlick, eyes, lashes, brows, cardboard wings |
| `blender/anim.py` | Procedural animation with numerically calibrated bone axes: run/flap cycle, sitting/breathing/looking |
| `blender/yard.py` | Golden-hour front yard: house, garage, maples, leaf carpet, street, telephone pole + wires, sky, aerial perspective |
| `blender/shot_test.py` | The two test shots (camera, DOF, lighting, animation) |
| `blender/lookdev.py` | Character turnaround renders |
| `blender/orion_v0_primitive.py` | First character attempt, discarded (kept as a record) |
| `review/` | Look-dev and test stills from each iteration, and the test film |
| `docs/` | Research & pipeline decision, production plan, licenses, production report |
| `tools/fetch_makehuman_data.sh` | Fetches the CC0 character data |

## Rebuild the test
```bash
pip install bpy==5.2.3            # Blender as a Python module (needs Python 3.13)
eval "$(v2/tools/fetch_makehuman_data.sh ~/mh | tail -1)"
cd v2/blender
python3 shot_test.py OUT --shot A --res 960x540 --samples 12   # 108 frames
python3 shot_test.py OUT --shot B --res 960x540 --samples 12   #  84 frames
python3 shot_test.py OUT --shot A --still 40                   # one frame, timed
python3 lookdev.py OUT_LOOKDEV [--wings]                       # turnaround
```
Renders are resumable (existing frames are skipped). Each shot also saves a `.blend` that opens in desktop Blender 5.2 for inspection or GPU rendering — on any machine with a GPU, set *Render Properties → Device → GPU Compute* and render the same file far faster.
