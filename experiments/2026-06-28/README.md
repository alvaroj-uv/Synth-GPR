# 2026-06-28 — Gap-fill + domain test + sub-ballast layer

Three sub-experiments extending the 2026-06-27 void-eps sweep and improving real-data match.

## Sub-experiment A: FI gap-fill (eps_void = 2.0, 3.0, 3.5)
Eliminated cubic-spline artifact in virtual sieve between FI=0 and FI=34%.
- `gssi_400_3d_rocks_veps3.0`, `gssi_400_3d_rocks_veps3.5`
- **Note:** eps_void=3.0 shows non-monotonic bump (coda_RMS=0.3945 > air=0.3741).
  Possible Mie-regime resonance; needs seed study to confirm.

## Sub-experiment B: Domain size test (0.55×0.55 m)
Tested whether 10% larger domain closes sim→real energy gap.
- `gssi_400_3d_rocks_veps4.5_d55`
- **Result:** No improvement. Energy gap is structural (missing sub-ballast/sleeper reflections).

## Sub-experiment C: Sub-ballast layer (15 cm, eps=7.5)
Added sand sub-ballast layer to match real PKC011 t≈10-11 ns reflection packet.
- `gssi_400_3d_subballast` + `scene_3d_subballast.toml`
- Layer stack: subgrade 5cm (eps=13) / subballast 15cm (eps=7.5) / ballast 50cm / air 5cm / GSSI
- Expected: ballast-subballast ~7.5 ns, subgrade ~10.3 ns after DW removal

## Summary plots
- `gssi_400_3d_void_eps_sweep.png` — coda RMS vs FI (10 points)
- `gssi_400_3d_virtual_sieve.png` — virtual sieve with gap-fill
- `gssi_400_3d_raw_waveforms.png` — all 11 raw Ey waveforms grid
- `gssi_400_3d_vivanco_comparison.png` — Vivanco envelopes (synthetic only)
- `gssi_400_3d_vivanco_vs_real.png` — Vivanco envelopes vs real PKC011 tr#77000
- `gssi_400_3d_domain_test.png` — d=0.50 m vs d=0.55 m vs real DZT
