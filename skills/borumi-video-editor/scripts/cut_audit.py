#!/usr/bin/env python3
# Copyright (c) 2026 Nillard Ltd (company no. 16312961). Nillard Ltd Skills License 1.0, see LICENSE. Not for resale or redistribution.
"""Read the audio around a cut point in a Borumi source clip, 10 ms at a time.

Borumi's MCP doesn't expose waveforms, so read the source media (in the project
bundle's medias/ folder) directly.

Usage:
  python3 cut_audit.py <source.mp4> <src_seconds> [window_s=0.5]

  <source.mp4>   the source media inside the Borumi project bundle, e.g.
                 <project>.bmprojbundle/medias/<media_id>*.mp4
                 (skip the *.rvm-*.background.mp4 matte files)
  <src_seconds>  the cut point in SOURCE time (not timeline time)
  window_s       seconds to show on each side of the cut (default 0.5)

Requires: ffmpeg on PATH, Python 3 with numpy.

Prints, per 10 ms: source time, loudness (RMS dB) and high-frequency energy
(>4 kHz, dB). High-frequency energy shows S/SH/T sounds that loudness alone misses.

How to read it:
- Speech is roughly > -35 dB. Room silence on a typical close mic is about -50 to -60 dB.
- A sibilant (S) shows as a big jump in the >4k column (e.g. -45 -> -10) even
  when loudness is only modest.
- Put an OUT point in the quiet valley after the last word's tail
  (including its T/S release).
- Put an IN point 20-40 ms before the next word's onset (the rise from the
  noise floor).
- Never trust Whisper word timestamps alone (±50-100 ms).

Map source time to timeline time with the segment's media start:
  timeline = seg.start_ms + (src_ms - seg.media.start_ms)
"""
import sys, subprocess, numpy as np
if len(sys.argv) < 3:
    sys.exit(__doc__)
f = sys.argv[1]; c = float(sys.argv[2]); w = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
s = max(0, c - w)
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(s), "-t", str(2 * w), "-i", f,
                      "-vn", "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(float) / 32768
sr, win = 48000, 480
for i in range(0, len(a) - win, win):
    seg = a[i:i + win]
    rms = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
    sp = np.abs(np.fft.rfft(seg * np.hanning(win))); fr = np.fft.rfftfreq(win, 1 / sr)
    hi = 20 * np.log10(np.sqrt((sp[fr > 4000] ** 2).mean()) + 1e-9)
    t = s + i / sr
    mark = "  <-- cut" if abs(t - c) < 0.005 else ""
    print(f"{t:8.3f}  {rms:6.1f} dB  hf {hi:6.1f}  {'#' * max(0, int((rms + 60) / 2))}{mark}")
