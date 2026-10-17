#!/usr/bin/env python3
"""Find a speaker's fillers from transcript + their own waveform signature.
Usage: python3 filler_detect.py <audio.wav> <words.json> <out.json> [from_s] [to_s] [--tags right,okay]
  audio.wav   export_audio of the current timeline (or the source mic file, with words in its own time)
  words.json  [{"w": word, "start": s, "end": s}, ...] for the same audio (from Borumi get_transcript)
  --tags      comma list of the speaker's verbal tag words cut when they end a sentence ("right?") or
              stand alone ("Right."). Default: right. Pass --tags "" to switch the tag pass off.
1. Transcript pass: words uh/um/er/ah/hmm, immediate repeats ("the the"), tag words ("right?") and standalone tags ("Right.")
2. Signature pass: voiced runs >=150 ms whose spectrum barely changes (held vowel) - the "uh" shape.
   The speaker profile (mean MFCC + flux/centroid stats of their confirmed fillers) is LEARNED from the
   transcript-marked fillers in this same file, then every held-vowel run is scored against it.
3. Each candidate gets: kind, start/end (s), overlapping words, score, verdict cut|review|keep.
Emphasis doubles ("very very", "so so", "super super", "really really") are never flagged.
Requires: ffmpeg on PATH, Python 3 with numpy and scipy (via voicefeat.py)."""
import sys, json, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
import voicefeat as V
FILL={"uh","um","umm","uhm","er","erm","ah","hmm","mm"}
norm=lambda w:w.lower().strip(" ,.?!;:\"'")
a=sys.argv[:]
TAGS={"right"}
if "--tags" in a:
    i=a.index("--tags"); TAGS={x.strip().lower() for x in a[i+1].split(",") if x.strip()}; del a[i:i+2]
if len(a)<4: sys.exit(__doc__)
audio,wordsf,out=a[1],a[2],a[3]; lo=float(a[4]) if len(a)>4 and not a[4].startswith("--") else 0; hi=float(a[5]) if len(a)>5 and not a[5].startswith("--") else 1e9
words=[w for w in json.load(open(wordsf)) if lo<=w["start"]<hi]
x=V.load(audio); F=V.feats(x); T=np.arange(len(F["db"]))*V.HOP/V.SR
fl=np.percentile(F["db"],10); sm=lambda v,k=5:np.convolve(v,np.ones(k)/k,"same")
flux=sm(F["flux"]); idx=lambda t:int(t*V.SR/V.HOP)
cands=[]
# ---- 1. transcript pass
for i,w in enumerate(words):
    n=norm(w["w"]); prev=norm(words[i-1]["w"]) if i else ""; nxt=words[i+1] if i+1<len(words) else None
    if n in FILL: cands.append(dict(kind="filler",start=w["start"],end=w["end"],words=w["w"]))
    elif i and n==prev and n not in ("very","so","many","super","really") and w["start"]-words[i-1]["end"]<0.35:
        cands.append(dict(kind="repeat",start=words[i-1]["start"],end=words[i-1]["end"],words=words[i-1]["w"]+" "+w["w"]))
    elif n in TAGS and (w["w"].strip().endswith("?") or (w["w"].strip().endswith(".") and (not i or words[i-1]["w"].strip()[-1:] in ".?!"))):
        cands.append(dict(kind="right_tag",start=w["start"],end=w["end"],words=w["w"]))
# ---- 2. learn the profile from transcript fillers, then scan held-vowel runs
def seg_stats(s,e):
    i,j=idx(s),max(idx(s)+1,idx(e)); return dict(mfcc=F["mfcc"][i:j].mean(0),flux=float(flux[i:j].mean()),cent_sd=float(np.std(F["cent"][i:j])),db=float(F["db"][i:j].mean()-fl))
conf=[seg_stats(c["start"],c["end"]) for c in cands if c["kind"]=="filler" and c["end"]-c["start"]>=0.12]
prof=None
if conf:
    prof=dict(mfcc=np.mean([c["mfcc"] for c in conf],0),flux=float(np.median([c["flux"] for c in conf])),n=len(conf))
held=(flux<0.16)&(F["db"]>fl+12)&(F["vc"]>0.3)
runs=[];s=None
for k,v in enumerate(held):
    if v and s is None: s=k
    if (not v or k==len(held)-1) and s is not None:
        if (k-s)>=15: runs.append((T[s],T[k]))
        s=None
def overl(s,e): return [w for w in words if w["end"]>s and w["start"]<e]
for s,e in runs:
    if not (lo<=s<hi): continue
    if any(c["start"]<e and c["end"]>s for c in cands): continue
    st=seg_stats(s,e); ow=overl(s,e)
    sim=float(np.dot(st["mfcc"],prof["mfcc"])/(np.linalg.norm(st["mfcc"])*np.linalg.norm(prof["mfcc"])+1e-9)) if prof else 0
    # a held vowel that is not covered by a real word (or only by a word's tail) is a missed filler
    covered=sum(min(e,w["end"])-max(s,w["start"]) for w in ow if norm(w["w"]) not in FILL)/(e-s)
    kind="held_unlabelled" if covered<0.4 else "elongated_word"
    cands.append(dict(kind=kind,start=round(s,3),end=round(e,3),words=" ".join(w["w"] for w in ow),sim=round(sim,3),covered=round(covered,2)))
for c in cands:
    st=seg_stats(c["start"],c["end"]); c["flux"]=round(st["flux"],3)
    if prof and "sim" not in c: c["sim"]=round(float(np.dot(st["mfcc"],prof["mfcc"])/(np.linalg.norm(st["mfcc"])*np.linalg.norm(prof["mfcc"])+1e-9)),3)
    c["verdict"]={"filler":"cut","repeat":"cut","right_tag":"cut","held_unlabelled":"cut" if c.get("sim",0)>0.97 and c["end"]-c["start"]>=0.18 else "review","elongated_word":"keep"}[c["kind"]]
cands.sort(key=lambda c:c["start"])
json.dump(dict(profile=dict(n=prof["n"],flux=prof["flux"],mfcc=prof["mfcc"].round(3).tolist()) if prof else None,candidates=cands),open(out,"w"),indent=1)
from collections import Counter
print("profile from",prof["n"] if prof else 0,"transcript fillers; candidates:",dict(Counter((c["kind"],c["verdict"]) for c in cands)))
