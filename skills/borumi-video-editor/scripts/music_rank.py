#!/usr/bin/env python3
# Copyright (c) 2026 Nillard Ltd (company no. 16312961). Nillard Ltd Skills License 1.0, see LICENSE. Not for resale or redistribution.
"""Rank candidate music tracks for a body bed, and render an audition reel under the voice.

Body music (talking, explaining, screen share) should be sparse: few instruments, low energy, and
little energy where the voice lives. This measures each track and ranks it against a reference
track the creator already likes.

Usage:
  python3 music_rank.py <reference> <candidate> [<candidate> ...] [--voice voice.wav] [--reel out.mp4]

  reference    a track that has the vibe the creator wants (e.g. one they approved before)
  candidates   tracks to rank (download only after the creator says yes; check the licence)
  --voice      a 10 s+ clip of the creator talking (export_audio of a plain talking stretch)
  --reel       write an audition reel: reference, then each of the top 5 candidates as
               10 s alone + 10 s under the voice, with the music 20 dB under the voice
               (the real mix level). The reel has no labels; the ranking table gives the order.

Measured on 60 s from 30 s into each track:
  busyness    onset peaks per second (lower = calmer)
  voice_band  share of energy in 300-3000 Hz, where speech sits (lower = less masking)
  tempo       BPM estimate from the onset envelope
  dynamics    spread (std) of 400 ms loudness in dB (lower = steadier)
Rank = distance to the reference on those four (busyness and voice_band weighted double).

Requires: ffmpeg on PATH, Python 3 with numpy.
"""
import os, re, subprocess, sys, tempfile
import numpy as np

SR = 22050


def load(path, ss=30.0, dur=60.0):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(ss), "-i", path, "-t", str(dur),
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) < SR * 10 and ss > 0:  # short track: measure from the start
        return load(path, 0, dur)
    return x


def features(x):
    hop, win = 512, 2048
    n = max(1, (len(x) - win) // hop)
    fr = np.lib.stride_tricks.sliding_window_view(x, win)[::hop][:n] * np.hanning(win)
    sp = np.abs(np.fft.rfft(fr))
    f = np.fft.rfftfreq(win, 1 / SR)
    e = (sp ** 2).sum(1) + 1e-12
    voice = (sp[:, (f >= 300) & (f <= 3000)] ** 2).sum(1).sum() / e.sum()
    flux = np.maximum(np.diff(np.log1p(sp), axis=0), 0).sum(1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    fps = SR / hop
    peaks = (flux[1:-1] > flux[:-2]) & (flux[1:-1] >= flux[2:]) & (flux[1:-1] > 1.0)
    busy = peaks.sum() / (len(flux) / fps)
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    lags = np.arange(len(ac)) / fps
    ok = (lags >= 60 / 180) & (lags <= 60 / 70)
    tempo = 60 / lags[ok][ac[ok].argmax()] if ok.any() else 0.0
    blk = int(0.4 * SR)
    m = len(x) // blk
    db = 20 * np.log10(np.sqrt((x[:m * blk].reshape(m, blk) ** 2).mean(1)) + 1e-9)
    dyn = float(np.std(db[db > db.max() - 40])) if m else 0.0
    return dict(busyness=float(busy), voice_band=float(voice), tempo=float(tempo), dynamics=dyn)


def lufs(path):
    log = subprocess.run(["ffmpeg", "-nostdin", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", log)[-1])


def reel(ref, ranked, voice, out):
    v_lufs = lufs(voice)
    tmp = tempfile.mkdtemp()
    pieces = []

    def clip(src, ss, dur, gain_to, name, under_voice=False):
        p = os.path.join(tmp, name)
        g = gain_to - lufs_cache.setdefault(src, lufs(src))
        if under_voice:
            fc = f"[0]volume={g}dB[m];[m][1]amix=inputs=2:normalize=0:duration=first"
            cmd = ["-ss", str(ss), "-t", str(dur), "-i", src, "-t", str(dur), "-i", voice, "-filter_complex", fc]
        else:
            cmd = ["-ss", str(ss), "-t", str(dur), "-i", src, "-af", f"volume={g}dB"]
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + cmd + ["-ar", "48000", "-ac", "2", p], check=True)
        pieces.append(p)

    lufs_cache = {}
    clip(ref, 30, 10, v_lufs - 6, "00_ref.wav")
    for i, (path, _, _) in enumerate(ranked[:5], 1):
        clip(path, 30, 10, v_lufs - 6, f"{i:02d}_alone.wav")
        clip(path, 30, 10, v_lufs - 20, f"{i:02d}_voice.wav", under_voice=True)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in pieces))
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "lavfi", "-i", "color=c=black:s=640x360:r=25", "-shortest", "-c:a", "aac", out], check=True)
    print(f"reel: {out}  (reference 10 s, then per candidate 10 s alone + 10 s under the voice)")


def main():
    a = sys.argv[1:]
    opt = {}
    for k in ("--voice", "--reel"):
        if k in a:
            i = a.index(k); opt[k] = a[i + 1]; del a[i:i + 2]
    if len(a) < 2:
        sys.exit(__doc__)
    ref, cands = a[0], a[1:]
    R = features(load(ref))
    keys, w = ["busyness", "voice_band", "tempo", "dynamics"], np.array([2, 2, 1, 1])
    scale = {"busyness": max(R["busyness"], 0.5), "voice_band": max(R["voice_band"], 0.05),
             "tempo": max(R["tempo"], 60), "dynamics": max(R["dynamics"], 1)}
    rows = []
    for c in cands:
        F = features(load(c))
        d = np.sqrt((w * np.array([((F[k] - R[k]) / scale[k]) ** 2 for k in keys])).sum())
        rows.append((c, float(d), F))
    rows.sort(key=lambda r: r[1])
    print(f"{'track':40s} {'dist':>5s} {'busy/s':>7s} {'voice%':>7s} {'bpm':>5s} {'dyn dB':>7s}")
    print(f"{'REF ' + os.path.basename(ref):40.40s} {0:5.2f} {R['busyness']:7.2f} {100 * R['voice_band']:7.1f} {R['tempo']:5.0f} {R['dynamics']:7.1f}")
    for c, d, F in rows:
        print(f"{os.path.basename(c):40.40s} {d:5.2f} {F['busyness']:7.2f} {100 * F['voice_band']:7.1f} {F['tempo']:5.0f} {F['dynamics']:7.1f}")
    if "--reel" in opt:
        if "--voice" not in opt:
            sys.exit("--reel needs --voice")
        reel(ref, rows, opt["--voice"], opt["--reel"])


if __name__ == "__main__":
    main()
