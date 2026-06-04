#!/usr/bin/env python3
"""
Extreme Debye test: push dispersion to the MAXIMUM (eps_inf -> 1, i.e. the
largest d_eps physically allowed) and sweep tau across the GPR band, to find
the CEILING of the frequency-vs-FI slope Debye can produce on the effective
medium. Baseline homog slope ~0.17, one Debye level gave ~0.37; real ~3.6.

If even the extreme can't approach 3.6, Debye is not the (whole) answer.

Scenes: same 30 spanning FI 0-55 (reuses homog_debye/manifest.csv).
Variants per scene: tau ∈ {0.2, 0.4, 0.8} ns, each with MAX d_eps (eps_inf=1).
Metric: spectral centroid.

Usage:
    python scripts/experiments/homog_debye_extreme.py --generate
    python scripts/experiments/homog_debye_extreme.py --analyze
"""
import re, sys, argparse
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.physics import crim_bulk_eps, debye_decompose

DATA_DIR = ROOT / "output" / "gpr_synth_dataset_80k"
OUT_DIR  = Path(r"D:\gprMax\user_models\homog_debye_extreme")
SRC_MAN  = Path(r"D:\gprMax\user_models\homog_debye\manifest.csv")
EPS_ROCK, SIG_ROCK = 5.0, 0.001
TAUS = [0.2e-9, 0.4e-9, 0.8e-9]

def parse(c,k):
    m=re.search(rf"^## {k}:\s*([-\d.eE+]+)",c,re.MULTILINE); return float(m.group(1)) if m else None
def foul(c):
    m=re.search(r"^#material:\s*([\d.eE+-]+)\s+([\d.eE+-]+).*bal_foul",c,re.MULTILINE)
    return (float(m.group(1)),float(m.group(2))) if m else (5.0,0.01)

def homog_debye_max(content, tau):
    fr=parse(content,"mc_rock_fraction") or 0; ff=parse(content,"mc_fouling_fraction") or 0
    fv=parse(content,"mc_void_fraction") or 0; tot=fr+ff+fv
    if tot<=0: return None
    vr,vf,va=fr/tot,ff/tot,fv/tot; ef,sf=foul(content)
    eps=round(crim_bulk_eps(vr,EPS_ROCK,vf,ef,0,1.0,va),4)
    sig=round(vr*SIG_ROCK+vf*sf,6)
    # MAX dispersion: d_eps_frac=1.0 -> capped so eps_inf=1
    einf,deps=debye_decompose(eps,1.0)
    bb=parse(content,"ballast_bottom_y"); bt=parse(content,"ballast_top_y")
    dom=re.search(r"#domain:\s*([\d.eE+-]+) [\d.eE+-]+ ([\d.eE+-]+)",content)
    dxx,dz=dom.group(1),dom.group(2)
    kept=[l for l in content.splitlines() if not l.startswith(("#box:","#cylinder:","#triangle:","#edge:","#plate:"))]
    body="\n".join(kept).rstrip()
    geom=(f"\n#material: {einf} {sig} 1 0.0 ballast_eff\n"
          f"#add_dispersion_debye: 1 {deps} {tau:.4e} ballast_eff\n"
          f"#box: 0.0 0.0 0.0 {dxx} 0.2 {dz} subgrade\n"
          f"#box: 0.0 0.2 0.0 {dxx} {bb} {dz} formation\n"
          f"#box: 0.0 {bb} 0.0 {dxx} {bt} {dz} ballast_eff\n")
    return body+geom

def generate():
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    man=pd.read_csv(SRC_MAN)
    out=[]
    for _,r in man.iterrows():
        src=DATA_DIR/f"s_{int(r['sample_id']):05d}.in"
        if not src.exists(): continue
        c=src.read_text(encoding="utf-8",errors="ignore")
        for tau in TAUS:
            txt=homog_debye_max(c,tau)
            if txt is None: continue
            tag=f"tau{tau*1e9:.1f}".replace(".","p")
            (OUT_DIR/f"s_{int(r['sample_id']):05d}_{tag}.in").write_text(txt,encoding="utf-8")
        out.append({"sample_id":int(r['sample_id']),"Lab_FI":r['Lab_FI']})
    pd.DataFrame(out).to_csv(OUT_DIR/"manifest.csv",index=False)
    print(f"Generated {len(out)*len(TAUS)} .in ({len(out)} scenes x {len(TAUS)} tau) in {OUT_DIR}")

def metric(ez,dt):
    from scipy.signal import welch,butter,filtfilt
    pk=int(np.argmax(np.abs(ez))); coda=ez[pk+20:]
    if len(coda)<64: return np.nan
    sig=coda-coda.mean(); fs=1/dt
    b,a=butter(4,[150e6/(fs/2),800e6/(fs/2)],btype="band"); sig=filtfilt(b,a,sig)
    f,p=welch(sig,fs=fs,nperseg=min(len(sig),256),nfft=4096)
    band=(f>=150e6)&(f<=800e6); f,p=f[band],p[band]
    return np.sum(f*p)/np.sum(p)/1e6 if p.sum()>0 else np.nan

def analyze():
    from src.data_loader import read_ascan
    from scipy.stats import linregress
    man=pd.read_csv(OUT_DIR/"manifest.csv")
    def load(p):
        d=read_ascan(p); return d["signal"].astype(float), d["dt"]
    print(f"Real target slope ~3.6 MHz/FI | baseline nodeb ~0.17 | 1-level debye ~0.37\n")
    for tau in TAUS:
        tag=f"tau{tau*1e9:.1f}".replace(".","p")
        rows=[]
        for _,r in man.iterrows():
            op=OUT_DIR/f"s_{int(r['sample_id']):05d}_{tag}.out"
            if op.exists():
                rows.append({"FI":r['Lab_FI'],"c":metric(*load(op))})
        d=pd.DataFrame(rows).dropna()
        if len(d)>2:
            s=linregress(d["FI"],d["c"])
            print(f"  tau={tau*1e9:.1f}ns (MAX d_eps): slope={s.slope:+.3f} MHz/FI "
                  f"(r={s.rvalue:+.2f}, p={s.pvalue:.2g}, n={len(d)})")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--generate",action="store_true")
    ap.add_argument("--analyze",action="store_true"); a=ap.parse_args()
    if a.generate: generate()
    elif a.analyze: analyze()
    else: print("--generate or --analyze")

if __name__=="__main__": main()
