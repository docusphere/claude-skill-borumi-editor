#!/usr/bin/env python3
# Copyright (c) 2026 Nillard Ltd (company no. 16312961). Nillard Ltd Skills License 1.0, see LICENSE. Not for resale or redistribution.
"""Audit every audio cut in a Borumi edit against the source audio.

Borumi's MCP has no waveform tool, so this reads the source media directly and
checks the start and end of every kept audio segment, relative to each clip's
own noise floor. It flags:
  (a) cuts made while sound is still active (a word cut in half), and
  (b) stray packets: a short burst separated from the kept speech by >= 40 ms
      of quiet (a leftover "S", an "uh", a lip click, a breath).
Inspect every flag with cut_audit.py before changing anything; many flags are
harmless breaths or run-on joins already at their valley.

Usage:
  python3 edge_audit.py <medias_dir> [segs.txt] [--id-chars N]

  <medias_dir>   the Borumi project bundle (<project>.bmprojbundle) or its
                 medias/ folder; both work. Microphone media may be .mp4 or
                 .wav depending on how the project was recorded.
                 (env var BORUMI_MEDIAS is used if the argument is omitted)
  segs.txt       one line per microphone segment (default: ./segs.txt):
                     <segment_id> <media_key> <src_start_ms> <src_end_ms> <tl_start_ms> <tl_end_ms>
                 Build it from get_timeline on the microphone_1 layer with media
                 fields (media id, media start/end, segment start/end).
  --id-chars N   media_key = the first N characters of the source file name
                 (default 4). Media files in medias/ are named after their media
                 id, so a short id prefix identifies the file.

Output: "<n> segments, <2n> edges checked; <k> flagged", then one line per flag:
  <segment_id> START|END <timeline_ms> <reason>

Requires: ffmpeg on PATH, Python 3 with numpy.
"""
import numpy as np,subprocess,glob,os,sys
_args=[a for a in sys.argv[1:]]
_n=4
if "--id-chars" in _args:
    i=_args.index("--id-chars"); _n=int(_args[i+1]); del _args[i:i+2]
M=_args[0].rstrip("/") if _args else os.environ.get("BORUMI_MEDIAS")
SEGS=_args[1] if len(_args)>1 else "segs.txt"
if M and os.path.isdir(M+"/medias"): M=M+"/medias"
if not M or not os.path.isdir(M): sys.exit(__doc__)
files={os.path.basename(f)[:_n]:f for f in glob.glob(M+"/*.mp4")+glob.glob(M+"/*.wav") if "rvm" not in f}
cache={}
def audio(mid):
    if mid not in cache:
        raw=subprocess.run(["ffmpeg","-loglevel","error","-i",files[mid],"-vn","-ac","1","-ar","48000","-f","s16le","-"],capture_output=True).stdout
        cache[mid]=np.frombuffer(raw,np.int16).astype(float)/32768
    return cache[mid]
def frames(a,t0,t1):
    sr=48000;out=[]
    for i in range(int(t0*sr),int(t1*sr)-480,480):
        if i<0 or i+480>len(a): out.append((-90,-90)); continue
        s=a[i:i+480]; r=20*np.log10(np.sqrt((s**2).mean())+1e-9)
        sp=np.abs(np.fft.rfft(s*np.hanning(480))); fr=np.fft.rfftfreq(480,1/sr); h=20*np.log10(np.sqrt((sp[fr>4000]**2).mean())+1e-9)
        out.append((r,h))
    return out
rows=[l.split() for l in open(SEGS) if l.strip()]
flags=[]
for sid,mid,s0,s1,t0,t1 in rows:
    a=audio(mid); s0=int(s0)/1000; s1=int(s1)/1000
    ctx=frames(a,max(0,s0-1),s1+1) ; floor=np.percentile([r for r,h in ctx],10)
    q=floor+6; loud=floor+14
    # END edge: last 250 ms kept
    E=frames(a,s1-0.25,s1)
    endlast=max(r for r,h in E[-2:])
    if endlast>loud: flags.append((sid,"END",int(t1),"cut while sound active (last 20ms %.0f dB, floor %.0f)"%(endlast,floor)))
    else:
        # quiet run then burst before the end = stray packet
        quiet=0;seen_quiet=False
        for k,(r,h) in enumerate(E):
            if r<q: quiet+=1
            else:
                if quiet>=4 and (r>loud or h>floor+30): flags.append((sid,"END",int(t1),"stray packet %d ms before end after %d ms quiet (%.0f dB)"%((len(E)-k)*10,quiet*10,r))); break
                quiet=0
    # START edge: first 250 ms kept
    S=frames(a,s0,s0+0.25)
    st=max(r for r,h in S[:2])
    if st>loud: flags.append((sid,"START",int(t0),"starts during sound (first 20ms %.0f dB, floor %.0f)"%(st,floor)))
    else:
        for k,(r,h) in enumerate(S):
            if r>loud or h>floor+30:
                # burst: is it followed by >=40ms quiet before more speech?
                rest=S[k:]; j=next((i for i,(rr,hh) in enumerate(rest) if rr<q),None)
                if j is not None and j<8:
                    run=0
                    for rr,hh in rest[j:]:
                        if rr<q: run+=1
                        else: break
                    if run>=4 and j+run<len(rest): flags.append((sid,"START",int(t0),"leading packet at +%d ms then %d ms quiet"%(k*10,run*10)))
                break
print(len(rows),"segments,",2*len(rows),"edges checked;",len(flags),"flagged")
for f in flags: print(*f)
