#!/usr/bin/env python3
# Copyright (c) 2026 Nillard Ltd (company no. 16312961). Nillard Ltd Skills License 1.0, see LICENSE. Not for resale or redistribution.
"""Paint out text burned into a screen recording (a date on a label, a name, a number).

Makes a small PNG patch to lay over the recording as a `media_overlay` at a custom position.
Each column inside the box is interpolated between the row just above and the row just below
it, then lightly blurred, so the patch matches see-through pills and gradients. One flat colour
leaves a visible block.

Only works where the text sits still in the frame for the whole overlay. If it moves, use a
still of the whole screen instead (see borumi-learnings.md, covering glitches).

Usage:
  python3 patch_still.py <frame.png> <x0> <y0> <x1> <y1> <out.png> [--pad 3]

  frame.png   a full frame at the exact moment, saved with inspect_timeline (save: true,
              quality "max"), or pulled from the source media with ffmpeg
  x0 y0 x1 y1 the text box in pixels of that frame (pad it by a few px)
Prints the Borumi custom position (x, y, w, h as 0-1 ratios of the frame) for the overlay.
Set the overlay's shadow to null and entrance/exit to instant.

Requires: Python 3 with numpy and Pillow.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

a = sys.argv[1:]
pad = 3
if "--pad" in a:
    i = a.index("--pad"); pad = int(a[i + 1]); del a[i:i + 2]
if len(a) < 6:
    sys.exit(__doc__)
src, (x0, y0, x1, y1), out = a[0], map(int, a[1:5]), a[5]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
H, W, _ = im.shape
x0, y0, x1, y1 = max(x0 - pad, 0), max(y0 - pad, 1), min(x1 + pad, W), min(y1 + pad, H - 1)
top, bot = im[y0 - 1, x0:x1], im[y1, x0:x1]
t = np.linspace(0, 1, y1 - y0)[:, None, None]
patch = (1 - t) * top[None] + t * bot[None]
img = Image.fromarray(patch.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
img.save(out)
print(f"{out}: {x1 - x0}x{y1 - y0} px; Borumi position x {x0 / W:.4f} y {y0 / H:.4f} w {(x1 - x0) / W:.4f} h {(y1 - y0) / H:.4f}")
