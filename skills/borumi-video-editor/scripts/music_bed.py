#!/usr/bin/env python3
# Copyright (c) 2026 Nillard Ltd (company no. 16312961). Nillard Ltd Skills License 1.0, see LICENSE. Not for resale or redistribution.
"""Build ONE continuous music bed (a WAV) for a stretch of the timeline, from several tracks.

Borumi's music layer is exclusive (no overlapping music segments), so a video with a track per
chapter needs the tracks pre-mixed into one file and placed as a single `music` segment.

Usage:
  python3 music_bed.py bed.json

bed.json (all times in PROJECT seconds, i.e. on the current Borumi timeline):
  {
    "music_dir": "<MUSIC_LIBRARY>",          folder the track paths are relative to
    "out": "<WORKSPACE>/<video>/music/bed.wav",
    "start": 148.1,                           where the bed starts (= where you will place it)
    "end": 1350.3,                            where it ends
    "lufs": -41,                              level of every part (about 20 dB under a -21 LUFS voice)
    "crossfade": 0.75,                        seconds each part overlaps its neighbour on each side
    "fade_in": 1.5, "fade_out": 3.0,          first part's fade in, last part's fade out
    "ramp": 0.4,                              fade to/from silence around each mute
    "parts": [[148.1, 388.1, "track-a.mp3", 0],      [start, end, file, offset into the file]
              [388.1, 582.3, "track-b.mp3", 100]],   put each switch under a chapter card
    "mutes": [[744.75, 762.54]]               silence under playbacks / montages with their own sound
  }

How it levels: each part is cut (looped if the track is shorter than the part), measured with
ffmpeg's ebur128 and gained to exactly `lufs`. loudnorm alone landed 1-2 dB off.

The bed is placed by fixed time, so REBUILD it after any later cut or untrim, and re-place it.
In Borumi: import_media, add a `music` segment at `start`, and turn `enable_looping` off (new
music segments default to looping).

Requires: ffmpeg on PATH, Python 3 with numpy.
"""
import json, os, re, subprocess, sys
import numpy as np

SR = 48000


def run(cmd, **kw):
    return subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + cmd, check=True, **kw)


def part_audio(path, offset, dur, target, tmp):
    run(["-stream_loop", "-1", "-ss", str(offset), "-i", path, "-t", str(dur),
         "-ar", str(SR), "-ac", "2", tmp])
    log = subprocess.run(["ffmpeg", "-nostdin", "-i", tmp, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", log)[-1])
    raw = run(["-i", tmp, "-f", "f32le", "-"], capture_output=True).stdout
    os.remove(tmp)
    return np.frombuffer(raw, np.float32).reshape(-1, 2) * 10 ** ((target - lufs) / 20)


def ramp(n, up):
    r = np.linspace(0, 1, n, dtype=np.float32) ** 0.5  # equal-power-ish
    return r if up else r[::-1]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    c = json.load(open(sys.argv[1]))
    t0, t1, X = c["start"], c["end"], c.get("crossfade", 0.75)
    N = int((t1 - t0) * SR)
    bed = np.zeros((N, 2), np.float32)
    parts = c["parts"]
    for i, (a, b, f, off) in enumerate(parts):
        s, e = max(a - X, t0), min(b + X, t1)
        x = part_audio(os.path.join(c["music_dir"], f), off, e - s, c.get("lufs", -41), c["out"] + f".p{i}.wav")
        n = len(x)
        fi = int((c.get("fade_in", 1.5) if i == 0 else 2 * X) * SR)
        fo = int((c.get("fade_out", 3.0) if i == len(parts) - 1 else 2 * X) * SR)
        g = np.ones(n, np.float32)
        g[:fi] = ramp(fi, True)
        g[n - fo:] = np.minimum(g[n - fo:], ramp(fo, False))
        o = int((s - t0) * SR)
        m = min(n, N - o)
        bed[o:o + m] += x[:m] * g[:m, None]
    env = np.ones(N, np.float32)
    r = int(c.get("ramp", 0.4) * SR)
    for a, b in c.get("mutes", []):
        ia, ib = max(int((a - t0) * SR), 0), min(int((b - t0) * SR), N)
        env[ia:ib] = 0
        lo = max(ia - r, 0)
        env[lo:ia] = np.minimum(env[lo:ia], np.linspace(1, 0, ia - lo))
        hi = min(ib + r, N)
        env[ib:hi] = np.minimum(env[ib:hi], np.linspace(0, 1, hi - ib))
    bed *= env[:, None]
    run(["-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", c["out"]], input=bed.tobytes())
    print(f"{c['out']}: {N / SR:.1f} s, {len(parts)} parts, {len(c.get('mutes', []))} mutes")


if __name__ == "__main__":
    main()
