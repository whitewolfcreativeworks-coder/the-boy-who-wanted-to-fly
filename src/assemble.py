"""Concatenate scene clips, mux the audio mix (loudness-normalised) and
soft subtitles into the final film.

  python3 src/assemble.py            -> build/The_Boy_Who_Wanted_to_Fly.mp4
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from render import BUILD

def run(cmd): print(" ".join(cmd[:6]), "…", flush=True); subprocess.run(cmd, check=True)

def main():
    scenes = [os.path.join(BUILD, "scenes", f"s{i:02d}.mp4") for i in range(19)]
    missing = [s for s in scenes if not os.path.exists(s)]
    if missing: sys.exit(f"missing scene clips: {missing}")
    lst = os.path.join(BUILD, "concat.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in scenes))
    video = os.path.join(BUILD, "video_only.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
    audio = os.path.join(BUILD, "audio", "mix_norm.m4a")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(BUILD, "audio", "mix.wav"),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", audio])
    out = os.path.join(BUILD, "The_Boy_Who_Wanted_to_Fly.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-i", os.path.join(BUILD, "film.srt"),
         "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
         "-metadata", "title=The Boy Who Wanted to Fly", "-metadata", "artist=Story by Jason Whitewolf",
         "-metadata", "copyright=© 2018 Jason Whitewolf. All rights reserved.",
         "-metadata:s:s:0", "language=eng", "-metadata:s:a:0", "language=eng",
         "-movflags", "+faststart", out])
    print(out)

if __name__ == "__main__":
    main()
