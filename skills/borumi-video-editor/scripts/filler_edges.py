#!/usr/bin/env python3
"""Turn filler candidates into cut ranges whose edges hug the filler on the waveform.
Usage: python3 filler_edges.py <timeline-audio.wav> <cands.json> <out.json>
cands.json: [[a_ms, b_ms, label], ...] in PROJECT time, where a = end of the last kept word and
b = start of the next kept word (from Borumi get_transcript words). Audio = export_audio of the
CURRENT timeline (re-export after any trim, including the creator's own edits in the app).
OUT = 30 ms-smoothed energy valley in [a-80, a+40] ms; IN = valley in [b-40, b+80] ms.
Keep these windows narrow: a +-200 ms search cut into the filler itself and left 60-130 ms of "uh".
Cuts shorter than 60 ms are skipped. Output: [[start_ms, end_ms, label], ...] for trim_timeline.
Requires: ffmpeg on PATH, Python 3 with numpy."""
import json, sys, subprocess, numpy as np
if len(sys.argv) < 4: sys.exit(__doc__)
src, cands, out_path = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; n = len(x) // 480; total_ms = n * 10
db = 20 * np.log10(np.sqrt((x[:n * 480].reshape(n, 480) ** 2).mean(1)) + 1e-9)
sm = np.convolve(db, np.ones(3) / 3, "same"); out = []
for a, b, lab in cands:
    ia, ib = a // 10, b // 10
    w1 = (max(ia - 8, 0), min(ia + 4, n - 1)); o = w1[0] + int(np.argmin(sm[w1[0]:w1[1] + 1]))
    w2 = (max(ib - 4, o + 4), min(ib + 8, n - 1))
    i = ib if w2[0] >= w2[1] else w2[0] + int(np.argmin(sm[w2[0]:w2[1] + 1])) + 1
    if b >= total_ms - 30: i = n  # trailing cut runs to the end
    if (i - o) * 10 < 60: print("skip", a, b, lab); continue
    out.append([o * 10, min(i * 10, total_ms), lab])
json.dump(out, open(out_path, "w"))
print(len(out), "cuts, removing", round(sum(e - s for s, e, _ in out) / 1000, 1), "s")
