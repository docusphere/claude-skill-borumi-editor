#!/usr/bin/env python3
"""Learn a speaker's filler signature from known fillers, then scan audio for unlabelled ones.
Usage: python3 filler_signature.py <audio> <known.json [[start_ms,end_ms,label],...]> <out.json> [from_s] [to_s]
known: transcript fillers (uh/um). Profile = mean MFCC + flux of their held-vowel core.
Scan: voiced runs >=140 ms with low spectral flux (held vowel, no articulation), scored by cosine
similarity to the profile. Output: profile + ranked candidates {start_ms,end_ms,sim,flux,db}.
A safety net: when the transcript already marks "uh/um", most top hits are stretched real words
("and...", "so..."). Put those on a review list for the creator; never cut them automatically.
Requires: ffmpeg on PATH, Python 3 with numpy and scipy (via voicefeat.py)."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voicefeat as V
a=sys.argv
if len(a)<4: sys.exit(__doc__)
audio,known,out=a[1],a[2],a[3]; lo=float(a[4]) if len(a)>4 else 0; hi=float(a[5]) if len(a)>5 else 1e9
x=V.load(audio); F=V.feats(x); fl=np.percentile(F["db"],10)
flux=np.convolve(F["flux"],np.ones(5)/5,"same"); fr=lambda ms:int(ms/10)
K=[k for k in json.load(open(known)) if any(t in k[2].lower() for t in ("uh","um"))]
cores=[]
for s,e,_ in K:
    i,j=fr(s)-5,fr(e)+5; seg=flux[i:j]; ok=np.where((seg<0.18)&(F["db"][i:j]>fl+10))[0]
    if len(ok)>=6: cores.append(F["mfcc"][i+ok].mean(0))
prof=np.mean(cores,0); pn=np.linalg.norm(prof)
held=(flux<0.16)&(F["db"]>fl+12)&(F["vc"]>0.3); runs=[];s=None
for k,v in enumerate(held):
    if v and s is None: s=k
    if (not v or k==len(held)-1) and s is not None:
        if k-s>=14 and lo*100<=s<hi*100: runs.append((s,k))
        s=None
res=[]
for s,e in runs:
    m=F["mfcc"][s:e].mean(0); sim=float(m@prof/(np.linalg.norm(m)*pn+1e-9))
    res.append(dict(start_ms=s*10,end_ms=e*10,sim=round(sim,3),flux=round(float(flux[s:e].mean()),3),db=round(float(F["db"][s:e].mean()-fl),1)))
res.sort(key=lambda r:-r["sim"])
json.dump(dict(profile_n=len(cores),profile=prof.round(3).tolist(),candidates=res),open(out,"w"),indent=1)
print("profile from",len(cores),"known fillers;",len(res),"held-vowel runs; top sims:",[r["sim"] for r in res[:8]])
