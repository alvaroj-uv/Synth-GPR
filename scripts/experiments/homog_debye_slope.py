#!/usr/bin/env python3
"""
Test: does Debye dispersion on the EFFECTIVE-MEDIUM ballast raise the
frequency-vs-FI slope toward the real value (~3.6 MHz/FI)?

Baseline (homogeneous, no Debye) gave slope ~0.25 MHz/FI — right direction,
~15x too weak. Here each scene gets a homogeneous ballast box in TWO versions:
  - nodeb : constant eps (baseline)
  - debye : same eps split into eps_inf + 1-pole Debye (d_eps = 60% of eps_eff,
            tau tuned near the GPR band)
Scenes span FI 0-55 so we can fit a real slope. Metric: spectral centroid.

Usage:
    python scripts/experiments/homog_debye_slope.py --generate
    python scripts/experiments/homog_debye_slope.py --analyze
"""

import re, sys, argparse, os
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.physics import crim_bulk_eps, debye_decompose

DATA_DIR = ROOT / "output" / "gpr_synth_dataset_80k"
OUT_DIR  = Path(r"D:\gprMax\user_models\homog_debye")
PARQUET  = ROOT / "output" / "dataset_80k_features.parquet"

EPS_ROCK, SIG_ROCK = 5.0, 0.001
D_EPS_FRAC = 0.6          # dispersive fraction of eps_eff
TAU = 0.4e-9              # ~ 1/(2*pi*400MHz), relaxation near GPR band
FI_BINS = [(0,5),(10,15),(20,25),(30,35),(45,55)]
N_PER_BIN = 6
SEED = 7


def parse(c,k):
    m=re.search(rf"^## {k}:\s*([-\d.eE+]+)",c,re.MULTILINE); return float(m.group(1)) if m else None

def foul(c):
    m=re.search(r"^#material:\s*([\d.eE+-]+)\s+([\d.eE+-]+).*bal_foul",c,re.MULTILINE)
    return (float(m.group(1)),float(m.group(2))) if m else (5.0,0.01)

def homog_box(content, debye):
    fr=parse(content,"mc_rock_fraction") or 0; ff=parse(content,"mc_fouling_fraction") or 0
    fv=parse(content,"mc_void_fraction") or 0; tot=fr+ff+fv
    if tot<=0: return None
    vr,vf,va=fr/tot,ff/tot,fv/tot
    ef,sf=foul(content)
    eps=round(crim_bulk_eps(vr,EPS_ROCK,vf,ef,0,1.0,va),4)
    sig=round(vr*SIG_ROCK+vf*sf,6)
    bb=parse(content,"ballast_bottom_y"); bt=parse(content,"ballast_top_y")
    dom=re.search(r"#domain:\s*([\d.eE+-]+) [\d.eE+-]+ ([\d.eE+-]+)",content)
    dxx,dz=dom.group(1),dom.group(2)
    kept=[l for l in content.splitlines() if not l.startswith(("#box:","#cylinder:","#triangle:","#edge:","#plate:"))]
    body="\n".join(kept).rstrip()
    if debye:
        einf,deps=debye_decompose(eps,D_EPS_FRAC)
        mat=(f"#material: {einf} {sig} 1 0.0 ballast_eff\n"
             f"#add_dispersion_debye: 1 {deps} {TAU:.4e} ballast_eff")
    else:
        mat=f"#material: {eps} {sig} 1 0.0 ballast_eff"
    geom=(f"\n{mat}\n"
          f"#box: 0.0 0.0 0.0 {dxx} 0.2 {dz} subgrade\n"
          f"#box: 0.0 0.2 0.0 {dxx} {bb} {dz} formation\n"
          f"#box: 0.0 {bb} 0.0 {dxx} {bt} {dz} ballast_eff\n")
    return body+geom

def generate():
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    syn=pd.read_parquet(PARQUET,columns=["sample_id","Lab_FI"])
    rng=np.random.default_rng(SEED); picks=[]
    for lo,hi in FI_BINS:
        pool=syn[(syn.Lab_FI>=lo)&(syn.Lab_FI<hi)].sample_id.values
        if len(pool): picks.extend(rng.choice(pool,min(N_PER_BIN,len(pool)),replace=False))
    man=[]
    for sid in picks:
        src=DATA_DIR/f"s_{int(sid):05d}.in"
        if not src.exists(): continue
        c=src.read_text(encoding="utf-8",errors="ignore")
        for kind,deb in [("nodeb",False),("debye",True)]:
            txt=homog_box(c,deb)
            if txt is None: continue
            p=OUT_DIR/f"s_{int(sid):05d}_{kind}.in"; p.write_text(txt,encoding="utf-8")
        man.append({"sample_id":int(sid),"Lab_FI":float(syn[syn.sample_id==sid].Lab_FI.iloc[0])})
    pd.DataFrame(man).to_csv(OUT_DIR/"manifest.csv",index=False)
    print(f"Generated {len(man)*2} .in ({len(man)} scenes x2) in {OUT_DIR}")
    print("Run run_all.bat, then --analyze")

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
    rows=[]
    for _,r in man.iterrows():
        rec={"FI":r["Lab_FI"]}
        for kind in ["nodeb","debye"]:
            op=OUT_DIR/f"s_{int(r['sample_id']):05d}_{kind}.out"
            rec[kind]=metric(*load(op)) if op.exists() else np.nan
        rows.append(rec)
    df=pd.DataFrame(rows)
    print(f"Analyzed {len(df)} scenes, FI {df.FI.min():.0f}-{df.FI.max():.0f}\n")
    for kind in ["nodeb","debye"]:
        d=df[["FI",kind]].dropna()
        s=linregress(d["FI"],d[kind])
        print(f"  {kind:6s}: centroid-vs-FI slope = {s.slope:+.3f} MHz/FI "
              f"(r={s.rvalue:+.2f}, p={s.pvalue:.2g}, n={len(d)})")
    print(f"\n  REAL target slope (median_freq): 3.6 MHz/FI")
    print("  Debye helps only if its slope is clearly larger than nodeb's 0.25.")
    df.to_csv(OUT_DIR/"results.csv",index=False)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--generate",action="store_true")
    ap.add_argument("--analyze",action="store_true"); a=ap.parse_args()
    if a.generate: generate()
    elif a.analyze: analyze()
    else: print("--generate or --analyze")

if __name__=="__main__": main()
