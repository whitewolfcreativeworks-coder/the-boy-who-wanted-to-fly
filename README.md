# The Boy Who Wanted to Fly

*An animated storybook adaptation of the original story by **Jason Whitewolf** (© 2018, all rights reserved).*

Orion wants to fly. Cardboard wings, chicken feathers and a very tall ladder don't do it — but a kind garbage-truck driver tells him he can fly in his dreams, if he practices. Night after night he learns, until he discovers that it's his heart that makes him fly.

## ▶ Watch the film

**`The_Boy_Who_Wanted_to_Fly.mp4`** — attached to the latest [GitHub Release](../../releases) (the file is too large for normal git storage).

- 1920×1080, 24 fps, H.264 video, AAC stereo audio, ~12½ minutes
- All 17 manuscript scenes, opening title, closing credits
- Soft English subtitles included (turn on captions in your player)

## What's in this repository

| Path | Contents |
|---|---|
| `manuscript/` | **The untouched original manuscript** — the canonical source |
| `script/screenplay.py` | The production screenplay: narration, character lines, voice casting |
| `src/engine.py` | Vector rendering engine: camera, parallax, particles, lighting, text |
| `src/characters.py` | The character rig — Orion, Mom, Dad, the driver, chickens |
| `src/environments.py` | Yard, garage, kitchen, stairs, bedroom, coop, dream worlds, dawn street |
| `src/scenes.py`, `src/scenes_dream.py` | The 17 scenes + title + credits, timed to the narration |
| `src/narrate.py` | Narration & voices (Kokoro TTS) |
| `src/audio.py` | Original procedural score, sound effects, mix with voice ducking, subtitles |
| `src/render.py` | Frame renderer → per-scene H.264 clips; stills and contact sheets for review |
| `src/assemble.py` | Final concatenation, loudness normalization, subtitle muxing |
| `assets/character_sheets/` | Character reference sheet |
| `assets/fonts/` | Fredoka & Nunito (SIL OFL) |
| `docs/ADAPTATION_NOTES.md` | Every change made from manuscript to screen |
| `docs/LICENSES.md` | Dependency & asset licenses, plus items to review before commercial release |
| `docs/PRODUCTION_REPORT.md` | What was made, how, what worked, what to improve |

## Reproduce the film

Requires Python 3.11+, FFmpeg, ~2 GB disk. CPU-only; no GPU needed.

```bash
pip install skia-python kokoro-onnx soundfile scipy numpy fonttools
mkdir -p ~/models && cd ~/models
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd -   # back to the repo

python3 src/narrate.py --models ~/models     # 1. voices   (~10 min)
python3 src/render.py --all --jobs 2         # 2. picture  (~40 min on 2 cores)
python3 src/audio.py                         # 3. music, SFX, mix, subtitles (~4 min)
python3 src/assemble.py                      # 4. → build/The_Boy_Who_Wanted_to_Fly.mp4
```

Useful while iterating:

```bash
python3 src/render.py --still 14 36.0        # one frame as PNG
python3 src/render.py --contact 7 --n 12     # contact sheet of a scene
python3 src/render.py --scenes 7 8           # re-render just those scenes
python3 src/narrate.py --models ~/models --only 11   # re-voice one scene
python3 src/charsheet.py                     # character reference sheet
```

Scene timing comes from the recorded narration, so editing a line in `script/screenplay.py` and re-running steps 1–4 keeps picture, sound and subtitles in sync automatically.
