"""Frame-level voice features for filler detection (numpy + scipy). Imported by filler_detect.py and
filler_signature.py; not run on its own.
Requires: ffmpeg on PATH, Python 3 with numpy and scipy.
feats(x, sr=16000) -> dict of arrays at 10 ms hop: db (RMS dB), f0 (Hz, 0 if unvoiced), vc (voicing 0-1),
cent (spectral centroid Hz), flux (spectral change), mfcc (n x 13)."""
import numpy as np, subprocess
from scipy.fft import dct
SR=16000; HOP=160; WIN=400
def load(path, start=None, dur=None):
    cmd=["ffmpeg","-loglevel","error"]+(["-ss",str(start)] if start is not None else [])+(["-t",str(dur)] if dur else [])+["-i",path,"-vn","-ac","1","-ar",str(SR),"-f","s16le","-"]
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.int16).astype(np.float32)/32768
def _mel(n=26,nfft=512):
    hz=lambda m:700*(10**(m/2595)-1); mel=lambda h:2595*np.log10(1+h/700)
    pts=hz(np.linspace(mel(60),mel(7600),n+2)); b=np.floor((nfft+1)*pts/SR).astype(int); fb=np.zeros((n,nfft//2+1))
    for i in range(1,n+1):
        fb[i-1,b[i-1]:b[i]]=(np.arange(b[i-1],b[i])-b[i-1])/max(1,b[i]-b[i-1]); fb[i-1,b[i]:b[i+1]]=(b[i+1]-np.arange(b[i],b[i+1]))/max(1,b[i+1]-b[i])
    return fb
FB=_mel()
def feats(x):
    n=max(0,(len(x)-WIN)//HOP); fr=np.lib.stride_tricks.sliding_window_view(x,WIN)[::HOP][:n]*np.hanning(WIN)
    db=20*np.log10(np.sqrt((fr**2).mean(1))+1e-9)
    sp=np.abs(np.fft.rfft(fr,512)); fq=np.fft.rfftfreq(512,1/SR)
    cent=(sp*fq).sum(1)/(sp.sum(1)+1e-9)
    nsp=sp/(np.linalg.norm(sp,axis=1,keepdims=True)+1e-9); flux=np.r_[0,np.linalg.norm(np.diff(nsp,axis=0),axis=1)]
    mfcc=dct(np.log(sp**2@FB.T+1e-9),type=2,axis=1,norm="ortho")[:,:13]
    # autocorrelation pitch 70-300 Hz
    lo,hi=SR//300,SR//70; ac=np.fft.irfft(np.abs(np.fft.rfft(fr,1024))**2)[:,:hi+1]
    r=ac[:,lo:hi+1]/(ac[:,:1]+1e-9); k=r.argmax(1); vc=r.max(1); f0=np.where(vc>0.45,SR/(k+lo),0.)
    return dict(db=db,f0=f0,vc=vc,cent=cent,flux=flux,mfcc=mfcc)
