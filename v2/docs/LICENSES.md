# Version 2 — dependency & asset license record

Version 1's record (`docs/LICENSES.md`) still applies to everything reused from it (story, narration, fonts). This file covers what Version 2 adds.

**Summary:** no AI image/video models were used in Version 2. Every visual is rendered in Blender from (a) the CC0 MakeHuman base character data and (b) geometry, materials and animation written in this repository's code.

## Story
| Item | Owner | Notes |
|---|---|---|
| *The Boy Who Wanted to Fly* | © 2018 Jason Whitewolf, all rights reserved | Untouched in `manuscript/`. Version 2 adds no story text. |

## Software
| Component | Used for | License | Commercial use |
|---|---|---|---|
| Blender 5.2.3 LTS (`bpy` from PyPI) | Modelling, rigging, animation, Cycles rendering | GPL-3.0-or-later | Yes — renders are the user's output and are not GPL-encumbered (Blender Foundation's own guidance) |
| FFmpeg + libx264 | Encoding | LGPL/GPL | Yes — tool use |

## Character data
| Asset | Source | License |
|---|---|---|
| hm08 base mesh (`3dobjs/base.obj`) incl. eyelash geometry | MakeHuman community, github.com/makehumancommunity/makehuman | **CC0** — header: "explicitly released as CC0 in September 2020" |
| Morph targets: `macrodetails/{caucasian,asian,african}-male-{child,baby}`, `head/head-round`, `eyes/{l,r}-eye-scale-incr` | same | **CC0** (same header in each file) |
| Default skeleton `rigs/default.mhskel`, weights `rigs/default_weights.mhw` | same | **CC0** (`"license": "CC0"` field) |

MakeHuman's *application code* is AGPL-3.0; **none of it is used** — `v2/blender/mhload.py` is an independent reader for the data formats. The data is not redistributed in this repo; `v2/tools/fetch_makehuman_data.sh` fetches it.

## Created by this production
Clothing (shells cut from the body mesh), hair, eyeballs and iris shader, cardboard wings, the house, garage, maples, leaves, street, telephone pole and wires, lighting, camera work and all animation — procedural code in `v2/blender/`.

## Items to review before commercial release
- Everything in Version 1's list (the "Superman" wording in narration, synthetic-voice disclosure, AI-assisted production disclosure).
- If a later pass adds **Wan 2.2** (Apache-2.0) it is commercially usable; **LTX-2.x** uses Lightricks' own open-weights license — read its actual LICENSE for commercial terms before using it.
