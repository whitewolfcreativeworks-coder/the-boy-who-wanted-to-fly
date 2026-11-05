# Dependency & asset license record

Summary: **every asset in the film was either created by this production from code, or comes from a source that permits commercial use.** No downloaded images, music, sound effects, or third-party characters are used.

## Story
| Item | Owner | Notes |
|---|---|---|
| *The Boy Who Wanted to Fly* manuscript | © 2018 Jason Whitewolf, all rights reserved | Kept untouched in `manuscript/`. Credited on the title card and in the credits. |

## Generated in this production (owned by the production / author)
| Asset | How it was made |
|---|---|
| All character designs, environments, animation | Hand-written vector drawing code in `src/` (no image models, no reference artwork) |
| Music score | Synthesized note-by-note in `src/audio.py` from original melodies (no samples, no loops) |
| Sound effects | Synthesized from noise/oscillators in `src/audio.py` |
| Narration & character voices | Synthesized with Kokoro TTS (below) from the screenplay |

## Software and model weights
| Component | Used for | License | Commercial use |
|---|---|---|---|
| Kokoro-82M weights + voice packs (hexgrad) | Narration and character voices | Apache-2.0 | Yes |
| kokoro-onnx (thewh1teagle) | Runs Kokoro on CPU | MIT | Yes |
| espeak-ng (via kokoro-onnx phonemizer) | Text → phonemes at synthesis time | GPL-3.0 | Yes — it is a tool; GPL does not attach to the audio it helps produce |
| onnxruntime | Model inference | MIT | Yes |
| skia-python / Skia | 2D vector rendering | BSD-3-Clause | Yes |
| NumPy, SciPy | Audio synthesis & DSP | BSD-3-Clause | Yes |
| python-soundfile / libsndfile | WAV I/O | BSD-3 / LGPL-2.1 | Yes |
| fontTools | Baking static font weights | MIT | Yes |
| FFmpeg + libx264 | Encoding and muxing | LGPL/GPL (this build includes GPL x264) | Yes — tool use; output video is not encumbered |

## Fonts
| Font | Use | License |
|---|---|---|
| Fredoka (variable, static instances baked) | Titles, credits | SIL Open Font License 1.1 (`assets/fonts/Fredoka-OFL.txt`) |
| Nunito | Credits | SIL Open Font License 1.1 (`assets/fonts/Nunito-OFL.txt`) |

## Items to review before commercial release
1. **"Superman" in the narration (scenes 11, 13, 14).** The manuscript names Superman and his "S" emblem. The *visuals* use an original design only (plain red cape, star-print pajamas, an invented caped-kid poster — no shield or logo). The *spoken words* keep the author's text. Naming a trademarked character in a story is common and often fine, but because this is a DC Comics trademark, have it checked before monetizing — or swap to a generic phrase ("a superhero", "the letter on a hero's chest"). This is a one-line change per beat in `script/screenplay.py`; re-run `src/narrate.py --only 11 13 14`.
2. **Synthetic voices.** Kokoro voice packs are Apache-2.0, but some platforms require disclosure of AI-generated voices. The credits already state "Narration & voices: Kokoro TTS".
3. **AI-assisted production disclosure.** The credits note the adaptation was produced with Claude (Anthropic). Check any distribution platform's AI-content labeling rules.
