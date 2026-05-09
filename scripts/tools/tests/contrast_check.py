"""Check code behavior against Liu et al. (2023) review and Selig & Waters (1994)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.physics import convert_pvc_to_fi, inverse_convert_fi_to_pvc, classify_fouling_index
from src.constants import PHC

print("=== 1. PVC -> FI mapping vs Liu 2023 Table 1 ===")
print("  (Table 1: Clean PVC<20, MF 20-29, F >30)")
print(f"  {'PVC%':>5}  {'FI%':>6}  {'Class':>5}  Paper-Table1-note")
paper_note = {
    0:   "C  (paper: 0<PVC<20)",
    10:  "C  (paper: clean)",
    20:  "?  (paper: MF boundary 20<PVC<29)",
    29:  "?  (paper: F boundary PVC>30)",
    30:  "F  (paper: Fouled PVC>30)",
    40:  "F  (paper: Fouled)",
    65:  "F  (paper: Fouled, extreme)",
    100: "?  (paper: no category)",
}
for pvc in [0, 10, 20, 29, 30, 40, 65, 100]:
    fi = convert_pvc_to_fi(pvc)
    cls = classify_fouling_index(fi)
    note = paper_note.get(pvc, "")
    print(f"  {pvc:>5}  {fi:>6.1f}  {cls:>5}  {note}")

print()
print("=== 2. FI boundary thresholds -> required PVC ===")
for fi_b, label in [(1,"C/MC"), (10,"MC/MF"), (20,"MF/F"), (40,"F/HF")]:
    pvc = inverse_convert_fi_to_pvc(fi_b)
    print(f"  FI={fi_b:2}% ({label:6}) -> needs PVC={pvc:.1f}%")

print()
print("=== 3. HF (FI>=40%) reachability at PVC=100% ===")
fi_max = convert_pvc_to_fi(100.0)
print(f"  Default (Gs_b={PHC.DEFAULT_BALLAST_DENSITY}, Gs_f={PHC.DEFAULT_FOULING_DENSITY}, phi={PHC.DEFAULT_POROSITY}): FI_max={fi_max:.2f}%  HF={fi_max>=40}")
for gs_b, gs_f, phi in [(2.6, 2.6, 0.4), (2.72, 2.58, 0.45), (2.7, 2.3, 0.4)]:
    fi2 = convert_pvc_to_fi(100.0, porosity=phi, Gs_b=gs_b, Gs_f=gs_f)
    print(f"  Gs_b={gs_b}, Gs_f={gs_f}, phi={phi} -> FI_max={fi2:.1f}%  HF={fi2>=40}")

print()
print("=== 4. VCI (Indraratna 2011) vs our Lab_Rb_f ===")
print("  VCI = (1 + ef/eb) x (Gs_b/Gs_f) x (Mf/Mb) x 100")
print("  Our Rb_f = (Vf/Gs_f) / (Vb/Gs_b) x 100  [different metric]")
ef = 0.90   # typical fouling void ratio (clay/silt)
eb = PHC.DEFAULT_POROSITY / (1.0 - PHC.DEFAULT_POROSITY)  # = phi/(1-phi)
print(f"  ef={ef}, eb={eb:.3f} (phi={PHC.DEFAULT_POROSITY})")
for fi_val in [5, 10, 20, 30, 38]:
    fi_frac = fi_val / 100.0
    mf_mb = fi_frac / (1.0 - fi_frac)
    vf_vb = mf_mb * (PHC.DEFAULT_BALLAST_DENSITY / PHC.DEFAULT_FOULING_DENSITY)
    vci = (1.0 + ef / eb) * vf_vb * 100.0
    rb_f = vf_vb * (PHC.DEFAULT_BALLAST_DENSITY / PHC.DEFAULT_FOULING_DENSITY) * 100.0
    print(f"  FI={fi_val:2}%  Mf/Mb={mf_mb:.3f}  Vf/Vb={vf_vb:.3f}  VCI={vci:.1f}%  Rb_f={rb_f:.1f}%")

print()
print("=== 5. Barrett et al. CRIM at scenario endpoints ===")
from src.physics import crim_bulk_eps, surface_reflectivity_R, attenuation_factor_npm, topp_mixing_model
print("  [dry clean: 60% rock, 0% foul, 0% water, 40% air]")
eps = crim_bulk_eps(0.60, 5.5, 0.0, 1.0, 0.0, 80.1, 0.40)
R   = surface_reflectivity_R(1.0, eps)
a400 = attenuation_factor_npm(400e6, eps, 1e-4)
a2g  = attenuation_factor_npm(2e9,   eps, 1e-4)
print(f"    bulk_eps={eps:.2f}  R={R:.4f}  alpha_400={a400:.4f}  alpha_2GHz={a2g:.4f} Np/m")

print("  [F class wet: 50% rock, 25% foul, 8% water, 17% air, moisture=0.08]")
moist = 0.08
eps_f = topp_mixing_model(moist)
eps2 = crim_bulk_eps(0.50, 5.5, 0.25, eps_f, 0.08, 80.1, 0.17)
R2   = surface_reflectivity_R(1.0, eps2)
sig  = 0.50*1e-4 + 0.25*moist*0.1 + 0.08*0.05
a400b = attenuation_factor_npm(400e6, eps2, sig)
a2gb  = attenuation_factor_npm(2e9,   eps2, sig)
print(f"    bulk_eps={eps2:.2f}  R={R2:.4f}  alpha_400={a400b:.4f}  alpha_2GHz={a2gb:.4f} Np/m")
print(f"    400MHz penetration depth (1/alpha): {1/a400b:.2f} m  (paper says ~4 m)")
print(f"    2GHz penetration depth  (1/alpha): {1/a2gb:.3f} m  (paper says ~0.75 m)")
