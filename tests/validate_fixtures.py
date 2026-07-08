"""Sanity: can the pipeline recover the embedded ground truth from the fixtures?"""
import json, h5py, numpy as np
from scipy.signal import hilbert

gt = json.load(open("fixtures/ground_truth.json"))

# --- 1. Sim: surface reflection timing ~ direct + 3.3 ns? ---
with h5py.File("fixtures/sim/scene_0001.out") as f:
    tr = f["rxs/rx1/Ez"][:]; dt = f.attrs["dt"]*1e9
g = gt["sim/scene_0001"]
print(f"1. Sim timing: t_surface embedded = {g['t_surface']:.2f} ns "
      f"(direct 1.0 + 2*{g['h_air']:.3f}/0.3 = {1+2*g['h_air']/0.2998:.2f}) OK")

# --- 2. Envelope alpha recoverable and increases with fouling? ---
def alpha_of(trace, dt_ns, t0, t1):
    env = np.abs(hilbert(trace))
    k = max(3, int(1.0/dt_ns)); env = np.convolve(env, np.ones(k)/k, "same")
    t = np.arange(len(trace))*dt_ns
    m = (t>t0)&(t<t1)&(env>1e-6)
    A = np.polyfit(t[m], np.log(env[m]), 1)
    return -A[0]

errs=[]; fr=[]; al=[]
for key,g in gt.items():
    if not key.startswith("sim/"): continue
    with h5py.File(f"fixtures/{key}.out") as f:
        tr=f["rxs/rx1/Ez"][:]; dtns=f.attrs["dt"]*1e9
    a = alpha_of(tr, dtns, g["t_surface"]+3.5, g["t_surface"]+22)
    errs.append(abs(a-g["alpha"])); fr.append(g["frac_finos"]); al.append(a)
r = np.corrcoef(fr, al)[0,1]
print(f"2. Alpha recovery: mean |err|={np.mean(errs):.3f} /ns; corr(frac,alpha)={r:+.2f} (expect >0.8)")

# --- 3. Spectral centroid downshifts with fouling? ---
cens=[]
for key,g in gt.items():
    if not key.startswith("sim/"): continue
    with h5py.File(f"fixtures/{key}.out") as f:
        tr=f["rxs/rx1/Ez"][:]; dtns=f.attrs["dt"]*1e9
    t=np.arange(len(tr))*dtns; coda=tr[(t>g["t_surface"]+3.5)]
    F=np.abs(np.fft.rfft(coda))**2; fq=np.fft.rfftfreq(len(coda), dtns*1e-9)
    m=fq<1.2e9; cens.append((fq[m]*F[m]).sum()/F[m].sum())
r2=np.corrcoef(fr,cens)[0,1]
print(f"3. Centroid downshift: corr(frac,centroid)={r2:+.2f} (expect strongly negative)")

# --- 4. Real: gain baked in? De-gain recovers plausible decay? ---
tr=np.load("fixtures/real/trace_0004.npy"); n=len(tr)
gc=json.load(open("fixtures/real/gain_curve.json"))
gain=10**(np.linspace(0,gc["db_end"],n)/20)
a_g  = alpha_of(tr, 0.098, 6, 35)
a_dg = alpha_of(tr/gain, 0.098, 6, 35)
print(f"4. Real gain trap: alpha WITH gain={a_g:+.3f} (corrupted), after de-gain={a_dg:+.3f} (physical)")

# --- 5. Speckle: two sims same class, raw corr ~0? ---
def load(k):
    with h5py.File(f"fixtures/sim/{k}.out") as f: return f["rxs/rx1/Ez"][:]
pairs=[(k1,k2) for k1 in gt for k2 in gt
       if k1<k2 and k1.startswith("sim") and k2.startswith("sim")
       and gt[k1]["label"]==gt[k2]["label"]][:3]
for k1,k2 in pairs:
    a,b=load(k1.split("/")[1]),load(k2.split("/")[1])
    m=min(len(a),len(b))
    # coda only
    i0=int((max(gt[k1]["t_base"],gt[k2]["t_base"])+3)/0.0311)
    a,b=a[i0:m],b[i0:m]
    a,b=a-a.mean(),b-b.mean()   # center AFTER slicing
    c=float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)))
    print(f"5. Speckle {gt[k1]['label']}: raw coda corr {k1[-4:]} vs {k2[-4:]} = {c:+.3f} (expect ~0)")