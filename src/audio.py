"""Original procedural score + synthesized SFX + narration mix + subtitles.

Everything here is generated from code (no samples), so the soundtrack is
fully owned by the production.  Output: build/audio/{music,sfx,narration,mix}.wav
and build/film.srt.

  python3 src/audio.py
"""
import json, math, os, sys
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
sys.path.insert(0, os.path.dirname(__file__))
from render import Ctx, load_manifest, BUILD

SR = 44100
rng = np.random.default_rng(7)

# ================================================================== helpers
def note_hz(midi): return 440.0 * 2 ** ((midi - 69) / 12)
MAJOR = [0, 2, 4, 5, 7, 9, 11]
def deg(root, d, scale=MAJOR):
    o, i = divmod(d, len(scale)); return root + 12 * o + scale[i]

def env(n, a=.005, r=.3, decay=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    if decay: e = e * np.exp(-t / decay)
    rel = int(r * SR)
    if rel and n > rel: e[-rel:] *= np.linspace(1, 0, rel)
    return e

def tone(f, dur, partials=((1, 1.0),), decay=None, a=.005, r=.2, vib=0.0):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    if vib: ph = ph + vib * np.sin(2 * np.pi * 5.2 * t) * 2 * np.pi * f / 5.2 * .002
    s = sum(w * np.sin(k * ph) for k, w in partials)
    return s * env(n, a, r, decay)

def bell(f, dur, amp=.2):
    n = int(dur * SR); t = np.arange(n) / SR
    idx = 2.2 * np.exp(-t / .5)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t))
    return amp * s * env(n, .002, .3, 1.4)

def musicbox(f, dur, amp=.18):
    return amp * tone(f, dur, ((1, 1), (2, .35), (5.04, .12), (3, .1)), decay=.9, a=.002, r=.25)

def marimba(f, dur, amp=.25):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / .45) + .35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / .06)
    return amp * s * env(n, .002, .05)

def pluck(f, dur, amp=.2):
    return amp * tone(f, dur, ((1, 1), (2, .5), (3, .25), (4, .12)), decay=.35, a=.003, r=.1)

def pad(freqs, dur, amp=.08, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-.25, 0, .25):
            ff = f * 2 ** (det / 100 * 8)
            s += np.sin(2 * np.pi * ff * t + rng.uniform(0, 6)) + .3 * bright * np.sin(4 * np.pi * ff * t) + .12 * bright * np.sin(6 * np.pi * ff * t)
    lfo = 1 + .15 * np.sin(2 * np.pi * .2 * t + rng.uniform(0, 6))
    return amp / len(freqs) * s * lfo * env(n, min(.9, dur / 3), min(1.2, dur / 3))

def bass(f, dur, amp=.22):
    return amp * tone(f, dur, ((1, 1), (2, .25)), decay=1.2, a=.01, r=.15)

def noise(n): return rng.standard_normal(n)

def bandpass(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos"); return sosfilt(sos, x)
def lowpass(x, f, order=2):
    sos = butter(order, f, btype="low", fs=SR, output="sos"); return sosfilt(sos, x)
def highpass(x, f, order=2):
    sos = butter(order, f, btype="high", fs=SR, output="sos"); return sosfilt(sos, x)

def reverb(st, size=1.6, wet=.3):
    n = int(size * SR); t = np.arange(n) / SR
    out = np.zeros((st.shape[0] + n - 1, 2))
    for ch in range(2):
        ir = noise(n) * np.exp(-t / (size / 5)); ir = lowpass(ir, 6000); ir /= np.sqrt((ir ** 2).sum())
        out[:, ch] = fftconvolve(st[:, ch], ir)
    dry = np.zeros_like(out); dry[:st.shape[0]] = st
    return (dry * (1 - wet) + out * wet * 2.2)[:st.shape[0]]

class Track:
    def __init__(self, dur): self.b = np.zeros((int(dur * SR) + SR, 2))
    def add(self, sig, t, pan=0.0, gain=1.0):
        i = int(t * SR)
        if i >= len(self.b) or i < -len(sig): return
        if i < 0: sig = sig[-i:]; i = 0
        sig = sig[:len(self.b) - i]
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        self.b[i:i + len(sig), 0] += sig * l * gain * 1.414; self.b[i:i + len(sig), 1] += sig * r * gain * 1.414

# ================================================================== themes (original)
THEME = [(2, 1), (4, 1), (5, 1), (4, 1), (2, 1.5), (1, .5), (0, 2), (2, 1), (4, 1), (5, 1), (7, 1), (6, 2), (4, 2),
         (5, 1), (4, 1), (2, 1), (4, 1), (5, 1.5), (4, .5), (2, 2), (1, 1), (2, 1), (4, 1), (1, 1), (0, 4)]
THEME_CH = [0, 5, 3, 4, 3, 0, 1, 4]          # chord degree per 4-beat bar
LULL = [(4, 1), (2, 1), (1, 1), (0, 3), (4, 1), (5, 1), (4, 1), (2, 3), (2, 1), (4, 1), (7, 1), (6, 2), (5, 1), (4, 1), (2, 1), (1, 1), (0, 3)]
LULL_CH = [0, 0, 3, 0, 5, 3, 4, 0]            # per 3-beat bar
def triad(root, d): return [deg(root, d), deg(root, d + 2), deg(root, d + 4)]

def cue(mood, dur, seed=0):
    """Generate a stereo cue of `dur` seconds for a mood."""
    tr = Track(dur)
    if mood in ("play", "title", "finale", "kind"):
        root = {"play": 60, "title": 65, "finale": 60, "kind": 55}[mood]
        bpm = {"play": 104, "title": 84, "finale": 92, "kind": 80}[mood]
        bt = 60 / bpm; bar = 4 * bt
        nb = int(dur / bar) + 1
        for b in range(nb):
            t0 = b * bar; ch = THEME_CH[b % 8]
            tr.add(pad([note_hz(m) for m in triad(root - 12, ch)], bar + .6, .07 if mood != "finale" else .1), t0, 0, 1)
            tr.add(bass(note_hz(deg(root - 24, ch)), bar * .9), t0, 0, .9 if mood != "kind" else .7)
            tr.add(bass(note_hz(deg(root - 24, ch + 4)), bar * .45), t0 + 2 * bt, 0, .5)
            for k in range(8):  # light arpeggio
                m = triad(root, ch)[[0, 1, 2, 1][k % 4]] + (12 if k >= 4 and mood == "finale" else 0)
                inst = marimba if mood == "play" else (pluck if mood == "kind" else bell)
                tr.add(inst(note_hz(m), .6, .09 if mood != "title" else .06), t0 + k * bt / 2, .3 * ((-1) ** k))
            if mood == "play":  # soft shaker
                for k in range(8):
                    sh = bandpass(noise(int(.05 * SR)), 5000, 11000) * np.exp(-np.arange(int(.05 * SR)) / SR / .015)
                    tr.add(sh * (.05 if k % 2 else .025), t0 + k * bt / 2, .5)
        # melody: theme, played from bar 2 if the cue is long enough
        if dur > 12:
            t = bar * (1 if mood != "title" else .5); inst = {"play": marimba, "title": bell, "finale": bell, "kind": pluck}[mood]
            rep = 0
            while t < dur - 2 and rep < 3:
                for d, ln in THEME:
                    if t > dur - 1.5: break
                    tr.add(inst(note_hz(deg(root + 12 if mood == "play" else root, d)), max(.5, ln * bt * 1.2), .17), t, -.1)
                    if mood == "finale": tr.add(tone(note_hz(deg(root, d)), ln * bt, ((1, 1), (2, .3)), a=.04, r=.1) * .05, t, .1)
                    t += ln * bt
                t += bar * 2; rep += 1
        wet = .25
    elif mood in ("evening", "lullaby", "credits", "memory"):
        root = {"evening": 65, "lullaby": 65, "credits": 65, "memory": 67}[mood]
        bpm = {"evening": 76, "lullaby": 66, "credits": 70, "memory": 72}[mood]
        bt = 60 / bpm; bar = 3 * bt
        for b in range(int(dur / bar) + 1):
            t0 = b * bar; ch = LULL_CH[b % 8]
            tr.add(pad([note_hz(m) for m in triad(root - 12, ch)], bar + .8, .06, .6), t0)
            tr.add(bass(note_hz(deg(root - 24, ch)), bar, .14), t0)
            for k in range(6):
                m = triad(root, ch)[[0, 1, 2, 1, 2, 1][k]] + 12
                tr.add(musicbox(note_hz(m), 1.2, .05), t0 + k * bt / 2, .4 * ((-1) ** k))
        if dur > 10:
            t = bar * 2
            while t < dur - 3:
                for d, ln in LULL:
                    if t > dur - 2: break
                    tr.add(musicbox(note_hz(deg(root + 12, d)), max(.8, ln * bt * 1.3), .14), t)
                    t += ln * bt
                t += bar * 2
        wet = .35
    else:  # dream moods: dream, honey, wonder, heart, flight, shoes, reveal
        root = {"dream": 63, "honey": 61, "wonder": 62, "heart": 62, "flight": 62, "shoes": 65, "reveal": 65}[mood]
        bpm = {"dream": 60, "honey": 50, "wonder": 88, "heart": 72, "flight": 124, "shoes": 110, "reveal": 70}[mood]
        LYD = [0, 2, 4, 6, 7, 9, 11]
        sc = LYD if mood in ("dream", "honey", "wonder") else MAJOR
        prog = {"dream": [0, 4, 5, 3], "honey": [0, 5, 3, 4], "wonder": [0, 1, 4, 5], "heart": [0, 5, 3, 4],
                "flight": [0, 4, 5, 3], "shoes": [0, 3, 4, 0], "reveal": [0, 5, 3, 4]}[mood]
        bt = 60 / bpm; bar = 4 * bt
        for b in range(int(dur / bar) + 1):
            t0 = b * bar; ch = prog[b % 4]
            tri = [deg(root - 12, ch, sc), deg(root - 12, ch + 2, sc), deg(root - 12, ch + 4, sc), deg(root, ch + 6, sc)]
            build = min(1, b / max(1, dur / bar - 1)) if mood == "flight" else 1
            tr.add(pad([note_hz(m) for m in tri], bar + 1.5, .09 if mood != "flight" else .07 + .05 * build, .5), t0)
            if mood in ("flight", "wonder", "heart", "reveal", "shoes"):
                tr.add(bass(note_hz(deg(root - 24, ch, sc)), bar * .9, .16), t0)
            steps = {"dream": 8, "honey": 4, "wonder": 8, "heart": 8, "flight": 16, "shoes": 8, "reveal": 6}[mood]
            for k in range(steps):
                m = tri[[0, 1, 2, 3, 2, 1][k % 6]] + 12 + (12 if mood == "flight" and k % 8 >= 4 else 0)
                inst = bell if mood != "shoes" else marimba
                a = {"dream": .06, "honey": .05, "wonder": .07, "heart": .06, "flight": .05 + .03 * build, "shoes": .1, "reveal": .05}[mood]
                tr.add(inst(note_hz(m), 1.0, a), t0 + k * bar / steps, .5 * math.sin(k * 1.3))
            if mood == "flight":  # pulse + swell
                for k in range(4):
                    kick = tone(60, .25, ((1, 1),), decay=.08, a=.001, r=.05) * .25 * build
                    tr.add(kick, t0 + k * bt)
                if b % 4 == 3:
                    sw = highpass(noise(int(bar * SR)), 3000) * np.linspace(0, 1, int(bar * SR)) ** 2 * .04
                    tr.add(sw, t0)
        if mood in ("heart", "flight", "reveal") and dur > 8:
            t = bar
            while t < dur - 3:
                for d, ln in THEME:
                    if t > dur - 2: break
                    tr.add(bell(note_hz(deg(root + 12, d)), max(.6, ln * bt * 1.3), .14), t)
                    tr.add(tone(note_hz(deg(root, d)), ln * bt + .2, ((1, 1), (2, .4), (3, .15)), a=.08, r=.2, vib=1) * .05, t)
                    t += ln * bt
                t += bar
        wet = .45 if mood in ("dream", "honey", "wonder", "heart") else .3
    out = reverb(tr.b[:int(dur * SR)], 2.4 if wet > .4 else 1.5, wet)
    n = out.shape[0]; f = min(int(1.2 * SR), n // 3)
    out[:f] *= np.linspace(0, 1, f)[:, None]; out[-f:] *= np.linspace(1, 0, f)[:, None]
    return out

# per-scene music plan: list of (mood, start_tag or None)
PLAN = {
 0: [("title", None)], 1: [("play", None)], 2: [("play", None), ("evening", "sunset")], 3: [("evening", None), ("lullaby", "walls")],
 4: [("play", None)], 5: [("play", None)], 6: [("play", None)], 7: [("play", None)], 8: [("kind", None)],
 9: [("lullaby", None), ("dream", "sleep")], 10: [("dream", None), ("honey", "honey"), ("memory", "pool")],
 11: [("evening", None), ("lullaby", "sleep")], 12: [("dream", None), ("wonder", "fly")], 13: [("wonder", None)],
 14: [("wonder", None), ("heart", "heart")], 15: [("flight", None)], 16: [("shoes", None), ("reveal", "wire")],
 17: [("play", None), ("dream", "adventures"), ("finale", "journey")], 18: [("credits", None)],
}

def scene_offsets(man):
    offs, cur = {}, 0.0
    ctxs = {}
    for s in range(19):
        c = Ctx(s, man); offs[s] = cur; ctxs[s] = c; cur += c.dur
    return offs, ctxs, cur

def build_music(man):
    offs, ctxs, total = scene_offsets(man)
    tr = Track(total + 2)
    # group consecutive scenes with the same mood into one continuous cue
    segs = []
    for s in range(19):
        c = ctxs[s]
        for i, (mood, tag) in enumerate(PLAN[s]):
            st = offs[s] + (c.s(tag) - .5 if tag else 0)
            segs.append([mood, st])
    merged = []
    for mood, st in segs:
        if merged and merged[-1][0] == mood: continue
        merged.append([mood, st])
    for i, (mood, st) in enumerate(merged):
        en = merged[i + 1][1] + 1.5 if i + 1 < len(merged) else total
        d = en - st
        print(f"  cue {mood:8s} {st:7.1f}s  {d:5.1f}s", flush=True)
        tr.b[int(st * SR):int(st * SR) + int(d * SR)] += cue(mood, d, i)[:len(tr.b) - int(st * SR)]
    return tr.b[:int(total * SR)], offs, ctxs, total

# ================================================================== SFX
def s_whoosh(d=.8, lo=300, hi=3000, amp=.25):
    n = int(d * SR); x = noise(n); x = bandpass(x, lo, hi); e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return amp * x * e / (np.abs(x).max() + 1e-9)
def s_rustle(d=1.2, amp=.15):
    n = int(d * SR); x = highpass(noise(n), 2000) * (np.abs(lowpass(noise(n), 30)) * 3)
    return amp * x * env(n, .05, .4) / (np.abs(x).max() + 1e-9)
def s_tape(amp=.18):
    n = int(.45 * SR); x = bandpass(noise(n), 1500, 7000) * (1 + np.sin(np.arange(n) / SR * 2 * np.pi * 60)) * env(n, .01, .1)
    return amp * x / (np.abs(x).max() + 1e-9)
def s_snip(amp=.2):
    n = int(.06 * SR); x = highpass(noise(n), 4000) * np.exp(-np.arange(n) / SR / .01); return amp * x / (np.abs(x).max() + 1e-9)
def s_tap(amp=.35):
    n = int(.12 * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 900 * t) * .5 + bandpass(noise(n), 600, 2500)) * np.exp(-t / .02); return amp * x / (np.abs(x).max() + 1e-9)
def s_cluck(amp=.15):
    n = int(.14 * SR); t = np.arange(n) / SR
    f = 700 + 500 * np.exp(-t / .03); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .005, .04) + .2 * bandpass(noise(n), 1000, 3000) * env(n, .005, .04)
    return amp * x
def s_pop(amp=.3):
    n = int(.15 * SR); t = np.arange(n) / SR; f = 300 + 900 * np.exp(-t / .02)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .05)
def s_slide(d=1.4, f0=1400, f1=300, amp=.12):
    n = int(d * SR); f = np.geomspace(f0, f1, n); return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .03, .2)
def s_chime(amp=.12):
    out = np.zeros(int(2.5 * SR))
    for i, m in enumerate((84, 88, 91, 96, 100)):
        b = bell(note_hz(m), 2.0, amp); s = int(i * .07 * SR); out[s:s + len(b)] += b[:len(out) - s]
    return out
def s_heartbeat(amp=.5):
    out = np.zeros(int(.9 * SR))
    for o in (0, .22):
        th = tone(55, .2, ((1, 1), (2, .3)), decay=.06, a=.002, r=.05); s = int(o * SR); out[s:s + len(th)] += th
    return amp * out
def s_thud(amp=.35):
    n = int(.4 * SR); t = np.arange(n) / SR
    return amp * (np.sin(2 * np.pi * 70 * t) * np.exp(-t / .08) + .4 * lowpass(noise(n), 800) * np.exp(-t / .05))
def s_splash(amp=.12):
    n = int(1.0 * SR); x = bandpass(noise(n), 800, 8000) * env(n, .01, .5, .3); return amp * x / (np.abs(x).max() + 1e-9)
def s_engine(d, amp=.18):
    n = int(d * SR); t = np.arange(n) / SR
    x = .6 * np.sin(2 * np.pi * 42 * t + 3 * np.sin(2 * np.pi * 7 * t)) + .5 * lowpass(noise(n), 300)
    return amp * x * env(n, .8, 1.2)
def s_hiss(amp=.12):
    n = int(.8 * SR); x = highpass(noise(n), 3000) * env(n, .01, .5); return amp * x / (np.abs(x).max() + 1e-9)
def s_wind(d, amp=.05):
    n = int(d * SR); x = bandpass(noise(n), 200, 1200) * (0.6 + .4 * np.sin(np.arange(n) / SR * 2 * np.pi * .13)); return amp * x / (np.abs(x).max() + 1e-9) * env(n, 1.0, 1.0)
def s_birds(d, amp=.05):
    out = np.zeros(int(d * SR))
    for k in range(int(d / 1.3)):
        st = rng.uniform(0, d - .5); n = int(.12 * SR); t = np.arange(n) / SR
        f = rng.uniform(2800, 4200) + 900 * np.sin(2 * np.pi * rng.uniform(15, 30) * t)
        ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .01, .05)
        s = int(st * SR); out[s:s + n] += ch * amp
    return out
def s_giggle(amp=.0): return np.zeros(1)
def s_step(amp=.12):
    n = int(.08 * SR); return amp * lowpass(noise(n), 900) * np.exp(-np.arange(n) / SR / .02)

def build_sfx(offs, ctxs, total):
    tr = Track(total + 2)
    def at(s, x): return offs[s] + x
    O = offs; C = ctxs
    # ambience
    for s in (1, 2, 5, 6, 7, 8, 17):
        d = C[s].dur
        tr.add(s_wind(d, .05), O[s]); tr.add(s_birds(d, .035), O[s], .3)
    for s in (9, 10, 11):
        tr.add(s_wind(C[s].dur, .03), O[s], -.3)
    # scene 1: snips + tape
    c = C[1]
    for k in range(10): tr.add(s_snip(), at(1, c.s("garage") + 2.2 + k * .33), .2)
    for k in range(4): tr.add(s_tape(), at(1, c.s("build") + 1 + k * 2.0), -.2)
    tr.add(s_chime(.08), at(1, c.s("idea")), .2)
    # scene 2: running steps, door, leaves
    c = C[2]
    for k in range(int(c.s("rest") * 4.4)): tr.add(s_step(.06), at(2, k / 4.4 + .3), .1 * ((-1) ** k))
    tr.add(s_rustle(2.5, .12), at(2, c.s("sunset")), 0)
    # scene 4: stairs + chair
    c = C[4]
    for k in range(int((c.s("mom") - c.s("run")) * 6)): tr.add(s_step(.1), at(4, c.s("run") + k / 6))
    tr.add(s_thud(.2), at(4, c.s("leap") + .15)); tr.add(s_thud(.15), at(4, c.s("leap") + 1.1))
    tr.add(s_chime(.07), at(4, c.s("idea")))
    # scene 5: clucks
    c = C[5]
    t = 0.4
    while t < c.dur - .5:
        tr.add(s_cluck(rng.uniform(.08, .15)), at(5, t), rng.uniform(-.6, .6)); t += rng.uniform(.35, 1.4)
    for k in range(3): tr.add(s_tape(.14), at(5, c.s("tape") + 1.5 + k * 2.2))
    # scene 6
    c = C[6]
    tr.add(s_whoosh(.6, 400, 2000, .12), at(6, c.s("run")))
    for k in range(int((c.s("collapse") - c.s("run")) * 5)): tr.add(s_step(.07), at(6, c.s("run") + k / 5))
    tr.add(s_thud(.25), at(6, c.s("collapse") + .1)); tr.add(s_chime(.08), at(6, c.s("spark")))
    # scene 7: rake + leaf bursts (same cycle maths as the animation)
    c = C[7]
    for k in range(int((c.e("rake") - 1.2 - c.s("rake")) / .8)): tr.add(s_rustle(.6, .08), at(7, c.s("rake") + k * .8))
    cs = c.e("rake") - 1.2; first = True
    while cs < c.dur:
        parts = (0.0, 2.6, 1.4, .9, 2.2) if first else (.8, 2.0, 1.0, .9, 1.6)
        land = cs + sum(parts[:4])
        tr.add(s_whoosh(.5, 500, 2500, .1), at(7, land - .6)); tr.add(s_rustle(1.6, .25), at(7, land)); tr.add(s_thud(.15), at(7, land))
        cs += sum(parts); first = False
    # scene 8: truck
    c = C[8]
    tr.add(s_engine(c.s("leave") + 5 - c.s("truck"), .16), at(8, c.s("truck")))
    tr.add(s_hiss(), at(8, c.s("truck") + 3.2)); tr.add(s_hiss(.08), at(8, c.s("leave") + 1.4))
    # scene 9 / 10 / 11: dream chimes and branch taps
    tr.add(s_chime(.1), at(9, C[9].dur - 3))
    c = C[10]
    k = 0
    while True:
        tt = (0.25 + k) / .9; k += 1
        if tt > c.s("remember") + .5: break
        tr.add(s_tap(.3), at(10, tt), .5)
    tr.add(s_chime(.12), at(10, c.s("remember") - .3))
    for k in range(10): tr.add(s_splash(.08), at(10, c.s("pool") + .5 + k * .7), rng.uniform(-.6, .6))
    # scene 12-15: flight
    c = C[12]; tr.add(s_whoosh(1.2, 300, 2500, .18), at(12, c.s("jump") + .2)); tr.add(s_chime(.12), at(12, c.s("fly")))
    c = C[13]
    zt = c.s("zip")
    while zt < c.s("nope"): tr.add(s_whoosh(.35, 800, 5000, .14), at(13, zt), rng.uniform(-.8, .8)); zt += .55
    c = C[14]
    for k in range(8): tr.add(s_heartbeat(.35 + .05 * k), at(14, c.s("heart") - .6 + k * .85))
    tr.add(s_chime(.15), at(14, c.s("heart") + .4))
    c = C[15]
    for tag in ("open", "higher", "clouds", "moon", "faster"): tr.add(s_whoosh(1.6, 200, 3000, .16), at(15, c.s(tag)), rng.uniform(-.5, .5))
    tr.add(s_whoosh(3.0, 400, 8000, .25), at(15, c.s("faster") + 1))
    # scene 16: pop, slide whistle, wire twang
    c = C[16]
    tr.add(s_pop(.3), at(16, c.s("lost") + 2.4)); tr.add(s_pop(.25), at(16, c.s("lost") + 2.5))
    tr.add(s_slide(1.6, 1500, 250, .1), at(16, c.s("laces")))
    tw = tone(110, 1.2, ((1, 1), (2, .5), (3, .3)), decay=.4) * .15
    tr.add(tw, at(16, c.s("wire") - .2))
    tr.add(s_chime(.1), at(16, c.s("reveal")))
    return tr.b[:int(total * SR)]

def build_narration(man, offs, ctxs, total):
    tr = Track(total + 2)
    lines_dir = os.path.join(BUILD, "audio", "lines")
    pan = {"N": 0, "O": -.08, "M": .1, "D": .12, "G": .12}
    for key, v in man.items():
        sid = v["scene"]; b = [x for x in ctxs[sid].beats if x.idx == v["idx"]][0]
        x, sr = sf.read(os.path.join(lines_dir, key + ".wav"))
        if sr != SR:
            from scipy.signal import resample_poly
            x = resample_poly(x, SR, sr)
        tr.add(x, offs[sid] + b.start, pan[v["speaker"]], 1.0)
    # gentle presence EQ + room
    y = tr.b[:int(total * SR)]
    y = y + .25 * highpass(y, 3500, 1) * 0
    return reverb(y, .6, .06)

def srt(man, offs, ctxs):
    def ts(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    rows = []
    for sid in range(1, 18):
        for b in ctxs[sid].beats:
            rows.append((offs[sid] + b.start, offs[sid] + b.end + .25, b.text))
    rows.sort()
    out = []
    for i, (a, e, txt) in enumerate(rows, 1):
        out.append(f"{i}\n{ts(a)} --> {ts(e)}\n{txt}\n")
    return "\n".join(out)

if __name__ == "__main__":
    man = load_manifest()
    os.makedirs(os.path.join(BUILD, "audio"), exist_ok=True)
    print("music…", flush=True)
    music, offs, ctxs, total = build_music(man)
    print("sfx…", flush=True)
    sfx = build_sfx(offs, ctxs, total)
    print("narration…", flush=True)
    narr = build_narration(man, offs, ctxs, total)
    # duck music under voice
    v = np.abs(narr).mean(axis=1)
    k = int(.25 * SR); vs = np.convolve(v, np.ones(k) / k, mode="same")
    duck = 1 - .55 * np.clip(vs / (np.percentile(vs, 90) + 1e-9), 0, 1)
    duck = np.convolve(duck, np.ones(k) / k, mode="same")[:, None]
    music = music / (np.abs(music).max() + 1e-9) * .5
    mix = narr * 1.0 + music * duck * .68 + sfx * .8
    peak = np.abs(mix).max(); mix = mix / peak * .89 if peak > .89 else mix
    for name, x in (("music", music), ("sfx", sfx), ("narration", narr), ("mix", mix)):
        sf.write(os.path.join(BUILD, "audio", name + ".wav"), x.astype(np.float32), SR)
    open(os.path.join(BUILD, "film.srt"), "w").write(srt(man, offs, ctxs))
    json.dump({str(k): v for k, v in offs.items()} | {"total": total}, open(os.path.join(BUILD, "audio", "offsets.json"), "w"), indent=1)
    print(f"done: {total/60:.2f} min, peak {peak:.2f}")
