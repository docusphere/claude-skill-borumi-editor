#!/usr/bin/env python3
# Copyright (c) 2026 Nillard Ltd (company no. 16312961). Nillard Ltd Skills License 1.0, see LICENSE. Not for resale or redistribution.
"""Render a real-page full-screen clip: replay the end of a scroll capture, hold,
ease the camera in to the claim, and wipe a lime highlight block under it (multiply
blend, so the text stays dark). A dark source pill appears bottom-left.

Usage:
  python3 page_clip.py config.json

Config keys (JSON):
  src     scroll-capture video (1920x1080), e.g. recorded with Playwright
  bbox    path to a JSON file with {"bbox": {"lines": [{x,y,w,h}, ...]}}
          OR
  lines   [{"x":..,"y":..,"w":..,"h":..}, ...]  the line boxes to highlight,
          in pixels of the final frame
  out     output .mp4 path
  dur     clip duration (s)
  tA      time (s) in the clip when the scroll arrives and stops
  rate    scroll replay speed (capture seconds per clip second)
  sEnd    capture time (s) whose frame matches the final screenshot. Use the
          frame that really matches; scrolls ease out slowly, so a frame-diff
          "scroll stopped" estimate can be seconds early.
  hl      [start, end] (s) of the highlight wipe
  tag     text of the source pill (e.g. the site name)
  tagAt   optional time (s) the pill fades in (default tA + 0.3)
  cam     camera keyframes [[t, cx, cy, scale], ...] (scale ~1.6-1.8 on the line)
  font    optional path to a .ttf for the pill (else env BORUMI_FONT,
          else Pillow's default font)

Output: 1920x1080, 60 fps, H.264 (crf 12).

Requires: ffmpeg on PATH, Python 3 with numpy and Pillow.
"""
import json, os, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1920,1080,60
LIME=np.array([200,255,0],np.float32)/255
FONT=os.environ.get("BORUMI_FONT")  # override per clip with the "font" config key
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x) if x<1 else 1.0
def eio(x): x=min(max(x,0),1); return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
def cam(t,keys):
    if t<=keys[0][0]: return keys[0][1:]
    for a,b in zip(keys,keys[1:]):
        if t<=b[0]:
            u=eio((t-a[0])/(b[0]-a[0])); return tuple(a[i]+(b[i]-a[i])*u for i in (1,2,3))
    return keys[-1][1:]
def decode(src):
    p=subprocess.run(["ffmpeg","-loglevel","error","-i",src,"-vf",f"fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True,check=True).stdout
    return np.frombuffer(p,np.uint8).reshape(-1,H,W,3)
def main(cfg):
    c=json.load(open(cfg)); fr=decode(c["src"]); D=c["dur"]; n=round(D*FPS)
    lines=c.get("lines") or json.load(open(c["bbox"]))["bbox"]["lines"]; tot=sum(l["w"] for l in lines)
    try: font=ImageFont.truetype(c.get("font") or FONT,30)
    except: font=ImageFont.load_default()
    tag=c["tag"]; tw=font.getbbox(tag)[2]
    out=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-crf","12","-preset","slow","-pix_fmt","yuv420p","-movflags","+faststart",c["out"]],stdin=subprocess.PIPE)
    tA,rate,sE=c["tA"],c["rate"],c["sEnd"]
    for i in range(n):
        t=i/FPS
        st=sE-(tA-t)*rate if t<tA else sE
        img=fr[min(len(fr)-1,max(0,round(st*FPS)))].astype(np.float32)/255
        h0,h1=c["hl"]; p=ease((t-h0)/(h1-h0))*tot; acc=0
        if t>=tA:
            for l in lines:
                seg=min(max(p-acc,0),l["w"]); acc+=l["w"]
                if seg<=0: continue
                x0,y0=l["x"]-6,l["y"]-3; x1,y1=int(l["x"]+seg+6),l["y"]+l["h"]+3
                img[y0:y1,x0:x1]*=LIME
        im=Image.fromarray((img*255).astype(np.uint8))
        cx,cy,s=cam(t,c["cam"]); cw,ch=W/s,H/s
        x0=min(max(cx-cw/2,0),W-cw); y0=min(max(cy-ch/2,0),H-ch)
        im=im.resize((W,H),Image.LANCZOS,box=(x0,y0,x0+cw,y0+ch))
        a=ease((t-c.get("tagAt",tA+0.3))/0.5)
        if a>0:
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
            d.rounded_rectangle((60,H-130,60+tw+48,H-70),radius=30,fill=(17,17,17,int(225*a)))
            d.text((84,H-124),tag,font=font,fill=(255,255,255,int(255*a)))
            im=Image.alpha_composite(im.convert("RGBA"),ov).convert("RGB")
        out.stdin.write(im.tobytes())
    out.stdin.close(); out.wait(); print("done",c["out"],n/FPS)
if len(sys.argv) < 2: sys.exit(__doc__)
main(sys.argv[1])
