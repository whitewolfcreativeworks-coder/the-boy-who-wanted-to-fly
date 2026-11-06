"""Join title, 17 scenes and credits with the Version 1 soundtrack into the final film.

    python3 v3/assemble.py [--out build/v3/The_Boy_Who_Wanted_to_Fly_V3.mp4]

Video: H.264 1920x1080 24 fps (stream copy of the scene clips). Audio: the music/SFX/narration
mix, loudness-normalised to -16 LUFS, AAC 192 kbps. English subtitles muxed as a soft track.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
B = os.path.join(ROOT, "build")

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(B, "v3", "The_Boy_Who_Wanted_to_Fly_V3.mp4"))
a = ap.parse_args()

clips = [os.path.join(B, "v3", "scenes", f"s{i:02d}.mp4") for i in range(19)]
missing = [c for c in clips if not os.path.exists(c)]
if missing:
    sys.exit("missing scene clips: " + ", ".join(os.path.basename(m) for m in missing))

# check each clip's length against the soundtrack's scene offsets
offs = json.load(open(os.path.join(B, "audio", "offsets.json")))
def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", p]).decode())
total = 0.0
for i, c in enumerate(clips):
    d = dur(c); total += d
    nxt = offs.get(str(i + 1))
    if nxt is not None and abs(total - nxt) > 0.1:
        print(f"warning: drift after scene {i}: video {total:.2f}s vs audio {nxt:.2f}s")

# Join losslessly via MPEG-TS (the mp4 concat demuxer drops frames at clip boundaries).
tsdir = os.path.join(B, "v3", "ts"); os.makedirs(tsdir, exist_ok=True)
ts = []
for c in clips:
    t = os.path.join(tsdir, os.path.basename(c)[:-4] + ".ts")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", c, "-c", "copy", "-bsf:v", "h264_mp4toannexb",
                    "-f", "mpegts", t], check=True)
    ts.append(t)
joined = os.path.join(B, "v3", "joined.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "concat:" + "|".join(ts), "-c", "copy", joined], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined,
                "-i", os.path.join(B, "audio", "mix.wav"), "-i", os.path.join(B, "film.srt"),
                "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                "-metadata", "title=The Boy Who Wanted to Fly",
                "-metadata", "artist=Story by Jason Whitewolf",
                "-movflags", "+faststart", a.out], check=True)
print(f"{a.out}  {dur(a.out) / 60:.2f} min")
